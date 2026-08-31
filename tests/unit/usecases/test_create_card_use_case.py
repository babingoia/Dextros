# tests/unit/usecases/test_create_card_use_case.py

import uuid
from datetime import date

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from usecases.create_card_use_case import CreateCardUseCase
from usecases.dtos.cardDTOInput import CardDTOInput
from usecases.utils.exceptions import DomainExceptionError


# ---------------------------------------------------------------------------
# Constantes de domínio para strategies Hypothesis
# ---------------------------------------------------------------------------

VALID_MEALS = (
    "jejum",
    "pós café da manhã",
    "pré lanche da manhã",
    "pós lanche da manhã",
    "pré almoço",
    "pós almoço",
    "pré café da tarde",
    "pós café da tarde",
    "pré jantar",
    "pós jantar",
    "madrugada",
)

VALID_INTENSITIES = (
    "leve",
    "moderada",
    "vigorosa",
)

EXERCISE_NAMES = (
    "caminhada",
    "corrida",
    "musculação",
    "natação",
)


# ---------------------------------------------------------------------------
# Strategies Hypothesis
# ---------------------------------------------------------------------------

uuid_strategy = st.builds(uuid.uuid4)

card_id_strategy = st.one_of(
    st.none(),
    uuid_strategy.map(str),
    uuid_strategy.map(lambda value: value.int),
)

card_date_strategy = st.dates(
    min_value=date(2020, 1, 1),
    max_value=date.today(),
).map(lambda value: value.strftime("%Y-%m-%d"))

card_time_strategy = st.times().map(lambda value: value.strftime("%H:%M"))

glycemia_strategy = st.integers(min_value=20, max_value=600)

insulin_strategy = st.one_of(
    st.none(),
    st.integers(min_value=0, max_value=1000),
)

meal_strategy = st.one_of(
    st.none(),
    st.sampled_from(VALID_MEALS),
)

observation_strategy = st.one_of(
    st.none(),
    st.text(min_size=1, max_size=240),
)


@st.composite
def exercise_fields_strategy(draw):
    """
    Gera pares coerentes de exercise_name/exercise_intensity.

    Regra de domínio:
    - não pode haver intensidade sem nome de exercício.
    """
    has_exercise = draw(st.booleans())

    if not has_exercise:
        return None, None

    name = draw(st.sampled_from(EXERCISE_NAMES))
    intensity = draw(
        st.one_of(
            st.none(),
            st.sampled_from(VALID_INTENSITIES),
        )
    )

    return name, intensity


@st.composite
def valid_card_dto_strategy(draw):
    exercise_name, exercise_intensity = draw(exercise_fields_strategy())

    return CardDTOInput(
        card_id=draw(card_id_strategy),
        card_date=draw(card_date_strategy),
        card_time=draw(card_time_strategy),
        glycemia=draw(glycemia_strategy),
        long_acting_insulin=draw(insulin_strategy),
        short_acting_insulin=draw(insulin_strategy),
        meal=draw(meal_strategy),
        observation=draw(observation_strategy),
        exercise_name=exercise_name,
        exercise_intensity=exercise_intensity,
    )


# ---------------------------------------------------------------------------
# Configuração dos testes property-based
# ---------------------------------------------------------------------------

suppressed_health_checks = [HealthCheck.too_slow]

# Em versões mais recentes do Hypothesis, existe o health check de fixture
# function-scoped. Como estamos usando fixtures apenas como factories
# stateless, é seguro suprimir esse aviso.
if hasattr(HealthCheck, "function_scoped_fixture"):
    suppressed_health_checks.append(HealthCheck.function_scoped_fixture)

property_test = settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=suppressed_health_checks,
)


# ---------------------------------------------------------------------------
# Testes de construção
# ---------------------------------------------------------------------------

def test_init_assigns_dependencies(card_repository_mock, card_creator_mock):
    use_case = CreateCardUseCase(
        repository=card_repository_mock,
        card_creator=card_creator_mock,
    )

    assert use_case.repository is card_repository_mock
    assert use_case.card_creator is card_creator_mock


# ---------------------------------------------------------------------------
# Testes com cardDTO None
# ---------------------------------------------------------------------------

def test_execute_none_raises_domain_exception_error_with_exact_message(create_card_use_case):
    with pytest.raises(DomainExceptionError) as excinfo:
        create_card_use_case.execute(None)

    assert str(excinfo.value) == "Card creation failed, cardDTO is missing."


def test_execute_none_does_not_call_card_creator(create_card_use_case, card_creator_mock):
    with pytest.raises(DomainExceptionError):
        create_card_use_case.execute(None)

    card_creator_mock.create_card.assert_not_called()


