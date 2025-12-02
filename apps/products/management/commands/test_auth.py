from django.core.management.base import BaseCommand
from django.contrib.auth import authenticate, get_user_model


class Command(BaseCommand):
    help = 'Diagnostica problemas de autenticación'

    def handle(self, *args, **options):
        User = get_user_model()
        
        username = 'admin'
        password = 'admin123'
        
        self.stdout.write(self.style.WARNING('=== DIAGNÓSTICO DE AUTENTICACIÓN ==='))
        
        # 1. Verificar que el usuario existe
        try:
            user = User.objects.get(username=username)
            self.stdout.write(self.style.SUCCESS(f'✓ Usuario encontrado: {user.username}'))
            self.stdout.write(f'  - ID: {user.id}')
            self.stdout.write(f'  - Email: {user.email}')
            self.stdout.write(f'  - is_active: {user.is_active}')
            self.stdout.write(f'  - is_staff: {user.is_staff}')
            self.stdout.write(f'  - is_superuser: {user.is_superuser}')
            self.stdout.write(f'  - role: {user.role}')
            self.stdout.write(f'  - password hash: {user.password[:20]}...')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'✗ Usuario "{username}" NO existe'))
            return
        
        # 2. Verificar la contraseña directamente
        if user.check_password(password):
            self.stdout.write(self.style.SUCCESS(f'✓ check_password() funciona correctamente'))
        else:
            self.stdout.write(self.style.ERROR(f'✗ check_password() FALLÓ'))
            self.stdout.write(self.style.ERROR(f'  La contraseña "{password}" no coincide'))
            return
        
        # 3. Probar authenticate()
        auth_user = authenticate(username=username, password=password)
        if auth_user is not None:
            self.stdout.write(self.style.SUCCESS(f'✓ authenticate() funciona correctamente'))
            self.stdout.write(f'  - Usuario autenticado: {auth_user.username}')
        else:
            self.stdout.write(self.style.ERROR(f'✗ authenticate() FALLÓ'))
            self.stdout.write(self.style.ERROR(f'  Posibles causas:'))
            self.stdout.write(self.style.ERROR(f'    1. Backend de autenticación no configurado'))
            self.stdout.write(self.style.ERROR(f'    2. Usuario no activo (is_active=False)'))
            self.stdout.write(self.style.ERROR(f'    3. Problema con AUTH_USER_MODEL'))
            return
        
        # 4. Verificar configuración de Django
        from django.conf import settings
        self.stdout.write(self.style.WARNING('\n=== CONFIGURACIÓN ==='))
        self.stdout.write(f'  - AUTH_USER_MODEL: {settings.AUTH_USER_MODEL}')
        self.stdout.write(f'  - DEBUG: {settings.DEBUG}')
        self.stdout.write(f'  - ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
        
        if hasattr(settings, 'AUTHENTICATION_BACKENDS'):
            self.stdout.write(f'  - AUTHENTICATION_BACKENDS: {settings.AUTHENTICATION_BACKENDS}')
        else:
            self.stdout.write(f'  - AUTHENTICATION_BACKENDS: (default)')
        
        self.stdout.write(self.style.SUCCESS('\n✓ TODOS LOS TESTS PASARON'))
        self.stdout.write(self.style.SUCCESS('El login debería funcionar correctamente'))
