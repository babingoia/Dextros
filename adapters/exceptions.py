class CardNotFoundError(Exception):
    pass

class InvalidCardFormat(Exception):
    pass


class FoodDataError(Exception):
    """Erro ao carregar/parsear dados de alimentos da tabela TACO."""


class RouteError(Exception):
    pass