"""
Reports URL Configuration
"""
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('reports/', views.ReportView.as_view(), name='reports'),
]
