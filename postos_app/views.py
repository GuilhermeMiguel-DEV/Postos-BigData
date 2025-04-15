from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Postos
from .utils import normalizar_texto

@api_view(['GET'])
def listar_postos(request):
    bairro = request.GET.get('bairro', '').strip()
    municipio = request.GET.get('municipio', 'Salvador').strip()
    
    # Consulta base - SQLite não suporta unaccent nativamente
    # Usaremos a normalização via Python
    postos = Postos.objects.filter(
        municipio__iexact=normalizar_texto(municipio)
    ).exclude(
        produto__iexact='GLP'
    ).exclude(
        bairro__isnull=True
    )

    if bairro:
        bairro_normalizado = normalizar_texto(bairro)
        # Filtro case-insensitive com normalização
        postos = postos.filter(bairro__icontains=bairro_normalizado)

    # Filtra valores nulos
    postos = postos.exclude(
        preco_revenda__isnull=True,
        produto__isnull=True,
        bandeira__isnull=True
    ).order_by('bairro', 'produto')

    # Serialização dos dados
    postos_list = [] 

    for posto in postos:    
        if posto.complemento and str(posto.complemento).lower() == 'nan':
            posto.complemento = None
        postos_list.append({
            'id': posto.id,
            'bairro': posto.bairro,
            'endereco': posto.endereco,
            'numero': posto.numero,
            'complemento': posto.complemento if posto.complemento else None,
            'produto': posto.produto,
            'preco_revenda': float(posto.preco_revenda),
            'bandeira': posto.bandeira,
            'razao': posto.razao
        })

        if 'application/json' in request.headers.get('Accept', ''):
            return Response({
                'status': 'success',
                'count': len(postos_list),
                'data': postos_list
            })
    else:
        # Para a view HTML
        bairros_unicos = sorted(set(
            p.bairro for p in postos if p.bairro
        ), key=lambda x: normalizar_texto(x))
        
        return render(request, 'postos_app/postos_tabela.html', {
            'postos': postos,
            'bairros_unicos': bairros_unicos,
            'municipio': municipio,
            'bairro': bairro if bairro else 'Todos'
        })