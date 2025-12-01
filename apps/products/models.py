"""
Products and Categories Models
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
import random
import string


class Category(models.Model):
    """Product Category"""
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre'
    )
    
    description = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    icon = models.CharField(
        max_length=50,
        default='bi-box',
        verbose_name='Icono',
        help_text='Bootstrap Icon class (ej: bi-box, bi-cart, etc.)'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Product Model"""
    
    code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        verbose_name='Código'
    )
    
    description = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    name = models.CharField(
        max_length=200,
        verbose_name='Nombre'
    )
    
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='Categoría'
    )
    
    presentation = models.CharField(
        max_length=50,
        verbose_name='Presentación',
        help_text='Ej: 1L, 500g, 1kg, etc.'
    )
    
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Precio de compra'
    )
    
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Precio de venta'
    )
    
    stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Stock actual'
    )
    
    reserved_stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Stock reservado'
    )
    
    min_stock = models.IntegerField(
        default=10,
        validators=[MinValueValidator(0)],
        verbose_name='Stock mínimo'
    )
    
    expiration_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de vencimiento'
    )
    
    supplier = models.ForeignKey(
        'suppliers.Supplier',
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='Proveedor'
    )
    
    image = models.ImageField(
        upload_to='products/',
        null=True,
        blank=True,
        verbose_name='Imagen'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización'
    )
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.name} ({self.presentation})"
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_code():
        """Generate unique product code"""
        while True:
            code = 'P-' + ''.join(random.choices(string.digits, k=6))
            if not Product.objects.filter(code=code).exists():
                return code
    
    @property
    def profit_margin(self):
        """Calculate profit margin percentage"""
        if self.purchase_price > 0:
            return ((self.sale_price - self.purchase_price) / self.purchase_price) * 100
        return 0
    
    @property
    def is_low_stock(self):
        """Check if stock is below minimum"""
        return (self.stock - self.reserved_stock) <= self.min_stock
    
    @property
    def is_expiring_soon(self):
        """Check if product expires in 30 days or less"""
        if self.expiration_date:
            days_until_expiration = (self.expiration_date - timezone.now().date()).days
            return 0 <= days_until_expiration <= 30
        return False
    
    @property
    def is_expired(self):
        """Check if product is expired"""
        if self.expiration_date:
            return self.expiration_date < timezone.now().date()
        return False
    
    @property
    def available_stock(self):
        """Stock disponible (stock - reservado)"""
        avail = self.stock - self.reserved_stock
        return avail if avail > 0 else 0
