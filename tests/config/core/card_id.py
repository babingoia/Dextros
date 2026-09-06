"""
Arquivo 100% escrito sem IA.
"""

from hypothesis import assume, strategies as st

from core.value_objects.card_id import CardID


invalid_uuid_version = st.one_of(
    st.uuids(version=1),
    st.uuids(version=2),
    st.uuids(version=3),
    st.uuids(version=5),
)


invalid_id_inputs = st.one_of(
    st.integers(min_value=2**128+1),
    st.integers(max_value=-1),
    st.floats(),
    st.text()
)


invalid_comparisions = st.one_of(
    st.booleans(),
    st.integers(),
    st.floats(),
    st.datetimes(),
    st.lists(st.nothing()),
    st.dictionaries(st.nothing(), st.nothing()),
    st.tuples()
)


@st.composite
def none_valid_card_id(draw) -> CardID:
    """
    Injeta None no card ID para gerar automaticamente ID's pela própria classe.
    """
    return CardID.parse(draw(st.none()))


@st.composite
def valid_card_id(draw) -> CardID:
    """
    Retorna um CardID válido à partir de valores válidos gerados via string.
    """
    return CardID.parse(draw(st.one_of(st.none(), st.uuids(version=4))))
