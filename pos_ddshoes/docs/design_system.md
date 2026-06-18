# 🎨 Design Guide — DD Shoes POS Style System

> Panduan ini mendokumentasikan **seluruh sistem desain** yang digunakan di project DD Shoes POS.
> Tujuannya agar project baru dapat mereplikasi tampilan yang **sama persis** tanpa harus menyalin konten bisnis-nya.

---

## 📦 Dependencies / Library

Semua library berikut wajib disertakan di setiap halaman:

```html
<!-- Fonts -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">

<!-- CSS Framework -->
<link rel="stylesheet" href="[bootstrap 5]/bootstrap.min.css">
<link rel="stylesheet" href="[material-admin]/vendors/mdi/css/materialdesignicons.min.css">
<link rel="stylesheet" href="[material-admin]/vendors/css/vendor.bundle.base.css">
<link rel="stylesheet" href="[material-admin]/css/demo/style.css">
<link rel="stylesheet" href="[select2]/dist/css/select2.min.css">
<link rel="stylesheet" href="[custom]/style.css">

<!-- JS -->
<script src="[custom]/jquery-3.6.0.min.js"></script>
<script src="[bootstrap]/bootstrap.bundle.min.js"></script>
<script src="[material-admin]/js/preloader.js"></script>  <!-- harus paling atas di body -->
<script src="[material-admin]/vendors/js/vendor.bundle.base.js"></script>
<script src="[material-admin]/js/material.js"></script>
<script src="[material-admin]/js/misc.js"></script>
<script src="[select2]/dist/js/select2.full.js"></script>
```

> **Catatan:** Preloader script (`preloader.js`) harus diletakkan **paling atas** di dalam `<body>`, sebelum konten lainnya. Ini yang mengontrol animasi loading halaman.

---

## 🎨 Color Palette

### Global CSS Variables (dipakai hampir di semua halaman)

```css
:root {
    /* --- WARNA UTAMA --- */
    --color-primary:       #4f46e5;   /* Indigo — tombol, fokus, aksen */
    --color-primary-hover: #4338ca;
    --color-primary-light: #e0e7ff;   /* Ring fokus input */

    /* --- WARNA STATUS --- */
    --color-success: #10b981;   /* Hijau emerald */
    --color-danger:  #ef4444;   /* Merah */
    --color-info:    #0ea5e9;   /* Biru langit */

    /* --- BACKGROUND --- */
    --bg-body:  #f8fafc;   /* Abu-abu sangat terang (body utama) */
    --bg-card:  #ffffff;   /* Putih (kartu/panel) */
    --bg-main:  #f8fafc;

    /* --- BORDER --- */
    --border-soft:  #e2e8f0;
    --border-glass: rgba(255,255,255,0.9);

    /* --- TEKS --- */
    --text-main:    #0f172a;   /* Hampir hitam — judul & teks utama */
    --text-heading: #0f172a;
    --text-body:    #334155;
    --text-sub:     #64748b;   /* Abu-abu — teks sekunder, placeholder */
    --text-muted:   #64748b;

    /* --- SHADOW --- */
    --shadow-card:  0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
    --shadow-hover: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
    --shadow-glass: 0 6px 24px -6px rgba(31,38,135,0.1);

    /* --- RADIUS --- */
    --radius-2xl: 18px;
    --radius-xl:  14px;
    --radius-lg:  10px;

    /* --- GRADIEN KARTU DASHBOARD --- */
    --grad-blue:    linear-gradient(135deg, #0ea5e9, #3b82f6);
    --grad-emerald: linear-gradient(135deg, #10b981, #14b8a6);
    --grad-violet:  linear-gradient(135deg, #8b5cf6, #d946ef);
    --grad-amber:   linear-gradient(135deg, #f59e0b, #ef4444);
}
```

### Warna Sidebar (Dark Theme)
| Elemen | Nilai |
|--------|-------|
| Background sidebar | `#06091a` (biru-hitam gelap) |
| Border sidebar | `rgba(100, 200, 255, 0.07)` |
| Text link nav | `rgb(255, 255, 255)` |
| Icon nav (default) | `rgba(100, 220, 255, 0.7)` |
| Link aktif background | `rgba(100, 220, 255, 0.1)` |
| Link aktif text/icon | `#5adbff` |
| Link aktif border | `rgba(100, 220, 255, 0.2)` |
| Link hover background | `rgba(255, 255, 255, 0.94)` |
| Link hover text | `#06091a` |
| Link hover icon | `#1a73e8` |

---

## 🔤 Typography

