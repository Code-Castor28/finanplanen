from django import forms
from .constants import CATEGORIAS_INGRESO_SLUGS, CATEGORIAS_AJUSTE_SLUGS
from .models import Ingreso, Gasto
from apps.categories.models import Categoria


class IngresoForm(forms.ModelForm):
    class Meta:
        model = Ingreso
        fields = ['cuenta', 'monto', 'fecha', 'nota', 'comprobante']
        widgets = {
            'cuenta': forms.Select(attrs={'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={
                'placeholder': '0.00', 'step': '0.01',
                'style': 'border:none;background:transparent;flex:1;min-width:0;padding:10px 12px;font-family:inherit;font-size:14px;outline:none'
            }),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nota': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Ej. Pago de nómina'}),
            'comprobante': forms.FileInput(attrs={'class': 'form-control'}),
        }


class GastoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        inquilino = kwargs.pop('inquilino', None)
        super().__init__(*args, **kwargs)
        qs = Categoria.objects.all()
        if inquilino:
            qs = qs.filter(inquilino=inquilino)
        self.fields['categoria'].queryset = qs.exclude(
            slug__in=CATEGORIAS_INGRESO_SLUGS + CATEGORIAS_AJUSTE_SLUGS
        )

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
