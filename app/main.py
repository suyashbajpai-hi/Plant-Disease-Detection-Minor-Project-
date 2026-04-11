from __future__ import annotations

import io
import json
import os
import sys
import threading
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import tensorflow as tf
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from keras.applications.efficientnet_v2 import preprocess_input
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, Field

# Ensure project root is on sys.path so the Recommendation Model package is importable
_PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from importlib import import_module as _import_module
_rec_engine = _import_module("Recommendation Model.recommendation_engine")
_gemini_svc = _import_module("Recommendation Model.LLM_Model")

# --- GPU memory safety: allow growth so we don't grab all VRAM ---------------
def _configure_gpu():
    try:
        gpus = tf.config.list_physical_devices("GPU")
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except Exception:
        pass  # CPU-only or already initialised

_configure_gpu()
# ------------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_DIR = Path(os.getenv("MODEL_DIR", BASE_DIR / "saved_models"))


def _env_float(env_name: str, default: float) -> float:
    value = os.getenv(env_name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _env_int(env_name: str, default: int) -> int:
    value = os.getenv(env_name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


IMAGE_VALIDATION_MASK_SIZE = max(32, _env_int("IMAGE_VALIDATION_MASK_SIZE", 96))
IMAGE_VALIDATION_MIN_COLOR_RATIO = _clamp01(
    _env_float("IMAGE_VALIDATION_MIN_COLOR_RATIO", 0.25)
)
IMAGE_VALIDATION_MIN_CLUSTER_RATIO = _clamp01(
    _env_float("IMAGE_VALIDATION_MIN_CLUSTER_RATIO", 0.08)
)


@dataclass(frozen=True)
class CropConfig:
    model_path: Path
    class_names_path: Path
    image_size: tuple[int, int]


class CropModel:
    def __init__(self, crop: str, config: CropConfig) -> None:
        self.crop = crop
        self.config = config
        self.model: tf.keras.Model | None = None
        self.class_names: list[str] | None = None
        self.effective_image_size: tuple[int, int] = config.image_size
        self._lock = threading.Lock()

    @property
    def is_loaded(self) -> bool:
        return self.model is not None and self.class_names is not None

    def load(self) -> None:
        if self.is_loaded:
            return

        with self._lock:
            if self.is_loaded:
                return

            if not self.config.model_path.exists():
                raise FileNotFoundError(
                    f"Missing model file for {self.crop}: {self.config.model_path}"
                )
            if not self.config.class_names_path.exists():
                raise FileNotFoundError(
                    f"Missing class names file for {self.crop}: {self.config.class_names_path}"
                )

            with self.config.class_names_path.open("r", encoding="utf-8") as f:
                class_names = json.load(f)
            if not isinstance(class_names, list) or not class_names:
                raise ValueError(
                    f"Invalid class names in {self.config.class_names_path}. Expected a non-empty JSON list."
                )

            # Try GPU first; on OOM / internal GPU error fall back to CPU
            _GPU_ERRORS = (tf.errors.ResourceExhaustedError, tf.errors.InternalError, RuntimeError)
            try:
                model = tf.keras.models.load_model(str(self.config.model_path), compile=False)
            except _GPU_ERRORS:
                with tf.device("/CPU:0"):
                    model = tf.keras.models.load_model(str(self.config.model_path), compile=False)

            resolved_size = self._resolve_model_image_size(model)

            self.class_names = [str(name) for name in class_names]
            self.model = model
            self.effective_image_size = resolved_size or self.config.image_size

    def _resolve_model_image_size(self, model: tf.keras.Model) -> tuple[int, int] | None:
        input_shape = model.input_shape
        if isinstance(input_shape, list):
            if not input_shape:
                return None
            input_shape = input_shape[0]

        if not isinstance(input_shape, tuple) or len(input_shape) != 4:
            return None

        height, width, channels = input_shape[1], input_shape[2], input_shape[3]
        if not isinstance(height, int) or not isinstance(width, int):
            return None
        if channels not in (3, None):
            return None

        return (height, width)

    def predict(self, image_bytes: bytes, top_k: int) -> list[dict[str, float | str]]:
        if not self.is_loaded:
            self.load()

        assert self.model is not None
        assert self.class_names is not None

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image = image.resize(self.effective_image_size)

        array = np.asarray(image, dtype=np.float32)
        batch = np.expand_dims(array, axis=0)
        batch = preprocess_input(batch)

        # Run inference; on GPU OOM / internal error transparently retry on CPU
        try:
            raw = self.model(batch, training=False).numpy()[0]
        except (tf.errors.ResourceExhaustedError, tf.errors.InternalError):
            with tf.device("/CPU:0"):
                raw = self.model(batch, training=False).numpy()[0]
        probs = _to_probabilities(raw)

        top_k = max(1, min(int(top_k), len(self.class_names)))
        top_indices = np.argsort(probs)[::-1][:top_k]

        return [
            {
                "class_name": self.class_names[int(idx)],
                "confidence": float(probs[int(idx)]),
            }
            for idx in top_indices
        ]


def _to_probabilities(raw_output: np.ndarray) -> np.ndarray:
    probs = np.asarray(raw_output, dtype=np.float32).reshape(-1)
    if probs.size == 0 or np.any(~np.isfinite(probs)):
        raise ValueError("Model returned invalid output.")

    looks_like_probs = (
        np.all(probs >= 0.0)
        and np.all(probs <= 1.0)
        and np.isclose(float(np.sum(probs)), 1.0, atol=1e-3)
    )

    if not looks_like_probs:
        probs = tf.nn.softmax(probs).numpy()

    total = float(np.sum(probs))
    if total <= 0:
        raise ValueError("Model returned zero probabilities.")

    return probs / total


def _path_from_env(env_name: str, fallback: Path) -> Path:
    value = os.getenv(env_name)
    if not value:
        return fallback
    return Path(value)


def _model_path_from_env_or_candidates(env_name: str, candidates: list[Path]) -> Path:
    value = os.getenv(env_name)
    if value:
        return Path(value)

    for candidate in candidates:
        if candidate.exists():
            return candidate

    # If no candidate exists yet (e.g., first deploy), return first preference.
    return candidates[0]


CROP_CONFIGS: dict[str, CropConfig] = {
    "cotton": CropConfig(
        model_path=_model_path_from_env_or_candidates(
            "COTTON_MODEL_PATH",
            [
                MODEL_DIR / "cotton_final_efficientnetv2s.keras",
                MODEL_DIR / "cotton_final_efficientnetv2b0.keras",
            ],
        ),
        class_names_path=_path_from_env(
            "COTTON_CLASSES_PATH", MODEL_DIR / "cotton_class_names.json"
        ),
        image_size=(224, 224),
    ),
    "wheat": CropConfig(
        model_path=_model_path_from_env_or_candidates(
            "WHEAT_MODEL_PATH",
            [
                MODEL_DIR / "wheat_final_efficientnetv2s.keras",
                MODEL_DIR / "wheat_final_efficientnetv2b0.keras",
            ],
        ),
        class_names_path=_path_from_env(
            "WHEAT_CLASSES_PATH", MODEL_DIR / "wheat_class_names.json"
        ),
        image_size=(224, 224),
    ),
}

MODELS = {crop: CropModel(crop, cfg) for crop, cfg in CROP_CONFIGS.items()}

DISEASE_INFO: dict[str, dict[str, dict[str, str]]] = {
    "cotton": {
        "Bacterial Blight": {
            "scientific_name": "Xanthomonas citri subsp. malvacearum",
            "description": "Angular, water-soaked lesions on leaves that turn brown and necrotic. Severely infected leaves may dry up and drop prematurely.",
            "treatment": "Use disease-free seeds, apply copper-based bactericides, practice crop rotation, and remove infected plant debris.",
        },
        "Curl Virus": {
            "scientific_name": "Cotton Leaf Curl Virus (CLCuV, Begomovirus)",
            "description": "Upward or downward curling of leaves with vein thickening and enations on the underside. Stunted plant growth and reduced boll formation.",
            "treatment": "Control whitefly vector (Bemisia tabaci) with neem-based or systemic insecticides. Use resistant varieties and remove infected plants early.",
        },
        "Healthy Leaf": {
            "scientific_name": "Gossypium spp. (No Pathogen)",
            "description": "The leaf shows no signs of disease, pest damage, or nutrient deficiency. Normal green coloration and structure.",
            "treatment": "No treatment required. Continue regular crop monitoring and balanced fertilization.",
        },
        "Herbicide Growth Damage": {
            "scientific_name": "Abiotic Stress (Herbicide Phytotoxicity)",
            "description": "Abnormal leaf curling, cupping, or strapping caused by herbicide drift or residual herbicide in soil. May show chlorosis or necrosis.",
            "treatment": "Avoid herbicide drift during application. Use buffer zones, apply growth regulators to aid recovery, and ensure proper herbicide selection.",
        },
        "Leaf Hopper Jassids": {
            "scientific_name": "Amrasca biguttula biguttula (Ishida)",
            "description": "Yellowing and curling of leaf margins progressing inward. Leaves show a burnt appearance (hopper burn) in severe infestations.",
            "treatment": "Apply systemic insecticides (imidacloprid, thiamethoxam). Use resistant varieties and maintain proper plant spacing for air circulation.",
        },
        "Leaf Redding": {
            "scientific_name": "Physiological Disorder / Leaf Reddening Syndrome",
            "description": "Reddish-purple discoloration of leaves due to nutrient deficiency (magnesium/nitrogen), waterlogging, or pest-induced stress.",
            "treatment": "Apply balanced fertilizers with magnesium supplementation. Improve drainage and control sucking pests that may trigger reddening.",
        },
        "Leaf Variegation": {
            "scientific_name": "Genetic Mosaicism / Nutrient Deficiency",
            "description": "Irregular patches of light and dark green on leaves. May be caused by genetic factors, viral infections, or micronutrient imbalance.",
            "treatment": "Apply micronutrient foliar sprays (zinc, manganese, iron). If viral, control insect vectors and remove symptomatic plants.",
        },
    },
    "wheat": {
        "Black Rust(Stem Rust)": {
            "scientific_name": "Puccinia graminis f. sp. tritici",
            "description": "Dark reddish-brown to black pustules on stems, leaves, and leaf sheaths. Can cause severe yield loss by weakening stems and reducing grain fill.",
            "treatment": "Use resistant varieties, apply fungicides (propiconazole, tebuconazole) at early infection, and eliminate alternate host (barberry).",
        },
        "BlackPoint": {
            "scientific_name": "Bipolaris sorokiniana / Alternaria alternata",
            "description": "Dark discoloration at the embryo end of wheat grains. Affects grain quality and germination but not always yield.",
            "treatment": "Timely harvest to avoid rain damage, use fungicide seed treatments, and ensure proper grain drying and storage.",
        },
        "FusariumFootRot": {
            "scientific_name": "Fusarium graminearum / F. culmorum",
            "description": "Brown lesions at the stem base, causing wilting, white-head symptoms, and premature death of tillers.",
            "treatment": "Rotate with non-cereal crops, use seed treatments (fludioxonil), avoid deep sowing, and manage crop residue.",
        },
        "HealthyPlant": {
            "scientific_name": "Triticum aestivum (No Pathogen)",
            "description": "The plant shows no signs of disease or pest damage. Normal green coloration and healthy growth pattern.",
            "treatment": "No treatment required. Maintain regular monitoring, balanced nutrition, and good agronomic practices.",
        },
        "LeafBlight": {
            "scientific_name": "Bipolaris sorokiniana (Spot Blotch)",
            "description": "Dark brown elliptical lesions on leaves that may coalesce, causing extensive leaf blight and premature drying.",
            "treatment": "Apply foliar fungicides (propiconazole, mancozeb), use resistant varieties, and practice crop rotation.",
        },
        "Mildew": {
            "scientific_name": "Blumeria graminis f. sp. tritici",
            "description": "White to gray powdery fungal growth on leaf surfaces, stems, and heads. Reduces photosynthesis and grain quality.",
            "treatment": "Use resistant varieties, apply fungicides (triadimefon, sulfur), avoid excessive nitrogen, and ensure adequate spacing.",
        },
        "Smut": {
            "scientific_name": "Ustilago tritici (Loose Smut)",
            "description": "Grain heads replaced by masses of dark brown to black spores. Infected heads appear earlier than healthy ones.",
            "treatment": "Use certified smut-free seeds, apply systemic seed treatments (carboxin, thiram), and use hot water seed treatment.",
        },
        "WheatBlast": {
            "scientific_name": "Magnaporthe oryzae pathotype Triticum (MoT)",
            "description": "Bleached or white heads with shriveled grains. Rapid spike death under warm, humid conditions. Highly destructive.",
            "treatment": "Use resistant varieties, apply fungicides preventively (strobilurins + triazoles), avoid late sowing, and manage crop residue.",
        },
        "Yellow Rust(Leaf Rust)": {
            "scientific_name": "Puccinia striiformis f. sp. tritici",
            "description": "Yellow-orange pustules arranged in stripes along leaf veins. Favored by cool, moist conditions. Can cause severe yield reduction.",
            "treatment": "Use resistant varieties, apply foliar fungicides early (propiconazole, tebuconazole), and monitor fields regularly.",
        },
    },
}


def _get_disease_info(crop: str, class_name: str) -> dict[str, str]:
    crop_info = DISEASE_INFO.get(crop, {})
    return crop_info.get(class_name, {
        "scientific_name": "",
        "description": "",
        "treatment": "",
    })

app = FastAPI(
    title="Plant Disease Inference API",
    description="Inference API for cotton and wheat disease classification models.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_model(crop: str) -> CropModel:
    key = crop.strip().lower()
    if key not in MODELS:
        raise HTTPException(
            status_code=404,
            detail=f"Unsupported crop '{crop}'. Use one of: {', '.join(sorted(MODELS.keys()))}",
        )

    model = MODELS[key]
    try:
        model.load()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to load model for {key}: {exc}",
        ) from exc

    return model


def _build_leaf_mask(image_bytes: bytes, size: int) -> np.ndarray:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image = image.resize((size, size))

    rgb = np.asarray(image, dtype=np.float32) / 255.0
    red = rgb[..., 0]
    green = rgb[..., 1]
    blue = rgb[..., 2]

    max_channel = np.max(rgb, axis=-1)
    min_channel = np.min(rgb, axis=-1)
    value = max_channel
    saturation = np.where(
        max_channel == 0,
        0.0,
        (max_channel - min_channel) / np.maximum(max_channel, 1e-6),
    )

    diff = np.maximum(max_channel - min_channel, 1e-6)
    red_comp = (max_channel - red) / diff
    green_comp = (max_channel - green) / diff
    blue_comp = (max_channel - blue) / diff

    hue = np.zeros_like(max_channel)
    hue = np.where(max_channel == red, (blue_comp - green_comp), hue)
    hue = np.where(max_channel == green, (2.0 + red_comp - blue_comp), hue)
    hue = np.where(max_channel == blue, (4.0 + green_comp - red_comp), hue)
    hue_degrees = ((hue / 6.0) % 1.0) * 360.0

    green_mask = (
        (hue_degrees >= 35.0)
        & (hue_degrees <= 170.0)
        & (saturation >= 0.15)
        & (value >= 0.12)
    )
    brown_mask = (
        (hue_degrees >= 8.0)
        & (hue_degrees <= 35.0)
        & (saturation >= 0.18)
        & (value >= 0.12)
    )
    return green_mask | brown_mask


def _largest_connected_component_ratio(mask: np.ndarray) -> float:
    height, width = mask.shape
    visited = np.zeros_like(mask, dtype=bool)
    largest = 0

    for y in range(height):
        for x in range(width):
            if not mask[y, x] or visited[y, x]:
                continue

            stack = [(y, x)]
            visited[y, x] = True
            component_size = 0

            while stack:
                current_y, current_x = stack.pop()
                component_size += 1

                for neighbor_y, neighbor_x in (
                    (current_y - 1, current_x),
                    (current_y + 1, current_x),
                    (current_y, current_x - 1),
                    (current_y, current_x + 1),
                ):
                    if (
                        0 <= neighbor_y < height
                        and 0 <= neighbor_x < width
                        and mask[neighbor_y, neighbor_x]
                        and not visited[neighbor_y, neighbor_x]
                    ):
                        visited[neighbor_y, neighbor_x] = True
                        stack.append((neighbor_y, neighbor_x))

            if component_size > largest:
                largest = component_size

    return largest / float(height * width)


def _validate_supported_crop_image(image_bytes: bytes) -> None:
    leaf_mask = _build_leaf_mask(
        image_bytes=image_bytes,
        size=IMAGE_VALIDATION_MASK_SIZE,
    )
    color_ratio = float(np.mean(leaf_mask))
    cluster_ratio = _largest_connected_component_ratio(leaf_mask)

    if (
        color_ratio < IMAGE_VALIDATION_MIN_COLOR_RATIO
        or cluster_ratio < IMAGE_VALIDATION_MIN_CLUSTER_RATIO
    ):
        raise HTTPException(
            status_code=422,
            detail="Invalid image. Upload only cotton or wheat plant leaf images.",
        )


@app.on_event("startup")
def preload_models_if_enabled() -> None:
    if os.getenv("EAGER_MODEL_LOAD", "0") != "1":
        return
    for model in MODELS.values():
        try:
            model.load()
        except Exception:
            # Startup should still succeed so health endpoint can expose missing artifact state.
            continue


@app.get("/")
def root() -> dict[str, object]:
    return {
        "service": "plant-disease-inference",
        "supported_crops": sorted(MODELS.keys()),
        "predict_endpoint": "/predict/{crop}",
        "health_endpoint": "/health",
    }


@app.get("/health")
def health() -> dict[str, object]:
    models = {}
    for crop, model in MODELS.items():
        models[crop] = {
            "loaded": model.is_loaded,
            "model_file_exists": model.config.model_path.exists(),
            "class_file_exists": model.config.class_names_path.exists(),
            "model_path": str(model.config.model_path),
            "class_names_path": str(model.config.class_names_path),
            "configured_image_size": model.config.image_size,
            "effective_image_size": model.effective_image_size,
            "image_size": model.effective_image_size,
        }

    ok = all(item["model_file_exists"] and item["class_file_exists"] for item in models.values())
    return {"status": "ok" if ok else "degraded", "models": models}


@app.get("/labels/{crop}")
def labels(crop: str) -> dict[str, object]:
    model = _get_model(crop)
    assert model.class_names is not None
    return {"crop": crop.lower(), "labels": model.class_names}


@app.post("/predict/{crop}")
async def predict(
    crop: str,
    file: UploadFile = File(...),
    top_k: int = 3,
) -> dict[str, object]:
    requested_crop = crop.strip().lower()

    if top_k < 1 or top_k > 10:
        raise HTTPException(status_code=400, detail="top_k must be between 1 and 10.")

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload a valid image file.")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    model = _get_model(requested_crop)

    try:
        _validate_supported_crop_image(image_bytes=image_bytes)
        top_predictions = model.predict(image_bytes=image_bytes, top_k=top_k)
    except HTTPException:
        raise
    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=400, detail="Could not read uploaded image.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    best = top_predictions[0]
    best_info = _get_disease_info(requested_crop, best["class_name"])
    best_rec = _rec_engine.get_recommendation(requested_crop, best["class_name"])

    top_k_with_info = []
    for pred in top_predictions:
        info = _get_disease_info(requested_crop, pred["class_name"])
        rec = _rec_engine.get_recommendation(requested_crop, pred["class_name"])
        top_k_with_info.append({
            **pred,
            "scientific_name": info.get("scientific_name", ""),
            "recommendation": rec,
        })

    return {
        "crop": requested_crop,
        "predicted_class": best["class_name"],
        "confidence": best["confidence"],
        "scientific_name": best_info.get("scientific_name", ""),
        "description": best_info.get("description", ""),
        "treatment": best_info.get("treatment", ""),
        "recommendation": best_rec,
        "top_k": top_k_with_info,
    }


# ---------------------------------------------------------------------------
# Gemini LLM-powered detailed recommendation
# ---------------------------------------------------------------------------

class RecommendRequest(BaseModel):
    crop: str = Field(..., min_length=1, max_length=50)
    disease: str = Field(..., min_length=1, max_length=200)
    remedies: list[str] = Field(default_factory=list)
    farm_size_acres: float = Field(..., gt=0, le=10_000)


@app.post("/recommend")
async def recommend(body: RecommendRequest) -> dict[str, object]:
    crop_key = body.crop.strip().lower()
    if crop_key not in MODELS:
        raise HTTPException(
            status_code=404,
            detail=f"Unsupported crop '{body.crop}'. Use one of: {', '.join(sorted(MODELS.keys()))}",
        )

    try:
        result = await _gemini_svc.generate_detailed_recommendation(
            crop=crop_key,
            disease=body.disease,
            remedies=body.remedies,
            farm_size_acres=body.farm_size_acres,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"LLM service error: {exc}",
        ) from exc

    return {
        "crop": crop_key,
        "disease": body.disease,
        "farm_size_acres": body.farm_size_acres,
        "detailed_recommendation": result,
    }
