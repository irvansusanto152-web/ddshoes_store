# Struktur Database DD Shoes Store (Kamus Data)

Dokumen ini mendeskripsikan seluruh model basis data (tabel) yang diimplementasikan dalam sistem **Point of Sale (POS) & Inventory DD Shoes Store** menggunakan Django ORM.

---

## 1. UserProfile (Pengguna Ekstensi)
Menyimpan informasi tambahan untuk sistem autentikasi bawaan Django (`auth_user`).

| Field | Tipe Data | Atribut Tambahan | Keterangan |
|---|---|---|---|
| `user` | OneToOneField | `User`, `CASCADE` | Relasi One-to-One dengan tabel akun utama |
| `role` | CharField(20) | `choices=('admin', 'kasir')` | Peran pengguna dalam sistem |
| `phone` | CharField(20) | `null=True`, `blank=True` | Nomor telepon kontak pengguna |

---

## 2. Categories (Kategori Produk)
Menyimpan data kategori dari produk sepatu yang dijual.

| Field | Tipe Data | Atribut Tambahan | Keterangan |
|---|---|---|---|
| `name` | CharField(100) | - | Nama kategori (contoh: Sneakers, Boots) |

---

## 3. Brands (Merek Produk)
Menyimpan data merek dari sepatu bekas yang dijual.

| Field | Tipe Data | Atribut Tambahan | Keterangan |
|---|---|---|---|
| `name` | CharField(100) | - | Nama merek (contoh: Nike, Adidas) |

---

## 4. Suppliers (Pemasok)
Menyimpan data pihak pemasok atau sumber barang bekas.

| Field | Tipe Data | Atribut Tambahan | Keterangan |
|---|---|---|---|
| `name` | CharField(100) | - | Nama orang atau pihak pemasok |
| `phone` | CharField(20) | `null=True`, `blank=True` | Nomor telepon pemasok |
| `notes` | TextField | `null=True`, `blank=True` | Catatan tambahan terkait pemasok |

---

## 5. Products (Katalog Produk)
Entitas sentral yang menyimpan seluruh data produk (sepatu) beserta stok dan harganya.

| Field | Tipe Data | Atribut Tambahan | Keterangan |
|---|---|---|---|
| `category` | ForeignKey | `Categories`, `SET_NULL` | Kategori sepatu |
| `brand` | ForeignKey | `Brands`, `SET_NULL` | Merek sepatu |
| `name` | CharField(255) | - | Nama/model spesifik sepatu |
| `size` | CharField(50) | - | Ukuran sepatu |
| `condition` | CharField(50) | `choices=('Baru', 'Like New', 'Good', 'Fair')` | Grade kondisi barang bekas |
| `description` | TextField | `null=True`, `blank=True` | Penjelasan detail mengenai kondisi/spesifikasi |
| `buy_price` | IntegerField | - | Harga beli produk (HPP) |
| `sell_price` | IntegerField | - | Harga jual ke pelanggan |
| `stock` | IntegerField | `default=0` | Jumlah stok yang tersedia |
| `image` | FileField | `upload_to='products/'` | Foto produk fisik |
| `status` | CharField(20) | `choices=('active', 'inactive')` | Aktif atau dinonaktifkan (karena habis) |
| `created_at` | DateTimeField | `auto_now_add=True` | Waktu produk ditambahkan ke sistem |

---

## 6. StockIns (Header Barang Masuk)
Mencatat header (dokumen induk) penerimaan barang masuk dari pemasok.

| Field | Tipe Data | Atribut Tambahan | Keterangan |
|---|---|---|---|
| `supplier` | ForeignKey | `Suppliers`, `SET_NULL` | Pemasok asal barang |
| `received_by`| ForeignKey | `User`, `SET_NULL` | Admin yang melakukan pencatatan |
| `received_date`| DateField | - | Tanggal penerimaan barang fisik |
| `notes` | TextField | `null=True`, `blank=True` | Catatan/kondisi penerimaan barang |
| `created_at` | DateTimeField | `auto_now_add=True` | Timestamp sistem penerimaan |

---

## 7. StockInDetails (Detail Barang Masuk)
Baris item spesifik (produk) yang diterima dalam satu sesi penerimaan barang masuk.

| Field | Tipe Data | Atribut Tambahan | Keterangan |
|---|---|---|---|
| `stock_in` | ForeignKey | `StockIns`, `CASCADE` | Referensi ke ID dokumen StockIn |
| `product` | ForeignKey | `Products`, `CASCADE` | Produk spesifik yang diterima |
| `quantity` | IntegerField | - | Jumlah unit produk masuk |
| `buy_price` | IntegerField | - | Harga beli pada saat penerimaan tersebut |
| `subtotal` | Property | - | Virtual field (Quantity x Buy Price) |

---

