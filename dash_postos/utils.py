import unicodedata
from matplotlib import pyplot as plt
from io import BytesIO
import base64
import plotly.express as px
import pandas as pd

import requests
import os


def normalizar_nome(texto):
    """Normaliza nomes removendo acentos, espaços extras e convertendo para maiúsculas"""
    if not texto:
        return ""
    # Remove acentos
    texto = unicodedata.normalize('NFKD', str(texto))
    texto = texto.encode('ASCII', 'ignore').decode('ASCII')
    # Remove espaços extras e converte para Title Case
    return ' '.join(texto.strip().title().split())

def gerar_grafico(labels, valores, titulo, eixo_y):
    """Função auxiliar para gerar gráficos"""
    plt.figure(figsize=(15, 8))
    plt.bar(labels, valores, color='#3498db')
    plt.title(titulo, pad=20)
    plt.ylabel(eixo_y)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=80, bbox_inches='tight')
    plt.close()
    return base64.b64encode(buffer.getvalue()).decode()


def gerar_grafico_ply(df, x, y, title, media):
    grafico = px.bar(
        df,
        x=x,
        y=y,
        title=title,
        labels={x: 'Bairro', y: 'Preço Médio (R$)'},
        color=media,
        color_continuous_scale='Greens'
    )
    return grafico


def gerar_grafico_historico_precos(df):
    # Garantir formatos corretos
    df = df.copy()
    df['data_coleta'] = pd.to_datetime(df['data_coleta'], errors='coerce')
    df['preco'] = pd.to_numeric(df['preco'], errors='coerce')

    # Remover nulos essenciais
    df = df.dropna(subset=['data_coleta', 'preco', 'bairro_normalizado'])

    # Filtrar últimos 30 dias
    ultimos_30 = df[df['data_coleta'] > pd.Timestamp.today() - pd.Timedelta(days=30)]

    # Agrupar dados
    historico = ultimos_30.groupby(['data_coleta', 'razao']).agg(
        preco_medio=('preco', 'mean')
    ).reset_index()

    # Evitar gráfico vazio
    if historico.empty:
        print("Sem dados nos últimos 30 dias.")
        return None

    # Criar gráfico com linhas marcadas e pontos visíveis
    fig = px.line(
        historico,
        x='data_coleta',
        y='preco_medio',
        color='razao',
        markers=True,  # Mostra pontos
        line_shape='linear',  # Usa linhas retas entre os pontos
        title='Histórico de Preços por posto (Últimos 30 dias)',
        labels={
            'data_coleta': 'Data',
            'preco_medio': 'Preço Médio (R$)',
            'razao': 'Posto'
        }
    )

    # Ajustes visuais adicionais
    fig.update_traces(line=dict(width=2))  # Linhas mais visíveis
    fig.update_layout(
        xaxis_title='Data',
        yaxis_title='Preço Médio (R$)',
        hovermode='x unified',
    )

    return fig




def ler_arquivo(nome_arquivo):
  """Lê o conteúdo de um arquivo .txt.

  Args:
    nome_arquivo: O nome do arquivo a ser lido.

  Returns:
    O conteúdo do arquivo como uma string, ou None se ocorrer um erro.
  """
  try:
    with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
      conteudo = arquivo.read()
    return conteudo
  except FileNotFoundError:
    print(f"Erro: Arquivo '{nome_arquivo}' não encontrado.")
    return None
  except Exception as e:
    print(f"Erro ao ler o arquivo: {e}")
    return None


def escrever_arquivo(nome_arquivo, conteudo):
  """Escreve o conteúdo em um arquivo .txt.

  Args:
    nome_arquivo: O nome do arquivo a ser escrito.
    conteudo: O conteúdo a ser escrito no arquivo.
  """
  try:
    with open(nome_arquivo, 'a', encoding='utf-8') as arquivo:
      arquivo.writelines(conteudo)
    print(f"Conteúdo escrito com sucesso em '{nome_arquivo}'.")
  except Exception as e:
    print(f"Erro ao escrever no arquivo: {e}")


def perguntar_gemini(info_posto,  municipio, bairro, produto ):
    # Substitua 'YOUR_GEMINI_API_KEY' pela sua chave de API real
    api_key = 'AIzaSyDYYSbo0JzERHMwSHMZ7GlAj5OXj0keoQM'
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + api_key

    headers = {
        'Content-Type': 'application/json'
    }


    if info_posto:
        data = {
            "contents": {
                "parts": {"text": f"Sugira de forma breve sem links e tem austerísticos, o melhor posto em {municipio} {bairro} e com o produto {produto}(caso não haja produto, diga uma sugestão para alguns produtos) a partir dessas informações: " + info_posto}
            }
        }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        texto = response.json().get('candidates')[0].get('content').get('parts')[0].get('text')

        return texto

    else:
       return 'Erro.'
    # response.text


