# Northflank Deployment Guide

## Memory Issues During Build - Solutions Applied

### 1. **CPU-Only PyTorch** ✅ APPLIED
- Changed to PyTorch CPU-only version to reduce download and build memory
- This reduces the wheel size from ~800MB to ~200MB
- Added `--extra-index-url https://download.pytorch.org/whl/cpu` in requirements.txt

### 2. **opencv-python-headless** ✅ APPLIED
- Switched from `opencv-python` to `opencv-python-headless`
- Removes GUI dependencies (Qt, GTK) which are not needed in containers
- Reduces package size significantly

### 3. **Optimized Build Process** ✅ APPLIED
- Added `--no-build-isolation` flag to reduce memory during pip install
- Added cleanup of `.pyc` files and `__pycache__` directories
- Using `--no-cache-dir` to avoid caching large packages

## Additional Northflank Configuration Recommendations

### Build Settings
```
Build Memory: 2GB minimum (4GB recommended for PyTorch)
Build Timeout: 900 seconds (15 minutes)
```

### Runtime Settings
```
Memory: 1GB minimum (2GB recommended for image processing)
CPU: 0.5 vCPU minimum (1 vCPU recommended)
```

### Environment Variables to Set in Northflank
```
REDIS_URL=<your-redis-url>
DB_URL=<your-postgres-url>
AWS_ACCESS_KEY_ID=<your-aws-key>
AWS_SECRET_ACCESS_KEY=<your-aws-secret>
AWS_BUCKET_NAME=<your-bucket>
AWS_REGION=<your-region>
QUEUE_NAME=image-processor-queue
PORT=8080
```

### Health Check Configuration
```
Path: /health
Port: 8080
Initial Delay: 30 seconds
Period: 30 seconds
Timeout: 10 seconds
```

## Alternative Solutions (If Still Having Memory Issues)

### Option 1: Split Build into Stages
If you're still hitting memory limits, consider building the Docker image locally or in GitHub Actions, then pushing to a registry:

```bash
# Build locally
docker build -t your-registry/image-processor:latest .
docker push your-registry/image-processor:latest
```

Then deploy from the pre-built image in Northflank.

### Option 2: Use Smaller Base Image
Consider switching to `python:3.13-alpine` (requires additional setup for scientific packages).

### Option 3: Remove Unused Dependencies
Review if you actually need all dependencies:
- If not using PyTorch extensively, consider lighter alternatives
- Remove scipy if not needed
- Use lighter image processing libraries if possible

## Monitoring Build Memory

You can monitor build logs in Northflank to see if memory issues persist:
```
Watch for: "Killed" or "Out of memory" messages
```

## Testing Build Locally

Test the build locally with memory constraints:
```bash
docker build --memory=2g --memory-swap=2g -t image-processor-test .
```

This simulates Northflank's memory constraints.

## Auto-Ping Feature ✅ APPLIED

Added automatic ping every 30 seconds in `server.py` to keep connections alive and prevent idle timeouts.
