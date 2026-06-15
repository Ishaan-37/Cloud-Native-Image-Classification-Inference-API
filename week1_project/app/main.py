"""
Medical Image Inference API
Summer Internship Project - Week 1
Student: Ishaan Maurya | IIT Jammu | 2026
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from PIL import Image
import io
import logging
import time

from app.model import ResNetModel
from app.schemas import PredictionResponse, HealthResponse, ModelInfoResponse

# ── Logging setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(name)s : %(message)s",
)
logger = logging.getLogger(__name__)

# ── App init ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Medical Image Inference API",
    description=(
        "A cloud-based RESTful inference API that serves a pre-trained ResNet-50 "
        "model for automated image classification. "
        "Built as part of IIT Jammu Summer Internship 2026."
    ),
    version="1.0.0",
    contact={
        "name": "Ishaan Maurya",
        "email": "ishaan@example.com",
    },
)

# Allow all origins during local dev (tighten in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load model once at startup ────────────────────────────────────────────────
logger.info("Loading ResNet-50 model …")
model = ResNetModel()
logger.info("Model loaded successfully.")


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    tags=["System"],
)
async def health_check():
    """Returns the current health status and whether the model is loaded."""
    return HealthResponse(
        status="healthy",
        model_loaded=model.is_loaded,
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )


@app.get(
    "/info",
    response_model=ModelInfoResponse,
    summary="Model Information",
    tags=["Model"],
)
async def model_info():
    """Returns metadata about the deployed deep learning model."""
    return ModelInfoResponse(
        model_name="ResNet-50",
        framework="PyTorch",
        input_size="224 × 224",
        num_classes=1000,
        training_dataset="ImageNet (ILSVRC 2012)",
        description=(
            "ResNet-50 is a 50-layer residual network pre-trained on ImageNet. "
            "It serves as the backbone for this inference pipeline."
        ),
    )


@app.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Run Inference on an Image",
    tags=["Inference"],
)
async def predict(file: UploadFile = File(..., description="JPEG / PNG image file")):
    """
    Accepts an image file, runs it through ResNet-50, and returns the
    top-5 class predictions with confidence scores and inference latency.
    """
    # ── Validate MIME type ────────────────────────────────────────────────────
    allowed_types = {"image/jpeg", "image/png", "image/jpg", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported media type '{file.content_type}'. "
                   f"Allowed: {sorted(allowed_types)}",
        )

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as exc:
        logger.error("Failed to decode image: %s", exc)
        raise HTTPException(status_code=400, detail="Could not decode the uploaded image.")

    try:
        result = model.predict(image)
    except Exception as exc:
        logger.exception("Inference error")
        raise HTTPException(status_code=500, detail=f"Inference failed: {exc}")

    logger.info(
        "Prediction: %s (%.2f%%) | Latency: %.1f ms",
        result["predicted_class"],
        result["confidence"] * 100,
        result["inference_time_ms"],
    )
    return PredictionResponse(**result)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
