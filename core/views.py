from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta
from .models import Products, Transactions, TransactionDetails, Brands, Categories, Suppliers, StockIns, StockInDetails, CashClosings, UserProfile
from django.contrib.auth.models import User

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            # Custom logic: check role
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
        # Fallback ke POS nanti jika kasir
        return render(request, 'base.html') # Placeholder if not admin, or redirect

    today = timezone.now().date()

    # 1. Total Stock (active products)
    total_stock_dict = Products.objects.filter(status='active').aggregate(total_stock=Sum('stock'))
    total_stock = total_stock_dict['total_stock'] or 0

    # 2. Total Products Sold Today
    sold_today_dict = TransactionDetails.objects.filter(transaction__transaction_date__date=today).aggregate(total_sold=Sum('quantity'))
    total_sold_today = sold_today_dict['total_sold'] or 0

    # 3. Revenue Today
    revenue_today_dict = Transactions.objects.filter(transaction_date__date=today).aggregate(total_rev=Sum('total_amount'))
    revenue_today = revenue_today_dict['total_rev'] or 0

    # 4. Low Stock Products
    low_stock_products = Products.objects.filter(stock__lte=3, status='active').order_by('stock')
    low_stock_count = low_stock_products.count()

    # Top 5 best selling products
    top_products = Products.objects.annotate(total_sold=Sum('transactiondetails__quantity')).order_by('-total_sold')[:5]

    context = {
        'total_stock': total_stock,
        'total_sold_today': total_sold_today,
        'revenue_today': revenue_today,
        'low_stock_count': low_stock_count,
        'low_stock_products': low_stock_products,
        'top_products': top_products,
    }

    return render(request, 'dashboard.html', context)

@login_required
def dashboard_chart_data(request):
    period = request.GET.get('period', 'daily')
    now = timezone.now()
    labels = []
    data = []

    if period == 'daily':
        for i in range(6, -1, -1):
            date = (now - timedelta(days=i)).date()
            labels.append(date.strftime('%b %d'))
            rev = Transactions.objects.filter(transaction_date__date=date).aggregate(t=Sum('total_amount'))['t'] or 0
            data.append(rev)
    elif period == 'weekly':
        for i in range(3, -1, -1):
            start = (now - timedelta(weeks=i+1)).date()
            end = (now - timedelta(weeks=i)).date()
            labels.append(f"{start.strftime('%b %d')} - {end.strftime('%b %d')}")
            rev = Transactions.objects.filter(transaction_date__date__gt=start, transaction_date__date__lte=end).aggregate(t=Sum('total_amount'))['t'] or 0
            data.append(rev)
    elif period == 'monthly':
        for i in range(5, -1, -1):
            month = now.month - i
            year = now.year
            if month <= 0:
                month += 12
                year -= 1
            labels.append(f"{month:02d}/{year}")
            rev = Transactions.objects.filter(transaction_date__year=year, transaction_date__month=month).aggregate(t=Sum('total_amount'))['t'] or 0
            data.append(rev)

    return JsonResponse({'labels': labels, 'data': data})

# --- BRANDS ---
@login_required
def brands_list(request):
    if request.user.userprofile.role != 'admin':
        return redirect('dashboard')
    brands = Brands.objects.annotate(product_count=Count('products')).order_by('name')
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
            messages.success(request, "Merek berhasil diubah.")
        else:
            Brands.objects.create(name=name)
            messages.success(request, "Merek berhasil ditambahkan.")
        return JsonResponse({'status': 'success'})
    
    id = request.GET.get('id', '')
    brand = Brands.objects.get(id=id) if id else None
    return render(request, 'brands_form.html', {'brand': brand})

