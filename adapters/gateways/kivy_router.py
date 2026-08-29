from logging import getLogger
from typing import Dict, Any
from adapters.exceptions import RouteError
from adapters.gateways.i_router import IRouter
from adapters.controllers.i_controller import IController

logger = getLogger(__name__)

class KivyRouter(IRouter):
    def __init__(self, controllers: Dict[str, IController]):
        self._controllers = controllers

    def navigate(self, route: str, request_data: Any = None) -> Any:
        controller = self._controllers.get(route)
        
        if not controller:
            raise RouteError(f"Route '{route}' not found")

        return controller.execute(request_data)