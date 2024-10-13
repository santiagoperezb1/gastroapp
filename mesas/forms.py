from django import forms
from .models import Mesa

OPCIONES_NUMEROS = [(str(i), str(i)) for i in range(1, 101)] 
OPCIONES_NUMEROS_CAPACIDAD = [(str(i), str(i)) for i in range(1, 21)] 

class MesaForm(forms.ModelForm):
    class Meta:
        model = Mesa
        fields = ['numero', 'capacidad', 'estado']
        widgets = {
            'numero': forms.Select(choices=OPCIONES_NUMEROS, attrs={'class': 'form-control'}),
            'capacidad': forms.Select(choices=OPCIONES_NUMEROS_CAPACIDAD, attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }
