from abc import ABC, abstractmethod
from typing import Generic, TypeVar

RequestDTO = TypeVar('RequestDTO')
ResponseDTO = TypeVar('ResponseDTO')

class IController(ABC, Generic[RequestDTO, ResponseDTO]):
    """Contrato abstrado de um controller em forma de comando. Recebe uma request tipada que depende
    do controlador e uma resposta também dependente. Geralmente é divido entre requests que retornam
    um valor de DTO dos controllers para a UI consumir e queries que são processadas sem retornar nada.
    """
    @abstractmethod
    def execute(self, request: RequestDTO) -> ResponseDTO:
        pass