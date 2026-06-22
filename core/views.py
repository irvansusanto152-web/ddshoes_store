import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from .models import Products, Transactions, TransactionDetails, Brands, Categories, Suppliers, StockIns, StockInDetails, CashClosings, UserProfile, StockAdjustments
from django.contrib.auth.models import User


def get_brand_initial(brand_name):
    """Ambil inisial merek dari nama merek.
    - 1 kata: ambil 2 huruf pertama (Nike → NK, Vans → VA)
    - 2+ kata: ambil huruf pertama tiap kata (New Balance → NB, New Era → NE)
    """
    if not brand_name:
        return 'XX'
    words = brand_name.strip().upper().split()
    if len(words) == 1:
        # 1 kata: ambil 2 huruf pertama
        word = ''.join(c for c in words[0] if c.isalpha())
        return word[:2] if len(word) >= 2 else word.ljust(2, 'X')
    else:
        # 2+ kata: ambil huruf pertama tiap kata (max 4 karakter)
        initials = ''.join(w[0] for w in words if w and w[0].isalpha())
        return initials[:4] if initials else 'XX'


def generate_product_code(brand_name, size):
    """Generate kode produk format [Inisial Merek]-[Ukuran]-[Nomor Urut].
    Contoh: NB-40-001, NK-42-003, AD-38-001
    Dijamin unik karena nomor urut dihitung dari yang sudah ada + unique=True di DB.
    """
    # Bersihkan ukuran — ambil angka saja untuk konsistensi
    import re
    size_clean = re.sub(r'[^0-9a-zA-Z]', '', str(size)).upper() if size else 'XX'

    brand_init = get_brand_initial(brand_name)
    prefix = f'{brand_init}-{size_clean}'

    # Hitung berapa produk dengan prefix yang sama sudah ada
    existing_count = Products.objects.filter(
        product_code__startswith=f'{prefix}-'
    ).count()
    new_num = existing_count + 1

    candidate = f'{prefix}-{new_num:03d}'

    # Double-check: pastikan kode belum dipakai (handle race condition)
    while Products.objects.filter(product_code=candidate).exists():
        new_num += 1
        candidate = f'{prefix}-{new_num:03d}'

    return candidate

def login_view(request):
    if request.user.is_authenticated:
        try:
            role = request.user.userprofile.role
        except Exception:
            role = 'admin'
        if role == 'kasir':
            return redirect('pos_page')
        return redirect('dashboard')
        
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            try:
                role = user.userprofile.role
            except Exception:
                # UserProfile belum ada — buat otomatis sebagai admin
                from core.models import UserProfile
                UserProfile.objects.get_or_create(user=user, defaults={'role': 'admin'})
                role = 'admin'
            if role == 'kasir':
                return redirect('pos_page')
            return redirect('dashboard')
        else:
            messages.error(request, "Username atau password salah.")
            
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    # Cek role
    if request.user.userprofile.role != 'admin':
        return redirect('pos_page')

    now = timezone.localtime(timezone.now())
    today = now.date()

    # 1. Total Jenis Sepatu (Count of varieties that are currently active and in stock)
    total_stock = Products.objects.filter(status='active', stock__gt=0).count()

    # 2. Total Products Sold Today
    sold_today_dict = TransactionDetails.objects.filter(transaction__transaction_date__date=today, transaction__status='success').aggregate(total_sold=Sum('quantity'))
    total_sold_today = sold_today_dict['total_sold'] or 0

    # 3. Revenue Today
    revenue_today_dict = Transactions.objects.filter(transaction_date__date=today, status='success').aggregate(total_rev=Sum('total_amount'))
    revenue_today = revenue_today_dict['total_rev'] or 0

    # 4. Barang Masuk Hari Ini
    # Menghitung jumlah catatan penerimaan (bukan total kuantitas)
    total_barang_masuk = StockIns.objects.filter(received_date=today).count()

    # Top 5 best selling brands
    top_brands = Brands.objects.annotate(
        total_sold=Sum('products__transactiondetails__quantity')
    ).filter(total_sold__gt=0).order_by('-total_sold')[:5]

    # Dead Stock: 5 produk yang belum terjual dengan umur terlama
    dead_stock = Products.objects.filter(stock__gt=0).order_by('created_at')[:5]

    context = {
        'total_stock': total_stock,
        'total_sold_today': total_sold_today,
        'revenue_today': revenue_today,
        'total_barang_masuk': total_barang_masuk,
        'top_brands': top_brands,
        'dead_stock': dead_stock,
    }

    return render(request, 'dashboard.html', context)

