# tests/unit/usecases/get_matrix_data/test_base_2d_matrix_template.py

from datetime import date
from unittest.mock import MagicMock

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from usecases.get_matrix_data import base_2d_matrix_template as base_2d_module
from usecases.get_matrix_data.base_2d_matrix_template import Base2DMatrixTemplate
from usecases.dtos.card_output import CardOutput
from usecases.dtos.matrix_data import MatrixData
from usecases.utils.exceptions import (
    DuplicatedCellError,
    DuplicatedColumnError,
)
from usecases.utils.mappers import to_card_output


# ---------------------------------------------------------------------------
# Strategies Hypothesis
# ---------------------------------------------------------------------------

date_strategy = st.dates(
    min_value=date(2020, 1, 1),
    max_value=date.today(),
).map(lambda value: value.strftime("%Y-%m-%d"))

label_strategy = st.text(max_size=8)
key_strategy = st.text(min_size=1, max_size=8)

unique_column_strategy = st.tuples(label_strategy, key_strategy)

unique_columns_strategy = st.lists(
    unique_column_strategy,
    unique_by=lambda column: column[1],
    max_size=5,
)

non_empty_unique_columns_strategy = st.lists(
    unique_column_strategy,
    unique_by=lambda column: column[1],
    min_size=1,
    max_size=5,
)

row_key_strategy = st.text(min_size=1, max_size=8)


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
# Spy para to_card_output
# ---------------------------------------------------------------------------

@pytest.fixture
def spy_to_card_output(monkeypatch):
    """
    Faz patch de to_card_output dentro do módulo do Base2DMatrixTemplate,
    preservando o comportamento real da função, mas permitindo verificar
    chamadas.
    """
    spy = MagicMock(side_effect=to_card_output)
    monkeypatch.setattr(base_2d_module, "to_card_output", spy)
    return spy


# ---------------------------------------------------------------------------
# Stub de teste para Base2DMatrixTemplate
# ---------------------------------------------------------------------------

UNSET = object()


class Stub2DMatrixTemplate(Base2DMatrixTemplate):
    """
    Subclasse configurável para testar o comportamento comum do
    Base2DMatrixTemplate sem depender das subclasses concretas.
    """

    def __init__(
        self,
        repository,
        columns=None,
        column_key_func=UNSET,
        filter_func=UNSET,
        row_key_func=UNSET,
    ):
        super().__init__(repository)
        self._stub_columns = columns or []
        self._stub_column_key_func = column_key_func
        self._stub_filter_func = filter_func
        self._stub_row_key_func = row_key_func

    def _get_columns(self):
        return self._stub_columns

    def _get_column_key(self, card):
        if self._stub_column_key_func is UNSET:
            raise NotImplementedError

        return self._stub_column_key_func(card)

    def _filter_cards(self, cards):
        if self._stub_filter_func is not UNSET:
            return self._stub_filter_func(cards)

        return super()._filter_cards(cards)

    def _get_card_row_key(self, card):
        if self._stub_row_key_func is not UNSET:
            return self._stub_row_key_func(card)

        return super()._get_card_row_key(card)


# ---------------------------------------------------------------------------
# Caminho vazio
# ---------------------------------------------------------------------------

def test_execute_without_cards_returns_empty_matrix_with_column_headers(
    card_repository_mock_factory,
    spy_to_card_output,
    assert_repository_methods_not_called_except,
):
    columns = [
        ("06:00", "06"),
        ("07:00", "07"),
    ]

    repository = card_repository_mock_factory()
    repository.get_all_cards.return_value = []

    template = Stub2DMatrixTemplate(
        repository,
        columns=columns,
        column_key_func=lambda card: "06",
    )

    matrix = template.execute()

    assert isinstance(matrix, MatrixData)
    assert matrix.row_headers == []
    assert matrix.col_headers == ["06:00", "07:00"]
    assert matrix.cell_data == {}

    repository.get_all_cards.assert_called_once()
    spy_to_card_output.assert_not_called()

    assert_repository_methods_not_called_except(
        repository,
        allowed={"get_all_cards"},
    )


