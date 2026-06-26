from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import CategoriaForm, EtiquetaForm
from .models import Categoria, Etiqueta


class InquilinoMixin(LoginRequiredMixin):
    def get_queryset(self):
        return self.model.objects.filter(inquilino=self.request.user.inquilino)

    def form_valid(self, form):
        if hasattr(form, 'instance'):
            form.instance.inquilino = self.request.user.inquilino
            form.instance.usuario = self.request.user
        return super().form_valid(form)


class CategoriaLista(InquilinoMixin, ListView):
    model = Categoria
    context_object_name = 'categorias'

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['categories/_lista_categorias.html']
        return ['categories/categoria.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'categories'
        return context


class CategoriaCrear(InquilinoMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'categories/_form_categoria.html'

    def get_success_url(self):
        return reverse_lazy('categories:lista')

    def form_valid(self, form):
        super().form_valid(form)
        messages.success(self.request, 'Categoría creada correctamente.')
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return self.render_to_response(self.get_context_data(form=form), status=422)
        return super().form_invalid(form)


class CategoriaEditar(InquilinoMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'categories/_form_categoria.html'

    def get_success_url(self):
        return reverse_lazy('categories:lista')

    def form_valid(self, form):
        super().form_valid(form)
        messages.success(self.request, 'Categoría actualizada correctamente.')
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return self.render_to_response(self.get_context_data(form=form), status=422)
        return super().form_invalid(form)


class CategoriaEliminar(InquilinoMixin, DeleteView):
    model = Categoria
    template_name = 'theme/_confirmar_eliminar.html'

    def get_success_url(self):
        return reverse_lazy('categories:lista')

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.delete()
        messages.success(self.request, 'Categoría eliminada correctamente.')
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['model_name'] = 'categoría'
        return ctx


class EtiquetaLista(InquilinoMixin, ListView):
    model = Etiqueta
    context_object_name = 'etiquetas'
    template_name = 'categories/_lista_etiquetas.html'


class EtiquetaCrear(InquilinoMixin, CreateView):
    model = Etiqueta
    form_class = EtiquetaForm
    template_name = 'categories/_form_etiqueta.html'

    def get_success_url(self):
        return reverse_lazy('categories:lista')

    def form_valid(self, form):
        super().form_valid(form)
        messages.success(self.request, 'Etiqueta creada correctamente.')
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return self.render_to_response(self.get_context_data(form=form), status=422)
        return super().form_invalid(form)


class EtiquetaEditar(InquilinoMixin, UpdateView):
    model = Etiqueta
    form_class = EtiquetaForm
    template_name = 'categories/_form_etiqueta.html'

    def get_success_url(self):
        return reverse_lazy('categories:lista')

    def form_valid(self, form):
        super().form_valid(form)
        messages.success(self.request, 'Etiqueta actualizada correctamente.')
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            return self.render_to_response(self.get_context_data(form=form), status=422)
        return super().form_invalid(form)


class EtiquetaEliminar(InquilinoMixin, DeleteView):
    model = Etiqueta
    template_name = 'theme/_confirmar_eliminar.html'

    def get_success_url(self):
        return reverse_lazy('categories:lista')

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.delete()
        messages.success(self.request, 'Etiqueta eliminada correctamente.')
        response = HttpResponse()
        response['HX-Redirect'] = self.get_success_url()
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['model_name'] = 'etiqueta'
        return ctx
