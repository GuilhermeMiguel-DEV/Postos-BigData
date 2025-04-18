from django.shortcuts import render
from django.db.models import Avg, Count
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from postos_app.models import Postos

def dash_graficos(request):
    # Mapeamento de regiões (já atualizado com nomes completos)
    REGIOES_BRASIL = {
        'NORTE': ['ACRE', 'AMAPÁ', 'AMAZONAS', 'PARÁ', 'RONDÔNIA', 'RORAIMA', 'TOCANTINS'],
        'NORDESTE': ['ALAGOAS', 'BAHIA', 'CEARÁ', 'MARANHÃO', 'PARAÍBA', 'PERNAMBUCO', 'PIAUÍ', 'RIO GRANDE DO NORTE', 'SERGIPE'],
        'CENTRO-OESTE': ['DISTRITO FEDERAL', 'GOIÁS', 'MATO GROSSO', 'MATO GROSSO DO SUL'],
        'SUDESTE': ['ESPÍRITO SANTO', 'MINAS GERAIS', 'RIO DE JANEIRO', 'SÃO PAULO'],
        'SUL': ['PARANÁ', 'RIO GRANDE DO SUL', 'SANTA CATARINA']
    }

    def generate_bar_chart(labels, values, title, ylabel):
        """Gera gráfico de barras e retorna como base64"""
        plt.figure(figsize=(10, 5))
        plt.bar(labels, values, color='#3498db')
        plt.title(title, pad=20)
        plt.ylabel(ylabel)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=80, bbox_inches='tight')
        plt.close()
        return base64.b64encode(buffer.getvalue()).decode()

    def dashboard_brasil(request):
        # Filtros
        postos = Postos.objects.all()
        regiao = request.GET.get('regiao')
        estado = request.GET.get('estado')
        produto = request.GET.get('produto')

        # Aplica filtros
        if regiao:
            postos = postos.filter(estado__in=REGIOES_BRASIL[regiao])
        if estado:
            postos = postos.filter(estado__iexact=estado)
        if produto:
            postos = postos.filter(produto__iexact=produto)

        # Dados para gráficos
        produtos_data = postos.values('produto').annotate(
            avg_price=Avg('preco_revenda'),
            count=Count('id')
        ).order_by('-avg_price')

        # Gráfico 1: Preço médio por produto
        grafico_preco = generate_bar_chart(
            labels=[p['produto'] for p in produtos_data],
            values=[float(p['avg_price']) for p in produtos_data],
            title='PREÇO MÉDIO POR PRODUTO',
            ylabel='Preço (R$)'
        )

        # Gráfico 2: Postos por estado (top 10)
        estados_data = postos.values('estado').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        grafico_estados = generate_bar_chart(
            labels=[e['estado'] for e in estados_data],
            values=[e['count'] for e in estados_data],
            title='TOP 10 ESTADOS (POSTOS)',
            ylabel='Quantidade'
        )

        context = {
            'grafico_preco': grafico_preco,
            'grafico_estados': grafico_estados,
            'total_postos': postos.count(),
            'preco_medio': postos.aggregate(Avg('preco_revenda'))['preco_revenda__avg'] or 0,
            'regioes': REGIOES_BRASIL.keys(),
            'filtros_aplicados': {
                'regiao': regiao,
                'estado': estado,
                'produto': produto
            }
        }
        return render(request, 'postos/dashboard_brasil.html', context)