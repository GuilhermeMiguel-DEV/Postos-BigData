from django.shortcuts import redirect, render

import matplotlib
# Configura o backend para 'Agg' ANTES de importar pyplot
matplotlib.use('Agg')  # Isso evita o uso do Tkinter
from matplotlib import pyplot as plt
import pandas as pd

import base64
from io import BytesIO

from postos_app.models import Postos
from dash_postos.utils import normalizar_nome, gerar_grafico, gerar_grafico_ply, gerar_grafico_historico_precos
import plotly.io as pio

pio.templates.default = "plotly_dark"

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
