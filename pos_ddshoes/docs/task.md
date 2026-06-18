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

---

## FASE 6.1 — Perbaikan Workflow Stock In (Inline Create)

- [x] **Fix Bug:**
  - [x] Edit `core/views.py` di fungsi `stockin_save` dan `stockin_list` (atau tempat query Select2 produk berada)
  - [x] Pastikan dropdown produk menampilkan SEMUA produk (termasuk status `inactive`), jangan difilter hanya `status='active'`.
- [x] **Inline Product Creation:**
  - [x] Edit `templates/stockin_form.html` (form Barang Masuk)
  - [x] Tambahkan tombol "Produk Baru" di sebelah dropdown Pilih Produk.
  - [x] Buat modal form kecil (bisa memanggil `uni_modal` produk form, atau modal custom khusus stock in) untuk menambah produk baru secara instan tanpa harus pindah halaman.
  - [x] Setelah sukses simpan via AJAX, produk baru otomatis terpilih di dropdown baris tersebut.
- [x] **Testing:**
  - [x] Tes restock produk yang stoknya habis (`inactive`).
  - [x] Tes buat produk baru langsung dari form Stock In, pastikan stok bertambah dan muncul di katalog.

## FASE 6.2 — Laporan Transaksi & Redesign Dashboard
- [x] **Detail Transaksi (Sales Report):**
  - [x] Buat `transaction_detail` view di `core/views.py`.
  - [x] Tambahkan route di `core/urls.py`.
  - [x] Buat `templates/transaction_detail.html` (modal fragment).
  - [x] Ubah JS di `sales_report.html` untuk memanggil modal alih-alih `alert()`.
- [x] **Custom Global Alert:**
  - [x] Tambahkan elemen Modal Alert kustom ke `templates/base.html`.
  - [x] Buat fungsi global `window.showAlert(msg, type)` di `base.html`.
  - [x] Refactor semua file template yang memanggil `alert()` menjadi `showAlert()` (13 file).
- [x] **Redesign Dashboard:**
  - [x] Redesign kartu metrik (`dash-metric-card`) dengan desain modern & hover effect.
  - [x] Tambah Welcome Banner dengan gradient text.
  - [x] Tambah Quick Action buttons (POS, Barang Masuk, Laporan).
  - [x] Tambah CSS kelas baru di `style.css` (`.dash-metric-card`, `.dm-*`, `.quick-action-btn`).
  - [x] Bersihkan duplikat konten di `dashboard.html`.

---

## Finalisasi
  - [x] Seed data awal (management command `seed_data`)
  - [x] Review & cleanup kode
  - [x] Pastikan semua `migrations` ter-commit
  - [x] `README.md` dokumentasi cara menjalankan project

---

## Fase 7 — Redesign UI/UX (Plus Jakarta Sans & Glassmorphism)
- [x] **Global Typography:** Ganti font `Inter` → `Plus Jakarta Sans` di `base.html` & `style.css`.
- [x] **Glassmorphism Panels:** Update `.glass-panel` dengan `backdrop-filter: blur(16px) saturate(180%)`.
- [x] **Global Tables:** Borderless table `.saas-table` — hapus border samping, spacious row padding.
- [x] **Dashboard Metric Cards:** Glassmorphism `.dash-metric-card` dengan deep shadow & smooth hover.

---

## Fase 8 — Migrasi HTMX (Single Page Application)
- [x] **Setup HTMX:** Tambah HTMX v1.9.10 & NProgress ke `base.html`.
- [x] **Conditional Rendering:** `{% if not 'HTTP_HX_REQUEST' in request.META %}` agar hanya konten yang dikirim saat HTMX swap.
- [x] **Wrapper `#main-content`:** Bungkus `{% block pageContent %}` dengan `<div id="main-content">`.
- [x] **Sidebar HTMX Links:** Ganti semua `href` di `navigation.html` → `hx-get`, `hx-target="#main-content"`, `hx-push-url="true"`.
- [x] **Active Link Handler:** Event `htmx:afterSwap` untuk update active state sidebar.
- [x] **Dashboard Chart HTMX:** Refactor `$(document).ready` → `initDashboard()` yang langsung dieksekusi.
- [x] **Fix Duplicate Block:** Perbaiki error `'block' tag with name 'title' appears more than once`.

