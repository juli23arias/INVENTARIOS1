from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

from .models import InventarioHistorial
from productos.models import Producto
from usuarios.mixins import AdminRequiredMixin
from .forms import InventarioAjusteForm

class HistorialListView(AdminRequiredMixin, ListView):
    model = InventarioHistorial
    template_name = 'inventario/historial_list.html'
    context_object_name = 'historial'
    ordering = ['-fecha']

class AjusteCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = InventarioHistorial
    form_class = InventarioAjusteForm
    template_name = 'inventario/ajuste_form.html'
    success_url = reverse_lazy('inventario:historial')
    success_message = "Ajuste de inventario guardado. El stock ha sido modificado."

    def form_valid(self, form):
        response = super().form_valid(form)
        movimiento = self.object
        producto = movimiento.producto
        
        if movimiento.tipo_movimiento == 'ENTRADA':
            producto.stock += movimiento.cantidad
        elif movimiento.tipo_movimiento in ['SALIDA', 'AJUSTE']:
            producto.stock -= movimiento.cantidad
            
        producto.save()
        return response
