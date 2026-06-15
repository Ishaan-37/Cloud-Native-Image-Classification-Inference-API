# Medical Image Inference API

A cloud-based RESTful inference API that serves a pre-trained **ResNet-50** convolutional neural network for automated image classification. Built as part of the **IIT Jammu Summer Internship 2026**.

> **Student:** Ishaan Maurya — B.Tech. Cloud Computing and Automation, VIT Bhopal (Summer Intern, IIT Jammu)
>
> **Supervisor:** Dr. Yamuna Prasad, Dept. of CSE, IIT Jammu
>
> **Mentor:** Sankar Behera 

---

# Live API

| Endpoint | URL |
|----------|-----|
| Health Check | `http://13.220.179.104:8000/health` |
| Swagger Docs | `http://13.220.179.104:8000/docs` |
| Predict | `POST http://13.220.179.104:8000/predict` |

---

# Project Structure

```text
medical-image-inference-api/
├── 01_fastapi_api/
│   ├── app/
│   │   ├── main.py
│   │   ├── model.py
│   │   └── schemas.py
│   ├── tests/
│   │   └── test_api.py
│   ├── requirements.txt
│   ├── FRAMEWORK_SURVEY.md
│   └── README.md
│
├── 02_dockerized_api/
│   ├── app/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── .dockerignore
│   └── README.md
│
├── 03_cloud_deployment/
│   ├── scripts/
│   │   ├── deploy_ec2.sh
│   │   ├── load_test.py
│   │   └── nginx.conf
│   └── BENCHMARKING_LOG.md
│
├── .gitignore
└── README.md
```

---

# Architecture

```text
Client (HTTP)
    │
    ▼
Nginx (port 80)
    │
    ▼
FastAPI + Uvicorn (port 8000, 2 workers)
    │
    ├── GET  /health
    ├── GET  /info
    └── POST /predict
            │
            ▼
Pillow → Resize → Normalize → ResNet-50 → Softmax → Top-5 Predictions
```

---

# Quick Start — Run Locally

## Option A: Python

```bash
git clone https://github.com/Ishaan-37/medical-image-inference-api.git

cd medical-image-inference-api/01_fastapi_api

python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open:

```text
http://localhost:8000/docs
```

---

## Option B: Docker

```bash
cd 02_dockerized_api

docker compose up --build
```

Open:

```text
http://localhost:8000/docs
```

---

# API Reference

## GET /health

```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2026-06-15T06:52:36Z"
}
```

---

## GET /info

```json
{
  "model_name": "ResNet-50",
  "framework": "PyTorch",
  "input_size": "224 x 224",
  "num_classes": 1000,
  "training_dataset": "ImageNet (ILSVRC 2012)"
}
```

---

## POST /predict

Request:

```bash
curl -X POST http://localhost:8000/predict \
-F "file=@your_image.jpg"
```

Response:

```json
{
  "predicted_class": "tabby cat",
  "class_id": 281,
  "confidence": 0.843,
  "top_5_predictions": [
    {
      "label": "tabby cat",
      "class_id": 281,
      "confidence": 0.843
    },
    {
      "label": "tiger cat",
      "class_id": 282,
      "confidence": 0.091
    },
    {
      "label": "Egyptian cat",
      "class_id": 285,
      "confidence": 0.041
    },
    {
      "label": "lynx",
      "class_id": 287,
      "confidence": 0.012
    },
    {
      "label": "persian cat",
      "class_id": 283,
      "confidence": 0.007
    }
  ],
  "inference_time_ms": 42.3,
  "device_used": "cpu"
}
```

---

# Running Tests

```bash
cd 01_fastapi_api

pip install pytest httpx

pytest tests/test_api.py -v
```

---

# Tech Stack

| Layer | Technology |
|-------|------------|
| Web Framework | FastAPI 0.111 |
| ASGI Server | Uvicorn 0.29 |
| Deep Learning | PyTorch 2.3 + torchvision 0.18 |
| Image Processing | Pillow 10.3 |
| Data Validation | Pydantic v2 |
| Containerisation | Docker 25 + Compose v2 |
| Reverse Proxy | Nginx |
| Cloud | Amazon EC2 (Ubuntu 22.04 LTS) |
| Load Testing | Locust |

---

# Weekly Progress

| Week | Focus | Deliverable |
|------|-------|-------------|
| 1 | API Development | FastAPI + ResNet-50 running locally |
| 2 | Containerisation | Docker multi-stage image |
| 3 | Cloud Deployment | EC2 deployment + benchmarking |
| 4 | Documentation | Final report + presentation |

---

# Research Context

This project aligns with ongoing IIT Jammu laboratory research on deploying computer vision models into clinical environments.

The architecture is designed to be model-agnostic, meaning ResNet-50 can later be replaced with the IIT Jammu IPI-CVx Intestinal Parasite Detection model by updating `model.py`.

---

# License

MIT License — free to use for academic and research purposes.
