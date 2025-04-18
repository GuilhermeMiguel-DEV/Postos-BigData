from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Avg, Count
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from postos_app.models import Postos

def dash_graficos(request):
    # Configurações das regiões
    REGIOES_BRASIL = {
        'NORTE': ['ACRE', 'AMAPÁ', 'AMAZONAS', 'PARÁ', 'RONDÔNIA', 'RORAIMA', 'TOCANTINS'],
        'NORDESTE': ['ALAGOAS', 'BAHIA', 'CEARÁ', 'MARANHÃO', 'PARAÍBA', 'PERNAMBUCO', 'PIAUÍ', 'RIO GRANDE DO NORTE', 'SERGIPE'],
        'CENTRO-OESTE': ['DISTRITO FEDERAL', 'GOIÁS', 'MATO GROSSO', 'MATO GROSSO DO SUL'],
        'SUDESTE': ['ESPÍRITO SANTO', 'MINAS GERAIS', 'RIO DE JANEIRO', 'SÃO PAULO'],
        'SUL': ['PARANÁ', 'RIO GRANDE DO SUL', 'SANTA CATARINA']
    }

    def gerar_grafico(labels, valores, titulo, eixo_y):
        """Função auxiliar para gerar gráficos"""
        plt.figure(figsize=(10, 5))
        plt.bar(labels, valores, color='#3498db')
        plt.title(titulo, pad=20)
        plt.ylabel(eixo_y)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=80, bbox_inches='tight')
        plt.close()
        return base64.b64encode(buffer.getvalue()).decode()

    # Filtros
    postos = Postos.objects.all()
    postos.exclude(produto__iexact='GLP')
    regiao = request.GET.get('regiao')
    estado = request.GET.get('estado')
    produto = request.GET.get('produto')

    # Aplicação dos filtros
    if regiao:
        postos = postos.filter(estado__in=REGIOES_BRASIL[regiao])
    if estado:
        postos = postos.filter(estado__iexact=estado)
    if produto:
        postos = postos.filter(produto__iexact=produto).exclude(produto__iexact='GLP')

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
    ).order_by('-total')[:10]

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