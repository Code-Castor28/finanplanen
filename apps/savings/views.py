import json
from datetime import date
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import ProtectedError
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import MetaAhorroForm, DepositoAhorroForm
from .models import MetaAhorro, DepositoAhorro
from apps.accounts.models import Cuenta
from apps.theme.models import Color, Icono


class InquilinoMixin(LoginRequiredMixin):
    def get_queryset(self):
        return self.model.objects.filter(inquilino=self.request.user.inquilino)

    def form_valid(self, form):
        if hasattr(form, 'instance'):
            form.instance.inquilino = self.request.user.inquilino
            form.instance.usuario = self.request.user
        return super().form_valid(form)


class MetaAhorroLista(InquilinoMixin, ListView):
    model = MetaAhorro
    context_object_name = 'metas'
    template_name = 'savings/ahoro.html'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('color', 'icono')
        qs = qs.filter(activo=True)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'savings'
        context['hoy'] = date.today().isoformat()
        context['form_meta'] = MetaAhorroForm()
        context['form_deposito'] = DepositoAhorroForm()

        if not self.request.headers.get('HX-Request'):
            qs = self.get_queryset()
            total_ahorrado = sum(m.monto_actual for m in qs)
            context['total_ahorrado'] = total_ahorrado
            total_meta = sum(m.meta for m in qs)
            context['progreso_promedio'] = round(total_ahorrado / total_meta * 100, 1) if total_meta else 0

            mejor = qs.order_by('-monto_actual').first()
            if mejor:
                context['mejor'] = mejor
                context['faltante_destacada'] = mejor.meta - mejor.monto_actual
            else:
                context['mejor'] = None
                context['faltante_destacada'] = 0

            context['total_metas'] = qs.count()
            context['colores'] = Color.objects.filter(inquilino=self.request.user.inquilino, activo=True)
            context['iconos'] = Icono.objects.filter(inquilino=self.request.user.inquilino, activo=True)
            context['cuentas'] = Cuenta.objects.filter(
                inquilino=self.request.user.inquilino,
                tipo__in=['efectivo', 'debito'],
                activo=True
            )

            metas_list = []
            for m in qs:
                metas_list.append({
                    'pk': m.pk,
                    'nombre': m.nombre,
                    'meta': str(m.meta),
                    'monto_actual': str(m.monto_actual),
                    'pct': m.progreso_pct(),
                })
            context['metas_json'] = json.dumps(metas_list, cls=DjangoJSONEncoder)

        return context


class MetaAhorroCrear(InquilinoMixin, CreateView):
    model = MetaAhorro
    form_class = MetaAhorroForm
    template_name = 'theme/_form_savings_meta.html'

    def get_success_url(self):
        return reverse_lazy('savings:lista')

    def form_valid(self, form):
        super().form_valid(form)
        messages.success(self.request, 'Meta de ahorro creada correctamente.')
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return self.render_to_response(self.get_context_data(form=form), status=422)
        return super().form_invalid(form)


class MetaAhorroEditar(InquilinoMixin, UpdateView):
    model = MetaAhorro
    form_class = MetaAhorroForm
    template_name = 'theme/_form_savings_meta.html'

    def get_success_url(self):
        return reverse_lazy('savings:lista')

    def form_valid(self, form):
        super().form_valid(form)
        messages.success(self.request, 'Meta de ahorro actualizada correctamente.')
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return self.render_to_response(self.get_context_data(form=form), status=422)
        return super().form_invalid(form)


class MetaAhorroEliminar(InquilinoMixin, DeleteView):
    model = MetaAhorro
    template_name = 'theme/_confirmar_eliminar.html'

    def get_success_url(self):
        return reverse_lazy('savings:lista')

    def form_valid(self, form):
        self.object = self.get_object()
        try:
            self.object.delete()
        except ProtectedError:
            messages.error(self.request, 'No se puede eliminar: esta meta tiene depósitos asociados. Elimina primero sus depósitos.')
            response = HttpResponse()
            response['HX-Redirect'] = self.get_success_url()
            return response
        messages.success(self.request, 'Meta de ahorro eliminada correctamente.')
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['model_name'] = 'meta de ahorro'
        return ctx


class DepositoAhorroCrear(InquilinoMixin, CreateView):
    model = DepositoAhorro
    form_class = DepositoAhorroForm
    template_name = 'theme/_form_savings_deposito.html'

    def get_success_url(self):
        return reverse_lazy('savings:lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['inquilino'] = self.request.user.inquilino
        return kwargs

    def form_valid(self, form):
        super().form_valid(form)
        messages.success(self.request, 'Depósito registrado correctamente.')
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return self.render_to_response(self.get_context_data(form=form), status=422)
        return super().form_invalid(form)


class DepositoAhorroEliminar(InquilinoMixin, DeleteView):
    model = DepositoAhorro
    template_name = 'theme/_confirmar_eliminar.html'

    def get_success_url(self):
        return reverse_lazy('savings:lista')

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.delete()
        messages.success(self.request, 'Depósito eliminado correctamente.')
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['model_name'] = 'depósito'
        return ctx
