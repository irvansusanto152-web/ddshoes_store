# DD Shoes POS System

Sistem Point of Sale (POS) berbasis web untuk toko sepatu DD Shoes. Dibangun menggunakan **Django** dengan tampilan modern menggunakan **Bootstrap 5**, **Material Icons**, dan **Chart.js** via CDN.

---

## 🚀 Cara Menjalankan Project

### 1. Clone Repository

```bash
git clone https://github.com/irvansusanto152-web/ddshoes_store.git
cd ddshoes_store
```

### 2. Buat & Aktifkan Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install Dependensi

```bash
pip install django
```

> **Catatan:** Project ini menggunakan CDN untuk semua aset frontend (Bootstrap, jQuery, Select2, Chart.js), sehingga tidak memerlukan npm atau build tool.

### 4. Jalankan Migrasi Database

```bash
python manage.py migrate
```

### 5. Seed Data Awal (Opsional tapi Direkomendasikan)

Perintah ini akan membuat data awal (merek, kategori, pemasok, dan akun demo):

```bash
python manage.py seed_data
```

**Akun Default yang Dibuat:**
| Role  | Username  | Password   |
|-------|-----------|------------|
| Admin | `admin`   | `admin123` |
| Kasir | `kasir01` | `kasir123` |

> ⚠️ **Penting:** Segera ganti password default setelah login pertama kali di production!

### 6. Jalankan Development Server

```bash
python manage.py runserver
```

Buka browser dan akses: **http://127.0.0.1:8000/**

---

## 🏗️ Struktur Proyek

```
pos_ddshoes2/
├── core/                       # Aplikasi utama
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py    # Command seed data awal
│   ├── migrations/             # Migrasi database
│   ├── models.py               # Definisi model data
│   ├── views.py                # Logic tampilan
│   ├── urls.py                 # URL routing
│   ├── signals.py              # Signal otomatis update stok
│   └── apps.py
├── pos_ddshoes/                # Konfigurasi project Django
│   ├── settings.py
│   ├── urls.py
│   └── docs/
│       ├── prd.md              # Product Requirements Document
│       └── task.md             # Checklist pengerjaan
├── templates/                  # Template HTML
├── static/                     # File statis (CSS)
│   └── css/
│       └── style.css
└── manage.py
```

---

## 🎯 Fitur Utama

### 👨‍💼 Role Admin
- **Dashboard** — Statistik penjualan, grafik tren, produk teratas
- **Master Data** — Kelola Merek, Kategori, Pemasok
- **Katalog Produk** — CRUD produk dengan foto, harga, ukuran, kondisi
- **Barang Masuk** — Catat penerimaan stok dari pemasok (stok otomatis bertambah)
- **Laporan Penjualan** — Filter by tanggal/kasir/metode bayar, ekspor/cetak PDF
- **Laporan Inventory** — Valuasi aset (total modal & potensi pendapatan)
- **Data Closing** — Pantau rekapan tutup kasir seluruh karyawan
- **Manajemen User** — Kelola akun kasir

### 🛒 Role Kasir
- **POS Transaksi** — Interface dua panel, real-time search, keranjang dinamis
- **Struk Digital** — Receipt modal yang bisa dicetak (thermal 80mm ready)
- **Katalog Produk** — Lihat ketersediaan stok (read-only)
- **Closing Shift** — Input kas fisik, kalkulasi selisih otomatis, kunci data

### ⚙️ Fitur Teknis
- **Auto stok update** via Django Signals (StockIn ↑ stok, Transaction ↓ stok)
- **Role-based access** — URL protection dengan `@login_required` + role check
- **Responsive design** — Mobile-friendly dengan sidebar toggle + backdrop
- **AJAX-powered** — Operasi CRUD tanpa page refresh

---

## 🛠️ Tech Stack

| Komponen    | Teknologi                               |
|-------------|------------------------------------------|
| Backend     | Django 4.x (Python)                      |
| Database    | SQLite (development)                     |
| Frontend    | Bootstrap 5.3, Material Icons           |
| Charts      | Chart.js (CDN)                          |
| Select Input| Select2 (CDN)                           |
| JS Library  | jQuery 3.6 (CDN)                        |
| Fonts       | Google Fonts — Inter                    |

---

## 📋 Perintah Berguna

```bash
# Jalankan sistem check
python manage.py check

# Buat migrasi baru (setelah edit models.py)
python manage.py makemigrations

# Seed data awal
python manage.py seed_data

# Akses Django Admin
python manage.py createsuperuser
# lalu buka http://127.0.0.1:8000/admin/
```

---

## 📄 Lisensi

Project ini dibuat untuk keperluan internal DD Shoes Store. Hak cipta dilindungi.
