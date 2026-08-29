import os
os.environ["KIVY_LOG_MODE"] = "MIXED"

from kivymd.app import MDApp
from infrastructure import log_service
import shutil

# Infrastructure
from frameworks.json_handler_service import JsonHandler
from adapters.repositories.jsonRepo import JsonRepository
from adapters.parsers.card_data_model_parser import CardDataModelParser
from infrastructure.path_provider_service import get_data_path, get_asset_path

# Use Cases
from usecases.Factories.card_creator import CardCreator
from usecases.get_time_list_use_case import GetTimeListUseCase
from usecases.get_hour_date_matrix_data import GetHourDateMatrixUseCase
from usecases.get_meal_list_use_case import GetMealListUseCase
from usecases.create_card_use_case import CreateCardUseCase

# Controllers (adapters)
from adapters.controllers.time_controller import TimeController
from adapters.controllers.date_hour_matrix_controller import DateHourMatrixController
from adapters.controllers.meal_controller import MealController
from adapters.controllers.save_request_controller import SaveRequestController

# Gateway
from adapters.gateways.kivy_router import KivyRouter

# Kivy
from frameworks.kivy.controllers.main_controller import MainController

log_service.configure_logging(console_level=log_service.logging.DEBUG)
logger = log_service.get_logger(__name__)

DB = "db/cards_v2.json"


class DextroApp(MDApp):
    def build(self):

        db_path = get_data_path(DB)

        if not os.path.exists(db_path):
            seed = get_asset_path(DB)
            if os.path.exists(seed):
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
                shutil.copyfile(seed, db_path)
                logger.info("Seed database copied to %s", db_path)
                logs_dir = os.path.join(self.user_data_dir, "logs")
                os.makedirs(logs_dir, exist_ok=True)
                log_service.add_file_handler(logs_dir, level=log_service.logging.DEBUG)

        # ✅ Usa o get_data_path em vez de user_data_dir
        db_path = get_data_path(DB)
        logger.info(f"Save path set to: {db_path}")

        # 1. Infraestrutura
        json_handler = JsonHandler(save_path=db_path)
        parser = CardDataModelParser()
        card_creator = CardCreator()
        card_repository = JsonRepository(
            handler=json_handler,
            parser=parser,
            card_creator=card_creator,
        )

        # 2. Use Cases (repo injetado)
        get_time_list_uc = GetTimeListUseCase()
        get_matrix_uc = GetHourDateMatrixUseCase(card_repository)
        get_meal_list_uc = GetMealListUseCase()
        create_card_uc = CreateCardUseCase(card_repository, card_creator)

        # 3. Controllers (use cases injetados)
        time_controller = TimeController(get_time_list_uc)
        matrix_controller = DateHourMatrixController(get_matrix_uc)
        meal_controller = MealController(get_meal_list_uc)
        save_request_controller = SaveRequestController(create_card_uc)

        # 4. Router (controllers injetados)
        router = KivyRouter(
            time_controller=time_controller,
            date_hour_matrix_controller=matrix_controller,
            meal_controller=meal_controller,
            save_request_controller=save_request_controller
        )

        # 5. Kivy (router injetado)
        self.controller = MainController(router=router)
        logger.info("Composition root complete.")

        return self.controller.main_view

    def on_start(self):
        logger.info("Starting App...")

    def on_stop(self):
        logger.info("App closed.")


if __name__ == "__main__":
    DextroApp().run()