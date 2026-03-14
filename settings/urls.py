from django.urls import path
from . import views

app_name = 'settings'

urlpatterns = [
    path('', views.SettingsView.as_view(), name='index'),
    path('organization/edit/', views.OrganizationUpdateView.as_view(), name='organization_edit'),
    path('store/create/', views.StoreCreateView.as_view(), name='store_create'),
    path('api-key/create/', views.CreateAPIKeyView.as_view(), name='create_api_key'),
    path('api-key/revoke/<int:pk>/', views.RevokeAPIKeyView.as_view(), name='revoke_api_key'),
]
