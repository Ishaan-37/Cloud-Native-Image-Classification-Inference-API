# Week 2 — Containerisation & Environment Standardisation

**Student:** Ishaan Maurya | IIT Jammu Summer Internship 2026

---

## Goal

Package the Week 1 FastAPI application into a **Docker container** so it can run
identically on any machine — your laptop, a labmate's PC, or an AWS EC2 instance —
without installing Python, PyTorch, or any other dependency manually.

---

## What's New in Week 2

| File | Purpose |
|------|---------|
| `Dockerfile` | Instructions to build the container image (multi-stage) |
| `docker-compose.yml` | Defines the full stack; lets you start everything with one command |
| `.dockerignore` | Tells Docker which files to skip (keeps image lean) |

The `app/` folder, `requirements.txt`, and `README.md` are copied from Week 1.

---

## Prerequisites

Install **Docker Desktop** from https://www.docker.com/products/docker-desktop/
(available for Windows, macOS, Linux — free for students).

Verify installation:
```bash
docker --version          # Docker version 25.x.x
docker compose version    # Docker Compose version v2.x.x
```

---

## Step-by-Step: Build & Run

### Step 1 — Copy Week 1 app folder into this directory

```
week2_project/
├── app/             ← copy from Week 1
│   ├── __init__.py
│   ├── main.py
│   ├── model.py
│   └── schemas.py
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
└── requirements.txt ← copy from Week 1
```

### Step 2 — Build the Docker image

```bash
docker compose build
```

You'll see Docker:
1. Pull `python:3.11-slim` base image
2. Install system libraries
3. Install all Python packages (Stage 1 / builder)
4. Create a lean runtime image (Stage 2)
5. Copy your app code in

This takes ~5–10 min on first run (downloads PyTorch). After that, rebuilds are
instant unless `requirements.txt` changes (Docker layer caching).

### Step 3 — Start the container

```bash
docker compose up
```

OR to run in the background (detached mode):
```bash
docker compose up -d
```

Watch for this line in the logs:
```
inference_api  | INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 4 — Test it

```bash
# From your host machine (not inside the container)
curl http://localhost:8000/health
```

Or open `http://localhost:8000/docs` in your browser.

### Step 5 — Stop the container

```bash
docker compose down
```

---

## Useful Docker Commands (Reference)

```bash
# See running containers
docker ps

# See all images on your machine
docker images

# Stream live logs
docker compose logs -f api

# Open a shell INSIDE the running container (useful for debugging)
docker exec -it inference_api bash

# Check container resource usage (CPU, RAM)
docker stats inference_api

# Remove everything (containers, networks, volumes)
docker compose down -v --rmi all
```

---

## Why Multi-Stage Build?

The `Dockerfile` uses two stages:

```
Stage 1 (builder) → has gcc + build tools → installs heavy Python packages
Stage 2 (runtime) → NO build tools → only the installed packages + your code
```

**Result:** The final image is ~40% smaller than a single-stage build.
Smaller images = faster deploys to EC2 in Week 3.

---

## Verifying Reproducibility (Deliverable)

To prove the container works from a **clean environment** (what the evaluator checks):

```bash
# Remove any local Python environment
# (The container has its own isolated environment — nothing from your PC leaks in)

# Rebuild from scratch with no cache
docker compose build --no-cache

# Run it
docker compose up -d

# Hit the predict endpoint
curl -X POST http://localhost:8000/predict \
     -F "file=@any_image.jpg"
```

If this works with just Docker installed (no Python, no pip, no venv), Week 2 is done. ✅

---

## Week 2 Deliverable Checklist

- [x] `Dockerfile` with multi-stage build
- [x] `docker-compose.yml` for one-command startup
- [x] `.dockerignore` to keep image lean
- [x] Container starts from a clean environment (no local deps)
- [x] `/health` endpoint reachable from host at `localhost:8000`
- [x] Screenshot of `docker ps` showing container running
- [x] Screenshot of `docker images` showing image size
