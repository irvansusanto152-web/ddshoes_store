# PRD — Sistem Informasi POS + Inventory DD Shoes Store
**Jenis Usaha:** Toko Sepatu Second (Bekas)
**Tech Stack:** Python · Django · SQLite3 · HTML/CSS/JS
**Metode Pengembangan:** RAD (Rapid Application Development)

---

## 1. Konteks Bisnis & Alur Barang

DD Shoes Store adalah toko ritel sepatu bekas (*second*). Karena produk yang dijual adalah barang bekas, **setiap sepatu diperlakukan sebagai item unik** — berbeda merek, ukuran, dan kondisi. Alur barang secara keseluruhan adalah:

```
[Pemasok / Sumber Barang]
        │
        ▼
[Pencatatan Barang Masuk (Stock In)]
  → Admin memilih produk yang sudah ada (termasuk inactive) ATAU langsung membuat produk baru secara inline (Nama, Merek, Kategori, Ukuran, Kondisi, Harga Beli, Harga Jual default).
        │
        ▼
[Katalog Produk (Inventory Aktif)]
  → Produk yang didaftarkan via Barang Masuk otomatis masuk katalog dengan stok terupdate. Harga Jual dapat disesuaikan kemudian.
        │
        ▼
[Transaksi POS (Kasir)]
  → Kasir cari produk, masuk keranjang, pilih pembayaran, cetak struk
        │
        ▼
[Stok Berkurang Otomatis → Produk Habis / Nonaktif]
        │
        ▼
[Laporan & Closing]
  → Admin lihat total penjualan, margin keuntungan, stok tersisa
```

---

## 2. User Roles & Hak Akses

| Role | Deskripsi | Hak Akses |
| :--- | :--- | :--- |
| **Admin (Pemilik)** | Pemilik toko yang mengelola operasional penuh | Semua halaman: Master Data, Inventory, Laporan, Closing, Manajemen User |
| **Kasir** | Petugas meja kasir | Hanya: Halaman POS, Katalog (read-only), Closing shift sendiri |

---

## 3. Daftar Halaman & Antarmuka (Pages)

### 3.1 Halaman Publik / Autentikasi

| Halaman | Akses | Fitur & Detail |
| :--- | :--- | :--- |
| **Login** | Semua | Form username + password. Sistem catat waktu login & role. Redirect otomatis ke dashboard sesuai role. |

---

### 3.2 Halaman Admin (Pemilik)

| Halaman | Fitur & Detail |
| :--- | :--- |
| **Dashboard** | Kartu metrik: Total Stok, Total Produk Terjual Hari Ini, Pendapatan Hari Ini, Stok Hampir Habis. Grafik tren pendapatan (Harian / Mingguan / Bulanan). Tabel 5 Produk Terlaris. Tabel Stok Kritis (stok ≤ 0 atau hampir habis). |
| **Master: Merek (Brands)** | Tabel daftar merek sepatu. CRUD: Tambah, Ubah, Hapus merek. *Contoh: Nike, Adidas, Vans, New Balance* |
| **Master: Kategori** | Tabel daftar kategori. CRUD: Tambah, Ubah, Hapus kategori. *Contoh: Sneakers, Formal, Sandal, Boots* |
| **Master: Pemasok (Suppliers)** | Tabel daftar pemasok/sumber barang. CRUD: Nama pemasok, Nomor HP, Keterangan. *Contoh: Pak Budi (Pasar), Supplier Online X* |
| **Katalog Produk (Inventory)** | Tabel semua produk beserta: Foto, Nama, Merek, Ukuran, Kondisi, Harga Beli, Harga Jual, Stok, Status. Filter by: Merek, Kategori, Kondisi, Stok. Tombol Tambah Produk → Form input lengkap produk. Tombol Edit & Nonaktifkan. |
| **Barang Masuk (Stock In)** | Tabel riwayat semua penerimaan barang dari pemasok. Filter by tanggal & pemasok. Tombol "Catat Barang Masuk" → Form: pilih pemasok, tanggal terima, lalu input baris demi baris. Pada tiap baris, Admin bisa **memilih produk existing (baik active maupun inactive)** ATAU **menambahkan produk baru secara inline** (via modal/inline form). Submit → stok otomatis bertambah di tabel Produk (dan produk baru otomatis terdaftar). Detail per transaksi penerimaan. |
| **Manajemen User** | Tabel daftar akun kasir. CRUD: Tambah, Ubah, Nonaktifkan akun kasir. |
| **Laporan Penjualan** | Tabel rekap semua transaksi. Filter: rentang tanggal, kasir, metode bayar. Klik detail → lihat item per struk. Ekspor / Cetak PDF laporan terfilter. Menampilkan kolom: No. Struk, Tanggal, Kasir, Total, Metode Bayar. |
| **Laporan Inventory** | Tabel stok saat ini. Tampilkan: total nilai inventory (Σ Harga Beli × Stok), total potensi pendapatan (Σ Harga Jual × Stok). Filter by merek/kategori. |
| **Closing (Pantau Semua)** | Admin dapat melihat semua histori data closing dari semua kasir dan semua tanggal. |

