"""
Supplier Views
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Supplier


class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'suppliers/supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = 20
    
    def get_queryset(self):
        return Supplier.objects.filter(is_active=True).order_by('name')


class SupplierCreateView(LoginRequiredMixin, CreateView):
    model = Supplier
    template_name = 'suppliers/supplier_form.html'
    fields = ['name', 'ruc', 'phone', 'email', 'address']
    success_url = reverse_lazy('suppliers:supplier_list')


class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    model = Supplier
    template_name = 'suppliers/supplier_edit.html'
    fields = ['name', 'ruc', 'phone', 'email', 'address']
    success_url = reverse_lazy('suppliers:supplier_list')


class SupplierDeleteView(LoginRequiredMixin, DeleteView):
    model = Supplier
    template_name = 'suppliers/confirm_delete.html'
    success_url = reverse_lazy('suppliers:supplier_list')
