from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class PresupuestoLista(LoginRequiredMixin, TemplateView):
    template_name = 'budgets/presupuesto.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'budgets'
        return context
