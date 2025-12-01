"""
Sales and Sale Items Models
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from datetime import datetime
import random
import string


class Sale(models.Model):
    """Sale/Invoice Model"""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        COMPLETED = 'COMPLETED', 'Completada'
        CANCELLED = 'CANCELLED', 'Cancelada'
    
    class PaymentMethod(models.TextChoices):
        CASH = 'CASH', 'Efectivo'
        CARD = 'CARD', 'Tarjeta'
        TRANSFER = 'TRANSFER', 'Transferencia'
        YAPE = 'YAPE', 'Yape/Plin'
    
    code = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name='Código'
    )
    
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.PROTECT,
        related_name='sales',
        null=True,
        blank=True,
        verbose_name='Cliente'
    )
    
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='sales',
        verbose_name='Vendedor'
    )
    
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Subtotal'
    )
    
    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Descuento'
    )
    
    tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='IGV (18%)'
    )
    
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Total'
    )
    
    payment_method = models.CharField(
        max_length=10,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH,
        verbose_name='Método de pago'
    )
    
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.COMPLETED,
        verbose_name='Estado'
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name='Notas'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de venta'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización'
    )
    
    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - S/ {self.total}"
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_code():
        """Generate unique sale code: V-YYYYMMDD-XXXX"""
        date_str = datetime.now().strftime('%Y%m%d')
        while True:
            random_str = ''.join(random.choices(string.digits, k=4))
            code = f'V-{date_str}-{random_str}'
            if not Sale.objects.filter(code=code).exists():
                return code
    
    @property
    def items_count(self):
        """Total items in sale"""
        return self.items.count()
    
    @property
    def total_profit(self):
        """Calculate total profit from sale"""
        profit = 0
        for item in self.items.all():
            profit += (item.unit_price - item.product.purchase_price) * item.quantity
        return profit


class SaleItem(models.Model):
    """Sale Line Item"""
    
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Venta'
    )
    
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='sale_items',
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
        verbose_name = 'Item de venta'
        verbose_name_plural = 'Items de venta'
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class Reservation(models.Model):
    class Status(models.TextChoices):
        RESERVED = 'RESERVED', 'Reservado'
        FULFILLED = 'FULFILLED', 'Cumplido'
        CANCELED = 'CANCELED', 'Cancelado'

    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='reservations',
        verbose_name='Producto'
    )

    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.PROTECT,
        related_name='reservations',
        null=True,
        blank=True,
        verbose_name='Cliente'
    )

    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Cantidad'
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.RESERVED,
        verbose_name='Estado'
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Expira'
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='reservations',
        verbose_name='Registrado por'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Actualizado')

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.code} x {self.quantity} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        delta = 0
        if self.pk:
            old = Reservation.objects.get(pk=self.pk)
            old_reserved = old.quantity if old.status == Reservation.Status.RESERVED else 0
            new_reserved = self.quantity if self.status == Reservation.Status.RESERVED else 0
            delta = new_reserved - old_reserved
        else:
            if self.status == Reservation.Status.RESERVED:
                delta = self.quantity
        super().save(*args, **kwargs)
        if delta != 0:
            p = self.product
            p.reserved_stock = max(0, p.reserved_stock + delta)
            p.save()

    def delete(self, using=None, keep_parents=False):
        if self.status == Reservation.Status.RESERVED:
            p = self.product
            p.reserved_stock = max(0, p.reserved_stock - self.quantity)
            p.save()
        return super().delete(using=using, keep_parents=keep_parents)
