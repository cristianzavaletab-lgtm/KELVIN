"""
Sales URL Configuration
"""
from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.SaleListView.as_view(), name='sale_list'),
    path('pos/', views.POSView.as_view(), name='pos'),
    path('process/', views.ProcessSaleView.as_view(), name='process_sale'),
    path('<int:pk>/', views.SaleDetailView.as_view(), name='sale_detail'),
]
