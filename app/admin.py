from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .resources import ProductResource
from .models import Product

# Register your models here.
class ProductAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    readonly_fields = ("created",)
    resource_class = ProductResource

admin.site.register(Product, ProductAdmin)