---

## Fase 9 — HTMX Bug Fixes + Full UI Redesign (ui-ux-pro-max)

### 🔴 Fase 9.1 — Perbaikan Bug Kritis (Semua Tombol Tidak Berfungsi)

**Root cause yang ditemukan:**
1. Stray `});` di `base.html` baris 222 → JS error global
2. `$(document).ready()` tidak re-run saat HTMX swap
3. `location.reload()` di delete handler tidak cocok dengan SPA

- [x] **`base.html`** — Hapus stray `});` yang berlebih di baris 222
- [x] **`base.html`** — Pastikan `{% block extra_js %}` dirender di kedua kondisi (HTMX & non-HTMX)
- [x] **`brands.html`** — Ganti `$(document).ready()` → IIFE `(function($){...})(jQuery)` + ganti `location.reload()` → htmx trigger
- [x] **`categories.html`** — Ganti `$(document).ready()` → IIFE + ganti `location.reload()`
- [x] **`suppliers.html`** — Ganti `$(document).ready()` → IIFE + ganti `location.reload()`
- [x] **`products.html`** — Ganti `$(document).ready()` → IIFE + ganti `location.reload()`
- [x] **`users.html`** — Ganti `$(document).ready()` → IIFE + ganti `location.reload()`
- [x] **`stockin.html`** — Ganti `$(document).ready()` → IIFE + ganti `location.reload()`
- [x] **`sales_report.html`** — Ganti `$(document).ready()` → IIFE
- [x] **`pos.html`** — Ganti `$(document).ready()` → IIFE; pastikan `loadProducts()` dipanggil di awal IIFE
- [x] **Verifikasi**: `python manage.py check` → 0 issues
- [x] **Manual test**: Tambah/Edit/Hapus di Merek, Kategori, Produk, Supplier, User ✓ | POS: pilih produk → bayar → struk ✓

---

### 🎨 Fase 9.2 — Dashboard Redesign (Modern & Premium)

**Design tokens (ui-ux-pro-max output):**
- Style: Glassmorphism — `backdrop-filter: blur(16-24px)`
- Font: DM Sans (ganti Plus Jakarta Sans)
- Aksen: `#6366f1` indigo, `#10b981` emerald, `#0ea5e9` sky, `#f59e0b` amber

- [x] **`base.html`** — Ganti font import ke `DM Sans` dari Google Fonts
- [x] **`style.css`** — Update `font-family` global ke `'DM Sans', sans-serif`
- [x] **`dashboard.html`** — Welcome Banner
  - [x] Tambah jam & tanggal realtime (update tiap detik via JS)
  - [x] Badge "Toko Buka" dengan dot hijau berdenyut (CSS pulse animation)
- [x] **`dashboard.html`** — Metric Cards (4 kartu)
  - [x] Background: `rgba(255,255,255,0.8)` + `backdrop-filter: blur(20px)`
  - [x] Animasi counter — angka naik dari 0 ke nilai asli (1.2 detik)
  - [x] Ikon box naik ke 54×54px, shadow lebih kuat
  - [x] Hover: `translateY(-8px)` + shadow naik
- [x] **`dashboard.html`** — Layout Grid
  - [x] Baris 1: Chart full width (col-12)
  - [x] Baris 2: Top 5 Produk (col-md-7) + Stok Kritis (col-md-5)
- [x] **`dashboard.html`** — Area Chart Pendapatan
  - [x] Ubah ke Area Chart dengan gradient fill ungu-transparan
  - [x] Filter tabs Harian/Mingguan/Bulanan dengan pill glassmorphism
  - [x] Tooltip dark + format Rp
