from django import forms
from ventas.models import Compra, CompraDomicilio

class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['tipo_pago', 'cedula_cliente', 'impuesto']  # Campos que deseas editar

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Puedes agregar aquí estilos adicionales o configuraciones para el formulario
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class CompraDomicilioForm(forms.ModelForm):
    class Meta:
        model = CompraDomicilio
        fields = ['tipo_pago','nombre_cliente','telefono_cliente', 'cedula_cliente', 'impuesto']  # Campos que deseas editar

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Puedes agregar aquí estilos adicionales o configuraciones para el formulario
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})