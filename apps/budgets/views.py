import json
from datetime import date
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import PresupuestoForm
from .models import Presupuesto
from apps.categories.models import Categoria
from apps.transactions.models import Ingreso, Gasto


class InquilinoMixin(LoginRequiredMixin):
    def get_queryset(self):
        return self.model.objects.filter(inquilino=self.request.user.inquilino)

    def form_valid(self, form):
        if hasattr(form, 'instance'):
            form.instance.inquilino = self.request.user.inquilino
            form.instance.usuario = self.request.user
        return super().form_valid(form)


class PresupuestoLista(InquilinoMixin, ListView):
    model = Presupuesto
    context_object_name = 'presupuestos'
    template_name = 'budgets/presupuesto.html'

    def get_queryset(self):
        hoy = date.today()
        return super().get_queryset().filter(
            mes=hoy.month, año=hoy.year, activo=True
        ).select_related('categoria', 'categoria__icono', 'categoria__color')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'budgets'
        context['form'] = PresupuestoForm()
        context['hoy'] = date.today()

        inquilino = self.request.user.inquilino
        hoy = date.today()
        mes = hoy.month
        año = hoy.year

        total_ingresos = Ingreso.objects.filter(
            inquilino=inquilino, fecha__month=mes, fecha__year=año
        ).aggregate(t=Sum('monto'))['t'] or 0

        total_gastos = Gasto.objects.filter(
            inquilino=inquilino, fecha__month=mes, fecha__year=año
        ).aggregate(t=Sum('monto'))['t'] or 0

        context['total_ingresos_mes'] = total_ingresos
        context['total_gastos_mes'] = total_gastos
        context['disponible'] = total_ingresos - total_gastos

        total_limite = sum(p.monto_limite for p in context['presupuestos'])
        total_gastado_p = sum(p.monto_gastado for p in context['presupuestos'])
        context['total_limite'] = total_limite
        context['total_gastado_p'] = total_gastado_p
        context['pct_general'] = round(total_gastado_p / total_limite * 100, 1) if total_limite else 0

        context['categorias'] = Categoria.objects.filter(
            inquilino=inquilino, activo=True
        ).exclude(slug__in=['ingreso-debito', 'ingreso-efectivo', 'pago-tarjeta'])

        presupuestos_json = []
        for p in context['presupuestos']:
            presupuestos_json.append({
                'pk': p.pk,
                'nombre': p.categoria.nombre if p.categoria_id else 'Sin categoría',
                'limite': str(p.monto_limite),
                'gastado': str(p.monto_gastado),
                'icono': p.categoria.icono.clase_css if p.categoria_id and p.categoria.icono_id else 'fa-tag',
                'color': p.categoria.color.hex if p.categoria_id and p.categoria.color_id else '#455A64',
            })
        context['presupuestos_json'] = json.dumps(presupuestos_json, cls=DjangoJSONEncoder)

        return context


class PresupuestoCrear(InquilinoMixin, CreateView):
    model = Presupuesto
    form_class = PresupuestoForm
    template_name = 'budgets/_form_presupuesto.html'

    def get_success_url(self):
        return reverse_lazy('budgets:lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['inquilino'] = self.request.user.inquilino
        return kwargs

    def form_valid(self, form):
        super().form_valid(form)
        messages.success(self.request, 'Presupuesto creado correctamente.')
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return self.render_to_response(self.get_context_data(form=form), status=422)
        return super().form_invalid(form)


class PresupuestoEditar(InquilinoMixin, UpdateView):
    model = Presupuesto
    form_class = PresupuestoForm
    template_name = 'budgets/_form_presupuesto.html'

    def get_success_url(self):
        return reverse_lazy('budgets:lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['inquilino'] = self.request.user.inquilino
        return kwargs

    def form_valid(self, form):
        super().form_valid(form)
        messages.success(self.request, 'Presupuesto actualizado correctamente.')
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return self.render_to_response(self.get_context_data(form=form), status=422)
        return super().form_invalid(form)


class PresupuestoEliminar(InquilinoMixin, DeleteView):
    model = Presupuesto
    template_name = 'theme/_confirmar_eliminar.html'

    def get_success_url(self):
        return reverse_lazy('budgets:lista')

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.delete()
        messages.success(self.request, 'Presupuesto eliminado correctamente.')
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['model_name'] = 'presupuesto'
        return ctx
