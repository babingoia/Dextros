import os
os.environ["KIVY_LOG_MODE"] = "MIXED" # Precisa vir antes de qualquer import do kivy

from kivymd.app import MDApp


from infrastructure.json_handler_service import JsonHandler
from presentation.kivy.controllers.main_controller import MainController
from presentation.kivy.controllers.session_controller import SessionController
from infrastructure import log_service


# Infrastructure Initial Load
log_service.configure_logging(console_level=log_service.logging.DEBUG)
logger = log_service.get_logger(__name__)
DB = "cards_populated.json"  
# "cards_populated.json" para fins de teste de performance
# "cards.json" mais leve

class DextroApp(MDApp):
    def build(self):
        
        logs_dir = os.path.join(self.user_data_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)

        log_service.add_file_handler(logs_dir, level=log_service.logging.DEBUG)
        save_path = os.path.join(self.user_data_dir, DB)
        logger.info(f"Save path set to: {save_path}")

        handler = JsonHandler(save_path=save_path)
        logger.info(f"JsonHandler initialized with save path: {handler.save_path}")

        SessionController(json_handler=handler)
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
