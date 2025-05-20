"""
Visualizações para o aplicativo postos_app.
Lógica para renderização de templates e endpoints da API.
"""

from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Postos
from .utils import normalizar_texto

@api_view(['GET'])
def listar_postos(request):
    """
    View para listagem de postos com suporte a JSON e HTML.
    
    Parâmetros GET:
        bairro: Filtro por bairro (opcional)
        municipio: Município para filtro (default: 'Salvador')
    
    Retornos:
        JSON: Para requisições API
        HTML: Para navegadores (template postos_tabela.html)
    """
    
    # Obtém parâmetros da requisição
    bairro = request.GET.get('bairro', '').strip()
    municipio = request.GET.get('municipio', 'Salvador').strip()
    
    # Consulta inicial com filtros básicos
    postos = Postos.objects.filter(
        municipio__iexact=normalizar_texto(municipio)
    ).exclude(
        produto__iexact='GLP'
    ).exclude(
        bairro__isnull=True
    )

    # Aplica filtro adicional por bairro se fornecido
    if bairro:
        bairro_normalizado = normalizar_texto(bairro)
        postos = postos.filter(bairro__icontains=bairro_normalizado)

    # Filtra valores nulos e ordena
    postos = postos.exclude(
        preco_revenda__isnull=True,
        produto__isnull=True,
        bandeira__isnull=True
    ).order_by('bairro', 'produto')

    # Serialização dos dados para API
    if 'application/json' in request.headers.get('Accept', ''):
        postos_list = [{
            'id': p.id,
            'bairro': p.bairro,
            'endereco': p.endereco,
            'numero': p.numero,
            'complemento': p.complemento if p.complemento else None,
            'produto': p.produto,
            'preco_revenda': float(p.preco_revenda),
            'bandeira': p.bandeira,
            'razao': p.razao
        } for p in postos]
        
        return Response({
            'status': 'success',
            'count': len(postos_list),
            'data': postos_list
        })
    
    # Renderização do template HTML
    bairros_unicos = sorted(set(
        p.bairro for p in postos if p.bairro
    ), key=lambda x: normalizar_texto(x))
    
    return render(request, 'postos_app/postos_tabela.html', {
        'postos': postos,
        'bairros_unicos': bairros_unicos,
        'municipio': municipio,
        'bairro': bairro if bairro else 'Todos'
    })