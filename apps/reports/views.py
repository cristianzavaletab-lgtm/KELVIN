"""
Reports and Dashboard Views
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from datetime import timedelta
from apps.sales.models import Sale
from apps.products.models import Product
from apps.customers.models import Customer
from decimal import Decimal
from django.db import transaction
from django.contrib.auth import get_user_model
from apps.accounts.models import WhatsAppTemplate


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
        context['low_stock'] = Product.objects.annotate(available=F('stock')-F('reserved_stock')).filter(
            available__lte=F('min_stock'),
            is_active=True
        ).count()
        context['out_of_stock_products'] = Product.objects.annotate(available=F('stock')-F('reserved_stock')).filter(
            available=0,
            is_active=True
        ).select_related('category', 'supplier').order_by('name')[:20]
        context['low_stock_products'] = Product.objects.annotate(available=F('stock')-F('reserved_stock')).filter(
            available__gt=0,
            available__lte=F('min_stock'),
            is_active=True
        ).select_related('category', 'supplier').order_by('available')[:20]
        
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
        
        # Dead stock (No sales in 30 days)
        last_30_days = today - timedelta(days=30)
        context['dead_stock'] = Product.objects.filter(
            is_active=True
        ).exclude(
            sale_items__sale__created_at__gte=last_30_days
        ).count()
        
        # Recent sales
        context['recent_sales'] = Sale.objects.filter(
            status='COMPLETED'
        ).select_related('customer', 'seller').order_by('-created_at')[:10]
        User = get_user_model()
        admin = User.objects.filter(username='admin').first()
        phone = ''
        if admin and admin.phone:
            phone = ''.join(ch for ch in admin.phone if ch.isdigit())
        context['admin_phone'] = phone
        context['wa_tpl_out_of_stock'] = WhatsAppTemplate.get_content(
            'ALERT_OUT_OF_STOCK',
            'Producto agotado\n\nNombre: {{name}}\nCódigo: {{code}}'
        )
        context['wa_tpl_low_stock'] = WhatsAppTemplate.get_content(
            'ALERT_LOW_STOCK',
            'Producto por debajo del stock mínimo\n\nNombre: {{name}}\nCódigo: {{code}}\nStock: {{stock}}\nStock mínimo: {{min_stock}}'
        )
        from apps.sales.models import Reservation
        context['reservations_active'] = Reservation.objects.filter(status='RESERVED').count()
        
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
        # Chart Data
        import json
        from django.core.serializers.json import DjangoJSONEncoder
        
        daily_data = list(daily)
        monthly_data = list(monthly)
        
        context['chart_daily_json'] = json.dumps({
            'labels': [str(d['created_at__date']) for d in daily_data],
            'values': [float(d['total']) for d in daily_data]
        }, cls=DjangoJSONEncoder)
        
        context['chart_monthly_json'] = json.dumps({
            'labels': [f"{d['created_at__month']}/{d['created_at__year']}" for d in monthly_data],
            'values': [float(d['total']) for d in monthly_data]
        }, cls=DjangoJSONEncoder)
        
        context.update({
            'daily_sales': daily_data,
            'monthly_sales': monthly_data,
            'top_products': top_products,
            'frequent_customers': frequent_customers,
            'purchases_by_supplier': purchases_by_supplier,
        })
        
        if request.GET.get('export') == 'excel':
            return self.export_excel(context)
            
        return context

    def export_excel(self, context):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reporte_ventas.csv"'
        writer = csv.writer(response)
        writer.writerow(['Fecha', 'Total'])
        for row in context['daily_sales']:
            writer.writerow([row['created_at__date'], row['total']])
        return response


class GenerateSuggestedOrdersView(LoginRequiredMixin, View):
    """Generate draft purchases grouped by supplier for critical products"""
    def post(self, request):
        from apps.purchases.models import Purchase, PurchaseItem
        critical_products = Product.objects.annotate(available=F('stock')-F('reserved_stock')).filter(
            is_active=True
        ).filter(
            Q(available=0) | Q(available__lte=F('min_stock'))
        ).select_related('supplier')
        grouped = {}
        for p in critical_products:
            if not p.supplier_id:
                continue
            avail = getattr(p, 'available', p.stock - p.reserved_stock)
            need_qty = max(p.min_stock - avail, 1)
            grouped.setdefault(p.supplier_id, []).append((p, need_qty))
        with transaction.atomic():
            for supplier_id, items in grouped.items():
                total = Decimal(0)
                for prod, qty in items:
                    total += (prod.purchase_price * qty)
                purchase = Purchase.objects.create(
                    supplier_id=supplier_id,
                    invoice_number='SUGERIDO',
                    total=total,
                    notes='Generado automáticamente por stock crítico',
                    created_by=request.user,
                    is_draft=True,
                )
                for prod, qty in items:
                    PurchaseItem.objects.create(
                        purchase=purchase,
                        product=prod,
                        quantity=qty,
                        unit_price=prod.purchase_price,
                        subtotal=(prod.purchase_price * qty)
                    )
        from django.shortcuts import redirect
        return redirect('purchases:purchase_list')