| Elemen | Font | Weight | Size |
|--------|------|--------|------|
| Font utama (body) | `Inter, sans-serif` | 400 | `11.5px` (dashboard) |
| Judul halaman | `Inter` | 800 | `1.6rem` |
| Subjudul / subtext | `Inter` | 500 | `0.9rem` |
| Brand name sidebar | `Georgia, Times New Roman, serif` | 700 | `15px` |
| Label section sidebar | System font | 700 | `9px`, UPPERCASE |
| Nav link | System (`-apple-system, Segoe UI`) | 500 | `13px` |
| Angka statistik | `Inter` | 800 | `1.35rem` |
| Label statistik | `Inter` | 800 | `0.7rem`, UPPERCASE |

---

## 🏗️ Layout Struktur

```
body
└── .body-wrapper
    ├── aside#mainSidebar  (.mdc-drawer)    ← Sidebar fixed left, lebar 240px
    └── .main-wrapper.mdc-drawer-app-content
        ├── header.mdc-top-app-bar          ← Topbar
        └── .page-wrapper
            └── main.content-wrapper
                └── .mdc-layout-grid
                    └── .mdc-layout-grid__inner
                        └── {% block pageContent %}
```

**Perilaku sidebar:**
- Default: terbuka (`margin-left: 240px` pada `.mdc-drawer-app-content`)
- State disimpan di `localStorage` dengan key khusus
- Toggle diatur oleh fungsi global `window.toggleSidebar()`
- Sidebar collapse: tambahkan class `.sidebar-collapsed` pada `aside`, body dapat class `sidebar-open` atau `sidebar-closed`

---

## 🗂️ Komponen: Sidebar

```html
<aside class="mdc-drawer mdc-drawer--dismissible mdc-drawer--open" id="mainSidebar">
    <!-- Particle canvas background -->
    <canvas id="sb-particle-canvas"></canvas>
    <!-- Dua scanline animasi -->
    <div class="sb-scanline"></div>
    <div class="sb-scanline-2"></div>

    <div class="sb-inner">
        <!-- BRAND / LOGO AREA -->
        <div class="sb-brand">
            <div class="sb-logo-wrap" id="sbLogoWrap" title="Klik untuk ganti logo">
                <div class="sb-logo-inner">
                    <!-- SVG atau img logo -->
                    <div id="sbLogoDefault"><!-- SVG ikon default --></div>
                    <img id="sb-logo-img" src="" alt="Logo" style="display:none;">
                    <div class="sb-logo-overlay">
                        <!-- Ikon upload + teks "Ganti" -->
                    </div>
                </div>
                <div class="sb-logo-ring"></div>    <!-- Ring berputar 1 -->
                <div class="sb-logo-ring-2"></div>  <!-- Ring berputar 2 -->
            </div>
            <span class="sb-brand-name">NAMA TOKO</span>
            <span class="sb-brand-sub">SUBTITLE</span>
            <button class="sb-logo-reset" id="sbLogoReset">✕ reset logo</button>
        </div>

        <!-- NAVIGASI -->
        <div class="sb-nav">
            <ul class="mdc-list">
                <!-- Glow divider (pemisah antar section) -->
                <div class="sb-glow-divider"></div>
                <!-- Section label -->
                <div class="sb-section-label">SECTION NAME</div>

                <li class="mdc-drawer-item">
                    <a class="mdc-drawer-link" href="/url">
                        <i class="material-icons">icon_name</i>
                        <span>Menu Label</span>
                    </a>
                </li>
            </ul>
        </div>
    </div>

    <input type="file" id="logoUploadInput" accept="image/*">
    <div class="sb-toast" id="sbToast"></div>
</aside>

<!-- Backdrop untuk mobile -->
<div id="sb-backdrop" onclick="toggleSidebar()"></div>
```

### CSS Sidebar Lengkap

