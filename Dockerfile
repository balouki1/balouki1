FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY devagent/ ./devagent/
COPY .env.example .env

# Create necessary directories
RUN mkdir -p devagent/data/jobs \
    devagent/data/embeddings \
    devagent/data/fpdevsml_examples \
    devagent/data/documentation

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "uvicorn", "devagent.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
