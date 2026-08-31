import pytest
import uuid
from typing import Any, Callable

import pytest
from unittest.mock import create_autospec


from usecases.IRepository import ICardRepository
from usecases.Factories.I_card_creator import ICardCreator
from usecases.dtos.cardDTOInput import CardDTOInput
from usecases.create_card_use_case import CreateCardUseCase
from usecases.delete_card_by_id_use_case import DeleteCardByIDUseCase
from usecases.get_matrix_data.base_column_matrix_template import BaseColumnMatrixTemplate

from core.value_objects.card_id import CardID
from core.value_objects.date import Date
from core.value_objects.time import Time
from core.value_objects.glycemia import Glycemia
from core.value_objects.long_acting_insulin import LongActingInsulin
from core.value_objects.short_acting_insulin import ShortActingInsulin
from core.value_objects.exercise import Exercise
from core.value_objects.meal import MealPeriod
from core.value_objects.observation import Observation
from core.value_objects.card import Card


def make_card(**overrides) -> Card:
    """Fábrica de Card válido, com todos os campos usando valores padrão
    sensatos. Passe overrides pra sobrescrever campos específicos no teste."""
    defaults = dict(
        card_id=CardID.parse(),
        card_date=Date.parse("2024-05-20"),
        card_time=Time.parse("08:00"),
        glycemia=Glycemia.parse(100),
        long_acting_insulin=LongActingInsulin.parse(10),
        short_acting_insulin=ShortActingInsulin.parse(4),
        exercise=Exercise.parse(),
        meal=MealPeriod.parse("jejum"),
        obs=Observation.parse(),
    )
    defaults.update(overrides)
    return Card(**defaults)


@pytest.fixture
def valid_card_kwargs():
    return dict(
        card_id=CardID.parse(),
        card_date=Date.parse("2024-05-20"),
        card_time=Time.parse("08:00"),
        glycemia=Glycemia.parse(100),
        long_acting_insulin=LongActingInsulin.parse(10),
        short_acting_insulin=ShortActingInsulin.parse(4),
        exercise=Exercise.parse(),
        meal=MealPeriod.parse("jejum"),
        obs=Observation.parse(),
    )


def make_card_dto(**overrides: Any) -> CardDTOInput:
    """
    Fábrica de CardDTOInput válido para testes.

    IMPORTANTE:
    - O CreateCardUseCase não valida o conteúdo do DTO além de `None`.
    - Quem valida/transforma o DTO em Card é o ICardCreator.
    - Aqui usamos valores razoáveis para o domínio.
    """
    defaults: dict[str, Any] = {
        "card_id": str(uuid.uuid4()),
        "card_date": "2024-05-20",
        "card_time": "08:00",
        "glycemia": 100,
        "long_acting_insulin": 10,
        "short_acting_insulin": 4,
        "meal": "jejum",
        "observation": None,
        "exercise_name": None,
        "exercise_intensity": None,
    }

    defaults.update(overrides)

    # CardDTOInput possui `exercise` como field(init=False), então não pode
    # ser passado diretamente no construtor.
    defaults.pop("exercise", None)

    return CardDTOInput(**defaults)


def build_card_repository_mock():
    """
    Cria mock do ICardRepository com spec_set.

    spec_set é importante para impedir acesso a métodos/atributos fora da
    interface.
    """
    return create_autospec(ICardRepository, instance=True, spec_set=True)


def build_card_creator_mock():
    """
    Cria mock do ICardCreator com spec_set.
    """
    return create_autospec(ICardCreator, instance=True, spec_set=True)


def build_create_card_use_case(repository=None, card_creator=None):
    """
    Fábrica de CreateCardUseCase para testes.

    Se repository/card_creator não forem informados, cria mocks novos.
    """
    repository = repository or build_card_repository_mock()
    card_creator = card_creator or build_card_creator_mock()

    return CreateCardUseCase(
        repository=repository,
        card_creator=card_creator,
    )


class FakeCardRepository(ICardRepository):
    """
    Fake simples de ICardRepository para testes mais legíveis.

    Ele não tenta reproduzir todas as regras do JsonRepository real.
    O foco aqui é testar a orquestração do CreateCardUseCase.
    """

    def __init__(self) -> None:
        self.cards: list[Card] = []
        self.fail_on_add: Exception | None = None

    def get_all_cards(self) -> list[Card]:
        return list(self.cards)

    def get_card(self, card_id: str) -> Card:
        for card in self.cards:
            if card.card_id == card_id:
                return card

        raise KeyError(card_id)

    def add_card(self, card: Card) -> None:
        if self.fail_on_add is not None:
            raise self.fail_on_add

        self.cards.append(card)

    def remove_card(self, card_id: str) -> None:
        self.cards = [card for card in self.cards if card.card_id != card_id]

    def update_card(self, card: Card) -> None:
        self.remove_card(card.card_id)
        self.add_card(card)


