import json
from pathlib import Path

import pytest

from infrastructure.db_migration_service import DatabaseMigrationService


CANONICAL_MEAL = {"meal_period": "pós almoço", "meal": {"carbohydrate_g": 45, "fat_g": 12}}


def _card(card_id="f47ac10b-58cc-4372-a567-0e02b2c3d479", meal="pós almoço"):
    return {
        "card_id": card_id, "card_date": "2024-01-03", "card_time": "00:00",
        "glycemia": 156, "long_acting_insulin": 30, "short_acting_insulin": 5,
        "meal": meal, "observation": "Me sentindo bem",
        "exercise": {"exercise_name": "ciclismo", "intensity": None}
    }


def _service(tmp_path: Path) -> DatabaseMigrationService:
    return DatabaseMigrationService(tmp_path / "cards.json")


def _write_raw(tmp_path: Path, payload, filename="cards.json") -> Path:
    path = tmp_path / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    return path


def _read_raw(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class TestMigracaoFormatoLegado:
    def test_meal_string_vira_objeto_canonico_sem_nutricao(self, tmp_path):
        """Card legado (meal string) não tem nutrição — migra para o objeto com meal: null."""
        path = _write_raw(tmp_path, {"cards": [_card()]})
        report = _service(tmp_path).run()

        migrated = _read_raw(path)["cards"][0]["meal"]
        assert migrated == {"meal_period": "pós almoço", "meal": None}
        assert report.cards_migrated == 1
        assert report.cards_checked == 1

    def test_meal_null_normalizado(self, tmp_path):
        path = _write_raw(tmp_path, {"cards": [_card(meal=None)]})
        report = _service(tmp_path).run()

        assert _read_raw(path)["cards"][0]["meal"] == {"meal_period": None, "meal": None}
        assert report.cards_migrated == 1

    def test_chave_meal_ausente_normalizada(self, tmp_path):
        card = _card()
        del card["meal"]
        path = _write_raw(tmp_path, {"cards": [card]})
        report = _service(tmp_path).run()

        assert _read_raw(path)["cards"][0]["meal"] == {"meal_period": None, "meal": None}
        assert report.cards_migrated == 1

    def test_periodo_invalido_vira_null_e_e_contabilizado(self, tmp_path):
        path = _write_raw(tmp_path, {"cards": [_card(meal="banana")]})
        report = _service(tmp_path).run()

        assert _read_raw(path)["cards"][0]["meal"]["meal_period"] is None
        assert report.invalid_periods_nulled == 1

    def test_container_legado_em_lista_e_preservado(self, tmp_path):
        """Arquivo no formato lista pura (pré cards_v2) continua lista após migrar meal."""
        path = _write_raw(tmp_path, [_card(), _card(meal=None)])
        _service(tmp_path).run()

        raw = _read_raw(path)
        assert isinstance(raw, list)
        assert raw[0]["meal"]["meal_period"] == "pós almoço"

    def test_container_dict_e_preservado(self, tmp_path):
        path = _write_raw(tmp_path, {"cards": [_card()]})
        _service(tmp_path).run()

        raw = _read_raw(path)
        assert isinstance(raw, dict)
        assert set(raw.keys()) == {"cards"}

    def test_arquivo_misto_migra_so_os_legados_no_report(self, tmp_path):
        cards = [
            _card(),                                  # string legado
            _card(card_id="1b4d0c5f-3e7a-4b8c-9d2e-5f6a7b8c9d0e", meal=CANONICAL_MEAL),  # canônico
            _card(card_id="2b4d0c5f-3e7a-4b8c-9d2e-5f6a7b8c9d0e", meal=None),            # null
        ]
        path = _write_raw(tmp_path, {"cards": cards})
        report = DatabaseMigrationService(path).run()

        assert report.cards_checked == 3
        assert report.cards_migrated == 2  # string e null; o canônico não conta


class TestIdempotencia:
    def test_arquivo_ja_canonico_nao_e_reescrito_byte_a_byte(self, tmp_path):
        cards = {"cards": [_card(meal=CANONICAL_MEAL), _card(meal={"meal_period": None, "meal": None})]}
        path = _write_raw(tmp_path, cards)
        antes = path.read_bytes()

        report = DatabaseMigrationService(path).run()

        assert report.cards_migrated == 0
        assert path.read_bytes() == antes  # NENHUMA escrita

    def test_segunda_execucao_e_no_op(self, tmp_path):
        path = _write_raw(tmp_path, {"cards": [_card()]})
        primeiro = DatabaseMigrationService(path).run()
        depois_primeira = path.read_bytes()

        segundo = DatabaseMigrationService(path).run()

        assert primeiro.cards_migrated == 1
        assert segundo.cards_migrated == 0
        assert path.read_bytes() == depois_primeira

    def test_nutricao_canonica_nao_e_coagida(self, tmp_path):
        meal = {"meal_period": "jejum", "meal": {"carbohydrate_g": 39, "fat_g": 2}}
        path = _write_raw(tmp_path, {"cards": [_card(meal=meal)]})
        DatabaseMigrationService(path).run()

        assert _read_raw(path)["cards"][0]["meal"] == meal


class TestNutricaoImpura:
    def test_nutricao_float_e_coagida_para_int(self, tmp_path):
        meal = {"meal_period": "jejum", "meal": {"carbohydrate_g": 45.6, "fat_g": 12.2}}
        path = _write_raw(tmp_path, {"cards": [_card(meal=meal)]})
        DatabaseMigrationService(path).run()

        assert _read_raw(path)["cards"][0]["meal"]["meal"] == {"carbohydrate_g": 46, "fat_g": 12}

    def test_nutricao_com_tipo_impossivel_vira_null(self, tmp_path):
        meal = {"meal_period": "jejum", "meal": {"carbohydrate_g": ["lixo"], "fat_g": 12}}
        path = _write_raw(tmp_path, {"cards": [_card(meal=meal)]})
        report = DatabaseMigrationService(path).run()

        assert _read_raw(path)["cards"][0]["meal"]["meal"] == {"carbohydrate_g": None, "fat_g": 12}
        assert report.cards_migrated == 1

    def test_nutricao_com_tipo_impossivel_e_verdadeiro_lixo_vira_null(self, tmp_path):
        meal = {"meal_period": "jejum", "meal": "banana"}
        path = _write_raw(tmp_path, {"cards": [_card(meal=meal)]})
        DatabaseMigrationService(path).run()

        assert _read_raw(path)["cards"][0]["meal"] == {"meal_period": "jejum", "meal": None}


class TestFalhaHonesta:
    def test_arquivo_inexistente_e_no_op_sem_criar_arquivo(self, tmp_path):
        report = _service(tmp_path).run()

        assert report.cards_checked == 0
        assert not (tmp_path / "cards.json").exists()

    def test_json_corrompido_propaga(self, tmp_path):
        path = tmp_path / "cards.json"
        path.write_text("{corrompido: [", encoding="utf-8")

        with pytest.raises(json.JSONDecodeError):
            DatabaseMigrationService(path).run()

    def test_estrutura_desconhecida_propaga(self, tmp_path):
        """Container de tipo impossível (nem lista nem dict) propaga ValueError,
        mesma regra do JsonHandler. Dict sem 'cards' é tratado como vazio,
        igual o JsonHandler faz — comportamento consistente de propósito."""
        path = _write_raw(tmp_path, "banana")

        with pytest.raises(ValueError):
            DatabaseMigrationService(path).run()

    def test_dict_sem_chave_cards_e_tratado_como_vazio(self, tmp_path):
        path = _write_raw(tmp_path, {"nao_sao_cards": []})
        report = DatabaseMigrationService(path).run()

        assert report.cards_checked == 0
