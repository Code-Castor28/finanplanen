import re
from django import forms
from django.utils.text import slugify
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
            'balance': forms.TextInput(attrs={
                'inputmode': 'decimal', 'autocomplete': 'off',
                'style': 'border:none;background:transparent;flex:1;min-width:0;padding:10px 12px;font-family:inherit;font-size:14px;outline:none',
            }),
            'emisor': forms.TextInput(attrs={'placeholder': 'Ej. Banco Popular'}),
            'ultimos_digitos': forms.TextInput(attrs={
                'placeholder': '4412', 'maxlength': '4', 'inputmode': 'numeric',
            }),
            'dia_corte': forms.TextInput(attrs={'placeholder': 'Día 12', 'inputmode': 'numeric'}),
            'dia_pago': forms.TextInput(attrs={'placeholder': 'Día 26', 'inputmode': 'numeric'}),
            'vencimiento': forms.TextInput(attrs={
                'placeholder': 'MM/AA', 'maxlength': '5', 'inputmode': 'numeric',
            }),
        }

    def __init__(self, *args, **kwargs):
        self.inquilino = kwargs.pop('inquilino', None)
        tipo_filter = kwargs.pop('tipo_filter', None)
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.initial['balance'] = ''
        if tipo_filter:
            choices = [c for c in self.fields['tipo'].choices if c[0] == tipo_filter or (tipo_filter == 'tarjeta' and c[0] in ('credito', 'debito'))]
            self.fields['tipo'].choices = choices

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if nombre and self.inquilino:
            slug = slugify(nombre)
            qs = Cuenta.objects.filter(inquilino=self.inquilino, slug=slug)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Ya existe una cuenta con ese nombre.')
        return nombre

    def clean_ultimos_digitos(self):
        val = self.cleaned_data.get('ultimos_digitos')
        if val:
            if not val.isdigit() or len(val) != 4:
                raise forms.ValidationError('Deben ser exactamente 4 dígitos.')
            if self.inquilino:
                qs = Cuenta.objects.filter(inquilino=self.inquilino, ultimos_digitos=val)
                if self.instance.pk:
                    qs = qs.exclude(pk=self.instance.pk)
                if qs.exists():
                    raise forms.ValidationError('Ya existe una cuenta con esos últimos 4 dígitos.')
        return val

    def clean_vencimiento(self):
        val = self.cleaned_data.get('vencimiento')
        if val:
            digits = re.sub(r'\D', '', val)
            if len(digits) != 4:
                raise forms.ValidationError('Formato inválido. Use MM/AA.')
            month = int(digits[:2])
            if month < 1 or month > 12:
                raise forms.ValidationError('Mes inválido (debe ser 01-12).')
            return f'{digits[:2]}/{digits[2:]}'
        return val

    def clean_dia_corte(self):
        val = self.cleaned_data.get('dia_corte')
        if val and not val.isdigit():
            raise forms.ValidationError('Solo números.')
        return val

    def clean_dia_pago(self):
        val = self.cleaned_data.get('dia_pago')
        if val and not val.isdigit():
            raise forms.ValidationError('Solo números.')
        return val