def test_execute_returns_empty_matrix_when_filter_removes_all_cards(
    repository_with_cards,
    card_with_date_factory,
    spy_to_card_output,
    assert_repository_methods_not_called_except,
):
    columns = [
        ("06:00", "06"),
        ("07:00", "07"),
    ]

    cards = [
        card_with_date_factory("2024-05-20"),
        card_with_date_factory("2024-05-21"),
    ]

    repository = repository_with_cards(cards)

    template = Stub2DMatrixTemplate(
        repository,
        columns=columns,
        column_key_func=lambda card: "06",
        filter_func=lambda cards: [],
    )

    matrix = template.execute()

    assert isinstance(matrix, MatrixData)
    assert matrix.row_headers == []
    assert matrix.col_headers == ["06:00", "07:00"]
    assert matrix.cell_data == {}

    repository.get_all_cards.assert_called_once()
    spy_to_card_output.assert_not_called()

    assert_repository_methods_not_called_except(
        repository,
        allowed={"get_all_cards"},
    )


def test_execute_calls_get_columns_before_get_filtered_cards(
    card_repository_mock_factory,
):
    calls = []

    class RecordingTemplate(Stub2DMatrixTemplate):
        def _get_columns(self):
            calls.append("columns")
            return super()._get_columns()

        def _get_filtered_cards(self):
            calls.append("filtered_cards")
            return super()._get_filtered_cards()

    repository = card_repository_mock_factory()
    repository.get_all_cards.return_value = []

    template = RecordingTemplate(
        repository,
        columns=[("06:00", "06")],
        column_key_func=lambda card: "06",
    )

    template.execute()

    assert calls == ["columns", "filtered_cards"]


# ---------------------------------------------------------------------------
# Caminho com dados
# ---------------------------------------------------------------------------

def test_execute_with_cards_builds_expected_matrix(
    repository_with_cards,
    card_with_date_factory,
    spy_to_card_output,
    assert_repository_methods_not_called_except,
):
    day_1 = "2024-05-20"
    day_2 = "2024-05-21"

    card_day_1_col_06 = card_with_date_factory(day_1)
    card_day_1_col_07 = card_with_date_factory(day_1)
    card_day_2_col_06 = card_with_date_factory(day_2)

    column_key_by_card_id = {
        id(card_day_1_col_06): "06",
        id(card_day_1_col_07): "07",
        id(card_day_2_col_06): "06",
    }

    columns = [
        ("06:00", "06"),
        ("07:00", "07"),
    ]

    repository = repository_with_cards(
        [
            card_day_2_col_06,
            card_day_1_col_07,
            card_day_1_col_06,
        ]
    )

    template = Stub2DMatrixTemplate(
        repository,
        columns=columns,
        column_key_func=lambda card: column_key_by_card_id[id(card)],
    )

    matrix = template.execute()

    assert isinstance(matrix, MatrixData)

    assert matrix.row_headers == [day_1, day_2]
    assert matrix.col_headers == ["06:00", "07:00"]

    assert len(matrix.cell_data) == 4

    assert matrix.cell_data[(0, 0)] == to_card_output(card_day_1_col_06)
    assert matrix.cell_data[(0, 1)] == to_card_output(card_day_1_col_07)
    assert matrix.cell_data[(1, 0)] == to_card_output(card_day_2_col_06)
    assert matrix.cell_data[(1, 1)] is None

    assert spy_to_card_output.call_count == 3

    spy_to_card_output.assert_any_call(card_day_1_col_06)
    spy_to_card_output.assert_any_call(card_day_1_col_07)
    spy_to_card_output.assert_any_call(card_day_2_col_06)

    assert_repository_methods_not_called_except(
        repository,
        allowed={"get_all_cards"},
    )


