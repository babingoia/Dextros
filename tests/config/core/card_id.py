import pytest

from hypothesis import assume, strategies as st

from core.value_objects.card_id import CardID


invalid_uuid_version = st.one_of(
    st.uuids(version=1),
    st.uuids(version=2),
    st.uuids(version=3),
    st.uuids(version=5),
)


invalid_id_inputs = st.one_of(
    st.integers(min_value=129),
    st.integers(max_value=0),
    st.text()
)


@st.composite
def valid_card_id(draw) -> CardID:
    """
    Retorna um CardID válido.
    """
    return CardID.parse(draw(st.uuids(version=4, allow_nil=True)))


