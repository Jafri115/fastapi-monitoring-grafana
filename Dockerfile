# Stage 1: Build stage (optional, but good for managing dependencies)
FROM python:3.9-slim AS builder
WORKDIR /install
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix="/install" -r requirements.txt

# Stage 2: Final stage
FROM python:3.9-slim
WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /install /usr/local

# Copy application code
COPY ./app /app

# Create a non-root user
RUN useradd --create-home appuser

# --- Add curl (requires root) ---
USER root
RUN apt-get update && apt-get install -y curl && apt-get clean
# --------------------------------

# Switch back to non-root user
USER appuser

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
