# tests/unit/usecases/get_matrix_data/test_base_column_matrix_template.py

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from usecases.get_matrix_data.base_column_matrix_template import BaseColumnMatrixTemplate
from usecases.utils.exceptions import DuplicatedColumnError

# ---------------------------------------------------------------------------
# Strategies Hypothesis
# ---------------------------------------------------------------------------

label_strategy = st.text(max_size=12)
key_strategy = st.text(min_size=1, max_size=12)

unique_column_strategy = st.tuples(label_strategy, key_strategy)

unique_columns_strategy = st.lists(
    unique_column_strategy,
    unique_by=lambda column: column[1],
    max_size=10,
)


@st.composite
def duplicate_key_columns_strategy(draw):
    """
    Gera uma lista de colunas contendo pelo menos uma chave duplicada.
    """
    duplicated_key = draw(key_strategy)

    first_label = draw(label_strategy)
    second_label = draw(label_strategy)

    safe_column_strategy = st.tuples(
        label_strategy,
        key_strategy.filter(lambda value: value != duplicated_key),
    )

    before = draw(
        st.lists(
            safe_column_strategy,
            unique_by=lambda column: column[1],
            max_size=3,
        )
    )

    after = draw(
        st.lists(
            safe_column_strategy,
            unique_by=lambda column: column[1],
            max_size=3,
        )
    )

    return before + [
        (first_label, duplicated_key),
        (second_label, duplicated_key),
    ] + after


# ---------------------------------------------------------------------------
# Configuração dos testes property-based
# ---------------------------------------------------------------------------

suppressed_health_checks = [
    HealthCheck.too_slow,
    HealthCheck.filter_too_much,
]

if hasattr(HealthCheck, "function_scoped_fixture"):
    suppressed_health_checks.append(HealthCheck.function_scoped_fixture)

property_test = settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=suppressed_health_checks,
)


# ---------------------------------------------------------------------------
# Test double para exercitar hooks do Template Method
# ---------------------------------------------------------------------------

UNSET = object()


class FilterRecordingTemplate(BaseColumnMatrixTemplate):
    """
    Subclasse de teste para observar o comportamento de _get_filtered_cards.

    Ela permite:
    - registrar quais cards foram recebidos por _filter_cards;
    - opcionalmente sobrescrever o resultado do filtro.
    """

    def __init__(self, repository, filter_result=UNSET):
        super().__init__(repository)
        self.filter_result = filter_result
        self.received_cards = None

    def _filter_cards(self, cards):
        self.received_cards = cards

        if self.filter_result is not UNSET:
            return self.filter_result

        return super()._filter_cards(cards)


# ---------------------------------------------------------------------------
# Construção
# ---------------------------------------------------------------------------

def test_init_stores_repository(base_column_matrix_template, card_repository_mock):
    assert base_column_matrix_template._repository is card_repository_mock


# ---------------------------------------------------------------------------
# _filter_cards padrão
# ---------------------------------------------------------------------------

def test_default_filter_cards_returns_same_list_identity(
    base_column_matrix_template,
    card_repository_mock,
    card_factory,
    assert_repository_methods_not_called_except,
):
    cards = [card_factory(), card_factory()]
    original_cards = list(cards)

    result = base_column_matrix_template._filter_cards(cards)

    assert result is cards
    assert cards == original_cards

    assert_repository_methods_not_called_except(
        card_repository_mock,
        allowed=set(),
    )


def test_default_filter_cards_accepts_empty_list(
    base_column_matrix_template,
    card_repository_mock,
    assert_repository_methods_not_called_except,
):
    cards = []

    result = base_column_matrix_template._filter_cards(cards)

    assert result is cards

    assert_repository_methods_not_called_except(
        card_repository_mock,
        allowed=set(),
    )


# ---------------------------------------------------------------------------
# _get_filtered_cards
# ---------------------------------------------------------------------------

def test_get_filtered_cards_returns_repository_cards_using_default_filter(
    card_repository_mock_factory,
    card_factory,
    assert_repository_methods_not_called_except,
):
    repository = card_repository_mock_factory()

    cards = [card_factory(), card_factory()]
    repository.get_all_cards.return_value = cards

    template = BaseColumnMatrixTemplate(repository)

    result = template._get_filtered_cards()

    assert result is cards

    repository.get_all_cards.assert_called_once()

    assert_repository_methods_not_called_except(
        repository,
        allowed={"get_all_cards"},
    )


def test_get_filtered_cards_applies_custom_filter_hook(
    card_repository_mock_factory,
    card_factory,
    assert_repository_methods_not_called_except,
):
    repository = card_repository_mock_factory()

    cards = [card_factory(), card_factory()]
    filtered_cards = [cards[0]]

    repository.get_all_cards.return_value = cards

    template = FilterRecordingTemplate(
        repository,
        filter_result=filtered_cards,
    )

    result = template._get_filtered_cards()

    assert template.received_cards is cards
    assert result is filtered_cards

    repository.get_all_cards.assert_called_once()

    assert_repository_methods_not_called_except(
        repository,
        allowed={"get_all_cards"},
    )


# ---------------------------------------------------------------------------
# _get_col_headers
# ---------------------------------------------------------------------------

