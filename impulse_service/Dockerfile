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

# Copy requirements and install dependencies
COPY impulse_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY impulse_service /app

# Set Python path
ENV PYTHONPATH=/app

# Set timezone
ENV TZ=Europe/Moscow

# Expose port
EXPOSE 8001

# Run the service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
