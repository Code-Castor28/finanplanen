from django import forms
from .models import Transferencia


class TransferenciaForm(forms.ModelForm):
    class Meta:
        model = Transferencia
        fields = ['origen', 'destino', 'monto', 'fecha', 'nota']
        widgets = {
            'origen': forms.Select(attrs={'class': 'form-control'}),
            'destino': forms.Select(attrs={'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={
                'placeholder': '0.00', 'step': '0.01',
                'style': 'border:none;background:transparent;flex:1;min-width:0;padding:10px 12px;font-family:inherit;font-size:14px;outline:none'
            }),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nota': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Ej. Transferencia mensual'}),
        }

    def clean(self):
        cleaned = super().clean()
        origen = cleaned.get('origen')
        destino = cleaned.get('destino')
        monto = cleaned.get('monto')
        if origen and destino and origen == destino:
            raise forms.ValidationError('La cuenta de origen y destino deben ser diferentes.')
        if monto is not None and monto <= 0:
            raise forms.ValidationError('El monto debe ser mayor a cero.')
        return cleaned
