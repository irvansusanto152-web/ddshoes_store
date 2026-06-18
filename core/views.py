from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta
from .models import Products, Transactions, TransactionDetails

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
