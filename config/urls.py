from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from config import views
from usuarios import views as usuarios_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.IndexRedirectView.as_view(), name='index'),
    path('dashboard/admin/', views.DashboardAdminView.as_view(), name='dashboard_admin'),
    path('dashboard/admin/estadisticas/', views.EstadisticasAdminView.as_view(), name='dashboard_stats'),
    path('dashboard/admin/export/', views.export_report_csv, name='export_report_csv'),
    path('dashboard/cajero/', views.DashboardCajeroView.as_view(), name='dashboard_cajero'),
    path('login/', usuarios_views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    path('usuarios/', include('usuarios.urls')),
    
    path('productos/', include('productos.urls')),
    path('inventario/', include('inventario.urls')),
    path('ventas/', include('ventas.urls')),
    path('proveedores/', include('proveedores.urls')),
    path('clientes/', include('clientes.urls')),
]
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
