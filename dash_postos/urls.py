from django.urls import path
from .views import dashboard_brasil, dashboard_cidade, melhor_posto

urlpatterns = [
    path('dashboard_brasil/', dashboard_brasil, name='dashboard_brasil'),
    path('dashboard_cidade/', dashboard_cidade, name='dashboard_cidade'),
    path('melhor-posto/', melhor_posto, name='melhor_posto'),
]