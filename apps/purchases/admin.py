from django.contrib import admin
from .models import Purchase, PurchaseItem, StockMovement


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['code', 'supplier', 'total', 'created_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['code', 'supplier__name']
    readonly_fields = ['code', 'created_at']
    inlines = [PurchaseItemInline]


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'movement_type', 'quantity', 'previous_stock', 'new_stock', 'created_at']
    list_filter = ['movement_type', 'created_at']
    search_fields = ['product__name', 'product__code']
    readonly_fields = ['created_at']
