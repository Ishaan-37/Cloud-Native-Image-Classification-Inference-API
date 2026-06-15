"""
tests/test_api.py
─────────────────
Quick smoke-tests for the Medical Image Inference API.

Run with:
    pytest tests/test_api.py -v
"""

import io
import pytest
from fastapi.testclient import TestClient
from PIL import Image

# ── Adjust sys.path so we can import from the project root ────────────────────
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.main import app

client = TestClient(app)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_dummy_image(width=224, height=224, color=(128, 64, 32)) -> bytes:
    """Generate a small in-memory JPEG image for testing."""
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestHealthEndpoint:
    def test_returns_200(self):
        r = client.get("/health")
        assert r.status_code == 200

    def test_body_structure(self):
        data = client.get("/health").json()
        assert "status" in data
        assert "model_loaded" in data
        assert "timestamp" in data

    def test_status_value(self):
        data = client.get("/health").json()
        assert data["status"] == "healthy"

    def test_model_is_loaded(self):
        data = client.get("/health").json()
        assert data["model_loaded"] is True


class TestInfoEndpoint:
    def test_returns_200(self):
        r = client.get("/info")
        assert r.status_code == 200

    def test_body_structure(self):
        data = client.get("/info").json()
        assert data["model_name"] == "ResNet-50"
        assert data["num_classes"] == 1000
        assert "framework" in data


class TestPredictEndpoint:
    def test_valid_image_returns_200(self):
        img_bytes = _make_dummy_image()
        r = client.post(
            "/predict",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")},
        )
        assert r.status_code == 200

    def test_response_has_required_fields(self):
        img_bytes = _make_dummy_image()
        data = client.post(
            "/predict",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")},
        ).json()
        for field in [
            "predicted_class",
            "class_id",
            "confidence",
            "top_5_predictions",
            "inference_time_ms",
            "device_used",
        ]:
            assert field in data, f"Missing field: {field}"

    def test_top5_has_five_entries(self):
        img_bytes = _make_dummy_image()
        data = client.post(
            "/predict",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")},
        ).json()
        assert len(data["top_5_predictions"]) == 5

    def test_confidence_between_0_and_1(self):
        img_bytes = _make_dummy_image()
        data = client.post(
            "/predict",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")},
        ).json()
        assert 0.0 <= data["confidence"] <= 1.0

    def test_inference_latency_is_positive(self):
        img_bytes = _make_dummy_image()
        data = client.post(
            "/predict",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")},
        ).json()
        assert data["inference_time_ms"] > 0

    def test_invalid_file_type_returns_415(self):
        r = client.post(
            "/predict",
            files={"file": ("test.txt", b"not an image", "text/plain")},
        )
        assert r.status_code == 415

    def test_corrupted_image_returns_400(self):
        r = client.post(
            "/predict",
            files={"file": ("bad.jpg", b"\xff\xd8\xff corrupted", "image/jpeg")},
        )
        assert r.status_code == 400
