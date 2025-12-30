"""
Configuración de la app Django: Lite Thinking Domain
"""
from django.apps import AppConfig


class LiteThinkingDomainConfig(AppConfig):
    """
    Configuración de la aplicación Core de Dominio
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lite_thinking_domain'
    verbose_name = 'Lite Thinking - Core de Dominio'
    
    def ready(self):
        """
        Código que se ejecuta cuando la app está lista
        Aquí se pueden importar signals si los hubiera
        """
        pass