```css
/* BASE */
aside.mdc-drawer {
    background: #06091a;
    width: 240px;
    min-height: 100vh;
    position: fixed;
    top: 0; left: 0;
    overflow: hidden;
    border-right: 1px solid rgba(100, 200, 255, 0.07);
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 100;
    display: flex; flex-direction: column;
}
aside.mdc-drawer.sidebar-collapsed { transform: translateX(-240px); }

/* CONTENT OFFSET */
body.sidebar-open  .mdc-drawer-app-content { margin-left: 240px !important; }
body.sidebar-closed .mdc-drawer-app-content { margin-left: 0 !important; }

/* SCANLINE ANIMASI */
.sb-scanline, .sb-scanline-2 {
    position: absolute; top: 0; bottom: 0; width: 1px; z-index: 1; pointer-events: none;
}
.sb-scanline   { background: linear-gradient(to bottom, transparent, rgba(100,200,255,0.06), transparent); animation: scanMove 7s ease-in-out infinite; }
.sb-scanline-2 { background: linear-gradient(to bottom, transparent, rgba(100,200,255,0.04), transparent); animation: scanMove2 11s ease-in-out infinite; }
@keyframes scanMove  { 0%,100%{ left:20%; opacity:.3 } 50%{ left:36%; opacity:.9 } }
@keyframes scanMove2 { 0%,100%{ left:68%; opacity:.2 } 50%{ left:78%; opacity:.6 } }

/* INNER */
.sb-inner { position:relative; z-index:2; display:flex; flex-direction:column; height:100%; overflow-y:auto; overflow-x:hidden; scrollbar-width:none; }
.sb-inner::-webkit-scrollbar { display:none; }

/* BRAND */
.sb-brand { padding:28px 16px 20px; display:flex; flex-direction:column; align-items:center; border-bottom:1px solid rgba(255,255,255,0.05); }

/* LOGO WRAP */
.sb-logo-wrap {
    width:68px; height:68px; border-radius:20px; position:relative;
    background:rgba(24,255,193,0.04); border:1px solid rgba(255,29,29,0.14);
    animation:logoPulse 4s ease-in-out infinite; transition:transform 0.3s ease;
    display:flex; align-items:center; justify-content:center;
}
.sb-logo-wrap:hover { transform:scale(1.06); }
@keyframes logoPulse {
    0%,100% { box-shadow:0 0 0 0 rgba(50,180,255,0); border-color:rgba(100,200,255,0.14); }
    50%     { box-shadow:0 0 0 8px rgba(50,180,255,0.07), 0 0 26px rgba(50,180,255,0.06); border-color:rgba(100,200,255,0.32); }
}

/* ROTATING RINGS */
.sb-logo-ring {
    position:absolute; inset:-6px; border-radius:26px; border:1px solid transparent;
    border-top-color:rgba(255,100,198,0.45); border-right-color:rgba(100,220,255,0.1);
    animation:ringRotate 5s linear infinite; pointer-events:none;
}
.sb-logo-ring-2 {
    position:absolute; inset:-10px; border-radius:30px; border:1px solid transparent;
    border-bottom-color:rgb(100,227,255); border-left-color:rgba(100,220,255,0.06);
    animation:ringRotate2 9s linear infinite; pointer-events:none;
}
@keyframes ringRotate  { from{ transform:rotate(0deg)   } to{ transform:rotate(360deg)  } }
@keyframes ringRotate2 { from{ transform:rotate(0deg)   } to{ transform:rotate(-360deg) } }

/* BRAND TEXT */
.sb-brand-name {
    margin-top:14px; font-size:15px; font-weight:700;
    color:#fff; font-family:'Georgia','Times New Roman',serif;
    letter-spacing:0.06em; text-align:center;
    animation:nameBreathe 5s ease-in-out infinite;
}
@keyframes nameBreathe { 0%,100%{ letter-spacing:0.06em; opacity:.88; } 50%{ letter-spacing:0.13em; opacity:1; } }

.sb-brand-sub {
    margin-top:5px; font-size:9px; color:#fff; font-weight:700;
    letter-spacing:0.24em; text-transform:uppercase;
    animation:subBlink 5s ease-in-out infinite;
}
@keyframes subBlink { 0%,100%{ opacity:.5 } 50%{ opacity:1 } }

/* GLOW DIVIDER */
.sb-glow-divider {
    height:1px; background:rgba(255,0,0,0.05); margin:8px 14px;
    position:relative; overflow:hidden;
}
.sb-glow-divider::after {
    content:''; position:absolute; top:-1px; left:-24px; width:24px; height:3px;
    border-radius:2px; background:rgba(255,100,250,0.5);
    animation:glowDot 4s ease-in-out infinite;
}
@keyframes glowDot { 0%{left:-24px;opacity:0} 8%{opacity:1} 92%{opacity:1} 100%{left:100%;opacity:0} }

/* SECTION LABEL */
.sb-section-label {
    font-size:9px; color:rgba(232,232,232,0.537); padding:10px 16px 4px;
    letter-spacing:0.14em; text-transform:uppercase; font-weight:700;
}

/* NAV AREA */
.sb-nav { padding:8px 10px; flex:1; }
.mdc-list { list-style:none; padding:0; margin:0; }
.mdc-drawer-item { margin-bottom:2px; }

/* NAV LINK */
.mdc-drawer-link {
    display:flex; align-items:center; gap:11px; padding:9px 13px;
    border-radius:10px; text-decoration:none; color:#fff;
    font-size:13px; font-weight:500;
    font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
    transition:background 0.22s, color 0.22s, transform 0.22s, border-color 0.22s;
    border:1px solid transparent;
}
.mdc-drawer-link .material-icons { font-size:17px; color:rgba(100,220,255,0.7); }
.mdc-drawer-link:hover {
    background:rgba(255,255,255,0.94); color:#06091a;
    transform:translateX(3px); border-color:rgb(17,37,255);
}
.mdc-drawer-link:hover .material-icons { color:#1a73e8; }
.mdc-drawer-link.active { background:rgba(100,220,255,0.1); color:#5adbff; border-color:rgba(100,220,255,0.2); }
.mdc-drawer-link.active .material-icons { color:#5adbff; }
```

