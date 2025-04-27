import unicodedata

def normalizar_nome(texto):
    """Normaliza nomes removendo acentos, espaços extras e convertendo para maiúsculas"""
    if not texto:
        return ""
    # Remove acentos
    texto = unicodedata.normalize('NFKD', str(texto))
    texto = texto.encode('ASCII', 'ignore').decode('ASCII')
    # Remove espaços extras e converte para Title Case
    return ' '.join(texto.strip().title().split())