from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

# Create your models here.
class Product(models.Model):
    item = models.IntegerField()
    imagen = models.ImageField(null=True, blank=True)
    articulo = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)
    impuesto = models.CharField(max_length=100)
    costo = models.IntegerField()
    precio = models.IntegerField()
    ubicacion = models.CharField(max_length=100)
    cantidad = models.IntegerField()
    medida = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.descripcion + ' - ' + self.articulo


class VendedorGroup(Group):
    class Meta:
        verbose_name = 'Vendedor'
        verbose_name_plural = 'Vendedores'

    def __str__(self):
        return 'Vendedor'