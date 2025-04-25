# postos_app/serializers.py

from rest_framework import serializers
from .models import Postos

class PostosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Postos
        fields = '__all__'
    
    '''def to_representation(self, instance):
        data = super().to_representation(instance)
        if 'GLP' in data.get('produto', '').upper():
            return None  # Ou filtrar no queryset, como já está sendo feito
        return data'''
