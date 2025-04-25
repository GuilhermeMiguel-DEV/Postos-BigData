from django.urls import path
from .views import dash_graficos

urlpatterns = [
    path('dash_brasil/', dash_graficos, name='graficos_postos')
]