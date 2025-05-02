from django.urls import path
from .views.dashboard_melhor_posto import melhor_posto
from .views.dashboard_brasil import dashboard_brasil
from .views.home_page import home_page
from .views.dashboard_cidade import dashboard_cidade


urlpatterns = [
    path('', home_page, name='home_page'),
    path('dashboard_brasil/', dashboard_brasil, name='dashboard_brasil'),
    path('dashboard_cidade/', dashboard_cidade, name='dashboard_cidade'),
    path('melhor-posto/', melhor_posto, name='melhor_posto'),
]