import hashlib
import hmac
import uuid
from random import sample
import re
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .carrito import Carrito
from .forms import ProductForm, CheckoutForm
from .models import Product
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import user_passes_test
from .forms import ContactForm
from django.core.mail import send_mail

def is_vendedor(request):
    """
    Verifica si el usuario actual es un vendedor.
    Devuelve True si es vendedor, False en caso contrario.
    """
    return {
        'is_vendedor': request.user.groups.filter(name='Vendedor').exists()
    }

# Create your views here.
def index(request):
    productos = Product.objects.all()
    productos_random = sample(list(productos), 6)
    return render(request, 'index.html', {'productos_random': productos_random})


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    elif request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Verificar si el campo de usuario está vacío
        if not username:
            return render(request, 'signup.html', {
                'form': UserCreationForm,
                "error": 'El campo de usuario no puede estar vacío'
            })

        # Verificar si la contraseña está vacía o no coincide
        if not password1 or password1 != password2:
            return render(request, 'signup.html', {
                'form': UserCreationForm,
                "error": 'Las contraseñas no coinciden o están vacías'
            })

        # Verificar si la contraseña cumple con los requisitos
        if len(password1) < 8 or not re.search(r'\d', password1) or not re.search(r'[!@#$%^&*()\-_=+{};:,<.>]',
                                                                                  password1):
            return render(request, 'signup.html', {
                'form': UserCreationForm,
                "error": 'La contraseña debe tener al menos 8 caracteres, contener al menos un número y un carácter especial'
            })

        # registrar
        try:
            user = User.objects.create_user(username=username, password=password1)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            user.save()
            login(request, user)
            return redirect('index')
        except IntegrityError:
            return render(request, 'signup.html', {
                'form': UserCreationForm,
                "error": 'Usuario ya existe'
            })


def signout(request):
    logout(request)
    return redirect('index')


def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'El usuario o la contraseña no es la correcta'
            })
        else:
            login(request, user)
            return redirect('index')


def product(request):
    q = request.GET.get('q')
    productos = Product.objects.all().order_by('descripcion')
    categorias = Product.objects.values('categoria').annotate(total=Count('categoria'))
    categoria = request.GET.get('categoria')

    if q:
        productos = productos.filter(descripcion__icontains=q)

    if categoria:  # Aplicar el filtro de categoría si se selecciona una
        productos = productos.filter(categoria=categoria)

    paginator = Paginator(productos, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'producto.html', {'page_obj': page_obj, 'categorias': categorias})


def carro(request):
    productos = Product.objects.all()
    return render(request, 'carro.html', {'productos': productos})


@login_required(login_url='cart')
def agregar_producto(request, producto_id):
    carrito = Carrito(request)
    producto = Product.objects.get(id=producto_id)
    carrito.agregar(producto)
    return redirect("cart")


def eliminar_producto(request, producto_id):
    carrito = Carrito(request)
    producto = Product.objects.get(id=producto_id)
    carrito.eliminar(producto)
    return redirect("cart")

def restar_producto(request, producto_id):
    carrito = Carrito(request)
    producto = Product.objects.get(id=producto_id)
    carrito.restar(producto)
    return redirect("cart")


def limpiar_carrito(request):
    carrito = Carrito(request)
    carrito.limpiar()
    return redirect("cart")


def ayuda(request):

    subject_email_map = {
        'Solicitud de cotización': 'ventas-1@papelerialosandes.com',
        'Estado del pedido, facturación o devoluciones': 'bodega@papelerialosandes.com',
        'Sugerencias, reclamos o pagos': 'asistente.administrativo@papelerialosandes.com',
        'Otro': 'asistente.administrativo@papelerialosandes.com',
    }

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

        to_email = subject_email_map.get(subject, settings.EMAIL_HOST_USER)

        send_mail(
            subject,  # Asunto del correo
            f'Nombre: {name}\nEmail: {email}\n\nMensaje:\n{message}',
            settings.EMAIL_HOST_USER,
            [to_email],
            fail_silently=False,
        )
        return redirect('thank_you')
    else:
        form = ContactForm()

    return render(request, 'ayuda.html', {'form': form})

