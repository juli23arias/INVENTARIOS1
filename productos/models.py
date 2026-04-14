from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    icono = models.CharField(max_length=50, default="bi-tag", help_text="Clase de Bootstrap Icon (ej: bi-cup-hot)")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

class Producto(models.Model):
    nombre = models.CharField(max_length=200, unique=True, verbose_name="Nombre")
    descripcion = models.TextField(verbose_name="Descripción", default="Sin descripción")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock")
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Categoría", related_name="productos")
    stock_minimo = models.PositiveIntegerField(default=0, verbose_name="Stock Mínimo")
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True, verbose_name="Imagen")
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.nombre
