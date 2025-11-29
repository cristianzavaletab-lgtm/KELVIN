"""
Management command to seed database with sample data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.products.models import Category, Product
from apps.suppliers.models import Supplier
from apps.customers.models import Customer
from decimal import Decimal
from datetime import date, timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with sample data'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')
        
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@agrotecnica.com',
                password='admin123',
                first_name='Administrador',
                last_name='Sistema',
                role='ADMIN'
            )
            self.stdout.write(self.style.SUCCESS('✓ Admin user created'))
        
        # Create vendedor user
        if not User.objects.filter(username='vendedor').exists():
            User.objects.create_user(
                username='vendedor',
                email='vendedor@agrotecnica.com',
                password='vendedor123',
                first_name='Juan',
                last_name='Pérez',
                role='VENDEDOR'
            )
            self.stdout.write(self.style.SUCCESS('✓ Vendedor user created'))
        
        # Create suppliers
        suppliers_data = [
            {'name': 'Distribuidora Agrícola SAC', 'ruc': '20123456789', 'phone': '987654321', 'address': 'Av. Agricultura 123'},
            {'name': 'Fertilizantes del Norte EIRL', 'ruc': '20987654321', 'phone': '987654322', 'address': 'Jr. Comercio 456'},
            {'name': 'Semillas Premium SAC', 'ruc': '20456789123', 'phone': '987654323', 'address': 'Av. Principal 789'},
        ]
        
        for supplier_data in suppliers_data:
            Supplier.objects.get_or_create(
                ruc=supplier_data['ruc'],
                defaults=supplier_data
            )
        self.stdout.write(self.style.SUCCESS(f'✓ {len(suppliers_data)} suppliers created'))
        
        # Create categories
        categories_data = [
            {'name': 'Fertilizantes', 'icon': 'bi-droplet', 'description': 'Fertilizantes y abonos'},
            {'name': 'Semillas', 'icon': 'bi-flower1', 'description': 'Semillas certificadas'},
            {'name': 'Herramientas', 'icon': 'bi-tools', 'description': 'Herramientas agrícolas'},
            {'name': 'Pesticidas', 'icon': 'bi-bug', 'description': 'Control de plagas'},
            {'name': 'Equipos', 'icon': 'bi-gear', 'description': 'Equipos y maquinaria'},
        ]
        
        for cat_data in categories_data:
            Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
        self.stdout.write(self.style.SUCCESS(f'✓ {len(categories_data)} categories created'))
        
        # Create products
        supplier = Supplier.objects.first()
        categories = Category.objects.all()
        
        products_data = [
            {'name': 'Fertilizante NPK 20-20-20', 'category': categories[0], 'presentation': '50kg', 'purchase_price': 80, 'sale_price': 120, 'stock': 50},
            {'name': 'Urea Granulada', 'category': categories[0], 'presentation': '50kg', 'purchase_price': 70, 'sale_price': 100, 'stock': 30},
            {'name': 'Semilla de Maíz Híbrido', 'category': categories[1], 'presentation': '20kg', 'purchase_price': 150, 'sale_price': 200, 'stock': 25},
            {'name': 'Semilla de Arroz', 'category': categories[1], 'presentation': '25kg', 'purchase_price': 100, 'sale_price': 140, 'stock': 40},
            {'name': 'Machete 18"', 'category': categories[2], 'presentation': 'Unidad', 'purchase_price': 15, 'sale_price': 25, 'stock': 60},
            {'name': 'Pala Cuadrada', 'category': categories[2], 'presentation': 'Unidad', 'purchase_price': 20, 'sale_price': 35, 'stock': 45},
            {'name': 'Insecticida Cipermetrina', 'category': categories[3], 'presentation': '1L', 'purchase_price': 30, 'sale_price': 50, 'stock': 35},
            {'name': 'Fungicida Mancozeb', 'category': categories[3], 'presentation': '1kg', 'purchase_price': 25, 'sale_price': 40, 'stock': 28},
            {'name': 'Mochila Fumigadora 20L', 'category': categories[4], 'presentation': 'Unidad', 'purchase_price': 80, 'sale_price': 120, 'stock': 15},
            {'name': 'Rastrillo Metálico', 'category': categories[2], 'presentation': 'Unidad', 'purchase_price': 12, 'sale_price': 20, 'stock': 50},
        ]
        
        for prod_data in products_data:
            if not Product.objects.filter(name=prod_data['name']).exists():
                Product.objects.create(
                    name=prod_data['name'],
                    category=prod_data['category'],
                    presentation=prod_data['presentation'],
                    purchase_price=Decimal(str(prod_data['purchase_price'])),
                    sale_price=Decimal(str(prod_data['sale_price'])),
                    stock=prod_data['stock'],
                    min_stock=10,
                    supplier=supplier,
                    expiration_date=date.today() + timedelta(days=365)
                )
        self.stdout.write(self.style.SUCCESS(f'✓ {len(products_data)} products created'))
        
        # Create customers
        customers_data = [
            {'dni': '12345678', 'name': 'María García López', 'phone': '987654321', 'address': 'Av. Los Pinos 123'},
            {'dni': '87654321', 'name': 'Carlos Rodríguez Pérez', 'phone': '987654322', 'address': 'Jr. Las Flores 456'},
            {'dni': '45678912', 'name': 'Ana Martínez Silva', 'phone': '987654323', 'address': 'Av. Principal 789'},
            {'dni': '78912345', 'name': 'José Fernández Torres', 'phone': '987654324', 'address': 'Jr. Comercio 321'},
            {'dni': '32165498', 'name': 'Rosa Sánchez Vega', 'phone': '987654325', 'address': 'Av. Agricultura 654'},
        ]
        
        for cust_data in customers_data:
            Customer.objects.get_or_create(
                dni=cust_data['dni'],
                defaults=cust_data
            )
        self.stdout.write(self.style.SUCCESS(f'✓ {len(customers_data)} customers created'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully!'))
        self.stdout.write('\nLogin credentials:')
        self.stdout.write('  Admin: username=admin, password=admin123')
        self.stdout.write('  Vendedor: username=vendedor, password=vendedor123')
