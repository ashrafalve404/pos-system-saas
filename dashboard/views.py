from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.db.models import Sum, Count, F
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta

from sales.models import Sale, SaleItem
from products.models import Product
from customers.models import Customer
from payments.models import Payment
from stores.models import Store


class CreateSaleView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        import json
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            data = json.loads(request.body)
            
            items = data.get('items', [])
            store_id = data.get('store_id')
            customer_id = data.get('customer_id')
            payment_method = data.get('payment_method', 'cash')
            discount_amount = data.get('discount_amount', 0)
            
            logger.info(f"Creating sale - items: {len(items)}, store_id: {store_id}")
            
            if not items:
                return JsonResponse({'error': 'No items in cart'}, status=400)
            
            if not store_id:
                return JsonResponse({'error': 'No store selected'}, status=400)
            
            store = get_object_or_404(
                Store,
                id=store_id,
                organization=request.user.organization
            )
            
            customer = None
            if customer_id:
                customer = Customer.objects.filter(
                    id=customer_id,
                    organization=request.user.organization
                ).first()
            
            sale = Sale.objects.create(
                organization=request.user.organization,
                store=store,
                cashier=request.user,
                customer=customer,
                discount_amount=discount_amount,
                tax_amount=0,
                payment_status='paid'
            )
            
            for item in items:
                product = get_object_or_404(
                    Product,
                    id=item['id'],
                    organization=request.user.organization
                )
                
                quantity = int(item['quantity'])
                price = product.price
                
                sale_item = SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    price=price,
                    subtotal=price * quantity
                )
                
                product.stock_quantity -= quantity
                product.save()
            
            sale.total = sale.items.aggregate(
                total=Sum(F('quantity') * F('price'))
            )['total'] or 0
            sale.subtotal = sale.total
            sale.total = sale.subtotal - sale.discount_amount
            sale.save()
            
            Payment.objects.create(
                sale=sale,
                organization=request.user.organization,
                payment_method=payment_method,
                amount=sale.total,
                status='completed',
                paid_by=request.user
            )
            
            if customer:
                customer.loyalty_points += int(sale.total)
                customer.total_purchases += sale.total
                customer.save()
            
            return JsonResponse({
                'success': True,
                'sale_id': sale.id,
                'invoice_number': sale.invoice_number,
                'total': str(sale.total)
            })
            
        except Exception as e:
            import traceback
            logger.error(f"Error creating sale: {e}\n{traceback.format_exc()}")
            return JsonResponse({'error': str(e)}, status=500)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if not self.request.user.organization:
            return context
        
        org = self.request.user.organization
        today = timezone.now().date()
        
        today_sales = Sale.objects.filter(
            organization=org,
            created_at__date=today,
            payment_status='paid'
        )
        
        today_revenue = today_sales.aggregate(total=Sum('total'))['total'] or 0
        today_orders = today_sales.count()
        
        month_start = today.replace(day=1)
        monthly_revenue = Sale.objects.filter(
            organization=org,
            created_at__date__gte=month_start,
            payment_status='paid'
        ).aggregate(total=Sum('total'))['total'] or 0
        
        low_stock_products = Product.objects.filter(
            organization=org,
            is_active=True
        ).filter(
            stock_quantity__lte=F('low_stock_threshold')
        )[:10]
        
        recent_sales = Sale.objects.filter(
            organization=org
        ).select_related('customer', 'cashier', 'store').order_by('-created_at')[:10]
        
        top_products = SaleItem.objects.filter(
            sale__organization=org,
            sale__created_at__date__gte=today - timedelta(days=30)
        ).values(
            'product__name'
        ).annotate(
            total_sold=Sum('quantity'),
            revenue=Sum('subtotal')
        ).order_by('-total_sold')[:5]
        
        total_customers = Customer.objects.filter(organization=org).count()
        
        context.update({
            'today_revenue': today_revenue,
            'today_orders': today_orders,
            'monthly_revenue': monthly_revenue,
            'low_stock_products': low_stock_products,
            'recent_sales': recent_sales,
            'top_products': top_products,
            'total_customers': total_customers,
        })
        
        return context


class POSView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/pos.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        store_id = self.request.GET.get('store')
        
        if self.request.user.store:
            products = Product.objects.filter(
                organization=self.request.user.organization,
                store=self.request.user.store,
                is_active=True
            ).select_related('category')
        else:
            products = Product.objects.filter(
                organization=self.request.user.organization,
                is_active=True
            ).select_related('category')
        
        if store_id:
            products = products.filter(store_id=store_id)
        
        context['products'] = products[:50]
        context['stores'] = self.request.user.organization.stores.filter(is_active=True)
        return context


class ProductSearchView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        store_id = request.GET.get('store')
        
        products = Product.objects.filter(
            organization=request.user.organization,
            is_active=True
        )
        
        if store_id:
            products = products.filter(store_id=store_id)
        
        if query:
            products = products.filter(
                name__icontains=query
            ) | products.filter(
                barcode__icontains=query
            ) | products.filter(
                sku__icontains=query
            )
        
        results = products[:20]
        
        from django.http import JsonResponse
        data = [{
            'id': p.id,
            'name': p.name,
            'price': str(p.price),
            'barcode': p.barcode,
            'stock': p.stock_quantity,
            'category': p.category.name if p.category else None
        } for p in results]
        
        return JsonResponse(data, safe=False)
