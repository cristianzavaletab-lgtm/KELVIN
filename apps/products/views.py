"""
Fix missing import in products views
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, F
from django.http import HttpResponseRedirect
from .models import Product, Category


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category', 'supplier')
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(category__name__icontains=search)
            )
        
        # Category filter
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['low_stock_count'] = Product.objects.annotate(available=F('stock')-F('reserved_stock')).filter(available__lte=F('min_stock')).count()
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'products/product_form.html'
    fields = ['code', 'name', 'category', 'presentation', 'description', 'purchase_price', 'sale_price', 
             'stock', 'reserved_stock', 'min_stock', 'expiration_date', 'supplier', 'image']
    success_url = reverse_lazy('products:product_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nuevo Producto'
        return context


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    template_name = 'products/product_form.html'
    fields = ['code', 'name', 'category', 'presentation', 'description', 'purchase_price', 'sale_price', 
             'stock', 'reserved_stock', 'min_stock', 'expiration_date', 'supplier', 'image', 'is_active']
    success_url = reverse_lazy('products:product_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Producto'
        return context


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/confirm_delete.html'
    success_url = reverse_lazy('products:product_list')
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()
        from django.contrib import messages
        messages.success(request, 'Producto desactivado correctamente')
        return HttpResponseRedirect(self.success_url)


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    template_name = 'products/category_form.html'
    fields = ['name', 'icon', 'description']
    success_url = reverse_lazy('products:product_create')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nueva Categoría'
        return context
