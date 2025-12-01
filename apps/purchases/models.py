"""
Purchases and Stock Movement Models
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from datetime import datetime
import random
import string


class Purchase(models.Model):
    """Purchase/Stock Entry Model"""
    
    code = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name='Código'
    )
    
    supplier = models.ForeignKey(
        'suppliers.Supplier',
        on_delete=models.PROTECT,
        related_name='purchases',
        verbose_name='Proveedor'
    )
    
    invoice_number = models.CharField(
        max_length=50,
        verbose_name='Número de factura'
    )
    
    invoice_photo = models.ImageField(
        upload_to='invoices/',
        null=True,
        blank=True,
        verbose_name='Foto de factura'
    )
    
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Total'
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name='Notas'
    )
    
    is_draft = models.BooleanField(
        default=False,
        verbose_name='Borrador'
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='purchases',
        verbose_name='Registrado por'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de compra'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización'
    )
    
    class Meta:
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.supplier.name}"
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_code():
        """Generate unique purchase code: C-YYYYMMDD-XXXX"""
        date_str = datetime.now().strftime('%Y%m%d')
        while True:
            random_str = ''.join(random.choices(string.digits, k=4))
            code = f'C-{date_str}-{random_str}'
            if not Purchase.objects.filter(code=code).exists():
                return code
    
    @property
    def items_count(self):
        """Total items in purchase"""
        return self.items.count()


class PurchaseItem(models.Model):
    """Purchase Line Item"""
    
    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Compra'
    )
    
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='purchase_items',
        verbose_name='Producto'
    )
    
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Cantidad'
    )
    
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Precio unitario'
    )
    
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Subtotal'
    )
    
    class Meta:
        verbose_name = 'Item de compra'
        verbose_name_plural = 'Items de compra'
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        if not self.purchase.is_draft:
            product = self.product
            previous = product.stock
            product.stock = previous + self.quantity
            product.save()
            StockMovement.objects.create(
                product=product,
                movement_type=StockMovement.MovementType.PURCHASE,
                quantity=self.quantity,
                previous_stock=previous,
                new_stock=product.stock,
                reference_id=self.purchase_id,
                created_by=self.purchase.created_by,
            )


class StockMovement(models.Model):
    """Stock Movement/Kardex Model"""
    
    class MovementType(models.TextChoices):
        PURCHASE = 'PURCHASE', 'Compra'
        SALE = 'SALE', 'Venta'
        ADJUSTMENT = 'ADJUSTMENT', 'Ajuste'
    
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='stock_movements',
        verbose_name='Producto'
    )
    
    movement_type = models.CharField(
        max_length=10,
        choices=MovementType.choices,
        verbose_name='Tipo de movimiento'
    )
    
    quantity = models.IntegerField(
        verbose_name='Cantidad',
        help_text='Positivo para entradas, negativo para salidas'
    )
    
    previous_stock = models.IntegerField(
        verbose_name='Stock anterior'
    )
    
    new_stock = models.IntegerField(
        verbose_name='Stock nuevo'
    )
    
    reference_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='ID de referencia',
        help_text='ID de venta o compra relacionada'
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name='Notas'
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='stock_movements',
        verbose_name='Registrado por'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de movimiento'
    )
    
    class Meta:
        verbose_name = 'Movimiento de stock'
        verbose_name_plural = 'Movimientos de stock (Kardex)'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.code} - {self.get_movement_type_display()} ({self.quantity:+d})"
