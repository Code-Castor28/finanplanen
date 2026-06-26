from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import ProtectedError, Sum
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import CuentaForm
from .models import Cuenta
from apps.categories.models import Categoria
from apps.theme.models import Color
from apps.transactions.constants import CAT_INGRESO_MAP, CAT_AJUSTE_MAP
from apps.transactions.models import Ingreso, Gasto


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
        tipo = form.cleaned_data.get('tipo')
        balance_deseado = form.cleaned_data.get('balance', 0)
        super().form_valid(form)
        cuenta = form.instance
        if balance_deseado > 0 and tipo in ('debito', 'efectivo'):
            nombre_cat, hex_color = CAT_INGRESO_MAP[tipo]
            color_obj, _ = Color.objects.get_or_create(
                inquilino=cuenta.inquilino,
                slug=slugify(nombre_cat),
                defaults={'nombre': f'Color {nombre_cat}', 'hex': hex_color, 'usuario': cuenta.usuario},
            )
            categoria, _ = Categoria.objects.get_or_create(
                inquilino=cuenta.inquilino,
                slug=slugify(nombre_cat),
                defaults={
                    'nombre': nombre_cat,
                    'usuario': cuenta.usuario,
                    'color': color_obj,
                }
            )
            Ingreso.objects.create(
                inquilino=cuenta.inquilino,
                usuario=cuenta.usuario,
                cuenta=cuenta,
                categoria=categoria,
                monto=balance_deseado,
                fecha=date.today(),
                nota=f'Balance inicial — {cuenta.nombre}',
            )
            Cuenta.objects.filter(pk=cuenta.pk).update(balance=balance_deseado)
        messages.success(self.request, 'Cuenta creada correctamente.')
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
        old_balance = self.get_object().balance
        tipo = form.cleaned_data.get('tipo', self.get_object().tipo)
        new_balance = form.cleaned_data.get('balance', 0)
        diff = new_balance - old_balance
        super().form_valid(form)
        cuenta = form.instance
        if diff != 0 and tipo in ('debito', 'efectivo'):
            if diff > 0:
                key = 'positivo'
                model_cls = Ingreso
                monto = diff
            else:
                key = 'negativo'
                model_cls = Gasto
                monto = abs(diff)
            nombre_cat, slug, hex_color = CAT_AJUSTE_MAP[key]
            color_obj, _ = Color.objects.get_or_create(
                inquilino=cuenta.inquilino,
                slug=slug,
                defaults={'nombre': f'Color {nombre_cat}', 'hex': hex_color, 'usuario': cuenta.usuario},
            )
            categoria, _ = Categoria.objects.get_or_create(
                inquilino=cuenta.inquilino,
                slug=slug,
                defaults={
                    'nombre': nombre_cat,
                    'usuario': cuenta.usuario,
                    'color': color_obj,
                }
            )
            model_cls.objects.create(
                inquilino=cuenta.inquilino,
                usuario=cuenta.usuario,
                cuenta=cuenta,
                categoria=categoria,
                monto=monto,
                fecha=date.today(),
                nota=f'Ajuste balance — {cuenta.nombre}',
            )
            Cuenta.objects.filter(pk=cuenta.pk).update(balance=new_balance)
        messages.success(self.request, 'Cuenta actualizada correctamente.')
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
        try:
            self.object.delete()
        except ProtectedError:
            messages.error(
                self.request,
                'No se puede eliminar: esta cuenta tiene transacciones asociadas. '
                'Elimina primero sus ingresos, gastos y transferencias.',
            )
            response = HttpResponse()
            response['HX-Redirect'] = self.get_success_url()
            return response
        messages.success(self.request, 'Cuenta eliminada correctamente.')
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['model_name'] = 'cuenta'
        return ctx


@login_required
@require_POST
def validar_campo(request):
    field = request.POST.get('field')
    value = request.POST.get('value', '')
    instance_pk = request.POST.get('instance_pk')
    instance = None
    if instance_pk:
        try:
            instance = Cuenta.objects.get(pk=instance_pk, inquilino=request.user.inquilino)
        except Cuenta.DoesNotExist:
            pass
    form = CuentaForm(data={field: value}, instance=instance, inquilino=request.user.inquilino)
    form.is_valid()
    errors = form.errors.get(field, [])
    if errors:
        return HttpResponse(f'<span class="field-error">{errors[0]}</span>')
    return HttpResponse('<span class="field-error"></span>')
