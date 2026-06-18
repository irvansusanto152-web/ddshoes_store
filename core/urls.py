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
]
