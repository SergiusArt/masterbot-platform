FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy shared module
COPY shared /app/shared

# Copy requirements and install dependencies
COPY service_template/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY service_template /app

# Set Python path
ENV PYTHONPATH=/app

# Expose port (change as needed)
EXPOSE 8002

# Run the service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
