# tests/unit/usecases/test_delete_card_by_id_use_case.py

import uuid

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from usecases.delete_card_by_id_use_case import DeleteCardByIDUseCase
from usecases.utils.exceptions import DomainExceptionError


# ---------------------------------------------------------------------------
# Exceção customizada apenas para testes
# ---------------------------------------------------------------------------

class RepositoryStubError(Exception):
    """
    Exceção genérica para simular erros de repositório sem importar
    exceções reais de adapters.
    """
    pass


# ---------------------------------------------------------------------------
# Strategies Hypothesis
# ---------------------------------------------------------------------------

uuid_strategy = st.builds(uuid.uuid4)

# CardID aceita UUID v4 string, UUID v4 int e None.
# Empty string não entra aqui porque não é um CardID válido.
card_id_strategy = st.one_of(
    st.none(),
    uuid_strategy.map(str),
    uuid_strategy.map(lambda value: value.int),
)

exception_class_strategy = st.sampled_from(
    [
        ValueError,
        RuntimeError,
        KeyError,
        Exception,
        RepositoryStubError,
    ]
)


# ---------------------------------------------------------------------------
# Configuração dos testes property-based
# ---------------------------------------------------------------------------

suppressed_health_checks = [HealthCheck.too_slow]

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

def test_init_assigns_repository(card_repository_mock):
    use_case = DeleteCardByIDUseCase(card_repository_mock)

    assert use_case.repository is card_repository_mock


# ---------------------------------------------------------------------------
# Caminho feliz
# ---------------------------------------------------------------------------

def test_execute_calls_remove_card_once_and_returns_none(
    delete_card_use_case,
    card_repository_mock,
    valid_card_id,
    assert_repository_methods_not_called_except,
):
    result = delete_card_use_case.execute(valid_card_id)

    assert result is None

    card_repository_mock.remove_card.assert_called_once_with(valid_card_id)

    assert_repository_methods_not_called_except(
        card_repository_mock,
        allowed={"remove_card"},
    )


# ---------------------------------------------------------------------------
# Ausência de validação no use case
# ---------------------------------------------------------------------------

def test_execute_does_not_validate_empty_card_id(
    delete_card_use_case,
    card_repository_mock,
    assert_repository_methods_not_called_except,
):
    result = delete_card_use_case.execute("")

    assert result is None

    card_repository_mock.remove_card.assert_called_once_with("")

    assert_repository_methods_not_called_except(
        card_repository_mock,
        allowed={"remove_card"},
    )


def test_execute_does_not_validate_none_card_id(
    delete_card_use_case,
    card_repository_mock,
    assert_repository_methods_not_called_except,
):
    result = delete_card_use_case.execute(None)

    assert result is None

    card_repository_mock.remove_card.assert_called_once_with(None)

    assert_repository_methods_not_called_except(
        card_repository_mock,
        allowed={"remove_card"},
    )


def test_execute_does_not_validate_numeric_card_id(
    delete_card_use_case,
    card_repository_mock,
    assert_repository_methods_not_called_except,
):
    numeric_card_id = uuid.uuid4().int

    result = delete_card_use_case.execute(numeric_card_id)

    assert result is None

    card_repository_mock.remove_card.assert_called_once_with(numeric_card_id)

    assert_repository_methods_not_called_except(
        card_repository_mock,
        allowed={"remove_card"},
    )


# ---------------------------------------------------------------------------
# Wrapping de exceções preservando causa
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "exception_class",
    [
        ValueError,
        RuntimeError,
        KeyError,
        Exception,
        RepositoryStubError,
    ],
)
def test_execute_repository_exception_is_wrapped_into_domain_exception_error_preserving_cause(
    delete_card_use_case,
    card_repository_mock,
    valid_card_id,
    exception_class,
    assert_repository_methods_not_called_except,
):
    original_exception = exception_class("boom")
    card_repository_mock.remove_card.side_effect = original_exception

    with pytest.raises(DomainExceptionError) as excinfo:
        delete_card_use_case.execute(valid_card_id)

    assert isinstance(excinfo.value, DomainExceptionError)

    # Comportamento desejado:
    # raise DomainExceptionError(err) from err
    assert excinfo.value.__cause__ is original_exception

    card_repository_mock.remove_card.assert_called_once_with(valid_card_id)

    assert_repository_methods_not_called_except(
        card_repository_mock,
        allowed={"remove_card"},
    )


