"""
Utilitários para o aplicativo postos_app.
Funções auxiliares para processamento de dados.
"""

import unicodedata

def normalizar_texto(texto):
    """
    Normaliza strings removendo acentos, espaços extras e convertendo para minúsculas.
    
    Args:
        texto (str): Texto a ser normalizado
        
    Returns:
        str: Texto normalizado em minúsculas sem acentos
        
    Exemplo:
        >>> normalizar_texto("São Paulo")
        'sao paulo'
    """
    if not texto:
        return ""
    # Remove acentos e caracteres especiais
    texto = unicodedata.normalize('NFKD', str(texto))
    texto = texto.encode('ASCII', 'ignore').decode('ASCII')
    # Remove espaços extras e converte para minúsculas
    return texto.strip().lower()