from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta

from sales.models import Sale, SaleItem
from products.models import Product
from customers.models import Customer


class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        org = self.request.user.organization
        today = timezone.now().date()
        
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if date_from:
            start_date = timezone.datetime.strptime(date_from, '%Y-%m-%d').date()
        else:
            start_date = today - timedelta(days=30)
        
        if date_to:
            end_date = timezone.datetime.strptime(date_to, '%Y-%m-%d').date()
        else:
            end_date = today
        
        sales = Sale.objects.filter(
            organization=org,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            payment_status='paid'
        )
        
        total_revenue = sales.aggregate(total=Sum('total'))['total'] or 0
        total_orders = sales.count()
        avg_order = total_revenue / total_orders if total_orders > 0 else 0
        
        top_products = SaleItem.objects.filter(
            sale__organization=org,
            sale__created_at__date__gte=start_date,
            sale__created_at__date__lte=end_date,
            sale__payment_status='paid'
        ).values(
            'product__name'
        ).annotate(
            total_sold=Sum('quantity'),
            revenue=Sum('subtotal')
        ).order_by('-total_sold')[:10]
        
        sales_by_day = sales.extra(
            select={'day': 'DATE(created_at)'}
        ).values('day').annotate(
            revenue=Sum('total'),
            orders=Count('id')
        ).order_by('day')
        
        context.update({
            'date_from': start_date,
            'date_to': end_date,
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'avg_order': avg_order,
            'top_products': top_products,
            'sales_by_day': sales_by_day,
        })
        
        return context