> **Fitur interaktif sidebar:**
> - Klik area logo → membuka file picker untuk upload logo kustom
> - Logo disimpan di `localStorage` (max 2MB)
> - Tombol "reset logo" muncul setelah logo diupload
> - Active link dideteksi otomatis dari `window.location.pathname`
> - Particle canvas: 45 titik warna `rgba(100,200,255,...)` bergerak dan tersambung dengan garis jika jarak < 60px

---

## 🔝 Komponen: Topbar (Header)

```html
<header class="mdc-top-app-bar border-bottom shadow">
    <div class="mdc-top-app-bar__row">
        <!-- Kiri: Hamburger menu -->
        <div class="mdc-top-app-bar__section mdc-top-app-bar__section--align-start">
            <button class="material-icons mdc-top-app-bar__navigation-icon mdc-icon-button sidebar-toggler">
                menu
            </button>
        </div>
        <!-- Kanan: Profil user -->
        <div class="mdc-top-app-bar__section mdc-top-app-bar__section--align-end">
            <div class="menu-button-container menu-profile d-none d-md-block">
                <button class="mdc-button mdc-menu-button">
                    <span class="d-flex align-items-center">
                        <span class="figure" style="display:flex; align-items:center; justify-content:center;
                              background:#e2e8f0; border-radius:50%; width:35px; height:35px; margin-right:10px;">
                            <!-- Superuser: mdi-shield-account (color: #6366f1) -->
                            <!-- Kasir: mdi-store (color: #10b981) -->
                        </span>
                        <span class="user-name" style="font-weight:600; color:#334155;">
                            Administrator <!-- atau Kasir -->
                        </span>
                    </span>
                </button>
                <!-- Dropdown menu -->
                <div class="mdc-menu mdc-menu-surface">
                    <ul class="mdc-list" role="menu">
                        <li class="mdc-list-item"><!-- Link Admin (superuser only) --></li>
                        <li class="mdc-list-item"><!-- Link Logout --></li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</header>
```

---

## 🔐 Komponen: Halaman Login

Login menggunakan **layout 2 kolom** (split screen):
- **Kiri (60%):** Hero image + overlay gelap + branding + slogan
- **Kanan (40%):** Form login clean, background putih

```css
/* WRAPPER */
body.login-body { font-family:'Inter',sans-serif; overflow:hidden; background:#f8fafc; height:100vh; }
.auth-wrapper   { display:flex; height:100%; width:100%; }

/* SISI KIRI — HERO */
.auth-image-side {
    flex: 1.3; position:relative; background:#0f172a;
    overflow:hidden; display:flex; flex-direction:column;
    justify-content:space-between; padding:60px;
}
/* Gambar background via ::before (background-image: url dari Unsplash atau gambar lokal) */
/* Gradient overlay via ::after: linear-gradient(180deg, rgba(15,23,42,0.4) 0%, rgba(15,23,42,0.9) 100%) */
/* Animasi masuk: imageZoomIn 2s ease-out forwards (scale 1.08 → 1) */

/* SISI KANAN — FORM */
.auth-form-side { flex:1; background:#fff; display:flex; align-items:center; justify-content:center; padding:40px; }
.auth-form-box  { width:100%; max-width:400px; animation:formSlideUp 0.6s cubic-bezier(0.22,1,0.36,1) forwards; }

/* FORM HEADER */
.form-header h2 { font-size:2rem; font-weight:800; color:#0f172a; letter-spacing:-1px; }
.form-header p  { font-size:1rem; color:#64748b; }

/* INPUT GRUP */
.saas-input-group { position:relative; }
.saas-input-group i { position:absolute; left:16px; top:14px; color:#94a3b8; font-size:20px; }
.saas-input {
    width:100%; padding:14px 16px 14px 48px; height:52px;
    border:2px solid #e2e8f0; border-radius:14px;
    font-family:'Inter',sans-serif; font-size:1rem; font-weight:500;
    background:#f8fafc; transition:all 0.3s cubic-bezier(0.4,0,0.2,1);
}
.saas-input:focus { border-color:#4f46e5; background:#fff; box-shadow:0 0 0 4px #e0e7ff; }

/* TOMBOL SUBMIT */
.btn-masuk {
    all:unset; display:flex; align-items:center; justify-content:center; gap:8px;
    background:#4f46e5; color:#fff; padding:14px 20px; border-radius:14px;
    font-weight:700; font-size:1.05rem; cursor:pointer; width:100%;
    box-shadow:0 4px 12px rgba(79,70,229,0.2); transition:all 0.3s cubic-bezier(0.4,0,0.2,1);
}
.btn-masuk:hover { background:#4338ca; transform:translateY(-2px); box-shadow:0 8px 20px rgba(79,70,229,0.35); }
.btn-masuk i     { font-size:20px; transition:transform 0.3s ease; }
.btn-masuk:hover i { transform:translateX(6px); }

/* GLASSMORPHISM BADGE (di sisi kiri bawah) */
.glass-badge {
    display:inline-flex; align-items:center; gap:12px;
    background:rgba(255,255,255,0.1); backdrop-filter:blur(12px);
    border:1px solid rgba(255,255,255,0.2); padding:12px 20px; border-radius:100px;
}
```

