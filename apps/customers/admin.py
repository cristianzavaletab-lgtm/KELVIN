from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['dni', 'name', 'phone', 'is_active', 'created_at']
    search_fields = ['dni', 'name', 'phone']
    list_filter = ['is_active', 'created_at']
