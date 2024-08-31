"""
URL configuration for firstapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('confirm/', views.comfirm_page, name='confirm'),
    path('confirm-email/<int:user_id>/', views.confirm_email, name='confirm_email'),
    path('logout/', views.signout, name='logout'),
    path('signin/', views.signin, name='signin'),
    path('product/', views.product, name='product'),
    path('cart/', views.carro, name='cart'),
    path('cart/agregar/<int:producto_id>/', views.agregar_producto, name="add"),
    path('cart/eliminar/<int:producto_id>/', views.eliminar_producto, name="delete"),
    path('cart/restar/<int:producto_id>/', views.restar_producto, name="rest"),
    path('cart/limpiar/', views.limpiar_carrito, name="clean"),
    path('help/', views.ayuda, name='help'),
    path('accounts/', include('allauth.urls')),
    path('accounts/profile/', views.index, name='index'),
    path('payment-success/', views.payment_successful, name='payment-success'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),
    path('crear-vendedor/', views.crear_vendedor, name='crear-vendedor'),
    path('vendedor_dashboard/', views.vendedor_dashboard, name='vendedor_dashboard'),
    path('thank-you/', views.contact_thanks, name='thank_you'),
    path('thank_you_payment/', views.contact_thanks_p, name='thank_you_payment'),
    path('actualizar_producto/<int:product_id>/', views.actualizar_producto, name='actualizar'),
    path('us/', views.nosotros_view, name='us'),
    path('operation/', views.operacion_view, name='operation'),
    path('brand/', views.marcas_view, name='brand'),
    path('contact/', views.contactos_view, name='contact'),
    path('process-payment/', views.process_payment, name='process_payment'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)