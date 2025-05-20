"""
Configuração do painel administrativo para o modelo Postos.
Customiza a interface de administração Django para gerenciamento de postos.
"""

from django.contrib import admin
from .models import Postos

@admin.register(Postos)
class PostoAdmin(admin.ModelAdmin):
    """
    Configurações personalizadas para a interface admin de Postos.
    
    Atributos:
        list_display: Campos exibidos na lista de postos
        (CNPJ, razão social, nome fantasia, endereço completo, etc.)
    
    Observações:
        - Todos os campos do modelo são exibidos
        - Ordenação padrão pelo campo CNPJ
        - Filtros e buscas devem ser adicionados conforme necessidade
    """
    
    list_display = (
        'cnpj',
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