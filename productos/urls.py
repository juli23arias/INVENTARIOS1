from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.ProductoListView.as_view(), name='list'),
    path('crear/', views.ProductoCreateView.as_view(), name='create'),
    path('<int:pk>/editar/', views.ProductoUpdateView.as_view(), name='update'),
    path('<int:pk>/eliminar/', views.ProductoDeleteView.as_view(), name='delete'),
]
