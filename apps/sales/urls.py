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
    path('reservations/create/', views.CreateReservationView.as_view(), name='create_reservation'),
    path('reservations/list/', views.ListReservationsView.as_view(), name='list_reservations'),
]
