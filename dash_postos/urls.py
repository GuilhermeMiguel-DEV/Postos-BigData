from django.contrib import admin
from django.urls import path, include
from .views import dash_graficos

urlpatterns = [
    path('dash_brasil/', dash_graficos, name='graficos_postos')
]