def test_execute_uses_only_filtered_cards(
    repository_with_cards,
    card_with_date_factory,
    spy_to_card_output,
    assert_repository_methods_not_called_except,
):
    kept_card = card_with_date_factory("2024-05-20")
    removed_card = card_with_date_factory("2024-05-21")

    repository = repository_with_cards([kept_card, removed_card])

    columns = [("06:00", "06")]

    template = Stub2DMatrixTemplate(
        repository,
        columns=columns,
        column_key_func=lambda card: "06",
        filter_func=lambda cards: [cards[0]],
    )

    matrix = template.execute()

    assert matrix.row_headers == ["2024-05-20"]
    assert matrix.col_headers == ["06:00"]

    assert matrix.cell_data[(0, 0)] == to_card_output(kept_card)

    spy_to_card_output.assert_called_once_with(kept_card)

    assert_repository_methods_not_called_except(
        repository,
        allowed={"get_all_cards"},
    )


def test_execute_keeps_row_when_column_key_is_none(
    repository_with_cards,
    card_with_date_factory,
    spy_to_card_output,
):
    card = card_with_date_factory("2024-05-20")

    repository = repository_with_cards([card])

    columns = [("06:00", "06")]

    template = Stub2DMatrixTemplate(
        repository,
        columns=columns,
        column_key_func=lambda card: None,
    )

    matrix = template.execute()

    assert matrix.row_headers == ["2024-05-20"]
    assert matrix.col_headers == ["06:00"]
    assert matrix.cell_data == {(0, 0): None}

    spy_to_card_output.assert_not_called()


def test_execute_keeps_row_when_column_key_is_unknown(
    repository_with_cards,
    card_with_date_factory,
    spy_to_card_output,
):
    card = card_with_date_factory("2024-05-20")

    repository = repository_with_cards([card])

    columns = [("06:00", "06")]

    template = Stub2DMatrixTemplate(
        repository,
        columns=columns,
        column_key_func=lambda card: "99",
    )

    matrix = template.execute()

    assert matrix.row_headers == ["2024-05-20"]
    assert matrix.col_headers == ["06:00"]
    assert matrix.cell_data == {(0, 0): None}

    spy_to_card_output.assert_not_called()


def test_execute_excludes_cards_with_none_row_key(
    repository_with_cards,
    card_with_date_factory,
    spy_to_card_output,
):
    card = card_with_date_factory("2024-05-20")

    repository = repository_with_cards([card])

    columns = [("06:00", "06")]

    template = Stub2DMatrixTemplate(
        repository,
        columns=columns,
        column_key_func=lambda card: "06",
        row_key_func=lambda card: None,
    )

    matrix = template.execute()

    assert matrix.row_headers == []
    assert matrix.col_headers == ["06:00"]
    assert matrix.cell_data == {}

    spy_to_card_output.assert_not_called()


# ---------------------------------------------------------------------------
# Row key
# ---------------------------------------------------------------------------

def test_get_card_row_key_formats_date_as_iso(
    card_repository_mock_factory,
    card_with_date_factory,
):
    card = card_with_date_factory("2024-05-20")

    template = Stub2DMatrixTemplate(card_repository_mock_factory())

    assert template._get_card_row_key(card) == "2024-05-20"


def test_get_raw_row_keys_collects_non_none_keys_in_order(
    card_repository_mock_factory,
    card_factory,
):
    first_card = card_factory()
    second_card = card_factory()
    third_card = card_factory()

    row_key_by_card_id = {
        id(first_card): "2024-05-22",
        id(second_card): None,
        id(third_card): "2024-05-20",
    }

    template = Stub2DMatrixTemplate(
        card_repository_mock_factory(),
        row_key_func=lambda card: row_key_by_card_id[id(card)],
    )

    result = template._get_raw_row_keys([first_card, second_card, third_card])

    assert result == ["2024-05-22", "2024-05-20"]


def test_unique_row_keys_preserves_first_occurrence(
    card_repository_mock_factory,
):
    template = Stub2DMatrixTemplate(card_repository_mock_factory())

    result = template._unique_row_keys(["b", "a", "b", "c", "a"])

    assert result == ["b", "a", "c"]


def test_order_row_keys_returns_sorted_keys(
    card_repository_mock_factory,
):
    template = Stub2DMatrixTemplate(card_repository_mock_factory())

    result = template._order_row_keys(
        [
            "2024-05-22",
            "2024-05-20",
            "2024-05-21",
        ]
    )

    assert result == [
        "2024-05-20",
        "2024-05-21",
        "2024-05-22",
    ]


