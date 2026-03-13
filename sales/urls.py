from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.SaleListView.as_view(), name='sale_list'),
    path('<int:pk>/', views.SaleDetailView.as_view(), name='sale_detail'),
]
