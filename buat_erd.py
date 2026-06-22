"""
Script untuk membuat ERD DD Shoes POS System
Menggunakan matplotlib - output PNG resolusi tinggi siap Word
"""

import matplotlib
matplotlib.use('Agg')  # non-GUI backend, tidak butuh Tkinter
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import matplotlib.patheffects as pe

# ============================================================
# DEFINISI TABEL: (nama_tabel, [(kolom, keterangan), ...])
# ============================================================
TABLES = {
    'tb_user': [
        ('user_id', 'INT  PK'),
        ('username', 'VARCHAR(150)'),
        ('password', 'VARCHAR(128)'),
        ('is_active', 'BOOLEAN'),
        ('last_login', 'DATETIME'),
        ('date_joined', 'DATETIME'),
    ],
    'tb_userprofile': [
        ('profile_id', 'INT  PK'),
        ('user_id', 'INT  FK'),
        ('role', 'VARCHAR(20)'),
        ('phone', 'VARCHAR(20)'),
    ],
    'tb_kategori': [
        ('category_id', 'INT  PK'),
        ('category_name', 'VARCHAR(100)'),
    ],
    'tb_merek': [
        ('brand_id', 'INT  PK'),
        ('brand_name', 'VARCHAR(100)'),
    ],
    'tb_pemasok': [
        ('supplier_id', 'INT  PK'),
        ('supplier_name', 'VARCHAR(100)'),
        ('supplier_phone', 'VARCHAR(20)'),
        ('supplier_notes', 'TEXT'),
    ],
    'tb_produk': [
        ('product_id', 'INT  PK'),
        ('category_id', 'INT  FK'),
        ('brand_id', 'INT  FK'),
        ('product_name', 'VARCHAR(255)'),
        ('size', 'VARCHAR(50)'),
        ('condition', 'VARCHAR(50)'),
        ('buy_price', 'INTEGER'),
        ('sell_price', 'INTEGER'),
        ('stock', 'INTEGER'),
        ('product_status', 'VARCHAR(20)'),
        ('product_created_at', 'DATETIME'),
    ],
    'tb_barangmasuk': [
        ('stockin_id', 'INT  PK'),
        ('supplier_id', 'INT  FK'),
        ('received_by', 'INT  FK'),
        ('received_date', 'DATE'),
        ('stockin_notes', 'TEXT'),
        ('stockin_created_at', 'DATETIME'),
    ],
    'tb_detailbarangmasuk': [
        ('stockin_detail_id', 'INT  PK'),
        ('stockin_id', 'INT  FK'),
        ('product_id', 'INT  FK'),
        ('stockin_qty', 'INTEGER'),
        ('stockin_buy_price', 'INTEGER'),
    ],
    'tb_transaksi': [
        ('transaction_id', 'INT  PK'),
        ('cashier_id', 'INT  FK'),
        ('subtotal_amount', 'INTEGER'),
        ('discount_amount', 'INTEGER'),
        ('total_amount', 'INTEGER'),
        ('payment_method', 'VARCHAR(20)'),
        ('cash_received', 'INTEGER'),
        ('change_amount', 'INTEGER'),
        ('transaction_date', 'DATETIME'),
        ('transaction_status', 'VARCHAR(20)'),
        ('voided_by', 'INT  FK'),
        ('void_reason', 'TEXT'),
        ('voided_at', 'DATETIME'),
    ],
    'tb_detailtransaksi': [
        ('trx_detail_id', 'INT  PK'),
        ('transaction_id', 'INT  FK'),
        ('product_id', 'INT  FK'),
        ('trx_quantity', 'INTEGER'),
        ('trx_sell_price', 'INTEGER'),
        ('trx_subtotal', 'INTEGER'),
    ],
    'tb_closing': [
        ('closing_id', 'INT  PK'),
        ('cashier_id', 'INT  FK'),
        ('closing_date', 'DATE'),
        ('system_cash_total', 'INTEGER'),
        ('system_transfer_total', 'INTEGER'),
        ('system_qris_total', 'INTEGER'),
        ('actual_cash', 'INTEGER'),
        ('cash_difference', 'INTEGER'),
        ('is_locked', 'BOOLEAN'),
        ('submitted_at', 'DATETIME'),
        ('unlocked_by', 'INT  FK'),
        ('unlock_count', 'INTEGER'),
    ],
    'tb_penyesuaianstok': [
        ('adjustment_id', 'INT  PK'),
        ('product_id', 'INT  FK'),
        ('adjusted_by', 'INT  FK'),
        ('adj_quantity', 'INTEGER'),
        ('adj_reason', 'VARCHAR(20)'),
        ('adj_notes', 'TEXT'),
        ('adjusted_at', 'DATETIME'),
    ],
}

