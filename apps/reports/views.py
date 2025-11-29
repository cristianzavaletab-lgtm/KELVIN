"""
Reports and Dashboard Views
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta
from apps.sales.models import Sale
from apps.products.models import Product
from apps.customers.models import Customer


class DashboardView(LoginRequiredMixin, TemplateView):
    """Mobile Dashboard with KPIs"""
    template_name = 'reports/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        # Today's sales
        today_sales = Sale.objects.filter(
            created_at__date=today,
            status='COMPLETED'
        ).aggregate(
            total=Sum('total'),
            count=Count('id')
        )
        
        context['today_sales'] = today_sales['total'] or 0
        context['today_count'] = today_sales['count'] or 0
        
        # Month's sales
        month_sales = Sale.objects.filter(
            created_at__date__gte=month_start,
            status='COMPLETED'
        ).aggregate(
            total=Sum('total'),
            count=Count('id')
        )
        
        context['month_sales'] = month_sales['total'] or 0
        context['month_count'] = month_sales['count'] or 0
        
        # Low stock products
        context['low_stock'] = Product.objects.filter(
            stock__lte=F('min_stock'),
            is_active=True
        ).count()
        
        # Expiring products (next 30 days)
        expiring_date = today + timedelta(days=30)
        context['expiring_soon'] = Product.objects.filter(
            expiration_date__lte=expiring_date,
            expiration_date__gte=today,
            is_active=True
        ).count()
        
        # Top products
        context['top_products'] = Product.objects.filter(
            is_active=True,
            sale_items__sale__status='COMPLETED',
            sale_items__sale__created_at__date__gte=month_start
        ).annotate(
            total_sold=Sum('sale_items__quantity')
        ).order_by('-total_sold')[:5]
        
        # Recent sales
        context['recent_sales'] = Sale.objects.filter(
            status='COMPLETED'
        ).select_related('customer', 'seller').order_by('-created_at')[:10]
        
        return context


class ReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/reports.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request
        start = request.GET.get('start')
        end = request.GET.get('end')
        qs_sales = Sale.objects.filter(status='COMPLETED')
        qs_purchases = None
        try:
            from apps.purchases.models import Purchase
            qs_purchases = Purchase.objects.all()
        except Exception:
            qs_purchases = None
        if start:
            qs_sales = qs_sales.filter(created_at__date__gte=start)
            if qs_purchases is not None:
                qs_purchases = qs_purchases.filter(created_at__date__gte=start)
        if end:
            qs_sales = qs_sales.filter(created_at__date__lte=end)
            if qs_purchases is not None:
                qs_purchases = qs_purchases.filter(created_at__date__lte=end)
        daily = qs_sales.values('created_at__date').annotate(total=Sum('total')).order_by('created_at__date')
        monthly = qs_sales.values('created_at__year', 'created_at__month').annotate(total=Sum('total')).order_by('created_at__year', 'created_at__month')
        top_products = Product.objects.filter(sale_items__sale__status='COMPLETED').annotate(total_sold=Sum('sale_items__quantity')).order_by('-total_sold')[:10]
        frequent_customers = Customer.objects.filter(sales__status='COMPLETED').annotate(count=Count('sales')).order_by('-count')[:10]
        purchases_by_supplier = []
        if qs_purchases is not None:
            purchases_by_supplier = qs_purchases.values('supplier__name').annotate(total=Sum('total'), count=Count('id')).order_by('-total')
        context.update({
            'daily_sales': list(daily),
            'monthly_sales': list(monthly),
            'top_products': top_products,
            'frequent_customers': frequent_customers,
            'purchases_by_supplier': purchases_by_supplier,
        })
        return context