def test_get_row_keys_returns_unique_sorted_row_keys(
    card_repository_mock_factory,
    card_factory,
):
    first_card = card_factory()
    second_card = card_factory()
    third_card = card_factory()
    fourth_card = card_factory()

    row_key_by_card_id = {
        id(first_card): "2024-05-22",
        id(second_card): "2024-05-20",
        id(third_card): "2024-05-22",
        id(fourth_card): "2024-05-21",
    }

    template = Stub2DMatrixTemplate(
        card_repository_mock_factory(),
        row_key_func=lambda card: row_key_by_card_id[id(card)],
    )

    result = template._get_row_keys(
        [
            first_card,
            second_card,
            third_card,
            fourth_card,
        ]
    )

    assert result == [
        "2024-05-20",
        "2024-05-21",
        "2024-05-22",
    ]


# ---------------------------------------------------------------------------
# Lookup
# ---------------------------------------------------------------------------

def test_build_lookup_maps_valid_cards(
    card_repository_mock_factory,
    card_with_date_factory,
):
    day = "2024-05-20"
    card = card_with_date_factory(day)

    columns = [
        ("06:00", "06"),
        ("07:00", "07"),
    ]

    template = Stub2DMatrixTemplate(
        card_repository_mock_factory(),
        columns=columns,
        column_key_func=lambda card: "07",
    )

    lookup = template._build_lookup([card], columns)

    assert lookup == {
        day: {
            1: card,
        },
    }


def test_build_lookup_skips_cards_with_none_row_key(
    card_repository_mock_factory,
    card_with_date_factory,
):
    card = card_with_date_factory("2024-05-20")

    columns = [("06:00", "06")]

    template = Stub2DMatrixTemplate(
        card_repository_mock_factory(),
        columns=columns,
        column_key_func=lambda card: "06",
        row_key_func=lambda card: None,
    )

    lookup = template._build_lookup([card], columns)

    assert lookup == {}


def test_build_lookup_skips_cards_with_none_column_key(
    card_repository_mock_factory,
    card_with_date_factory,
):
    card = card_with_date_factory("2024-05-20")

    columns = [("06:00", "06")]

    template = Stub2DMatrixTemplate(
        card_repository_mock_factory(),
        columns=columns,
        column_key_func=lambda card: None,
    )

    lookup = template._build_lookup([card], columns)

    assert lookup == {}


def test_build_lookup_skips_cards_with_unknown_column_key(
    card_repository_mock_factory,
    card_with_date_factory,
):
    card = card_with_date_factory("2024-05-20")

    columns = [("06:00", "06")]

    template = Stub2DMatrixTemplate(
        card_repository_mock_factory(),
        columns=columns,
        column_key_func=lambda card: "99",
    )

    lookup = template._build_lookup([card], columns)

    assert lookup == {}


def test_build_lookup_raises_duplicated_cell_error_when_two_cards_share_row_and_column(
    card_repository_mock_factory,
    card_with_date_factory,
):
    day = "2024-05-20"

    first_card = card_with_date_factory(day)
    second_card = card_with_date_factory(day)

    columns = [("06:00", "06")]

    template = Stub2DMatrixTemplate(
        card_repository_mock_factory(),
        columns=columns,
        column_key_func=lambda card: "06",
    )

    with pytest.raises(DuplicatedCellError):
        template._build_lookup([first_card, second_card], columns)


# ---------------------------------------------------------------------------
# Cell data
# ---------------------------------------------------------------------------

def test_build_cell_data_fills_missing_cells_with_none(
    card_repository_mock_factory,
    spy_to_card_output,
):
    columns = [
        ("A", "a"),
        ("B", "b"),
    ]

    row_keys = ["row"]

    template = Stub2DMatrixTemplate(
        card_repository_mock_factory(),
        columns=columns,
    )

    cell_data = template._build_cell_data(row_keys, columns, {})

    assert cell_data == {
        (0, 0): None,
        (0, 1): None,
    }

    spy_to_card_output.assert_not_called()


