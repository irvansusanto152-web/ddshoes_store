import sqlite3
conn = sqlite3.connect(r'c:\Users\IRVAN SUSANTO\pos_ddshoes2\db.sqlite3')
cur = conn.cursor()
cur.execute("""
SELECT p.name, p.stock, p.status 
FROM core_products p 
JOIN core_categories c ON p.category_id = c.id 
WHERE c.name LIKE '%Sport%'
""")
for row in cur.fetchall():
    print(f"- {row[0]} (Stok: {row[1]}, Status: {row[2]})")
conn.close()
