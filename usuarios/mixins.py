from django.contrib.auth.mixins import AccessMixin
from django.contrib import messages
from django.shortcuts import redirect

class AdminRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.rol != 'ADMIN':
            messages.error(request, "Acceso denegado. Se requiere rol de Administrador.")
            return redirect('index')
        return super().dispatch(request, *args, **kwargs)

class ClienteRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.rol != 'CLIENTE':
            messages.error(request, "Acceso restringido para Usuarios del sistema.")
            return redirect('index')
        return super().dispatch(request, *args, **kwargs)
