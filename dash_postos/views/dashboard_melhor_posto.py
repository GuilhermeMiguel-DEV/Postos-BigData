# dashboard_melhor_posto.py

from django.shortcuts import redirect, render
import pandas as pd
from postos_app.models import Postos
from dash_postos.utils import (normalizar_nome, gerar_grafico_ply, gerar_grafico_historico_precos, perguntar_gemini)
import plotly.io as pio
import plotly.express as px

# Configura o tema padrão para os gráficos Plotly
pio.templates.default = "plotly_dark"

def melhor_posto(request):
    """
    View principal para exibir o melhor posto de combustível com base nos filtros.
    Processa os parâmetros GET, filtra os postos e gera visualizações dos dados.
    
    Parâmetros GET esperados:
    - municipio: Nome do município para filtrar
    - bairro: (opcional) Nome do bairro para filtrar
    - produto: (opcional) Tipo de produto para filtrar
    """
    
    # Normalização e tratamento dos parâmetros de entrada
    bairro = request.GET.get('bairro', '').upper().strip()
    produto = request.GET.get('produto', '').upper().strip()
    municipio = request.GET.get('municipio', '').strip().upper()
    
    # Redireciona se não houver município (filtro obrigatório)
    if not municipio:
        return redirect('dashboard_brasil')

    # Query inicial com filtros básicos
    postos = Postos.objects.filter(municipio__iexact=municipio)
    postos = postos.exclude(bairro__isnull=True).exclude(bairro__exact='')
    postos = postos.exclude(produto__iexact='GLP')  # Exclui GLP que tem lógica diferente

    # Aplica filtros adicionais se fornecidos
    if produto:
        postos = postos.filter(produto__iexact=produto)
    if bairro:
        postos = postos.filter(bairro__iexact=bairro)

    # Transforma os dados do queryset em uma lista de dicionários
    # Isso facilita a manipulação com pandas depois
    dados_bairros = []
    for posto in postos:
        dados_bairros.append({
            'bairro_normalizado': normalizar_nome(posto.bairro),  # Padroniza formato do nome
            'razao': normalizar_nome(posto.razao),
            'preco': float(posto.preco_revenda),
            'bandeira': posto.bandeira,
            'numero': posto.numero,  # Usado como ID único do posto
            'endereco': posto.endereco,
            'data_coleta': posto.data_coleta,
            'produto': posto.produto,
            # Gera link para o Google Maps com o endereço
            'link_google_maps': f"https://www.google.com/maps/search/?api=1&query={posto.endereco.replace(' ', '+')},{posto.numero}"
        })

    # Retorna template vazio se não houver dados
    if not dados_bairros:
        return render(request, 'dashboard/melhor_posto.html', {
            'municipio': municipio,
            'bairro': bairro,
            'produto': produto
        })

    # Cria DataFrame pandas para manipulação avançada dos dados
    df = pd.DataFrame(dados_bairros)
    
    # Tratamento especial para datas - converte para formato datetime do pandas
    # Usa coerção para evitar erros com formatos inválidos
    if 'data_coleta' in df.columns:
        df['data_coleta'] = pd.to_datetime(df['data_coleta'], errors='coerce')
    else:
        # Se não houver data, usa a data atual como fallback
        df['data_coleta'] = pd.to_datetime('today')

    # Remove duplicatas mantendo apenas a entrada mais recente para cada combinação de posto+produto
    # Isso evita mostrar dados duplicados ou desatualizados
    df = df.sort_values('data_coleta').drop_duplicates(subset=['numero', 'produto'], keep='last')

    # Verifica novamente se há dados após o processamento
    if df.empty:
        return render(request, 'dashboard/melhor_posto.html', {
            'municipio': municipio,
            'bairro': bairro,
            'produto': produto
        })

    # Determina o melhor posto (menor preço) e calcula economia
    try:
        # Ordena por preço e pega o primeiro registro
        melhor_posto = df.sort_values('preco').iloc[0].to_dict()
        
        # Calcula economia comparando com a média de preços
        economia = round(df['preco'].mean() - melhor_posto['preco'], 2)
        
        # Gera recomendação usando a API Gemini (IA generativa)
        resposta_ia = perguntar_gemini(df.to_string(), municipio, bairro, produto)

    except (KeyError, IndexError) as e:
        # Trata erros caso não haja dados válidos após o processamento
        print(f"Erro ao processar melhor posto: {e}")
        return render(request, 'dashboard/melhor_posto.html', {
            'municipio': municipio,
            'bairro': bairro,
            'produto': produto
        })

    # --- Geração dos Gráficos ---

    # 1. Gráfico de produtos do posto selecionado
    # Filtra apenas os produtos do posto escolhido (melhor preço)
    produtos_posto = df[df['numero'] == melhor_posto['numero']]
    
    grafico_produtos = None
    if not produtos_posto.empty:
        # Cria gráfico de barras com Plotly Express
        grafico_produtos = px.bar(
            produtos_posto,
            x='produto',  # Eixo X: nomes dos produtos
            y='preco',    # Eixo Y: preços dos produtos
            title=f'Preços por Produto - {melhor_posto["razao"]}',
            labels={'produto': 'Produto', 'preco': 'Preço (R$)'},
            color='produto',  # Cores diferentes para cada produto
            color_discrete_sequence=px.colors.sequential.Greens_r  # Escala de verdes
        )
        # Remove legenda para economizar espaço (rótulos já estão no eixo X)
        grafico_produtos.update_layout(showlegend=False)

    # 2. Gráfico histórico (mantido da versão anterior)
    grafico_historico = gerar_grafico_historico_precos(df) if not df.empty else None

    # Prepara contexto para o template
    context = {
        'municipio': municipio,
        'bairro': bairro,
        'produto': produto,
        'melhor_posto': melhor_posto,  # Dicionário com info do melhor posto
        'resposta_ia': resposta_ia,   # Recomendação gerada pela IA
        'economia': economia,         # Valor economizado em relação à média
        # Gráficos convertidos para HTML
        'grafico_produtos': pio.to_html(grafico_produtos, full_html=False) if grafico_produtos else None,
        'grafico_historico': pio.to_html(grafico_historico, full_html=False) if grafico_historico else None,
    }

    return render(request, 'dashboard/melhor_posto.html', context)