# 📋 Task List — DD Shoes POS System
> Panduan langkah-langkah pengerjaan project dari awal sampai selesai.
> Update status setiap item: `[ ]` = belum · `[/]` = sedang · `[x]` = selesai

---

## FASE 0 — Setup Project Django

- [x] Buat Django project baru atau verifikasi project `pos_ddshoes` sudah terkonfigurasi dengan benar
- [x] Buat Django app utama (contoh: `core` atau `main`)
- [x] Konfigurasi `settings.py`:
  - [x] `INSTALLED_APPS` — daftarkan app
  - [x] `DATABASES` — SQLite3
  - [x] `MEDIA_ROOT` & `MEDIA_URL` — untuk upload foto produk
  - [x] `STATIC_ROOT` & `STATICFILES_DIRS`
  - [x] `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL`
  - [x] `MESSAGE_STORAGE` (opsional: session-based)
- [x] Konfigurasi `urls.py` utama — include URL tiap app
- [x] Salin seluruh folder `assets/` ke dalam `static/` app (Digantikan CDN sesuai instruksi user)
- [x] Buat `favicon.svg` di folder static

---

## FASE 1 — Database & Models

- [x] Buat `models.py` — definisikan semua tabel sesuai PRD:
  - [x] `UserProfile` (OneToOne ke `auth_user`, field: `role`, `phone`)
  - [x] `Categories` (field: `name`)
  - [x] `Brands` (field: `name`)
  - [x] `Suppliers` (field: `name`, `phone`, `notes`)
  - [x] `Products` (field: `category`, `brand`, `name`, `size`, `condition`, `description`, `buy_price`, `sell_price`, `stock`, `image`, `status`, `created_at`)
  - [x] `StockIns` (field: `supplier`, `received_by`, `received_date`, `notes`, `created_at`)
  - [x] `StockInDetails` (field: `stock_in`, `product`, `quantity`, `buy_price`)
  - [x] `Transactions` (field: `cashier`, `total_amount`, `payment_method`, `cash_received`, `change_amount`, `transaction_date`)
  - [x] `TransactionDetails` (field: `transaction`, `product`, `quantity`, `sell_price`, `subtotal`)
  - [x] `CashClosings` (field: `cashier`, `closing_date`, `system_cash_total`, `system_transfer_total`, `system_qris_total`, `actual_cash`, `cash_difference`, `notes`, `is_locked`, `submitted_at`)
- [x] Jalankan `python manage.py makemigrations`
- [x] Jalankan `python manage.py migrate`
- [x] Buat `signals.py` — auto-kurangi stok saat `TransactionDetails` disimpan, auto-tambah stok saat `StockInDetails` disimpan, auto-set status produk `inactive` jika stok = 0
- [x] Buat superuser admin awal: `python manage.py createsuperuser`
- [x] Daftarkan semua model ke `admin.py` (untuk debug awal)

---

## FASE 2 — Autentikasi & Base Template

### 2.1 Base Template & Layout

- [x] Buat `templates/` folder (global atau di dalam app)
- [x] Konfigurasi `TEMPLATES` di `settings.py` agar mengarah ke folder templates
- [x] Buat `base.html` — layout utama dengan:
  - [x] Load semua CSS & JS sesuai design_system (Inter font, Material Icons, Bootstrap 5, Material Admin, Select2, jQuery)
  - [x] Struktur `.body-wrapper > aside + .main-wrapper > header + .page-wrapper > main`
  - [x] `{% block pageContent %}` untuk konten halaman
  - [x] Include `navigation.html` dan `topNavigation.html`
  - [x] Include 2 global modal: `uni_modal` dan `confirm_modal`
  - [x] Implementasi helper JS global: `start_loader`, `end_loader`, `uni_modal()`, `_conf()`, `toggleSidebar()`
  - [x] Definisikan CSS Variables (`:root { --color-primary, --bg-body, ... }`) sesuai design_system
  - [x] Body background radial-gradient sudut (4 warna)
  - [x] Sistem alert overlay animasi dari Django `messages` framework (sukses/error + audio notifikasi)

