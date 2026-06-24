import json
import random
from datetime import date
from dateutil.relativedelta import relativedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.views.generic import TemplateView
from apps.accounts.models import Cuenta
from apps.core.utils import calcular_prox_pago
from apps.transactions.models import Ingreso, Gasto


class PanelPrincipal(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'dashboard'

        inquilino = self.request.user.inquilino
        hoy = date.today()
        mes_actual = hoy.month
        año_actual = hoy.year
        mes_anterior = mes_actual - 1 if mes_actual > 1 else 12
        año_anterior = año_actual if mes_actual > 1 else año_actual - 1

        # --- Balance total ---
        total_balance = Cuenta.objects.filter(
            inquilino=inquilino, activo=True
        ).aggregate(t=Sum('balance'))['t'] or 0
        context['total_balance'] = total_balance

        # --- Mes actual ---
        ing_mes = Ingreso.objects.filter(
            inquilino=inquilino, fecha__month=mes_actual, fecha__year=año_actual
        ).aggregate(t=Sum('monto'))['t'] or 0
        gas_mes = Gasto.objects.filter(
            inquilino=inquilino, fecha__month=mes_actual, fecha__year=año_actual
        ).aggregate(t=Sum('monto'))['t'] or 0
        context['ingresos_mes'] = ing_mes
        context['gastos_mes'] = gas_mes
        context['ahorro_neto'] = ing_mes - gas_mes

        # --- Mes anterior ---
        ing_ant = Ingreso.objects.filter(
            inquilino=inquilino, fecha__month=mes_anterior, fecha__year=año_anterior
        ).aggregate(t=Sum('monto'))['t'] or 0
        gas_ant = Gasto.objects.filter(
            inquilino=inquilino, fecha__month=mes_anterior, fecha__year=año_anterior
        ).aggregate(t=Sum('monto'))['t'] or 0

        def pct_change(curr, prev):
            if prev:
                return round((curr - prev) / prev * 100, 1)
            return 0

        context['ingreso_cambio'] = pct_change(ing_mes, ing_ant)
        context['gasto_cambio'] = pct_change(gas_mes, gas_ant)
        context['ahorro_cambio'] = pct_change(ing_mes - gas_mes, ing_ant - gas_ant)

        # --- Últimos 6 meses (una sola consulta con TruncMonth) ---
        seis_meses = [hoy - relativedelta(months=i) for i in range(5, -1, -1)]
        inicio_periodo = seis_meses[0]

        ingresos_agg = list(Ingreso.objects.filter(
            inquilino=inquilino, fecha__gte=inicio_periodo, fecha__lte=hoy
        ).annotate(mes=TruncMonth('fecha')).values('mes').annotate(
            total=Sum('monto')
        ))
        gastos_agg = list(Gasto.objects.filter(
            inquilino=inquilino, fecha__gte=inicio_periodo, fecha__lte=hoy
        ).annotate(mes=TruncMonth('fecha')).values('mes').annotate(
            total=Sum('monto')
        ))

        ing_dict = {(r['mes'].year, r['mes'].month): r['total'] for r in ingresos_agg}
        gas_dict = {(r['mes'].year, r['mes'].month): r['total'] for r in gastos_agg}

        labels_meses = []
        income_data = []
        expense_data = []
        savings_data = []
        savings_rows = []

        for m in seis_meses:
            key = (m.year, m.month)
            labels_meses.append(m.strftime('%b'))
            total_ing = float(ing_dict.get(key, 0) or 0)
            total_gas = float(gas_dict.get(key, 0) or 0)
            income_data.append(total_ing)
            expense_data.append(total_gas)
            savings_data.append(total_ing - total_gas)

        for m in reversed(seis_meses):
            key = (m.year, m.month)
            ti = ing_dict.get(key, 0) or 0
            tg = gas_dict.get(key, 0) or 0
            ahorro = ti - tg
            savings_rows.append({
                'mes': m.strftime('%B %Y'),
                'ingresos': ti,
                'gastos': tg,
                'ahorro': ahorro,
                'superavit': ahorro >= 0,
            })

        context['months_json'] = json.dumps(labels_meses)
        context['income_json'] = json.dumps(income_data)
        context['expense_json'] = json.dumps(expense_data)
        context['savings_json'] = json.dumps(savings_data)
        context['savings_rows'] = savings_rows

        # --- Gastos por categoría (mes actual) ---
        gastos_por_cat = Gasto.objects.filter(
            inquilino=inquilino, fecha__month=mes_actual, fecha__year=año_actual
        ).values('categoria__nombre').annotate(
            total=Sum('monto')
        ).order_by('-total')

        total_gastos = sum(g['total'] for g in gastos_por_cat) or 1
        cat_data = []
        for g in gastos_por_cat:
            cat_data.append({
                'label': g['categoria__nombre'] or 'Sin categoría',
                'value': round(float(g['total']) / float(total_gastos) * 100, 1),
                'color': '#1a237e',
            })
        if not cat_data:
            cat_data = [{'label': 'Sin gastos', 'value': 100, 'color': '#e0e0e0'}]

        context['cat_json'] = json.dumps(cat_data)

        # --- Transacciones recientes (con select_related) ---
        movs = []
        for ing in Ingreso.objects.filter(
            inquilino=inquilino
        ).select_related('categoria', 'categoria__icono', 'categoria__color').order_by('-fecha', '-creado')[:10]:
            movs.append({
                'fecha': ing.fecha,
                'creado': ing.creado,
                'comercio': str(ing.categoria) if ing.categoria else 'Ingreso',
                'categoria': str(ing.categoria) if ing.categoria else '',
                'categoria_icono': ing.categoria.icono.clase_css if ing.categoria and ing.categoria.icono_id else 'fa-building-columns',
                'categoria_color': ing.categoria.color.hex if ing.categoria and ing.categoria.color_id else 'var(--inc)',
                'categoria_bg': 'var(--incb)',
                'monto': ing.monto,
                'tipo': 'ingreso',
            })
        for gas in Gasto.objects.filter(
            inquilino=inquilino
        ).select_related('categoria', 'categoria__icono', 'categoria__color').order_by('-fecha', '-creado')[:10]:
            movs.append({
                'fecha': gas.fecha,
                'creado': gas.creado,
                'comercio': str(gas.categoria) if gas.categoria else 'Gasto',
                'categoria': str(gas.categoria) if gas.categoria else '',
                'categoria_icono': gas.categoria.icono.clase_css if gas.categoria and gas.categoria.icono_id else fa_random(),
                'categoria_color': gas.categoria.color.hex if gas.categoria and gas.categoria.color_id else 'var(--exp)',
                'categoria_bg': 'var(--expb)',
                'monto': gas.monto,
                'tipo': 'gasto',
            })
        movs.sort(key=lambda x: (x['fecha'], x['creado']), reverse=True)
        context['recientes'] = movs[:10]

        # --- Próximos pagos tarjetas crédito ---
        tarjetas_credito = Cuenta.objects.filter(
            inquilino=inquilino, tipo='credito', activo=True
        ).exclude(dia_pago='').select_related('color', 'icono')

        proximos_pagos = []
        for t in tarjetas_credito:
            prox = calcular_prox_pago(t)
            if prox is None:
                continue
            days_left = (prox - hoy).days
            if days_left < 0:
                continue
            total_a_pagar = max(t.limite_credito - t.balance, 0)
            proximos_pagos.append({
                'nombre': t.nombre,
                'emisor': t.emisor,
                'color': t.color.hex if t.color_id else '#1a237e',
                'icono': t.icono.clase_css if t.icono_id else 'fa-credit-card',
                'total_a_pagar': total_a_pagar,
                'dia_pago': t.dia_pago,
                'fecha_pago': prox,
                'days_left': days_left,
            })
        proximos_pagos.sort(key=lambda x: x['days_left'])
        context['proximos_pagos'] = proximos_pagos

        return context


def fa_random():
    icons = ['fa-receipt', 'fa-cart-shopping', 'fa-tag', 'fa-circle']
    return random.choice(icons)
