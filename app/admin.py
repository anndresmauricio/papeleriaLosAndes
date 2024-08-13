from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Product

# Register your models here.
class AutorResource(resources.ModelResource):
    class Meta:
        model = Product
class ProductAdmin(ImportExportModelAdmin):
    readonly_fields = ("created",)
    resource_class = AutorResource

admin.site.register(Product, ProductAdmin)