# Panduan Deploy ke VPS dengan Coolify

Coolify adalah self-hosted PaaS yang mengelola Nginx, SSL (Let's Encrypt), dan domain secara otomatis. Kamu hanya perlu push kode dan konfigurasi environment variables.

---

## Prasyarat

- VPS dengan Ubuntu 20.04 / 22.04, minimal RAM 2GB
- Coolify sudah terinstall di VPS ([panduan install Coolify](https://coolify.io/docs/installation))
- Repository sudah di-push ke GitHub / GitLab / Gitea

---

## Langkah Deploy

### 1. Install Coolify di VPS

Jalankan di terminal VPS:

```bash
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

Setelah selesai, akses Coolify via `http://IP_VPS:8000` dan buat akun admin.

---

### 2. Tambah Repository di Coolify

1. Buka Coolify dashboard
2. Klik **Projects** → **New Project** → beri nama (misal: `pos-ddshoes`)
3. Klik **New Resource** → pilih **Application**
4. Pilih source: **GitHub / GitLab / Gitea** → connect repo `pos_ddshoes2`
5. Branch: `master`
6. Build Pack: pilih **Dockerfile** (Coolify akan otomatis detect `Dockerfile` di root)

---

### 3. Konfigurasi di Coolify Dashboard

Di halaman konfigurasi aplikasi:

**General:**
- Port: `8000`
- Health Check Path: `/health/`

**Environment Variables** — tambahkan satu per satu:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | *(generate di bawah)* |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `your-domain.com,www.your-domain.com` |
| `TIME_ZONE` | `Asia/Jakarta` |

> Generate SECRET_KEY di terminal VPS:
> ```bash
> python3 -c "import secrets; print(secrets.token_urlsafe(50))"
> ```

**Domain:**
- Masukkan domain kamu, contoh: `pos.your-domain.com`
- Coolify otomatis setup SSL via Let's Encrypt

---

### 4. Deploy Pertama Kali

Setelah konfigurasi selesai, klik tombol **Deploy** di Coolify dashboard.

Coolify akan otomatis:
1. Clone repository
2. Build Docker image dari `Dockerfile`
3. Jalankan container
4. Setup SSL dan routing domain

Setelah build selesai, jalankan migrasi dan buat superuser lewat Coolify terminal:

```bash
# Buka terminal di Coolify: Applications → pos-ddshoes → Terminal
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

---

### 5. Deploy Update Selanjutnya

Cukup push ke branch `master`:

```bash
git push origin master
```

Coolify bisa dikonfigurasi untuk **auto-deploy** saat ada push baru (webhook otomatis), atau klik manual **Redeploy** di dashboard.

---

### 6. Persistent Storage (Penting!)

Pastikan Coolify memetakan volume untuk data yang tidak boleh hilang saat redeploy.

Di Coolify: **Applications → pos-ddshoes → Storages**, tambahkan:

| Source Path (di container) | Keterangan |
|----------------------------|------------|
| `/app/media` | Upload foto produk |
| `/app/db.sqlite3` | Database SQLite |
| `/app/staticfiles` | Static files hasil collectstatic |

---

## Backup Database

Dari terminal VPS:

```bash
# Masuk ke container
docker exec -it pos_ddshoes_web bash

# Backup
cp /app/db.sqlite3 /app/db_backup_$(date +%Y%m%d).sqlite3
exit

# Copy ke host
docker cp pos_ddshoes_web:/app/db_backup_$(date +%Y%m%d).sqlite3 ~/
```

---

## Struktur File Docker

```
pos_ddshoes2/
├── Dockerfile          ← Image Python + Gunicorn (dipakai Coolify)
├── docker-compose.yml  ← Referensi lokal (Coolify pakai Dockerfile langsung)
├── .env.example        ← Template env (isi nilainya di Coolify dashboard)
├── .dockerignore       ← File yang dikecualikan dari image
└── nginx/              ← Tidak dipakai di Coolify (Coolify handle Nginx sendiri)
```

> **Catatan:** File `nginx/` dan service `nginx` di `docker-compose.yml` tidak digunakan saat deploy via Coolify. Coolify sudah menyediakan reverse proxy dan SSL secara built-in.
