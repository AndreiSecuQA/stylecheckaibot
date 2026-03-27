FROM python:3.11-slim

# Keeps Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Signal to logger.py that file logging should be disabled
ENV DOCKER_ENV=1

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY app/ ./app/

# Create data directories (overridden by Railway volumes in production)
RUN mkdir -p /data/db /data/images

# Default env var overrides pointing to the volume mount paths
ENV DB_PATH=/data/db/stylecheck.db
ENV IMAGES_DIR=/data/images

CMD ["python", "-m", "app.main"]