---

## 📊 Komponen: Dashboard — Stat Cards

4 kartu statistik di baris atas, tersusun dalam grid 4 kolom:

```css
.stats-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:0.75rem; }

.stat-card {
    border:1px solid var(--border-glass); border-radius:var(--radius-2xl);
    padding:1rem; display:flex; flex-direction:column; gap:0.5rem;
    box-shadow:var(--shadow-glass); transition:all 0.35s var(--ease-spring);
    position:relative; overflow:hidden; cursor:pointer;
}
.stat-card:hover { transform:translateY(-5px); box-shadow:var(--shadow-hover); border-color:#fff; }

/* 4 TEMA WARNA KARTU */
.card-cat  { background:linear-gradient(135deg, rgba(250,92,255,0.9) 0%, rgba(139,92,246,0.15) 100%); border-bottom:3px solid rgba(139,92,246,0.4); }
.card-prod { background:linear-gradient(135deg, rgba(63,255,137,0.9) 0%, rgba(16,185,129,0.15) 100%);  border-bottom:3px solid rgba(16,185,129,0.4); }
.card-ord  { background:linear-gradient(135deg, rgba(30,221,255,0.9) 0%, rgba(14,165,233,0.15) 100%);  border-bottom:3px solid rgba(14,165,233,0.4); }
.card-rev  { background:linear-gradient(135deg, rgba(255,184,70,0.9) 0%, rgba(245,158,11,0.15) 100%);  border-bottom:3px solid rgba(245,158,11,0.4); }

/* IKON LATAR (besar, opacity rendah, rotate saat hover) */
.bg-icon { position:absolute; right:-10px; bottom:-20px; font-size:110px !important; opacity:0.05; transition:all 0.5s; }
.stat-card:hover .bg-icon { transform:scale(1.15) rotate(-10deg); opacity:0.12; }

/* ICON BOX (kanan atas) */
.icon-box { width:38px; height:38px; border-radius:var(--radius-lg); display:flex; align-items:center; justify-content:center; color:white; }
.ib-1 { background:var(--grad-violet); box-shadow:0 6px 14px rgba(139,92,246,0.35); }
.ib-2 { background:var(--grad-emerald); box-shadow:0 6px 14px rgba(16,185,129,0.35); }
.ib-3 { background:var(--grad-blue);    box-shadow:0 6px 14px rgba(14,165,233,0.35); }
.ib-4 { background:var(--grad-amber);   box-shadow:0 6px 14px rgba(245,158,11,0.35); }
```

**Struktur HTML 1 kartu:**
```html
<div class="stat-card card-cat" onclick="...">
    <i class="material-icons bg-icon" style="color:#8b5cf6;">icon_name</i>
    <div class="stat-header">
        <span class="stat-label">LABEL KARTU</span>
        <div class="icon-box ib-1"><i class="material-icons">icon_name</i></div>
    </div>
    <div><p class="stat-val">123</p></div>
</div>
```

---

## 📈 Komponen: Dashboard — Glass Panel (Chart & Leaderboard)

```css
/* LAYOUT: 2 kolom (7:3) */
.main-grid { display:grid; grid-template-columns:minmax(0,7fr) minmax(0,3fr); gap:0.75rem; }

/* GLASS PANEL */
.glass-panel {
    background:rgba(255,255,255,0.75); backdrop-filter:blur(24px);
    border:1px solid rgba(255,255,255,0.9); border-radius:var(--radius-2xl);
    padding:1rem 1.25rem; box-shadow:var(--shadow-glass);
}

/* PANEL HEADER */
.panel-head { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.8rem; }
.ph-icon    { width:36px; height:36px; border-radius:var(--radius-lg); display:flex; align-items:center; justify-content:center; color:white; }
.ph-title h3 { font-size:0.95rem; font-weight:800; color:#0f172a; margin:0 0 2px 0; }
.ph-title p  { font-size:0.7rem; color:#64748b; margin:0; }

/* CHART FILTER TABS */
.chart-filters { display:flex; background:rgba(255,255,255,0.6); padding:3px; border-radius:8px; border:1px solid rgba(255,255,255,0.9); }
.filter-btn { background:transparent; border:none; padding:5px 12px; font-size:0.7rem; font-weight:700; color:#64748b; border-radius:6px; cursor:pointer; transition:all 0.3s; }
.filter-btn.active { background:#fff; color:#6366f1; box-shadow:0 3px 8px rgba(0,0,0,0.08); }
```

