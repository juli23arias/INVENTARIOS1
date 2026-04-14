from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('historial/', views.HistorialListView.as_view(), name='historial'),
    path('ajustar/', views.AjusteCreateView.as_view(), name='ajustar'),
]
