from django.contrib import admin
from .models import Postos

# Register your models here.

@admin.register(Postos)
class PostoAdmin(admin.ModelAdmin):
    list_display = ('cnpj',
                    'razao',
                    'fantasia',
                    'endereco',
                    'numero',
                    'complemento',
                    'bairro',
                    'cep',
                    'municipio',
                    'estado',
                    'bandeira',
                    'produto',
                    'unidade_de_medida',
                    'preco_revenda',
                    'data_coleta'
                    )
