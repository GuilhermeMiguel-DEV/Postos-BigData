from django.shortcuts import redirect, render

import matplotlib

matplotlib.use('Agg')
from matplotlib import pyplot as plt
import pandas as pd

from postos_app.models import Postos
from dash_postos.utils import normalizar_nome, gerar_grafico, gerar_grafico_ply, gerar_grafico_historico_precos
import plotly.io as pio

pio.templates.default = "plotly_dark"


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