- [x] Buat `navigation.html` — sidebar dark dengan:
  - [x] Background `#06091a` + border `rgba(100,200,255,0.07)`
  - [x] Particle canvas (`sb-particle-canvas`) + 2 scanline animasi
  - [x] Area brand: logo wrap dengan rotating rings + logoPulse, nama toko (Georgia font), subtitle
  - [x] Fitur upload logo kustom (klik logo → file picker → simpan di localStorage, max 2MB)
  - [x] Tombol reset logo
  - [x] Navigasi dengan `mdc-drawer-link`, section labels, glow divider
  - [x] Semua animasi sidebar: `ringRotate`, `logoPulse`, `nameBreathe`, `subBlink`, `scanMove`, `glowDot`
  - [x] Auto-detect active link dari `window.location.pathname`
  - [x] Backdrop untuk mobile

- [x] Buat `topNavigation.html` — topbar dengan:
  - [x] Hamburger menu (toggle sidebar)
  - [x] Dropdown profil user kanan (ikon mdi-shield-account untuk superuser / mdi-store untuk kasir)
  - [x] Link Admin Django (superuser only) + link Logout

### 2.2 Halaman Login

- [x] Buat view `login_view` (custom, bukan default Django)
- [x] Buat `login.html` — split layout 2 kolom:
  - [x] Kiri (flex 1.3): hero image + overlay gradient gelap + branding + slogan + glass-badge bawah
  - [x] Kanan (flex 1): form login bersih background putih
  - [x] Input username & password dengan `.saas-input` (padding + icon kiri)
  - [x] Tombol masuk `.btn-masuk` (ungu indigo, hover translateY + arrow icon slide kanan)
  - [x] Animasi `imageZoomIn` pada hero, `formSlideUp` pada form box
  - [x] Tampilkan pesan error jika login gagal
  - [x] Redirect ke dashboard sesuai role setelah login berhasil
- [x] Buat view `logout_view`
- [x] Sistem catat waktu login (`last_login` dari Django built-in)
- [x] Middleware / decorator untuk cek role pada setiap view yang memerlukan izin
- [x] Buat `urls.py` untuk autentikasi

---

## FASE 3 — Halaman Admin

### 3.1 Dashboard

- [x] Buat view `dashboard` (admin only)
- [x] Query data untuk 4 kartu metrik:
  - Total Stok (Σ semua stok produk aktif)
  - Total Produk Terjual Hari Ini (dari TransactionDetails hari ini)
  - Pendapatan Hari Ini (Σ total_amount transaksi hari ini)
  - Stok Hampir Habis (produk dengan stok ≤ 3)
- [x] Query data grafik tren pendapatan (Harian / Mingguan / Bulanan) → kirim ke template sebagai JSON
- [x] Query 5 produk terlaris (berdasarkan total quantity terjual)
- [x] Query tabel stok kritis (stok ≤ 0 atau hampir habis)
- [x] Buat `dashboard.html`:
  - [x] 4 stat cards dengan tema warna berbeda (`.card-cat`, `.card-prod`, `.card-ord`, `.card-rev`)
  - [x] Layout 7:3 grid — chart panel kiri + leaderboard kanan (`.main-grid`)
  - [x] Chart.js line chart dengan gradient fill ungu-pink sesuai design_system
  - [x] Filter tabs Harian/Mingguan/Bulanan (AJAX update chart)
  - [x] Tabel 5 produk terlaris
  - [x] Tabel stok kritis (dengan badge warning)
- [x] Endpoint AJAX untuk update data chart berdasarkan filter periode

### 3.2 Master Data — Merek (Brands)

- [x] Buat view `brands_list`, `brands_save`, `brands_delete`
- [x] Buat `brands.html`:
  - [x] Page header (`.saas-header`) dengan judul + tombol "Tambah Merek"
  - [x] Toolbar pencarian (`.saas-toolbar`) — filter real-time
  - [x] Tabel daftar merek (nama, jumlah produk terkait, aksi)
  - [x] Tombol Edit → buka `uni_modal` dengan form edit (AJAX load)
  - [x] Tombol Hapus → buka `confirm_modal` → AJAX delete
  - [x] Form tambah/edit merek (via modal)
