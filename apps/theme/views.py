from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import ColorForm, IconoForm
from .models import Color, Icono


class InquilinoMixin(LoginRequiredMixin):
    def get_queryset(self):
        return self.model.objects.filter(inquilino=self.request.user.inquilino)

    def form_valid(self, form):
        if hasattr(form, 'instance'):
            form.instance.inquilino = self.request.user.inquilino
            form.instance.usuario = self.request.user
        return super().form_valid(form)


class ColorLista(InquilinoMixin, ListView):
    model = Color
    context_object_name = 'colores'

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['theme/_lista_colores.html']
        return ['theme/colores.html']


class ColorCrear(InquilinoMixin, CreateView):
    model = Color
    form_class = ColorForm
    template_name = 'theme/_form_color.html'

    def get_success_url(self):
        return reverse_lazy('theme:colores_lista')

    def form_valid(self, form):
        super().form_valid(form)
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return self.render_to_response(self.get_context_data(form=form), status=422)
        return super().form_invalid(form)


class ColorEditar(InquilinoMixin, UpdateView):
    model = Color
    form_class = ColorForm
    template_name = 'theme/_form_color.html'

    def get_success_url(self):
        return reverse_lazy('theme:colores_lista')

    def form_valid(self, form):
        super().form_valid(form)
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return self.render_to_response(self.get_context_data(form=form), status=422)
        return super().form_invalid(form)


class ColorEliminar(InquilinoMixin, DeleteView):
    model = Color
    template_name = 'theme/_confirmar_eliminar.html'

    def get_success_url(self):
        return reverse_lazy('theme:colores_lista')

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.delete()
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['model_name'] = 'color'
        return ctx


class IconoLista(InquilinoMixin, ListView):
    model = Icono
    context_object_name = 'iconos'

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['theme/_lista_iconos.html']
        return ['theme/iconos.html']


class IconoCrear(InquilinoMixin, CreateView):
    model = Icono
    form_class = IconoForm
    template_name = 'theme/_form_icono.html'

    def get_success_url(self):
        return reverse_lazy('theme:iconos_lista')

    def form_valid(self, form):
        super().form_valid(form)
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return self.render_to_response(self.get_context_data(form=form), status=422)
        return super().form_invalid(form)


class IconoEditar(InquilinoMixin, UpdateView):
    model = Icono
    form_class = IconoForm
    template_name = 'theme/_form_icono.html'

    def get_success_url(self):
        return reverse_lazy('theme:iconos_lista')

    def form_valid(self, form):
        super().form_valid(form)
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return self.render_to_response(self.get_context_data(form=form), status=422)
        return super().form_invalid(form)


class IconoEliminar(InquilinoMixin, DeleteView):
    model = Icono
    template_name = 'theme/_confirmar_eliminar.html'

    def get_success_url(self):
        return reverse_lazy('theme:iconos_lista')

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.delete()
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['model_name'] = 'icono'
        return ctx
