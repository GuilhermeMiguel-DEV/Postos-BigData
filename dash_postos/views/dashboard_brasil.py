from django.shortcuts import redirect, render
from django.core.paginator import Paginator
from django.db.models import Avg, Count

import pandas as pd

import base64
from io import BytesIO

from postos_app.models import Postos
from dash_postos.utils import normalizar_nome, gerar_grafico_ply, gerar_grafico_historico_precos
import plotly.io as pio
import plotly.express as px

pio.templates.default = "plotly_dark"

"""
Módulo de visualização do dashboard nacional.
Exibe dados agregados de postos por região/estado com gráficos interativos.
"""


def dashboard_brasil(request):
    """
    View principal do dashboard nacional.
    
    Processa filtros e exibe:
    - Gráfico de distribuição de preços por produto (pizza)
    - Gráfico de evolução por estado (linhas)
    - Estatísticas resumidas
    
    Parâmetros GET aceitos:
    - regiao: Filtra por região (NORTE, NORDESTE, etc.)
    - estado: Filtra por UF específica
    - produto: Filtra por tipo de combustível
    """

    # Configurações constantes das regiões brasileiras
    REGIOES_BRASIL = {
        'NORTE': ['ACRE', 'AMAPÁ', 'AMAZONAS', 'PARÁ', 'RONDÔNIA', 'RORAIMA', 'TOCANTINS'],
        'NORDESTE': ['ALAGOAS', 'BAHIA', 'CEARÁ', 'MARANHÃO', 'PARAÍBA', 'PERNAMBUCO', 'PIAUÍ', 'RIO GRANDE DO NORTE', 'SERGIPE'],
        'CENTRO-OESTE': ['DISTRITO FEDERAL', 'GOIÁS', 'MATO GROSSO', 'MATO GROSSO DO SUL'],
        'SUDESTE': ['ESPÍRITO SANTO', 'MINAS GERAIS', 'RIO DE JANEIRO', 'SÃO PAULO'],
        'SUL': ['PARANÁ', 'RIO GRANDE DO SUL', 'SANTA CATARINA']
    }


    postos = Postos.objects.all()
    postos = postos.exclude(produto__iexact='GLP')

    regiao = request.GET.get('regiao')
    estado = request.GET.get('estado')
    produto = request.GET.get('produto')

    if regiao:
        postos = postos.filter(estado__in=REGIOES_BRASIL[regiao])
    if estado:
        postos = postos.filter(estado__iexact=estado)
    if produto:
        postos = postos.filter(produto__iexact=produto)

   # Gráfico de Barras para Produtos
    dados_produtos = postos.values('produto').annotate(
        preco_medio=Avg('preco_revenda'),
        total=Count('id')
    ).order_by('-preco_medio')
    
    grafico_produtos = px.bar(
        dados_produtos,
        x='produto',
        y='preco_medio',
        title='PREÇO MÉDIO POR PRODUTO',
        labels={'produto': 'Produto', 'preco_medio': 'Preço Médio (R$)'},
        color='produto',
        color_discrete_sequence=px.colors.sequential.Greens_r
    )
    grafico_produtos.update_layout(showlegend=False)

    # Gráfico de Pizza para Top 5 Estados
    dados_estados = postos.values('estado').annotate(
        total=Count('id')
    ).order_by('-total')[:5]
    
    grafico_estados = px.pie(
        dados_estados,
        names='estado',
        values='total',
        title='DISTRIBUIÇÃO POR ESTADO (TOP 5)',
        color_discrete_sequence=px.colors.sequential.Greens_r,
        hole=0.3  # Cria efeito de donut
    )
    grafico_estados.update_traces(
        textposition='inside',
        textinfo='percent+label',
        pull=[0.1, 0, 0, 0, 0]  # Destaque para o primeiro estado
    )

    # Converte os gráficos para HTML
    grafico_produtos_html = pio.to_html(grafico_produtos, full_html=False)
    grafico_estados_html = pio.to_html(grafico_estados, full_html=False)

    contexto = {
        'postos': Paginator(postos.order_by('estado', 'municipio'), 25).get_page(request.GET.get('page')),
        'estados_por_regiao': REGIOES_BRASIL.get(regiao, []) if regiao else [],
        'grafico_produtos': grafico_produtos_html,
        'grafico_estados': grafico_estados_html,
        'total_postos': postos.values('numero', 'produto').distinct().count(),
        'preco_medio': postos.aggregate(Avg('preco_revenda'))['preco_revenda__avg'] or 0,
        'total_estados': postos.values('estado').distinct().count(),
        'regioes': sorted(REGIOES_BRASIL.keys()),
        'estados': sorted(set(p.estado for p in postos)),
        'produtos': sorted(set(p.produto for p in postos)),
        'filtros_aplicados': {
            'regiao': regiao,
            'estado': estado,
            'produto': produto
        }
    }

    return render(request, 'dashboard/dashboard_brasil.html', contexto)