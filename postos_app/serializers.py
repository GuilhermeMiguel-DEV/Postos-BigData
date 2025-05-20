"""
Serializadores para o modelo Postos.
Transforma objetos Postos em formatos JSON e vice-versa para a API REST.
"""

from rest_framework import serializers
from .models import Postos

class PostosSerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo Postos.
    
    Meta:
        model: Modelo Postos
        fields: Todos os campos do modelo
        
    Funcionalidades:
        - Serialização completa de objetos Postos
        - Validação de dados para criação/atualização
        - Transformação para representação JSON
    """
    
    class Meta:
        model = Postos
        fields = '__all__'