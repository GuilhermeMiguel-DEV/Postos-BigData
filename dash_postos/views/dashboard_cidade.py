"""
Módulo de visualização do dashboard por cidade.
Analisa e exibe dados de postos de combustível para um município específico.
"""

from django.shortcuts import redirect, render
import pandas as pd
import plotly.express as px
import plotly.io as pio
from postos_app.models import Postos
from dash_postos.utils import normalizar_nome, gerar_grafico_ply, gerar_grafico_historico_precos

# Configura tema escuro padrão para os gráficos Plotly
pio.templates.default = "plotly_dark"

def dashboard_cidade(request):
    """
    View principal do dashboard por cidade.
    
    Processa parâmetros GET e exibe:
    - Estatísticas resumidas do município
    - Gráfico de preços por bairro
    - Histórico temporal de preços
    - Formulário para buscar o melhor posto
    
    Parâmetros GET:
        - municipio: Nome do município (obrigatório)
        - produto: Tipo de combustível (opcional)
        - bairro: Nome do bairro (opcional)
    """

    # Obtém e sanitiza parâmetros da URL
    municipio = request.GET.get('municipio', '').strip()
    produto = request.GET.get('produto', '').strip()
    bairro = request.GET.get('bairro', '').strip()

    # Redireciona se não houver município (parâmetro obrigatório)
    if not municipio:
        return redirect('dashboard_brasil')

    # Query inicial com filtros básicos
    postos = Postos.objects.filter(municipio__iexact=municipio)
    postos = postos.exclude(bairro__isnull=True).exclude(bairro__exact='')
    postos = postos.exclude(produto__iexact='GLP')  # Exclui GLP que tem dinâmica diferente

    # Aplica filtros adicionais se fornecidos
    if produto:
        postos = postos.filter(produto__iexact=produto)
    if bairro:
        postos = postos.filter(bairro__iexact=bairro)

    # Transforma QuerySet em lista de dicionários para processamento
    dados_bairros = []
    for posto in postos:
        dados_bairros.append({
            'bairro_normalizado': normalizar_nome(posto.bairro),
            'razao': normalizar_nome(posto.razao),
            'preco': float(posto.preco_revenda),
            'bandeira': posto.bandeira,
            'numero': posto.numero,  # Identificador único do posto
            'endereco': posto.endereco,
            'data_coleta': posto.data_coleta,
            'produto': posto.produto
        })

    # Retorna template vazio se não houver dados
    if not dados_bairros:
        return render(request, 'dashboard/dashboard_cidade.html', {
            'municipio': municipio,
            'sem_dados': True  # Flag para template exibir mensagem adequada
        })

    # Cria DataFrame pandas para análise avançada
    df = pd.DataFrame(dados_bairros)
    
    # Converte datas e trata valores inválidos
    df['data_coleta'] = pd.to_datetime(df['data_coleta'], errors='coerce')
    
    # Remove duplicatas mantendo apenas a entrada mais recente por posto+produto
    df = df.sort_values('data_coleta').drop_duplicates(
        subset=['numero', 'produto'], 
        keep='last'
    )

    # Agrega dados por bairro para estatísticas
    bairros_stats = df.groupby('bairro_normalizado').agg(
        total_postos=('numero', 'nunique'),  # Conta postos únicos
        preco_medio=('preco', 'mean')
    ).reset_index().sort_values('total_postos', ascending=False)

    # Prepara dados para gráfico de melhores bairros
    bairros_df = df.groupby('bairro_normalizado').agg(
        preco_medio=('preco', 'mean')
    ).reset_index().sort_values('preco_medio')

    # Gera gráfico interativo com Plotly
    grafico_1 = gerar_grafico_ply(
        bairros_df.head(10),  # Top 10 bairros com menores preços
        'bairro_normalizado',
        'preco_medio',
        f'Top 10 Bairros com Menor Preço Médio - {municipio}',
        'preco_medio'
    )
    grafico_bairros = pio.to_html(grafico_1, full_html=False)

    # Calcula estatísticas resumidas
    total_postos_cidade = df['numero'].nunique()  # Contagem distinta de postos
    preco_medio_cidade = df['preco'].mean()
    total_bairros = len(bairros_stats)

    # Gera gráfico histórico
    grafico_2 = gerar_grafico_historico_precos(df)
    grafico_historico = pio.to_html(grafico_2, full_html=False) if grafico_2 else None

    # Prepara listas para filtros do template
    bairros_disponiveis = sorted(df['bairro_normalizado'].unique())
    produtos_disponiveis = sorted(df['produto'].unique())

    # Determina melhor posto para sugestão
    melhor_posto = df.sort_values('preco').iloc[0].to_dict()
    economia = round(preco_medio_cidade - melhor_posto['preco'], 2)

    # Contexto para template
    context = {
        'municipio': municipio,
        'produto': produto or 'Todos',  # Valor padrão
        'bairro': bairro,
        'grafico_bairros': grafico_bairros,
        'grafico_historico': grafico_historico,
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