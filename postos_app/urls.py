"""
Configuração de URLs para o aplicativo postos_app.
Define os endpoints da API e URLs de visualização.
"""

from django.urls import path
from .views import listar_postos

urlpatterns = [
    # Endpoint para listagem de postos
    # URL: /postos/
    # View: listar_postos
    # Nome: 'postos'
    path('postos/', listar_postos, name='postos'),
]