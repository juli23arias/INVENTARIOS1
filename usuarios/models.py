from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    ROLES = (
        ('ADMIN', 'Administrador'),
        ('CAJERO', 'Cajero'),
        ('CLIENTE', 'Cliente'),
    )
    rol = models.CharField(max_length=10, choices=ROLES, default='CAJERO')
    puntos = models.PositiveIntegerField(default=0, verbose_name="Puntos Acumulados")

    def __str__(self):
        return f"{self.username} - {self.get_rol_display()}"
