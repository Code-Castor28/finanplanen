from django import forms
from .models import Color, Icono


class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ['nombre', 'hex', 'slug', 'activo']
        widgets = {
            'hex': forms.TextInput(attrs={'placeholder': '#FF5733', 'type': 'color'}),
        }

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        if not slug:
            from django.utils.text import slugify
            slug = slugify(self.cleaned_data.get('nombre', ''))
        return slug


class IconoForm(forms.ModelForm):
    class Meta:
        model = Icono
        fields = ['nombre', 'slug', 'clase_css', 'activo']
        widgets = {
            'clase_css': forms.TextInput(attrs={'placeholder': 'fas fa-home'}),
        }