def test_execute_none_does_not_use_repository(
    create_card_use_case,
    card_repository_mock,
    assert_repository_methods_not_called,
):
    with pytest.raises(DomainExceptionError):
        create_card_use_case.execute(None)

    card_repository_mock.add_card.assert_not_called()
    assert_repository_methods_not_called(card_repository_mock)


# ---------------------------------------------------------------------------
# Testes do caminho feliz
# ---------------------------------------------------------------------------

def test_execute_valid_dto_orchestrates_creator_and_repository(
    create_card_use_case,
    card_creator_mock,
    card_repository_mock,
    valid_card_dto,
    valid_card,
    assert_repository_methods_not_called,
):
    card_creator_mock.create_card.return_value = valid_card

    result = create_card_use_case.execute(valid_card_dto)

    card_creator_mock.create_card.assert_called_once_with(valid_card_dto)
    assert card_creator_mock.create_card.call_args.args[0] is valid_card_dto

    card_repository_mock.add_card.assert_called_once_with(valid_card)
    assert card_repository_mock.add_card.call_args.args[0] is valid_card

    assert result is valid_card

    assert_repository_methods_not_called(card_repository_mock)


def test_execute_valid_dto_calls_creator_before_repository(
    create_card_use_case,
    card_creator_mock,
    card_repository_mock,
    valid_card_dto,
    valid_card,
):
    calls: list[str] = []

    def create_side_effect(dto: CardDTOInput):
        calls.append("create_card")
        return valid_card

    def add_side_effect(card):
        calls.append("add_card")
        return None

    card_creator_mock.create_card.side_effect = create_side_effect
    card_repository_mock.add_card.side_effect = add_side_effect

    result = create_card_use_case.execute(valid_card_dto)

    assert calls == ["create_card", "add_card"]
    assert card_creator_mock.create_card.call_args.args[0] is valid_card_dto
    assert card_repository_mock.add_card.call_args.args[0] is valid_card
    assert result is valid_card


# ---------------------------------------------------------------------------
# Testes de propagação de exceção
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "exception_class",
    [
        ValueError,
        RuntimeError,
        DomainExceptionError,
    ],
)
def test_execute_when_card_creator_raises_propagates_and_repository_is_not_used(
    create_card_use_case,
    card_creator_mock,
    card_repository_mock,
    valid_card_dto,
    exception_class,
    assert_repository_methods_not_called,
):
    expected_exception = exception_class("boom")
    card_creator_mock.create_card.side_effect = expected_exception

    with pytest.raises(exception_class) as excinfo:
        create_card_use_case.execute(valid_card_dto)

    assert excinfo.value is expected_exception

    card_creator_mock.create_card.assert_called_once_with(valid_card_dto)
    assert card_creator_mock.create_card.call_args.args[0] is valid_card_dto

    card_repository_mock.add_card.assert_not_called()
    assert_repository_methods_not_called(card_repository_mock)


@pytest.mark.parametrize(
    "exception_class",
    [
        ValueError,
        RuntimeError,
        DomainExceptionError,
    ],
)
def test_execute_when_repository_add_raises_propagates(
    create_card_use_case,
    card_creator_mock,
    card_repository_mock,
    valid_card_dto,
    valid_card,
    exception_class,
    assert_repository_methods_not_called,
):
    card_creator_mock.create_card.return_value = valid_card

    expected_exception = exception_class("boom")
    card_repository_mock.add_card.side_effect = expected_exception

    with pytest.raises(exception_class) as excinfo:
        create_card_use_case.execute(valid_card_dto)

    assert excinfo.value is expected_exception

    card_creator_mock.create_card.assert_called_once_with(valid_card_dto)
    assert card_creator_mock.create_card.call_args.args[0] is valid_card_dto

    card_repository_mock.add_card.assert_called_once_with(valid_card)
    assert card_repository_mock.add_card.call_args.args[0] is valid_card

    assert_repository_methods_not_called(card_repository_mock)


# ---------------------------------------------------------------------------
# Testes com FakeCardRepository
# ---------------------------------------------------------------------------

def test_fake_repository_stores_created_card(
    fake_card_repository,
    card_creator_mock,
    valid_card_dto,
    valid_card,
):
    card_creator_mock.create_card.return_value = valid_card

    use_case = CreateCardUseCase(
        repository=fake_card_repository,
        card_creator=card_creator_mock,
    )

    result = use_case.execute(valid_card_dto)

    assert result is valid_card
    assert fake_card_repository.cards == [valid_card]

    card_creator_mock.create_card.assert_called_once_with(valid_card_dto)
    assert card_creator_mock.create_card.call_args.args[0] is valid_card_dto


