# Use official lightweight Python 3.12 slim base image
FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

# Set working directory inside container
WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to optimize Docker layer caching
COPY requirements-render.txt .

# Install lightweight CPU-only PyTorch first (avoids multi-gigabyte CUDA dependencies)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install remaining deterministic dependencies with CPU extra-index
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements-render.txt

# Copy application code into container
COPY . .

# Create reports directory and set up non-root user permissions
RUN mkdir -p reports && \
    useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user for security
USER appuser

# Expose production port
EXPOSE 5000

# Default environment secret key (override in production via ENV)
ENV SECRET_KEY="resumeiq-default-dev-key"

# Entrypoint command to run production WSGI server
CMD ["python", "wsgi.py"]
