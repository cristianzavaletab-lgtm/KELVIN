"""
Accounts URL Configuration
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('whatsapp-templates/', views.WhatsAppTemplatesView.as_view(), name='whatsapp_templates'),
    path('password-change/', views.PasswordChangeView.as_view(), name='password_change'),
]
