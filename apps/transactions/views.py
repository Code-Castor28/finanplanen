from datetime import date
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Sum
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import IngresoForm, GastoForm
from .models import Ingreso, Gasto
from apps.accounts.models import Cuenta
from apps.categories.models import Categoria
from apps.transfers.models import Transferencia


class InquilinoMixin(LoginRequiredMixin):
    def get_queryset(self):
        return self.model.objects.filter(inquilino=self.request.user.inquilino)

    def form_valid(self, form):
        form.instance.inquilino = self.request.user.inquilino
        form.instance.usuario = self.request.user
        return super().form_valid(form)


class IngresoLista(InquilinoMixin, ListView):
    model = Ingreso
    context_object_name = 'ingresos'
    template_name = 'transactions/ingresos.html'
    paginate_by = 20

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['transactions/_lista_ingresos.html']
        return [self.template_name]

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('cuenta', 'categoria', 'categoria__icono')
        fecha_desde = self.request.GET.get('fecha_desde')
        fecha_hasta = self.request.GET.get('fecha_hasta')
        cuenta = self.request.GET.get('cuenta')
        categoria = self.request.GET.get('categoria')
        if fecha_desde:
            qs = qs.filter(fecha__gte=fecha_desde)
        if fecha_hasta:
            qs = qs.filter(fecha__lte=fecha_hasta)
        if cuenta:
            qs = qs.filter(cuenta_id=cuenta)
        if categoria:
            qs = qs.filter(categoria_id=categoria)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'ingresos'
        context['filtros'] = self.request.GET
        context['hoy'] = date.today().isoformat()

        if not self.request.headers.get('HX-Request'):
            inquilino = self.request.user.inquilino
            context['cuentas'] = Cuenta.objects.filter(inquilino=inquilino).order_by('nombre')

            cats = Categoria.objects.filter(inquilino=inquilino).order_by('nombre')
            ingresos_qs = Ingreso.objects.filter(inquilino=inquilino)
            for cat in cats:
                cat_ingresos = ingresos_qs.filter(categoria=cat)
                cat.total_ingresos = cat_ingresos.aggregate(s=Sum('monto'))['s'] or 0
                cat.ingresos_count = cat_ingresos.count()
            context['categorias'] = cats

            qs_all = self.get_queryset()
            total = qs_all.aggregate(s=Sum('monto'))['s'] or 0
            context['total_ingresos'] = total

            hoy = date.today()
            mes_qs = Ingreso.objects.filter(
                inquilino=inquilino,
                fecha__year=hoy.year,
                fecha__month=hoy.month
            )
            total_mes = mes_qs.aggregate(s=Sum('monto'))['s'] or 0
            context['total_mes'] = total_mes

            cats_dist = Categoria.objects.filter(inquilino=inquilino).order_by('nombre')
            total_cats = 0
            dist_data = []
            for cat in cats_dist:
                cat_total = Ingreso.objects.filter(
                    inquilino=inquilino, categoria=cat
                ).aggregate(s=Sum('monto'))['s'] or 0
                total_cats += cat_total
                dist_data.append({
                    'nombre': cat.nombre,
                    'total': cat_total,
                    'color': cat.color.hex if cat.color else '#1a237e',
                })
            for d in dist_data:
                d['pct'] = round((d['total'] / total_cats * 100)) if total_cats else 0
            context['distribucion'] = dist_data

        return context


class IngresoCrear(InquilinoMixin, CreateView):
    model = Ingreso
    form_class = IngresoForm
    template_name = 'transactions/_form_ingreso.html'

    def get_success_url(self):
        return reverse_lazy('transactions:ingresos')

    def form_valid(self, form):
        super().form_valid(form)
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return self.render_to_response(self.get_context_data(form=form), status=422)
        return super().form_invalid(form)


class IngresoEditar(InquilinoMixin, UpdateView):
    model = Ingreso
    form_class = IngresoForm
    template_name = 'transactions/_form_ingreso.html'

    def get_success_url(self):
        return reverse_lazy('transactions:ingresos')

    def form_valid(self, form):
        super().form_valid(form)
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return self.render_to_response(self.get_context_data(form=form), status=422)
        return super().form_invalid(form)


