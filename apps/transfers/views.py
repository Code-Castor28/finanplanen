from datetime import date
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import TransferenciaForm
from .models import Transferencia
from apps.accounts.models import Cuenta


class InquilinoMixin(LoginRequiredMixin):
    def get_queryset(self):
        return self.model.objects.filter(inquilino=self.request.user.inquilino)

    def form_valid(self, form):
        if hasattr(form, 'instance'):
            form.instance.inquilino = self.request.user.inquilino
            form.instance.usuario = self.request.user
        return super().form_valid(form)


class TransferenciaLista(InquilinoMixin, ListView):
    model = Transferencia
    context_object_name = 'transferencias'
    template_name = 'transfers/transferencias.html'
    paginate_by = 20

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['transfers/_lista_transferencias.html']
        return [self.template_name]

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('origen', 'destino')
        fecha_desde = self.request.GET.get('fecha_desde')
        fecha_hasta = self.request.GET.get('fecha_hasta')
        cuenta = self.request.GET.get('cuenta')
        if fecha_desde:
            qs = qs.filter(fecha__gte=fecha_desde)
        if fecha_hasta:
            qs = qs.filter(fecha__lte=fecha_hasta)
        if cuenta:
            qs = qs.filter(origen_id=cuenta) | qs.filter(destino_id=cuenta)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'transfers'
        context['filtros'] = self.request.GET
        context['hoy'] = date.today().isoformat()

        if not self.request.headers.get('HX-Request'):
            inquilino = self.request.user.inquilino
            context['cuentas'] = Cuenta.objects.filter(inquilino=inquilino).order_by('nombre')
            hoy = date.today()
            total_mes = Transferencia.objects.filter(
                inquilino=inquilino,
                fecha__year=hoy.year,
                fecha__month=hoy.month
            ).aggregate(total=Sum('monto'))['total'] or 0
            context['total_mes'] = total_mes
        return context


class TransferenciaCrear(InquilinoMixin, CreateView):
    model = Transferencia
    form_class = TransferenciaForm
    template_name = 'transfers/_form_transferencia.html'

    def get_success_url(self):
        return reverse_lazy('transfers:lista')

    def form_valid(self, form):
        super().form_valid(form)
        messages.success(self.request, 'Transferencia creada correctamente.')
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            if self.request.headers.get('HX-Target') == 'transferencia-list':
                errors = form.non_field_errors()
                error_msg = errors[0] if errors else 'Error en el formulario'
                html = (
                    '<div style="padding:12px 16px;border-radius:8px;font-size:13px;font-weight:500;display:flex;align-items:center;gap:8px;background:rgba(198,40,40,.1);color:#C62828">'
                    '<i class="fas fa-exclamation-circle"></i> %s</div>'
                ) % error_msg
                response = HttpResponse(html, status=422)
                response['HX-Retarget'] = '#form-errors'
                response['HX-Reswap'] = 'innerHTML'
                return response
            return self.render_to_response(self.get_context_data(form=form), status=422)
        return super().form_invalid(form)


class TransferenciaEditar(InquilinoMixin, UpdateView):
    model = Transferencia
    form_class = TransferenciaForm
    template_name = 'transfers/_form_transferencia.html'

    def get_success_url(self):
        return reverse_lazy('transfers:lista')

    def form_valid(self, form):
        super().form_valid(form)
        messages.success(self.request, 'Transferencia actualizada correctamente.')
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return self.render_to_response(self.get_context_data(form=form), status=422)
        return super().form_invalid(form)


class TransferenciaEliminar(InquilinoMixin, DeleteView):
    model = Transferencia
    template_name = 'theme/_confirmar_eliminar.html'

    def get_success_url(self):
        return reverse_lazy('transfers:lista')

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.delete()
        messages.success(self.request, 'Transferencia eliminada correctamente.')
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['model_name'] = 'transferencia'
        return ctx
