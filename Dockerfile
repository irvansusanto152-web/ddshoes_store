FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        curl \
        wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Create directories and set ownership BEFORE collectstatic
RUN mkdir -p /app/staticfiles /app/media /app/data \
    && chown -R appuser:appgroup /app

# Switch to non-root user for collectstatic (no permission issues)
USER appuser

# Collect static files baked into image
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Auto-migrate then start gunicorn — data aman karena db di volume
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn pos_ddshoes.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120 --access-logfile - --error-logfile -"]
