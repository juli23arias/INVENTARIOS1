from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Sum, Count
from django.utils import timezone
from django.http import HttpResponse
import json
import csv

from productos.models import Producto
from usuarios.mixins import AdminRequiredMixin
from usuarios.models import Usuario
from ventas.models import Venta, DetalleVenta
from clientes.models import Pedido, DetallePedido
from django.db.models.functions import TruncDate

# Redirigir el / base si un usuario entra
class IndexRedirectView(TemplateView):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.rol == 'ADMIN':
            return redirect('dashboard_admin')
        elif request.user.rol == 'CLIENTE':
            return redirect('clientes:dashboard')
        return redirect('dashboard_cajero')

import json
import csv

class DashboardAdminView(AdminRequiredMixin, TemplateView):
    template_name = 'dashboard_admin.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        
        # 1. Alertas de stock bajo
        alertas = Producto.objects.filter(stock__lte=F('stock_minimo'))
        context['alertas_stock'] = alertas
        context['count_stock_bajo'] = alertas.count()
        
        # 2. Métricas generales
        context['total_usuarios'] = Usuario.objects.count()
        context['total_productos'] = Producto.objects.count()
        # Ventas del día (Últimas 24 horas para mayor dinamismo)
        since_24h = timezone.now() - timezone.timedelta(days=1)
        
        ventas_hoy_tpv = Venta.objects.filter(fecha__gte=since_24h, total__gt=0).aggregate(Sum('total'))['total__sum'] or 0
        ventas_hoy_online = Pedido.objects.filter(fecha__gte=since_24h).exclude(estado='CANCELADO').aggregate(Sum('total'))['total__sum'] or 0
        context['ventas_dia_total'] = ventas_hoy_tpv + ventas_hoy_online
        
        return context