# ============================================================
# POSISI TABEL (x, y) — layout alur bisnis kiri ke kanan
# Format: center x, top y
# ============================================================
POSITIONS = {
    # Kolom 1 — Master user
    'tb_user':              (1.0,  19.0),
    'tb_userprofile':       (1.0,  13.5),

    # Kolom 2 — Master produk
    'tb_kategori':          (5.5,  21.0),
    'tb_merek':             (5.5,  18.0),
    'tb_pemasok':           (5.5,  14.5),

    # Kolom 3 — Produk (sentral)
    'tb_produk':            (10.5, 19.5),

    # Kolom 4 — Barang masuk
    'tb_barangmasuk':       (15.5, 21.0),
    'tb_detailbarangmasuk': (15.5, 16.5),

    # Kolom 5 — Transaksi
    'tb_transaksi':         (20.5, 21.0),
    'tb_detailtransaksi':   (20.5, 15.5),

    # Bawah — Closing & Penyesuaian
    'tb_closing':           (15.5, 10.5),
    'tb_penyesuaianstok':   (20.5, 9.5),
}

# ============================================================
# RELASI: (tabel_asal, tabel_tujuan, label)
# ============================================================
RELATIONS = [
    ('tb_user',             'tb_userprofile',       '1 : 1'),
    ('tb_kategori',         'tb_produk',            '1 : N'),
    ('tb_merek',            'tb_produk',            '1 : N'),
    ('tb_pemasok',          'tb_barangmasuk',       '1 : N'),
    ('tb_user',             'tb_barangmasuk',       '1 : N'),
    ('tb_barangmasuk',      'tb_detailbarangmasuk', '1 : N'),
    ('tb_produk',           'tb_detailbarangmasuk', '1 : N'),
    ('tb_user',             'tb_transaksi',         '1 : N'),
    ('tb_transaksi',        'tb_detailtransaksi',   '1 : N'),
    ('tb_produk',           'tb_detailtransaksi',   '1 : N'),
    ('tb_user',             'tb_closing',           '1 : N'),
    ('tb_produk',           'tb_penyesuaianstok',   '1 : N'),
    ('tb_user',             'tb_penyesuaianstok',   '1 : N'),
]

# ============================================================
# UKURAN & WARNA
# ============================================================
TABLE_W      = 3.8    # lebar tabel
ROW_H        = 0.38   # tinggi per baris
HEADER_H     = 0.48   # tinggi header
HEADER_COLOR = '#1e3a5f'   # biru tua
PK_COLOR     = '#fff3cd'   # kuning muda untuk PK
FK_COLOR     = '#e8f4f8'   # biru muda untuk FK
ROW_COLOR    = '#ffffff'
ROW_ALT      = '#f7f9fc'
BORDER_COLOR = '#2c5f8a'
TEXT_COLOR   = '#1a1a2e'
REL_COLOR    = '#c0392b'

# ============================================================
# FUNGSI GAMBAR TABEL
# ============================================================
def get_table_height(table_name):
    return HEADER_H + len(TABLES[table_name]) * ROW_H

def draw_table(ax, name, pos_x, pos_y):
    cols = TABLES[name]
    n    = len(cols)
    w    = TABLE_W
    hh   = HEADER_H
    rh   = ROW_H
    total_h = hh + n * rh

    x = pos_x - w / 2
    y = pos_y - total_h

    # Shadow
    shadow = mpatches.FancyBboxPatch(
        (x + 0.06, y - 0.06), w, total_h,
        boxstyle='round,pad=0.05',
        linewidth=0, facecolor='#b0b0b0', alpha=0.35, zorder=1
    )
    ax.add_patch(shadow)

    # Header background
    header_rect = mpatches.FancyBboxPatch(
        (x, pos_y - hh), w, hh,
        boxstyle='round,pad=0.0',
        linewidth=1.2, edgecolor=BORDER_COLOR,
        facecolor=HEADER_COLOR, zorder=2
    )
    ax.add_patch(header_rect)

    # Header text
    ax.text(pos_x, pos_y - hh / 2, name,
            ha='center', va='center',
            fontsize=7.5, fontweight='bold',
            color='white', zorder=3,
            fontfamily='monospace')

    # Body border
    body_rect = mpatches.Rectangle(
        (x, y), w, n * rh,
        linewidth=1.2, edgecolor=BORDER_COLOR,
        facecolor='none', zorder=2
    )
    ax.add_patch(body_rect)

    # Rows
    for i, (col_name, col_type) in enumerate(cols):
        row_y   = pos_y - hh - (i + 1) * rh
        is_pk   = 'PK' in col_type
        is_fk   = 'FK' in col_type
        bg      = PK_COLOR if is_pk else (FK_COLOR if is_fk else (ROW_ALT if i % 2 == 0 else ROW_COLOR))

        row_rect = mpatches.Rectangle(
            (x, row_y), w, rh,
            linewidth=0.5, edgecolor='#d0d8e4',
            facecolor=bg, zorder=2
        )
        ax.add_patch(row_rect)

        # Separator line
        ax.plot([x, x + w], [row_y + rh, row_y + rh],
                color='#d0d8e4', linewidth=0.4, zorder=3)

        # PK/FK icon
        icon = ''
        if is_pk:
            icon = '[PK] '
        elif is_fk:
            icon = '[FK] '

        # Column name
        col_display = col_name.replace('_', '_')
        fw = 'bold' if is_pk else 'normal'
        ax.text(x + 0.12, row_y + rh / 2,
                icon + col_display,
                ha='left', va='center',
                fontsize=6.2, color=TEXT_COLOR,
                fontweight=fw, zorder=3)

        # Type
        type_clean = col_type.replace('  PK', '').replace('  FK', '').strip()
        ax.text(x + w - 0.1, row_y + rh / 2,
                type_clean,
                ha='right', va='center',
                fontsize=5.8, color='#5a6a7a',
                style='italic', zorder=3)

    # Divider line header-body
    ax.plot([x, x + w], [pos_y - hh, pos_y - hh],
            color=BORDER_COLOR, linewidth=1.2, zorder=4)

    # Return anchor points (center kiri, kanan, atas, bawah)
    cx = pos_x
    cy = pos_y - total_h / 2
    return {
        'left':   (x,       cy),
        'right':  (x + w,   cy),
        'top':    (cx,       pos_y),
        'bottom': (cx,       y),
        'x': x, 'y': y, 'w': w, 'h': total_h,
        'center': (cx, cy)
    }

