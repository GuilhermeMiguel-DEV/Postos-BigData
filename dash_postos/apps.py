from django.apps import AppConfig

class DashPostosConfig(AppConfig):
    """
    Configuração do aplicativo Dash Postos.
    Define metadados e configurações básicas do aplicativo Django.
    """
    
    # Usa BigAutoField como padrão para IDs automáticos
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Nome do aplicativo (deve corresponder ao nome do pacote)
    name = 'dash_postos'