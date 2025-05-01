import unicodedata
from matplotlib import pyplot as plt
from io import BytesIO
import base64
import plotly.express as px
import pandas as pd


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
    ultimos_30 = df[df['data_coleta'] > pd.Timestamp.today() - pd.Timedelta(days=90)]

    # Agrupar dados
    historico = ultimos_30.groupby(['data_coleta', 'bairro_normalizado']).agg(
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
        color='bairro_normalizado',
        markers=True,  # Mostra pontos
        line_shape='linear',  # Usa linhas retas entre os pontos
        title='Histórico de Preços por Bairro (Últimos 30 dias)',
        labels={
            'data_coleta': 'Data',
            'preco_medio': 'Preço Médio (R$)',
            'bairro_normalizado': 'Bairro'
        }
    )

    # Ajustes visuais adicionais
    fig.update_traces(line=dict(width=2))  # Linhas mais visíveis
    fig.update_layout(
        xaxis_title='Data',
        yaxis_title='Preço Médio (R$)',
        hovermode='x unified',
        template='plotly_white'
    )

    return fig
