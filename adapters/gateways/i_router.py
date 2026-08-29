from abc import ABC, abstractmethod
from typing import Any


class IRouter(ABC):
    """
    Interface para roteamento de navegação e ações da UI.
    Permite mockar o router em testes unitários da UI.
    """

    @abstractmethod
    def navigate(self, route: str, request_data: Any = None) -> Any:
        """
        Navega para uma rota ou executa uma ação.

        Args:
            route: String identificando a rota/ação (ex: "get_time_list", "save_card")
            data: Dados opcionais para passar para a rota

        Returns:
            Qualquer retorno da operação, se houver
        """
        pass
