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

- [ ] Buat view `products_list`, `products_save`, `products_delete`, `products_toggle_status`
- [ ] Buat `products.html`:
  - [ ] Page header + tombol "Tambah Produk"
  - [ ] Toolbar pencarian + filter (by Merek, Kategori, Kondisi, Stok)
  - [ ] Tabel produk dengan kolom: Foto, Nama, Merek, Ukuran, Kondisi, Harga Beli, Harga Jual, Stok, Status, Aksi
  - [ ] Tombol Edit produk → `uni_modal` dengan form lengkap
  - [ ] Tombol Toggle Status (Aktifkan/Nonaktifkan) → AJAX
  - [ ] Tombol Hapus → `confirm_modal`
- [ ] Form produk (via modal):
  - [ ] Select2 untuk pilih Merek & Kategori
  - [ ] Field: nama, ukuran, kondisi (dropdown: Baru/Like New/Good/Fair), deskripsi
  - [ ] Field harga beli, harga jual, stok awal
  - [ ] Upload foto produk (ImageField)

### 3.6 Barang Masuk (Stock In)

- [ ] Buat view `stockin_list`, `stockin_detail`, `stockin_save`
- [ ] Buat `stockin.html` — halaman utama:
  - [ ] Page header + tombol "Catat Barang Masuk"
  - [ ] Toolbar filter (tanggal, pemasok)
  - [ ] Tabel riwayat penerimaan (No. Dokumen, Tanggal, Pemasok, Dicatat Oleh, Jml Item, Aksi Detail)
  - [ ] Link ke halaman detail per sesi penerimaan
- [ ] Buat `stockin_form.html` — form catat barang masuk:
  - [ ] Header form: Select2 pilih pemasok, input tanggal terima, textarea catatan
  - [ ] Tabel baris detail dinamis (bisa tambah/hapus baris dengan JS)
  - [ ] Setiap baris: Select2 pilih produk | ukuran | kondisi | harga beli | qty
  - [ ] Tombol "Tambah Baris" & "Hapus Baris"
  - [ ] Tombol "Simpan" → POST → sistem update stok produk otomatis
- [ ] Buat `stockin_detail.html` — detail per sesi penerimaan:
  - [ ] Info header (pemasok, tanggal, dicatat oleh, catatan)
  - [ ] Tabel item yang diterima

### 3.7 Manajemen User (Kasir)

- [ ] Buat view `users_list`, `users_save`, `users_toggle_status`
- [ ] Buat `users.html`:
  - [ ] Page header + tombol "Tambah Kasir"
  - [ ] Tabel daftar akun kasir (username, nama, no. HP, status, last login, aksi)
  - [ ] Tombol Edit → `uni_modal` dengan form edit (username, password, phone)
  - [ ] Tombol Aktifkan/Nonaktifkan → AJAX toggle `is_active`
  - [ ] Form tambah kasir (field: username, password, phone)

### 3.8 Laporan Penjualan

- [ ] Buat view `sales_report`, `sales_report_detail`, `sales_report_export_pdf`
- [ ] Buat `sales_report.html`:
  - [ ] Toolbar filter: rentang tanggal (date picker), kasir (dropdown), metode bayar
  - [ ] Ringkasan total (total transaksi, total pendapatan, breakdown per metode bayar)
  - [ ] Tabel rekap transaksi (No. Struk, Tanggal, Kasir, Total, Metode Bayar, Aksi Detail)
  - [ ] Klik detail → tampilkan item per struk (via modal atau halaman terpisah)
  - [ ] Tombol Ekspor/Cetak PDF laporan terfilter (gunakan `window.print()` atau library PDF)

### 3.9 Laporan Inventory

- [ ] Buat view `inventory_report`
- [ ] Buat `inventory_report.html`:
  - [ ] Toolbar filter (by merek, kategori)
  - [ ] Summary card: Total Nilai Inventory (Σ harga beli × stok), Total Potensi Pendapatan (Σ harga jual × stok)
  - [ ] Tabel stok saat ini (nama produk, merek, kategori, ukuran, kondisi, stok, harga beli, harga jual, nilai beli, nilai jual)

### 3.10 Closing (Pantau Semua — Admin)

