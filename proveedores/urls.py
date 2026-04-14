from django.urls import path
from . import views

app_name = 'proveedores'

urlpatterns = [
    # Proveedores
    path('', views.ProveedorListView.as_view(), name='list'),
    path('crear/', views.ProveedorCreateView.as_view(), name='create'),
    path('<int:pk>/editar/', views.ProveedorUpdateView.as_view(), name='update'),
    path('<int:pk>/eliminar/', views.ProveedorDeleteView.as_view(), name='delete'),
    
    # Compras
    path('compras/', views.CompraListView.as_view(), name='compras_list'),
    path('compras/crear/', views.crear_compra, name='compra_crear'),
    path('compras/<int:pk>/', views.compra_detalle, name='compra_detalle'),
]
