from __future__ import annotations

import io
import json
import os
import threading
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import tensorflow as tf
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from keras.applications.efficientnet_v2 import preprocess_input
from PIL import Image, UnidentifiedImageError

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
                MODEL_DIR / "cotton_final_efficientnetv2b0.keras",
                MODEL_DIR / "cotton_final_efficientnetv2s.keras",
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
    return {
        "crop": requested_crop,
        "predicted_class": best["class_name"],
        "confidence": best["confidence"],
        "top_k": top_predictions,
    }
