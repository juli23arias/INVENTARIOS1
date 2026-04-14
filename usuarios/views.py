from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin

from .models import Usuario
from .forms import RegisterForm, AdminUserUpdateForm
from .mixins import AdminRequiredMixin

class CustomLoginView(LoginView):
    template_name = 'usuarios/login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated and user.rol == 'CAJERO':
            return reverse_lazy('dashboard_cajero')
        return reverse_lazy('dashboard_admin')

class RegisterView(SuccessMessageMixin, CreateView):
    model = Usuario
    form_class = RegisterForm
    template_name = 'usuarios/register.html'
    success_url = reverse_lazy('login')
    success_message = "Usuario '%(username)s' registrado correctamente. Ingrese con sus credenciales."

class UserListView(AdminRequiredMixin, ListView):
    model = Usuario
    template_name = 'usuarios/user_list.html'
    context_object_name = 'usuarios'
    
    def get_queryset(self):
        return Usuario.objects.all().order_by('-date_joined')

class UserUpdateView(AdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Usuario
    form_class = AdminUserUpdateForm
    template_name = 'usuarios/user_form.html'
    success_url = reverse_lazy('usuarios:list')
    success_message = "Roles o permisos de '%(username)s' actualizados con éxito."
