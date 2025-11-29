"""
Sales Views - POS and Sales Management
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from .models import Sale, SaleItem
from apps.products.models import Product
from apps.customers.models import Customer
from apps.purchases.models import StockMovement
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from PIL import Image, ImageDraw, ImageFont
import os


class POSView(LoginRequiredMixin, TemplateView):
    """Point of Sale - Mobile Optimized"""
    template_name = 'sales/pos.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.filter(is_active=True, stock__gt=0).select_related('category')
        context['customers'] = Customer.objects.filter(is_active=True)
        return context


class ProcessSaleView(LoginRequiredMixin, View):
    """Process sale and update stock"""
    
    @transaction.atomic
    def post(self, request):
        try:
            import json
            data = json.loads(request.body)
            
            # Customer handling
            customer_id = data.get('customer_id') if data.get('customer_id') else None
            new_customer = data.get('new_customer')
            if not customer_id and new_customer:
                dni = (new_customer.get('dni') or '').strip()
                name = (new_customer.get('name') or '').strip()
                phone = (new_customer.get('phone') or '').strip()
                email = (new_customer.get('email') or '').strip()
                address = (new_customer.get('address') or '').strip()
                if dni:
                    customer, _ = Customer.objects.get_or_create(dni=dni, defaults={
                        'name': name or dni,
                        'phone': phone,
                        'email': email,
                        'address': address,
                        'is_active': True,
                    })
                else:
                    customer, _ = Customer.objects.get_or_create(name=name, defaults={
                        'dni': '',
                        'phone': phone,
                        'email': email,
                        'address': address,
                        'is_active': True,
                    })
                customer_id = customer.id

            # Create sale
            sale = Sale.objects.create(
                customer_id=customer_id if customer_id else None,
                seller=request.user,
                subtotal=Decimal(data['subtotal']),
                discount=Decimal(0),
                tax=Decimal(0),
                total=Decimal(data['total']),
                payment_method=data['payment_method'],
                status='COMPLETED'
            )
            
            # Create sale items and update stock
            for item in data['items']:
                product = Product.objects.get(id=item['product_id'])
                qty = int(item['quantity'])
                if qty <= 0:
                    return JsonResponse({'success': False, 'error': 'Cantidad inválida'}, status=400)
                if qty > product.stock:
                    return JsonResponse({'success': False, 'error': f"Stock insuficiente para {product.name}"}, status=400)
                
                # Create sale item
                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=qty,
                    unit_price=Decimal(item['price']),
                    subtotal=Decimal(item['subtotal'])
                )
                
                # Update stock
                previous_stock = product.stock
                product.stock -= qty
                product.save()
                
                # Create stock movement (Kardex)
                StockMovement.objects.create(
                    product=product,
                    movement_type='SALE',
                    quantity=-qty,
                    previous_stock=previous_stock,
                    new_stock=product.stock,
                    reference_id=sale.id,
                    created_by=request.user
                )
            
            return JsonResponse({
                'success': True,
                'sale_id': sale.id,
                'sale_code': sale.code,
                'message': 'Venta registrada exitosamente',
                'invoice_pdf_url': self.generate_invoice_pdf(sale),
                'invoice_png_url': self.generate_invoice_png(sale)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

    def generate_invoice_pdf(self, sale):
        media_dir = os.path.join(settings.MEDIA_ROOT, 'invoices')
        os.makedirs(media_dir, exist_ok=True)
        pdf_path = os.path.join(media_dir, f"{sale.code}.pdf")
        c = canvas.Canvas(pdf_path, pagesize=A4)
        w, h = A4
        y = h - 40*mm
        c.setFont("Helvetica-Bold", 16)
        c.drawString(20*mm, y, "AGROTECNICA MIJAEL")
        y -= 10*mm
        c.setFont("Helvetica", 11)
        c.drawString(20*mm, y, f"Fecha: {sale.created_at.strftime('%d/%m/%Y %H:%M')}")
        y -= 6*mm
        c.drawString(20*mm, y, f"Cliente: {sale.customer.name if sale.customer else 'Cliente General'}")
        y -= 6*mm
        c.drawString(20*mm, y, f"Venta: {sale.code}")
        y -= 12*mm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(20*mm, y, "Productos")
        y -= 8*mm
        c.setFont("Helvetica", 11)
        for item in sale.items.all():
            c.drawString(20*mm, y, f"{item.product.name}")
            c.drawRightString(w-20*mm, y, f"{item.quantity} x S/ {item.unit_price} = S/ {item.subtotal}")
            y -= 6*mm
            if y < 30*mm:
                c.showPage(); y = h - 40*mm
        y -= 8*mm
        c.setFont("Helvetica-Bold", 12)
        c.drawRightString(w-20*mm, y, f"TOTAL: S/ {sale.total}")
        c.save()
        return os.path.join(settings.MEDIA_URL, 'invoices', f"{sale.code}.pdf")

    def generate_invoice_png(self, sale):
        media_dir = os.path.join(settings.MEDIA_ROOT, 'invoices')
        os.makedirs(media_dir, exist_ok=True)
        img_path = os.path.join(media_dir, f"{sale.code}.png")
        img = Image.new('RGB', (800, 1000), color=(245, 247, 248))
        draw = ImageDraw.Draw(img)
        try:
            font_title = ImageFont.truetype("arial.ttf", 28)
            font_text = ImageFont.truetype("arial.ttf", 20)
        except Exception:
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()
        y = 40
        draw.text((40, y), "AGROTECNICA MIJAEL", fill=(30, 81, 40), font=font_title)
        y += 40
        draw.text((40, y), f"Fecha: {sale.created_at.strftime('%d/%m/%Y %H:%M')}", fill=(28,28,28), font=font_text)
        y += 28
        draw.text((40, y), f"Cliente: {sale.customer.name if sale.customer else 'Cliente General'}", fill=(28,28,28), font=font_text)
        y += 28
        draw.text((40, y), f"Venta: {sale.code}", fill=(28,28,28), font=font_text)
        y += 40
        draw.text((40, y), "Productos", fill=(78, 159, 61), font=font_title)
        y += 32
        for item in sale.items.all():
            draw.text((40, y), f"{item.product.name}", fill=(28,28,28), font=font_text)
            draw.text((500, y), f"{item.quantity} x S/ {item.unit_price}", fill=(28,28,28), font=font_text)
            y += 26
        y += 20
        draw.text((500, y), f"TOTAL: S/ {sale.total}", fill=(78, 159, 61), font=font_title)
        img.save(img_path)
        return os.path.join(settings.MEDIA_URL, 'invoices', f"{sale.code}.png")


class SaleListView(LoginRequiredMixin, ListView):
    model = Sale
    template_name = 'sales/sale_list.html'
    context_object_name = 'sales'
    paginate_by = 20
    ordering = ['-created_at']


class SaleDetailView(LoginRequiredMixin, DetailView):
    model = Sale
    template_name = 'sales/sale_detail.html'
    context_object_name = 'sale'
