from django.urls import path
from .views import listar_postos

urlpatterns = [
    path('postos/', listar_postos, name='postos'),
]