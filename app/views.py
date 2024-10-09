from random import sample
import re
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate, get_backends
from django.db import IntegrityError
from .carrito import Carrito
from .forms import ProductForm, CheckoutForm
from .models import Product
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import user_passes_test
from .forms import ContactForm
from django.core.mail import send_mail
import hashlib
from django.urls import reverse
import random
from django.utils.timezone import now
from firstapp import settings
from .forms import CustomAuthenticationForm


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
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Verificar si el campo de usuario o email están vacío
        if not username or not email:
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
            user = User.objects.create_user(username=username, password=password1, email=email)
            user.is_active = False  # Desactiva la cuenta hasta que se confirme
            user.save()

            send_confirmation_email(request, user)
            return redirect('confirm')
        except IntegrityError:
            return render(request, 'signup.html', {
                'form': UserCreationForm,
                "error": 'Usuario ya existe'
            })


def comfirm_page(request):
    return render(request, 'confirm.html')


def send_confirmation_email(request, user):
    subject = 'Confirma tu cuenta'
    message = f'Por favor, confirma tu cuenta haciendo clic en el siguiente enlace: http://{request.get_host()}/confirm-email/{user.id}/'
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)


def confirm_email(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.is_active = True
    user.save()
    backend = get_backends()[0]
    user.backend = f"{backend.__module__}.{backend.__class__.__name__}"

    login(request, user, backend=user.backend)

    return redirect('index')


def privacy_policy(request):
    return render(request, 'privacy_policy.html')


def signout(request):
    logout(request)
    return redirect('index')


def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        form = CustomAuthenticationForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username_or_email']
            password = form.cleaned_data['password']

            try:
                user = User.objects.get(email=username_or_email)
                username = user.username
            except User.DoesNotExist:
                username = username_or_email

            user = authenticate(request, username=username, password=password)

            if user is None:
                return render(request, 'signin.html', {
                    'form': form,
                    'error': 'El usuario o la contraseña no es la correcta'
                })
            else:
                login(request, user)
                return redirect('index')
        else:
            return render(request, 'signin.html', {
                'form': form,
                'error': 'Por favor, ingresa información válida'
            })


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

@login_required(login_url='cart')
def actualizar_cantidad(request, producto_id):
    if request.method == 'POST':
        nueva_cantidad = int(request.POST.get('cantidad'))
        carrito = Carrito(request)
        producto = Product.objects.get(id=producto_id)
        carrito.actualizar_cantidad(producto, nueva_cantidad)
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

    MIN_MONTO = 100
    MAX_MONTO = 3000000

    if acumulado < MIN_MONTO or acumulado > MAX_MONTO:
        messages.error(request, f"El monto total debe estar entre $ 400.000 - $ 3.000.000 de pesos Colombianos para realizar la compra.")
        return redirect('cart')

    amount = int(acumulado)

    # Generar un identificador único para el pedido usando UUID
    order_id = f"ORD{now().strftime('%Y%m%d')}{random.randint(100, 999)}"

    # Llave secreta de integración
    secret_key = settings.BOLD_SECRET_KEY

    badge = 'COP'
    # Generar el hash de integridad
    data_to_hash = f'{order_id}{amount}{badge}{secret_key}'
    m = hashlib.sha256()
    m.update(data_to_hash.encode('utf-8'))
    integrity_signature = m.hexdigest()

    # URL de redirección después del pago
    redirection_url = request.build_absolute_uri('/payment-success')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Guardar datos del formulario en la sesión
            request.session['form_data'] = form.cleaned_data
            request.session['order_id'] = order_id
            request.session['amount'] = amount
            request.session['integrity_signature'] = integrity_signature
            return redirect('thank_you_payment')
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


@login_required(login_url='signin')
def contact_thanks_p(request):
    order_id = request.session.get('order_id')
    amount = request.session.get('amount')
    integrity_signature = request.session.get('integrity_signature')

    context = {
        'order_id': order_id,
        'currency': 'COP',
        'amount': amount,
        'api_key': settings.BOLD_API_KEY,
        'integrity_signature': integrity_signature,
        'redirection_url': request.build_absolute_uri('/payment-success')
    }

    return render(request, 'thank_you_payment.html', context)


@login_required(login_url='signin')
def payment_successful(request):
    tx_status = request.GET.get('bold-tx-status')

    if tx_status == 'approved':
        # Recuperar datos del formulario desde la sesión
        form_data = request.session.get('form_data')
        order_id = request.session.get('order_id')

        if form_data:
            first_name = form_data['first_name']
            last_name = form_data['last_name']
            cc = form_data['cc']
            city = form_data['city']
            address = form_data['address']
            email = form_data['email']
            telephone = form_data['telephone']

            # Productos
            productos = Carrito(request).listado_productos()
            productos_list = "\n".join([f"{item['name']} \n Cantidad: {item['quantity']} \n Precio: {item['price']}" for item in productos])

            # Enviar correo al cliente
            customer_message = f"Gracias por tu compra, {first_name} {last_name}.\nTu pedido ha sido recibido y está en proceso.\nProductos comprados:\n{productos_list}"
            send_mail(
                'Confirmación de Compra',
                customer_message,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            # Enviar correo al vendedor
            seller_message = f"Nombres: {first_name}\nApellidos: {last_name}\nDocumento de identidad: {cc}\nCiudad: {city}\nDirección: {address}\nCorreo electrónico: {email}\nTeléfono: {telephone}\n\nProductos:\n{productos_list}"

            send_mail(
                f'Nuevo pedido  - ID: {order_id}',
                seller_message,
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_HOST_USER],
                fail_silently=False,
            )

            carrito = Carrito(request)
            carrito.limpiar()

            return render(request, 'payment-success.html')
    else:
        return redirect(reverse('payment_failed'))


def payment_failed(request):
    return render(request, 'payment_failed.html')


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

    products = Product.objects.all().order_by('articulo')
    if q:
        products = products.filter(articulo__icontains=q)

    paginator = Paginator(products, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vendedor_dashboard')
    else:
        form = ProductForm()

    if request.method == 'POST' and 'delete' in request.POST:
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        return redirect('vendedor_dashboard')


    context = {
        'page_obj': page_obj,
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