- [x] Response JSON standar untuk semua AJAX: `{ "status": "success" }` / `{ "status": "failed", "msg": "..." }`

### 3.3 Master Data — Kategori

- [x] Buat view `categories_list`, `categories_save`, `categories_delete`
- [x] Buat `categories.html`:
  - [x] Page header + tombol "Tambah Kategori"
  - [x] Toolbar pencarian + filter
  - [x] Card grid (`.card-grid`) — tampilan kartu per kategori
  - [x] Setiap kartu: nama kategori, jumlah produk, badge status aktif/nonaktif
  - [x] Tombol edit & hapus di setiap kartu (`.btn-icon-edit`, `.btn-icon-delete`)
  - [x] Form tambah/edit via `uni_modal`

### 3.4 Master Data — Pemasok (Suppliers)

- [x] Buat view `suppliers_list`, `suppliers_save`, `suppliers_delete`
- [x] Buat `suppliers.html`:
  - [x] Page header + tombol "Tambah Pemasok"
  - [x] Toolbar pencarian
  - [x] Tabel daftar pemasok (nama, no. HP, keterangan, aksi)
  - [x] Form tambah/edit via `uni_modal` (field: nama, HP, catatan)
  - [x] Konfirmasi hapus via `confirm_modal`

### 3.5 Katalog Produk (Inventory)

- [x] Buat view `products_list`, `products_save`, `products_delete`, `products_toggle_status`
- [x] Buat `products.html`:
  - [x] Page header + tombol "Tambah Produk"
  - [x] Toolbar pencarian + filter (by Merek, Kategori, Kondisi, Stok)
  - [x] Tabel produk dengan kolom: Foto, Nama, Merek, Ukuran, Kondisi, Harga Beli, Harga Jual, Stok, Status, Aksi
  - [x] Tombol Edit produk → `uni_modal` dengan form lengkap
  - [x] Tombol Toggle Status (Aktifkan/Nonaktifkan) → AJAX
  - [x] Tombol Hapus → `confirm_modal`
- [x] Form produk (via modal):
  - [x] Select2 untuk pilih Merek & Kategori
  - [x] Field: nama, ukuran, kondisi (dropdown: Baru/Like New/Good/Fair), deskripsi
  - [x] Field harga beli, harga jual, stok awal
  - [x] Upload foto produk (ImageField)

### 3.6 Barang Masuk (Stock In)

- [x] Buat view `stockin_list`, `stockin_detail`, `stockin_save`
- [x] Buat `stockin.html` — halaman utama:
  - [x] Page header + tombol "Catat Barang Masuk"
  - [x] Toolbar filter (tanggal, pemasok)
  - [x] Tabel riwayat penerimaan (No. Dokumen, Tanggal, Pemasok, Dicatat Oleh, Jml Item, Aksi Detail)
  - [x] Link ke halaman detail per sesi penerimaan
- [x] Buat `stockin_form.html` — form catat barang masuk:
  - [x] Header form: Select2 pilih pemasok, input tanggal terima, textarea catatan
  - [x] Tabel baris detail dinamis (bisa tambah/hapus baris dengan JS)
  - [x] Setiap baris: Select2 pilih produk | ukuran | kondisi | harga beli | qty
  - [x] Tombol "Tambah Baris" & "Hapus Baris"
  - [x] Tombol "Simpan" → POST → sistem update stok produk otomatis
- [x] Buat `stockin_detail.html` — detail per sesi penerimaan:
  - [x] Info header (pemasok, tanggal, dicatat oleh, catatan)
  - [x] Tabel item yang diterima

### 3.7 Manajemen User (Kasir)

- [x] Buat view `users_list`, `users_save`, `users_toggle_status`
- [x] Buat `users.html`:
  - [x] Page header + tombol "Tambah User Baru"
  - [x] Toolbar pencarian
  - [x] Tabel akun (Username, Peran, No. HP, Status Aktif)
  - [x] Tombol Edit & Toggle Status
