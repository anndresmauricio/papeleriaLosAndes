from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

class ContactForm(forms.Form):

    SUBJECT_CHOICES = [
        ('', '(Seleccione una opción)'),
        ('Solicitud de cotización', 'Solicitud de cotización'),
        ('Estado del pedido, facturación o devoluciones', 'Estado del pedido, facturación o devoluciones'),
        ('Sugerencias, reclamos o pagos', 'Sugerencias, reclamos o pagos'),
        ('Otro', 'Otro (especificar)'),
    ]

    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.ChoiceField(choices=SUBJECT_CHOICES)
    message = forms.CharField(widget=forms.Textarea)

    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        if subject == '':
            raise forms.ValidationError('Por favor selecciona un asunto válido.')
        return subject

class CheckoutForm(forms.Form):
    first_name = forms.CharField(label='Nombres', max_length=100)
    last_name = forms.CharField(label='Apellidos', max_length=100)
    cc = forms.CharField(label='Documento de identidad', max_length=100)
    city = forms.CharField(label='Ciudad', max_length=100)
    address = forms.CharField(label='Dirección', max_length=255)
    email = forms.EmailField(label='Correo electrónico')
    telephone = forms.CharField(label='Teléfono', max_length=15)