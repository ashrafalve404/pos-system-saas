from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .models import Customer


class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'customers/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 20

    def get_queryset(self):
        queryset = Customer.objects.filter(
            organization=self.request.user.organization
        )
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )
        
        return queryset.order_by('-created_at')


class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    template_name = 'customers/customer_form.html'
    fields = ['name', 'email', 'phone', 'address']
    success_url = reverse_lazy('customers:customer_list')
    
    def form_valid(self, form):
        form.instance.organization = self.request.user.organization
        if self.request.user.store:
            form.instance.store = self.request.user.store
        messages.success(self.request, 'Customer created successfully!')
        return super().form_valid(form)


class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    template_name = 'customers/customer_form.html'
    fields = ['name', 'email', 'phone', 'address', 'is_active']
    success_url = reverse_lazy('customers:customer_list')
    
    def get_queryset(self):
        return Customer.objects.filter(organization=self.request.user.organization)

    def form_valid(self, form):
        messages.success(self.request, 'Customer updated successfully!')
        return super().form_valid(form)


class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model = Customer
    template_name = 'customers/customer_confirm_delete.html'
    success_url = reverse_lazy('customers:customer_list')
    
    def get_queryset(self):
        return Customer.objects.filter(organization=self.request.user.organization)

    def form_valid(self, form):
        messages.success(self.request, 'Customer deleted successfully!')
        return super().form_valid(form)
