"""
Custom User Model with Role-Based Access
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model with role-based permissions
    """
    
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        VENDEDOR = 'VENDEDOR', 'Vendedor'
    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.ADMIN,
        verbose_name='Rol'
    )
    
    phone = models.CharField(
        max_length=15,
        blank=True,
        verbose_name='Teléfono'
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
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN
    
    @property
    def is_vendedor(self):
        return self.role == self.Role.VENDEDOR
