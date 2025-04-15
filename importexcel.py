import os
import django
import pandas as pd

# Configurar o Django manualmente
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BigDataPostos.settings")  # Substitua pelo nome correto do projeto
django.setup()

from postos_app.models import Postos  # Agora o Django está configurado

# Carregar o Excel
df = pd.read_excel("postos.xlsx")  # Arquivo Excel com os dados

# Inserir os dados no banco
for _, row in df.iterrows():
    Postos.objects.create(
        cnpj=row["CNPJ"],
        razao=row["RAZÃO"],
        fantasia=row["FANTASIA"],
        endereco=row["ENDEREÇO"],
        numero=row["NÚMERO"],
        complemento=row["COMPLEMENTO"],
        bairro=row["BAIRRO"],
        cep=row["CEP"],
        municipio=row["MUNICÍPIO"],
        estado=row["ESTADO"],
        bandeira=row["BANDEIRA"],
        produto=row["PRODUTO"],
        unidade_de_medida=row["UNIDADE DE MEDIDA"],
        preco_revenda=row["PREÇO DE REVENDA"],
        data_coleta=row["DATA DA COLETA"]
    )

print("Importação concluída!")
