from django.db import models
from django.forms import ValidationError

class Postos(models.Model):
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
        """Validação do modelo"""
        if self.produto and 'GLP' in self.produto.upper():
            raise ValidationError("O produto GLP não é permitido neste sistema.")

    def save(self, *args, **kwargs):
        """Sobrescrita do save com validação"""
        self.full_clean()
        self.regiao = self._get_regiao_from_estado()  # Atualiza a região antes de salvar
        super().save(*args, **kwargs)

    def _get_regiao_from_estado(self):
        """Método interno para determinar a região"""
        REGIOES = {
            'NORTE': ['ACRE', 'AMAPÁ', 'AMAZONAS', 'PARÁ', 'RONDÔNIA', 'RORAIMA', 'TOCANTINS'],
            'NORDESTE': ['ALAGOAS', 'BAHIA', 'CEARÁ', 'MARANHÃO', 'PARAÍBA', 'PERNAMBUCO', 'PIAUÍ', 'RIO GRANDE DO NORTE', 'SERGIPE'],
            'CENTRO-OESTE': ['DISTRITO FEDERAL', 'GOIÁS', 'MATO GROSSO', 'MATO GROSSO DO SUL'],
            'SUDESTE': ['ESPÍRITO SANTO', 'MINAS GERAIS', 'RIO DE JANEIRO', 'SÃO PAULO'],
            'SUL': ['PARANÁ', 'RIO GRANDE DO SUL', 'SANTA CATARINA']
        }
        estado_upper = self.estado.upper().strip()
        for regiao, estados in REGIOES.items():
            if estado_upper in estados:
                return regiao
        return 'DESCONHECIDA'

    @property
    def regiao(self):
        """Propriedade que acessa o campo regiao se existir, ou calcula dinamicamente"""
        if hasattr(self, '_regiao'):
            return self._regiao
        return self._get_regiao_from_estado()

    
   