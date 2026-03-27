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

# Create non-root user for security
RUN addgroup --system --gid 1001 botgroup \
    && adduser --system --uid 1001 --gid 1001 --ingroup botgroup botuser

# Create data directories (overridden by Railway volumes in production)
RUN mkdir -p /data/db /data/images \
    && chown -R botuser:botgroup /data /app

USER botuser

# Default env var overrides pointing to the volume mount paths
ENV DB_PATH=/data/db/stylecheck.db
ENV IMAGES_DIR=/data/images

CMD ["python", "-m", "app.main"]
