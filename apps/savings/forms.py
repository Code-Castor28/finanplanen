from django import forms
from .models import MetaAhorro, DepositoAhorro
from apps.accounts.models import Cuenta


class MetaAhorroForm(forms.ModelForm):
    class Meta:
        model = MetaAhorro
        fields = ['nombre', 'meta', 'fecha_limite', 'color', 'icono', 'nota']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Viaje a Europa'}),
            'meta': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'min': '0.01',
                'placeholder': '0.00'
            }),
            'fecha_limite': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'color': forms.Select(attrs={'class': 'form-control'}),
            'icono': forms.Select(attrs={'class': 'form-control'}),
            'nota': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Motivo de la meta...'}),
        }


class DepositoAhorroForm(forms.ModelForm):
    cuenta = forms.ModelChoiceField(
        queryset=Cuenta.objects.none(),
        required=True,
        label='Cuenta de origen',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = DepositoAhorro
        fields = ['meta', 'cuenta', 'monto', 'fecha', 'nota']
        widgets = {
            'meta': forms.Select(attrs={'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'min': '0.01',
                'placeholder': '0.00'
            }),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nota': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Ej. Depósito quincenal'}),
        }

    def __init__(self, *args, **kwargs):
        inquilino = kwargs.pop('inquilino', None)
        super().__init__(*args, **kwargs)
        if inquilino:
            self.fields['cuenta'].queryset = Cuenta.objects.filter(
                inquilino=inquilino,
                tipo__in=['efectivo', 'debito'],
                activo=True
            )