@pytest.fixture
def card_repository_mock():
    return build_card_repository_mock()


@pytest.fixture
def card_creator_mock():
    return build_card_creator_mock()


@pytest.fixture
def create_card_use_case(card_repository_mock, card_creator_mock):
    return build_create_card_use_case(
        repository=card_repository_mock,
        card_creator=card_creator_mock,
    )


@pytest.fixture
def mock_factory() -> Callable[[], tuple[Any, Any]]:
    """
    Factory para criar mocks novos por exemplo.

    Isso é útil em testes Hypothesis, onde não é bom reutilizar mocks com
    estado acumulado entre exemplos.
    """

    def _make():
        return build_card_repository_mock(), build_card_creator_mock()

    return _make


@pytest.fixture
def use_case_factory() -> Callable[..., CreateCardUseCase]:
    def _make(repository=None, card_creator=None):
        return build_create_card_use_case(
            repository=repository,
            card_creator=card_creator,
        )

    return _make


@pytest.fixture
def valid_card() -> Card:
    """
    Retorna um Card válido usando a fábrica make_card existente.
    """
    return make_card()


@pytest.fixture
def card_factory() -> Callable[..., Card]:
    """
    Permite criar novos Cards dentro de testes Hypothesis.
    """
    return make_card


@pytest.fixture
def valid_card_dto() -> CardDTOInput:
    return make_card_dto()


@pytest.fixture
def card_dto_factory() -> Callable[..., CardDTOInput]:
    return make_card_dto


@pytest.fixture
def fake_card_repository() -> FakeCardRepository:
    return FakeCardRepository()


@pytest.fixture
def assert_repository_methods_not_called() -> Callable[[Any], None]:
    """
    Helper para garantir que métodos de leitura/escrita não relacionados
    do repositório não sejam chamados.

    Observação:
    - Ele não verifica add_card de propósito.
    - add_card é verificado separadamente em cada teste.
    """

    def _assert(repository) -> None:
        repository.get_all_cards.assert_not_called()
        repository.get_card.assert_not_called()
        repository.remove_card.assert_not_called()
        repository.update_card.assert_not_called()

    return _assert


def make_card_id() -> str:
    """
    Gera um card_id UUID v4 válido em formato string.
    """
    return str(uuid.uuid4())


def make_card_with_id(card_id: Any) -> Card:
    """
    Cria um Card válido com um CardID conhecido.

    Útil para testes de delete em fake repositories.
    """
    return make_card(card_id=CardID.parse(card_id))


class FakeCardRepository(ICardRepository):
    """
    Fake retrocompatível do ICardRepository.

    Mantém o comportamento anterior para create, mas adiciona controles
    específicos para testes de delete:

    - fail_on_remove: força exceção em remove_card;
    - strict_remove: lança KeyError se o card não existir.
    """

    def __init__(self) -> None:
        self.cards: list[Card] = []
        self.fail_on_add: Exception | None = None
        self.fail_on_remove: Exception | None = None
        self.strict_remove: bool = False

    def get_all_cards(self) -> list[Card]:
        return list(self.cards)

    def get_card(self, card_id: str) -> Card:
        for card in self.cards:
            if card.card_id == card_id:
                return card

        raise KeyError(card_id)

    def add_card(self, card: Card) -> None:
        if self.fail_on_add is not None:
            raise self.fail_on_add

        self.cards.append(card)

    def remove_card(self, card_id: str) -> None:
        if self.fail_on_remove is not None:
            raise self.fail_on_remove

        if self.strict_remove and not self._has_card(card_id):
            raise KeyError(card_id)

        self.cards = [card for card in self.cards if card.card_id != card_id]

    def update_card(self, card: Card) -> None:
        self.remove_card(card.card_id)
        self.add_card(card)

    def _has_card(self, card_id: Any) -> bool:
        return any(card.card_id == card_id for card in self.cards)


@pytest.fixture
def fake_card_repository() -> FakeCardRepository:
    return FakeCardRepository()