@login_required
def brands_delete(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        Brands.objects.get(id=id).delete()
        messages.success(request, "Merek berhasil dihapus.")
        return JsonResponse({'status': 'success'})

# --- CATEGORIES ---
@login_required
def categories_list(request):
    if request.user.userprofile.role != 'admin':
        return redirect('dashboard')
    categories = Categories.objects.annotate(product_count=Count('products')).order_by('name')
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
            messages.success(request, "Kategori berhasil diubah.")
        else:
            Categories.objects.create(name=name)
            messages.success(request, "Kategori berhasil ditambahkan.")
        return JsonResponse({'status': 'success'})
    
    id = request.GET.get('id', '')
    category = Categories.objects.get(id=id) if id else None
    return render(request, 'categories_form.html', {'category': category})

@login_required
def categories_delete(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        Categories.objects.get(id=id).delete()
        messages.success(request, "Kategori berhasil dihapus.")
        return JsonResponse({'status': 'success'})

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
            messages.success(request, "Pemasok berhasil diubah.")
        else:
            Suppliers.objects.create(name=name, phone=phone, notes=notes)
            messages.success(request, "Pemasok berhasil ditambahkan.")
        return JsonResponse({'status': 'success'})
    
    id = request.GET.get('id', '')
    supplier = Suppliers.objects.get(id=id) if id else None
    return render(request, 'suppliers_form.html', {'supplier': supplier})

@login_required
def suppliers_delete(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        Suppliers.objects.get(id=id).delete()
        messages.success(request, "Pemasok berhasil dihapus.")
        return JsonResponse({'status': 'success'})

# --- PRODUCTS ---
@login_required
def products_list(request):
    if request.user.userprofile.role != 'admin':
        return redirect('dashboard')
    products = Products.objects.select_related('brand', 'category').all().order_by('-id')
    return render(request, 'products.html', {'products': products})

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
            p.name = name
            p.category = cat
            p.brand = brand
            p.size = size
            p.condition = condition
            p.description = description
            p.buy_price = buy_price
            p.sell_price = sell_price
            # stock usually updated via stockin, but allow edit here just in case? Or maybe keep it? Let's allow edit.
            p.stock = stock
            if image:
                p.image = image
            p.save()
            messages.success(request, "Produk berhasil diubah.")
        else:
            p = Products.objects.create(
                name=name, category=cat, brand=brand, size=size,
                condition=condition, description=description,
                buy_price=buy_price, sell_price=sell_price, stock=stock
            )
            if image:
                p.image = image
                p.save()
            messages.success(request, "Produk berhasil ditambahkan.")
        return JsonResponse({'status': 'success'})
    
    id = request.GET.get('id', '')
    product = Products.objects.get(id=id) if id else None
    categories = Categories.objects.all()
    brands = Brands.objects.all()
    conditions = Products.CONDITION_CHOICES
    
    context = {
        'product': product,
        'categories': categories,
        'brands': brands,
        'conditions': conditions,
    }
    return render(request, 'products_form.html', context)

@login_required
def products_delete(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        Products.objects.get(id=id).delete()
        messages.success(request, "Produk berhasil dihapus.")
        return JsonResponse({'status': 'success'})

@login_required
def products_toggle_status(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        p = Products.objects.get(id=id)
        if p.status == 'active':
            p.status = 'inactive'
            msg = "Produk dinonaktifkan."
        else:
            p.status = 'active'
            msg = "Produk diaktifkan."
        p.save()
        messages.success(request, msg)
        return JsonResponse({'status': 'success', 'new_status': p.status})

# --- STOCK IN ---
@login_required
def stockin_list(request):
    if request.user.userprofile.role != 'admin':
        return redirect('dashboard')
    stockins = StockIns.objects.select_related('supplier', 'received_by').annotate(total_items=Count('details')).order_by('-received_date', '-id')
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
        supplier_id = request.POST.get('supplier_id')
        received_date = request.POST.get('received_date')
        notes = request.POST.get('notes', '')
        
        product_ids = request.POST.getlist('product_id[]')
        quantities = request.POST.getlist('quantity[]')
        buy_prices = request.POST.getlist('buy_price[]')

        if not supplier_id or not received_date or not product_ids:
            messages.error(request, "Data penerimaan tidak lengkap.")
            return redirect('stockin_save')

        supplier = Suppliers.objects.get(id=supplier_id)
        si = StockIns.objects.create(
            supplier=supplier,
            received_by=request.user,
            received_date=received_date,
            notes=notes
        )

        for i in range(len(product_ids)):
            pid = product_ids[i]
            qty_str = quantities[i]
            bp_str = buy_prices[i]
            
            qty = int(qty_str) if qty_str.strip() else 0
            bp = int(bp_str) if bp_str.strip() else 0
            
            if qty > 0:
                product = Products.objects.get(id=pid)
                StockInDetails.objects.create(
                    stock_in=si,
                    product=product,
                    quantity=qty,
                    buy_price=bp
                )
                # Note: signals.py handles incrementing product.stock
                
                # Update product buy_price if changed? The PRD implies stock details have buy_price, let's also update the master product buy_price to the latest one
                if bp > 0:
                    product.buy_price = bp
                    product.save()

        messages.success(request, "Penerimaan barang berhasil dicatat.")
        return redirect('stockin_list')

    suppliers = Suppliers.objects.all().order_by('name')
    products = Products.objects.filter(status='active').select_related('brand', 'category').order_by('name')
    return render(request, 'stockin_form.html', {'suppliers': suppliers, 'products': products})

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
            messages.success(request, "Kasir/User berhasil diubah.")
        else:
            u = User.objects.create_user(username=username, password=password)
            UserProfile.objects.create(user=u, role=role, phone=phone)
            messages.success(request, "Kasir/User berhasil ditambahkan.")
        return JsonResponse({'status': 'success'})

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
        messages.success(request, msg)
        return JsonResponse({'status': 'success', 'is_active': u.is_active})

# --- REPORTS ---
@login_required
def sales_report(request):
    if request.user.userprofile.role != 'admin':
        return redirect('dashboard')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    cashier_id = request.GET.get('cashier_id')
    payment_method = request.GET.get('payment_method')

    qs = Transactions.objects.select_related('cashier').all().order_by('-transaction_date')

    if start_date:
        qs = qs.filter(transaction_date__date__gte=start_date)
    if end_date:
        qs = qs.filter(transaction_date__date__lte=end_date)
    if cashier_id:
        qs = qs.filter(cashier_id=cashier_id)
    if payment_method:
        qs = qs.filter(payment_method=payment_method)

    cashiers = User.objects.filter(userprofile__role='kasir')
    total_revenue = qs.aggregate(t=Sum('total_amount'))['t'] or 0

    return render(request, 'sales_report.html', {
        'transactions': qs,
        'cashiers': cashiers,
        'start_date': start_date,
        'end_date': end_date,
        'cashier_id': cashier_id,
        'payment_method': payment_method,
        'total_revenue': total_revenue
    })

@login_required
def inventory_report(request):
    if request.user.userprofile.role != 'admin':
        return redirect('dashboard')
    
    brand_id = request.GET.get('brand_id')
    category_id = request.GET.get('category_id')

    qs = Products.objects.select_related('brand', 'category').filter(status='active').order_by('name')
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
def closing_admin(request):
    if request.user.userprofile.role != 'admin':
        return redirect('dashboard')
    
    date_filter = request.GET.get('date')
    cashier_id = request.GET.get('cashier_id')

    qs = CashClosings.objects.select_related('cashier').all().order_by('-closing_date', '-id')
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
