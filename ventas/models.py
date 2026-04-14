from django.db import models
from productos.models import Producto
from usuarios.models import Usuario

class Venta(models.Model):
    METODOS_PAGO = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA', 'Tarjeta'),
    ]
    usuario = models.ForeignKey(Usuario, on_delete=models.RESTRICT, null=True)
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Total")
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, default='EFECTIVO', verbose_name="Método de Pago")
    monto_recibido = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Monto Recibido")
    monto_cambio = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Cambio")

    def __str__(self):
        return f"Venta #{self.id} - {self.fecha.strftime('%Y-%m-%d %H:%M')}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.RESTRICT, related_name="detalles_venta")
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario")

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

    def subtotal(self):
        return self.cantidad * self.precio_unitario
