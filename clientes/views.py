from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from decimal import Decimal

from usuarios.mixins import ClienteRequiredMixin
from productos.models import Producto, Categoria
from clientes.models import Pedido, DetallePedido

import qrcode
import base64
from io import BytesIO

@login_required
def dashboard_cliente(request):
    """Vista principal (Dashboard) para Clientes."""
    if request.user.rol != 'CLIENTE':
        return redirect('index')
    
    # Generar QR dinámicamente que apunte al Catálogo
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    # Suponiendo base root, redirige a catalogo 
    qr.add_data(f"http://{request.get_host()}/clientes/catalogo/") 
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    qr_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    # Datos para el Dashboard
    ultimos_pedidos = request.user.pedidos.all().order_by('-fecha')[:5]
    total_pedidos = request.user.pedidos.count()
    recomendados = Producto.objects.filter(stock__gt=0).order_by('?')[:4]
    carrito_count = len(request.session.get('carrito', {}))
    
    puntos = request.user.puntos
    puntos_meta = 1000  # Meta para barra de progreso
    progreso = min(int((puntos / puntos_meta) * 100), 100)
    
    context = {
        'qr_image': qr_b64,
        'pedidos': ultimos_pedidos,
        'total_pedidos': total_pedidos,
        'puntos': puntos,
        'valor_puntos': float(puntos) * 100.0, # 1 punto = $100 COP
        'puntos_meta': puntos_meta,
        'progreso': progreso,
        'recomendados': recomendados,
        'carrito_count': carrito_count,
    }
    return render(request, 'clientes/dashboard.html', context)

@login_required
def catalogo(request):
    if request.user.rol != 'CLIENTE': return redirect('index')
    
    qs = Producto.objects.filter(stock__gt=0).order_by('nombre')
    
    # Filtro por categoría
    cat_id = request.GET.get('categoria')
    if cat_id:
        qs = qs.filter(categoria_id=cat_id)
        
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(nombre__icontains=q)
        
    context = {
        'productos': qs,
        'q_val': q,
        'cat_id': cat_id,
        'categorias': Categoria.objects.all()
    }
    return render(request, 'clientes/catalogo.html', context)

@login_required
def ver_carrito(request):
    if request.user.rol != 'CLIENTE': return redirect('index')
    carrito = request.session.get('carrito', {})
    
    items = []
    subtotal_general = Decimal('0.00')
    for prod_id, cantidad in carrito.items():
        try:
            prod = Producto.objects.get(id=prod_id)
            subtotal_item = prod.precio * cantidad
            subtotal_general += subtotal_item
            items.append({
                'producto': prod,
                'cantidad': cantidad,
                'subtotal': subtotal_item
            })
        except Producto.DoesNotExist:
            continue
            
    puntos_disponibles = request.user.puntos
    valor_puntos = Decimal(str(puntos_disponibles)) * Decimal('100.00')
    
    # Lógica de Envío (NUEVO)
    ENVIO_BASE = Decimal('8500.00')
    UMBRAL_GRATIS = Decimal('50000.00')
    
    costo_envio = Decimal('0.00') if subtotal_general >= UMBRAL_GRATIS else ENVIO_BASE
    if not items: costo_envio = Decimal('0.00') # Carrito vacío
    
    restante_gratis = max(UMBRAL_GRATIS - subtotal_general, Decimal('0.00'))
    progreso_envio = min(int((subtotal_general / UMBRAL_GRATIS) * 100), 100)
    
    # Descuento Puntos
    descuento_puntos = min(valor_puntos, subtotal_general + costo_envio)
    total_recalculado = (subtotal_general + costo_envio)
    total_con_descuento = total_recalculado - descuento_puntos
    
    context = {
        'items': items,
        'subtotal': subtotal_general,
        'costo_envio': costo_envio,
        'umbral_envio': UMBRAL_GRATIS,
        'restante_envio_gratis': restante_gratis,
        'progreso_envio': progreso_envio,
        'puntos_disponibles': puntos_disponibles,
        'valor_puntos_pesos': valor_puntos,
        'descuento_puntos': descuento_puntos,
        'total_final': total_con_descuento
    }
    return render(request, 'clientes/carrito.html', context)

