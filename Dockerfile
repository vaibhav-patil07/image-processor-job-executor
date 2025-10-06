# Multi-stage build for optimized image size
# Stage 1: Build stage with all dependencies
FROM python:3.13-slim AS builder

# Install build dependencies required for OpenCV, PostgreSQL, and scientific packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libglib2.0-dev \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgtk-3-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libopenblas-dev \
    liblapack-dev \
    gfortran \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create virtual environment
RUN python -m venv /opt/venv

# Activate virtual environment and upgrade pip
RUN /opt/venv/bin/pip install --upgrade pip setuptools wheel

# Copy requirements and install Python dependencies in virtual environment
COPY requirements.txt .
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime stage with minimal dependencies
FROM python:3.13-slim AS runtime

# Install runtime dependencies required for OpenCV and other packages
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libpq5 \
    libgfortran5 \
    libopenblas0 \
    libjpeg62-turbo \
    libpng16-16t64 \
    libtiff6 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy the models directory (contains CNNIQA-LIVE model)
COPY models/ ./models/

# Copy application code
COPY *.py ./

# Create uploads directory for temporary file storage
RUN mkdir -p uploads

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
# Add virtual environment to PATH
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
RUN chown -R appuser:appuser /opt/venv
USER appuser

# Health check to ensure Redis connection is available
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import redis; import os; r = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0')); r.ping()" || exit 1

# Run the background job processor
CMD ["python", "main.py"]