**Chart.js konfigurasi (garis, gradient fill):**
```js
// Gradient fill
const gradientFill = ctx.createLinearGradient(0, 0, 0, 280);
gradientFill.addColorStop(0,   'rgba(99,102,241,0.55)');
gradientFill.addColorStop(0.5, 'rgba(236,72,153,0.18)');
gradientFill.addColorStop(1,   'rgba(255,255,255,0)');

// Dataset config
{
    borderColor: '#6366f1', borderWidth: 3,
    backgroundColor: gradientFill,
    fill: true, tension: 0.4,
    pointRadius: 0, pointHoverRadius: 7,
    pointBackgroundColor: '#fff',
    pointBorderColor: '#ec4899', pointBorderWidth: 2.5,
}

// Tooltip dark
tooltip: {
    backgroundColor: 'rgba(15,23,42,0.9)',
    titleColor: '#f8fafc', bodyColor: '#fff',
    padding: 12, cornerRadius: 12,
}
```

---

## 📋 Komponen: Halaman Data (Table + Card Grid)

### Page Header (judul + tombol tambah)

```html
<div class="saas-header">
    <div class="sh-title">
        <h2>Judul Halaman</h2>
        <p>Deskripsi singkat halaman</p>
    </div>
    <button class="btn-tambah" onclick="...">
        <i class="material-icons">add</i>
        Tambah Data
    </button>
</div>
```

```css
.saas-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; flex-wrap:wrap; gap:16px; }
.sh-title h2 { font-size:1.6rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin:0; }
.sh-title p  { font-size:0.9rem; color:#64748b; font-weight:500; margin:4px 0 0 0; }

/* TOMBOL TAMBAH */
.btn-tambah {
    all:unset; display:inline-flex; align-items:center; gap:8px;
    background:linear-gradient(135deg, #4f46e5, #6366f1); color:#fff;
    padding:10px 20px; border-radius:50px; font-size:0.9rem; font-weight:600;
    box-shadow:0 4px 12px rgba(79,70,229,0.3); cursor:pointer;
    transition:all 0.3s cubic-bezier(0.4,0,0.2,1);
}
.btn-tambah:hover { transform:translateY(-2px); box-shadow:0 8px 15px rgba(79,70,229,0.4); }
```

### Toolbar Pencarian & Filter

```html
<div class="saas-toolbar">
    <div class="search-box">
        <i class="material-icons">search</i>
        <input type="text" placeholder="Cari...">
    </div>
    <div class="filter-box">
        <i class="material-icons">filter_list</i>
        <select>...</select>
    </div>
</div>
```

```css
.saas-toolbar { display:flex; gap:16px; margin-bottom:24px; flex-wrap:wrap; }
.search-box, .filter-box {
    position:relative; display:flex; align-items:center;
    background:#fff; border:1px solid #e2e8f0; border-radius:12px;
    padding:8px 16px; box-shadow:0 2px 4px rgba(0,0,0,0.02); transition:all 0.3s ease;
}
.search-box:focus-within, .filter-box:focus-within {
    border-color:#4f46e5; box-shadow:0 0 0 3px rgba(79,70,229,0.1);
}
```

---

## 🃏 Komponen: Card Grid (Kategori)

Untuk tampilan data berbasis kartu (bukan tabel):

```css
.card-grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(220px, 1fr)); gap:16px; }

.item-card {
    background:#fff; border:1px solid #e2e8f0; border-radius:16px;
    overflow:hidden; transition:all 0.3s cubic-bezier(0.4,0,0.2,1);
    box-shadow:0 4px 6px -1px rgba(0,0,0,0.05);
}
.item-card:hover { transform:translateY(-4px); box-shadow:0 10px 15px -3px rgba(0,0,0,0.1); border-color:rgba(79,70,229,0.3); }

/* Gambar / thumbnail atas */
.card-image-area { height:140px; background:#f8fafc; position:relative; overflow:hidden; }
.card-image-area img { width:100%; height:100%; object-fit:cover; }

/* Badge status */
.status-badge {
    position:absolute; top:10px; right:10px;
    padding:4px 10px; border-radius:100px; font-size:0.7rem; font-weight:700;
}
.badge-active   { background:#dcfce7; color:#16a34a; }
.badge-inactive { background:#fef2f2; color:#dc2626; }

/* Card body */
.card-body-area { padding:14px 16px; }
.card-title     { font-size:0.95rem; font-weight:700; color:#0f172a; margin:0 0 4px 0; }
.card-desc      { font-size:0.8rem; color:#64748b; margin:0 0 12px 0; }

/* Aksi tombol di card */
.card-actions   { display:flex; gap:8px; }
.btn-icon-edit, .btn-icon-delete {
    flex:1; border:none; border-radius:8px; padding:7px; cursor:pointer;
    font-size:0.75rem; font-weight:600; transition:all 0.2s; display:flex; align-items:center; justify-content:center; gap:4px;
}
.btn-icon-edit   { background:#eff6ff; color:#2563eb; }
.btn-icon-edit:hover   { background:#2563eb; color:#fff; transform:translateY(-1px); }
.btn-icon-delete { background:#fef2f2; color:#dc2626; }
.btn-icon-delete:hover { background:#dc2626; color:#fff; transform:translateY(-1px); }
```

