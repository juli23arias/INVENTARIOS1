from django import forms
from .models import DetalleVenta
from productos.models import Producto

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar solo productos con stock > 0
        self.fields['producto'].queryset = Producto.objects.filter(stock__gt=0).order_by('nombre')
        # Agregar información de stock al nombre en el select
        self.fields['producto'].label_from_instance = lambda obj: f"{obj.nombre} - ${obj.precio} (Stock: {obj.stock})"

    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad')

        if producto and cantidad is not None:
            if cantidad <= 0:
                raise forms.ValidationError("La cantidad debe ser mayor a cero.")
            if cantidad > producto.stock:
                raise forms.ValidationError(f"Stock insuficiente. Solo hay {producto.stock} unidades de {producto.nombre}.")

        return cleaned_data
