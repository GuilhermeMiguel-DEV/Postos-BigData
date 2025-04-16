from django.db import models
from django.forms import ValidationError

class Postos(models.Model):
    class Meta:
        db_table = "postos_combustiveis"

    cnpj = models.CharField(max_length=18)
    razao = models.CharField(max_length=255)
    fantasia = models.CharField(max_length=255)
    endereco = models.CharField(max_length=255)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=255, blank=True, null=True)
    bairro = models.CharField(max_length=255)
    cep = models.CharField(max_length=9)

    municipio = models.CharField(max_length=50)
    estado = models.CharField(max_length=50)

    bandeira = models.CharField(max_length=50)
    produto = models.CharField(max_length=50)
    unidade_de_medida = models.CharField(max_length=10)

    preco_revenda = models.DecimalField(max_digits=10, decimal_places=2)
    data_coleta = models.DateField()

    def clean(self):
        if self.produto and 'GLP' in self.produto.upper():
            raise ValidationError("O produto GLP não é permitido neste sistema.")
<<<<<<< HEAD
    def save(self, *args, **kwargs):
        """Auto-preencher região ao salvar"""
        self.regiao = self.get_regiao_from_estado()
        super().save(*args, **kwargs)
    
@property
def regiao(self):
    """Determina a região com base no estado"""
    REGIOES_BRASIL = {
        'NORTE': ['ACRE', 'AMAPÁ', 'AMAZONAS', 'PARÁ', 'RONDÔNIA', 'RORAIMA', 'TOCANTINS'],
        'NORDESTE': ['ALAGOAS', 'BAHIA', 'CEARÁ', 'MARANHÃO', 'PARAÍBA', 'PERNAMBUCO', 'PIAUÍ', 'RIO GRANDE DO NORTE', 'SERGIPE'],
        'CENTRO-OESTE': ['DISTRITO FEDERAL', 'GOIÁS', 'MATO GROSSO', 'MATO GROSSO DO SUL'],
        'SUDESTE': ['ESPÍRITO SANTO', 'MINAS GERAIS', 'RIO DE JANEIRO', 'SÃO PAULO'],
        'SUL': ['PARANÁ', 'RIO GRANDE DO SUL', 'SANTA CATARINA']
    }
    estado_upper = self.estado.upper().strip()
    for regiao, estados in REGIOES_BRASIL.items():
        if estado_upper in estados:
            return regiao
    return 'DESCONHECIDA'
=======
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
>>>>>>> 5c8bbf3c846bd4c215f908588cdb6d2f42950ad8
