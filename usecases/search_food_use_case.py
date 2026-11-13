"""Use case de busca de alimentos da tabela TACO.

Puro e sem porta nova: recebe a lista de Foods já carregada pelo composition
root (mesmo padrão do GetMealListUseCase). Toda a regra de matching (sem
acento/pontuação, ranking por relevância) vive aqui; a fonte de dados fica
isolada no TacoRepository, na camada de adapters.
"""

import unicodedata
from logging import getLogger

from core.value_objects.food import Food
from usecases.dtos.food_search import FoodSearchResult

logger = getLogger(__name__)


def _normalize(text: str) -> str:
    """Normaliza texto para busca: minúsculas, sem acentos e sem pontuação,
    para que "macarrao" encontre "Macarrão, instantâneo" e "pao frances"
    encontre "Pão, francês" (a TACO usa vírgulas em toda a descrição).
    A string exibida ao usuário continua sendo a original do Food — a
    apresentação mostra o cru, busca no normalizado.
    """
    normalized = unicodedata.normalize("NFD", text.strip().lower())
    without_accents = "".join(char for char in normalized if not unicodedata.combining(char))
    # Pontuação vira espaço ("Pão, francês" -> "pao frances"), espaços colapsam
    cleaned = "".join(char if (char.isalnum() or char.isspace()) else " " for char in without_accents)
    return " ".join(cleaned.split())


def _match_rank(normalized_description: str, normalized_query: str) -> int | None:
    """Ranqueia a qualidade do match. Prefixo > início de palavra > contém."""
    if normalized_description.startswith(normalized_query):
        return 0
    if any(word.startswith(normalized_query) for word in normalized_description.split()):
        return 1
    if normalized_query in normalized_description:
        return 2
    return None


class SearchFoodUseCase:
    """Busca pura por alimentos da tabela TACO.

    Não depende de repositório nem porta: recebe a lista de Foods já carregada
    pelo composition root (mesmo padrão do GetMealListUseCase, que recebe os
    dados de onde estão). A fonte de dados fica isolada no TacoRepository
    (adapters); aqui só existe lógica de consulta, 100% testável sem arquivo.

    Query vazia devolve a TABELA COMPLETA em ordem alfabética — decisão de
    produto: o popup de busca abre navegável (mobile first, o usuário folheia
    antes de digitar) e a RecycleView na UI torna despejar 597 itens barato.
    Query preenchida mantém ranking por relevância com limite.
    """

    DEFAULT_LIMIT = 25

    def __init__(self, foods: list[Food]):
        # Pré-normaliza uma vez: cada consulta é uma varredura O(n) em memória
        # sobre 597 alimentos — barato o suficiente para o app offline.
        self._entries: list[tuple[str, str, Food]] = [
            (_normalize(food.description), _normalize(food.category), food) for food in foods
        ]

    def execute(self, query: str, category: str | None = None,
                limit: int = DEFAULT_LIMIT) -> FoodSearchResult:
        """Executa a busca. Query vazia devolve a tabela completa (ou a
        categoria filtrada) em ordem alfabética — o popup abre navegável.
        Query preenchida devolve os melhores matches por ranking (prefixo >
        início de palavra > contém), com empate resolvido alfabeticamente.
        """
        if not isinstance(query, str):
            raise TypeError(f"Invalid type for query: {type(query)}")

        if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
            raise ValueError(f"Invalid limit: {limit!r}")

        normalized_query = _normalize(query)
        normalized_category = _normalize(category) if isinstance(category, str) and category.strip() else None

        if not normalized_query:
            # Tabela inteira navegável (decisão de produto): filtra por categoria
            # quando houver, ordem alfabética — não há ranking sem termo.
            matches = [food
                       for _, food_category, food in self._entries
                       if normalized_category is None or food_category == normalized_category]
            matches.sort(key=lambda food: food.description)
            logger.debug(f"Food search empty query (category={category!r}): {len(matches)} foods")
            return FoodSearchResult(matches)

        ranked: list[tuple[int, str, Food]] = []
        for normalized_description, food_category, food in self._entries:
            if normalized_category is not None and food_category != normalized_category:
                continue

            rank = _match_rank(normalized_description, normalized_query)
            if rank is not None:
                ranked.append((rank, food.description, food))

        ranked.sort(key=lambda entry: (entry[0], entry[1]))

        logger.debug(f"Food search '{query}' (category={category!r}): {len(ranked)} matches")
        return FoodSearchResult([food for _, _, food in ranked[:limit]])