@pytest.fixture
def valid_card_id() -> str:
    return make_card_id()


@pytest.fixture
def card_id_factory() -> Callable[[], str]:
    return make_card_id


@pytest.fixture
def card_with_id_factory() -> Callable[[Any], Card]:
    return make_card_with_id


@pytest.fixture
def delete_card_use_case(card_repository_mock):
    return DeleteCardByIDUseCase(card_repository_mock)


@pytest.fixture
def card_repository_mock_factory():
    """
    Factory para criar mocks novos do repositório.

    Importante para testes Hypothesis, evitando reutilizar mocks com estado
    acumulado entre exemplos.
    """
    return build_card_repository_mock


@pytest.fixture
def assert_repository_methods_not_called_except():
    """
    Helper genérico para garantir que métodos não usados do repositório
    não sejam chamados.

    Uso:

        assert_repository_methods_not_called_except(
            repository,
            allowed={"remove_card"},
        )
    """

    def _assert(repository, allowed: set[str]) -> None:
        all_methods = {
            "get_all_cards",
            "get_card",
            "add_card",
            "remove_card",
            "update_card",
        }

        for method_name in all_methods - allowed:
            getattr(repository, method_name).assert_not_called()

    return _assert


def build_card_repository_mock():
    """
    Cria mock do ICardRepository com spec_set.
    """
    return create_autospec(ICardRepository, instance=True, spec_set=True)


@pytest.fixture
def card_repository_mock():
    return build_card_repository_mock()


@pytest.fixture
def card_repository_mock_factory():
    """
    Factory para criar mocks novos do repositório.

    Útil para testes Hypothesis, evitando reutilizar mocks com estado
    acumulado entre exemplos.
    """
    return build_card_repository_mock


@pytest.fixture
def valid_card() -> Card:
    """
    Retorna um Card válido usando a fábrica make_card existente.
    """
    return make_card()


@pytest.fixture
def card_factory():
    """
    Permite criar novos Cards dentro de testes Hypothesis.
    """
    return make_card


@pytest.fixture
def base_column_matrix_template(card_repository_mock):
    return BaseColumnMatrixTemplate(card_repository_mock)


@pytest.fixture
def base_column_matrix_template_factory(card_repository_mock_factory):
    def _make(repository=None):
        return BaseColumnMatrixTemplate(
            repository=repository or card_repository_mock_factory()
        )

    return _make


@pytest.fixture
def assert_repository_methods_not_called_except():
    """
    Helper genérico para garantir que métodos não usados do repositório
    não sejam chamados.

    Uso:

        assert_repository_methods_not_called_except(
            repository,
            allowed={"get_all_cards"},
        )
    """

    def _assert(repository, allowed: set[str]) -> None:
        all_methods = {
            "get_all_cards",
            "get_card",
            "add_card",
            "remove_card",
            "update_card",
        }

        for method_name in all_methods - allowed:
            getattr(repository, method_name).assert_not_called()

    return _assert

# ---------------------------------------------------------------------------
# Helpers novos para Base2DMatrixTemplate
# ---------------------------------------------------------------------------

def build_card_repository_mock():
    """
    Cria mock do ICardRepository com spec_set.
    """
    return create_autospec(ICardRepository, instance=True, spec_set=True)


@pytest.fixture
def card_repository_mock_factory():
    """
    Factory para criar mocks novos do repositório.

    Útil para testes Hypothesis, evitando reutilizar mocks com estado
    acumulado entre exemplos.
    """
    return build_card_repository_mock


def make_card_with_date(card_date: str) -> Card:
    """
    Cria um Card válido com uma data específica.
    """
    return make_card(card_date=Date.parse(card_date))


def make_card_with_date_and_time(card_date: str, card_time: str) -> Card:
    """
    Cria um Card válido com data e hora específicas.
    """
    return make_card(
        card_date=Date.parse(card_date),
        card_time=Time.parse(card_time),
    )


@pytest.fixture
def card_with_date_factory() -> Callable[[str], Card]:
    return make_card_with_date


@pytest.fixture
def card_with_date_and_time_factory() -> Callable[[str, str], Card]:
    return make_card_with_date_and_time


@pytest.fixture
def repository_with_cards(card_repository_mock_factory):
    """
    Cria um repositório mock cujo get_all_cards retorna a lista de cards
    informada.
    """

    def _make(cards):
        repository = card_repository_mock_factory()
        repository.get_all_cards.return_value = cards
        return repository

    return _make