#!/bin/bash
# Script deploy untuk VPS
# Jalankan: chmod +x deploy.sh && ./deploy.sh

set -e

echo "=========================================="
echo "   POS DDShoes - Deploy ke VPS"
echo "=========================================="

# Pull perubahan terbaru
echo "[1/5] Pull kode terbaru dari Git..."
git pull origin master

# Build ulang image Docker
echo "[2/5] Build Docker image..."
docker compose build --no-cache

# Jalankan migrasi database
echo "[3/5] Jalankan migrasi database..."
docker compose run --rm web python manage.py migrate

# Collect static files
echo "[4/5] Collect static files..."
docker compose run --rm web python manage.py collectstatic --noinput

# Restart container
echo "[5/5] Restart container..."
docker compose up -d

echo ""
echo "=========================================="
echo "   Deploy selesai!"
echo "   Cek status: docker compose ps"
echo "   Cek log: docker compose logs -f web"
echo "=========================================="
