from .models import Product


class Carrito:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        carrito = self.session.get("carrito")
        if not carrito:
            self.session["carrito"] = {}
            self.carrito = self.session["carrito"]
        else:
            self.carrito = carrito

    def agregar(self, producto):
        id = str(producto.id)
        precio_sin_iva = producto.precio
        precio_con_iva = precio_sin_iva * 1.19
        if id not in self.carrito.keys():
            self.carrito[id] = {
                "producto_id": producto.id,
                "articulo": producto.articulo,
                "impuesto": producto.impuesto,
                "precio": precio_sin_iva,
                "acumulado": precio_con_iva,
                "cantidad": 1,
            }
        else:
            self.carrito[id]["cantidad"] += 1
            self.carrito[id]["acumulado"] += precio_con_iva
            self.carrito[id]["precio"] += precio_sin_iva
        self.guardar_carrito()

    def get_productos(self):
        # Obtener los IDs de los productos en el carrito
        ids_productos = [item['producto_id'] for item in self.carrito.values()]
        # Obtener los objetos Producto correspondientes a los IDs
        productos = Product.objects.filter(id__in=ids_productos)
        # Ordenar los productos según el orden en que aparecen en el carrito
        productos_en_carrito = [productos.get(id=id_producto) for id_producto in ids_productos]
        return productos_en_carrito

    def get_total_acumulado(self):
        # Calcular el total acumulado dentro de la clase Carrito
        total_acumulado = sum(item['acumulado'] for item in self.carrito.values())
        return total_acumulado

    def get_total_sin_iva(self):
        total_sin_iva = sum(item['precio'] * item['cantidad'] for item in self.carrito.values())
        return total_sin_iva

    def guardar_carrito(self):
        self.session["carrito"] = self.carrito
        self.session.modified = True

    def eliminar(self, producto):
        id = str(producto.id)
        if id in self.carrito:
            del self.carrito[id]
            self.guardar_carrito()

    def restar(self, producto):
        id = str(producto.id)
        if id in self.carrito.keys():
            self.carrito[id]["cantidad"] -= 1
            self.carrito[id]["acumulado"] -= producto.precio * 1.19
            if self.carrito[id]["cantidad"] <= 0:
                self.eliminar(producto)
            self.guardar_carrito()

    def limpiar(self):
        self.session["carrito"] = {}
        self.session.modified = True

    def listado_productos(self):
        ids_productos = [item['producto_id'] for item in self.carrito.values()]
        productos = Product.objects.filter(id__in=ids_productos)
        productos_en_carrito = []
        for id_producto in ids_productos:
            producto = productos.get(id=id_producto)
            producto_info = {
                'name': producto.articulo,
                'quantity': self.carrito[str(id_producto)]['cantidad'],
                'price': producto.precio,
            }
            productos_en_carrito.append(producto_info)
        return productos_en_carrito

    def actualizar_cantidad(self, producto, cantidad):
        id = str(producto.id)
        if id in self.carrito.keys():
            precio_sin_iva = producto.precio
            precio_con_iva = precio_sin_iva * 1.19
            diferencia_cantidad = cantidad - self.carrito[id]['cantidad']
            self.carrito[id]['cantidad'] = cantidad
            self.carrito[id]['acumulado'] += diferencia_cantidad * precio_con_iva
            self.carrito[id]['precio'] += diferencia_cantidad * precio_sin_iva
            self.guardar_carrito()