---

### 3.3 Halaman Kasir

| Halaman | Fitur & Detail |
| :--- | :--- |
| **Halaman POS (Transaksi)** | Tampilan dua panel: kiri = pencarian & katalog produk, kanan = keranjang belanja. Pencarian produk by nama/merek/ukuran. Klik produk → masuk keranjang (qty default 1, bisa diubah). Kalkulasi subtotal & total otomatis. Pilih metode bayar: Tunai (input nominal → hitung kembalian), Transfer BRI, QRIS. Tombol "Proses Bayar" → simpan transaksi, potong stok, pop-up struk. |
| **Katalog Produk** | Read-only. Kasir bisa lihat daftar produk, stok, harga, kondisi untuk keperluan pelayanan pelanggan. |
| **Closing Shift** | Kasir buka halaman ini di akhir shift. Sistem tampilkan: total transaksi hari ini, rincian per metode bayar (tunai, transfer, QRIS). Kasir input jumlah uang fisik (tunai) di laci. Sistem hitung selisih. Kasir tambah catatan (opsional). Klik "Submit Closing" → data terkunci, tidak bisa diedit. |

---

## 4. Struktur Database (Tabel SQLite)

### 4.1 `auth_user` *(Django built-in, di-extend)*
Tabel bawaan Django untuk autentikasi.

| Field | Tipe | Keterangan |
| :--- | :--- | :--- |
| `id` | Integer (PK) | Auto increment |
| `username` | String | Nama login |
| `password` | String (hash) | Password terenkripsi |
| `is_active` | Boolean | Status aktif akun |
| `last_login` | Datetime | Waktu login terakhir |

### 4.2 `UserProfile` *(Custom Extension)*
Menyimpan role & info tambahan kasir.

| Field | Tipe | Keterangan |
| :--- | :--- | :--- |
| `id` | Integer (PK) | |
| `user_id` | FK → auth_user | One-to-one |
| `role` | String | `admin` / `kasir` |
| `phone` | String (nullable) | No. HP |

---

### 4.3 `Categories`

| Field | Tipe | Keterangan |
| :--- | :--- | :--- |
| `id` | Integer (PK) | |
| `name` | String | Nama kategori (Sneakers, Boots, dll) |

### 4.4 `Brands`

| Field | Tipe | Keterangan |
| :--- | :--- | :--- |
| `id` | Integer (PK) | |
| `name` | String | Nama merek (Nike, Adidas, dll) |

### 4.5 `Suppliers`

| Field | Tipe | Keterangan |
| :--- | :--- | :--- |
| `id` | Integer (PK) | |
| `name` | String | Nama pemasok |
| `phone` | String (nullable) | No. HP pemasok |
| `notes` | Text (nullable) | Keterangan tambahan |

---

### 4.6 `Products`
Tabel utama katalog/inventory sepatu second.

| Field | Tipe | Keterangan |
| :--- | :--- | :--- |
| `id` | Integer (PK) | |
| `category_id` | FK → Categories | |
| `brand_id` | FK → Brands | |
| `name` | String | Nama produk |
| `size` | String | Ukuran sepatu (39, 40, 41, dll) |
| `condition` | String | Grade kondisi: `Baru`, `Like New`, `Good`, `Fair` |
| `description` | Text (nullable) | Deskripsi detail produk |
| `buy_price` | Integer | Harga beli dari pemasok |
| `sell_price` | Integer | Harga jual ke pelanggan |
| `stock` | Integer | Stok saat ini (default: 0) |
| `image` | ImageField | Foto produk |
| `status` | String | `active` / `inactive` |
| `created_at` | Datetime | Tanggal produk ditambahkan |

---

