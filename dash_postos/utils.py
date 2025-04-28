import unicodedata
from matplotlib import pyplot as plt
from io import BytesIO
import base64
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
