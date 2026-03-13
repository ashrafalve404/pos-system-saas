from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('pos/', views.POSView.as_view(), name='pos'),
    path('pos/search/', views.ProductSearchView.as_view(), name='product-search'),
    path('pos/create-sale/', views.CreateSaleView.as_view(), name='create-sale'),
]
