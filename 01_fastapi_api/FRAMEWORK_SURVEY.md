# Model Serving Framework Survey
## Week 1 — Summer Internship Project, IIT Jammu 2026
**Student:** Ishaan Maurya

---

## 1. Why We Need a Serving Framework

A deep learning model saved as a `.pt` file cannot be directly used by end-users
or downstream systems. A serving framework wraps the model in an HTTP server,
exposing it through a standard API that any client can call.

---

## 2. Frameworks Evaluated

### 2.1 Flask
- **Type:** Micro web framework
- **Pros:** Simple to learn, huge community, minimal boilerplate
- **Cons:** No built-in async, no automatic validation, no interactive docs
- **Best for:** Quick prototypes

### 2.2 FastAPI ✅ *(Selected)*
- **Type:** Modern async web framework built on Starlette + Pydantic
- **Pros:**
  - Automatic Swagger/ReDoc API docs generated from type hints
  - Built-in request validation via Pydantic
  - Native async/await — handles concurrent requests efficiently
  - Python type hints = self-documenting code
  - One of the fastest Python frameworks (close to Go/NodeJS)
- **Cons:** Slightly steeper learning curve than Flask
- **Best for:** Production APIs, ML inference endpoints

### 2.3 TorchServe
- **Type:** Purpose-built model server by PyTorch/AWS
- **Pros:** Multi-model serving, batching, metrics built-in, REST + gRPC
- **Cons:** Heavyweight, complex setup, less flexible for custom logic
- **Best for:** Large-scale production with multiple models

### 2.4 Triton Inference Server (NVIDIA)
- **Type:** High-performance GPU inference server
- **Pros:** Extreme throughput, dynamic batching, multi-framework support
- **Cons:** Requires NVIDIA GPU, very complex to configure
- **Best for:** GPU clusters with heavy traffic

### 2.5 BentoML
- **Type:** ML model deployment framework
- **Pros:** Framework-agnostic, built-in batching, easy containerization
- **Cons:** Extra abstraction layer, smaller community
- **Best for:** Teams deploying many different model types

---

## 3. Decision Matrix

| Criterion              | Flask | FastAPI | TorchServe | Triton |
|------------------------|:-----:|:-------:|:----------:|:------:|
| Ease of setup          | ★★★★★ | ★★★★☆   | ★★☆☆☆      | ★☆☆☆☆  |
| Performance            | ★★★☆☆ | ★★★★★   | ★★★★☆      | ★★★★★  |
| Auto API docs          | ✗     | ✓       | ✗          | ✗      |
| Input validation       | Manual| Built-in | Manual    | Manual |
| Async support          | ✗     | ✓       | ✓          | ✓      |
| Community & docs       | ★★★★★ | ★★★★★   | ★★★☆☆      | ★★★☆☆  |
| Suitable for this project | ★★★ | ★★★★★ | ★★★☆☆    | ★★☆☆☆  |

---

## 4. Selected: FastAPI

**Rationale:** FastAPI provides the best balance of developer productivity,
performance, and built-in features (validation, docs) for a 4-week internship
project. Its type-hint-driven design also naturally enforces documentation,
which is required by the evaluation rubric.

---

## 5. References

1. FastAPI Documentation — https://fastapi.tiangolo.com
2. TorchServe GitHub — https://github.com/pytorch/serve
3. Triton Inference Server — https://github.com/triton-inference-server/server
4. BentoML Documentation — https://docs.bentoml.com