def test_build_cell_data_converts_present_cards(
    card_repository_mock_factory,
    card_factory,
    spy_to_card_output,
):
    card = card_factory()

    columns = [
        ("A", "a"),
        ("B", "b"),
    ]

    row_keys = ["row"]

    lookup = {
        "row": {
            0: card,
        },
    }

    template = Stub2DMatrixTemplate(
        card_repository_mock_factory(),
        columns=columns,
    )

    cell_data = template._build_cell_data(row_keys, columns, lookup)

    assert cell_data == {
        (0, 0): to_card_output(card),
        (0, 1): None,
    }

    spy_to_card_output.assert_called_once_with(card)


# ---------------------------------------------------------------------------
# Erros e hooks obrigatórios
# ---------------------------------------------------------------------------

def test_execute_propagates_repository_error(
    card_repository_mock_factory,
):
    repository = card_repository_mock_factory()
    repository.get_all_cards.side_effect = RuntimeError("boom")

    template = Stub2DMatrixTemplate(
        repository,
        columns=[("A", "a")],
        column_key_func=lambda card: "a",
    )

    with pytest.raises(RuntimeError):
        template.execute()


def test_execute_propagates_mapper_error(
    repository_with_cards,
    card_with_date_factory,
    spy_to_card_output,
):
    card = card_with_date_factory("2024-05-20")

    repository = repository_with_cards([card])

    spy_to_card_output.side_effect = RuntimeError("boom")

    template = Stub2DMatrixTemplate(
        repository,
        columns=[("A", "a")],
        column_key_func=lambda card: "a",
    )

    with pytest.raises(RuntimeError):
        template.execute()


def test_execute_raises_duplicated_column_error_for_duplicate_column_keys(
    repository_with_cards,
    card_with_date_factory,
):
    card = card_with_date_factory("2024-05-20")

    repository = repository_with_cards([card])

    columns = [
        ("A", "same"),
        ("B", "same"),
    ]

    template = Stub2DMatrixTemplate(
        repository,
        columns=columns,
        column_key_func=lambda card: "same",
    )

    with pytest.raises(DuplicatedColumnError):
        template.execute()


def test_execute_raises_duplicated_cell_error_when_two_cards_share_row_and_column(
    repository_with_cards,
    card_with_date_factory,
    spy_to_card_output,
):
    day = "2024-05-20"

    first_card = card_with_date_factory(day)
    second_card = card_with_date_factory(day)

    repository = repository_with_cards([first_card, second_card])

    columns = [("A", "a")]

    template = Stub2DMatrixTemplate(
        repository,
        columns=columns,
        column_key_func=lambda card: "a",
    )

    with pytest.raises(DuplicatedCellError):
        template.execute()

    spy_to_card_output.assert_not_called()


def test_execute_raises_not_implemented_when_columns_hook_missing(
    card_repository_mock_factory,
):
    class MissingColumnsTemplate(Base2DMatrixTemplate):
        def _get_column_key(self, card):
            return "a"

    repository = card_repository_mock_factory()
    repository.get_all_cards.return_value = []

    template = MissingColumnsTemplate(repository)

    with pytest.raises(NotImplementedError):
        template.execute()

    repository.get_all_cards.assert_not_called()


def test_execute_raises_not_implemented_when_column_key_hook_missing(
    repository_with_cards,
    card_with_date_factory,
):
    class MissingColumnKeyTemplate(Base2DMatrixTemplate):
        def _get_columns(self):
            return [("A", "a")]

    card = card_with_date_factory("2024-05-20")

    repository = repository_with_cards([card])

    template = MissingColumnKeyTemplate(repository)

    with pytest.raises(NotImplementedError):
        template.execute()

    repository.get_all_cards.assert_called_once()


# ---------------------------------------------------------------------------
# Testes property-based
# ---------------------------------------------------------------------------

@property_test
@given(row_keys=st.lists(row_key_strategy, max_size=10))
def test_property_unique_row_keys_preserves_first_occurrence(
    row_keys,
    card_repository_mock_factory,
):
    template = Stub2DMatrixTemplate(card_repository_mock_factory())

    result = template._unique_row_keys(row_keys)

    assert result == list(dict.fromkeys(row_keys))


