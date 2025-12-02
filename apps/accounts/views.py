"""
Authentication Views - Mobile Optimized
"""
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView as BaseLoginView, LogoutView as BaseLogoutView
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.views.generic import FormView
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from .models import WhatsAppTemplate
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse


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
    def get_next_page(self):
        from django.urls import reverse
        return reverse('accounts:login') + '?logged_out=1'


class WhatsAppTemplatesView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/whatsapp_templates.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sale_message'] = WhatsAppTemplate.get_content('SALE_MESSAGE', '')
        context['alert_out'] = WhatsAppTemplate.get_content('ALERT_OUT_OF_STOCK', '')
        context['alert_low'] = WhatsAppTemplate.get_content('ALERT_LOW_STOCK', '')
        return context
    
    def post(self, request):
        data = request.POST
        WhatsAppTemplate.objects.update_or_create(key='SALE_MESSAGE', defaults={'content': data.get('sale_message','')})
        WhatsAppTemplate.objects.update_or_create(key='ALERT_OUT_OF_STOCK', defaults={'content': data.get('alert_out','')})
        WhatsAppTemplate.objects.update_or_create(key='ALERT_LOW_STOCK', defaults={'content': data.get('alert_low','')})
        from django.shortcuts import redirect
        return redirect('accounts:whatsapp_templates')


class PasswordChangeView(LoginRequiredMixin, FormView):
    template_name = 'accounts/password_change.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('reports:dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        from django.shortcuts import redirect
        logout(self.request)
        return redirect(reverse('accounts:login') + '?changed=1')
