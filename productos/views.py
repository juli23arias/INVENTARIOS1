from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.db.models import ProtectedError, RestrictedError

from .models import Producto, Categoria
from usuarios.mixins import AdminRequiredMixin

class ProductoListView(LoginRequiredMixin, ListView):
    model = Producto
    template_name = 'productos/producto_list.html'
    context_object_name = 'productos'
    
    def get_queryset(self):
        qs = Producto.objects.all()
        q = self.request.GET.get('q', '').strip()
        cat = self.request.GET.get('cat', '').strip()
        if q:
            qs = qs.filter(nombre__icontains=q)
        if cat:
            qs = qs.filter(categoria__nombre__icontains=cat)
        return qs.order_by('nombre')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass unique category names to template for filter dropdown
        context['categorias'] = Categoria.objects.all().order_by('nombre')
        context['q_val'] = self.request.GET.get('q', '')
        context['cat_val'] = self.request.GET.get('cat', '')
        return context

class ProductoCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Producto
    template_name = 'productos/producto_form.html'
    fields = ['nombre', 'descripcion', 'categoria', 'precio', 'stock', 'stock_minimo', 'imagen']
    success_url = reverse_lazy('productos:list')
    success_message = "Producto '%(nombre)s' creado con éxito."

class ProductoUpdateView(AdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Producto
    template_name = 'productos/producto_form.html'
    fields = ['nombre', 'descripcion', 'categoria', 'precio', 'stock', 'stock_minimo', 'imagen']
    success_url = reverse_lazy('productos:list')
    success_message = "Producto '%(nombre)s' actualizado con éxito."

    def form_valid(self, form):
        # Obtener el objeto original antes de guardar
        original_obj = self.get_object()
        old_name = original_obj.nombre
        new_name = form.cleaned_data.get('nombre')

        response = super().form_valid(form)

        # Si el nombre cambió de forma significativa, agregar advertencia
        if old_name != new_name:
            messages.warning(
                self.request, 
                f"⚠️ Has cambiado el título de '{old_name}' a '{new_name}'. "
                "Recuerda revisar que la descripción coincida con el nuevo nombre."
            )
        
        return response

class ProductoDeleteView(AdminRequiredMixin, DeleteView):
    model = Producto
    template_name = 'productos/producto_confirm_delete.html'
    success_url = reverse_lazy('productos:list')

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except (ProtectedError, RestrictedError):
            messages.error(request, "No se puede eliminar este producto porque tiene historial, compras o ventas asociadas.")
            return redirect('productos:list')