### 4.7 `StockIns` *(Header Barang Masuk)*
Mencatat satu sesi penerimaan barang dari pemasok.

| Field | Tipe | Keterangan |
| :--- | :--- | :--- |
| `id` | Integer (PK) | Nomor dokumen penerimaan |
| `supplier_id` | FK → Suppliers | Sumber barang |
| `received_by` | FK → auth_user | Admin yang mencatat |
| `received_date` | Date | Tanggal terima barang |
| `notes` | Text (nullable) | Catatan (kondisi kiriman, dll) |
| `created_at` | Datetime | |

### 4.8 `StockInDetails` *(Baris Item Barang Masuk)*
Detail produk yang masuk dalam satu sesi penerimaan.

| Field | Tipe | Keterangan |
| :--- | :--- | :--- |
| `id` | Integer (PK) | |
| `stock_in_id` | FK → StockIns | |
| `product_id` | FK → Products | Produk yang diterima |
| `quantity` | Integer | Jumlah unit diterima |
| `buy_price` | Integer | Harga beli saat penerimaan ini (bisa berbeda waktu) |

> **Catatan:** Saat `StockInDetails` disimpan, field `stock` di tabel `Products` akan otomatis **bertambah** sebesar `quantity`.

---

### 4.9 `Transactions` *(Header Transaksi Penjualan)*

| Field | Tipe | Keterangan |
| :--- | :--- | :--- |
| `id` | Integer (PK) | Nomor struk unik |
| `cashier_id` | FK → auth_user | Kasir yang memproses |
| `total_amount` | Integer | Total harga akhir |
| `payment_method` | String | `tunai` / `transfer_bri` / `qris` |
| `cash_received` | Integer (nullable) | Nominal uang tunai diterima |
| `change_amount` | Integer (nullable) | Kembalian |
| `transaction_date` | Datetime | Timestamp otomatis |

### 4.10 `TransactionDetails` *(Baris Item Penjualan)*

| Field | Tipe | Keterangan |
| :--- | :--- | :--- |
| `id` | Integer (PK) | |
| `transaction_id` | FK → Transactions | |
| `product_id` | FK → Products | |
| `quantity` | Integer | Jumlah terjual |
| `sell_price` | Integer | Harga jual saat transaksi (snapshot) |
| `subtotal` | Integer | `quantity × sell_price` |

> **Catatan:** Saat `TransactionDetails` disimpan, field `stock` di tabel `Products` akan otomatis **berkurang** sebesar `quantity`.

---

### 4.11 `CashClosings` *(Rekap Closing Kasir)*

| Field | Tipe | Keterangan |
| :--- | :--- | :--- |
| `id` | Integer (PK) | |
| `cashier_id` | FK → auth_user | Kasir yang submit |
| `closing_date` | Date | Tanggal shift |
| `system_cash_total` | Integer | Total tunai menurut sistem |
| `system_transfer_total` | Integer | Total transfer menurut sistem |
| `system_qris_total` | Integer | Total QRIS menurut sistem |
| `actual_cash` | Integer | Uang fisik tunai yang dihitung kasir |
| `cash_difference` | Integer | Selisih (actual - system). 0 = match |
| `notes` | Text (nullable) | Catatan kasir |
| `is_locked` | Boolean | True setelah di-submit (tidak bisa diedit) |
| `submitted_at` | Datetime | Waktu submit |

---

## 5. Alur Pengguna Lengkap (User Flow)

### 5.1 Alur Barang Masuk (Admin)

```
Admin Login
    │
    ▼
Menu "Barang Masuk" → Klik "Catat Barang Masuk"
    │
    ▼
Isi Form Header:
  - Pilih Pemasok (dari dropdown Suppliers)
  - Tanggal Terima
  - Catatan (opsional)
    │
    ▼
Input Detail Barang (bisa lebih dari 1 baris):
  Baris 1: Pilih/Tambah Produk | Ukuran | Kondisi | Harga Beli | Qty
  Baris 2: ... (tambah baris)
    │
    ▼
Klik "Simpan"
    │
    ▼
Sistem: Simpan ke StockIns + StockInDetails
        → UPDATE Products SET stock = stock + qty [untuk setiap baris]
    │
    ▼
Produk muncul di Katalog dengan stok terupdate ✓
```

### 5.2 Alur Transaksi Penjualan (Kasir)