---

## 🚨 Komponen: Alert / Notifikasi

Alert dirender otomatis dari Django `messages` framework. Tampilnya sebagai **overlay modal** di tengah layar:

```css
/* Overlay blur */
.modern-alert-overlay {
    position:fixed; top:0; left:0; width:100%; height:100%;
    background:rgba(15,23,42,0.6); backdrop-filter:blur(6px);
    z-index:999999; display:flex; align-items:center; justify-content:center;
    opacity:0; visibility:hidden; transition:all 0.3s ease;
}
.modern-alert-overlay.show { opacity:1; visibility:visible; }

/* Kartu alert */
.modern-alert-card {
    background:#ffffff; width:90%; max-width:360px; border-radius:24px;
    padding:36px 24px 24px 24px; text-align:center;
    box-shadow:0 25px 50px -12px rgba(0,0,0,0.25);
    transform:scale(0.8) translateY(30px);
    transition:all 0.4s cubic-bezier(0.175,0.885,0.32,1.275);
}
.modern-alert-overlay.show .modern-alert-card { transform:scale(1) translateY(0); }

/* Lingkaran ikon dengan pulse */
.alert-icon-ring {
    width:76px; height:76px; border-radius:50%; margin:0 auto 24px;
    display:flex; align-items:center; justify-content:center; position:relative;
}
.alert-icon-ring::before {
    content:''; position:absolute; inset:-8px; border-radius:50%;
    opacity:0.2; animation:pulseRing 2s infinite;
}
.alert-success .alert-icon-ring { background:#ecfdf5; color:#10b981; }
.alert-error   .alert-icon-ring { background:#fef2f2; color:#ef4444;  }

@keyframes pulseRing { 0%{ transform:scale(0.8); opacity:0.5; } 100%{ transform:scale(1.3); opacity:0; } }

/* Tombol aksi */
.alert-success .alert-action-btn { background:#10b981; color:white; box-shadow:0 4px 15px rgba(16,185,129,0.3); }
.alert-error   .alert-action-btn { background:#ef4444; color:white; box-shadow:0 4px 15px rgba(239,68,68,0.3); }
```

**Fitur tambahan:** Alert sukses/error memainkan **audio notifikasi** dari CDN Mixkit secara otomatis.

---

## 🪟 Komponen: Modal (uni_modal & confirm_modal)

Dua modal global yang harus ada di setiap halaman (didefinisikan di `base.html`):

```html
<!-- Modal untuk form CRUD -->
<div class="modal fade" id="uni_modal" role="dialog">
    <div class="modal-dialog modal-md modal-dialog-centered">
        <div class="modal-content rounded-0">
            <div class="modal-header">
                <h5 class="modal-title"></h5>
            </div>
            <div class="modal-body"></div>
            <div class="modal-footer">
                <button class="btn btn-sm btn-primary rounded-0" id="submit"
                        onclick="$('#uni_modal form').submit()">Save</button>
                <button class="btn btn-sm btn-secondary rounded-0"
                        data-bs-dismiss="modal">Cancel</button>
            </div>
        </div>
    </div>
</div>

<!-- Modal konfirmasi (hapus dll) -->
<div class="modal fade" id="confirm_modal" role="dialog">
    <div class="modal-dialog modal-md modal-dialog-centered">
        <div class="modal-content rounded-0">
            <div class="modal-header">
                <h5 class="modal-title">Confirmation</h5>
            </div>
            <div class="modal-body">
                <div id="delete_content"></div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-sm btn-primary rounded-0" id="confirm">Continue</button>
                <button class="btn btn-sm btn-secondary rounded-0"
                        data-bs-dismiss="modal">Close</button>
            </div>
        </div>
    </div>
</div>
```

**Helper functions global (wajib ada di setiap halaman):**

