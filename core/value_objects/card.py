from core.data_classes import DateHourGrid
from logging import getLogger


logger = getLogger(__name__)


class Card:
    def __init__(self, data, horario, dextro, lenta, rapida, exercicio, refeicao, observacao):
        logger.debug(f"Creating Card with data: {data}, horario: {horario}, dextro: {dextro}, lenta: {lenta}, rapida: {rapida}, exercicio: {exercicio}, refeicao: {refeicao}, observacao: {observacao}")
        
        self.data = data
        self.horario = horario
        self.dextro = dextro
        self.lenta = lenta
        self.rapida = rapida
        self.exercicio = exercicio
        self.refeicao = refeicao
        self.observacao = observacao


    @classmethod
    def from_dict(cls, data: dict) -> "Card":
        """Cria um card a partir de um dicionário."""
        logger.debug(f"Creating Card from dict: {data}")

        return cls(
            data=data.get("data", ""),
            horario=data.get("horario", ""),
            dextro=data.get("dextro", ""),
            lenta=data.get("lenta", ""),
            rapida=data.get("rapida", ""),
            exercicio=data.get("exercicio", ""),
            refeicao=data.get("refeicao", ""),
            observacao=data.get("observacao", "")
        )


    def to_dict(self):
        """Converte o card para um dicionário."""
        logger.debug(f"Converting Card to dict: {self.__dict__}")

        return {
            "data": self.data,
            "horario": self.horario,
            "dextro": self.dextro,
            "lenta": self.lenta,
            "rapida": self.rapida,
            "exercicio": self.exercicio,
            "refeicao": self.refeicao,
            "observacao": self.observacao
        }
