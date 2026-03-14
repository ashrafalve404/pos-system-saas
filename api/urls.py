from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('products/add/', views.add_product, name='add_product'),
    path('products/bulk/', views.add_products_bulk, name='add_products_bulk'),
    path('products/import/', views.import_products, name='import_products'),
    path('', views.api_docs, name='api_docs'),
]
