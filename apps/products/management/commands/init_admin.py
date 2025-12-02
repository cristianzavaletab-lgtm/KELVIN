from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model, authenticate


class Command(BaseCommand):
    help = 'Crea o actualiza el usuario admin con credenciales por defecto'

    def handle(self, *args, **options):
        User = get_user_model()
        
        username = 'admin'
        email = 'admin@agrotecnica.com'
        password = 'admin123'
        
        try:
            # Intentar obtener el usuario existente
            user = User.objects.get(username=username)
            self.stdout.write(self.style.WARNING(f'Usuario "{username}" ya existe - actualizando...'))
            
            # Actualizar todos los campos importantes
            user.email = email
            user.first_name = 'Administrador'
            user.last_name = 'Sistema'
            user.set_password(password)
            user.role = 'ADMIN'
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.save()
            
            self.stdout.write(self.style.SUCCESS(f'✓ Usuario admin actualizado exitosamente'))
            
        except User.DoesNotExist:
            # Crear nuevo usuario si no existe
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name='Administrador',
                last_name='Sistema'
            )
            
            # Asegurar que tenga el rol correcto
            user.role = 'ADMIN'
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.save()
            
            self.stdout.write(self.style.SUCCESS(f'✓ Usuario admin creado exitosamente'))
        
        # Verificar que la contraseña funciona
        test_user = authenticate(username=username, password=password)
        if test_user is not None:
            self.stdout.write(self.style.SUCCESS(f'✓ Autenticación verificada correctamente'))
        else:
            self.stdout.write(self.style.ERROR(f'✗ ERROR: La autenticación falló'))
            self.stdout.write(self.style.ERROR(f'   Verifica la configuración de AUTH_USER_MODEL'))
        
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS(f'  Usuario: {username}'))
        self.stdout.write(self.style.SUCCESS(f'  Contraseña: {password}'))
        self.stdout.write(self.style.SUCCESS(f'  Email: {email}'))
        self.stdout.write(self.style.SUCCESS(f'  ID: {user.id}'))
        self.stdout.write(self.style.SUCCESS(f'  is_active: {user.is_active}'))
        self.stdout.write(self.style.SUCCESS(f'  is_staff: {user.is_staff}'))
        self.stdout.write(self.style.SUCCESS(f'  is_superuser: {user.is_superuser}'))
        self.stdout.write(self.style.SUCCESS(f'  role: {user.role}'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
