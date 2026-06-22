import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_ddshoes.settings')
django.setup()

from core.models import Products, Categories

with open('output_check.txt', 'w') as f:
    for cat in Categories.objects.all():
        prods = Products.objects.filter(category=cat)
        f.write(f"Category: {cat.name} (ID: {cat.id})\n")
        f.write(f"Total Products count(): {prods.count()}\n")
        f.write("Products:\n")
        for p in prods:
            f.write(f" - ID: {p.id}, Name: {p.name}, Status: {p.status}, Stock: {p.stock}\n")
        f.write("-" * 40 + "\n")