def contact_thanks(request):
    return render(request, 'thank_you.html')


@csrf_exempt
@login_required(login_url='signin')
def process_payment(request):
    carrito = Carrito(request)
    acumulado = carrito.get_total_acumulado()
    amount = int(acumulado)

    # Generar un identificador único para el pedido usando UUID
    order_id = str(uuid.uuid4())

    # Llave secreta de integración
    secret_key = settings.BOLD_SECRET_KEY

    # Generar el hash de integridad
    data_to_hash = f'{order_id}{amount}COP{secret_key}'
    integrity_signature = hmac.new(
        secret_key.encode('utf-8'),
        data_to_hash.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # URL de redirección después del pago
    redirection_url = request.build_absolute_uri('/payment-success/')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            city = form.cleaned_data['city']
            address = form.cleaned_data['address']
            email = form.cleaned_data['email']

            # Obtén los productos del carrito
            productos = carrito.listado_productos()

            # Construye el mensaje del correo
            productos_list = "\n".join([f"{item['name']} \n Cantidad: {item['quantity']}" for item in productos])
            message = f"Nombres: {first_name}\nApellidos: {last_name}\nCiudad: {city}\nDirección: {address}\nCorreo electrónico: {email}\n\nProductos:\n{productos_list}"

            send_mail(
                f'Nuevo pedido  - ID: {order_id}',  # Asunto del correo
                message,  # Cuerpo del correo
                settings.EMAIL_HOST_USER,  # Desde
                [settings.EMAIL_HOST_USER],  # Para (tu propio correo)
                fail_silently=False,
            )
            return redirect('thank_you')  # Redirige a una página de éxito
    else:
        form = CheckoutForm()

    context = {
        'form': form,
        'order_id': order_id,
        'currency': 'COP',
        'amount': amount,
        'api_key': settings.BOLD_API_KEY,
        'integrity_signature': integrity_signature,
        'redirection_url': redirection_url
    }

    return render(request, 'payment.html', context)

def payment_successful(request):
    return render(request, 'payment-success.html')


@user_passes_test(lambda u: u.is_superuser)
def crear_vendedor(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Verificar si la contraseña coincide
        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden')
            return redirect('crear-vendedor')

        # Crear el usuario
        try:
            user = User.objects.create_user(username=username, password=password1)
            # Agregar el usuario al grupo de vendedores
            group = Group.objects.get(name='Vendedor')
            user.groups.add(group)
            messages.success(request, 'Usuario vendedor creado exitosamente')
            return redirect('crear-vendedor')
        except Exception as e:
            messages.error(request, f'Error al crear usuario vendedor: {e}')
            return redirect('crear-vendedor')

    return render(request, 'crear-vendedor.html')


def vendedor_dashboard(request):

    q = request.GET.get('q')

    # Leer (Read): Obtener todos los productos de la base de datos
    products = Product.objects.all()
    if q:
        products = products.filter(articulo__icontains=q)

    # Crear (Create): Procesar el formulario de creación de un nuevo producto
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vendedor_dashboard')
    else:
        form = ProductForm()

    # Eliminar (Delete): Eliminar un producto existente
    if request.method == 'POST' and 'delete' in request.POST:
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        return redirect('vendedor_dashboard')


    context = {
        'products': products,
        'form': form,
        'search': q,
    }

    return render(request, 'vendedor_dashboard.html', context)

def actualizar_producto(request, product_id):
    # Obtener el producto existente por su ID
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        # Procesar el formulario de actualización del producto
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('vendedor_dashboard')
    else:
        # Mostrar el formulario prellenado con los datos del producto existente
        form = ProductForm(instance=product)

    return render(request, 'actualizar.html', {'form': form})

def nosotros_view(request):
    return render(request, 'nosotros.html')

def operacion_view(request):
    return render(request, 'operation.html')

def marcas_view(request):
    return render(request, 'marcas.html')

def contactos_view(request):
    return render(request, 'contactos.html')