def test_fake_repository_does_not_store_when_dto_is_none(
    fake_card_repository,
    card_creator_mock,
):
    use_case = CreateCardUseCase(
        repository=fake_card_repository,
        card_creator=card_creator_mock,
    )

    with pytest.raises(DomainExceptionError) as excinfo:
        use_case.execute(None)

    assert str(excinfo.value) == "Card creation failed, cardDTO is missing."
    assert fake_card_repository.cards == []
    card_creator_mock.create_card.assert_not_called()


def test_fake_repository_does_not_store_when_card_creator_fails(
    fake_card_repository,
    card_creator_mock,
    valid_card_dto,
):
    card_creator_mock.create_card.side_effect = RuntimeError("boom")

    use_case = CreateCardUseCase(
        repository=fake_card_repository,
        card_creator=card_creator_mock,
    )

    with pytest.raises(RuntimeError):
        use_case.execute(valid_card_dto)

    assert fake_card_repository.cards == []
    card_creator_mock.create_card.assert_called_once_with(valid_card_dto)
    assert card_creator_mock.create_card.call_args.args[0] is valid_card_dto


def test_fake_repository_does_not_store_when_add_fails(
    fake_card_repository,
    card_creator_mock,
    valid_card_dto,
    valid_card,
):
    card_creator_mock.create_card.return_value = valid_card
    fake_card_repository.fail_on_add = RuntimeError("boom")

    use_case = CreateCardUseCase(
        repository=fake_card_repository,
        card_creator=card_creator_mock,
    )

    with pytest.raises(RuntimeError):
        use_case.execute(valid_card_dto)

    assert fake_card_repository.cards == []
    card_creator_mock.create_card.assert_called_once_with(valid_card_dto)
    assert card_creator_mock.create_card.call_args.args[0] is valid_card_dto


# ---------------------------------------------------------------------------
# Testes property-based com Hypothesis
# ---------------------------------------------------------------------------

@property_test
@given(dto=valid_card_dto_strategy())
def test_property_execute_valid_dto_returns_and_persists_created_card(
    dto,
    mock_factory,
    card_factory,
    assert_repository_methods_not_called,
):
    repository, creator = mock_factory()
    card = card_factory()

    creator.create_card.return_value = card

    use_case = CreateCardUseCase(
        repository=repository,
        card_creator=creator,
    )

    result = use_case.execute(dto)

    creator.create_card.assert_called_once_with(dto)
    assert creator.create_card.call_args.args[0] is dto

    repository.add_card.assert_called_once_with(card)
    assert repository.add_card.call_args.args[0] is card

    assert result is card

    assert_repository_methods_not_called(repository)


@property_test
@given(
    dto=valid_card_dto_strategy(),
    exception_class=st.sampled_from(
        [
            ValueError,
            RuntimeError,
            DomainExceptionError,
        ]
    ),
)
def test_property_creator_exception_prevents_repository_use(
    dto,
    exception_class,
    mock_factory,
    assert_repository_methods_not_called,
):
    repository, creator = mock_factory()

    expected_exception = exception_class("boom")
    creator.create_card.side_effect = expected_exception

    use_case = CreateCardUseCase(
        repository=repository,
        card_creator=creator,
    )

    with pytest.raises(exception_class) as excinfo:
        use_case.execute(dto)

    assert excinfo.value is expected_exception

    creator.create_card.assert_called_once_with(dto)
    assert creator.create_card.call_args.args[0] is dto

    repository.add_card.assert_not_called()
    assert_repository_methods_not_called(repository)


@property_test
@given(
    dto=valid_card_dto_strategy(),
    exception_class=st.sampled_from(
        [
            ValueError,
            RuntimeError,
            DomainExceptionError,
        ]
    ),
)
def test_property_repository_exception_propagates_after_card_creation(
    dto,
    exception_class,
    mock_factory,
    card_factory,
    assert_repository_methods_not_called,
):
    repository, creator = mock_factory()
    card = card_factory()

    creator.create_card.return_value = card

    expected_exception = exception_class("boom")
    repository.add_card.side_effect = expected_exception

    use_case = CreateCardUseCase(
        repository=repository,
        card_creator=creator,
    )

    with pytest.raises(exception_class) as excinfo:
        use_case.execute(dto)

    assert excinfo.value is expected_exception

    creator.create_card.assert_called_once_with(dto)
    assert creator.create_card.call_args.args[0] is dto

    repository.add_card.assert_called_once_with(card)
    assert repository.add_card.call_args.args[0] is card

    assert_repository_methods_not_called(repository)