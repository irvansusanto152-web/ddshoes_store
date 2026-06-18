import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta
from .models import Products, Transactions, TransactionDetails, Brands, Categories, Suppliers, StockIns, StockInDetails, CashClosings, UserProfile
from django.contrib.auth.models import User

def login_view(request):
    if request.user.is_authenticated:
        if request.user.userprofile.role == 'kasir':
            return redirect('pos_page')
        return redirect('dashboard')
        
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            if user.userprofile.role == 'kasir':
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
        return JsonResponse({'status': 'success', 'id': p.id, 'name': p.name})
    
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
                final_bp = bp if bp > 0 else product.buy_price
                StockInDetails.objects.create(
                    stock_in=si,
                    product=product,
                    quantity=qty,
                    buy_price=final_bp
                )
                # Note: signals.py handles incrementing product.stock
                
                # Update product buy_price if changed? The PRD implies stock details have buy_price, let's also update the master product buy_price to the latest one
                if bp > 0:
                    product.buy_price = bp
                    product.save()

        messages.success(request, "Penerimaan barang berhasil dicatat.")
        return redirect('stockin_list')

    suppliers = Suppliers.objects.all().order_by('name')
    products = Products.objects.select_related('brand', 'category').order_by('name')
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

# --- POS / KASIR ---
@login_required
def pos_page(request):
    if request.user.userprofile.role not in ['admin', 'kasir']:
        return redirect('dashboard')
    
    categories = Categories.objects.all()
    brands = Brands.objects.all()
    return render(request, 'pos.html', {'categories': categories, 'brands': brands})

@login_required
def pos_get_products(request):
    query = request.GET.get('q', '').lower()
    cat_id = request.GET.get('category_id')
    brand_id = request.GET.get('brand_id')

    qs = Products.objects.select_related('brand', 'category').filter(status='active', stock__gt=0).order_by('name')
    if query:
        qs = qs.filter(name__icontains=query)
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
            'image': p.image.url if p.image else ''
        })
    return JsonResponse({'products': data})

@login_required
def pos_process_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            items = data.get('items', [])
            payment_method = data.get('payment_method')
            cash_received = int(data.get('cash_received', 0))

            if not items:
                return JsonResponse({'status': 'error', 'message': 'Keranjang kosong.'})

            # Calculate total
            total_amount = 0
            product_updates = []
            for item in items:
                p = Products.objects.get(id=item['id'])
                if p.stock < int(item['qty']):
                    return JsonResponse({'status': 'error', 'message': f'Stok {p.name} tidak mencukupi.'})
                subtotal = p.sell_price * int(item['qty'])
                total_amount += subtotal
                product_updates.append((p, int(item['qty']), subtotal))

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
                'total': trx.total_amount,
                'method': trx.get_payment_method_display(),
                'received': trx.cash_received,
                'change': trx.change_amount,
                'items': [{'name': p.name, 'size': p.size, 'qty': qty, 'price': p.sell_price, 'subtotal': subtotal} for p, qty, subtotal in product_updates]
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

    qs = Products.objects.select_related('brand', 'category').filter(status='active').order_by('name')
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

    today = timezone.now().date()
    cashier = request.user

    # Check if already submitted today
    existing_closing = CashClosings.objects.filter(cashier=cashier, closing_date=today).first()

    # Compute today's totals from transactions
    today_transactions = Transactions.objects.filter(
        cashier=cashier,
        transaction_date__date=today
    )
    total_cash    = today_transactions.filter(payment_method='tunai').aggregate(t=Sum('total_amount'))['t'] or 0
    total_transfer= today_transactions.filter(payment_method='transfer_bri').aggregate(t=Sum('total_amount'))['t'] or 0
    total_qris    = today_transactions.filter(payment_method='qris').aggregate(t=Sum('total_amount'))['t'] or 0
    grand_total   = total_cash + total_transfer + total_qris
    trx_count     = today_transactions.count()

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

        today = timezone.now().date()
        cashier = request.user

        if CashClosings.objects.filter(cashier=cashier, closing_date=today).exists():
            return JsonResponse({'status': 'error', 'message': 'Closing hari ini sudah dikunci.'})

        actual_cash = int(request.POST.get('actual_cash', 0))
        notes = request.POST.get('notes', '')

        today_transactions = Transactions.objects.filter(cashier=cashier, transaction_date__date=today)
        total_cash    = today_transactions.filter(payment_method='tunai').aggregate(t=Sum('total_amount'))['t'] or 0
        total_transfer= today_transactions.filter(payment_method='transfer_bri').aggregate(t=Sum('total_amount'))['t'] or 0
        total_qris    = today_transactions.filter(payment_method='qris').aggregate(t=Sum('total_amount'))['t'] or 0

        difference = actual_cash - total_cash

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
