"""
Authentication Views - Mobile Optimized
"""
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView as BaseLoginView, LogoutView as BaseLogoutView
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.views.generic import FormView
from django import forms


class MobileLoginForm(AuthenticationForm):
    """Mobile-optimized login form"""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Usuario',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Contraseña',
            'autocomplete': 'current-password',
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        })
    )


class LoginView(BaseLoginView):
    """Mobile-optimized login view"""
    template_name = 'accounts/login.html'
    form_class = MobileLoginForm
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        user = form.get_user()
        if user.username != 'admin':
            form.add_error(None, 'Solo el usuario admin tiene acceso')
            return self.form_invalid(form)
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(0)
        return super().form_valid(form)


class LogoutView(BaseLogoutView):
    """Logout view"""
    next_page = reverse_lazy('accounts:login')
