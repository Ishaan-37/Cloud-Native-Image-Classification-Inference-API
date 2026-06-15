# Medical Image Inference API — Week 1

**Summer Internship Project | IIT Jammu | 2026**
**Student:** Ishaan Maurya | **Supervisor:** Dr. Yamuna Prasad

---

## Overview

A RESTful inference API built with **FastAPI** that serves a pre-trained **ResNet-50**
convolutional neural network. The API accepts an image file and returns the top-5
ImageNet class predictions with confidence scores and per-request latency.

---

## Project Structure

```
week1_project/
├── app/
│   ├── __init__.py
│   ├── main.py        ← FastAPI app, routes, middleware
│   ├── model.py       ← ResNet-50 loader + inference logic
│   └── schemas.py     ← Pydantic request/response models
├── tests/
│   └── test_api.py    ← Pytest smoke-tests for all endpoints
├── requirements.txt
└── README.md
```

---

## Setup Instructions

### 1. Clone / download the project

```bash
cd ~/Desktop
# If using git:
git clone <your-repo-url>
cd week1_project

# Or just unzip the provided folder.
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> ⚠️ PyTorch (~700 MB) will be downloaded on first install. This may take a few minutes.

### 4. Run the API server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
INFO  : Loading ResNet-50 model …
INFO  : ResNet-50 ready on cpu.
INFO  : Uvicorn running on http://0.0.0.0:8000
```

---

## API Endpoints

| Method | Route      | Description                              |
|--------|------------|------------------------------------------|
| GET    | `/health`  | Health check — confirms model is loaded  |
| GET    | `/info`    | Metadata about the ResNet-50 model       |
| POST   | `/predict` | Run inference on an uploaded image       |
| GET    | `/docs`    | Auto-generated Swagger UI                |
| GET    | `/redoc`   | ReDoc API documentation                  |

---

## Usage Examples

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Model info
curl http://localhost:8000/info

# Predict (replace cat.jpg with any image)
curl -X POST http://localhost:8000/predict \
     -F "file=@cat.jpg"
```

### Using Python (requests library)

```python
import requests

url = "http://localhost:8000/predict"
with open("cat.jpg", "rb") as f:
    response = requests.post(url, files={"file": f})

print(response.json())
```

---

## Example JSON Response (`/predict`)

```json
{
  "predicted_class": "tabby cat",
  "class_id": 281,
  "confidence": 0.843,
  "top_5_predictions": [
    { "label": "tabby cat",    "class_id": 281, "confidence": 0.843 },
    { "label": "tiger cat",    "class_id": 282, "confidence": 0.091 },
    { "label": "Egyptian cat", "class_id": 285, "confidence": 0.041 },
    { "label": "lynx",         "class_id": 287, "confidence": 0.012 },
    { "label": "persian cat",  "class_id": 283, "confidence": 0.007 }
  ],
  "inference_time_ms": 42.3,
  "device_used": "cpu"
}
```

---

## Running Tests

```bash
pip install pytest httpx
pytest tests/test_api.py -v
```

---

## Interactive API Docs

Once the server is running, open your browser and go to:

```
http://localhost:8000/docs
```

This gives you a full Swagger UI where you can test all endpoints interactively —
upload images directly from the browser.

---

## How It Works (Technical Summary)

1. **Request comes in** → FastAPI validates the file MIME type via Pydantic
2. **Image decoded** → Pillow opens it and converts to RGB
3. **Preprocessing** → Resize → CenterCrop(224) → Normalize (ImageNet stats)
4. **Forward pass** → ResNet-50 returns 1000-class logits
5. **Softmax** → logits → probability distribution
6. **Top-5 selected** → returned as structured JSON with latency

---

## Week 1 Deliverable Checklist

- [x] Survey of model-serving frameworks (FastAPI vs Flask vs TorchServe)
- [x] RESTful API with FastAPI serving pre-trained ResNet-50
- [x] `/predict` endpoint for image ingestion
- [x] Structured JSON response format
- [x] Input validation and error handling
- [x] Pydantic schemas documenting all request/response structures
- [x] Swagger / ReDoc auto-docs at `/docs` and `/redoc`
- [x] Unit tests for all endpoints
