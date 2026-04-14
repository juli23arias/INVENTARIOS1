from django import forms
from django.core.exceptions import ValidationError
from .models import InventarioHistorial
from productos.models import Producto

class InventarioAjusteForm(forms.ModelForm):
    class Meta:
        model = InventarioHistorial
        fields = ['producto', 'tipo_movimiento', 'cantidad']

    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        tipo_movimiento = cleaned_data.get('tipo_movimiento')
        cantidad = cleaned_data.get('cantidad')

        if producto and tipo_movimiento and cantidad is not None:
            if cantidad <= 0:
                raise ValidationError("La cantidad debe ser mayor a 0.")
            
            if tipo_movimiento in ['SALIDA', 'AJUSTE']:
                # Asumiremos AJUSTE como resta si se quiere quitar (o podemos obligar a usar SALIDA/ENTRADA).
                # Para simplificar, asumimos que SALIDA resta stock.
                if producto.stock - cantidad < 0:
                    raise ValidationError(f"Stock insuficiente. El stock actual es {producto.stock}.")

        return cleaned_data