- [ ] Buat view `closing_admin`
- [ ] Buat `closing_admin.html`:
  - [ ] Toolbar filter (tanggal, kasir)
  - [ ] Tabel histori semua data closing (tanggal, kasir, total tunai sistem, total transfer, total QRIS, kas fisik aktual, selisih, status match/selisih, catatan)
  - [ ] Badge warna: MATCH = hijau, SELISIH = merah/kuning

---

## FASE 4 — Halaman Kasir

### 4.1 Halaman POS (Transaksi)

- [ ] Buat view `pos_page`, `pos_process_payment`, `pos_get_products` (AJAX)
- [ ] Buat `pos.html` — tampilan dua panel:
  - [ ] **Panel Kiri — Katalog & Pencarian:**
    - [ ] Input pencarian real-time (by nama/merek/ukuran) → AJAX fetch produk aktif
    - [ ] Grid kartu produk: foto, nama, merek, ukuran, kondisi, harga jual, stok
    - [ ] Tombol "+ Tambah ke Keranjang" di setiap kartu produk
  - [ ] **Panel Kanan — Keranjang:**
    - [ ] Daftar item dalam keranjang (nama, qty input, harga satuan, subtotal, tombol hapus)
    - [ ] Kalkulasi total otomatis (update real-time saat qty berubah)
    - [ ] Pilih metode bayar: Tunai / Transfer BRI / QRIS (toggle tombol/tab)
    - [ ] Jika Tunai: input nominal diterima → tampilkan kembalian otomatis
    - [ ] Tombol "Proses Bayar" → POST transaksi
    - [ ] Tombol "Batal / Kosongkan Keranjang"
- [ ] Logic proses bayar:
  - [ ] Simpan ke `Transactions` + `TransactionDetails`
  - [ ] Kurangi stok setiap produk
  - [ ] Jika stok = 0 → set status produk = `inactive`
- [ ] Pop-up / Modal Struk setelah transaksi berhasil:
  - [ ] Tampilkan: No. Struk, Tanggal, Kasir, daftar item, total, metode bayar, kembalian (jika tunai)
  - [ ] Tombol "Cetak" (browser print)
  - [ ] Tombol "Transaksi Baru"

### 4.2 Katalog Produk (Read-Only — Kasir)

- [ ] Buat view `catalog_kasir`
- [ ] Buat `catalog_kasir.html`:
  - [ ] Toolbar pencarian + filter (merek, kategori, kondisi)
  - [ ] Grid kartu produk read-only (foto, nama, merek, ukuran, kondisi, harga jual, stok)
  - [ ] Tidak ada tombol tambah/edit/hapus

### 4.3 Closing Shift (Kasir)

- [ ] Buat view `closing_kasir`, `closing_submit`
- [ ] Buat `closing_kasir.html`:
  - [ ] Tampilkan ringkasan hari ini untuk kasir yang sedang login:
    - Total Tunai (sistem)
    - Total Transfer (sistem)
    - Total QRIS (sistem)
    - Grand Total
    - Jumlah Transaksi
  - [ ] Input "Kas Fisik Aktual" (jumlah uang tunai yang dihitung di laci)
  - [ ] Kalkulasi selisih real-time: Selisih = Kas Fisik - Total Tunai Sistem
  - [ ] Badge status: MATCH (selisih = 0) / SELISIH (selisih ≠ 0)
  - [ ] Textarea catatan (opsional)
  - [ ] Tombol "Submit & Kunci" → POST → `is_locked = True`
  - [ ] Tampilkan pesan jika closing hari ini sudah di-submit (locked)
  - [ ] Jika sudah ada closing hari ini yang locked → tampilkan data closing tersebut (read-only)

---

## FASE 5 — Fitur Pendukung & Polish

### 5.1 Navigasi & Routing

- [ ] Konfigurasi semua URL patterns di `urls.py`
- [ ] Pastikan setiap URL dilindungi dengan decorator `@login_required` + pengecekan role
- [ ] Sidebar: tandai nav link aktif sesuai halaman yang sedang dibuka (`window.location.pathname`)
- [ ] Sidebar: tampilkan menu yang relevan sesuai role (Admin vs Kasir)

### 5.2 Keamanan