## 8. Transactions (Header Penjualan POS)
Mencatat header struk/transaksi penjualan kasir.

| Field | Tipe Data | Atribut Tambahan | Keterangan |
|---|---|---|---|
| `cashier` | ForeignKey | `User`, `SET_NULL` | Kasir yang bertugas |
| `subtotal_amount`| IntegerField | `default=0` | Total kotor penjualan sebelum diskon |
| `discount_amount`| IntegerField | `default=0` | Total nominal diskon |
| `total_amount` | IntegerField | - | Total bersih yang harus dibayar |
| `payment_method`| CharField(20) | `choices=('tunai', 'transfer_bri', 'qris')` | Metode pembayaran |
| `cash_received` | IntegerField | `null=True`, `blank=True` | Nominal tunai fisik yang diterima kasir |
| `change_amount` | IntegerField | `null=True`, `blank=True` | Nominal uang kembalian |
| `transaction_date`| DateTimeField | `auto_now_add=True` | Timestamp waktu transaksi berhasil |
| `status` | CharField(20) | `choices=('success', 'void')` | Status transaksi aktif atau dibatalkan |
| `voided_by` | ForeignKey | `User`, `SET_NULL` | User yang membatalkan (retur) |
| `void_reason` | TextField | `null=True`, `blank=True` | Alasan pembatalan transaksi |
| `voided_at` | DateTimeField | `null=True`, `blank=True` | Waktu pembatalan dilakukan |

---

## 9. TransactionDetails (Detail Penjualan POS)
Baris item produk spesifik yang terjual di dalam sebuah transaksi.

| Field | Tipe Data | Atribut Tambahan | Keterangan |
|---|---|---|---|
| `transaction` | ForeignKey | `Transactions`, `CASCADE` | Referensi ke ID struk transaksi |
| `product` | ForeignKey | `Products`, `PROTECT` | Produk yang terjual (mencegah hapus produk) |
| `quantity` | IntegerField | - | Jumlah unit produk yang dibeli |
| `sell_price` | IntegerField | - | Harga jual snapshot saat itu |
| `subtotal` | IntegerField | - | Total nilai baris ini (Qty x Sell Price) |

---

## 10. CashClosings (Penutupan Kasir)
Mencatat pelaporan dan rekonsiliasi jumlah uang kasir pada setiap akhir shift kerja.

| Field | Tipe Data | Atribut Tambahan | Keterangan |
|---|---|---|---|
| `cashier` | ForeignKey | `User`, `CASCADE` | Kasir yang bertanggung jawab atas shift |
| `closing_date`| DateField | - | Tanggal operasional shift |
| `system_cash_total`| IntegerField| - | Total tunai transaksi berdasarkan sistem |
| `system_transfer_total`| IntegerField| - | Total transfer BRI transaksi sistem |
| `system_qris_total`| IntegerField| - | Total QRIS transaksi berdasarkan sistem |
| `actual_cash` | IntegerField| - | Uang tunai fisik aktual yang dihitung kasir |
| `cash_difference`| IntegerField| - | Selisih uang fisik dengan data sistem |
| `notes` | TextField | `null=True`, `blank=True` | Catatan tambahan dari kasir |
| `is_locked` | BooleanField | `default=False` | Kunci keamanan agar data tidak bisa diubah |
| `submitted_at`| DateTimeField | `auto_now_add=True` | Timestamp penyerahan laporan closing |
| `unlocked_by` | ForeignKey | `User`, `SET_NULL` | (Audit) Admin yang membuka kembali data |
| `unlocked_at` | DateTimeField | `null=True`, `blank=True` | (Audit) Waktu re-open laporan |
| `unlock_reason`| TextField | `null=True`, `blank=True` | (Audit) Alasan re-open laporan |
| `unlock_count`| IntegerField | `default=0` | (Audit) Berapa kali laporan ini dibuka ulang |

---

## 11. StockAdjustments (Penyesuaian Stok)
Mencatat perubahan/pengurangan stok yang tidak berasal dari jalur penjualan atau pembelian (misal: hilang, rusak, retur pemasok).

| Field | Tipe Data | Atribut Tambahan | Keterangan |
|---|---|---|---|
| `product` | ForeignKey | `Products`, `SET_NULL` | Produk yang stoknya disesuaikan |
| `adjusted_by` | ForeignKey | `User`, `SET_NULL` | Admin yang melakukan koreksi |
| `quantity` | IntegerField | - | Jumlah koreksi (bisa minus/negatif) |
| `reason` | CharField(20) | `choices=('rusak', 'hilang', 'retur', 'lainnya')` | Kategori penyebab koreksi |
| `notes` | TextField | `null=True`, `blank=True` | Deskripsi detail dari penyesuaian |
| `adjusted_at` | DateTimeField | `auto_now_add=True` | Waktu penyesuaian dilakukan |
