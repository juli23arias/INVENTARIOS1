from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    path('dashboard/', views.dashboard_cliente, name='dashboard'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('carrito/', views.ver_carrito, name='carrito'),
    path('add/<int:producto_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:producto_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('ajax/cart/update/', views.api_cart_update, name='api_cart_update'),
    path('mis-pedidos/', views.mis_pedidos, name='pedidos'),
]
