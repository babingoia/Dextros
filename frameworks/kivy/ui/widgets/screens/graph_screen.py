from kivy.uix.screenmanager import Screen
from logging import getLogger

logger = getLogger(__name__)

class GraphScreen(Screen):
    """
    Uma Screen especializada que executa um callback de atualização 
    sempre que o usuário navega para ela (Lazy Load).
    """
    def __init__(self, refresh_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.refresh_callback = refresh_callback

    def on_pre_enter(self, *args):
        """
        on_pre_enter é disparado ANTES da transição de tela terminar.
        É o momento ideal para buscar dados, dando a sensação de 
        carregamento instantâneo quando a tela aparece.
        """
        logger.info(f"🔄 on_pre_enter DISPARADO para: {self.name}")
        super().on_pre_enter(*args)
        logger.info(f"🔍 refresh_callback atual: {self.refresh_callback}")

        if self.refresh_callback:
            logger.info(f"⚡ Executando lazy load para: {self.name}")
            self.refresh_callback()
        else:
            logger.warning(f"⚠️ refresh_callback é None na tela {self.name}!")