class EstadisticasAdminView(AdminRequiredMixin, TemplateView):
    template_name = 'admin_estadisticas.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Datos para Gráficas (Chart.js)
        # Combinamos datos de Venta (Caja) y Pedido (Online)
        from itertools import chain
        from operator import itemgetter

        # 1. Ventas por día (Combinado)
        v_dia = Venta.objects.annotate(dia=TruncDate('fecha')).values('dia').annotate(count=Count('id'))
        p_dia = Pedido.objects.exclude(estado='CANCELADO').annotate(dia=TruncDate('fecha')).values('dia').annotate(count=Count('id'))
        
        # Agrupar por día
        combined_days = {}
        for item in v_dia: combined_days[item['dia']] = combined_days.get(item['dia'], 0) + item['count']
        for item in p_dia: combined_days[item['dia']] = combined_days.get(item['dia'], 0) + item['count']
        
        sorted_days = sorted(combined_days.items(), key=itemgetter(0))[-7:]
        context['chart_ventas_dia'] = json.dumps({
            'labels': [d[0].strftime('%d/%m') for d in sorted_days],
            'data': [d[1] for d in sorted_days]
        })

        # 2. Ingresos en el tiempo (Combinado)
        v_ingresos = Venta.objects.annotate(dia=TruncDate('fecha')).values('dia').annotate(total=Sum('total'))
        p_ingresos = Pedido.objects.exclude(estado='CANCELADO').annotate(dia=TruncDate('fecha')).values('dia').annotate(total=Sum('total'))
        
        combined_ingresos = {}
        for item in v_ingresos: combined_ingresos[item['dia']] = combined_ingresos.get(item['dia'], 0) + float(item['total'])
        for item in p_ingresos: combined_ingresos[item['dia']] = combined_ingresos.get(item['dia'], 0) + float(item['total'])
        
        sorted_ingresos = sorted(combined_ingresos.items(), key=itemgetter(0))[-7:]
        context['chart_ingresos'] = json.dumps({
            'labels': [d[0].strftime('%d/%m') for d in sorted_ingresos],
            'data': [d[1] for d in sorted_ingresos]
        })

        # 3. Ventas por categoría (Combinado)
        v_cat = DetalleVenta.objects.values('producto__categoria__nombre').annotate(total=Sum('cantidad'))
        p_cat = DetallePedido.objects.exclude(pedido__estado='CANCELADO').values('producto__categoria__nombre').annotate(total=Sum('cantidad'))
        
        combined_cat = {}
        for item in v_cat:
            name = item['producto__categoria__nombre'] or 'Sin Categoría'
            combined_cat[name] = combined_cat.get(name, 0) + item['total']
        for item in p_cat:
            name = item['producto__categoria__nombre'] or 'Sin Categoría'
            combined_cat[name] = combined_cat.get(name, 0) + item['total']
            
        context['chart_categorias'] = json.dumps({
            'labels': list(combined_cat.keys()),
            'data': list(combined_cat.values())
        })

        # 4. Productos más vendidos (Combinado)
        v_top = DetalleVenta.objects.values('producto__nombre').annotate(total=Sum('cantidad'))
        p_top = DetallePedido.objects.exclude(pedido__estado='CANCELADO').values('producto__nombre').annotate(total=Sum('cantidad'))
        
        combined_top = {}
        for item in v_top: combined_top[item['producto__nombre']] = combined_top.get(item['producto__nombre'], 0) + item['total']
        for item in p_top: combined_top[item['producto__nombre']] = combined_top.get(item['producto__nombre'], 0) + item['total']
        
        sorted_top = sorted(combined_top.items(), key=itemgetter(1), reverse=True)[:5]
        context['chart_top_productos'] = json.dumps({
            'labels': [x[0] for x in sorted_top],
            'data': [x[1] for x in sorted_top]
        })

        # 5. Métodos de pago (Combinado)
        metodos = Venta.objects.values('metodo_pago').annotate(count=Count('id'))
        pedidos_count = Pedido.objects.exclude(estado='CANCELADO').count()
        
        labels = [v['metodo_pago'] for v in metodos] + ['ONLINE (Pedido)']
        data = [v['count'] for v in metodos] + [pedidos_count]
        
        context['chart_metodos'] = json.dumps({
            'labels': labels,
            'data': data
        })
        
        return context

def export_report_csv(request):
    """Exporta un reporte básico de ventas a CSV."""
    if not request.user.is_authenticated or request.user.rol != 'ADMIN':
        return HttpResponse("No autorizado", status=401)
        
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_ventas.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID Venta', 'Fecha', 'Usuario', 'Método Pago', 'Total'])
    
    ventas = Venta.objects.all().order_by('-fecha')
    for v in ventas:
        writer.writerow([v.id, v.fecha.strftime('%Y-%m-%d %H:%M'), v.usuario.username if v.usuario else 'N/A', v.metodo_pago, v.total])
        
    return response



class DashboardCajeroView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard_cajero.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        # Ventas del día
        ventas_hoy = Venta.objects.filter(fecha__date=today)
        context['ventas_dia_total'] = ventas_hoy.aggregate(Sum('total'))['total__sum'] or 0
        context['ventas_dia_count'] = ventas_hoy.count()
        
        # Total productos en inventario (Suma de stock)
        context['total_stock'] = Producto.objects.aggregate(Sum('stock'))['stock__sum'] or 0
        
        # Producto más vendido (Top 1)
        top_vuelto = DetalleVenta.objects.values('producto__nombre').annotate(
            total_vendido=Sum('cantidad')
        ).order_by('-total_vendido').first()
        context['top_producto'] = top_vuelto['producto__nombre'] if top_vuelto else "N/A"
        
        # Actividad Reciente (Últimas 5 ventas)
        context['ultimas_ventas'] = Venta.objects.all().order_by('-fecha')[:5]
        
        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.rol != 'CAJERO' and request.user.rol != 'ADMIN':
             return redirect('login')
        return super().dispatch(request, *args, **kwargs)
