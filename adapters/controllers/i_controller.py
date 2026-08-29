from abc import ABC, abstractmethod
from typing import Generic, TypeVar

RequestDTO = TypeVar('RequestDTO')
ResponseDTO = TypeVar('ResponseDTO')

class IController(ABC, Generic[RequestDTO, ResponseDTO]):
    @abstractmethod
    def execute(self, request: RequestDTO) -> ResponseDTO:
        pass