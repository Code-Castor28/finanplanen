from django import forms
from .models import Ingreso, Gasto


class IngresoForm(forms.ModelForm):
    class Meta:
        model = Ingreso
        fields = ['cuenta', 'categoria', 'monto', 'fecha', 'nota', 'comprobante']
        widgets = {
            'cuenta': forms.Select(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={
                'placeholder': '0.00', 'step': '0.01',
                'style': 'border:none;background:transparent;flex:1;min-width:0;padding:10px 12px;font-family:inherit;font-size:14px;outline:none'
            }),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nota': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Ej. Pago de nómina'}),
            'comprobante': forms.FileInput(attrs={'class': 'form-control'}),
        }


class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = ['cuenta', 'categoria', 'monto', 'fecha', 'nota', 'comprobante']
        widgets = {
            'cuenta': forms.Select(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={
                'placeholder': '0.00', 'step': '0.01',
                'style': 'border:none;background:transparent;flex:1;min-width:0;padding:10px 12px;font-family:inherit;font-size:14px;outline:none'
            }),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nota': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Ej. Compra semanal'}),
            'comprobante': forms.FileInput(attrs={'class': 'form-control'}),
        }
