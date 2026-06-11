from django import forms
from .models import Categoria, Etiqueta


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'slug', 'color', 'icono', 'deducible', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Ej. Transporte'}),
            'slug': forms.TextInput(attrs={'placeholder': 'transporte'}),
            'color': forms.Select(),
            'icono': forms.Select(),
        }

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        if not slug:
            from django.utils.text import slugify
            slug = slugify(self.cleaned_data.get('nombre', ''))
        return slug


class EtiquetaForm(forms.ModelForm):
    class Meta:
        model = Etiqueta
        fields = ['nombre', 'slug', 'color', 'categorias', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Ej. Trabajo'}),
            'slug': forms.TextInput(attrs={'placeholder': 'trabajo'}),
            'color': forms.Select(),
            'categorias': forms.SelectMultiple(),
        }
