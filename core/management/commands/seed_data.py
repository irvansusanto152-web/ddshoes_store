from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile, Brands, Categories, Suppliers, Products, StockIns, StockInDetails
from datetime import date


class Command(BaseCommand):
    help = 'Seed initial data: brands, categories, suppliers, and demo users'

    def handle(self, *args, **kwargs):
        # --- BRANDS ---
        brands = [f'Brand {i}' for i in range(1, 101)]
        for name in brands:
            obj, created = Brands.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Brand created: {name}'))

        # --- CATEGORIES ---
        categories = [
            'Sneakers', 'Running', 'Casual', 'Sandal', 'Boots',
            'Formal', 'Olahraga', 'Anak-anak', 'Slip On', 'High Heels'
        ]
        for name in categories:
            obj, created = Categories.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Category created: {name}'))

        # --- SUPPLIERS ---
        suppliers_data = [
            {'name': 'Supplier Utama', 'phone': '08111000001', 'notes': 'Supplier utama untuk semua merek'},
            {'name': 'Distributor Sepatu Bandung', 'phone': '08111000002', 'notes': 'Khusus merek lokal'},
            {'name': 'Agen Nike Resmi', 'phone': '08111000003', 'notes': 'Distributor resmi Nike'},
        ]
        for s in suppliers_data:
            obj, created = Suppliers.objects.get_or_create(
                name=s['name'],
                defaults={'phone': s['phone'], 'notes': s['notes']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Supplier created: {s["name"]}'))

        # --- ADMIN USER ---
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                password='admin123',
                email='admin@ddshoes.com'
            )
            UserProfile.objects.create(user=admin_user, role='admin')
            self.stdout.write(self.style.SUCCESS('  Admin user created (admin / admin123)'))
        else:
            self.stdout.write(self.style.WARNING('  Admin user already exists, skipping.'))
            # Ensure UserProfile exists
            if not hasattr(User.objects.get(username='admin'), 'userprofile'):
                UserProfile.objects.create(user=User.objects.get(username='admin'), role='admin')

        # --- DEMO KASIR ---
        if not User.objects.filter(username='kasir01').exists():
            kasir = User.objects.create_user(username='kasir01', password='kasir123')
            UserProfile.objects.create(user=kasir, role='kasir', phone='08199900001')
            self.stdout.write(self.style.SUCCESS('  Kasir demo created (kasir01 / kasir123)'))
        else:
            self.stdout.write(self.style.WARNING('  kasir01 already exists, skipping.'))

        # --- PRODUCTS ---
        products_data = []
        for i in range(1, 101):
            products_data.append({
                'product_code': f'BR-{i:03d}',
                'name': f'Sepatu Brand {i} Model A',
                'brand_name': f'Brand {i}',
                'category_name': 'Sneakers',
                'size': '42',
                'condition': 'Baru',
                'buy_price': 500000,
                'sell_price': 750000,
                'stock': 0,
            })

        for p_data in products_data:
            brand = Brands.objects.get(name=p_data['brand_name'])
            category = Categories.objects.get(name=p_data['category_name'])
            obj, created = Products.objects.get_or_create(
                product_code=p_data['product_code'],
                defaults={
                    'name': p_data['name'],
                    'brand': brand,
                    'category': category,
                    'size': p_data['size'],
                    'condition': p_data['condition'],
                    'buy_price': p_data['buy_price'],
                    'sell_price': p_data['sell_price'],
                    'stock': p_data['stock'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Product created: {obj.name}'))

        # --- STOCK INS (BARANG MASUK) ---
        admin_user_obj = User.objects.get(username='admin')
        supplier_obj = Suppliers.objects.get(name='Supplier Utama')

        if not StockIns.objects.filter(notes='Seed Stock 100 Brands').exists():
            stock_in = StockIns.objects.create(
                supplier=supplier_obj,
                received_by=admin_user_obj,
                received_date=date.today(),
                notes='Seed Stock 100 Brands'
            )
            
            for p_data in products_data:
                prod = Products.objects.get(product_code=p_data['product_code'])
                qty = 1
                StockInDetails.objects.create(
                    stock_in=stock_in,
                    product=prod,
                    quantity=qty,
                    buy_price=prod.buy_price
                )
                prod.stock += qty
                prod.save()
            
            self.stdout.write(self.style.SUCCESS('  Stock In created with initial quantities (1 each).'))
        else:
            self.stdout.write(self.style.WARNING('  Stock In already exists, skipping.'))

        self.stdout.write(self.style.SUCCESS('\n✅ Seed data completed successfully!'))
        self.stdout.write('  Default accounts:')
        self.stdout.write('    Admin  → username: admin    | password: admin123')
        self.stdout.write('    Kasir  → username: kasir01  | password: kasir123')
