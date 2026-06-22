# Panduan Deploy ke VPS dengan Coolify

Coolify adalah self-hosted PaaS yang mengelola Nginx, SSL (Let's Encrypt), dan domain secara otomatis.

---

## Arsitektur Penyimpanan Data

| Path di container | Volume        | Keterangan                                      |
|-------------------|---------------|-------------------------------------------------|
| `/app/data/`      | `db_volume`   | Database SQLite — persistent, tidak boleh hilang |
| `/app/media/`     | `media_volume`| Foto produk upload — persistent                  |
| `/app/staticfiles/` | *(tidak di-mount)* | Di-bake ke image saat build, tidak perlu volume |

**Prinsip:** Data penting (DB + media) disimpan di Docker volume yang terpisah dari image.
Saat kamu push kode baru dan Coolify rebuild image, volume tidak tersentuh → data aman.

---

## Deploy Pertama Kali

### 1. Setup di Coolify Dashboard

**General:**
- Port: `8000`
- Health Check Path: `/health/`
- Build Pack: `Dockerfile`

**Environment Variables:**

| Key | Value |
|-----|-------|
| `SECRET_KEY` | *(generate: `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`)* |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `ddshoespos.my.id` |
| `CSRF_TRUSTED_ORIGINS` | `https://ddshoespos.my.id` |
| `TIME_ZONE` | `Asia/Jakarta` |

**Storages (di Coolify: Applications → Storages):**

| Source Path | Keterangan |
|-------------|------------|
| `/app/data` | Database SQLite |
| `/app/media` | Foto produk |

> ⚠️ Pastikan `/app/staticfiles` TIDAK ada di Storages — static files sudah di-bake ke image.

### 2. Deploy

Klik **Deploy** di Coolify. Proses otomatis:
1. Build image (termasuk `collectstatic`)
2. Jalankan container
3. `migrate` otomatis jalan saat container start (sudah di CMD)
4. Gunicorn mulai melayani request

### 3. Buat Superuser (sekali saja)

```bash
sudo docker exec -it <nama_container> python manage.py createsuperuser
```

Buat juga UserProfile untuk superuser:

```bash
sudo docker exec -it <nama_container> python manage.py shell -c "
from django.contrib.auth.models import User
from core.models import UserProfile
for u in User.objects.all():
    obj, created = UserProfile.objects.get_or_create(user=u, defaults={'role': 'admin'})
    print(u.username, obj.role, created)
"
```

---

## Update Kode (Rutin)

```bash
git add .
git commit -m "deskripsi perubahan"
git push origin master
```

Coolify otomatis rebuild image dan redeploy. Yang terjadi:
- ✅ Image baru di-build dengan kode terbaru
- ✅ `collectstatic` jalan ulang → static files terbaru di-bake ke image
- ✅ `migrate` otomatis jalan saat container start baru
- ✅ Volume `db_volume` dan `media_volume` tidak tersentuh → **data aman**
- ✅ Zero downtime (Coolify stop container lama setelah container baru healthy)

---

## Backup Database

```bash
# Copy database dari volume ke host
sudo docker cp $(sudo docker ps -qf "name=go2ij") :/app/data/db.sqlite3 ~/db_backup_$(date +%Y%m%d).sqlite3
```

---

## Troubleshooting

**Static files hancur / CSS tidak muncul:**
Static files sudah di-bake ke image. Pastikan `/app/staticfiles` TIDAK di-mount sebagai volume di Coolify Storages.

**Database hilang setelah redeploy:**
Pastikan volume `/app/data` terdaftar di Coolify Storages dan path-nya tepat.

**500 error setelah login:**
Jalankan shell command buat UserProfile di atas.

**CSRF error:**
Pastikan env var `CSRF_TRUSTED_ORIGINS=https://ddshoespos.my.id` ada di Coolify dashboard.
