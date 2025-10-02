# Docker Deployment Guide

This document provides instructions for deploying the Image Processor Job Executor using Docker.

## Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository and navigate to the project directory**
   ```bash
   cd image-processor-job-executor
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **View logs**
   ```bash
   docker-compose logs -f image-processor-job
   ```

4. **Stop services**
   ```bash
   docker-compose down
   ```

### Using Docker Build

1. **Build the image**
   ```bash
   docker build -t image-processor-job .
   ```

2. **Run the container**
   ```bash
   docker run -d \
     --name image-processor-job \
     -e DATABASE_URL=postgresql://user:pass@host:5432/db \
     -e REDIS_URL=redis://redis-host:6379/0 \
     -e STORAGE_END_POINT=http://minio:9000 \
     -e ACCESS_KEY=your-access-key \
     -e SECRET_KEY=your-secret-key \
     -e STORAGE_BUCKET=image-processor \
     image-processor-job
   ```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://localhost:5432/image_processor` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `QUEUE_NAME` | BullMQ queue name | `image-processor` |
| `STORAGE_END_POINT` | S3/MinIO endpoint URL | - |
| `STORAGE_REGION` | Storage region | - |
| `ACCESS_KEY` | Storage access key | - |
| `SECRET_KEY` | Storage secret key | - |
| `STORAGE_BUCKET` | Storage bucket name | - |
| `LOG_LEVEL` | Logging level | `INFO` |
| `JOB_TIMEOUT` | Job timeout in seconds | `30` |
| `MAX_RETRIES` | Maximum job retries | `3` |

## Docker Features

### Multi-Stage Build
The Dockerfile uses a multi-stage build approach:
- **Builder stage**: Installs all build dependencies and Python packages
- **Runtime stage**: Contains only runtime dependencies and application code

This approach significantly reduces the final image size while maintaining all necessary functionality.

### Security Features
- Runs as non-root user (`appuser`)
- Minimal runtime dependencies
- No unnecessary packages in final image

### Health Check
The container includes a health check that verifies Redis connectivity:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import redis; import os; r = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0')); r.ping()" || exit 1
```

## Production Deployment

### Docker Swarm
```bash
docker stack deploy -c docker-compose.yml image-processor
```

### Kubernetes
For Kubernetes deployment, convert the docker-compose.yml using tools like Kompose:
```bash
kompose convert -f docker-compose.yml
```

### Resource Requirements
- **CPU**: 1-2 cores recommended
- **Memory**: 2-4GB RAM (depends on image processing load)
- **Storage**: Minimal (temporary uploads directory)

## Monitoring

### Logs
```bash
# View real-time logs
docker-compose logs -f image-processor-job

# View logs with timestamps
docker-compose logs -t image-processor-job
```

### Health Status
```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' image-processor-job-executor
```

## Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   - Verify Redis is running: `docker-compose ps redis`
   - Check Redis logs: `docker-compose logs redis`

2. **Database Connection Failed**
   - Verify PostgreSQL is running: `docker-compose ps postgres`
   - Check database credentials in environment variables

3. **Storage Access Issues**
   - Verify MinIO/S3 credentials
   - Check storage endpoint accessibility

4. **Job Processing Errors**
   - Check application logs: `docker-compose logs image-processor-job`
   - Verify all required models are present in the `models/` directory

### Debug Mode
To run in debug mode with more verbose logging:
```bash
docker-compose up -e LOG_LEVEL=DEBUG
```

## Development

### Local Development with Docker
```bash
# Build development image
docker build -t image-processor-job:dev .

# Run with volume mounts for development
docker run -it --rm \
  -v $(pwd):/app \
  -e DATABASE_URL=postgresql://localhost:5432/image_processor \
  image-processor-job:dev
```