```
Kasir Login
    │
    ▼
Masuk Halaman POS
    │
    ▼
Pelanggan bawa sepatu → Kasir ketik nama/merek/ukuran di kolom pencarian
    │
    ▼
Produk muncul → Klik "+ Tambah ke Keranjang"
    │
    ▼
(Ulangi jika beli lebih dari 1 item)
    │
    ▼
Review Keranjang:
  - Cek daftar item & subtotal
  - Total otomatis terhitung
    │
    ▼
Pilih Metode Pembayaran:
  ┌─────────────┬──────────────────────────────────┐
  │  TUNAI      │ Input nominal → sistem hitung kembalian │
  │  TRANSFER   │ Kasir konfirmasi bukti transfer → klik Valid │
  │  QRIS       │ Kasir konfirmasi pembayaran scan → klik Valid │
  └─────────────┴──────────────────────────────────┘
    │
    ▼
Klik "Proses Bayar"
    │
    ▼
Sistem:
  → Simpan ke Transactions + TransactionDetails
  → UPDATE Products SET stock = stock - qty [setiap item]
  → Jika stock = 0, status produk → inactive
    │
    ▼
Pop-up Struk: No. Struk | Tanggal | Kasir | Item | Total | Metode Bayar
  → Kasir klik "Cetak" (browser print / thermal printer)
    │
    ▼
Transaksi selesai ✓
```

### 5.3 Alur Penutupan Shift / Closing (Kasir)

```
Akhir Shift → Kasir buka menu "Closing Shift"
    │
    ▼
Sistem tampilkan ringkasan hari ini (berdasarkan sesi kasir tersebut):
  - Total Tunai    : Rp XXX
  - Total Transfer : Rp XXX
  - Total QRIS     : Rp XXX
  - Grand Total    : Rp XXX
  - Jumlah Transaksi: N
    │
    ▼
Kasir hitung uang fisik di laci → input "Kas Fisik Aktual"
    │
    ▼
Sistem hitung Selisih = Kas Fisik - Total Tunai Sistem
  ┌──────────────────────────────────────┐
  │ Selisih = 0    → Status: MATCH ✓    │
  │ Selisih ≠ 0    → Status: SELISIH ⚠️ │
  └──────────────────────────────────────┘
    │
    ▼
Kasir tambah catatan (opsional) → Klik "Submit & Kunci"
    │
    ▼
Data closing tersimpan (is_locked = True) → Admin bisa lihat ✓
```

### 5.4 Alur Monitoring Admin (Harian)

```
Admin Login → Dashboard
    │
    ├── Lihat metrik harian (pendapatan, produk terjual, stok kritis)
    │
    ├── Jika ada barang baru masuk dari pemasok:
    │     → Menu "Barang Masuk" → Catat penerimaan
    │
    ├── Jika ingin lihat laporan periode tertentu:
    │     → Menu "Laporan Penjualan" → Filter tanggal → Cetak/Export PDF
    │
    ├── Jika ingin pantau closing kasir:
    │     → Menu "Closing" → Lihat semua closing hari ini
    │
    └── Jika stok produk habis (dari notif Dashboard):
          → Menu "Katalog" → Nonaktifkan produk atau update stok
```

---

## 6. Batasan Masalah (Project Constraints)

1. **Produk Sepatu Second Saja:** Sistem dirancang untuk toko sepatu bekas. Tidak mencakup penjualan aksesoris atau produk lain yang berbeda jenis.
2. **Satu Gudang / Satu Toko:** Sistem tidak mendukung multi-cabang atau multi-gudang. Stok bersifat terpusat.
3. **Tanpa Retur Barang ke Pemasok:** Jika barang dikembalikan ke pemasok, tidak dikelola dalam sistem ini. Koreksi stok dilakukan manual oleh Admin.
4. **Tanpa Retur dari Pelanggan:** Sistem tidak mengelola retur/pengembalian produk dari pelanggan ke toko.
5. **Metode Pembayaran Terbatas:** Hanya mendukung tiga metode: Tunai, Transfer Bank BRI, dan QRIS. Tidak ada integrasi payment gateway otomatis.
6. **Tanpa Manajemen Diskon Kompleks:** Diskon bersifat manual (admin ubah harga jual sebelum transaksi). Tidak ada modul promo/kupon otomatis.
7. **Hardware:** Sistem berbasis Web. Cetak struk menggunakan fungsi print browser standar (kompatibel dengan thermal printer 58mm/80mm). Tidak memerlukan integrasi barcode scanner khusus.
