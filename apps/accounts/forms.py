from django import forms
from .models import Cuenta


class CuentaForm(forms.ModelForm):
    class Meta:
        model = Cuenta
        fields = [
            'nombre', 'tipo', 'color', 'icono',
            'balance', 'emisor', 'ultimos_digitos',
            'dia_corte', 'dia_pago', 'vencimiento', 'activo',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Ej. Visa Signature'}),
            'balance': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01', 'style': 'border:none;background:transparent;flex:1;min-width:0;padding:10px 12px;font-family:inherit;font-size:14px;outline:none'}),
            'emisor': forms.TextInput(attrs={'placeholder': 'Ej. Banco Popular'}),
            'ultimos_digitos': forms.TextInput(attrs={'placeholder': '4412', 'maxlength': '4'}),
            'dia_corte': forms.TextInput(attrs={'placeholder': 'Día 12'}),
            'dia_pago': forms.TextInput(attrs={'placeholder': 'Día 26'}),
            'vencimiento': forms.TextInput(attrs={'placeholder': '08/26'}),
        }

    def __init__(self, *args, **kwargs):
        tipo_filter = kwargs.pop('tipo_filter', None)
        super().__init__(*args, **kwargs)
        if tipo_filter:
            choices = [c for c in self.fields['tipo'].choices if c[0] == tipo_filter or (tipo_filter == 'tarjeta' and c[0] in ('credito', 'debito'))]
            self.fields['tipo'].choices = choices
