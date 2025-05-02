from django.shortcuts import redirect, render
from django.core.paginator import Paginator
from django.db.models import Avg, Count

import matplotlib
# Configura o backend para 'Agg' ANTES de importar pyplot
matplotlib.use('Agg')  # Isso evita o uso do Tkinter
from matplotlib import pyplot as plt
import pandas as pd

import base64
from io import BytesIO

from postos_app.models import Postos
from .utils import normalizar_nome, gerar_grafico, gerar_grafico_ply, gerar_grafico_historico_precos
import plotly.io as pio

pio.templates.default = "plotly_dark"


def dashboard_brasil(request):
    # Configurações das regiões
    REGIOES_BRASIL = {
        'NORTE': ['ACRE', 'AMAPÁ', 'AMAZONAS', 'PARÁ', 'RONDÔNIA', 'RORAIMA', 'TOCANTINS'],
        'NORDESTE': ['ALAGOAS', 'BAHIA', 'CEARÁ', 'MARANHÃO', 'PARAÍBA', 'PERNAMBUCO', 'PIAUÍ', 'RIO GRANDE DO NORTE', 'SERGIPE'],
        'CENTRO-OESTE': ['DISTRITO FEDERAL', 'GOIÁS', 'MATO GROSSO', 'MATO GROSSO DO SUL'],
        'SUDESTE': ['ESPÍRITO SANTO', 'MINAS GERAIS', 'RIO DE JANEIRO', 'SÃO PAULO'],
        'SUL': ['PARANÁ', 'RIO GRANDE DO SUL', 'SANTA CATARINA']
    }

    # Filtros
    postos = Postos.objects.all()
    postos = postos.exclude(produto__iexact='GLP')

    #Receber os filtros vindo do GET caso alguém decida filtrar os dados da página inicial
    regiao = request.GET.get('regiao')
    estado = request.GET.get('estado')
    produto= request.GET.get('produto')

    # Aplicação dos filtros
    if regiao:
        postos = postos.filter(estado__in=REGIOES_BRASIL[regiao])
    if estado:
        postos = postos.filter(estado__iexact=estado)
    if produto:
        postos = postos.filter(produto__iexact=produto)

    # Paginação
    paginador = Paginator(postos.order_by('estado', 'municipio'), 25)
    numero_pagina = request.GET.get('page')
    pagina_obj = paginador.get_page(numero_pagina)

    # Dados para gráficos
    dados_produtos = postos.values('produto').annotate(
        preco_medio=Avg('preco_revenda'),
        total=Count('id')
    ).order_by('-preco_medio')

    # Geração dos gráficos
    grafico_precos = gerar_grafico(
        labels=[p['produto'] for p in dados_produtos],
        valores=[float(p['preco_medio']) for p in dados_produtos],
        titulo='PREÇO MÉDIO POR PRODUTO',
        eixo_y='Preço (R$)'
    )

    dados_estados = postos.values('estado').annotate(
        total=Count('id')
    ).order_by('-total')[:5]

    grafico_estados = gerar_grafico(
        labels=[e['estado'] for e in dados_estados],
        valores=[e['total'] for e in dados_estados],
        titulo='TOP 5 ESTADOS (POSTOS)',
        eixo_y='Quantidade'
    )

    # Contexto para o template
    contexto = {
        'postos': pagina_obj,
        'grafico_preco': grafico_precos,
        'grafico_estados': grafico_estados,
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


def dashboard_cidade(request):
    municipio = request.GET.get('municipio', '').strip()
    produto = request.GET.get('produto', '').strip()
    bairro = request.GET.get('bairro', '').strip()

    if not municipio:
        return redirect('dashboard_brasil')

    postos = Postos.objects.filter(municipio__iexact=municipio)
    postos = postos.exclude(bairro__isnull=True).exclude(bairro__exact='')
    postos = postos.exclude(produto__iexact='GLP')

    if produto:
        postos = postos.filter(produto__iexact=produto)
    if bairro:
        postos = postos.filter(bairro__iexact=bairro)

    dados_bairros = []
    for posto in postos:
        dados_bairros.append({
            'bairro_normalizado': normalizar_nome(posto.bairro),
            'razao' : normalizar_nome(posto.razao),
            'preco': float(posto.preco_revenda),
            'bandeira': posto.bandeira,
            'numero': posto.numero,
            'endereco': posto.endereco,
            'data_coleta': posto.data_coleta,
            'produto': posto.produto
        })

    df = pd.DataFrame(dados_bairros)
    df['data_coleta'] = pd.to_datetime(df['data_coleta'], errors='coerce')

    # Remove duplicatas de postos considerando número + produto para contabilizar corretamente
    df = df.sort_values('data_coleta').drop_duplicates(subset=['numero', 'produto'], keep='last')

    if df.empty:
        return render(request, 'dashboard/dashboard_cidade.html', {
            'municipio': municipio,
            'sem_dados': True
        })

    bairros_stats = df.groupby('bairro_normalizado').agg(
        total_postos=('numero', 'nunique'),
        preco_medio=('preco', 'mean')
    ).reset_index().sort_values('total_postos', ascending=False)

    bairros_df = df.groupby('bairro_normalizado').agg(
        preco_medio=('preco', 'mean'),
        total_postos=('numero', 'nunique')
    ).reset_index().sort_values('preco_medio')

    grafico_1 = gerar_grafico_ply(
        bairros_df.head(10),
        'bairro_normalizado',
        'preco_medio',
        f'Top 10 Bairros com Menor Preço Médio - {municipio}',
        'preco_medio'
    )
    grafico_bairros = pio.to_html(grafico_1, full_html=False)

    total_postos_cidade = df['numero'].nunique()
    preco_medio_cidade = df['preco'].mean()
    total_bairros = len(bairros_stats)

    grafico_2 = gerar_grafico_historico_precos(df)
    grafico_2 = pio.to_html(grafico_2, full_html=False)

    bairros_disponiveis = sorted(df['bairro_normalizado'].unique())
    produtos_disponiveis = sorted(df['produto'].unique())

    # Melhor sugestão de economia
    melhor_posto = df.sort_values('preco').iloc[0].to_dict()
    economia = round(preco_medio_cidade - melhor_posto['preco'], 2)

    context = {
        'municipio': municipio,
        'produto': produto or 'Todos',
        'bairro': bairro,
        'grafico_bairros': grafico_bairros,
        'grafico_historico': grafico_2,
        'total_postos_cidade': total_postos_cidade,
        'preco_medio_cidade': round(preco_medio_cidade, 2),
        'total_bairros': total_bairros,
        'top_bairros': bairros_stats.head(10).to_dict('records'),
        'bairros_disponiveis': bairros_disponiveis,
        'produtos_disponiveis': produtos_disponiveis,
        'melhor_posto': melhor_posto,
        'economia': economia
    }

    return render(request, 'dashboard/dashboard_cidade.html', context)


def melhor_posto(request):
    bairro = request.GET.get('bairro', '').upper().strip()
    produto = request.GET.get('produto', '').upper().strip()
    municipio = request.GET.get('municipio', '').strip().upper()
    if not municipio:
        return redirect('dashboard_brasil')

    # Filtro para postos na cidade
    postos = Postos.objects.filter(municipio__iexact=municipio)
    postos = postos.exclude(bairro__isnull=True).exclude(bairro__exact='')
    postos = postos.exclude(produto__iexact='GLP')

    if produto:
        postos = postos.filter(produto__iexact=produto)
    if bairro:
        postos = postos.filter(bairro__iexact=bairro)

    dados_bairros = []
    for posto in postos:
        dados_bairros.append({
            'bairro_normalizado': normalizar_nome(posto.bairro),
            'razao': normalizar_nome(posto.razao),
            'preco': float(posto.preco_revenda),
            'bandeira': posto.bandeira,
            'numero': posto.numero,
            'endereco': posto.endereco,
            'data_coleta': posto.data_coleta,
            'produto': posto.produto,
            'link_google_maps': f"https://www.google.com/maps/search/?api=1&query={posto.endereco.replace(' ', '+')},{posto.numero}"
        })

    df = pd.DataFrame(dados_bairros)
    df['data_coleta'] = pd.to_datetime(df['data_coleta'], errors='coerce')

    # Remove duplicatas para considerar um único posto por produto
    df = df.sort_values('data_coleta').drop_duplicates(subset=['numero', 'produto'], keep='last')

    # Sugestão de economia: Melhor posto para abastecer
    melhor_posto = df.sort_values('preco').iloc[0].to_dict()
    economia = round(df['preco'].mean() - melhor_posto['preco'], 2)

    # Gráficos
    grafico_1 = gerar_grafico_ply(
        df.groupby('bairro_normalizado').agg(preco_medio=('preco', 'mean')).reset_index(),
        'bairro_normalizado', 'preco_medio', f'Menor Preço Médio - {municipio}', 'preco_medio'
    )

    grafico_2 = gerar_grafico_historico_precos(df)

    context = {
        'municipio': municipio,
        'bairro': bairro,
        'produto': produto,
        'melhor_posto': melhor_posto,
        'economia': economia,
        'grafico_bairros': pio.to_html(grafico_1, full_html=False),
        'grafico_historico': pio.to_html(grafico_2, full_html=False),
    }

    return render(request, 'dashboard/melhor_posto.html', context)


def home_page(request):
    return render(request, 'dashboard/home_page.html')