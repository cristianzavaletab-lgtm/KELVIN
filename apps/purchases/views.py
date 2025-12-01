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
    
    def get_success_url(self):
        return reverse_lazy('purchases:purchase_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


from django.views.generic import DetailView
from .models import PurchaseItem
from apps.products.models import Product

class PurchaseDetailView(LoginRequiredMixin, DetailView):
    model = Purchase
    template_name = 'purchases/purchase_detail.html'
    context_object_name = 'purchase'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.filter(is_active=True)
        return context


class PurchaseItemCreateView(LoginRequiredMixin, CreateView):
    model = PurchaseItem
    fields = ['product', 'quantity', 'unit_price']
    
    def form_valid(self, form):
        purchase = Purchase.objects.get(pk=self.kwargs['pk'])
        form.instance.purchase = purchase
        form.instance.subtotal = form.instance.quantity * form.instance.unit_price
        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse_lazy('purchases:purchase_detail', kwargs={'pk': self.kwargs['pk']})