# ---------------------------------------------------------------------------
# Testes com FakeCardRepository
# ---------------------------------------------------------------------------

def test_fake_repository_removes_existing_card(
    fake_card_repository,
    card_with_id_factory,
    valid_card_id,
):
    card = card_with_id_factory(valid_card_id)
    fake_card_repository.cards.append(card)

    use_case = DeleteCardByIDUseCase(fake_card_repository)

    result = use_case.execute(valid_card_id)

    assert result is None
    assert card not in fake_card_repository.cards


def test_fake_repository_removes_only_target_card(
    fake_card_repository,
    card_with_id_factory,
):
    first_card_id = str(uuid.uuid4())
    second_card_id = str(uuid.uuid4())

    first_card = card_with_id_factory(first_card_id)
    second_card = card_with_id_factory(second_card_id)

    fake_card_repository.cards.extend([first_card, second_card])

    use_case = DeleteCardByIDUseCase(fake_card_repository)

    use_case.execute(first_card_id)

    assert first_card not in fake_card_repository.cards
    assert second_card in fake_card_repository.cards


def test_fake_repository_remove_failure_is_wrapped_preserving_cause(
    fake_card_repository,
    card_with_id_factory,
    valid_card_id,
):
    card = card_with_id_factory(valid_card_id)
    fake_card_repository.cards.append(card)

    original_exception = RuntimeError("boom")
    fake_card_repository.fail_on_remove = original_exception

    use_case = DeleteCardByIDUseCase(fake_card_repository)

    with pytest.raises(DomainExceptionError) as excinfo:
        use_case.execute(valid_card_id)

    assert isinstance(excinfo.value, DomainExceptionError)
    assert excinfo.value.__cause__ is original_exception

    assert card in fake_card_repository.cards


def test_fake_repository_strict_remove_missing_card_is_wrapped_preserving_cause(
    fake_card_repository,
    valid_card_id,
):
    fake_card_repository.strict_remove = True

    use_case = DeleteCardByIDUseCase(fake_card_repository)

    with pytest.raises(DomainExceptionError) as excinfo:
        use_case.execute(valid_card_id)

    assert isinstance(excinfo.value, DomainExceptionError)
    assert isinstance(excinfo.value.__cause__, KeyError)

    assert fake_card_repository.cards == []


# ---------------------------------------------------------------------------
# Testes property-based
# ---------------------------------------------------------------------------

@property_test
@given(card_id=card_id_strategy)
def test_property_success_calls_remove_card_once_and_no_other_repository_methods(
    card_id,
    card_repository_mock_factory,
    assert_repository_methods_not_called_except,
):
    repository = card_repository_mock_factory()

    use_case = DeleteCardByIDUseCase(repository)

    result = use_case.execute(card_id)

    assert result is None

    repository.remove_card.assert_called_once_with(card_id)

    assert_repository_methods_not_called_except(
        repository,
        allowed={"remove_card"},
    )


@property_test
@given(
    card_id=card_id_strategy,
    exception_class=exception_class_strategy,
)
def test_property_repository_exception_is_wrapped_preserving_cause(
    card_id,
    exception_class,
    card_repository_mock_factory,
    assert_repository_methods_not_called_except,
):
    repository = card_repository_mock_factory()

    original_exception = exception_class("boom")
    repository.remove_card.side_effect = original_exception

    use_case = DeleteCardByIDUseCase(repository)

    with pytest.raises(DomainExceptionError) as excinfo:
        use_case.execute(card_id)

    assert isinstance(excinfo.value, DomainExceptionError)
    assert excinfo.value.__cause__ is original_exception

    repository.remove_card.assert_called_once_with(card_id)

    assert_repository_methods_not_called_except(
        repository,
        allowed={"remove_card"},
    )