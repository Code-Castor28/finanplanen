from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.conf import settings
from .forms import RegistroForm, LoginForm, PerfilForm
from .models import Usuario


class IniciarSesion(LoginView):
    template_name = 'users/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('core:inicio')


class RegistroView(CreateView):
    template_name = 'users/register.html'
    form_class = RegistroForm
    success_url = reverse_lazy('users:ingresar')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Crear Cuenta'
        return ctx


class PerfilView(LoginRequiredMixin, UpdateView):
    template_name = 'users/perfil.html'
    form_class = PerfilForm
    success_url = reverse_lazy('users:perfil')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['vapid_public_key'] = settings.VAPID_PUBLIC_KEY
        return ctx
