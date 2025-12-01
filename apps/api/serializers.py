"""
API Serializers
"""
from rest_framework import serializers
from apps.products.models import Product, Category
from apps.sales.models import Sale, SaleItem
from apps.customers.models import Customer
from apps.suppliers.models import Supplier


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    available_stock = serializers.IntegerField(source='available_stock', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'code', 'name', 'category', 'category_name', 'presentation',
                  'purchase_price', 'sale_price', 'stock', 'reserved_stock', 'available_stock', 'min_stock', 'expiration_date',
                  'supplier', 'supplier_name', 'image', 'is_active', 'is_low_stock',
                  'created_at', 'updated_at']
        read_only_fields = ['code', 'created_at', 'updated_at']


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'dni', 'name', 'phone', 'email', 'address', 'is_active', 'created_at']


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'ruc', 'phone', 'email', 'address', 'is_active', 'created_at']


class SaleItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = SaleItem
        fields = ['id', 'product', 'product_name', 'quantity', 'unit_price', 'subtotal']


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)
    seller_name = serializers.CharField(source='seller.get_full_name', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True, allow_null=True)
    
    class Meta:
        model = Sale
        fields = ['id', 'code', 'customer', 'customer_name', 'seller', 'seller_name',
                  'subtotal', 'discount', 'tax', 'total', 'payment_method', 'status',
                  'items', 'created_at']
        read_only_fields = ['code', 'seller', 'created_at']
