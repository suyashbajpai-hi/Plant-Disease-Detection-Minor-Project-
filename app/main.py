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

            self.class_names = [str(name) for name in class_names]
            self.model = model

    def predict(self, image_bytes: bytes, top_k: int) -> list[dict[str, float | str]]:
        if not self.is_loaded:
            self.load()

        assert self.model is not None
        assert self.class_names is not None

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image = image.resize(self.config.image_size)

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


CROP_CONFIGS: dict[str, CropConfig] = {
    "cotton": CropConfig(
        model_path=_path_from_env(
            "COTTON_MODEL_PATH", MODEL_DIR / "cotton_final_efficientnetv2b0.keras"
        ),
        class_names_path=_path_from_env(
            "COTTON_CLASSES_PATH", MODEL_DIR / "cotton_class_names.json"
        ),
        image_size=(224, 224),
    ),
    "wheat": CropConfig(
        model_path=_path_from_env(
            "WHEAT_MODEL_PATH", MODEL_DIR / "wheat_final_efficientnetv2b0.keras"
        ),
        class_names_path=_path_from_env(
            "WHEAT_CLASSES_PATH", MODEL_DIR / "wheat_class_names.json"
        ),
        image_size=(300, 300),
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
            "image_size": model.config.image_size,
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
    if top_k < 1 or top_k > 10:
        raise HTTPException(status_code=400, detail="top_k must be between 1 and 10.")

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload a valid image file.")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    model = _get_model(crop)

    try:
        top_predictions = model.predict(image_bytes=image_bytes, top_k=top_k)
    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=400, detail="Could not read uploaded image.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    best = top_predictions[0]
    return {
        "crop": crop.lower(),
        "predicted_class": best["class_name"],
        "confidence": best["confidence"],
        "top_k": top_predictions,
    }
