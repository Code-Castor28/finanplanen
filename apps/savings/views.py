from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class AhorroLista(LoginRequiredMixin, TemplateView):
    template_name = 'savings/ahoro.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'savings'
        return context