@login_required
def api_cart_update(request):
    if request.method == 'POST':
        prod_id = request.POST.get('producto_id')
        action = request.POST.get('action') # 'plus' or 'minus'
        
        carrito = request.session.get('carrito', {})
        if prod_id in carrito:
            producto = get_object_or_404(Producto, id=prod_id)
            if action == 'plus':
                if carrito[prod_id] < producto.stock:
                    carrito[prod_id] += 1
                else:
                    return JsonResponse({'status': 'error', 'message': 'Máximo stock alcanzado'})
            elif action == 'minus':
                if carrito[prod_id] > 1:
                    carrito[prod_id] -= 1
                else:
                    del carrito[prod_id]
            
            request.session['carrito'] = carrito
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@login_required
def add_to_cart(request, producto_id):
    if request.user.rol != 'CLIENTE': return redirect('index')
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        
        # Validar en base al carro actual
        carrito = request.session.get('carrito', {})
        str_id = str(producto_id)
        
        cant_actual = carrito.get(str_id, 0)
        nueva_cantidad = cant_actual + cantidad
        
        if nueva_cantidad > producto.stock:
            messages.error(request, f"¡Stock insuficiente! Solo quedan {producto.stock} uds.")
        else:
            carrito[str_id] = nueva_cantidad
            request.session['carrito'] = carrito
            messages.success(request, f"{cantidad}x {producto.nombre} añadido al carrito.")
            
    return redirect('clientes:catalogo')

@login_required
def remove_from_cart(request, producto_id):
    if request.user.rol != 'CLIENTE': return redirect('index')
    carrito = request.session.get('carrito', {})
    str_id = str(producto_id)
    
    if str_id in carrito:
        del carrito[str_id]
        request.session['carrito'] = carrito
        messages.success(request, "Producto removido del carrito.")
        
    return redirect('clientes:carrito')

@login_required
def checkout(request):
    if request.user.rol != 'CLIENTE': return redirect('index')
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, "Tu carrito está vacío.")
        return redirect('clientes:catalogo')
        
    if request.method == 'POST':
        usar_puntos = 'usar_puntos' in request.POST
        
        try:
            with transaction.atomic():
                pedido = Pedido.objects.create(
                    usuario=request.user,
                    estado='PENDIENTE'
                )
                
                subtotal_venta = Decimal('0.00')
                for prod_id, cantidad in carrito.items():
                    prod = Producto.objects.select_for_update().get(id=prod_id)
                    if prod.stock < cantidad:
                        raise ValueError(f"Stock insuficiente para {prod.nombre}.")
                    
                    subtotal_item = prod.precio * cantidad
                    subtotal_venta += subtotal_item
                    
                    prod.stock -= cantidad
                    prod.save()
                    
                    DetallePedido.objects.create(
                        pedido=pedido,
                        producto=prod,
                        cantidad=cantidad,
                        precio_unitario=prod.precio
                    )
                
                # Manejo de Envío
                UMBRAL_GRATIS = Decimal('50000.00')
                ENVIO_BASE = Decimal('8500.00')
                costo_envio = Decimal('0.00') if subtotal_venta >= UMBRAL_GRATIS else ENVIO_BASE
                
                # Manejo de Puntos (1 punto = $100 COP)
                descuento = Decimal('0.00')
                puntos_gastados = 0
                total_antes_puntos = subtotal_venta + costo_envio
                
                if usar_puntos and request.user.puntos > 0:
                    valor_max_descuento = Decimal(str(request.user.puntos)) * Decimal('100.00')
                    
                    if valor_max_descuento > total_antes_puntos:
                        descuento = total_antes_puntos
                        puntos_gastados = int(total_antes_puntos / Decimal('100.00'))
                    else:
                        descuento = valor_max_descuento
                        puntos_gastados = request.user.puntos
                    
                    request.user.puntos -= puntos_gastados
                    pedido.puntos_gastados = puntos_gastados

                total_final = total_antes_puntos - descuento
                pedido.total = total_final
                # Earning: 1 pt per $1000 spent
                puntos_ganados = int(total_final // Decimal('1000'))
                request.user.puntos += puntos_ganados
                request.user.save()
                
                pedido.puntos_ganados = puntos_ganados
                pedido.save()
                
                # Limpiar carrito
                request.session['carrito'] = {}
                messages.success(request, f"¡Súper! Pedido #{pedido.id} completado. (+{puntos_ganados} Pts)")
                return redirect('clientes:dashboard')
                
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('clientes:carrito')
            
    return redirect('clientes:carrito')

@login_required
def mis_pedidos(request):
    if request.user.rol != 'CLIENTE': return redirect('index')
    pedidos = request.user.pedidos.all().order_by('-fecha')
    return render(request, 'clientes/pedidos.html', {'pedidos': pedidos})
