# Sistema de Gestión de Inventarios

Sistema completo de gestión de inventarios con interfaz gráfica desarrollado con Python y tkinter, siguiendo principios de Clean Architecture.

## Características

- ✨ Interfaz gráfica moderna con tema dark y acentos rojos
- 📦 Gestión completa de productos (CRUD)
- 💾 Almacenamiento persistente con SQLite
- 🧮 Cálculo automático del valor total del inventario
- 🏗️ Arquitectura modular y mantenible

## Estructura del Proyecto

```
inventory_manager/
├── __init__.py              # Paquete principal
├── config/                  # Configuración
│   ├── __init__.py
│   └── settings.py          # Settings y paleta de colores
├── domain/                  # Modelos de dominio
│   ├── __init__.py
│   └── models.py            # Modelo Producto
├── repository/              # Acceso a datos
│   ├── __init__.py
│   └── product_repository.py # Repositorio SQLite
├── services/                # Lógica de negocio
│   ├── __init__.py
│   └── inventory_service.py # Servicio de inventario
├── ui/                      # Interfaz de usuario
│   ├── __init__.py
│   ├── styles.py            # Gestor de estilos
│   └── views.py             # Vista principal
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

### Uso programático

```python
from inventory_manager import InventoryService, Producto

# Crear servicio
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

- **Domain**: Contiene los modelos de datos (`Producto`)
- **Repository**: Maneja el acceso a la base de datos SQLite
- **Services**: Contiene la lógica de negocio (validaciones, operaciones CRUD)
- **UI**: Interfaz gráfica con tkinter
- **Config**: Configuración centralizada (colores, fuentes, settings)
- **Utils**: Utilidades reutilizables (validadores)

## Licencia

MIT License