- [x] Form tambah user (via modal):
  - [x] Input username, password (dengan validasi sederhana), pilihan role (Admin/Kasir), no HP.

### 3.8 Laporan Penjualan

- [x] Buat view `sales_report`
- [x] Buat `sales_report.html`:
  - [x] Toolbar filter: Rentang tanggal (Start-End), Kasir, Metode Bayar
  - [x] Tabel rekap transaksi (No. Trx, Tanggal, Kasir, Metode Bayar, Total Pembayaran)
  - [x] Footer tabel: Total Pendapatan Terfilter
  - [x] Tombol cetak / ekspor laporan
  - [x] Tombol Detail per transaksi (membuka modal detail / placeholder)

### 3.9 Laporan Inventory

- [x] Buat view `inventory_report`
- [x] Buat `inventory_report.html`:
  - [x] Toolbar filter (by merek, kategori)
  - [x] Summary card: Total Nilai Inventory (Σ harga beli × stok), Total Potensi Pendapatan (Σ harga jual × stok)
  - [x] Tabel stok saat ini (nama produk, merek, kategori, ukuran, kondisi, stok, harga beli, harga jual)

### 3.10 Closing (Pantau Semua — Admin)

- [x] Buat view `closing_admin`
- [x] Buat `closing_admin.html`:
  - [x] Toolbar filter (tanggal, kasir)
  - [x] Tabel histori semua data closing (tanggal, kasir, total tunai sistem, kas fisik aktual, selisih, status match/selisih, catatan)
  - [x] Badge warna: MATCH = hijau, SELISIH = merah/kuning

---

## FASE 4 — Halaman Kasir

### 4.1 Halaman POS (Transaksi)

- [x] Buat view `pos_page`, `pos_process_payment`, `pos_get_products` (AJAX)
- [x] Buat `pos.html` — tampilan dua panel:
  - [x] **Panel Kiri — Katalog & Pencarian:**
    - [x] Input pencarian real-time (by nama/merek/ukuran) → AJAX fetch produk aktif
    - [x] Grid kartu produk: foto, nama, merek, ukuran, kondisi, harga jual, stok
    - [x] Klik kartu → tambah ke keranjang
  - [x] **Panel Kanan — Keranjang:**
    - [x] Daftar item dalam keranjang (nama, qty +/-, harga satuan, subtotal, tombol hapus)
    - [x] Kalkulasi total otomatis (update real-time saat qty berubah)
    - [x] Pilih metode bayar: Tunai / Transfer BRI / QRIS (toggle tombol/tab)
    - [x] Jika Tunai: input nominal diterima → tampilkan kembalian otomatis
    - [x] Tombol "Proses Bayar" → POST transaksi via AJAX
    - [x] Tombol "Batal / Kosongkan Keranjang"
- [x] Logic proses bayar:
  - [x] Simpan ke `Transactions` + `TransactionDetails`
  - [x] Kurangi stok setiap produk (via signals)
  - [x] Jika stok = 0 → set status produk = `inactive`
- [x] Pop-up / Modal Struk setelah transaksi berhasil:
  - [x] Tampilkan: No. Struk, Tanggal, Kasir, daftar item, total, metode bayar, kembalian
  - [x] Tombol "Cetak" (browser print — thermal 80mm CSS)
  - [x] Tombol "Transaksi Baru"

### 4.2 Katalog Produk (Read-Only — Kasir)

- [x] Buat view `catalog_kasir`
- [x] Buat `catalog_kasir.html`:
  - [x] Toolbar pencarian + filter (merek, kategori)
  - [x] Grid kartu produk read-only (foto, nama, merek, ukuran, kondisi, harga jual, stok)
  - [x] Tidak ada tombol tambah/edit/hapus

### 4.3 Closing Shift (Kasir)

- [x] Buat view `closing_kasir`, `closing_submit`
- [x] Buat `closing_kasir.html`:
  - [x] Tampilkan ringkasan hari ini untuk kasir yang sedang login
  - [x] Input "Kas Fisik Aktual"
  - [x] Kalkulasi selisih real-time
  - [x] Badge status: MATCH / SELISIH
  - [x] Textarea catatan (opsional)
  - [x] Tombol "Submit & Kunci" → `is_locked = True`
  - [x] Jika sudah dikunci → tampilkan data read-only