@property_test
@given(row_keys=st.lists(row_key_strategy, max_size=10))
def test_property_order_row_keys_returns_sorted_keys(
    row_keys,
    card_repository_mock_factory,
):
    template = Stub2DMatrixTemplate(card_repository_mock_factory())

    result = template._order_row_keys(row_keys)

    assert result == sorted(row_keys)


@property_test
@given(data=st.data())
def test_property_get_row_keys_returns_unique_sorted_dates(
    data,
    card_repository_mock_factory,
    card_with_date_factory,
):
    dates = data.draw(st.lists(date_strategy, max_size=10))

    cards = [card_with_date_factory(card_date) for card_date in dates]

    template = Stub2DMatrixTemplate(
        card_repository_mock_factory(),
        columns=[("A", "a")],
        column_key_func=lambda card: "a",
    )

    result = template._get_row_keys(cards)

    assert result == sorted(set(dates))


@property_test
@given(
    row_keys=st.lists(row_key_strategy, unique=True, max_size=5),
    columns=unique_columns_strategy,
)
def test_property_build_cell_data_creates_all_cells(
    row_keys,
    columns,
    card_repository_mock_factory,
):
    template = Stub2DMatrixTemplate(
        card_repository_mock_factory(),
        columns=columns,
    )

    cell_data = template._build_cell_data(row_keys, columns, {})

    assert len(cell_data) == len(row_keys) * len(columns)
    assert all(value is None for value in cell_data.values())


@property_test
@given(columns=unique_columns_strategy)
def test_property_execute_without_cards_returns_empty_matrix(
    columns,
    card_repository_mock_factory,
):
    repository = card_repository_mock_factory()
    repository.get_all_cards.return_value = []

    template = Stub2DMatrixTemplate(
        repository,
        columns=columns,
        column_key_func=lambda card: None,
    )

    matrix = template.execute()

    assert matrix.row_headers == []
    assert matrix.cell_data == {}
    assert matrix.col_headers == [label for label, _ in columns]


@property_test
@given(data=st.data())
def test_property_execute_with_one_card_per_date_returns_dense_matrix(
    data,
    card_repository_mock_factory,
    card_with_date_factory,
):
    columns = data.draw(non_empty_unique_columns_strategy)
    dates = data.draw(st.lists(date_strategy, unique=True, max_size=5))

    cards = [card_with_date_factory(card_date) for card_date in dates]

    repository = card_repository_mock_factory()
    repository.get_all_cards.return_value = cards

    first_column_key = columns[0][1]

    template = Stub2DMatrixTemplate(
        repository,
        columns=columns,
        column_key_func=lambda card: first_column_key,
    )

    matrix = template.execute()

    assert matrix.row_headers == sorted(dates)
    assert len(matrix.cell_data) == len(dates) * len(columns)

    expected_outputs = {
        card_date: to_card_output(card)
        for card_date, card in zip(dates, cards)
    }

    for row_index, row_key in enumerate(sorted(dates)):
        assert isinstance(matrix.cell_data[(row_index, 0)], CardOutput)
        assert matrix.cell_data[(row_index, 0)] == expected_outputs[row_key]

        for column_index in range(1, len(columns)):
            assert matrix.cell_data[(row_index, column_index)] is None


@property_test
@given(data=st.data())
def test_property_execute_raises_duplicated_cell_error_when_two_cards_share_row_and_column(
    data,
    card_repository_mock_factory,
    card_with_date_factory,
):
    columns = data.draw(non_empty_unique_columns_strategy)
    duplicated_date = data.draw(date_strategy)

    first_card = card_with_date_factory(duplicated_date)
    second_card = card_with_date_factory(duplicated_date)

    repository = card_repository_mock_factory()
    repository.get_all_cards.return_value = [first_card, second_card]

    first_column_key = columns[0][1]

    template = Stub2DMatrixTemplate(
        repository,
        columns=columns,
        column_key_func=lambda card: first_column_key,
    )

    with pytest.raises(DuplicatedCellError):
        template.execute()