"""
Sales Views - POS and Sales Management
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction, models
from django.utils import timezone
from decimal import Decimal
from .models import Sale, SaleItem
from apps.products.models import Product
from apps.customers.models import Customer
from apps.purchases.models import StockMovement
from .models import Reservation
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
        context['products'] = Product.objects.annotate(
            available=models.F('stock') - models.F('reserved_stock')
        ).filter(is_active=True, available__gt=0).select_related('category')
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
                available = product.stock - getattr(product, 'reserved_stock', 0)
                reserved_for_customer = 0
                if customer_id:
                    reserved_for_customer = Reservation.objects.filter(product=product, customer_id=customer_id, status=Reservation.Status.RESERVED).aggregate(total_qty=models.Sum('quantity'))['total_qty'] or 0
                allowed = available + reserved_for_customer
                if qty > allowed:
                    return JsonResponse({'success': False, 'error': f"Stock insuficiente (disponible: {allowed}) para {product.name}"}, status=400)
                
                # Create sale item
                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=qty,
                    unit_price=Decimal(item['price']),
                    subtotal=Decimal(item['subtotal'])
                )
                
                # Consume reservations
                if customer_id and reserved_for_customer > 0:
                    remaining = qty
                    reservations = Reservation.objects.filter(product=product, customer_id=customer_id, status=Reservation.Status.RESERVED).order_by('created_at')
                    for r in reservations:
                        if remaining <= 0:
                            break
                        use = min(remaining, r.quantity)
                        r.quantity -= use
                        if r.quantity == 0:
                            r.status = Reservation.Status.FULFILLED
                        r.save()
                        remaining -= use
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
                'invoice_pdf_url': generate_invoice_pdf(sale),
                'invoice_png_url': generate_invoice_png(sale),
                'whatsapp_text_url': generate_whatsapp_text_url(sale)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


class CreateReservationView(LoginRequiredMixin, View):
    @transaction.atomic
    def post(self, request):
        import json
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 0))
        customer_id = data.get('customer_id')
        if not product_id or quantity <= 0:
            return JsonResponse({'success': False, 'error': 'Datos inválidos'}, status=400)
        product = get_object_or_404(Product, pk=product_id)
        available = product.stock - product.reserved_stock
        if quantity > available:
            return JsonResponse({'success': False, 'error': f'Disponible: {available}'}, status=400)
        reservation = Reservation.objects.create(
            product=product,
            customer_id=customer_id if customer_id else None,
            quantity=quantity,
            status=Reservation.Status.RESERVED,
            created_by=request.user
        )
        return JsonResponse({'success': True, 'reservation_id': reservation.id})


class ListReservationsView(LoginRequiredMixin, View):
    def get(self, request):
        customer_id = request.GET.get('customer_id')
        qs = Reservation.objects.filter(status=Reservation.Status.RESERVED)
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        data = []
        for r in qs.select_related('product')[:50]:
            p = r.product
            data.append({
                'id': r.id,
                'product_id': p.id,
                'code': p.code,
                'name': p.name,
                'quantity': r.quantity,
                'sale_price': float(p.sale_price),
                'available_stock': p.stock - p.reserved_stock
            })
        return JsonResponse({'success': True, 'reservations': data})

def generate_invoice_pdf(sale):
    media_dir = os.path.join(settings.MEDIA_ROOT, 'invoices')
    os.makedirs(media_dir, exist_ok=True)
    pdf_path = os.path.join(media_dir, f"{sale.code}.pdf")
    c = canvas.Canvas(pdf_path, pagesize=A4)
    w, h = A4
    header_h = 22*mm
    c.setFillColorRGB(43/255, 76/255, 126/255)
    c.rect(0, h-header_h, w, header_h, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    # Logo ruedita (blanco) en header
    cx = 12*mm; cy = h - header_h/2; r = 6*mm
    c.setLineWidth(2)
    c.setStrokeColorRGB(1,1,1)
    c.circle(cx, cy, r)
    for i in range(8):
        import math
        ang = i * (math.pi/4)
        x1 = cx + (r-3) * math.cos(ang)
        y1 = cy + (r-3) * math.sin(ang)
        x2 = cx + (r) * math.cos(ang)
        y2 = cy + (r) * math.sin(ang)
        c.line(x1, y1, x2, y2)
    # Marca y contacto
    c.setFont("Helvetica-Bold", 18)
    c.drawString(22*mm, h-header_h+7*mm, "Kelvin Repuestos")
    c.setFont("Helvetica", 10)
    c.drawString(22*mm, h-header_h-1*mm, "Teléfono: 987654321 | Dirección: Av. Principal 123")
    c.setFillColorRGB(0, 0, 0)
    y = h - header_h - 12*mm
    c.setFont("Helvetica", 11)
    c.drawString(20*mm, y, f"Fecha: {sale.created_at.strftime('%d/%m/%Y %H:%M')}")
    y -= 6*mm
    c.drawString(20*mm, y, f"Cliente: {sale.customer.name if sale.customer else 'Cliente General'}")
    y -= 6*mm
    c.drawString(20*mm, y, f"Venta: {sale.code}")
    y -= 10*mm
    c.setFont("Helvetica-Bold", 13)
    c.setFillColorRGB(60/255, 106/255, 163/255)
    c.drawString(20*mm, y, "Productos")
    c.setFillColorRGB(0, 0, 0)
    y -= 8*mm
    c.setFont("Helvetica", 11)
    for item in sale.items.all():
        left_text = f"{item.product.name}"
        right_text = f"{item.quantity} x S/ {item.unit_price:.2f} = S/ {item.subtotal:.2f}"
        c.drawString(20*mm, y, left_text)
        c.drawRightString(w-20*mm, y, right_text)
        y -= 6*mm
        if y < 30*mm:
            c.showPage();
            c.setFillColorRGB(43/255, 76/255, 126/255)
            c.rect(0, h-header_h, w, header_h, fill=1, stroke=0)
            c.setFillColorRGB(1, 1, 1)
            c.setFont("Helvetica-Bold", 18)
            c.drawString(20*mm, h-header_h+7*mm, "Kelvin Repuestos")
            c.setFillColorRGB(0, 0, 0)
            y = h - header_h - 12*mm
            c.setFont("Helvetica-Bold", 13)
            c.setFillColorRGB(60/255, 106/255, 163/255)
            c.drawString(20*mm, y, "Productos")
            c.setFillColorRGB(0, 0, 0)
            y -= 8*mm
            c.setFont("Helvetica", 11)
    y -= 10*mm
    c.setFont("Helvetica-Bold", 14)
    c.setFillColorRGB(43/255, 76/255, 126/255)
    c.drawRightString(w-20*mm, y, f"TOTAL: S/ {sale.total:.2f}")
    c.save()
    return os.path.join(settings.MEDIA_URL, 'invoices', f"{sale.code}.pdf")

def generate_invoice_png(sale):
    media_dir = os.path.join(settings.MEDIA_ROOT, 'invoices')
    os.makedirs(media_dir, exist_ok=True)
    img_path = os.path.join(media_dir, f"{sale.code}.png")
    img = Image.new('RGB', (800, 1100), color=(245, 247, 248))
    draw = ImageDraw.Draw(img)
    try:
        font_title = ImageFont.truetype("arial.ttf", 30)
        font_text = ImageFont.truetype("arial.ttf", 20)
        font_bold = ImageFont.truetype("arialbd.ttf", 22)
    except Exception:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()
        font_bold = ImageFont.load_default()
    draw.rectangle([0,0,800,100], fill=(43,76,126))
    # Logo ruedita
    cx, cy, r = 40, 50, 20
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(255,255,255), width=3)
    import math
    for i in range(8):
        ang = i * (math.pi/4)
        x1 = cx + int((r-6) * math.cos(ang))
        y1 = cy + int((r-6) * math.sin(ang))
        x2 = cx + int(r * math.cos(ang))
        y2 = cy + int(r * math.sin(ang))
        draw.line([x1,y1,x2,y2], fill=(255,255,255), width=3)
    # Marca
    draw.text((80, 30), "Kelvin Repuestos", fill=(255,255,255), font=font_title)
    # Contacto
    draw.text((80, 68), "Teléfono: 987654321 | Dirección: Av. Principal 123", fill=(255,255,255), font=font_text)
    y = 130
    draw.text((40, y), f"Fecha: {sale.created_at.strftime('%d/%m/%Y %H:%M')}", fill=(28,28,28), font=font_text)
    y += 26
    draw.text((40, y), f"Cliente: {sale.customer.name if sale.customer else 'Cliente General'}", fill=(28,28,28), font=font_text)
    y += 26
    draw.text((40, y), f"Venta: {sale.code}", fill=(28,28,28), font=font_text)
    y += 34
    draw.text((40, y), "Productos", fill=(60,106,163), font=font_bold)
    y += 28
    for item in sale.items.all():
        left = f"{item.product.name}"
        right = f"{item.quantity} x S/ {item.unit_price:.2f} = S/ {item.subtotal:.2f}"
        draw.text((40, y), left, fill=(28,28,28), font=font_text)
        draw.text((520, y), right, fill=(28,28,28), font=font_text)
        y += 26
    y += 22
    draw.text((520, y), f"TOTAL: S/ {sale.total:.2f}", fill=(43,76,126), font=font_bold)
    img.save(img_path)
    return os.path.join(settings.MEDIA_URL, 'invoices', f"{sale.code}.png")

def generate_whatsapp_text_url(sale):
        from urllib.parse import quote
        from apps.accounts.models import WhatsAppTemplate
        customer_name = sale.customer.name if sale.customer else 'Cliente General'
        items_text = '\n'.join([
            f"- {item.product.name} x {item.quantity} = S/ {item.subtotal}" for item in sale.items.all()
        ])
        template = WhatsAppTemplate.get_content('SALE_MESSAGE',
            'Gracias por su compra\nVenta: {{code}}\nCliente: {{customer}}\nProductos:\n{{items}}\nTOTAL: S/ {{total}}'
        )
        text_raw = template.replace('{{code}}', sale.code)
        text_raw = text_raw.replace('{{customer}}', customer_name)
        text_raw = text_raw.replace('{{items}}', items_text)
        text_raw = text_raw.replace('{{total}}', str(sale.total))
        text = quote(text_raw)
        phone = sale.customer.phone if sale.customer and sale.customer.phone else ''
        phone = ''.join(ch for ch in phone if ch.isdigit())
        if phone:
            return f"https://wa.me/{phone}?text={text}"
        return f"https://wa.me/?text={text}"


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['whatsapp_text_url'] = generate_whatsapp_text_url(self.object)
        return context
