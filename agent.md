# 🤖 Agent Instructions — DD Shoes POS Development

> File ini adalah **panduan wajib** yang harus dibaca dan diikuti oleh AI Agent sebelum dan sesudah melakukan setiap perubahan pada project ini.

---

## ⚠️ ATURAN UTAMA (WAJIB DIIKUTI)

### Sebelum Memulai Setiap Pekerjaan:

1. **Baca PRD terlebih dahulu** → `pos_ddshoes/docs/prd.md`
   - Pahami konteks bisnis, alur barang, dan kebutuhan fitur
   - Pastikan perubahan yang akan dilakukan sesuai dengan requirement di PRD
   - Jangan membuat fitur yang bertentangan atau keluar dari scope PRD

2. **Baca Design System** → `pos_ddshoes/docs/design_system.md`
   - Setiap halaman WAJIB menggunakan komponen, warna, dan CSS yang sudah didefinisikan
   - Jangan membuat gaya baru yang bertentangan dengan sistem desain
   - Gunakan CSS Variables yang sudah ada (`:root { --color-primary, ... }`)

3. **Baca Task List** → `pos_ddshoes/docs/task.md`
   - Cek item mana yang sudah selesai (`[x]`) dan mana yang belum (`[ ]`)
   - Kerjakan task secara berurutan sesuai fase (Fase 0 → 1 → 2 → dst)
   - Tandai item yang sedang dikerjakan dengan `[/]`

### Setelah Selesai Setiap Pekerjaan:

4. **Verifikasi Sistem (PENTING)** → sebelum menandai task selesai:
   - Jalankan `python manage.py check` untuk memastikan tidak ada error konfigurasi atau syntax.
   - Jika ada error yang terdeteksi, perbaiki seketika (langsung fix) sebelum melanjutkan.

5. **Update task.md** → segera setelah fitur diverifikasi dan berjalan baik:
   - Tandai task yang baru saja selesai dengan `[x]`
   - Update Progress Tracker di bagian bawah task.md
   - Jika ada sub-task yang selesai, tandai juga semua sub-task-nya

6. **Git Commit & Push (WAJIB)** → sebagai penutup setiap pengerjaan fitur:
   - Jalankan `git add .`
   - Buat commit dengan pesan *best practice* (Conventional Commits), misal: `feat: implement login authentication` atau `fix: resolve image field dependency`.
   - Jalankan `git commit -m "pesan commit"`
   - Jalankan `git push`

---

## 📋 Workflow Standar

```
START
  │
  ▼
1. Baca prd.md → pahami requirement
  │
  ▼
2. Baca task.md → identifikasi item yang akan dikerjakan
  │
  ▼
3. Tandai item yang sedang dikerjakan → [/] di task.md
  │
  ▼
4. Buat / ubah kode sesuai PRD + Design System
  │
  ▼
5. Verifikasi hasil pekerjaan (fungsional + tampilan)
   & Jalankan `python manage.py check` (Fix error jika ada)
  │
  ▼
6. Tandai item selesai → [x] di task.md
  │
  ▼
7. Update Progress Tracker di task.md
  │
  ▼
8. Git Commit & Push (dengan pesan best practice)
  │
  ▼
END
```

---

## 📁 Referensi File Penting

| File | Path | Fungsi |
|------|------|--------|
| **PRD** | `pos_ddshoes/docs/prd.md` | Requirement bisnis & fitur lengkap |
| **Design System** | `pos_ddshoes/docs/design_system.md` | Panduan visual & komponen UI |
| **Task List** | `pos_ddshoes/docs/task.md` | Checklist progress pengerjaan |
| **Settings** | `pos_ddshoes/settings.py` | Konfigurasi Django |
| **URLs Utama** | `pos_ddshoes/urls.py` | Routing utama project |

---

## ✅ Konvensi Checklist task.md

```markdown
[ ]  → Belum dikerjakan
[/]  → Sedang dikerjakan (in progress)
[x]  → Selesai
```

**Contoh update yang benar:**

Sebelum mengerjakan:
```markdown
- [/] Buat `models.py` — definisikan semua tabel sesuai PRD
```

Setelah selesai:
```markdown
- [x] Buat `models.py` — definisikan semua tabel sesuai PRD
  - [x] `UserProfile`
  - [x] `Categories`
  - [x] `Brands`
  ...
```

---

## 🛡️ Aturan Tambahan

### Keamanan
- Semua view yang memerlukan login → wajib pakai `@login_required`
- Semua view Admin → wajib cek `request.user.userprofile.role == 'admin'`
- Semua AJAX POST → wajib sertakan header `X-CSRFToken`

### Database
- Setiap perubahan model → jalankan `makemigrations` + `migrate`
- Jangan hapus data migration yang sudah ada
- Saat stok produk berubah lewat `StockInDetails` atau `TransactionDetails` → update field `stock` di tabel `Products` secara otomatis (via signals atau `save()` override)

### Kode
- Gunakan response JSON standar untuk semua AJAX:
  - Sukses: `{ "status": "success" }`
  - Gagal: `{ "status": "failed", "msg": "pesan error" }`
- Setiap template → extend `base.html` dan gunakan `{% block pageContent %}`
- Semua URL dinamis di template → gunakan `{% url 'nama_url' %}`

### Tampilan
- Wajib mengikuti design_system.md untuk setiap komponen
- Stat cards → gunakan class `.stat-card` dengan tema warna yang sesuai
- Header halaman → gunakan `.saas-header` + `.sh-title` + `.btn-tambah`
- Toolbar → gunakan `.saas-toolbar` + `.search-box` + `.filter-box`
- Tombol aksi di tabel/card → gunakan `.btn-icon-edit` dan `.btn-icon-delete`

---

## 🚫 Hal yang TIDAK Boleh Dilakukan

- ❌ Membuat halaman tanpa mengecek PRD terlebih dahulu
- ❌ Membuat gaya CSS baru yang bertentangan dengan design_system.md
- ❌ Menandai task selesai di task.md sebelum fitur benar-benar berfungsi
- ❌ Melewati fase yang belum selesai (harus berurutan)
- ❌ Membuat fitur di luar scope yang didefinisikan di PRD Section 6 (Batasan Masalah)
- ❌ Lupa update task.md setelah menyelesaikan pekerjaan

---

## 📌 Quick Reference — Scope Sistem (dari PRD)

### Role & Akses
- **Admin** → Semua halaman (Master Data, Inventory, Laporan, Closing, Manajemen User)
- **Kasir** → Hanya: POS, Katalog (read-only), Closing Shift sendiri

### Metode Pembayaran yang Didukung
- Tunai (hitung kembalian otomatis)
- Transfer BRI
- QRIS

### Batasan Sistem
- Satu toko / satu gudang (tidak multi-cabang)
- Tidak ada retur barang (ke pemasok maupun dari pelanggan)
- Tidak ada modul diskon/promo otomatis
- Cetak struk via browser print standard (kompatibel thermal printer 58mm/80mm)
