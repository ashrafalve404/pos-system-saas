from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView
from django.contrib import messages
from django.urls import reverse_lazy
from organizations.models import Organization
from stores.models import Store


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'settings/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization'] = self.request.user.organization
        context['stores'] = self.request.user.organization.stores.all() if self.request.user.organization else []
        return context


class OrganizationUpdateView(LoginRequiredMixin, UpdateView):
    model = Organization
    template_name = 'settings/organization_form.html'
    fields = ['name', 'subscription_plan']
    success_url = reverse_lazy('settings:index')

    def get_object(self):
        return self.request.user.organization

    def form_valid(self, form):
        messages.success(self.request, 'Organization updated successfully!')
        return super().form_valid(form)


class StoreCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'settings/store_form.html'

    def post(self, request, *args, **kwargs):
        from django.shortcuts import redirect
        
        name = request.POST.get('name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        
        Store.objects.create(
            organization=request.user.organization,
            name=name,
            address=address,
            phone=phone
        )
        messages.success(request, 'Store created successfully!')
        return redirect('settings:index')
