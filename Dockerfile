# Multi-stage Docker build for Fantastic Palm Tree framework
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Set working directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt requirements-lock.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --no-deps -r requirements-lock.txt

# Development stage
FROM base as development

# Install development dependencies
RUN pip install -e ".[dev,test]"

# Copy source code
COPY --chown=app:app . .

# Switch to non-root user
USER app

# Default command for development
CMD ["python", "-m", "uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production

# Copy only necessary files
COPY --chown=app:app fantastic_palm_tree/ ./fantastic_palm_tree/
COPY --chown=app:app api_server.py env_config.py ./
COPY --chown=app:app README.md LICENSE ./

# Install the package
COPY --chown=app:app pyproject.toml ./
RUN pip install -e . --no-deps

# Create data and cache directories
RUN mkdir -p /app/data /app/cache && chown -R app:app /app/data /app/cache

# Switch to non-root user
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Expose port
EXPOSE 8000

# Set environment for production
ENV ENVIRONMENT=production

# Default command for production
CMD ["python", "-m", "uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]