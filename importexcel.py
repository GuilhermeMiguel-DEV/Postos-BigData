import os
import django
import pandas as pd

# Configurar o Django manualmente
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BigDataPostos.settings")  # Substitua pelo nome correto do projeto
django.setup()

from postos_app.models import Postos  # Agora o Django está configurado

# Caminho da pasta com os arquivos Excel
pasta_dados = "imports"  # Substitua pelo caminho real

# Percorrer todos os arquivos na pasta
for arquivo in os.listdir(pasta_dados):
    if arquivo.endswith(".xlsx") or arquivo.endswith(".xls"):
        caminho_arquivo = os.path.join(pasta_dados, arquivo)
        print(f"Importando: {caminho_arquivo}")

        # Carregar o Excel
        df = pd.read_excel(caminho_arquivo)

        # Inserir os dados no banco
        for _, row in df.iterrows():
            Postos.objects.create(
                cnpj=row.get("CNPJ"),
                razao=row.get("RAZÃO"),
                fantasia=row.get("FANTASIA"),
                endereco=row.get("ENDEREÇO"),
                numero=row.get("NÚMERO"),
                complemento=row.get("COMPLEMENTO"),
                bairro=row.get("BAIRRO"),
                cep=row.get("CEP"),
                municipio=row.get("MUNICÍPIO"),
                estado=row.get("ESTADO"),
                bandeira=row.get("BANDEIRA"),
                produto=row.get("PRODUTO"),
                unidade_de_medida=row.get("UNIDADE DE MEDIDA"),
                preco_revenda=row.get("PREÇO DE REVENDA"),
                data_coleta=row.get("DATA DA COLETA")
            )

print("Importação concluída para todos os arquivos!")
