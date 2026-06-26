from django import forms
from .models import Presupuesto
from apps.categories.models import Categoria
from apps.transactions.constants import CATEGORIAS_AJUSTE_SLUGS


class PresupuestoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        inquilino = kwargs.pop('inquilino', None)
        super().__init__(*args, **kwargs)
        qs = Categoria.objects.all()
        if inquilino:
            qs = qs.filter(inquilino=inquilino)
        self.fields['categoria'].queryset = qs.exclude(
            slug__in=['ingreso-debito', 'ingreso-efectivo', 'pago-tarjeta'] + CATEGORIAS_AJUSTE_SLUGS
        )

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