class IngresoEliminar(InquilinoMixin, DeleteView):
    model = Ingreso
    template_name = 'theme/_confirmar_eliminar.html'

    def get_success_url(self):
        return reverse_lazy('transactions:ingresos')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['model_name'] = 'ingreso'
        return ctx


class GastoLista(InquilinoMixin, ListView):
    model = Gasto
    context_object_name = 'gastos'
    template_name = 'transactions/gastos.html'
    paginate_by = 20

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['transactions/_lista_gastos.html']
        return [self.template_name]

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('cuenta', 'categoria', 'categoria__icono')
        fecha_desde = self.request.GET.get('fecha_desde')
        fecha_hasta = self.request.GET.get('fecha_hasta')
        cuenta = self.request.GET.get('cuenta')
        categoria = self.request.GET.get('categoria')
        if fecha_desde:
            qs = qs.filter(fecha__gte=fecha_desde)
        if fecha_hasta:
            qs = qs.filter(fecha__lte=fecha_hasta)
        if cuenta:
            qs = qs.filter(cuenta_id=cuenta)
        if categoria:
            qs = qs.filter(categoria_id=categoria)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'gastos'
        context['filtros'] = self.request.GET
        context['hoy'] = date.today().isoformat()

        if not self.request.headers.get('HX-Request'):
            inquilino = self.request.user.inquilino
            context['cuentas'] = Cuenta.objects.filter(inquilino=inquilino).order_by('nombre')

            cats = Categoria.objects.filter(inquilino=inquilino).order_by('nombre')
            gastos_qs = Gasto.objects.filter(inquilino=inquilino)
            for cat in cats:
                cat_gastos = gastos_qs.filter(categoria=cat)
                cat.total_gastos = cat_gastos.aggregate(s=Sum('monto'))['s'] or 0
                cat.gastos_count = cat_gastos.count()
            context['categorias'] = cats

            qs_all = self.get_queryset()
            total = qs_all.aggregate(s=Sum('monto'))['s'] or 0
            context['total_gastos'] = total

            hoy = date.today()
            mes_qs = Gasto.objects.filter(
                inquilino=inquilino,
                fecha__year=hoy.year,
                fecha__month=hoy.month
            )
            total_mes = mes_qs.aggregate(s=Sum('monto'))['s'] or 0
            context['total_mes'] = total_mes
            context['budget_limit'] = 20000

            cats_dist = Categoria.objects.filter(inquilino=inquilino).order_by('nombre')
            total_cats = 0
            dist_data = []
            for cat in cats_dist:
                cat_total = Gasto.objects.filter(
                    inquilino=inquilino, categoria=cat
                ).aggregate(s=Sum('monto'))['s'] or 0
                total_cats += cat_total
                dist_data.append({
                    'nombre': cat.nombre,
                    'total': cat_total,
                    'color': cat.color.hex if cat.color else '#1a237e',
                })
            for d in dist_data:
                d['pct'] = round((d['total'] / total_cats * 100)) if total_cats else 0
            context['distribucion'] = dist_data

        return context


class GastoCrear(InquilinoMixin, CreateView):
    model = Gasto
    form_class = GastoForm
    template_name = 'transactions/_form_gasto.html'

    def get_success_url(self):
        return reverse_lazy('transactions:gastos')

    def form_valid(self, form):
        super().form_valid(form)
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return self.render_to_response(self.get_context_data(form=form), status=422)
        return super().form_invalid(form)


class GastoEditar(InquilinoMixin, UpdateView):
    model = Gasto
    form_class = GastoForm
    template_name = 'transactions/_form_gasto.html'

    def get_success_url(self):
        return reverse_lazy('transactions:gastos')

    def form_valid(self, form):
        super().form_valid(form)
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return self.render_to_response(self.get_context_data(form=form), status=422)
        return super().form_invalid(form)


class GastoEliminar(InquilinoMixin, DeleteView):
    model = Gasto
    template_name = 'theme/_confirmar_eliminar.html'

    def get_success_url(self):
        return reverse_lazy('transactions:gastos')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['model_name'] = 'gasto'
        return ctx


