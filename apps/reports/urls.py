"""
Reports URL Configuration
"""
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('reports/', views.ReportView.as_view(), name='reports'),
    path('generate-suggested-orders/', views.GenerateSuggestedOrdersView.as_view(), name='generate_suggested_orders'),
]
