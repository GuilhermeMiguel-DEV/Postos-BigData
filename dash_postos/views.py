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
from .utils import normalizar_nome, gerar_grafico

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
        'total_postos': postos.count(),
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
    
    # Se cidade estiver vazia, redireciona para o dashboard Brasil
    if not municipio:
        return redirect('dashboard_brasil')
    
    # Filtra os postos pelo municipio (case-insensitive)
    postos = Postos.objects.filter(
        municipio__iexact=municipio
    ).exclude(
        bairro__isnull=True
    ).exclude(
        bairro__exact=''
    ).exclude(produto__iexact='GLP')
    
    # Filtro adicional por produto se especificado
    if produto:
        postos = postos.filter(produto__iexact=produto)
    
    # Normaliza os nomes dos bairros e agrupa
    dados_bairros = []
    for posto in postos:
        dados_bairros.append({
            'bairro_normalizado': normalizar_nome(posto.bairro),
            'preco': float(posto.preco_revenda),
            'bandeira': posto.bandeira,
            'numero': posto.numero,
            'endereco': posto.endereco
        })
    
    # Cria DataFrame para análise
    df = pd.DataFrame(dados_bairros)
    
    # Se não houver dados, mostra mensagem
    if df.empty:
        return render(request, 'dashboard/dashboard_cidade.html', {
            'municipio': municipio,
            'sem_dados': True
        })
    
    # Agrupa por bairro para estatísticas
    bairros_stats = df.groupby('bairro_normalizado').agg(
        total_postos=('bairro_normalizado', 'size'),
        preco_medio=('preco', 'mean')
    ).reset_index().sort_values('total_postos', ascending=False)
    
    # Cria gráfico de barras de postos por bairro
    plt.figure(figsize=(10, 6))
    ax = bairros_stats.head(10).plot.bar(
        x='bairro_normalizado', 
        y='total_postos',
        color='skyblue',
        legend=False
    )
    plt.title(f'Top 10 Bairros com Mais Postos em {municipio}')
    plt.xlabel('Bairro')
    plt.ylabel('Número de Postos')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Converte gráfico para imagem base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    grafico_bairros = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    
    # Prepara dados para a tabela
    tabela_bairros = bairros_stats.to_dict('records')

    
    # Calcula estatísticas gerais
    postos_unicos = df.drop_duplicates(subset=['numero'])
    # print(postos_unicos)
    # print('='*15)
    # print(df)
    total_postos_cidade = len(df)
    preco_medio_cidade = df['preco'].mean()
    total_bairros = len(bairros_stats)

    context = {
        'municipio': municipio,
        'produto': produto or 'Todos',
        'grafico_bairros': grafico_bairros,
        'tabela_bairros': tabela_bairros,
        'total_postos_cidade': total_postos_cidade,
        'preco_medio_cidade': round(preco_medio_cidade, 2),
        'total_bairros': total_bairros,
        'top_bairros': bairros_stats.head(10).to_dict('records')
    }
    
    return render(request, 'dashboard/dashboard_cidade.html', context)
