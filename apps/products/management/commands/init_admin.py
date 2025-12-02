from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Crea o actualiza el usuario admin con credenciales por defecto'

    def handle(self, *args, **options):
        User = get_user_model()
        
        username = 'admin'
        email = 'admin@agrotecnica.com'
        password = 'admin123'
        
        try:
            user = User.objects.get(username=username)
            self.stdout.write(self.style.WARNING(f'Usuario "{username}" ya existe'))
            # Actualizar contraseña por si acaso
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Contraseña actualizada para "{username}"'))
        except User.DoesNotExist:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f'Usuario admin creado exitosamente'))
        
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS(f'Usuario: {username}'))
        self.stdout.write(self.style.SUCCESS(f'Contraseña: {password}'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
