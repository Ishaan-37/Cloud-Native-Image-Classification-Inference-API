# Performance Benchmarking Log
## Medical Image Inference API — Week 3
**Student:** Ishaan Maurya | **Institution:** IIT Jammu | **Date:** ___________

---

## 1. Test Environment

| Parameter | Value |
|-----------|-------|
| EC2 Instance Type | t2.micro / t3.medium *(t3.micro)* |
| vCPUs | *(2)* |
| RAM | *(1 GB)* |
| Operating System | Ubuntu 22.04 LTS |
| Docker Version | *(29.1.3)* |
| API Framework | FastAPI 0.111.0 |
| Model | ResNet-50 (PyTorch) |
| Inference Device | CPU |
| EC2 Region | us-east-1 (N. Virginia) |

---

## 2. Baseline — Single Request Latency

Not measured.

Reason:

ApacheBench (ab) was used for benchmarking instead of individual curl latency measurements.

```

| Run | Latency (ms) |
|-----|-------------|
| 1 | |
| 2 | |
| 3 | |
| 4 | |
| 5 | |
| 6 | |
| 7 | |
| 8 | |
| 9 | |
| 10 | |
| **Average** | |
| **Min** | |
| **Max** | |

---

## 3. Load Test — Concurrent Users

ApacheBench (ab) was used instead of Locust.


---

## 4. Summary Table (All Runs)

| VUs | Avg (ms)   | RPS        | Failure %  |
| --- | ---------- | ---------- | ---------- |
| 5   | 5.282      | 946.57     | 0          |
| 10  | 6.592      | 1516.90    | 0          |
| 20  | Not Tested | Not Tested | Not Tested |


---

## 5. Observations & Bottleneck Analysis

At 5 concurrent users, the API responded consistently with an average latency of 5.282 ms and achieved 946.57 requests per second with zero failed requests. Increasing concurrency to 10 users slightly increased average latency to 6.592 ms while improving throughput to 1516.90 requests per second. The main bottleneck observed during development was CPU-bound inference and storage limitations during Docker image construction. After optimizing PyTorch installation and fixing permission issues, the application remained stable with zero failures.


---

## 6. Bottleneck Identified

- [x] CPU-bound inference (model forward pass)
- [ ] I/O-bound image decoding
- [ ] Network latency (client ↔ EC2)
- [x] Uvicorn worker count too low
- [ ] Memory pressure / swapping

---

## 7. Optimisations Applied

| Optimisation                         | Effect                            |
| ------------------------------------ | --------------------------------- |
| Increased Uvicorn workers from 1 → 2 | Improved throughput               |
| Model loaded once at startup         | Reduced repeated loading overhead |
| CPU-only PyTorch                     | Reduced storage usage             |
| Increased EBS storage                | Solved `No space left on device`  |


---

## 8. EC2 Security Group Configuration

| Rule Type | Protocol | Port | Source |
|-----------|----------|------|--------|
| Inbound | TCP | 22 | Your IP (SSH) |
| Inbound | TCP | 80 | 0.0.0.0/0 (Nginx HTTP) |
| Inbound | TCP | 8000 | 0.0.0.0/0 (Direct API) |
| Outbound | All | All | 0.0.0.0/0 |

---

## 9. Live API URL

```
http://13.220.179.104:8000

```

Swagger Docs: `http://13.220.179.104:8000/docs`
