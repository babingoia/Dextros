# tests/unit/test_json_repo_unit.py
import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from adapters.repositories.jsonRepo import JsonRepository
from core.value_objects.card_id import CardID
from tests.exceptions import CardNotFoundError

@pytest.fixture
def mock_handler():
    handler = MagicMock()
    handler.load.return_value = [] # Começa vazio
    return handler

@pytest.fixture
def mock_parser():
    return MagicMock()

@pytest.fixture
def mock_creator():
    return MagicMock()

@pytest.fixture
def repo(mock_handler, mock_parser, mock_creator):
    return JsonRepository(mock_handler, mock_creator, mock_parser)


class TestInitialization:
    def test_init_calls_import_cards(self, mock_handler, mock_parser, mock_creator):
        JsonRepository(mock_handler, mock_creator, mock_parser)
        mock_handler.load.assert_called_once()

    def test_import_cards_parses_and_creates(self, mock_handler, mock_parser, mock_creator):
        mock_handler.load.return_value = [{"card_id": "1"}, {"card_id": "2"}]
        mock_parser.parse.side_effect = ["dto1", "dto2"]
        mock_creator.create_card.side_effect = ["card1", "card2"]
        
        repo = JsonRepository(mock_handler, mock_creator, mock_parser)
        
        assert mock_parser.parse.call_count == 2
        assert mock_creator.create_card.call_count == 2
        assert repo.cards_on_session == ["card1", "card2"]


class TestGetOperations:
    def test_get_all_cards_returns_copy(self, repo):
        repo.cards_on_session.append("card1")
        result = repo.get_all_cards()
        assert result == ["card1"]
        result.append("card2") # Modificar a lista retornada não afeta o repo
        assert len(repo.cards_on_session) == 1

    def test_get_card_success(self, repo):
        # Usamos um CardID real para que o __eq__ que você implementou funcione no mock
        real_id = CardID.parse("f47ac10b-58cc-4372-a567-0e02b2c3d479")
        mock_card = MagicMock()
        mock_card.card_id = real_id 
        
        repo.cards_on_session.append(mock_card)
        
        result = repo.get_card("f47ac10b-58cc-4372-a567-0e02b2c3d479")
        assert result == mock_card

    def test_get_card_not_found(self, repo):
        with pytest.raises(CardNotFoundError):
            repo.get_card("00000000-0000-0000-0000-000000000000")


class TestMutations:
    def test_add_card_appends_and_exports(self, repo, mock_handler):
        mock_card = MagicMock()
        repo.add_card(mock_card)
        
        assert mock_card in repo.cards_on_session
        mock_handler.export.assert_called_once()

    def test_remove_card_success(self, repo, mock_handler):
        real_id = CardID.parse("f47ac10b-58cc-4372-a567-0e02b2c3d479")
        mock_card = MagicMock()
        mock_card.card_id = real_id
        repo.cards_on_session.append(mock_card)
        
        repo.remove_card("f47ac10b-58cc-4372-a567-0e02b2c3d479")
        
        assert mock_card not in repo.cards_on_session
        mock_handler.export.assert_called_once()

    def test_remove_card_not_found(self, repo):
        with pytest.raises(CardNotFoundError):
            repo.remove_card("00000000-0000-0000-0000-000000000000")

    def test_update_card_success(self, repo, mock_handler):
        real_id = CardID.parse("f47ac10b-58cc-4372-a567-0e02b2c3d479")
        old_card = MagicMock()
        old_card.card_id = real_id
        repo.cards_on_session.append(old_card)
        
        new_card = MagicMock()
        new_card.card_id = real_id
        
        repo.update_card(new_card)
        
        assert old_card not in repo.cards_on_session
        assert new_card in repo.cards_on_session
        mock_handler.export.assert_called_once()

    def test_update_card_not_found(self, repo):
        fake_card = MagicMock()
        fake_card.card_id = CardID.parse("db0a221f-cd9c-469b-980b-df067332e185")
        
        with pytest.raises(CardNotFoundError):
            repo.update_card(fake_card)