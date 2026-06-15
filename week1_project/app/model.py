"""
model.py — ResNet-50 model loading, preprocessing, and inference.
"""

import time
import json
import os
import urllib.request
import logging

import torch
import torchvision.transforms as T
from torchvision import models
from PIL import Image

logger = logging.getLogger(__name__)

# URL for human-readable ImageNet class labels
_LABELS_URL = (
    "https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels"
    "/master/imagenet-simple-labels.json"
)
_LABELS_PATH = "imagenet_labels.json"

# ImageNet normalisation constants
_IMAGENET_MEAN = [0.485, 0.456, 0.406]
_IMAGENET_STD  = [0.229, 0.224, 0.225]


class ResNetModel:
    """Wraps a pre-trained ResNet-50 for single-image inference."""

    def __init__(self) -> None:
        self.is_loaded = False
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info("Using device: %s", self.device)

        self._load_labels()
        self._build_model()
        self._build_transform()

    # ── Private helpers ───────────────────────────────────────────────────────

    def _build_model(self) -> None:
        """Download (or load from cache) the pre-trained weights and set eval mode."""
        logger.info("Initialising ResNet-50 …")
        # weights=DEFAULT uses the best available ImageNet weights
        self.model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        self.model.eval()
        self.model.to(self.device)
        self.is_loaded = True
        logger.info("ResNet-50 ready on %s.", self.device)

    def _build_transform(self) -> None:
        """Standard ImageNet preprocessing pipeline."""
        self.transform = T.Compose(
            [
                T.Resize(256),                # Resize shorter side to 256 px
                T.CenterCrop(224),            # Crop centre 224×224
                T.ToTensor(),                 # HWC uint8 → CHW float32 [0,1]
                T.Normalize(mean=_IMAGENET_MEAN, std=_IMAGENET_STD),
            ]
        )

    def _load_labels(self) -> None:
        """Fetch/cache the 1 000 human-readable ImageNet class names."""
        if not os.path.exists(_LABELS_PATH):
            logger.info("Downloading ImageNet labels …")
            urllib.request.urlretrieve(_LABELS_URL, _LABELS_PATH)
        with open(_LABELS_PATH, "r") as fh:
            self.labels: list[str] = json.load(fh)
        logger.info("Loaded %d class labels.", len(self.labels))

    # ── Public API ────────────────────────────────────────────────────────────

    def predict(self, image: Image.Image, top_k: int = 5) -> dict:
        """
        Run ResNet-50 inference on a PIL image.

        Parameters
        ----------
        image : PIL.Image  –  RGB image (any size; preprocessing handles resizing)
        top_k : int        –  Number of top predictions to return (default 5)

        Returns
        -------
        dict with keys:
            predicted_class, class_id, confidence,
            top_5_predictions, inference_time_ms, device_used
        """
        t0 = time.perf_counter()

        # Pre-process: add batch dimension → [1, 3, 224, 224]
        tensor = self.transform(image).unsqueeze(0).to(self.device)

        # Forward pass (no gradient computation needed)
        with torch.no_grad():
            logits = self.model(tensor)

        # Convert logits → probabilities
        probs = torch.nn.functional.softmax(logits[0], dim=0)

        # Top-K results
        top_probs, top_indices = torch.topk(probs, k=min(top_k, len(self.labels)))

        latency_ms = (time.perf_counter() - t0) * 1_000

        top_predictions = [
            {
                "label":      self.labels[idx.item()],
                "class_id":   idx.item(),
                "confidence": round(prob.item(), 6),
            }
            for prob, idx in zip(top_probs, top_indices)
        ]

        return {
            "predicted_class":   top_predictions[0]["label"],
            "class_id":          top_predictions[0]["class_id"],
            "confidence":        top_predictions[0]["confidence"],
            "top_5_predictions": top_predictions,
            "inference_time_ms": round(latency_ms, 2),
            "device_used":       str(self.device),
        }