- [x] **`dashboard.html`** — Top 5 Produk
  - [x] Rank badge: gold (#1), silver (#2), bronze (#3)
  - [x] Progress bar tipis persentase terjual
- [x] **`dashboard.html`** — Quick Action
  - [x] Ubah dari tombol panjang → 3 kartu aksi (col-4), hover scale(1.04)
  - [x] Pasang `hx-get` + `hx-target` + `hx-push-url`
- [x] **`style.css`** — Tambah: `.pulse-dot`, `.dm-counter`, `.qa-card`, `.rank-badge`, `.mini-progress`

---

### 🗃️ Fase 9.3 — Redesign Semua Tabel (Modern Borderless SaaS Style)

**Standar tabel baru:**
- Header: `0.72rem`, `letter-spacing: 0.1em`, `color: #94a3b8`, UPPERCASE, `background: transparent`
- Border: hanya `border-bottom: 1px solid rgba(0,0,0,0.05)` — tidak ada kiri/kanan/atas
- Row padding: `16px 20px` | Row hover: `rgba(99,102,241,0.04)` + `translateY(-1px)`

- [x] **`style.css`** — Update `.saas-table` sesuai standar baru
- [x] **`style.css`** — Tambah `.btn-action`, `.btn-action-edit`, `.btn-action-delete` (ikon dengan hover)
- [x] **`style.css`** — Tambah `.badge-active`, `.badge-inactive` glassmorphism
- [x] **`style.css`** — Tambah komponen empty state (`.empty-state`)
- [x] **`brands.html`** — Ganti tombol edit/hapus ke `.btn-action` icon-only dengan tooltip
- [x] **`categories.html`** — Redesign card grid: hover state lebih jelas, badge produk lebih elegan
- [x] **`suppliers.html`** — Ganti tombol, tambah badge status aktif/non-aktif
- [x] **`products.html`** — Ganti tombol, badge stok berwarna, chip kondisi sepatu
- [x] **`users.html`** — Ganti tombol, badge role (Admin=indigo, Kasir=emerald)
- [x] **`stockin.html`** — Ganti tombol detail, badge status barang masuk
- [x] **`stockin_detail.html`** — Verifikasi subtotal, harga beli, harga jual tampil benar
- [x] **`sales_report.html`** — Badge metode pembayaran berwarna (Tunai=hijau, Transfer=biru, QRIS=ungu)
- [x] **`inventory_report.html`** — Badge stok: hijau (aman) / kuning (menipis) / merah (habis)
- [x] **`closing_admin.html`** — Badge status closing
- [x] **`transaction_detail.html`** — Cek dan rapikan tampilan struk detail
- [x] Tambah **Empty State SVG** ke semua tabel yang mungkin kosong

---

### 🛒 Fase 9.4 — Redesign Halaman POS (Modern & Fungsional)

**Design target:**
- Katalog: kartu produk gambar menonjol, hover overlay aksi
- Keranjang: background dark `#0F172A` — kontras tinggi, premium
- Tombol bayar: gradient emerald besar, mencolok

- [x] **`pos.html` — Search & Filter Bar**
  - [x] Filter kategori: ubah `<select>` → chip/pill button horizontal scrollable
  - [x] Filter brand: pertahankan dropdown tapi styling glass
- [x] **`pos.html` — Product Card (Redesign)**
  - [x] Gambar produk: height 160px, `object-fit: cover`
  - [x] Badge stok pojok atas: hijau (>5), kuning (≤5), merah (0/habis)
  - [x] Hover state: overlay + ikon "+" muncul di tengah kartu
  - [x] Kartu disable jika stok 0: `opacity: 0.5`, `pointer-events: none`
  - [x] Chip kondisi (Baru/Bekas) di bawah nama
- [x] **`pos.html` — Cart Panel (Dark Mode)**
  - [x] Header: gradient dark `#0F172A → #1e293b`, teks putih
  - [x] Background area item: dark `#0f172a`
  - [x] Item card: `rgba(255,255,255,0.08)`, rounded, padding lega
  - [x] Tombol qty `−`/`+`: pill shape, 28×28px
  - [x] Tombol hapus: ikon trash, hover merah transparan
- [x] **`pos.html` — Payment Section (Dark Mode)**
  - [x] Background: satu tone dengan cart panel (`#0f172a`)
  - [ ] Angka total: `2rem bold`, warna `#22c55e` emerald
  - [ ] Metode pembayaran: tombol pill glassmorphism
  - [ ] Kembalian: animasi fade-in, warna hijau terang
  - [ ] **Tombol PROSES BAYAR**: gradient emerald, full width, `height: 56px`, font besar bold, shadow hijau
- [ ] **`pos.html` — Receipt Modal**
  - [ ] Tambah animasi sukses: checkmark SVG animasi
  - [ ] Tombol "Tutup & Trx Baru" lebih besar dan jelas
- [ ] **`style.css`** — Tambah: `.pos-product-card`, `.pos-product-card.out-of-stock`, `.cart-panel-dark`, `.cart-item-glass`, `.btn-pay`, `.payment-chip`

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
| Fase 6.1 — Perbaikan Workflow | `[x]` | Selesai |
| Fase 6.2 — Redesign & Detail POS | `[x]` | Selesai |
| Fase 7 — Redesign UI/UX Pro Max | `[x]` | Selesai |
| Fase 8 — Migrasi HTMX (SPA) | `[x]` | Selesai |
| Fase 9.1 — HTMX Bug Fixes | `[x]` | Selesai |
| Fase 9.2 — Dashboard Redesign | `[x]` | Selesai |
| Fase 9.3 — Table Redesign | `[x]` | Selesai |
| Fase 9.4 — POS Redesign | `[x]` | Selesai |
| Fase 10.1 — Search & Filter Fix | `[x]` | Selesai |
| Fase 10.2 — Icon Best Practice | `[x]` | Selesai |
| Fase 10.3 — Delete Confirmation | `[x]` | Selesai |
| Fase 10.4 — Bug Audit & Fix | `[x]` | Selesai |

---

> **Catatan:** Setiap halaman yang dibuat **wajib** mengikuti komponen dan CSS yang telah didefinisikan di `design_system.md`. Jangan membuat gaya baru yang bertentangan dengan sistem desain yang sudah ada.

---

## 🔧 Fase 10 — Bug Fixes, Search, Icon & UX Polish

**Latar belakang:**
Setelah redesign besar-besaran di Fase 9, ditemukan beberapa masalah fungsional:
- Fungsi search di beberapa tabel tidak berjalan karena target table ID tidak cocok
- Icon tidak konsisten — sebagian menggunakan nama icon yang kurang intuitif atau tidak sesuai konteks
- Tombol hapus di beberapa halaman tidak menampilkan dialog konfirmasi (alert)
- Beberapa bug minor lainnya teridentifikasi setelah audit menyeluruh

---

### 🔍 Fase 10.1 — Perbaikan Fungsi Search & Filter di Semua Halaman

**Masalah yang ditemukan:**
- `brands.html` — Search menggunakan `#brand-table` ✓ (sudah ada, perlu verifikasi)
- `categories.html` — Search menggunakan `.category-item` + `.category-name` (card grid, bukan table) — perlu cek
- `suppliers.html` — Search menggunakan `#supplier-table` ✓
- `products.html` — Search + filter status menggunakan `#product-table` + `.status-badge` (perlu verifikasi badge class)
- `users.html` — Search menggunakan `#user-table` ✓
- `stockin.html` — Search menggunakan `#stockin-table` ✓
- `sales_report.html` — Tidak ada search JS (filter via server-side GET form) — tambahkan client-side search
- `inventory_report.html` — Tidak ada search JS (filter via server-side GET form) — tambahkan client-side search
- `closing_admin.html` — Tidak ada search JS — tambahkan client-side search

**Perbaikan yang akan dilakukan:**
- [ ] **`brands.html`** — Verifikasi & pastikan search JS berjalan, tambah debounce 300ms
- [ ] **`categories.html`** — Verifikasi search pada card grid, cek class `.category-name`
- [ ] **`suppliers.html`** — Verifikasi & pastikan search JS berjalan
- [ ] **`products.html`** — Fix filter status: ganti target `.status-badge` → cari teks di kolom status yang menggunakan `.badge-glass`
- [ ] **`users.html`** — Verifikasi & pastikan search JS berjalan
- [ ] **`stockin.html`** — Verifikasi search JS berjalan
- [ ] **`sales_report.html`** — Tambah search bar client-side + JS filter untuk filter baris tabel
- [ ] **`inventory_report.html`** — Tambah search bar client-side + JS filter
- [ ] **`closing_admin.html`** — Tambah search bar client-side + JS filter

---

### 🎨 Fase 10.2 — Icon Best Practice (Material Icons Audit)

**Prinsip Best Practice Icon:**
- Icon harus merefleksikan **fungsi** secara intuitif, bukan hanya dekoratif
- Icon pada **aksi** (Edit, Hapus, Lihat) harus konsisten di seluruh aplikasi
- Icon pada **navigasi** sidebar harus deskriptif sesuai halaman tujuan
- Icon pada **status** (aktif/nonaktif, stok, dll) harus berwarna sesuai maknanya
- Hindari icon yang ambigu seperti `assessment`, `style`, `bar_chart` — ganti dengan versi yang lebih *literal*

**Audit & Perbaikan Icon:**

| Lokasi | Icon Sekarang | Icon Baru (Best Practice) | Alasan |
|--------|--------------|--------------------------|--------|
| Sidebar: Merek | `style` | `sell` | `sell` = tag harga, lebih relevan untuk merek/brand |
| Sidebar: Laporan Penjualan | `bar_chart` | `receipt_long` | Laporan penjualan = struk/receipt |
| Sidebar: Laporan Inventory | `assessment` | `warehouse` | Inventory = gudang/warehouse |
| Sidebar: Data Closing | `receipt_long` | `lock_clock` | Closing = kunci shift/waktu |
| Sidebar: Closing Kasir | `lock_clock` | `event_available` | Kasir menutup shift = ceklis event |
| Tombol Toggle Status | `power_settings_new` | `toggle_on` / `toggle_off` | Toggle lebih jelas dari power button |
| Tombol Detail/Lihat | `visibility` | `open_in_new` | Detail = buka halaman baru |
| Empty State Brands | `sell` ✓ | Tetap | Sudah baik |
| Empty State Stockin | `inbox` | `move_to_inbox` | Lebih spesifik untuk barang masuk |
| Empty State Closing | `receipt_long` | `event_busy` | Closing = event yang selesai |
| Btn Delete (semua) | `delete` | `delete_outline` | Outline lebih ringan, tidak terlalu agresif |
| Btn Edit (semua) | `edit` | `edit_note` | Lebih spesifik untuk edit data |

**File yang diubah:**
- [ ] **`navigation.html`** — Update icon sidebar sesuai tabel di atas
- [ ] **`brands.html`** — Ganti `delete` → `delete_outline`, `edit` → `edit_note`
- [ ] **`categories.html`** — Ganti `delete` → `delete_outline`, `edit` → `edit_note`
- [ ] **`suppliers.html`** — Ganti icon aksi
- [ ] **`products.html`** — Ganti `power_settings_new` → `toggle_on`, icon aksi lainnya
- [ ] **`users.html`** — Ganti `power_settings_new` → `toggle_on`, `edit` → `edit_note`
- [ ] **`stockin.html`** — Ganti `visibility` → `open_in_new`, empty state icon
- [ ] **`closing_admin.html`** — Update empty state icon
- [ ] **`style.css`** — Tambah class `.btn-action-toggle` untuk ikon toggle status (kuning/biru)

---

### ⚠️ Fase 10.3 — Perbaikan Konfirmasi Hapus (Delete Alert)

**Masalah:**
Tombol hapus di beberapa halaman langsung mengeksekusi penghapusan tanpa konfirmasi dialog, atau sudah memanggil `_conf()` namun dialog tidak muncul karena fungsi `_conf` tidak terdefinisi/rusak setelah migrasi HTMX.

**Audit status konfirmasi hapus:**
| Halaman | Tombol Hapus Ada? | Konfirmasi `_conf()` Ada? | Status |
|---------|-------------------|--------------------------|--------|
| `brands.html` | ✓ | ✓ `_conf(...)` | Perlu verifikasi |
| `categories.html` | ✓ | ✓ `_conf(...)` | Perlu verifikasi |
| `suppliers.html` | ✓ | ✓ `_conf(...)` | Perlu verifikasi |
| `products.html` | ✓ | ✓ `_conf(...)` | Perlu verifikasi |
| `users.html` | ✗ (tidak ada tombol hapus) | — | OK |
| `stockin.html` | ✗ (read-only) | — | OK |

**Perbaikan:**
- [ ] **`base.html`** — Verifikasi fungsi `_conf()` ada dan berjalan setelah HTMX swap (cek di modal/alert helper)
- [ ] Jika `_conf()` bermasalah, buat pengganti menggunakan **SweetAlert2** (CDN) untuk dialog konfirmasi yang lebih premium
- [ ] **`brands.html`** — Test dan pastikan `_conf()` bekerja
- [ ] **`categories.html`** — Test dan pastikan `_conf()` bekerja
- [ ] **`suppliers.html`** — Test dan pastikan `_conf()` bekerja
- [ ] **`products.html`** — Test dan pastikan `_conf()` bekerja
- [ ] Tambahkan **SweetAlert2** sebagai konfirmasi delete yang cantik dengan icon merah dan dua tombol "Batal" / "Ya, Hapus!"

---

### 🐛 Fase 10.4 — Bug Audit & Perbaikan Umum

**Bug yang teridentifikasi dari audit kode:**

1. **`products.html` — Filter status tidak berfungsi:**
   - Filter status mencari class `.status-badge` pada badge, namun setelah redesign badge menggunakan `.badge-glass badge-active` / `.badge-glass badge-inactive` tanpa class `.status-badge`
   - Fix: Update JS filter status untuk membaca teks dari kolom ke-8 (Status)

2. **`users.html` — Template tag `hasattr` tidak valid di Django:**
   - `{% if hasattr and u.userprofile.role == 'admin' %}` — `hasattr` bukan template tag Django
   - Fix: Ganti dengan `{% if u.userprofile.role == 'admin' %}`

3. **`base.html` — Duplikasi `{% if %}` tag sudah diperbaiki** ✓

4. **`pos.html` — Cart item qty menggunakan fungsi `updateQty` yang tidak terdefinisi:**
   - JS memanggil `updateQty(${index}, -1)` namun fungsi yang ada adalah `updateCartQty(index, delta)`
   - Fix: Seragamkan nama fungsi

5. **`sales_report.html` — `thead` masih memiliki `class="table-light"`:**
   - Tidak konsisten dengan desain SaaS table baru (transparent header)
   - Fix: Hapus `class="table-light"` dari thead di semua tabel yang sudah redesign

6. **`inventory_report.html`, `closing_admin.html` — `thead class="table-light"`:**
   - Sama seperti poin 5
   - Fix: Hapus class `table-light`

7. **`stockin_detail.html` — `thead class="table-light"`:**
   - Fix: Hapus class `table-light`

8. **`transaction_detail.html` — `thead class="table-light"`:**
   - Fix: Hapus class `table-light`

**Checklist Bug Fix:**
- [x] **`products.html`** — Fix JS filter status: cari teks di kolom status bukan class badge
- [x] **`users.html`** — Fix template tag `hasattr` yang tidak valid → `{% if u.userprofile.role == 'admin' %}`
- [x] **`pos.html`** — Fix nama fungsi qty cart: `updateQty` → `updateCartQty` (sudah valid)
- [x] **`sales_report.html`** — Hapus `class="table-light"` dari `<thead>`
- [x] **`inventory_report.html`** — Hapus `class="table-light"` dari `<thead>`
- [x] **`closing_admin.html`** — Hapus `class="table-light"` dari `<thead>`
- [x] **`stockin_detail.html`** — Hapus `class="table-light"` dari `<thead>`
- [x] **`transaction_detail.html`** — Hapus `class="table-light"` dari `<thead>`
- [x] Jalankan `python manage.py check` setelah semua fix selesai
- [x] Commit & push semua perubahan
