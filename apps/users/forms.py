from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario


class RegistroForm(UserCreationForm):
    correo = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={'placeholder': 'tu@email.com'}),
    )
    nombre = forms.CharField(
        label='Nombre', max_length=30,
        widget=forms.TextInput(attrs={'placeholder': 'Tu nombre'}),
    )
    apellido = forms.CharField(
        label='Apellido', max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Tu apellido'}),
    )

    class Meta:
        model = Usuario
        fields = ['nombre_usuario', 'correo', 'nombre', 'apellido', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nombre_usuario'].widget.attrs.update({'placeholder': 'usuario123'})
        self.fields['nombre_usuario'].label = 'Nombre de usuario'


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Nombre de usuario',
        widget=forms.TextInput(attrs={'placeholder': 'tu_usuario'}),
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'}),
    )


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'correo', 'telefono', 'avatar', 'ingreso_mensual']
        widgets = {
            'telefono': forms.TextInput(attrs={'placeholder': '809-555-1234'}),
            'ingreso_mensual': forms.NumberInput(attrs={'step': '0.01'}),
        }
