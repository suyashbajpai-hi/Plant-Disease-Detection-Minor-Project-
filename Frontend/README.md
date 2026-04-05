# Plant Disease Frontend (React)

React + Vite frontend for the FastAPI plant disease inference backend.

## Features

- Select crop model: Cotton or Wheat
- Upload a leaf image
- Get predicted disease name and confidence
- View top-3 class probabilities

## Configure API URL

Create a `.env` file in this folder:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

If not set, the app defaults to `http://localhost:8000`.

## Run

```bash
npm install
npm run dev
```

Open: `http://localhost:5173`

## Build

```bash
npm run build
npm run preview
```