def test_get_col_headers_returns_labels_preserving_order(
    base_column_matrix_template,
    card_repository_mock,
    assert_repository_methods_not_called_except,
):
    columns = [
        ("06:00", "06"),
        ("07:00", "07"),
        ("08:00", "08"),
    ]

    result = base_column_matrix_template._get_col_headers(columns)

    assert result == ["06:00", "07:00", "08:00"]

    assert_repository_methods_not_called_except(
        card_repository_mock,
        allowed=set(),
    )


def test_get_col_headers_returns_empty_list_for_empty_columns(
    base_column_matrix_template,
    card_repository_mock,
    assert_repository_methods_not_called_except,
):
    result = base_column_matrix_template._get_col_headers([])

    assert result == []

    assert_repository_methods_not_called_except(
        card_repository_mock,
        allowed=set(),
    )


# ---------------------------------------------------------------------------
# _build_column_index_by_key
# ---------------------------------------------------------------------------

def test_build_column_index_by_key_maps_keys_to_indexes(
    base_column_matrix_template,
    card_repository_mock,
    assert_repository_methods_not_called_except,
):
    columns = [
        ("06:00", "06"),
        ("07:00", "07"),
        ("08:00", "08"),
    ]

    result = base_column_matrix_template._build_column_index_by_key(columns)

    assert result == {
        "06": 0,
        "07": 1,
        "08": 2,
    }

    assert_repository_methods_not_called_except(
        card_repository_mock,
        allowed=set(),
    )


def test_build_column_index_by_key_returns_empty_dict_for_empty_columns(
    base_column_matrix_template,
    card_repository_mock,
    assert_repository_methods_not_called_except,
):
    result = base_column_matrix_template._build_column_index_by_key([])

    assert result == {}

    assert_repository_methods_not_called_except(
        card_repository_mock,
        allowed=set(),
    )


def test_build_column_index_by_key_raises_when_keys_are_duplicated(
    base_column_matrix_template,
    card_repository_mock,
    assert_repository_methods_not_called_except,
):
    columns = [
        ("Primeiro label", "same_key"),
        ("Segundo label", "same_key"),
    ]

    with pytest.raises(DuplicatedColumnError):
        base_column_matrix_template._build_column_index_by_key(columns)

    assert_repository_methods_not_called_except(
        card_repository_mock,
        allowed=set(),
    )


# ---------------------------------------------------------------------------
# Hooks obrigatórios
# ---------------------------------------------------------------------------

def test_get_columns_raises_not_implemented(
    base_column_matrix_template,
    card_repository_mock,
    assert_repository_methods_not_called_except,
):
    with pytest.raises(NotImplementedError):
        base_column_matrix_template._get_columns()

    assert_repository_methods_not_called_except(
        card_repository_mock,
        allowed=set(),
    )


def test_get_column_key_raises_not_implemented(
    base_column_matrix_template,
    card_repository_mock,
    valid_card,
    assert_repository_methods_not_called_except,
):
    with pytest.raises(NotImplementedError):
        base_column_matrix_template._get_column_key(valid_card)

    assert_repository_methods_not_called_except(
        card_repository_mock,
        allowed=set(),
    )


# ---------------------------------------------------------------------------
# Testes property-based
# ---------------------------------------------------------------------------

@property_test
@given(data=st.data())
def test_property_default_filter_cards_returns_same_list_and_does_not_mutate(
    data,
    card_factory,
    base_column_matrix_template_factory,
):
    cards = data.draw(
        st.lists(
            st.builds(card_factory),
            max_size=5,
        )
    )

    original_cards = list(cards)

    template = base_column_matrix_template_factory()

    result = template._filter_cards(cards)

    assert result is cards
    assert cards == original_cards


@property_test
@given(data=st.data())
def test_property_get_filtered_cards_returns_repository_cards(
    data,
    card_factory,
    card_repository_mock_factory,
    assert_repository_methods_not_called_except,
):
    cards = data.draw(
        st.lists(
            st.builds(card_factory),
            max_size=5,
        )
    )

    repository = card_repository_mock_factory()
    repository.get_all_cards.return_value = cards

    template = BaseColumnMatrixTemplate(repository)

    result = template._get_filtered_cards()

    assert result is cards

    repository.get_all_cards.assert_called_once()

    assert_repository_methods_not_called_except(
        repository,
        allowed={"get_all_cards"},
    )


@property_test
@given(columns=unique_columns_strategy)
def test_property_get_col_headers_returns_labels_preserving_order(
    columns,
    base_column_matrix_template_factory,
):
    template = base_column_matrix_template_factory()

    result = template._get_col_headers(columns)

    assert result == [label for label, _ in columns]


@property_test
@given(columns=unique_columns_strategy)
def test_property_build_column_index_by_key_maps_unique_keys(
    columns,
    base_column_matrix_template_factory,
):
    template = base_column_matrix_template_factory()

    result = template._build_column_index_by_key(columns)

    expected = {
        key: index
        for index, (_, key) in enumerate(columns)
    }

    assert result == expected


@property_test
@given(columns=duplicate_key_columns_strategy())
def test_property_build_column_index_by_key_raises_for_duplicate_keys(
    columns,
    base_column_matrix_template_factory,
):
    template = base_column_matrix_template_factory()

    with pytest.raises(DuplicatedColumnError):
        template._build_column_index_by_key(columns)