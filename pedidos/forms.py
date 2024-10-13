from django import forms
from mesas.models import Mesa
from platos.models import Plato
from .models import Pedido, ItemPedido, PedidoDomicilio, ItemPedidoDomicilio
from pagos.choices import METODO_PAGO_CHOICES

METODO_PAGO_CHOICES = [
    ('Efectivo', 'Efectivo'),
    ('Consignación', 'Consignación'),
    ('Transferencia', 'Transferencia'),
    ('Cheque', 'Cheque'),
    ('Tarjeta crédito', 'Tarjeta crédito'),
    ('Tarjeta débito', 'Tarjeta débito'),
]

IMPUESTO_CHOICES = [
        ('Ninguno', 'Ninguno'),
        ('IVA Exento (0%)', 'IVA Exento (0%)'),
        ('IVA Excluido (0%)', 'IVA Excluido (0%)'),
        ('IVA (5.00%)', 'IVA (5.00%)'),
        ('IVA (19.00%)', 'IVA (19.00%)'),
        ('IVA (8.00%)', 'IVA (8.00%)'),
    ]

DESCUENTOS_CHOICES = [(i, str(i)) for i in range(0, 101, 5)]

class CrearPedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['mesa']  # Solo incluye el campo 'mesa'

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['mesa'].queryset = Mesa.objects.filter(usuario=user, estado='Libre')  # Asegura que solo el usuario logueado esté en el formulario

class CrearPedidoFormDomicilio(forms.ModelForm):
    
    class Meta:
        model = PedidoDomicilio
        fields = ['doc_cliente','nombre_cliente','telefono_cliente','direccion_cliente']  

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Personalización de widgets
        self.fields['doc_cliente'].widget = forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Documento del cliente',
            'maxlength': '20',
        })
        self.fields['nombre_cliente'].widget = forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre del cliente',
        })
        self.fields['telefono_cliente'].widget = forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Teléfono del cliente',
            'type': 'tel',
            'pattern': '[0-9]{10}',
        })
        self.fields['direccion_cliente'].widget = forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Dirección del cliente',
            'rows': 1,
        })

class AgregarPlatoPedidoForm(forms.Form):
    plato = forms.ModelChoiceField(queryset=Plato.objects.none(), widget=forms.Select(attrs={'class': 'form-control'}))
    cantidad = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad','value':1}))
    detalle = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Detalle','value':'-'}))

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        search_term = kwargs.pop('search_term', None)
        super().__init__(*args, **kwargs)
        if user:
            queryset = Plato.objects.filter(usuario=user)
            if search_term:
                queryset = queryset.filter(nombre__icontains=search_term)
            # Ordena el queryset por nombre alfabéticamente
            queryset = queryset.order_by('nombre')
            self.fields['plato'].queryset = queryset

        self.fields['cantidad'].initial = 1
        self.fields['detalle'].initial = '-'

class FinalizarVentaForm(forms.Form):
    tipo_pago = forms.ChoiceField(
        choices=METODO_PAGO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    cedula_cliente = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cédula del Cliente'})
    )
    impuesto = forms.ChoiceField(
        choices=IMPUESTO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    descuento = forms.DecimalField(
        required=False,
        initial=0.00,
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control descuento-field',
            'step': '5',
            'min': '0',
            'maxlength': '5'
        })
    )
    propina = forms.DecimalField(
        required=False,
        initial=0.00,
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control propina-field',
            'step': '5',
            'min': '0',
            'maxlength': '5'
        })
    )

class FinalizarVentaDomicilioForm(forms.Form):
    tipo_pago = forms.ChoiceField(
        choices=METODO_PAGO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    impuesto = forms.ChoiceField(
        choices=IMPUESTO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    descuento = forms.DecimalField(
        required=False,
        initial=0.00,
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control descuento-field',
            'step': '5',
            'min': '0',
            'maxlength': '5'
        })
    )
    propina = forms.DecimalField(
        required=False,
        initial=0.00,
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control propina-field',
            'step': '5',
            'min': '0',
            'maxlength': '5'
        })
    )
    guardar_cliente = forms.BooleanField(required=False, label="Guardar cliente en la base de datos")
    
class EditarPlatoForm(forms.ModelForm):
    class Meta:
        model = ItemPedido
        fields = ['cantidad']

class EditarPlatoDomicilioForm(forms.ModelForm):
    class Meta:
        model = ItemPedidoDomicilio
        fields = ['cantidad']

class EliminarPlatoForm(forms.ModelForm):
    class Meta:
        model = ItemPedido
        fields = []

class EliminarPlatoDomicilioForm(forms.ModelForm):
    class Meta:
        model = ItemPedidoDomicilio
        fields = []
