"""
Supplier Model
"""
from django.db import models
from django.core.validators import RegexValidator


class Supplier(models.Model):
    """Supplier/Provider Model"""
    
    ruc_validator = RegexValidator(
        regex=r'^\d{11}$',
        message='El RUC debe tener 11 dígitos'
    )
    
    name = models.CharField(
        max_length=200,
        verbose_name='Nombre/Razón Social'
    )
    
    ruc = models.CharField(
        max_length=11,
        unique=True,
        validators=[ruc_validator],
        verbose_name='RUC'
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
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - RUC: {self.ruc}"