```js
window.start_loader = () => $('body').removeClass('loaded');
window.end_loader   = () => $('body').addClass('loaded');

// Buka modal dengan konten AJAX
window.uni_modal = function(title, url, size = '') {
    start_loader();
    $.ajax({ url, success: resp => {
        if (resp) {
            $('#uni_modal .modal-title').html(title);
            $('#uni_modal .modal-body').html(resp);
            const dialogClass = size ? `modal-dialog ${size} modal-dialog-centered` : 'modal-dialog modal-md modal-dialog-centered';
            $('#uni_modal .modal-dialog').attr('class', dialogClass);
            $('#uni_modal').modal({ backdrop:'static', keyboard:false, focus:true });
            $('#uni_modal').modal('show');
            end_loader();
        }
    }});
};

// Buka konfirmasi
window._conf = function(msg, funcName, params = []) {
    $('#confirm_modal #confirm').attr('onclick', funcName + '(' + params.join(',') + ')');
    $('#confirm_modal .modal-body').html(msg);
    $('#confirm_modal').modal('show');
};
```

---

## 🔁 Animasi Global

| Nama | Deskripsi |
|------|-----------|
| `imageZoomIn` | Zoom masuk lambat (1.08 → 1) saat halaman load — dipakai di hero login |
| `formSlideUp` | Fade + slide dari bawah ke atas — dipakai di form login |
| `slideUpFade` | Muncul dari bawah — dipakai di badge glass |
| `logoPulse` | Denyutan border logo sidebar setiap 4 detik |
| `ringRotate` / `ringRotate2` | Rotasi ring mengelilingi logo sidebar |
| `nameBreathe` | Letter-spacing brand name bernapas |
| `subBlink` | Opacity subtitle sidebar berkedip |
| `scanMove` / `scanMove2` | Garis scanline bergerak horizontal di sidebar |
| `glowDot` | Titik glow berjalan sepanjang divider sidebar |
| `pulseRing` | Ring pulse di sekitar ikon alert |
| `pulseRing` | Scale 0.8→1.3 kemudian fade out |

---

## 🖥️ Body Background (Halaman Dalam)

```css
body {
    background-color: #f8fafc;
    background-image:
        radial-gradient(at 0% 0%,   rgba(139,92,246,0.12)  0px, transparent 50%),
        radial-gradient(at 100% 0%,  rgba(14,165,233,0.12)  0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(236,72,153,0.12) 0px, transparent 50%),
        radial-gradient(at 0% 100%,  rgba(245,158,11,0.12)  0px, transparent 50%);
    background-attachment: fixed;
}
```

Ini menciptakan efek **radial gradient sudut** (4 warna berbeda di 4 pojok layar) yang subtil tapi terasa premium.

---

## 📱 Responsif

| Breakpoint | Aturan |
|------------|--------|
| `max-width: 992px` | Sisi hero login tersembunyi, form full width |
| `max-width: 1100px` | Dashboard: main grid jadi 1 kolom |
| `max-width: 720px` | Stats grid: 4 → 2 kolom |
| `max-width: 480px` | Stats grid: 2 → 1 kolom |

---

## ⚙️ Konvensi AJAX Response

```js
// Pola standar response JSON:
{ "status": "success" }  // atau
{ "status": "failed", "msg": "pesan error" }

// Semua request AJAX POST wajib sertakan CSRF token:
headers: { "X-CSRFToken": "{{ csrf_token }}" }
```

---

## 📁 Struktur Folder Static (Replikasi)

```
static/
└── [appName]/
    ├── favicon.svg
    ├── assets/
    │   ├── bootstrap/
    │   │   ├── css/bootstrap.min.css
    │   │   └── js/(bootstrap.min.js, bootstrap.bundle.min.js, popper.min.js)
    │   ├── material-admin/
    │   │   ├── vendors/mdi/css/materialdesignicons.min.css
    │   │   ├── vendors/css/vendor.bundle.base.css
    │   │   ├── vendors/js/vendor.bundle.base.js
    │   │   ├── css/demo/style.css
    │   │   └── js/(preloader.js, material.js, misc.js)
    │   ├── select2/
    │   │   └── dist/(css/select2.min.css, js/select2.full.js)
    │   └── default/
    │       ├── css/style.css   ← Override kustom
    │       └── js/jquery-3.6.0.min.js
```

---

## ✅ Checklist Implementasi di Project Baru

- [ ] Salin seluruh folder `assets/` ke project baru
- [ ] Buat `base.html` dengan struktur layout & dua modal global
- [ ] Buat `navigation.html` (sidebar dark dengan particle + fitur logo upload)
- [ ] Buat `topNavigation.html` (header + hamburger + dropdown profil)
- [ ] Buat `login.html` (split layout 2 kolom)
- [ ] Implementasi helper JS: `start_loader`, `end_loader`, `uni_modal`, `_conf`, `toggleSidebar`
- [ ] Definisikan CSS variables di setiap halaman (atau di file global)
- [ ] Terapkan body background radial-gradient sudut
- [ ] Implementasikan sistem alert Django messages dengan overlay animasi
- [ ] Gunakan Google Font `Inter` di semua halaman dalam (dan sidebar pakai `Georgia` untuk brand)
