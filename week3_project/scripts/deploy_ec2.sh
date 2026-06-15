#!/usr/bin/env bash
# =============================================================================
#  deploy_ec2.sh
#  One-shot script to set up a fresh Amazon Linux 2023 / Ubuntu 22.04 EC2
#  instance and run the Medical Image Inference API container.
#
#  Run this ON THE EC2 INSTANCE after SSH-ing in:
#    chmod +x deploy_ec2.sh
#    ./deploy_ec2.sh
# =============================================================================

set -euo pipefail          # Exit immediately on error; treat unset vars as errors

echo "======================================================"
echo " Medical Image Inference API — EC2 Deployment Script"
echo " IIT Jammu Summer Internship 2026"
echo "======================================================"

# ── 1. Detect OS and install Docker ───────────────────────────────────────────
echo "[1/6] Installing Docker …"

if command -v apt-get &>/dev/null; then
    # Ubuntu / Debian
    sudo apt-get update -qq
    sudo apt-get install -y -qq docker.io docker-compose-plugin curl git
    sudo systemctl enable --now docker
    sudo usermod -aG docker "$USER"

elif command -v dnf &>/dev/null; then
    # Amazon Linux 2023 / Fedora
    sudo dnf update -y -q
    sudo dnf install -y docker git curl
    sudo systemctl enable --now docker
    sudo usermod -aG docker "$USER"

else
    echo "ERROR: Unsupported OS. Install Docker manually." >&2
    exit 1
fi

echo "  Docker installed: $(docker --version)"

# ── 2. Clone / copy project files ─────────────────────────────────────────────
echo "[2/6] Setting up project directory …"

PROJECT_DIR="$HOME/medical-inference-api"
mkdir -p "$PROJECT_DIR"

# If you pushed your code to GitHub, replace the URL below:
# git clone https://github.com/YOUR_USERNAME/medical-inference-api.git "$PROJECT_DIR"
# For now, we assume you SCP'd the files to the instance.
echo "  Project directory: $PROJECT_DIR"
echo "  NOTE: Upload your project files to $PROJECT_DIR via:"
echo "        scp -r ./week2_project/* ec2-user@<EC2_IP>:$PROJECT_DIR/"

cd "$PROJECT_DIR"

# ── 3. Configure environment ───────────────────────────────────────────────────
echo "[3/6] Writing .env file …"
cat > .env << 'EOF'
LOG_LEVEL=info
WORKERS=2
EOF

# ── 4. Build Docker image ──────────────────────────────────────────────────────
echo "[4/6] Building Docker image (this may take several minutes) …"
docker compose build --no-cache

# ── 5. Start the container ────────────────────────────────────────────────────
echo "[5/6] Starting the API container …"
docker compose up -d

# Wait for the container to be healthy
echo "  Waiting for health check to pass …"
MAX_WAIT=120
ELAPSED=0
until docker inspect --format='{{.State.Health.Status}}' inference_api 2>/dev/null | grep -q "healthy"; do
    sleep 5
    ELAPSED=$((ELAPSED + 5))
    if [ "$ELAPSED" -ge "$MAX_WAIT" ]; then
        echo "  WARNING: Health check did not pass within ${MAX_WAIT}s. Check logs:"
        echo "           docker compose logs -f api"
        break
    fi
    echo "  Still waiting … (${ELAPSED}s elapsed)"
done

# ── 6. Verify deployment ───────────────────────────────────────────────────────
echo "[6/6] Verifying deployment …"

PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "YOUR_EC2_IP")

HEALTH=$(curl -s http://localhost:8000/health || echo '{"error": "API not responding"}')
echo "  Health check response: $HEALTH"

echo ""
echo "======================================================"
echo " ✅ DEPLOYMENT COMPLETE"
echo "======================================================"
echo ""
echo "  API is live at:  http://${PUBLIC_IP}:8000"
echo "  Swagger UI:      http://${PUBLIC_IP}:8000/docs"
echo ""
echo "  Useful commands:"
echo "    docker compose logs -f api    ← stream logs"
echo "    docker compose down           ← stop"
echo "    docker stats inference_api    ← resource usage"
echo ""
