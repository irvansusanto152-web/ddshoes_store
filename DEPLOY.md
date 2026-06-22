# Panduan Deploy ke VPS

## Prasyarat VPS

- Ubuntu 20.04 / 22.04
- Docker + Docker Compose terinstall
- Minimal RAM: 1GB
- Port 80 dan 443 terbuka di firewall

## Langkah Deploy

### 1. Install Docker di VPS

```bash
# Update sistem
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose plugin
sudo apt install docker-compose-plugin -y

# Verifikasi
docker --version
docker compose version
```

### 2. Clone Repository ke VPS

```bash
git clone https://github.com/USERNAME/pos_ddshoes2.git
cd pos_ddshoes2
```

### 3. Buat File .env

```bash
cp .env.example .env
nano .env
```

Isi nilai berikut:
```
SECRET_KEY=buat-secret-key-panjang-dan-random-di-sini
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,123.456.789.0
TIME_ZONE=Asia/Jakarta
```

> Generate secret key: `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`

### 4. Setup Nginx

**Jika belum punya domain (akses via IP):**

```bash
cp nginx/nginx.http.conf nginx/nginx.conf
```

**Jika sudah punya domain (dengan SSL):**

Edit `nginx/nginx.conf`, ganti `YOUR_DOMAIN_OR_IP` dan `YOUR_DOMAIN` dengan domain kamu, lalu setup SSL:

```bash
# Jalankan dulu tanpa SSL untuk certbot
cp nginx/nginx.http.conf nginx/nginx.conf
docker compose up -d nginx

# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Dapatkan sertifikat SSL
sudo certbot certonly --webroot -w /var/www/certbot -d your-domain.com -d www.your-domain.com

# Setelah dapat sertifikat, ganti ke nginx.conf yang ada SSL
cp nginx/nginx.conf.ssl nginx/nginx.conf   # atau edit manual
docker compose restart nginx
```

### 5. Jalankan Aplikasi

```bash
# Pertama kali: build + migrate + up
docker compose build
docker compose run --rm web python manage.py migrate
docker compose run --rm web python manage.py collectstatic --noinput

# Buat superuser admin
docker compose run --rm web python manage.py createsuperuser

# Jalankan semua service
docker compose up -d

# Cek status
docker compose ps
```

### 6. Deploy Update Selanjutnya

```bash
chmod +x deploy.sh
./deploy.sh
```

---

## Perintah Berguna

```bash
# Lihat log realtime
docker compose logs -f web
docker compose logs -f nginx

# Masuk ke container
docker compose exec web bash

# Restart service tertentu
docker compose restart web

# Stop semua
docker compose down

# Backup database SQLite
docker compose exec web cp db.sqlite3 /app/db.sqlite3.backup
docker cp pos_ddshoes_web:/app/db.sqlite3 ./backup_$(date +%Y%m%d).sqlite3
```

---

## Struktur File Docker

```
pos_ddshoes2/
├── Dockerfile          ← Image Python + Gunicorn
├── docker-compose.yml  ← Orkestrasi web + nginx
├── .env                ← Variabel environment (jangan di-commit!)
├── .env.example        ← Template .env
├── .dockerignore       ← File yang dikecualikan dari image
├── deploy.sh           ← Script deploy otomatis
└── nginx/
    ├── nginx.conf      ← Konfigurasi aktif Nginx
    └── nginx.http.conf ← Fallback tanpa SSL
```
