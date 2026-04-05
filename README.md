# Plant Disease Deployment (Cotton + Wheat)

This repository now includes a deployable FastAPI inference service for your trained models.

## Included API

- Service file: `app/main.py`
- Supported crops: `cotton`, `wheat`
- Endpoints:
  - `GET /health`
  - `GET /labels/{crop}`
  - `POST /predict/{crop}` (multipart image upload)

## Input validation behavior

`POST /predict/{crop}` now validates uploads so that only cotton/wheat plant leaf images are accepted.

- Non-image files are rejected (`400`).
- Empty uploads are rejected (`400`).
- Images that do not look like cotton/wheat leaf inputs are rejected (`422`) using leaf color + connected-region checks.

This keeps the disease predictor from returning results for unsupported images.

## Model artifacts tracked in git

Only these model files are kept for deployment:

- `saved_models/cotton_final_efficientnetv2b0.keras`
- `saved_models/wheat_final_efficientnetv2s.keras`
- `saved_models/cotton_class_names.json`
- `saved_models/wheat_class_names.json`

Everything else in `saved_models` remains ignored.

## Run locally

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start API:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

3. Health check:

```bash
curl http://localhost:8000/health
```

4. Predict example:

```bash
curl -X POST "http://localhost:8000/predict/cotton?top_k=3" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/absolute/path/to/leaf.jpg"
```

## Deploy with Docker

Build and run:

```bash
docker build -t plant-disease-api .
docker run -p 8000:8000 plant-disease-api
```

## Deploy on Render/Railway/Heroku-style platforms

This repo includes:

- `Procfile`
- `runtime.txt`
- `requirements.txt`

Start command (already in Procfile):

```bash
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

## Optional environment variables

Use these if you want custom model paths:

- `MODEL_DIR`
- `COTTON_MODEL_PATH`
- `WHEAT_MODEL_PATH`
- `COTTON_CLASSES_PATH`
- `WHEAT_CLASSES_PATH`
- `EAGER_MODEL_LOAD=1` (preload models at startup)

Validation tuning (optional):

- `IMAGE_VALIDATION_MASK_SIZE` (default `96`)
- `IMAGE_VALIDATION_MIN_COLOR_RATIO` (default `0.25`)
- `IMAGE_VALIDATION_MIN_CLUSTER_RATIO` (default `0.08`)
