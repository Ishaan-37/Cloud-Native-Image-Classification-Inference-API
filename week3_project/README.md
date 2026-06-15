# Week 3 — Cloud Deployment & Performance Benchmarking

**Student:** Ishaan Maurya | IIT Jammu Summer Internship 2026

---

## Goal

Take the Docker container from Week 2 and deploy it to a **live Amazon EC2
instance** accessible over the internet. Then measure how well it performs
under concurrent load using Locust.

---

## Files in This Folder

| File | Purpose |
|------|---------|
| `scripts/deploy_ec2.sh` | One-shot setup script — run on the EC2 instance |
| `scripts/load_test.py` | Locust load-testing script |
| `scripts/nginx.conf` | Reverse proxy config (exposes API on port 80) |
| `BENCHMARKING_LOG.md` | Fill-in template for recording all test results |

---

## Part A: Launch an EC2 Instance (AWS Console)

### Step 1 — Create an AWS Account / Log In

Go to https://aws.amazon.com and sign in.
Students: check if your institute has AWS Academy credits — IIT Jammu may.

### Step 2 — Launch Instance

1. Go to **EC2 → Instances → Launch Instance**
2. Settings:
   - **Name:** `inference-api`
   - **AMI:** `Ubuntu Server 22.04 LTS` (Free tier eligible)
   - **Instance type:** `t2.micro` (free tier) or `t3.small` for better performance
   - **Key pair:** Create new → download `.pem` file → **keep it safe, you cannot re-download it**
   - **Network:** Allow SSH (port 22) from your IP
3. Click **Launch Instance**
4. Wait ~1 min → Instance state: `running`

### Step 3 — Configure Security Group (open port 8000)

1. Click your instance → **Security** tab → click the security group
2. **Inbound rules → Edit inbound rules → Add rule:**
   - Type: Custom TCP | Port: 8000 | Source: 0.0.0.0/0
   - Type: HTTP | Port: 80 | Source: 0.0.0.0/0 (for Nginx)
3. Save rules

---

## Part B: SSH into the EC2 Instance

```bash
# Fix key permissions (required on Mac/Linux)
chmod 400 your-key.pem

# Connect
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>
```

On Windows: use **PuTTY** or **Windows Terminal** with the .pem key.

---

## Part C: Upload Project Files to EC2

From your **local machine** (not inside EC2 SSH):

```bash
# Upload the entire Week 2 project to the instance
scp -i your-key.pem -r ./week2_project ubuntu@<EC2_PUBLIC_IP>:~/medical-inference-api/
```

---

## Part D: Run Deployment Script on EC2

Inside the EC2 SSH session:

```bash
cd ~/medical-inference-api

# Make script executable
chmod +x scripts/deploy_ec2.sh

# Run it
./scripts/deploy_ec2.sh
```

The script will:
1. Install Docker
2. Build the image
3. Start the container
4. Wait for health checks to pass
5. Print the live URL

---

## Part E: Verify Live API

```bash
# Replace with your actual EC2 IP
curl http://<EC2_PUBLIC_IP>:8000/health

# Test prediction (from your local machine)
curl -X POST http://<EC2_PUBLIC_IP>:8000/predict \
     -F "file=@any_image.jpg"
```

Open in browser: `http://<EC2_PUBLIC_IP>:8000/docs`

---

## Part F: Load Testing with Locust

### Install Locust (on your local machine)

```bash
pip install locust Pillow
```

### Run headless benchmark (20 users, 60 seconds)

```bash
mkdir -p benchmark_results

# Run all 3 test scenarios (5, 10, 20 users)
for users in 5 10 20; do
    echo "Testing with $users users..."
    locust -f scripts/load_test.py \
           --host http://<EC2_PUBLIC_IP>:8000 \
           --headless \
           -u $users -r $((users/2)) \
           --run-time 60s \
           --csv=benchmark_results/run_${users}users
    sleep 10   # Cool-down between runs
done

echo "All tests complete. Results in benchmark_results/"
```

### Or use the interactive dashboard

```bash
locust -f scripts/load_test.py --host http://<EC2_PUBLIC_IP>:8000
# Open http://localhost:8089 in your browser
```

Fill in the results in `BENCHMARKING_LOG.md`.

---

## Cost Warning ⚠️

A `t2.micro` instance costs **~$0.012/hour** (~₹1/hour).
**Always stop your instance after testing:**

```bash
# From AWS Console: Instances → select → Instance State → Stop
# Or from CLI:
aws ec2 stop-instances --instance-ids <your-instance-id>
```

A stopped instance does NOT cost compute (only storage, ~$0.10/month).

---

## Week 3 Deliverable Checklist

- [x] EC2 instance running (screenshot of AWS console)
- [x] Security groups configured (port 8000 + 80 open)
- [x] API accessible at public IP (screenshot of `/docs` in browser)
- [x] Load test with 3 concurrency levels completed
- [x] `BENCHMARKING_LOG.md` fully filled in with real numbers
- [x] Bottleneck identified and analysed
