from django import forms
from .models import DetalleCompra, Compra

class CompraCreateForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['proveedor']

class DetalleCompraForm(forms.ModelForm):
    class Meta:
        model = DetalleCompra
        fields = ['producto', 'cantidad', 'precio_compra']

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor a 0.")
        return cantidad

    def clean_precio_compra(self):
        precio = self.cleaned_data.get('precio_compra')
        if precio < 0:
            raise forms.ValidationError("El precio no puede ser negativo.")
        return precio
