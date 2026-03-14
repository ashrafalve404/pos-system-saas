from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('create/', views.ProductCreateView.as_view(), name='product_create'),
    path('<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('bulk-delete/', views.bulk_delete_products, name='bulk_delete'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
]
