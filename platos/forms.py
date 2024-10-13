# platos/forms.py
from django import forms
from .models import Plato, Categoria

class PlatoForm(forms.ModelForm):
    class Meta:
        model = Plato
        fields = ['nombre', 'precio','imagen','categoria','detalle']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del plato'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'detalle': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'Describe el plato...', 
                'rows': 5,  # Ajusta el número de filas
                'style': 'resize: none;'  # Evita el redimensionamiento manual
            })
        }
        
    def __init__(self, *args, **kwargs):
        # Extraer el usuario de los argumentos keyword
        user = kwargs.pop('user', None)
        super(PlatoForm, self).__init__(*args, **kwargs)
        
        # Filtrar las categorías basadas en el usuario
        if user is not None:
            self.fields['categoria'].queryset = Categoria.objects.filter(usuario=user)

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la categoría'}),
        }