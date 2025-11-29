# AGROTECNICA MIJAEL 🌾

Sistema de Gestión Agropecuaria Mobile-First con PWA (Progressive Web App)

## 📱 Características Principales

- **100% Mobile-First**: Diseñado específicamente para dispositivos móviles
- **PWA Instalable**: Se puede instalar en Android como una aplicación nativa
- **Punto de Venta (POS)**: Sistema de ventas optimizado para celular
- **Gestión Completa**: Productos, ventas, compras, clientes, proveedores
- **Dashboard en Tiempo Real**: KPIs y métricas actualizadas
- **API REST Completa**: Django REST Framework con autenticación por token
- **Modo Oscuro**: Tema claro/oscuro
- **Offline Support**: Funcionalidad básica sin conexión

## 🚀 Tecnologías

- **Backend**: Django 5.0+
- **API**: Django REST Framework
- **Base de Datos**: PostgreSQL (producción) / SQLite (desarrollo)
- **Frontend**: Bootstrap 5 + CSS personalizado
- **Gráficos**: Chart.js
- **Iconos**: Bootstrap Icons
- **PDF**: ReportLab
- **Deployment**: Render.com

## 📋 Requisitos Previos

- Python 3.11+
- pip
- virtualenv (recomendado)

## 🛠️ Instalación Local

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd "AGROTECNICA MIJAEL"
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copiar `.env.example` a `.env` y configurar:

```bash
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Ejecutar migraciones

```bash
python manage.py migrate
```

### 6. Crear superusuario

```bash
python manage.py createsuperuser
```

### 7. Cargar datos de ejemplo (opcional)

```bash
python manage.py seed_data
```

### 8. Ejecutar servidor de desarrollo

```bash
python manage.py runserver
```

Abrir en el navegador: `http://127.0.0.1:8000`

## 📱 Instalación como PWA en Android

1. Abrir la aplicación en Chrome para Android
2. Tocar el menú (⋮) > "Agregar a pantalla de inicio"
3. La aplicación se instalará como una app nativa

## 🗂️ Estructura del Proyecto

```
AGROTECNICA MIJAEL/
├── config/                 # Configuración Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/                   # Aplicaciones Django
│   ├── accounts/          # Autenticación y usuarios
│   ├── products/          # Productos y categorías
│   ├── sales/             # Ventas y POS
│   ├── purchases/         # Compras e inventario
│   ├── customers/         # Clientes
│   ├── suppliers/         # Proveedores
│   ├── reports/           # Dashboard y reportes
│   └── api/               # API REST
├── static/                # Archivos estáticos
│   ├── css/              # Estilos
│   ├── js/               # JavaScript
│   ├── icons/            # Iconos PWA
│   └── manifest.json     # Manifest PWA
├── templates/             # Templates HTML
├── media/                 # Archivos subidos
├── sw.js                  # Service Worker
├── manage.py
├── requirements.txt
└── README.md
```

## 👥 Roles de Usuario

### Administrador
- Acceso completo al sistema
- Gestión de usuarios
- Reportes avanzados
- Configuración del sistema

### Vendedor
- Punto de Venta (POS)
- Consulta de productos
- Registro de ventas
- Consulta de clientes

## 🔌 API REST

### Autenticación

Obtener token:
```bash
POST /api/auth/token/
{
  "username": "usuario",
  "password": "contraseña"
}
```

Usar token en headers:
```
Authorization: Token <tu-token>
```

### Endpoints Disponibles

- `GET /api/products/` - Listar productos
- `POST /api/products/` - Crear producto
- `GET /api/products/{id}/` - Detalle de producto
- `PUT /api/products/{id}/` - Actualizar producto
- `DELETE /api/products/{id}/` - Eliminar producto

- `GET /api/categories/` - Listar categorías
- `GET /api/customers/` - Listar clientes
- `GET /api/suppliers/` - Listar proveedores
- `GET /api/sales/` - Listar ventas

Todos los endpoints soportan:
- **Búsqueda**: `?search=término`
- **Ordenamiento**: `?ordering=-created_at`
- **Paginación**: `?page=1`

## 🚀 Deployment en Render

### 1. Crear cuenta en Render.com

### 2. Crear nuevo Web Service

- Conectar repositorio Git
- Build Command: `./build.sh`
- Start Command: `gunicorn config.wsgi:application`

### 3. Configurar variables de entorno

```
SECRET_KEY=<generar-clave-segura>
DEBUG=False
ALLOWED_HOSTS=.onrender.com
CSRF_TRUSTED_ORIGINS=https://tu-app.onrender.com
```

### 4. Crear base de datos PostgreSQL

En Render Dashboard:
- New > PostgreSQL
- Conectar con el Web Service

### 5. Deploy

El deploy se ejecutará automáticamente.

## 📊 Módulos del Sistema

### 1. Dashboard
- Ventas del día y del mes
- Productos con stock bajo
- Productos por vencer
- Top productos más vendidos
- Ventas recientes

### 2. Punto de Venta (POS)
- Búsqueda rápida de productos
- Carrito de compras dinámico
- Cálculo automático de totales
- IGV (18%)
- Descuentos
- Múltiples métodos de pago
- Actualización automática de stock

### 3. Productos
- CRUD completo
- Categorías
- Imágenes
- Control de stock
- Alertas de stock bajo
- Fechas de vencimiento
- Precios de compra/venta

### 4. Ventas
- Historial de ventas
- Detalles de venta
- Filtros y búsqueda
- Exportación a PDF/Excel

### 5. Compras
- Registro de compras
- Foto de factura
- Aumento automático de stock
- Historial

### 6. Clientes
- Registro con DNI
- Historial de compras
- Búsqueda rápida

### 7. Proveedores
- Registro con RUC
- Historial de compras

## 🔒 Seguridad

- Autenticación requerida para todas las vistas
- CSRF protection habilitado
- Validación de datos en formularios
- Sanitización de inputs
- SSL/HTTPS en producción
- Permisos por rol

## 📝 Comandos Útiles

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recolectar archivos estáticos
python manage.py collectstatic

# Cargar datos de ejemplo
python manage.py seed_data

# Ejecutar servidor
python manage.py runserver

# Ejecutar tests
python manage.py test
```

## 🐛 Troubleshooting

### Error: No module named 'apps'
```bash
# Asegúrate de estar en el directorio correcto
cd "AGROTECNICA MIJAEL"
```

### Error de base de datos
```bash
# Eliminar base de datos y recrear
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Archivos estáticos no cargan
```bash
python manage.py collectstatic --no-input
```

## 📄 Licencia

Este proyecto es privado y confidencial.

## 👨‍💻 Soporte

Para soporte técnico, contactar al administrador del sistema.

---

**AGROTECNICA MIJAEL** - Sistema de Gestión Agropecuaria Mobile-First
Versión 1.0.0
