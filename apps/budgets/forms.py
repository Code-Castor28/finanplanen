from django import forms
from .models import Presupuesto


class PresupuestoForm(forms.ModelForm):
    class Meta:
        model = Presupuesto
        fields = ['categoria', 'monto_limite', 'mes', 'año']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'monto_limite': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'min': '0.01',
                'placeholder': '0.00'
            }),
            'mes': forms.NumberInput(attrs={
                'class': 'form-control', 'min': '1', 'max': '12'
            }),
            'año': forms.NumberInput(attrs={
                'class': 'form-control', 'min': '2020', 'max': '2099'
            }),
        }
