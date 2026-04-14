from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('', views.VentaListView.as_view(), name='list'),
    path('crear/', views.crear_venta, name='crear'),
    path('<int:pk>/', views.venta_detalle, name='detalle'),
    path('<int:pk>/factura/', views.FacturaView.as_view(), name='factura'),
    
    # API POS
    path('api/buscar-productos/', views.api_buscar_productos, name='api_buscar_productos'),
    path('api/productos/', views.api_productos, name='api_productos'),
    path('api/agregar-producto/<int:venta_id>/', views.api_agregar_producto, name='api_agregar_producto'),
    path('api/eliminar-detalle/<int:detalle_id>/', views.api_eliminar_detalle, name='api_eliminar_detalle'),
    path('api/finalizar-venta/<int:venta_id>/', views.api_finalizar_venta, name='api_finalizar_venta'),
]
