from django.urls import path
from .views.dashboard_melhor_posto import melhor_posto
from .views.dashboard_brasil import dashboard_brasil
from .views.home_page import home_page
from .views.dashboard_cidade import dashboard_cidade
from .views.api import EstadosPorRegiaoView

"""
Configuração de URLs do aplicativo Dash Postos.
Define os endpoints e mapeia para as views correspondentes.
"""

urlpatterns = [
    # Página inicial
    path('', home_page, name='home_page'),
    
    # Dashboard nacional
    path('dashboard_brasil/', dashboard_brasil, name='dashboard_brasil'),
    
    # Dashboard por cidade
    path('dashboard_cidade/', dashboard_cidade, name='dashboard_cidade'),
    
    # Melhor posto (recomendações)
    path('melhor-posto/', melhor_posto, name='melhor_posto'),
    
    # API para filtros dinâmicos
    path('api/estados-por-regiao/', EstadosPorRegiaoView.as_view(), name='estados_por_regiao'),
]