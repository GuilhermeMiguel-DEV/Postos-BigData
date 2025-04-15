import unicodedata

def normalizar_texto(texto):
    if not texto:
        return ""
    # Remove acentos e caracteres especiais
    texto = unicodedata.normalize('NFKD', str(texto))
    texto = texto.encode('ASCII', 'ignore').decode('ASCII')
    # Remove espaços extras e converte para minúsculas
    return texto.strip().lower()