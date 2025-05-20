"""
Módulo de API para endpoints utilitários do sistema.
Fornece dados auxiliares para funcionalidades dinâmicas da interface.
"""

from django.http import JsonResponse
from django.views import View

# Mapeamento constante das regiões brasileiras e seus estados
REGIOES_BRASIL = {
    'NORTE': ['ACRE', 'AMAPÁ', 'AMAZONAS', 'PARÁ', 'RONDÔNIA', 'RORAIMA', 'TOCANTINS'],
    'NORDESTE': ['ALAGOAS', 'BAHIA', 'CEARÁ', 'MARANHÃO', 'PARAÍBA', 'PERNAMBUCO', 'PIAUÍ', 'RIO GRANDE DO NORTE', 'SERGIPE'],
    'CENTRO-OESTE': ['DISTRITO FEDERAL', 'GOIÁS', 'MATO GROSSO', 'MATO GROSSO DO SUL'],
    'SUDESTE': ['ESPÍRITO SANTO', 'MINAS GERAIS', 'RIO DE JANEIRO', 'SÃO PAULO'],
    'SUL': ['PARANÁ', 'RIO GRANDE DO SUL', 'SANTA CATARINA']
}

class EstadosPorRegiaoView(View):
    """
    Endpoint API que retorna estados filtrados por região.
    
    Método: GET
    Parâmetros:
        - regiao: Nome da região (ex: 'SUDESTE')
    
    Retorno JSON:
        {
            "estados": ["ESTADO1", "ESTADO2", ...]
        }
    """

    def get(self, request):
        """
        Processa requisições GET para obter estados por região.
        
        Args:
            request: Objeto HttpRequest com parâmetros GET
            
        Returns:
            JsonResponse: Lista de estados da região ou lista vazia se região inválida
        """
        try:
            # Obtém e normaliza parâmetro da região
            regiao = request.GET.get('regiao', '').upper()
            
            # Recupera estados da região ou lista vazia se não existir
            estados = REGIOES_BRASIL.get(regiao, [])
            
            return JsonResponse({
                'estados': sorted(estados)  # Retorna em ordem alfabética
            })
            
        except Exception as e:
            # Log de erro em produção deveria ser adicionado aqui
            return JsonResponse({
                'estados': [],
                'erro': 'Falha ao processar requisição'
            }, status=400)