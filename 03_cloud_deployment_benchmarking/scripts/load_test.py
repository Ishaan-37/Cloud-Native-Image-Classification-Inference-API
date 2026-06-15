"""
load_test.py — Locust load-testing script for the Inference API
===============================================================
Week 3: Cloud Deployment & Performance Benchmarking
Student: Ishaan Maurya | IIT Jammu 2026

Installation:
    pip install locust Pillow

Usage (replace IP with your EC2 public IP or localhost):

  # Interactive web dashboard (open http://localhost:8089 in browser):
  locust -f load_test.py --host http://localhost:8000

  # Headless / CI mode — 20 users, 5 spawn rate, run for 60 seconds:
  locust -f load_test.py --host http://localhost:8000 \
         --headless -u 20 -r 5 --run-time 60s \
         --csv=benchmark_results/run1

Results are saved as:
    benchmark_results/run1_stats.csv
    benchmark_results/run1_failures.csv
    benchmark_results/run1_stats_history.csv
"""

import io
import os
import random

from locust import HttpUser, task, between, events
from PIL import Image


# ── Helpers ───────────────────────────────────────────────────────────────────

def _generate_jpeg(width: int = 224, height: int = 224) -> bytes:
    """Create a random-coloured in-memory JPEG to use as the test payload."""
    color = (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    )
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


# Pre-generate a small pool of test images so we're not creating them during
# every single request (reduces CPU noise in measurements)
_IMAGE_POOL = [_generate_jpeg() for _ in range(10)]


# ── User behaviour ────────────────────────────────────────────────────────────

class InferenceAPIUser(HttpUser):
    """
    Simulates a single concurrent user of the inference API.
    Each user waits between 0.5 and 2 seconds between requests,
    mimicking realistic (not flood) traffic.
    """
    wait_time = between(0.5, 2.0)

    # Ratio: 80% predict calls, 10% health, 10% info
    @task(8)
    def predict_image(self):
        """POST /predict — the main workload."""
        img_bytes = random.choice(_IMAGE_POOL)
        with self.client.post(
            "/predict",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")},
            catch_response=True,
            name="POST /predict",
        ) as response:
            if response.status_code == 200:
                data = response.json()
                # Basic sanity check on the response
                if "predicted_class" not in data:
                    response.failure("Response missing 'predicted_class'")
                else:
                    response.success()
            else:
                response.failure(
                    f"Unexpected status {response.status_code}: {response.text[:200]}"
                )

    @task(1)
    def health_check(self):
        """GET /health — lightweight liveness probe."""
        self.client.get("/health", name="GET /health")

    @task(1)
    def model_info(self):
        """GET /info — model metadata."""
        self.client.get("/info", name="GET /info")


# ── Event hooks (print summary to console) ────────────────────────────────────

@events.quitting.add_listener
def on_quitting(environment, **kwargs):
    stats = environment.runner.stats
    total = stats.total
    print("\n" + "=" * 60)
    print("  LOAD TEST SUMMARY")
    print("=" * 60)
    print(f"  Total requests   : {total.num_requests}")
    print(f"  Failures         : {total.num_failures}")
    print(f"  Avg latency (ms) : {total.avg_response_time:.1f}")
    print(f"  P50 latency (ms) : {total.get_response_time_percentile(0.50):.1f}")
    print(f"  P95 latency (ms) : {total.get_response_time_percentile(0.95):.1f}")
    print(f"  P99 latency (ms) : {total.get_response_time_percentile(0.99):.1f}")
    print(f"  Max latency (ms) : {total.max_response_time:.1f}")
    print(f"  Requests/sec     : {total.current_rps:.2f}")
    print("=" * 60 + "\n")
