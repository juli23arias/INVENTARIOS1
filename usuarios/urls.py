from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('registro/', views.RegisterView.as_view(), name='registro'),
    path('dashboard/admin/usuarios/', views.UserListView.as_view(), name='list'),
    path('dashboard/admin/usuarios/editar/<int:pk>/', views.UserUpdateView.as_view(), name='editar'),
]
