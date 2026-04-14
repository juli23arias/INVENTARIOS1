from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.db.models import ProtectedError, RestrictedError

from usuarios.mixins import AdminRequiredMixin
from .models import Proveedor, Compra, DetalleCompra
from .forms import CompraCreateForm, DetalleCompraForm
from inventario.models import InventarioHistorial

class ProveedorListView(AdminRequiredMixin, ListView):
    model = Proveedor
    template_name = 'proveedores/proveedor_list.html'
    context_object_name = 'proveedores'

class ProveedorCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Proveedor
    template_name = 'proveedores/form_base.html'
    fields = ['nombre', 'contacto', 'telefono', 'email']
    success_url = reverse_lazy('proveedores:list')
    success_message = "Proveedor guardado con éxito."

class ProveedorUpdateView(AdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Proveedor
    template_name = 'proveedores/form_base.html'
    fields = ['nombre', 'contacto', 'telefono', 'email']
    success_url = reverse_lazy('proveedores:list')
    success_message = "Proveedor actualizado con éxito."

class ProveedorDeleteView(AdminRequiredMixin, DeleteView):
    model = Proveedor
    template_name = 'proveedores/proveedor_confirm_delete.html'
    success_url = reverse_lazy('proveedores:list')

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except (ProtectedError, RestrictedError):
            messages.error(request, "Este proveedor tiene compras asociadas y no puede eliminarse.")
            return redirect('proveedores:list')

# ====== COMPRAS ======

class CompraListView(AdminRequiredMixin, ListView):
    model = Compra
    template_name = 'proveedores/compra_list.html'
    context_object_name = 'compras'
    ordering = ['-fecha']

def crear_compra(request):
    if request.method == 'POST':
        form = CompraCreateForm(request.POST)
        if form.is_valid():
            compra = form.save()
            return redirect('proveedores:compra_detalle', pk=compra.pk)
    else:
        form = CompraCreateForm()
    return render(request, 'proveedores/compra_form.html', {'form': form})

def compra_detalle(request, pk):
    compra = get_object_or_404(Compra, pk=pk)
    
    if request.method == 'POST':
        form = DetalleCompraForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                producto = form.cleaned_data['producto']
                cantidad = form.cleaned_data['cantidad']
                precio_compra = form.cleaned_data['precio_compra']
                
                DetalleCompra.objects.create(
                    compra=compra,
                    producto=producto,
                    cantidad=cantidad,
                    precio_compra=precio_compra
                )
                
                # Aumentar stock
                producto.stock += cantidad
                producto.save()
                
                # Registrar Historial
                InventarioHistorial.objects.create(
                    producto=producto,
                    tipo_movimiento='ENTRADA',
                    cantidad=cantidad
                )
            
            messages.success(request, f"Producto agregado a la compra. Stock actualizado (+{cantidad}).")
            return redirect('proveedores:compra_detalle', pk=compra.pk)
    else:
        form = DetalleCompraForm()
        
    context = {
        'compra': compra,
        'detalles': compra.detalles.all(),
        'form': form,
        'total': sum(d.subtotal() for d in compra.detalles.all())
    }
    return render(request, 'proveedores/compra_detalle.html', context)
