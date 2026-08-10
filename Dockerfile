# Dockerfile for 24/7 Market Monitoring Bot
# Optimized for continuous operation with auto-restart

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create directories for persistent data
RUN mkdir -p /app/data

# Environment variables (override with docker run -e or docker-compose)
ENV PYTHONUNBUFFERED=1
ENV TZ=UTC

# Health check
HEALTHCHECK --interval=5m --timeout=30s --start-period=30s --retries=3 \
    CMD python -c "import os; exit(0 if os.path.exists('worker_24x7_state.json') else 1)"

# Run the 24/7 worker
CMD ["python", "-u", "unified_24x7_worker.py"]