class TransaccionLista(LoginRequiredMixin, ListView):
    template_name = 'transactions/transacciones.html'
    context_object_name = 'movimientos'
    paginate_by = 30

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['transactions/_lista_transacciones.html']
        return [self.template_name]

    def get_queryset(self):
        return Gasto.objects.none()

    def _build_movimientos(self, inquilino):
        fecha_desde = self.request.GET.get('fecha_desde')
        fecha_hasta = self.request.GET.get('fecha_hasta')
        cuenta = self.request.GET.get('cuenta')
        categoria = self.request.GET.get('categoria')
        tipo = self.request.GET.get('tipo')

        movimientos = []

        if not tipo or tipo == 'ingreso':
            qs = Ingreso.objects.filter(inquilino=inquilino).select_related('cuenta', 'categoria', 'categoria__icono')
            if fecha_desde:
                qs = qs.filter(fecha__gte=fecha_desde)
            if fecha_hasta:
                qs = qs.filter(fecha__lte=fecha_hasta)
            if cuenta:
                qs = qs.filter(cuenta_id=cuenta)
            if categoria:
                qs = qs.filter(categoria_id=categoria)
            for obj in qs:
                movimientos.append({
                    'tipo': 'ingreso',
                    'fecha': obj.fecha,
                    'monto': obj.monto,
                    'nota': obj.nota,
                    'cuenta': obj.cuenta,
                    'cuenta_nombre': obj.cuenta.nombre,
                    'categoria': obj.categoria,
                    'pk': obj.pk,
                    'model': 'Ingreso',
                })

        if not tipo or tipo == 'gasto':
            qs = Gasto.objects.filter(inquilino=inquilino).select_related('cuenta', 'categoria', 'categoria__icono')
            if fecha_desde:
                qs = qs.filter(fecha__gte=fecha_desde)
            if fecha_hasta:
                qs = qs.filter(fecha__lte=fecha_hasta)
            if cuenta:
                qs = qs.filter(cuenta_id=cuenta)
            if categoria:
                qs = qs.filter(categoria_id=categoria)
            for obj in qs:
                movimientos.append({
                    'tipo': 'gasto',
                    'fecha': obj.fecha,
                    'monto': obj.monto,
                    'nota': obj.nota,
                    'cuenta': obj.cuenta,
                    'cuenta_nombre': obj.cuenta.nombre,
                    'categoria': obj.categoria,
                    'pk': obj.pk,
                    'model': 'Gasto',
                })

        if not tipo or tipo == 'transferencia':
            tqs = Transferencia.objects.filter(inquilino=inquilino).select_related('origen', 'destino')
            if fecha_desde:
                tqs = tqs.filter(fecha__gte=fecha_desde)
            if fecha_hasta:
                tqs = tqs.filter(fecha__lte=fecha_hasta)
            if cuenta:
                tqs = tqs.filter(origen_id=cuenta) | tqs.filter(destino_id=cuenta)
            for obj in tqs:
                movimientos.append({
                    'tipo': 'transferencia',
                    'fecha': obj.fecha,
                    'monto': obj.monto,
                    'nota': f'{obj.origen.nombre} → {obj.destino.nombre}',
                    'cuenta': obj.origen,
                    'cuenta_nombre': obj.origen.nombre,
                    'categoria': None,
                    'pk': obj.pk,
                    'model': 'Transferencia',
                })

        movimientos.sort(key=lambda x: x['fecha'], reverse=True)
        return movimientos

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'transactions'
        context['filtros'] = self.request.GET

        inquilino = self.request.user.inquilino
        movimientos = self._build_movimientos(inquilino)

        paginator = Paginator(movimientos, self.paginate_by)
        page = self.request.GET.get('page', 1)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        context['movimientos'] = page_obj.object_list
        context['paginator'] = paginator
        context['page_obj'] = page_obj
        context['is_paginated'] = page_obj.has_other_pages()

        if not self.request.headers.get('HX-Request'):
            context['cuentas'] = Cuenta.objects.filter(inquilino=inquilino).order_by('nombre')
            context['categorias'] = Categoria.objects.filter(inquilino=inquilino).order_by('nombre')

            total_cuentas = Cuenta.objects.filter(
                inquilino=inquilino
            ).aggregate(s=Sum('balance'))['s'] or 0

            total_ingresos = sum(
                m['monto'] for m in movimientos if m['tipo'] == 'ingreso'
            )
            total_gastos = sum(
                m['monto'] for m in movimientos if m['tipo'] == 'gasto'
            )

            context['total_ingresos'] = total_ingresos
            context['total_gastos'] = total_gastos
            context['balance'] = total_cuentas

        return context
