from core.DataClasses import DateHourGrid


class Card:
    def __init__(self, data, horario, dextro, lenta, rapida, exercicio, refeicao, observacao):
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


    @staticmethod
    def organize_cards(cards: list["Card"]) -> DateHourGrid:
        """Organiza os cards por data e horário. Retorna um DateHourGrid
          com um mapa de data para horário e uma lista de datas únicas."""
        
        date_map: dict[str, dict[str, Card]] = {}
        unique_dates: list[str] = []

        cards = Card.order_by_date(cards)

        for card in cards:
            if card.data not in date_map:
                date_map[card.data] = {}
                unique_dates.append(card.data)

            date_map[card.data][card.horario] = card

        return DateHourGrid(date_map=date_map, unique_dates=unique_dates)


    @staticmethod
    def order_by_date(cards: list["Card"]) -> list["Card"]:
        """Ordena os cards por data."""
        return sorted(cards, key=lambda card: card.data)


    @staticmethod
    def order_by_horario(cards: list["Card"]) -> list["Card"]:
        """Ordena os cards por horário."""
        return sorted(cards, key=lambda card: card.horario)


    @staticmethod
    def order_by_date_and_horario(cards: list["Card"]) -> list["Card"]:
        """Ordena os cards por data e horário."""
        return sorted(cards, key=lambda card: (card.data, card.horario))