---

## FASE 5 — Fitur Pendukung & Polish

### 5.1 Navigasi & Routing

- [x] Konfigurasi semua URL patterns di `urls.py`
- [x] Semua URL dilindungi dengan `@login_required` + pengecekan role
- [x] Sidebar: nav link aktif sesuai halaman (`request.resolver_match.url_name`)
- [x] Sidebar: tampilkan menu yang relevan sesuai role (Admin vs Kasir)
- [x] Login Kasir → redirect ke POS, Login Admin → redirect ke Dashboard

### 5.2 Keamanan

- [x] Semua AJAX POST sertakan CSRF token di header: `X-CSRFToken`
- [x] View Admin hanya bisa diakses role `admin`
- [x] View Kasir hanya bisa diakses role `kasir`
- [x] Redirect otomatis jika user tidak punya hak akses

### 5.3 Responsif

- [x] Login: sisi hero tersembunyi di `max-width: 992px`
- [x] Dashboard: main grid jadi 1 kolom di `max-width: 1100px`
- [x] Stat cards: 2 kolom di `max-width: 720px`, 1 kolom di `max-width: 480px`
- [x] Sidebar: toggle dengan backdrop untuk mobile

### 5.4 UX & Detail

- [x] Alert overlay animasi (sukses/error) di `base.html`
- [x] Semua tabel dengan kondisi "tidak ada data" → pesan kosong informatif
- [x] Loading state pada tombol saat AJAX berlangsung (disable + spinner)
- [x] Format angka Rupiah di semua tampilan harga
- [x] Konfirmasi sebelum hapus data (via `confirm_modal`)

---

## FASE 6 — Testing & Finalisasi

- [x] **Testing fungsional:**
  - [x] Login Admin → redirect ke dashboard
  - [x] Login Kasir → redirect ke POS
  - [x] CRUD Merek, Kategori, Pemasok
  - [x] Tambah Produk → muncul di katalog
  - [x] Catat Barang Masuk → stok produk bertambah (via signals)
  - [x] Transaksi POS → stok produk berkurang, produk nonaktif jika stok = 0
  - [x] Cetak struk dari modal POS
  - [x] Closing kasir → data locked, admin bisa lihat
  - [x] Laporan penjualan dengan filter tanggal
  - [x] Laporan inventory menampilkan nilai yang benar

- [x] **Testing tampilan:**
  - [x] Sidebar animasi berjalan
  - [x] Alert overlay muncul dengan animasi
  - [x] Tampilan responsif di mobile
  - [x] `manage.py check` — 0 issues

- [x] **Testing keamanan:**
  - [x] URL Admin tidak bisa diakses oleh Kasir
  - [x] URL Kasir tidak bisa diakses tanpa login
  - [x] CSRF terlindungi di semua AJAX POST

- [x] **Finalisasi:**
  - [x] Seed data awal (management command `seed_data`)
  - [x] Review & cleanup kode
  - [x] Pastikan semua `migrations` ter-commit
  - [x] `README.md` dokumentasi cara menjalankan project

---

## 📊 Progress Tracker

| Fase | Status | Keterangan |
|------|--------|------------|
| Fase 0 — Setup Project | `[x]` | Selesai (Menggunakan CDN) |
| Fase 1 — Database & Models | `[x]` | Selesai |
| Fase 2 — Auth & Base Template | `[x]` | Selesai |
| Fase 3 — Halaman Admin | `[x]` | Selesai |
| Fase 4 — Halaman Kasir | `[x]` | Selesai |
| Fase 5 — Fitur Pendukung | `[x]` | Selesai |
| Fase 6 — Testing & Finalisasi | `[x]` | Selesai |

---

> **Catatan:** Setiap halaman yang dibuat **wajib** mengikuti komponen dan CSS yang telah didefinisikan di `design_system.md`. Jangan membuat gaya baru yang bertentangan dengan sistem desain yang sudah ada.
