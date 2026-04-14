from django.contrib import admin
from .models import InventarioHistorial

@admin.register(InventarioHistorial)
class InventarioHistorialAdmin(admin.ModelAdmin):
    list_display = ('producto', 'tipo_movimiento', 'cantidad', 'fecha')
    list_filter = ('tipo_movimiento', 'fecha')
    search_fields = ('producto__nombre',)
