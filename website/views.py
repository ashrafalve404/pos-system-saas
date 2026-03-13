from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth import login
from django.contrib import messages
from django.conf import settings

from subscriptions.models import Plan


class HomeView(TemplateView):
    template_name = 'website/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plans'] = Plan.objects.filter(is_active=True)
        return context


class FeaturesView(TemplateView):
    template_name = 'website/features.html'


class PricingView(TemplateView):
    template_name = 'website/pricing.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plans'] = Plan.objects.filter(is_active=True)
        return context


class AboutView(TemplateView):
    template_name = 'website/about.html'


class ContactView(TemplateView):
    template_name = 'website/contact.html'


class FAQView(TemplateView):
    template_name = 'website/faq.html'


class PrivacyView(TemplateView):
    template_name = 'website/privacy.html'


class TermsView(TemplateView):
    template_name = 'website/terms.html'


class CookiesView(TemplateView):
    template_name = 'website/cookies.html'


class SignupView(TemplateView):
    template_name = 'website/signup.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plans'] = Plan.objects.filter(is_active=True)
        return context
    
    def post(self, request, *args, **kwargs):
        from accounts.models import User
        from organizations.models import Organization
        from stores.models import Store
        from subscriptions.models import Subscription
        from django.utils import timezone
        from datetime import timedelta
        
        # Step 1: User account
        email = request.POST.get('email')
        full_name = request.POST.get('full_name')
        password = request.POST.get('password')
        
        # Step 2: Business info
        business_name = request.POST.get('business_name')
        phone = request.POST.get('phone', '')
        
        # Step 3: Plan
        plan_id = request.POST.get('plan', 'free')
        
        # Validate
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return redirect('website:signup')
        
        # Create user
        user = User.objects.create_user(
            email=email,
            password=password,
            full_name=full_name,
            phone=phone,
            role='owner'
        )
        
        # Create organization
        organization = Organization.objects.create(
            name=business_name,
            owner=user,
            subscription_plan=plan_id
        )
        
        # Create default store
        Store.objects.create(
            organization=organization,
            name='Main Store',
            phone=phone
        )
        
        # Update user with organization
        user.organization = organization
        user.save()
        
        # Create subscription
        plan = Plan.objects.filter(slug=plan_id).first()
        if not plan:
            plan = Plan.objects.filter(slug='free').first()
        
        if plan:
            Subscription.objects.create(
                organization=organization,
                plan=plan,
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + timedelta(days=30),
                status='active'
            )
        
        # Log user in
        login(request, user, backend='accounts.backends.EmailBackend')
        
        messages.success(request, f'Welcome to {business_name}! Your account has been created.')
        
        return redirect('dashboard:dashboard')
