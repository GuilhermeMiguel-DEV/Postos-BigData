"""
Modelo Postos e métodos relacionados.
Define a estrutura de dados dos postos de combustível e comportamentos associados.
"""

from django.db import models
from django.forms import ValidationError

class Postos(models.Model):
    """
    Modelo principal que representa um posto de combustível.
    
    Campos:
        cnpj: CNPJ do posto (18 caracteres)
        razao: Razão social (255 caracteres)
        fantasia: Nome fantasia (255 caracteres)
        endereco: Logradouro (255 caracteres)
        numero: Número do endereço (10 caracteres)
        complemento: Complemento opcional (255 caracteres)
        bairro: Bairro (255 caracteres)
        cep: CEP (9 caracteres)
        municipio: Município (50 caracteres)
        estado: UF (50 caracteres)
        bandeira: Bandeira do posto (50 caracteres)
        produto: Tipo de combustível (50 caracteres)
        unidade_de_medida: Unidade de venda (10 caracteres)
        preco_revenda: Preço (Decimal 10 digitos, 2 decimais)
        data_coleta: Data da coleta (Date)
    """
    
    class Meta:
        db_table = "postos_combustiveis"
        verbose_name_plural = "Postos"

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
        """
        Validação do modelo antes de salvar.
        Impede cadastro de postos com produto GLP.
        
        Raises:
            ValidationError: Se o produto for GLP
        """
        if self.produto and 'GLP' in self.produto.upper():
            raise ValidationError("O produto GLP não é permitido neste sistema.")
            
    @property
    def regiao(self):
        """
        Propriedade que calcula a região geográfica com base no estado.
        
        Returns:
            str: Nome da região (NORTE, NORDESTE, etc.) ou 'DESCONHECIDA'
        """
        REGIOES_BRASIL = {
            'NORTE': ['ACRE', 'AMAPÁ', 'AMAZONAS', 'PARÁ', 'RONDÔNIA', 'RORAIMA', 'TOCANTINS'],
            'NORDESTE': ['ALAGOAS', 'BAHIA', 'CEARÁ', 'MARANHÃO', 'PARAÍBA', 
                         'PERNAMBUCO', 'PIAUÍ', 'RIO GRANDE DO NORTE', 'SERGIPE'],
            'CENTRO-OESTE': ['DISTRITO FEDERAL', 'GOIÁS', 'MATO GROSSO', 'MATO GROSSO DO SUL'],
            'SUDESTE': ['ESPÍRITO SANTO', 'MINAS GERAIS', 'RIO DE JANEIRO', 'SÃO PAULO'],
            'SUL': ['PARANÁ', 'RIO GRANDE DO SUL', 'SANTA CATARINA']
        }
        estado_upper = self.estado.upper().strip()
        for regiao, estados in REGIOES_BRASIL.items():
            if estado_upper in estados:
                return regiao
        return 'DESCONHECIDA'