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
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)