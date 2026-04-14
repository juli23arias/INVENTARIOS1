from django.db import models
from productos.models import Producto

class Proveedor(models.Model):
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    contacto = models.CharField(max_length=200, blank=True, null=True, verbose_name="Contacto")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, null=True, verbose_name="Correo Electrónico")

    def __str__(self):
        return self.nombre

class Compra(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.RESTRICT, related_name="compras")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")
    
    def __str__(self):
        return f"Compra {self.id} - {self.proveedor.nombre}"

class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.RESTRICT, related_name="detalles_compra")
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad")
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Compra")

    def subtotal(self):
        return self.cantidad * self.precio_compra