@login_required
def dashboard_chart_data(request):
    period = request.GET.get('period', 'daily')
    now = timezone.localtime(timezone.now())
    labels = []
    data = []

    total_sold = 0
    total_revenue = 0
    total_stockin = 0
    start_date_str = ""
    end_date_str = ""

    if period == 'daily':
        # Per jam hari ini
        today = now.date()
        start_date_str = today.strftime('%Y-%m-%d')
        end_date_str = start_date_str
        
        # Calculate totals for today
        total_revenue = Transactions.objects.filter(transaction_date__date=today, status='success').aggregate(t=Sum('total_amount'))['t'] or 0
        total_sold = TransactionDetails.objects.filter(transaction__transaction_date__date=today, transaction__status='success').aggregate(t=Sum('quantity'))['t'] or 0
        total_stockin = StockIns.objects.filter(received_date=today).count()

        from datetime import datetime as dt
        for i in range(0, 24): # jam 00:00 sampai 23:00
            # Buat waktu lokal (Asia/Jakarta) lalu konversi ke timezone-aware
            start_local = timezone.make_aware(dt(today.year, today.month, today.day, i, 0, 0))
            end_local   = start_local + timedelta(hours=1)
            labels.append(f"{i:02d}:00")
            rev = Transactions.objects.filter(
                transaction_date__gte=start_local,
                transaction_date__lt=end_local,
                status='success'
            ).aggregate(t=Sum('total_amount'))['t'] or 0
            data.append(rev)
            
    elif period == 'weekly':
        # 7 hari terakhir
        start_date = (now - timedelta(days=6)).date()
        end_date = now.date()
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        # Calculate totals for the week
        total_revenue = Transactions.objects.filter(transaction_date__date__gte=start_date, transaction_date__date__lte=end_date, status='success').aggregate(t=Sum('total_amount'))['t'] or 0
        total_sold = TransactionDetails.objects.filter(transaction__transaction_date__date__gte=start_date, transaction__transaction_date__date__lte=end_date, transaction__status='success').aggregate(t=Sum('quantity'))['t'] or 0
        total_stockin = StockIns.objects.filter(received_date__gte=start_date, received_date__lte=end_date).count()

        for i in range(6, -1, -1):
            date = (now - timedelta(days=i)).date()
            labels.append(date.strftime('%b %d'))
            rev = Transactions.objects.filter(transaction_date__date=date, status='success').aggregate(t=Sum('total_amount'))['t'] or 0
            data.append(rev)
            
    elif period == 'monthly':
        # 30 hari terakhir
        start_date = (now - timedelta(days=29)).date()
        end_date = now.date()
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        # Calculate totals for the month
        total_revenue = Transactions.objects.filter(transaction_date__date__gte=start_date, transaction_date__date__lte=end_date, status='success').aggregate(t=Sum('total_amount'))['t'] or 0
        total_sold = TransactionDetails.objects.filter(transaction__transaction_date__date__gte=start_date, transaction__transaction_date__date__lte=end_date, transaction__status='success').aggregate(t=Sum('quantity'))['t'] or 0
        total_stockin = StockIns.objects.filter(received_date__gte=start_date, received_date__lte=end_date).count()

        for i in range(29, -1, -1):
            date = (now - timedelta(days=i)).date()
            labels.append(date.strftime('%d %b'))
            rev = Transactions.objects.filter(transaction_date__date=date, status='success').aggregate(t=Sum('total_amount'))['t'] or 0
            data.append(rev)

    return JsonResponse({
        'labels': labels, 
        'data': data,
        'total_sold': total_sold,
        'total_revenue': total_revenue,
        'total_stockin': total_stockin,
        'start_date': start_date_str,
        'end_date': end_date_str
    })

# --- BRANDS ---
@login_required
def brands_list(request):
    if request.user.userprofile.role != 'admin':
        return redirect('dashboard')
    brands = Brands.objects.annotate(
        product_count=Count('products', distinct=True),
        active_count=Count('products', filter=Q(products__status='active', products__stock__gt=0), distinct=True)
    ).order_by('name')
    return render(request, 'brands.html', {'brands': brands})

@login_required
def brands_save(request):
    if request.method == 'POST':
        id = request.POST.get('id', '')
        name = request.POST.get('name', '')
        if id:
            brand = Brands.objects.get(id=id)
            brand.name = name
            brand.save()
            msg = "Merek berhasil diubah."
        else:
            Brands.objects.create(name=name)
            msg = "Merek berhasil ditambahkan."
        return JsonResponse({'status': 'success', 'msg': msg})
    
    id = request.GET.get('id', '')
    brand = Brands.objects.get(id=id) if id else None
    return render(request, 'brands_form.html', {'brand': brand})

