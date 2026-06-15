"""
schemas.py — Pydantic models that define the API request/response contract.
"""

from pydantic import BaseModel, Field
from typing import List


# ── System schemas ────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = Field(..., example="healthy")
    model_loaded: bool = Field(..., example=True)
    timestamp: str = Field(..., example="2026-06-01T10:00:00Z")

    model_config = {"json_schema_extra": {
        "example": {
            "status": "healthy",
            "model_loaded": True,
            "timestamp": "2026-06-01T10:00:00Z",
        }
    }}


class ModelInfoResponse(BaseModel):
    model_name: str = Field(..., example="ResNet-50")
    framework: str = Field(..., example="PyTorch")
    input_size: str = Field(..., example="224 × 224")
    num_classes: int = Field(..., example=1000)
    training_dataset: str = Field(..., example="ImageNet (ILSVRC 2012)")
    description: str


# ── Inference schemas ─────────────────────────────────────────────────────────

class TopPrediction(BaseModel):
    """A single class prediction with its confidence score."""
    label: str     = Field(..., example="cat")
    class_id: int  = Field(..., example=281)
    confidence: float = Field(..., ge=0.0, le=1.0, example=0.843)


class PredictionResponse(BaseModel):
    """Full inference result returned by the /predict endpoint."""
    predicted_class: str   = Field(..., example="tabby cat")
    class_id: int          = Field(..., example=281)
    confidence: float      = Field(..., ge=0.0, le=1.0, example=0.843)
    top_5_predictions: List[TopPrediction]
    inference_time_ms: float = Field(..., example=42.3)
    device_used: str         = Field(..., example="cpu")

    model_config = {"json_schema_extra": {
        "example": {
            "predicted_class": "tabby cat",
            "class_id": 281,
            "confidence": 0.843,
            "top_5_predictions": [
                {"label": "tabby cat",   "class_id": 281, "confidence": 0.843},
                {"label": "tiger cat",   "class_id": 282, "confidence": 0.091},
                {"label": "Egyptian cat","class_id": 285, "confidence": 0.041},
                {"label": "lynx",        "class_id": 287, "confidence": 0.012},
                {"label": "persian cat", "class_id": 283, "confidence": 0.007},
            ],
            "inference_time_ms": 42.3,
            "device_used": "cpu",
        }
    }}
