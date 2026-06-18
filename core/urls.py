from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('dashboard/chart-data/', views.dashboard_chart_data, name='dashboard_chart_data'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
