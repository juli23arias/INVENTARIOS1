from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = list(UserCreationForm.Meta.fields)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = 'CLIENTE'
        if commit:
            user.save()
        return user

class AdminUserUpdateForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['rol', 'is_active']
        labels = {
            'rol': 'Rol del Sistema',
            'is_active': 'Usuario Activo',
        }
