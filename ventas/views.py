from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.db.models import Q
import json

from .models import Venta, DetalleVenta
from .forms import DetalleVentaForm
from inventario.models import InventarioHistorial
from productos.models import Producto, Categoria

class VentaListView(LoginRequiredMixin, ListView):
    model = Venta
    template_name = 'ventas/venta_list.html'
    context_object_name = 'ventas'
    ordering = ['-fecha']

@login_required
def crear_venta(request):
    """Crea una venta en blanco y redirige al POS para añadir productos."""
    if request.user.rol == 'ADMIN':
        messages.error(request, "Los Administradores no pueden registrar ventas.")
        return redirect('ventas:list')
    venta = Venta.objects.create(usuario=request.user)
    return redirect('ventas:detalle', pk=venta.pk)

@login_required
def venta_detalle(request, pk):
    """Vista tipo Point of Sale, permite agregar detalles a una venta activa."""
    if request.user.rol == 'ADMIN':
        messages.error(request, "Los Administradores no pueden interactuar con el TPV.")
        return redirect('ventas:list')
        
    venta = get_object_or_404(Venta, pk=pk)
    
    if request.method == 'POST':
        form = DetalleVentaForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                producto = form.cleaned_data['producto']
                cantidad = form.cleaned_data['cantidad']
                precio_unitario = producto.precio
                
                # Crear el detalle
                detalle = DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario
                )
                
                # Actualizar totales
                venta.total += detalle.subtotal()
                venta.save()
                
                # Restar stock
                producto.stock -= cantidad
                producto.save()
                
                # Crear historial de inventario
                InventarioHistorial.objects.create(
                    producto=producto,
                    tipo_movimiento='SALIDA',
                    cantidad=cantidad
                )
                
            messages.success(request, f"Agregado {cantidad} x {producto.nombre} a la venta.")
            return redirect('ventas:detalle', pk=venta.pk)
    else:
        form = DetalleVentaForm()

    categorias = Categoria.objects.filter(productos__stock__gt=0).distinct()
    context = {
        'venta': venta,
        'detalles': venta.detalles.all(),
        'form': form,
        'categorias': categorias
    }
    return render(request, 'ventas/venta_detalle.html', context)

class FacturaView(LoginRequiredMixin, DetailView):
    model = Venta
    template_name = 'ventas/factura.html'
    context_object_name = 'venta'

# --- API POS ENDPOINTS ---

@login_required
def api_buscar_productos(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'results': []})
    
    productos = Producto.objects.filter(
        Q(nombre__icontains=query) | Q(pk__icontains=query),
        stock__gt=0
    )[:10]
    
    results = [{
        'id': p.id,
        'nombre': p.nombre,
        'precio': float(p.precio),
        'stock': p.stock,
        'categoria': p.categoria.nombre if p.categoria else 'Sin Categoría'
    } for p in productos]
    
    return JsonResponse({'results': results})

@login_required
def api_productos(request):
    """Retorna todos los productos o filtrados por categoría en JSON."""
    categoria = request.GET.get('categoria', '').strip()
    query = request.GET.get('q', '').strip()
    
    productos = Producto.objects.filter(stock__gt=0)
    
    if categoria:
        productos = productos.filter(categoria=categoria)
    if query:
        productos = productos.filter(nombre__icontains=query)
        
    results = [{
        'id': p.id,
        'nombre': p.nombre,
        'precio': float(p.precio),
        'stock': p.stock,
        'categoria': p.categoria.nombre if p.categoria else 'Sin Categoría',
        'imagen_url': p.imagen.url if p.imagen else '/static/img/no-image.png'
    } for p in productos[:50]] # Limit to 50 for performance
    
    return JsonResponse({'results': results})

@login_required
@transaction.atomic
def api_agregar_producto(request, venta_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        producto_id = data.get('producto_id')
        cantidad = int(data.get('cantidad', 1))
        
        venta = get_object_or_404(Venta, pk=venta_id)
        producto = get_object_or_404(Producto, pk=producto_id)
        
        if producto.stock < cantidad:
            return JsonResponse({'error': f'Stock insuficiente para {producto.nombre}'}, status=400)
        
        # Crear o actualizar detalle
        detalle, created = DetalleVenta.objects.get_or_create(
            venta=venta,
            producto=producto,
            defaults={'cantidad': 0, 'precio_unitario': producto.precio}
        )
        
        detalle.cantidad += cantidad
        detalle.save()
        
        # Actualizar totales
        venta.total += (producto.precio * cantidad)
        venta.save()
        
        # Restar stock
        producto.stock -= cantidad
        producto.save()
        
        # Log Inventario
        InventarioHistorial.objects.create(
            producto=producto,
            tipo_movimiento='SALIDA',
            cantidad=cantidad
        )
        
        return JsonResponse({
            'success': True,
            'item': {
                'id': detalle.id,
                'producto': producto.nombre,
                'cantidad': detalle.cantidad,
                'precio': float(detalle.precio_unitario),
                'subtotal': float(detalle.subtotal())
            },
            'venta_total': float(venta.total)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@transaction.atomic
def api_eliminar_detalle(request, detalle_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    detalle = get_object_or_404(DetalleVenta, pk=detalle_id)
    venta = detalle.venta
    producto = detalle.producto
    
    # Reversar stock
    producto.stock += detalle.cantidad
    producto.save()
    
    # Actualizar total venta
    venta.total -= detalle.subtotal()
    venta.save()
    
    # Log Inventario (Entrada por cancelación)
    InventarioHistorial.objects.create(
        producto=producto,
        tipo_movimiento='ENTRADA',
        cantidad=detalle.cantidad
    )
    
    detalle.delete()
    
    return JsonResponse({
        'success': True,
        'venta_total': float(venta.total)
    })

@login_required
@transaction.atomic
def api_finalizar_venta(request, venta_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        venta = get_object_or_404(Venta, pk=venta_id)
        
        venta.metodo_pago = data.get('metodo_pago', 'EFECTIVO')
        venta.monto_recibido = data.get('monto_recibido', venta.total)
        venta.monto_cambio = data.get('monto_cambio', 0)
        venta.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