# ============================================================
# FUNGSI GAMBAR RELASI
# ============================================================
def draw_relation(ax, p1, p2, label=''):
    x1, y1 = p1
    x2, y2 = p2
    mx = (x1 + x2) / 2
    my = (y1 + y2) / 2

    ax.annotate('',
        xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle='-|>',
            color=REL_COLOR,
            lw=1.2,
            connectionstyle='arc3,rad=0.05',
        ),
        zorder=1
    )

    if label:
        ax.text(mx, my + 0.12, label,
                ha='center', va='bottom',
                fontsize=5.5, color=REL_COLOR,
                fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.15',
                          facecolor='white',
                          edgecolor=REL_COLOR,
                          alpha=0.85,
                          linewidth=0.6),
                zorder=5)

# ============================================================
# MAIN — GAMBAR ERD
# ============================================================
fig, ax = plt.subplots(figsize=(26, 24), dpi=150)
ax.set_xlim(-0.5, 25)
ax.set_ylim(-0.5, 23.5)
ax.axis('off')
fig.patch.set_facecolor('#f0f4f8')
ax.set_facecolor('#f0f4f8')

# Grid background ringan
for gx in range(0, 26, 1):
    ax.axvline(gx, color='#dde3ea', linewidth=0.3, alpha=0.5)
for gy in range(0, 24, 1):
    ax.axhline(gy, color='#dde3ea', linewidth=0.3, alpha=0.5)

# Judul
ax.text(12.5, 23.1,
        'Entity Relationship Diagram — DD Shoes POS System',
        ha='center', va='center',
        fontsize=13, fontweight='bold',
        color='white',
        bbox=dict(boxstyle='round,pad=0.4',
                  facecolor='#1e3a5f',
                  edgecolor='#1e3a5f',
                  alpha=1.0))

# Gambar semua tabel dan simpan anchor
anchors = {}
for tname, (px, py) in POSITIONS.items():
    anchors[tname] = draw_table(ax, tname, px, py)

# ============================================================
# GAMBAR RELASI — pilih sisi anchor yang paling dekat
# ============================================================
def best_anchor(a1, a2):
    """Pilih sisi anchor kiri/kanan/atas/bawah yang paling pendek"""
    sides1 = ['left', 'right', 'top', 'bottom']
    sides2 = ['left', 'right', 'top', 'bottom']
    best_d = float('inf')
    bp1 = a1['right']
    bp2 = a2['left']
    for s1 in sides1:
        for s2 in sides2:
            x1, y1 = a1[s1]
            x2, y2 = a2[s2]
            d = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
            if d < best_d:
                best_d = d
                bp1 = a1[s1]
                bp2 = a2[s2]
    return bp1, bp2

for (t1, t2, label) in RELATIONS:
    p1, p2 = best_anchor(anchors[t1], anchors[t2])
    draw_relation(ax, p1, p2, label)

# Legend
legend_items = [
    mpatches.Patch(facecolor=HEADER_COLOR, edgecolor=BORDER_COLOR, label='Nama Tabel'),
    mpatches.Patch(facecolor=PK_COLOR,     edgecolor='#aaa',        label='Primary Key (PK)'),
    mpatches.Patch(facecolor=FK_COLOR,     edgecolor='#aaa',        label='Foreign Key (FK)'),
    mpatches.Patch(facecolor=ROW_COLOR,    edgecolor='#aaa',        label='Atribut Biasa'),
]
ax.legend(handles=legend_items,
          loc='lower left',
          fontsize=7,
          framealpha=0.95,
          edgecolor='#aaa',
          title='Keterangan',
          title_fontsize=7.5)

plt.tight_layout(pad=0.5)
output_path = r'c:\Users\IRVAN SUSANTO\pos_ddshoes2\pos_ddshoes\docs\ERD_DDShoes_POS.png'
plt.savefig(output_path, dpi=180, bbox_inches='tight',
            facecolor=fig.get_facecolor())
plt.close()
print(f'ERD berhasil dibuat: {output_path}')