@login_required
def brands_delete(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        Brands.objects.get(id=id).delete()
        return JsonResponse({'status': 'success', 'msg': 'Merek berhasil dihapus.'})

# --- CATEGORIES ---
@login_required
def categories_list(request):
    if request.user.userprofile.role != 'admin':
        return redirect('dashboard')
    categories = Categories.objects.annotate(
        product_count=Count('products', distinct=True),
        active_count=Count('products', filter=Q(products__status='active', products__stock__gt=0), distinct=True)
    ).order_by('name')
    return render(request, 'categories.html', {'categories': categories})

@login_required
def categories_save(request):
    if request.method == 'POST':
        id = request.POST.get('id', '')
        name = request.POST.get('name', '')
        if id:
            cat = Categories.objects.get(id=id)
            cat.name = name
            cat.save()
            msg = "Kategori berhasil diubah."
        else:
            Categories.objects.create(name=name)
            msg = "Kategori berhasil ditambahkan."
        return JsonResponse({'status': 'success', 'msg': msg})
    
    id = request.GET.get('id', '')
    category = Categories.objects.get(id=id) if id else None
    return render(request, 'categories_form.html', {'category': category})

@login_required
def categories_delete(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        Categories.objects.get(id=id).delete()
        return JsonResponse({'status': 'success', 'msg': 'Kategori berhasil dihapus.'})

# --- SUPPLIERS ---
@login_required
def suppliers_list(request):
    if request.user.userprofile.role != 'admin':
        return redirect('dashboard')
    suppliers = Suppliers.objects.all().order_by('name')
    return render(request, 'suppliers.html', {'suppliers': suppliers})

@login_required
def suppliers_save(request):
    if request.method == 'POST':
        id = request.POST.get('id', '')
        name = request.POST.get('name', '')
        phone = request.POST.get('phone', '')
        notes = request.POST.get('notes', '')
        if id:
            sup = Suppliers.objects.get(id=id)
            sup.name = name
            sup.phone = phone
            sup.notes = notes
            sup.save()
            msg = "Pemasok berhasil diubah."
        else:
            Suppliers.objects.create(name=name, phone=phone, notes=notes)
            msg = "Pemasok berhasil ditambahkan."
        return JsonResponse({'status': 'success', 'msg': msg})
    
    id = request.GET.get('id', '')
    supplier = Suppliers.objects.get(id=id) if id else None
    return render(request, 'suppliers_form.html', {'supplier': supplier})

@login_required
def suppliers_delete(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        Suppliers.objects.get(id=id).delete()
        return JsonResponse({'status': 'success', 'msg': 'Pemasok berhasil dihapus.'})

# --- PRODUCTS ---
@login_required
def products_list(request):
    if request.user.userprofile.role != 'admin':
        return redirect('dashboard')
    products = Products.objects.select_related('brand', 'category').order_by('-id')
    brands = Brands.objects.all().order_by('name')
    categories = Categories.objects.all().order_by('name')
    return render(request, 'products.html', {
        'products': products,
        'brands': brands,
        'categories': categories
    })

@login_required
def products_save(request):
    if request.method == 'POST':
        id = request.POST.get('id', '')
        name = request.POST.get('name', '')
        category_id = request.POST.get('category_id', '')
        brand_id = request.POST.get('brand_id', '')
        size = request.POST.get('size', '')
        condition = request.POST.get('condition', '')
        description = request.POST.get('description', '')
        buy_price = request.POST.get('buy_price', '0')
        sell_price = request.POST.get('sell_price', '0')
        stock = request.POST.get('stock', '0')
        image = request.FILES.get('image')

        cat = Categories.objects.get(id=category_id) if category_id else None
        brand = Brands.objects.get(id=brand_id) if brand_id else None

        if id:
            p = Products.objects.get(id=id)
            if p.status == 'inactive':
                return JsonResponse({'status': 'error', 'msg': 'Produk yang sudah terjual/nonaktif tidak dapat diedit.'})
            p.name = name
            p.category = cat
            p.brand = brand
            p.size = size
            p.condition = condition
            p.description = description
            p.buy_price = buy_price
            p.sell_price = sell_price
            # Stok tidak boleh diubah dari form edit produk
            if image:
                p.image = image
            p.save()
            msg = "Produk berhasil diubah."
        else:
            # Produk baru selalu mulai dari stok 0
            p = Products.objects.create(
                name=name, category=cat, brand=brand, size=size,
                condition=condition, description=description,
                buy_price=buy_price, sell_price=sell_price, stock=0,
                product_code=generate_product_code(
                    brand.name if brand else '', size
                )
            )
            if image:
                p.image = image
                p.save()
            msg = "Produk berhasil ditambahkan."
        return JsonResponse({'status': 'success', 'id': p.id, 'name': p.name, 'msg': msg})
    
    id = request.GET.get('id', '')
    product = Products.objects.get(id=id) if id else None
    categories = Categories.objects.all()
    brands = Brands.objects.all()
    conditions = Products.CONDITION_CHOICES
    
    inline = request.GET.get('inline', '0')
    context = {
        'product': product,
        'categories': categories,
        'brands': brands,
        'conditions': conditions,
        'inline': inline,
    }
    return render(request, 'products_form.html', context)

@login_required
def products_delete(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        Products.objects.get(id=id).delete()
        return JsonResponse({'status': 'success', 'msg': 'Produk berhasil dihapus.'})

@login_required
def products_toggle_status(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        p = Products.objects.get(id=id)
        if p.status == 'inactive' and p.stock == 0:
            return JsonResponse({'status': 'error', 'msg': 'Produk dengan stok 0 tidak dapat diaktifkan manual. Gunakan fitur Retur Transaksi.'})
            
        if p.status == 'active':
            p.status = 'inactive'
            msg = "Produk dinonaktifkan."
        else:
            p.status = 'active'
            msg = "Produk diaktifkan."
        p.save()
        return JsonResponse({'status': 'success', 'new_status': p.status, 'msg': msg})

# --- STOCK IN ---
@login_required
def stockin_list(request):
    if request.user.userprofile.role != 'admin':
        return redirect('dashboard')
        
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    queryset = StockIns.objects.select_related('supplier', 'received_by').annotate(total_items=Count('details'))
    
    if start_date and end_date:
        queryset = queryset.filter(received_date__gte=start_date, received_date__lte=end_date)
        
    stockins = queryset.order_by('-received_date', '-id')
    return render(request, 'stockin.html', {'stockins': stockins})

@login_required
def stockin_detail(request, pk):
    if request.user.userprofile.role != 'admin':
        return redirect('dashboard')
    stockin = StockIns.objects.get(id=pk)
    return render(request, 'stockin_detail.html', {'stockin': stockin})

@login_required
def stockin_save(request):
    if request.user.userprofile.role != 'admin':
        return redirect('dashboard')

    if request.method == 'POST':
        supplier_id   = request.POST.get('supplier_id')
        received_date = request.POST.get('received_date')
        notes         = request.POST.get('notes', '')

        # Data per-baris produk (format baru)
        product_names = request.POST.getlist('product_name[]')
        brand_ids     = request.POST.getlist('brand_id[]')
        category_ids  = request.POST.getlist('category_id[]')
        sizes         = request.POST.getlist('size[]')
        conditions_in = request.POST.getlist('condition[]')
        buy_prices    = request.POST.getlist('buy_price[]')
        sell_prices   = request.POST.getlist('sell_price[]')
        quantities    = request.POST.getlist('quantity[]')

        if not supplier_id or not received_date or not product_names:
            messages.error(request, "Data penerimaan tidak lengkap.")
            return redirect('stockin_save')

        supplier = Suppliers.objects.get(id=supplier_id)
        si = StockIns.objects.create(
            supplier=supplier,
            received_by=request.user,
            received_date=received_date,
            notes=notes
        )

        new_product_count = 0
        for i in range(len(product_names)):
            nama    = product_names[i].strip() if i < len(product_names) else ''
            bid     = brand_ids[i]     if i < len(brand_ids)     else ''
            cid     = category_ids[i]  if i < len(category_ids)  else ''
            size    = sizes[i].strip() if i < len(sizes)          else ''
            cond    = conditions_in[i] if i < len(conditions_in)  else 'Baru'
            bp_str  = buy_prices[i]    if i < len(buy_prices)     else '0'
            sp_str  = sell_prices[i]   if i < len(sell_prices)    else '0'
            qty_str = quantities[i]    if i < len(quantities)     else '0'

            if not nama:
                continue

            qty = int(qty_str) if qty_str.strip().isdigit() else 0
            bp  = int(bp_str)  if bp_str.strip().isdigit()  else 0
            sp  = int(sp_str)  if sp_str.strip().isdigit()  else 0

            if qty < 1:
                continue

            brand    = Brands.objects.get(id=bid)       if bid else None
            category = Categories.objects.get(id=cid)   if cid else None

            # Cari produk yang sudah ada berdasarkan nama + ukuran + kondisi
            product_qs = Products.objects.filter(
                name__iexact=nama,
                size__iexact=size,
                condition=cond
            )

            if product_qs.exists():
                # Produk sudah ada — update harga jika berubah
                product = product_qs.first()
                updated = False
                if bp > 0 and product.buy_price != bp:
                    product.buy_price = bp
                    updated = True
                if sp > 0 and product.sell_price != sp:
                    product.sell_price = sp
                    updated = True
                if updated:
                    product.save()
            else:
                # Produk belum ada — buat otomatis
                product = Products.objects.create(
                    name=nama,
                    brand=brand,
                    category=category,
                    size=size,
                    condition=cond,
                    buy_price=bp,
                    sell_price=sp,
                    stock=0,
                    status='active',
                    product_code=generate_product_code(
                        brand.name if brand else '', size
                    )
                )
                new_product_count += 1

            StockInDetails.objects.create(
                stock_in=si,
                product=product,
                quantity=qty,
                buy_price=bp if bp > 0 else product.buy_price
            )
            # signals.py secara otomatis menambah product.stock

        if new_product_count > 0:
            messages.success(request, f"Berhasil! {new_product_count} produk baru ditambahkan ke katalog dan stok telah diperbarui.")
        else:
            messages.success(request, "Penerimaan barang berhasil dicatat. Stok produk telah diperbarui.")

        return redirect('stockin_list')

    # GET — tampilkan form
    suppliers  = Suppliers.objects.all().order_by('name')
    brands     = Brands.objects.all().order_by('name')
    categories = Categories.objects.all().order_by('name')
    conditions = Products.CONDITION_CHOICES
    return render(request, 'stockin_form.html', {
        'suppliers':  suppliers,
        'brands':     brands,
        'categories': categories,
        'conditions': conditions,
    })

# --- USERS ---
@login_required
def users_list(request):
    if request.user.userprofile.role != 'admin':
        return redirect('dashboard')
    users = User.objects.select_related('userprofile').all().order_by('username')
    return render(request, 'users.html', {'users': users})

@login_required
def users_save(request):
    if request.user.userprofile.role != 'admin':
        return redirect('dashboard')
    if request.method == 'POST':
        id = request.POST.get('id', '')
        username = request.POST.get('username')
        role = request.POST.get('role')
        password = request.POST.get('password')
        phone = request.POST.get('phone', '')

        if id:
            u = User.objects.get(id=id)
            u.username = username
            if password:
                u.set_password(password)
            u.save()
            up = u.userprofile
            up.role = role
            up.phone = phone
            up.save()
            msg = "User berhasil diubah."
        else:
            u = User.objects.create_user(username=username, password=password)
            UserProfile.objects.create(user=u, role=role, phone=phone)
            msg = "User baru berhasil ditambahkan."
        return JsonResponse({'status': 'success', 'msg': msg})

    id = request.GET.get('id', '')
    u = User.objects.get(id=id) if id else None
    return render(request, 'users_form.html', {'user_obj': u})

@login_required
def users_toggle_status(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        u = User.objects.get(id=id)
        if u.is_active:
            u.is_active = False
            msg = "Akun dinonaktifkan."
        else:
            u.is_active = True
            msg = "Akun diaktifkan."
        u.save()
        return JsonResponse({'status': 'success', 'is_active': u.is_active, 'msg': msg})

# --- REPORTS ---
@login_required
def sales_report(request):
    if request.user.userprofile.role != 'admin':
        return redirect('dashboard')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    cashier_id = request.GET.get('cashier_id')
    payment_method = request.GET.get('payment_method')
    brand_id = request.GET.get('brand_id')

    qs = Transactions.objects.select_related('cashier').annotate(total_qty=Sum('details__quantity')).order_by('-transaction_date')

    if start_date:
        qs = qs.filter(transaction_date__date__gte=start_date)
    if end_date:
        qs = qs.filter(transaction_date__date__lte=end_date)
    if cashier_id:
        qs = qs.filter(cashier_id=cashier_id)
    if payment_method:
        qs = qs.filter(payment_method=payment_method)
    if brand_id:
        # Filter transactions that include products from this brand
        qs = qs.filter(details__product__brand_id=brand_id).distinct()

    cashiers = User.objects.filter(userprofile__role='kasir')
    qs_success = qs.filter(status='success')
    total_revenue = qs_success.aggregate(t=Sum('total_amount'))['t'] or 0
    total_discount = qs_success.aggregate(d=Sum('discount_amount'))['d'] or 0

    return render(request, 'sales_report.html', {
        'transactions': qs,
        'cashiers': cashiers,
        'start_date': start_date,
        'end_date': end_date,
        'cashier_id': cashier_id,
        'payment_method': payment_method,
        'total_revenue': total_revenue,
        'total_discount': total_discount
    })

@login_required
def inventory_report(request):
    if request.user.userprofile.role != 'admin':
        return redirect('dashboard')
    
    brand_id = request.GET.get('brand_id')
    category_id = request.GET.get('category_id')

    qs = Products.objects.select_related('brand', 'category').filter(stock__gt=0).order_by('name')
    if brand_id:
        qs = qs.filter(brand_id=brand_id)
    if category_id:
        qs = qs.filter(category_id=category_id)

    # Calculate total value dynamically or using annotate
    total_buy_value = sum([p.buy_price * p.stock for p in qs if p.stock > 0])
    total_sell_value = sum([p.sell_price * p.stock for p in qs if p.stock > 0])

    brands = Brands.objects.all()
    categories = Categories.objects.all()

    return render(request, 'inventory_report.html', {
        'products': qs,
        'brands': brands,
        'categories': categories,
        'brand_id': brand_id,
        'category_id': category_id,
        'total_buy_value': total_buy_value,
        'total_sell_value': total_sell_value
    })

@login_required
def adjustment_list(request):
    if request.user.userprofile.role != 'admin':
        return redirect('dashboard')
    adjustments = StockAdjustments.objects.select_related('product', 'product__brand', 'product__category', 'adjusted_by').order_by('-adjusted_at')
    return render(request, 'adjustment.html', {'adjustments': adjustments})

@login_required
def adjustment_save(request):
    if request.user.userprofile.role != 'admin':
        return redirect('dashboard')

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 0))
        reason = request.POST.get('reason')
        notes = request.POST.get('notes', '')

        try:
            product = Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            return JsonResponse({'status': 'error', 'msg': 'Produk tidak ditemukan.'})

        if quantity <= 0:
            return JsonResponse({'status': 'error', 'msg': 'Jumlah pengurangan harus lebih dari 0.'})

        if quantity > product.stock:
            return JsonResponse({'status': 'error', 'msg': f'Jumlah melebihi stok saat ini ({product.stock} unit).'})

        # Simpan catatan penyesuaian
        StockAdjustments.objects.create(
            product=product,
            adjusted_by=request.user,
            quantity=-quantity,  # disimpan sebagai angka negatif
            reason=reason,
            notes=notes
        )

        # Kurangi stok produk
        product.stock -= quantity
        if product.stock <= 0:
            product.stock = 0
            product.status = 'inactive'
        product.save()

        return JsonResponse({'status': 'success', 'msg': f'Penyesuaian berhasil. Stok "{product.name}" berkurang {quantity} unit.'})

    # GET: tampilkan form
    products = Products.objects.filter(stock__gt=0).select_related('brand', 'category').order_by('name')
    return render(request, 'adjustment_form.html', {'products': products})

@login_required
def closing_admin(request):
    if request.user.userprofile.role != 'admin':
        return redirect('dashboard')
    
    date_filter = request.GET.get('date')
    cashier_id = request.GET.get('cashier_id')

    qs = CashClosings.objects.select_related('cashier', 'unlocked_by').all().order_by('-closing_date', '-id')
    if date_filter:
        qs = qs.filter(closing_date=date_filter)
    if cashier_id:
        qs = qs.filter(cashier_id=cashier_id)

    cashiers = User.objects.filter(userprofile__role='kasir')

    return render(request, 'closing_admin.html', {
        'closings': qs,
        'cashiers': cashiers,
        'date_filter': date_filter,
        'cashier_id': cashier_id
    })

# --- POS / KASIR ---
@login_required
def pos_page(request):
    import json
    if request.user.userprofile.role not in ['admin', 'kasir']:
        return redirect('dashboard')

    categories = Categories.objects.all()
    brands = Brands.objects.all()

    # Embed initial product data to avoid extra AJAX request on first load
    qs = Products.objects.select_related('brand', 'category').filter(status='active', stock__gt=0).order_by('name')
    initial_products = []
    for p in qs:
        initial_products.append({
            'id': p.id,
            'name': p.name,
            'brand': p.brand.name if p.brand else '-',
            'size': p.size,
            'condition': p.condition,
            'price': float(p.sell_price),
            'stock': p.stock,
            'image': p.image.url if p.image else '',
            'category_id': p.category_id,
            'product_code': p.product_code or '-',
        })

    return render(request, 'pos.html', {
        'categories': categories,
        'brands': brands,
        'initial_products_json': json.dumps(initial_products),
    })

@login_required
def pos_get_products(request):
    query = request.GET.get('q', '').lower()
    cat_id = request.GET.get('category_id')
    brand_id = request.GET.get('brand_id')

    qs = Products.objects.select_related('brand', 'category').filter(status='active', stock__gt=0).order_by('name')
    if query:
        qs = qs.filter(
            Q(name__icontains=query) | Q(product_code__icontains=query)
        )
    if cat_id:
        qs = qs.filter(category_id=cat_id)
    if brand_id:
        qs = qs.filter(brand_id=brand_id)

    data = []
    for p in qs:
        data.append({
            'id': p.id,
            'name': p.name,
            'brand': p.brand.name if p.brand else '-',
            'size': p.size,
            'condition': p.condition,
            'price': p.sell_price,
            'stock': p.stock,
            'image': p.image.url if p.image else '',
            'product_code': p.product_code or '-',
        })
    return JsonResponse({'products': data})

@login_required
@transaction.atomic
def pos_process_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            items = data.get('items', [])
            payment_method = data.get('payment_method')
            cash_received = int(data.get('cash_received', 0))
            discount_type = data.get('discount_type', 'nominal')
            discount_value = float(data.get('discount_value', 0))

            if not items:
                return JsonResponse({'status': 'error', 'message': 'Keranjang kosong.'})

            # Calculate total
            subtotal_amount = 0
            product_updates = []
            
            # Sort items by id to avoid deadlocks
            item_ids = [item['id'] for item in items]
            
            # Lock the rows for these products
            products_locked = Products.objects.select_for_update().filter(id__in=item_ids)
            products_dict = {p.id: p for p in products_locked}

            for item in items:
                p = products_dict.get(item['id'])
                if not p:
                    return JsonResponse({'status': 'error', 'message': f'Produk ID {item["id"]} tidak ditemukan.'})
                
                if p.stock < int(item['qty']):
                    return JsonResponse({'status': 'error', 'message': f'Stok {p.name} tidak mencukupi. Sisa stok: {p.stock}.'})
                
                subtotal = p.sell_price * int(item['qty'])
                subtotal_amount += subtotal
                product_updates.append((p, int(item['qty']), subtotal))

            # Calculate Discount
            discount_amount = 0
            if discount_value > 0:
                if discount_type == 'percent':
                    discount_amount = int(subtotal_amount * (min(discount_value, 100) / 100))
                else:
                    discount_amount = int(discount_value)
                    if discount_amount > subtotal_amount:
                        discount_amount = subtotal_amount

            total_amount = subtotal_amount - discount_amount

            change_amount = 0
            if payment_method == 'tunai':
                if cash_received < total_amount:
                    return JsonResponse({'status': 'error', 'message': 'Uang tunai kurang.'})
                change_amount = cash_received - total_amount
            else:
                cash_received = total_amount # Untuk QRIS/Transfer, cash received dianggap pas

            # Create Transaction
            trx = Transactions.objects.create(
                cashier=request.user,
                subtotal_amount=subtotal_amount,
                discount_amount=discount_amount,
                total_amount=total_amount,
                payment_method=payment_method,
                cash_received=cash_received,
                change_amount=change_amount
            )

            # Create Details & signals will update stock
            for p, qty, subtotal in product_updates:
                TransactionDetails.objects.create(
                    transaction=trx,
                    product=p,
                    quantity=qty,
                    sell_price=p.sell_price,
                    subtotal=subtotal
                )
            
            # Return transaction data for receipt printing
            receipt_data = {
                'id': trx.id,
                'date': trx.transaction_date.strftime("%d %b %Y %H:%M"),
                'cashier': trx.cashier.username,
                'subtotal': trx.subtotal_amount,
                'discount': trx.discount_amount,
                'total': trx.total_amount,
                'method': trx.get_payment_method_display(),
                'received': trx.cash_received,
                'change': trx.change_amount,
                'items': [{'name': p.name, 'size': p.size, 'qty': qty, 'price': p.sell_price, 'subtotal': subtotal, 'product_code': p.product_code or '-'} for p, qty, subtotal in product_updates]
            }

            return JsonResponse({'status': 'success', 'message': 'Transaksi berhasil.', 'receipt': receipt_data})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def transaction_detail(request, pk):
    if request.user.userprofile.role not in ['admin', 'kasir']:
        return redirect('dashboard')
    try:
        transaction = Transactions.objects.prefetch_related('details__product').get(id=pk)
    except Transactions.DoesNotExist:
        return HttpResponse("Transaksi tidak ditemukan.", status=404)
    
    return render(request, 'transaction_detail.html', {'t': transaction})

@login_required
def catalog_kasir(request):
    if request.user.userprofile.role not in ['admin', 'kasir']:
        return redirect('dashboard')
    
    query = request.GET.get('q', '')
    brand_id = request.GET.get('brand_id', '')
    category_id = request.GET.get('category_id', '')

    qs = Products.objects.select_related('brand', 'category').filter(status='active', stock__gt=0).order_by('name')
    if query:
        qs = qs.filter(name__icontains=query)
    if brand_id:
        qs = qs.filter(brand_id=brand_id)
    if category_id:
        qs = qs.filter(category_id=category_id)

    brands = Brands.objects.all()
    categories = Categories.objects.all()

    return render(request, 'catalog_kasir.html', {
        'products': qs,
        'brands': brands,
        'categories': categories,
        'q': query,
        'brand_id': brand_id,
        'category_id': category_id
    })

# --- CLOSING KASIR ---
@login_required
def closing_kasir(request):
    if request.user.userprofile.role not in ['admin', 'kasir']:
        return redirect('dashboard')

    # Gunakan waktu lokal (Asia/Jakarta) agar sesuai dengan jam kerja kasir
    today = timezone.localtime(timezone.now()).date()
    cashier = request.user

    # Check if already submitted today
    existing_closing = CashClosings.objects.filter(cashier=cashier, closing_date=today).first()

    # Filter transaksi: jika admin maka ambil semua transaksi hari ini,
    # jika kasir maka hanya miliknya sendiri
    if request.user.userprofile.role == 'admin':
        today_transactions = Transactions.objects.filter(
            transaction_date__date=today
        )
    else:
        today_transactions = Transactions.objects.filter(
            cashier=cashier,
            transaction_date__date=today
        )
    
    # Hanya hitung transaksi yang sukses
    success_transactions = today_transactions.filter(status='success')

    total_cash    = success_transactions.filter(payment_method='tunai').aggregate(t=Sum('total_amount'))['t'] or 0
    total_transfer= success_transactions.filter(payment_method='transfer_bri').aggregate(t=Sum('total_amount'))['t'] or 0
    total_qris    = success_transactions.filter(payment_method='qris').aggregate(t=Sum('total_amount'))['t'] or 0
    grand_total   = total_cash + total_transfer + total_qris
    trx_count     = success_transactions.count()

    return render(request, 'closing_kasir.html', {
        'today': today,
        'existing_closing': existing_closing,
        'total_cash': total_cash,
        'total_transfer': total_transfer,
        'total_qris': total_qris,
        'grand_total': grand_total,
        'trx_count': trx_count,
    })

@login_required
def closing_submit(request):
    if request.method == 'POST':
        if request.user.userprofile.role not in ['admin', 'kasir']:
            return JsonResponse({'status': 'error', 'message': 'Akses ditolak.'})

        # Gunakan waktu lokal (Asia/Jakarta)
        today = timezone.localtime(timezone.now()).date()
        cashier = request.user

        actual_cash = int(request.POST.get('actual_cash', 0))
        notes = request.POST.get('notes', '')

        # Hitung dari transaksi yang relevan (konsisten dengan closing_kasir view)
        if request.user.userprofile.role == 'admin':
            today_transactions = Transactions.objects.filter(transaction_date__date=today)
        else:
            today_transactions = Transactions.objects.filter(cashier=cashier, transaction_date__date=today)

        # Hanya hitung transaksi yang sukses
        success_transactions = today_transactions.filter(status='success')

        total_cash     = success_transactions.filter(payment_method='tunai').aggregate(t=Sum('total_amount'))['t'] or 0
        total_transfer = success_transactions.filter(payment_method='transfer_bri').aggregate(t=Sum('total_amount'))['t'] or 0
        total_qris     = success_transactions.filter(payment_method='qris').aggregate(t=Sum('total_amount'))['t'] or 0
        difference     = actual_cash - total_cash

        # Cek apakah sudah ada record (bisa jadi dibuka ulang oleh admin)
        existing = CashClosings.objects.filter(cashier=cashier, closing_date=today).first()

        if existing:
            # Jika masih terkunci (bukan dibuka ulang), tolak
            if existing.is_locked:
                return JsonResponse({'status': 'error', 'message': 'Closing hari ini sudah dikunci. Hubungi admin untuk membukanya.'})
            # Update record yang sudah ada (setelah dibuka ulang)
            existing.system_cash_total    = total_cash
            existing.system_transfer_total = total_transfer
            existing.system_qris_total    = total_qris
            existing.actual_cash          = actual_cash
            existing.cash_difference      = difference
            existing.notes                = notes
            existing.is_locked            = True
            existing.save()
        else:
            # Buat record baru (pertama kali closing)
            CashClosings.objects.create(
                cashier=cashier,
                closing_date=today,
                system_cash_total=total_cash,
                system_transfer_total=total_transfer,
                system_qris_total=total_qris,
                actual_cash=actual_cash,
                cash_difference=difference,
                notes=notes,
                is_locked=True
            )

        messages.success(request, "Closing kasir berhasil dikunci!")
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid method'})


# --- CLOSING: BUKA ULANG (Admin Only) ---
@login_required
def closing_unlock(request):
    """Admin membuka kembali closing kasir yang sudah terkunci."""
    if request.user.userprofile.role != 'admin':
        return JsonResponse({'status': 'error', 'message': 'Hanya admin yang dapat membuka kembali closing.'})

    if request.method == 'POST':
        closing_id = request.POST.get('closing_id')
        reason     = request.POST.get('reason', '').strip()

        if not reason:
            return JsonResponse({'status': 'error', 'message': 'Alasan wajib diisi.'})

        try:
            closing = CashClosings.objects.select_related('cashier').get(id=closing_id)
        except CashClosings.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Data closing tidak ditemukan.'})

        if not closing.is_locked:
            return JsonResponse({'status': 'error', 'message': 'Closing ini sudah dalam kondisi terbuka.'})

        closing.is_locked     = False
        closing.unlocked_by   = request.user
        closing.unlocked_at   = timezone.now()
        closing.unlock_reason = reason
        closing.unlock_count  = (closing.unlock_count or 0) + 1
        closing.save()

        return JsonResponse({
            'status': 'success',
            'message': f'Closing {closing.cashier.username} ({closing.closing_date}) berhasil dibuka. Kasir dapat mengisi ulang.'
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid method'})

# --- VOID / RETUR TRANSAKSI ---
@login_required
@transaction.atomic
def transaction_void(request, pk):
    """Membatalkan transaksi dan mengembalikan stok produk ke 1/aktif."""
    if request.user.userprofile.role != 'admin':
        return JsonResponse({'status': 'error', 'message': 'Hanya admin yang dapat membatalkan transaksi.'})

    if request.method == 'POST':
        try:
            trx = Transactions.objects.prefetch_related('details__product').get(id=pk)
        except Transactions.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Transaksi tidak ditemukan.'})

        if trx.status == 'void':
            return JsonResponse({'status': 'error', 'message': 'Transaksi ini sudah dibatalkan sebelumnya.'})

        reason = request.POST.get('reason', '').strip()
        if not reason:
            return JsonResponse({'status': 'error', 'message': 'Alasan retur/pembatalan wajib diisi.'})

        # Kembalikan stok
        for detail in trx.details.all():
            product = detail.product
            product.stock += detail.quantity
            product.status = 'active'
            product.save()

        # Update status transaksi
        trx.status = 'void'
        trx.voided_by = request.user
        trx.void_reason = reason
        trx.voided_at = timezone.now()
        trx.save()

        return JsonResponse({'status': 'success', 'message': f'Transaksi {trx.id} berhasil dibatalkan dan stok dikembalikan.'})

    return JsonResponse({'status': 'error', 'message': 'Metode tidak diizinkan.'})

# --- CHECK CLOSING KASIR ---
@login_required
def check_closing_status(request):
    """Mengecek apakah user (kasir) sudah submit closing hari ini."""
    if request.user.userprofile.role != 'kasir':
        return JsonResponse({'status': 'success', 'has_closed': True}) # Admin bebas keluar
    
    today = timezone.localtime(timezone.now()).date()
    # Cek apakah ada record closing hari ini untuk user
    existing = CashClosings.objects.filter(cashier=request.user, closing_date=today).exists()
    return JsonResponse({'status': 'success', 'has_closed': existing})
