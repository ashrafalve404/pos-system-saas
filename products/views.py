from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Product, Category


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        queryset = Product.objects.filter(
            organization=self.request.user.organization
        ).select_related('category', 'store')
        
        search = self.request.GET.get('search')
        category = self.request.GET.get('category')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(barcode__icontains=search) |
                Q(sku__icontains=search)
            )
        
        if category:
            queryset = queryset.filter(category_id=category)
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(
            organization=self.request.user.organization
        )
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'products/product_form.html'
    fields = ['name', 'category', 'store', 'barcode', 'sku', 'price', 'cost_price', 'stock_quantity', 'low_stock_threshold', 'description', 'is_active']
    success_url = reverse_lazy('products:product_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'] = {'organization': self.request.user.organization}
        return kwargs

    def form_valid(self, form):
        form.instance.organization = self.request.user.organization
        messages.success(self.request, 'Product created successfully!')
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    template_name = 'products/product_form.html'
    fields = ['name', 'category', 'store', 'barcode', 'sku', 'price', 'cost_price', 'stock_quantity', 'low_stock_threshold', 'description', 'is_active']
    success_url = reverse_lazy('products:product_list')
    
    def get_queryset(self):
        return Product.objects.filter(organization=self.request.user.organization)

    def form_valid(self, form):
        messages.success(self.request, 'Product updated successfully!')
        return super().form_valid(form)


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:product_list')
    
    def get_queryset(self):
        return Product.objects.filter(organization=self.request.user.organization)

    def form_valid(self, form):
        messages.success(self.request, 'Product deleted successfully!')
        return super().form_valid(form)


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(organization=self.request.user.organization)


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    template_name = 'products/category_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('products:category_list')
    
    def form_valid(self, form):
        form.instance.organization = self.request.user.organization
        messages.success(self.request, 'Category created successfully!')
        return super().form_valid(form)


def bulk_delete_products(request):
    """AJAX view to bulk delete products"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        product_ids = data.get('product_ids', [])
    except:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    if not product_ids:
        return JsonResponse({'error': 'No products selected'}, status=400)
    
    # Delete products belonging to user's organization
    deleted_count = Product.objects.filter(
        id__in=product_ids,
        organization=request.user.organization
    ).delete()[0]
    
    return JsonResponse({
        'success': True,
        'deleted_count': deleted_count
    })
