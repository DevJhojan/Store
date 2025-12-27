# Sistema de Gestión de Ventas - Store

Sistema completo de gestión de ventas con interfaz gráfica desarrollado con Python y tkinter, siguiendo principios de Clean Architecture. Incluye gestión de inventarios, ventas, clientes y cierre de caja con almacenamiento local.

## Características

- ✨ Interfaz gráfica moderna con tema dark y acentos rojos
- 📦 **Gestión de Inventarios**: Administración completa de productos (CRUD), control de stock y precios
- 💰 **Gestión de Ventas**: Registro de ventas con actualización automática de inventario, gestión de clientes y gastos
- 💵 **Cierre de Caja**: Consulta y análisis de ventas con filtros avanzados por fecha, cliente y producto
- 📄 **Generación de Facturas**: Creación automática de facturas en formato PDF
- 💾 **Almacenamiento Local**: Persistencia de datos con SQLite (sin dependencias de servidor)
- 🧮 Cálculo automático del valor total del inventario y totales de ventas
- 🏗️ Arquitectura modular y mantenible
- 🔗 Acceso directo al repositorio de GitHub desde la aplicación

## Estructura del Proyecto

```
app/
├── __init__.py              # Paquete principal
├── main_window.py           # Ventana principal del sistema
├── config/                  # Configuración
│   ├── __init__.py
│   └── settings.py          # Settings y paleta de colores
├── domain/                  # Modelos de dominio compartidos
│   ├── __init__.py
│   └── models.py            # Modelos base
├── inventory/               # Módulo de Inventarios
│   ├── domain/              # Modelos de inventario
│   ├── repository/          # Repositorio de productos
│   ├── services/            # Servicios de inventario
│   └── ui/                  # Interfaz de inventario
│       └── views.py
├── sales/                   # Módulo de Ventas
│   ├── domain/              # Modelos de ventas, clientes
│   ├── repository/          # Repositorios de ventas, clientes, gastos
│   ├── services/            # Servicios de ventas
│   └── ui/                  # Interfaz de ventas
│       ├── views.py
│       └── pdf_generator.py # Generador de facturas PDF
├── cash_closure/            # Módulo de Cierre de Caja
│   ├── repository/          # Repositorio de consultas
│   ├── services/            # Servicios de cierre
│   └── ui/                  # Interfaz de cierre
│       └── views.py
├── repository/              # Repositorios compartidos
│   ├── __init__.py
│   └── product_repository.py
├── services/                # Servicios compartidos
│   ├── __init__.py
│   └── inventory_service.py
├── ui/                      # Componentes UI compartidos
│   ├── __init__.py
│   ├── styles.py            # Gestor de estilos
│   └── views.py             # Vistas compartidas
└── utils/                   # Utilidades
    ├── __init__.py
    └── validators.py        # Validadores de campos
```

## Instalación

### Como módulo instalable

```bash
pip install -e .
```

### Uso directo

```bash
python main.py
```

## Uso

### Ejecutar la aplicación

```bash
python main.py
```

La aplicación se abrirá con una ventana principal desde la cual podrás acceder a los diferentes módulos:

- **📦 Gestión de Inventarios**: Administra productos, stock y precios
- **💰 Gestión de Ventas**: Registra ventas, gestiona clientes y genera facturas
- **💵 Cierre de Caja**: Consulta y analiza todas las ventas registradas

### Módulos Principales

#### Gestión de Inventarios
- Agregar, editar y eliminar productos
- Control de stock y precios
- Búsqueda y filtrado de productos
- Cálculo automático del valor total del inventario

#### Gestión de Ventas
- Registro de ventas con múltiples productos
- Actualización automática del inventario al realizar ventas
- Gestión de clientes
- Registro de gastos
- Generación de facturas en PDF

#### Cierre de Caja
- Consulta de todas las ventas registradas
- Filtros avanzados por fecha, cliente y producto
- Análisis de ventas y totales
- Exportación de datos

### Uso programático

```python
from app import (
    InventoryService, 
    Producto,
    MainWindow,
    InventoryGUI,
    SalesGUI,
    CashClosureGUI
)

# Crear servicio de inventario
service = InventoryService()

# Agregar producto
service.agregar_producto(
    codigo="PROD001",
    nombre="Producto de Ejemplo",
    categoria="Categoría",
    cantidad=10,
    precio_unitario=99.99
)

# Obtener todos los productos
productos = service.obtener_todos_los_productos()

# Calcular valor total
total = service.calcular_valor_total()
```

## Arquitectura

El proyecto sigue los principios de **Clean Architecture**:

- **Domain**: Modelos de negocio independientes
- **Repository**: Abstracción del acceso a datos
- **Services**: Lógica de negocio
- **UI**: Capa de presentación desacoplada

## Requisitos

- Python 3.8+
- tkinter (incluido en la mayoría de distribuciones de Python)
- sqlite3 (incluido en Python estándar)

## Desarrollo

### Estructura de módulos

- **Domain**: Contiene los modelos de datos (Producto, Venta, Cliente, etc.)
- **Repository**: Maneja el acceso a las bases de datos SQLite locales
- **Services**: Contiene la lógica de negocio (validaciones, operaciones CRUD, cálculos)
- **UI**: Interfaz gráfica con tkinter, organizada por módulos
- **Config**: Configuración centralizada (colores, fuentes, settings)
- **Utils**: Utilidades reutilizables (validadores, generadores de PDF)

### Almacenamiento Local

El sistema utiliza bases de datos SQLite locales para el almacenamiento:
- `inventario.db`: Base de datos de productos e inventario
- `Ventas.DB`: Base de datos de ventas, clientes y gastos

Todos los datos se almacenan localmente sin necesidad de conexión a servidor externo.

## Licencia

MIT License

