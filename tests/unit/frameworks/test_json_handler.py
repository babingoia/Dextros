import pytest
import json
from pathlib import Path
from frameworks.json_handler_service import JsonHandler
from adapters.repositories.DTOs.card_data_model import CardDataModel

class TestJsonHandlerInit:
    def test_init_sets_path_object(self, tmp_path):
        handler = JsonHandler(tmp_path / "test.json")
        assert str(handler.save_path).endswith("test.json")

class TestJsonHandlerExport:
    def test_export_creates_tmp_and_replaces(self, tmp_path):
        file_path = tmp_path / "test.json"
        handler = JsonHandler(file_path)
        handler.export([{"card_id": "123"}])
        
        assert file_path.exists()
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data == {"cards": [{"card_id": "123"}]}

class TestJsonHandlerLoad:
    def test_load_returns_parsed_data(self, tmp_path):
        file_path = tmp_path / "test.json"
        file_path.write_text('{"cards": [{"card_id": "1"}]}', encoding="utf-8")
        
        handler = JsonHandler(file_path)
        result = handler.load()
        
        assert len(result) == 1
        assert result[0]["card_id"] == "1"

    def test_load_handles_file_not_found(self, tmp_path):
        file_path = tmp_path / "nonexistent.json"
        handler = JsonHandler(file_path)
        result = handler.load()
        assert result == []

    def test_load_handles_json_decode_error(self, tmp_path):
        file_path = tmp_path / "invalid.json"
        # Escreve um JSON inválido de propósito para forçar o erro real do módulo json
        file_path.write_text("{ this is not valid json }", encoding="utf-8")
        
        handler = JsonHandler(file_path)
        with pytest.raises(json.JSONDecodeError):
            handler.load()

    def test_load_handles_invalid_data_structure(self, tmp_path):
        file_path = tmp_path / "invalid_structure.json"
        # Força um TypeError: "cards" é uma string, não uma lista.
        # O código vai tentar fazer CardDataModel("n"), o que lança TypeError.
        file_path.write_text('{"cards": "not_a_list"}', encoding="utf-8")
        
        handler = JsonHandler(file_path)
        with pytest.raises((TypeError, ValueError)):
            handler.load()