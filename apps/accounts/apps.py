from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = 'Cuentas y Usuarios'

    def ready(self):
        try:
            from django.contrib.auth import get_user_model
            from django.db.utils import ProgrammingError, OperationalError
            import os
            from .models import WhatsAppTemplate
            User = get_user_model()
            # Ensure admin exists and has a password
            email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
            password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
            admin, _ = User.objects.get_or_create(
                username='admin',
                defaults={
                    'email': email,
                    'is_staff': True,
                    'is_superuser': True,
                }
            )
            if password:
                admin.set_password(password)
                admin.is_staff = True
                admin.is_superuser = True
                admin.save()
            # Ensure default WhatsApp templates exist
            defaults = {
                'SALE_MESSAGE': (
                    'Gracias por su compra\n'
                    'Venta: {{code}}\n'
                    'Cliente: {{customer}}\n'
                    'Productos:\n{{items}}\n'
                    'TOTAL: S/ {{total}}'
                ),
                'ALERT_OUT_OF_STOCK': (
                    'Producto agotado\n\n'
                    'Nombre: {{name}}\n'
                    'Código: {{code}}'
                ),
                'ALERT_LOW_STOCK': (
                    'Producto por debajo del stock mínimo\n\n'
                    'Nombre: {{name}}\n'
                    'Código: {{code}}\n'
                    'Stock: {{stock}}\n'
                    'Stock mínimo: {{min_stock}}'
                ),
            }
            for key, content in defaults.items():
                WhatsAppTemplate.objects.get_or_create(key=key, defaults={'content': content})
        except (ProgrammingError, OperationalError):
            # Database not ready during migrations or initial setup
            pass
