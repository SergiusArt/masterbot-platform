FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Copy shared module
COPY shared /app/shared

# Copy requirements and install
COPY bablo_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY bablo_service /app

# Set timezone
ENV TZ=Europe/Moscow

# Run service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
