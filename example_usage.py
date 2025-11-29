"""Ejemplo de uso del sistema de inventario como módulo."""
from inventory_manager import InventoryService, Producto


def ejemplo_uso_basico():
    """Ejemplo básico de uso del servicio de inventario."""
    # Crear instancia del servicio
    service = InventoryService()
    
    # Agregar algunos productos
    print("Agregando productos...")
    
    service.agregar_producto(
        codigo="PROD001",
        nombre="Laptop Dell",
        categoria="Electrónica",
        cantidad=5,
        precio_unitario=1299.99
    )
    
    service.agregar_producto(
        codigo="PROD002",
        nombre="Mouse Inalámbrico",
        categoria="Periféricos",
        cantidad=20,
        precio_unitario=29.99
    )
    
    service.agregar_producto(
        codigo="PROD003",
        nombre="Teclado Mecánico",
        categoria="Periféricos",
        cantidad=15,
        precio_unitario=89.99
    )
    
    # Obtener todos los productos
    print("\nListando todos los productos:")
    productos = service.obtener_todos_los_productos()
    for producto in productos:
        subtotal = producto.calcular_subtotal()
        print(f"  - {producto.codigo}: {producto.nombre} "
              f"({producto.cantidad} x ${producto.precio_unitario:.2f} = ${subtotal:.2f})")
    
    # Calcular valor total
    total = service.calcular_valor_total()
    print(f"\nValor total del inventario: ${total:,.2f}")
    
    # Actualizar un producto
    print("\nActualizando producto PROD002...")
    service.actualizar_producto(
        codigo_original="PROD002",
        codigo="PROD002",
        nombre="Mouse Inalámbrico Pro",
        categoria="Periféricos",
        cantidad=25,
        precio_unitario=39.99
    )
    
    # Obtener un producto específico
    producto = service.obtener_producto_por_codigo("PROD002")
    if producto:
        print(f"\nProducto actualizado: {producto.nombre} - "
              f"${producto.precio_unitario:.2f}")
    
    # Eliminar un producto
    print("\nEliminando producto PROD003...")
    service.eliminar_producto("PROD003")
    
    # Valor total actualizado
    total_final = service.calcular_valor_total()
    print(f"\nValor total después de cambios: ${total_final:,.2f}")


def ejemplo_uso_modelo():
    """Ejemplo de uso directo del modelo Producto."""
    print("\n" + "="*50)
    print("Ejemplo de uso del modelo Producto:")
    print("="*50)
    
    # Crear producto directamente
    producto = Producto(
        codigo="TEST001",
        nombre="Producto de Prueba",
        categoria="Test",
        cantidad=10,
        precio_unitario=50.0
    )
    
    # Validar producto
    es_valido, mensaje_error = producto.validar()
    if es_valido:
        print(f"✓ Producto válido: {producto.nombre}")
        print(f"  Subtotal: ${producto.calcular_subtotal():.2f}")
    else:
        print(f"✗ Error: {mensaje_error}")
    
    # Convertir a diccionario
    producto_dict = producto.to_dict()
    print(f"\nProducto como diccionario: {producto_dict}")
    
    # Crear desde diccionario
    producto2 = Producto.from_dict(producto_dict)
    print(f"Producto recreado: {producto2.nombre}")


if __name__ == "__main__":
    print("="*50)
    print("Ejemplos de uso del Sistema de Inventario")
    print("="*50)
    
    ejemplo_uso_basico()
    ejemplo_uso_modelo()
    
    print("\n" + "="*50)
    print("¡Ejemplos completados!")
    print("="*50)

