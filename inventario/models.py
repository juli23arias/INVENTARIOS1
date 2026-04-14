from django.db import models
from productos.models import Producto

class InventarioHistorial(models.Model):
    TIPO_MOVIMIENTO = (
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
        ('AJUSTE', 'Ajuste Manual'),
    )
    producto = models.ForeignKey(Producto, on_delete=models.RESTRICT, related_name="historial_inventario")
    tipo_movimiento = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO, verbose_name="Tipo de Movimiento")
    cantidad = models.IntegerField(verbose_name="Cantidad")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")

    def __str__(self):
        return f"{self.producto.nombre} | {self.get_tipo_movimiento_display()} | {self.cantidad}"
