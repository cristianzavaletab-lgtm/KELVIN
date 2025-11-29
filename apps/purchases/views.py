"""
Purchase Views
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from .models import Purchase


class PurchaseListView(LoginRequiredMixin, ListView):
    model = Purchase
    template_name = 'purchases/purchase_list.html'
    context_object_name = 'purchases'
    paginate_by = 20
    ordering = ['-created_at']


class PurchaseCreateView(LoginRequiredMixin, CreateView):
    model = Purchase
    template_name = 'purchases/purchase_form.html'
    fields = ['supplier', 'invoice_number', 'invoice_photo', 'total', 'notes']
    success_url = reverse_lazy('purchases:purchase_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
