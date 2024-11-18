import os
import tempfile
from import_export import resources, fields
from django.core.files import File
from django.conf import settings
from import_export.tmp_storages import CacheStorage

from .models import Product

class ProductResource(resources.ModelResource):
    item = fields.Field(attribute='item', column_name='item')
    image_name = fields.Field(attribute='imagen', column_name='imagen')

    class Meta:
        model = Product
        tmp_storage_class = CacheStorage
        import_id_fields = ('item',)
        fields = ('articulo', 'descripcion', 'categoria', 'precio', 'cantidad')
        skip_unchanged = True
        report_skipped = True

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
        # Verifica si ya hay una imagen
        if instance.imagen and instance.imagen.name:
            return

        # Comprueba si se proporciona una nueva imagen
        if hasattr(instance, 'imagen') and instance.imagen:
            image_path = os.path.join(settings.MEDIA_ROOT, instance.imagen.name)
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    instance.imagen.save(instance.imagen.name, File(f), save=False)

    def write_to_tmp_storage(self, import_file, **kwargs):
        """
        Usa un archivo temporal en disco para manejar los datos importados.
        """
        # Crea un archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp_file:
            tmp_file.write(import_file.read())  # Escribe los datos en el archivo temporal
            tmp_file_path = tmp_file.name  # Guarda la ruta del archivo temporal
            tmp_file.close()

        # Devuelve la ruta del archivo temporal
        print(f"Archivo temporal creado en: {tmp_file_path}")
        return tmp_file_path