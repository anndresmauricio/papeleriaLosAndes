import os
from import_export import resources, fields
from django.core.files import File
from django.conf import settings
from .models import Product

class ProductResource(resources.ModelResource):
    item = fields.Field(attribute='item', column_name='item')
    image_name = fields.Field(attribute='imagen', column_name='imagen')

    class Meta:
        model = Product
        import_id_fields = ('item',)
        fields = ('articulo', 'descripcion', 'categoria', 'precio', 'cantidad')
        skip_unchanged = True  # Solo actualiza si algo ha cambiado
        report_skipped = True  # Reporta los saltos

    def before_import_row(self, row, **kwargs):
        row['item'] = str(row['item']).strip().lower()
        super().before_import_row(row, **kwargs)

    def get_instance(self, instance_loader, row):
        item_normalizado = row['item'].strip().lower()
        try:
            return Product.objects.get(item__iexact=item_normalizado)
        except Product.DoesNotExist:
            return None

    def before_save_instance(self, instance, using_transactions, dry_run):
        if instance.imagen:
            image_path = os.path.join(settings.MEDIA_ROOT, instance.imagen.name)
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    instance.imagen.save(instance.imagen.name, File(f), save=False)
