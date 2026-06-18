from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('dashboard/chart-data/', views.dashboard_chart_data, name='dashboard_chart_data'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Master: Brands
    path('brands/', views.brands_list, name='brands_list'),
    path('brands/save/', views.brands_save, name='brands_save'),
    path('brands/delete/', views.brands_delete, name='brands_delete'),

    # Master: Categories
    path('categories/', views.categories_list, name='categories_list'),
    path('categories/save/', views.categories_save, name='categories_save'),
    path('categories/delete/', views.categories_delete, name='categories_delete'),

    # Master: Suppliers
    path('suppliers/', views.suppliers_list, name='suppliers_list'),
    path('suppliers/save/', views.suppliers_save, name='suppliers_save'),
    path('suppliers/delete/', views.suppliers_delete, name='suppliers_delete'),

    # Inventory: Products
    path('products/', views.products_list, name='products_list'),
    path('products/save/', views.products_save, name='products_save'),
    path('products/delete/', views.products_delete, name='products_delete'),
    path('products/toggle/', views.products_toggle_status, name='products_toggle_status'),

    # Inventory: Stock In
    path('stockin/', views.stockin_list, name='stockin_list'),
    path('stockin/save/', views.stockin_save, name='stockin_save'),
    path('stockin/detail/<int:pk>/', views.stockin_detail, name='stockin_detail'),

    # Users
    path('users/', views.users_list, name='users_list'),
    path('users/save/', views.users_save, name='users_save'),
    path('users/toggle/', views.users_toggle_status, name='users_toggle_status'),

    # Reports & Closing (Admin)
    path('sales-report/', views.sales_report, name='sales_report'),
    path('inventory-report/', views.inventory_report, name='inventory_report'),
    path('closing-admin/', views.closing_admin, name='closing_admin'),

    # POS / Kasir
    path('pos/', views.pos_page, name='pos_page'),
    path('pos/get-products/', views.pos_get_products, name='pos_get_products'),
    path('pos/process-payment/', views.pos_process_payment, name='pos_process_payment'),
    path('catalog-kasir/', views.catalog_kasir, name='catalog_kasir'),
    path('closing-kasir/', views.closing_kasir, name='closing_kasir'),
    path('closing-kasir/submit/', views.closing_submit, name='closing_submit'),
]
