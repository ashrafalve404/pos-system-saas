"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Public website
    path('', include('website.urls', namespace='website')),
    
    # App (dashboard)
    path('app/', include('dashboard.urls')),
    path('app/products/', include('products.urls', namespace='products')),
    path('app/customers/', include('customers.urls', namespace='customers')),
    path('app/sales/', include('sales.urls', namespace='sales')),
    path('app/reports/', include('reports.urls', namespace='reports')),
    path('app/settings/', include('settings.urls', namespace='settings')),
    
    # Legacy URLs redirect
    path('dashboard/', RedirectView.as_view(url='/app/dashboard/', permanent=True)),
    path('pos/', RedirectView.as_view(url='/app/pos/', permanent=True)),
    path('products/', RedirectView.as_view(url='/app/products/', permanent=True)),
    path('customers/', RedirectView.as_view(url='/app/customers/', permanent=True)),
    path('sales/', RedirectView.as_view(url='/app/sales/', permanent=True)),
    path('reports/', RedirectView.as_view(url='/app/reports/', permanent=True)),
    path('settings/', RedirectView.as_view(url='/app/settings/', permanent=True)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