- [ ] Semua AJAX POST sertakan CSRF token di header: `X-CSRFToken`
- [ ] View Admin hanya bisa diakses role `admin`
- [ ] View Kasir hanya bisa diakses role `kasir` (dan `admin` jika perlu)
- [ ] Redirect otomatis jika user tidak punya hak akses

### 5.3 Responsif

- [ ] Login: sisi hero tersembunyi di `max-width: 992px`, form full width
- [ ] Dashboard: main grid (7:3) jadi 1 kolom di `max-width: 1100px`
- [ ] Stat cards: 4 → 2 kolom di `max-width: 720px`, → 1 kolom di `max-width: 480px`
- [ ] Sidebar: bisa di-toggle dengan backdrop untuk mobile

### 5.4 UX & Detail

- [ ] Preloader animasi loading halaman (via `preloader.js` dari Material Admin)
- [ ] Alert overlay animasi (sukses/error) dengan audio notifikasi dari CDN Mixkit
- [ ] Semua tabel dengan kondisi "tidak ada data" → tampilkan pesan kosong yang informatif
- [ ] Loading state pada tombol saat proses AJAX berlangsung (disable + spinner)
- [ ] Format angka Rupiah di semua tampilan harga (contoh: `Rp 150.000`)
- [ ] Konfirmasi sebelum hapus data (via `confirm_modal`)
- [ ] Toast / feedback singkat setelah aksi berhasil

---

## FASE 6 — Testing & Finalisasi

- [ ] **Testing fungsional:**
  - [ ] Login Admin → redirect ke dashboard ✓
  - [ ] Login Kasir → redirect ke POS ✓
  - [ ] CRUD Merek, Kategori, Pemasok ✓
  - [ ] Tambah Produk dengan foto → muncul di katalog ✓
  - [ ] Catat Barang Masuk → stok produk bertambah ✓
  - [ ] Transaksi POS → stok produk berkurang, produk nonaktif jika stok = 0 ✓
  - [ ] Cetak struk dari modal POS ✓
  - [ ] Closing kasir → data locked, admin bisa lihat ✓
  - [ ] Laporan penjualan dengan filter tanggal ✓
  - [ ] Laporan inventory menampilkan nilai yang benar ✓

- [ ] **Testing tampilan:**
  - [ ] Sidebar animasi (particle, rings, scanline, glow divider) berjalan ✓
  - [ ] Logo upload di sidebar (localStorage) berfungsi ✓
  - [ ] Stat cards dashboard hover effect ✓
  - [ ] Chart.js grafik tren tampil dengan data benar ✓
  - [ ] Alert overlay muncul dengan animasi & audio ✓
  - [ ] Tampilan responsif di mobile ✓

- [ ] **Testing keamanan:**
  - [ ] URL Admin tidak bisa diakses oleh Kasir ✓
  - [ ] URL Kasir tidak bisa diakses tanpa login ✓
  - [ ] CSRF terlindungi di semua AJAX POST ✓

- [ ] **Finalisasi:**
  - [ ] Seed data awal: kategori default, merek populer (Nike, Adidas, Vans, dll)
  - [ ] Buat akun kasir demo
  - [ ] Review & cleanup kode (hapus print/debug statements)
  - [ ] Pastikan semua `migrations` ter-commit
  - [ ] Dokumentasi cara menjalankan project (`README.md`)

---

## 📊 Progress Tracker

| Fase | Status | Keterangan |
|------|--------|------------|
| Fase 0 — Setup Project | `[x]` | Selesai (Menggunakan CDN) |
| Fase 1 — Database & Models | `[x]` | Selesai |
| Fase 2 — Auth & Base Template | `[x]` | Selesai |
| Fase 3 — Halaman Admin | `[ ]` | — |
| Fase 4 — Halaman Kasir | `[ ]` | — |
| Fase 5 — Fitur Pendukung | `[ ]` | — |
| Fase 6 — Testing & Finalisasi | `[ ]` | — |

---

> **Catatan:** Setiap halaman yang dibuat **wajib** mengikuti komponen dan CSS yang telah didefinisikan di `design_system.md`. Jangan membuat gaya baru yang bertentangan dengan sistem desain yang sudah ada.
