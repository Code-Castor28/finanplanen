from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import CuentaForm
from .models import Cuenta


class InquilinoMixin(LoginRequiredMixin):
    def get_queryset(self):
        return self.model.objects.filter(inquilino=self.request.user.inquilino)

    def form_valid(self, form):
        if hasattr(form, 'instance'):
            form.instance.inquilino = self.request.user.inquilino
            form.instance.usuario = self.request.user
        return super().form_valid(form)


class CuentaLista(InquilinoMixin, ListView):
    model = Cuenta
    context_object_name = 'cuentas'
    template_name = 'accounts/Cuenta.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'accounts'
        qs = context['cuentas']
        context['tarjetas'] = qs.exclude(tipo__in=['efectivo'])
        context['wallets'] = qs.filter(tipo='efectivo')
        context['total_credito'] = qs.filter(tipo='credito').aggregate(s=Sum('balance'))['s'] or 0
        context['total_debito'] = qs.filter(tipo='debito').aggregate(s=Sum('balance'))['s'] or 0
        context['total_wallet'] = qs.filter(tipo='efectivo').aggregate(s=Sum('balance'))['s'] or 0
        context['total'] = context['total_credito'] + context['total_debito'] + context['total_wallet']
        return context


class CuentaCrear(InquilinoMixin, CreateView):
    model = Cuenta
    form_class = CuentaForm
    template_name = 'accounts/_form_cuenta.html'

    def get_initial(self):
        initial = super().get_initial()
        tipo = self.request.GET.get('tipo')
        if tipo in dict(Cuenta.TIPO_CHOICES):
            initial['tipo'] = tipo
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['inquilino'] = self.request.user.inquilino
        tipo = self.request.GET.get('tipo')
        if tipo == 'efectivo':
            kwargs['tipo_filter'] = 'efectivo'
        elif tipo in ('credito', 'debito'):
            kwargs['tipo_filter'] = 'tarjeta'
        return kwargs

    def get_success_url(self):
        return reverse_lazy('accounts:lista')

    def form_valid(self, form):
        super().form_valid(form)
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return self.render_to_response(self.get_context_data(form=form), status=422)
        return super().form_invalid(form)


class CuentaEditar(InquilinoMixin, UpdateView):
    model = Cuenta
    form_class = CuentaForm
    template_name = 'accounts/_form_cuenta.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['inquilino'] = self.request.user.inquilino
        return kwargs

    def get_success_url(self):
        return reverse_lazy('accounts:lista')

    def form_valid(self, form):
        super().form_valid(form)
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return self.render_to_response(self.get_context_data(form=form), status=422)
        return super().form_invalid(form)


class CuentaEliminar(InquilinoMixin, DeleteView):
    model = Cuenta
    template_name = 'theme/_confirmar_eliminar.html'

    def get_success_url(self):
        return reverse_lazy('accounts:lista')

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.delete()
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['model_name'] = 'cuenta'
        return ctx
