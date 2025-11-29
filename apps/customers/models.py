"""
Customer Model
"""
from django.db import models
from django.core.validators import RegexValidator


class Customer(models.Model):
    """Customer Model"""
    
    dni_validator = RegexValidator(
        regex=r'^\d{8}$',
        message='El DNI debe tener 8 dígitos'
    )
    
    dni = models.CharField(
        max_length=8,
        unique=True,
        validators=[dni_validator],
        verbose_name='DNI'
    )
    
    name = models.CharField(
        max_length=200,
        verbose_name='Nombre completo'
    )
    
    phone = models.CharField(
        max_length=15,
        verbose_name='Teléfono'
    )
    
    email = models.EmailField(
        blank=True,
        verbose_name='Correo electrónico'
    )
    
    address = models.TextField(
        blank=True,
        verbose_name='Dirección'
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
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - DNI: {self.dni}"
    
    @property
    def total_purchases(self):
        """Calculate total purchases amount"""
        return self.sales.filter(status='COMPLETED').aggregate(
            total=models.Sum('total')
        )['total'] or 0
