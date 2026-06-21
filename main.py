import os

# 1. A REGRA DE OURO: Define o modo de log oficial ANTES do Kivy ser importado.
# O modo "PYTHON" diz pro Kivy: "Abaixe as armas, use o logging padrão do Python".
os.environ["KIVY_LOG_MODE"] = "MIXED"

from kivymd.app import MDApp


from infrastructure.json_handler import JsonHandler
from presentation.kivy.controllers.main_controller import MainController
from presentation.kivy.controllers.session_cache import SessionCache
from infrastructure import log_config


# Configure root logger (colored console). File handler is added in on_start.
log_config.configure_logging(console_level=log_config.logging.DEBUG)
logger = log_config.get_logger(__name__)


class DextroApp(MDApp):
    def build(self):
        
        logs_dir = os.path.join(self.user_data_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)

        log_config.add_file_handler(logs_dir, level=log_config.logging.DEBUG)
        save_path = os.path.join(self.user_data_dir, "cards.json")
        logger.info(f"Save path set to: {save_path}")

        handler = JsonHandler(save_path=save_path)
        logger.info(f"JsonHandler initialized with save path: {handler.save_path}")

        SessionCache(json_handler=handler)
        logger.info("SessionCache initialized with JsonHandler")

        self.controller = MainController()
        logger.info("MainController initialized")

        return self.controller.main_view

    def on_start(self):
        logger.info("Starting App...")

    def on_stop(self):
        logger.info("App closed.")


if __name__ == "__main__":
    DextroApp().run()
