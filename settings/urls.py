from django.urls import path
from . import views

app_name = 'settings'

urlpatterns = [
    path('', views.SettingsView.as_view(), name='index'),
    path('organization/edit/', views.OrganizationUpdateView.as_view(), name='organization_edit'),
    path('store/create/', views.StoreCreateView.as_view(), name='store_create'),
]
