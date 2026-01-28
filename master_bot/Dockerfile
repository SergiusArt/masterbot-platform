FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy shared module
COPY shared /app/shared

# Copy requirements and install dependencies
COPY master_bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY master_bot /app

# Set Python path
ENV PYTHONPATH=/app

# Run the bot
CMD ["python", "main.py"]
