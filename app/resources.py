import os
from import_export import resources, fields
from django.core.files import File
from django.conf import settings
from .models import Product

class ProductResource(resources.ModelResource):
    articulo = fields.Field(attribute='name', column_name='articulo')
    image_name = fields.Field(attribute='image', column_name='imagen')

    class Meta:
        model = Product
        import_id_fields = ('name',)  # Usamos 'name' como identificador único
        fields = ('name', 'imagen',)

    def before_save_instance(self, instance, using_transactions, dry_run):
        if instance.image:
            image_path = os.path.join(settings.MEDIA_ROOT, 'products', instance.image.name)
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    instance.image.save(instance.image.name, File(f), save=False)