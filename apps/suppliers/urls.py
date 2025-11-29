from django.urls import path
from . import views

app_name = 'suppliers'

urlpatterns = [
    path('', views.SupplierListView.as_view(), name='supplier_list'),
    path('create/', views.SupplierCreateView.as_view(), name='supplier_create'),
    path('edit/<int:pk>/', views.SupplierUpdateView.as_view(), name='supplier_edit'),
    path('delete/<int:pk>/', views.SupplierDeleteView.as_view(), name='supplier_delete'),
]
