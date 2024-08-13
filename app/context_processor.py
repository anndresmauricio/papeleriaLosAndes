def total_carrito(request):
    total = 0
    if "carrito" in request.session:
        carrito = request.session["carrito"]
        for producto_id, producto_info in carrito.items():
            total += producto_info["acumulado"]
    return {"total_carrito": total}

def total_pago(request):
    total = 0
    if "carrito" in request.session:
        carrito = request.session["carrito"]
        for producto_id, producto_info in carrito.items():
            total += producto_info["acumulado"]
    return total