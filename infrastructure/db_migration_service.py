import json
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path

from core.value_objects.meal import _VALID_MEAL_VALUES

logger = getLogger(__name__)


@dataclass
class MigrationReport:
    """Resumo do que a migração encontrou e fez numa execução."""

    cards_checked: int = 0
    cards_migrated: int = 0
    invalid_periods_nulled: int = 0


class DatabaseMigrationService:
    """Checa o banco de cards do usuário e atualiza o arquivo quando a
    estrutura está desatualizada em relação ao formato canônico atual.

    Formato canônico do campo meal (espelho do VO MealPeriod):
        {"meal_period": str | None, "meal": {"carbohydrate_g": int | None,
         "fat_g": int | None} | None}
    Formato legado (pré meal-improvements): meal como string simples.

    Propriedades:
    - Idempotente: nada a migrar -> NENHUMA escrita (arquivo fica byte a byte igual),
      por isso pode rodar em todo início de app.
    - Atômico: escreve em .tmp e faz replace (mesmo padrão do JsonHandler).
    - Sem quarentena: valor não mapeável vira None + log — nada de card é descartado.
    - Container preservado: arquivo legado em lista pura continua em lista;
      arquivo em {"cards": [...]} continua em dict.
    - Falha honesta: JSON corrompido propaga (igual ao JsonHandler), não "conserta"
      corrupção silenciosamente.

    Trabalha em dicts crus (sem VOs, sem repositório) e roda no composition root
    ANTES da construção do JsonHandler/repositório, que então sempre leem o
    formato canônico. A tolerância a legado no parser é só cinto e suspensório.
    """

    def __init__(self, save_path: str | Path):
        self.save_path = Path(save_path)

    def run(self) -> MigrationReport:
        report = MigrationReport()

        loaded = self._load()
        if loaded is None:
            return report  # arquivo inexistente: nada a migrar

        raw_cards, container = loaded

        migrated_cards: list[dict] = []
        for card in raw_cards:
            report.cards_checked += 1

            if not isinstance(card, dict):
                migrated_cards.append(card)
                logger.warning(f"Non-dict card entry kept as-is: {type(card)}")
                continue

            new_card, changed, invalid_period = self._migrate_card_meal(card)
            migrated_cards.append(new_card)

            if changed:
                report.cards_migrated += 1
            if invalid_period:
                report.invalid_periods_nulled += 1

        if report.cards_migrated > 0:
            self._write(migrated_cards, container)
            logger.info(
                f"Migration complete: {report.cards_migrated}/{report.cards_checked} cards migrated, "
                f"{report.invalid_periods_nulled} invalid periods nulled"
            )
        else:
            logger.debug(f"Migration no-op: {report.cards_checked} cards already canonical")

        return report

    # -------------------------------------------------------------------
    # Carga / escrita (dicts crus, mesmo contrato de forma do JsonHandler)
    # -------------------------------------------------------------------

    def _load(self) -> tuple[list[dict], str] | None:
        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            logger.debug(f"No database file to migrate at {self.save_path}")
            return None

        # Compatibilidade retroativa do container (mesma do JsonHandler):
        # lista pura de cards (legado) ou {"cards": [...]} (formato atual).
        if isinstance(data, list):
            return data, "list"
        if isinstance(data, dict):
            return data.get("cards", []), "dict"

        raise ValueError(
            f"Unexpected JSON structure in {self.save_path}: {type(data).__name__}"
        )

    def _write(self, cards: list[dict], container: str) -> None:
        payload = cards if container == "list" else {"cards": cards}

        self.save_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.save_path.with_suffix(self.save_path.suffix + ".tmp")

        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        tmp_path.replace(self.save_path)

    # -------------------------------------------------------------------
    # Migração do campo meal
    # -------------------------------------------------------------------

    def _migrate_card_meal(self, card: dict) -> tuple[dict, bool, bool]:
        """Normaliza a chave meal do card para o formato canônico.

        Retorna (novo_card, houve_mudanca, periodo_invalido_anulado).
        """
        meal_raw = card.get("meal")  # chave ausente e null seguem o mesmo caminho
        invalid_period = False

        if isinstance(meal_raw, str):
            period = meal_raw.strip().lower()
            if period not in _VALID_MEAL_VALUES:
                logger.warning(f"Invalid legacy meal period nulled: {meal_raw!r}")
                period = None
                invalid_period = True
            new_meal: dict = {"meal_period": period, "meal": None}
            changed = True
        elif meal_raw is None:
            # meal null é SEMPRE legado: o formato canônico grava o objeto dict
            # (mesmo que internamente tudo null), nunca null cru.
            new_meal = {"meal_period": None, "meal": None}
            changed = True
        elif isinstance(meal_raw, dict):
            nutrition_raw = meal_raw.get("meal")
            normalized_nutrition = self._normalize_nutrition(nutrition_raw)
            new_meal = {
                "meal_period": meal_raw.get("meal_period"),
                "meal": normalized_nutrition,
            }
            changed = new_meal != meal_raw
        else:
            logger.warning(f"Unexpected meal type nulled: {type(meal_raw)}")
            new_meal = {"meal_period": None, "meal": None}
            changed = True

        if changed:
            new_card = dict(card)
            new_card["meal"] = new_meal
            return new_card, True, invalid_period

        return card, False, False

    def _normalize_nutrition(self, nutrition_raw) -> dict | None:
        """Traz a nutrição aninhada para o canônico (inteiros ou None).

        Estrutura já canônica -> devolvida intacta (idempotência).
        Float -> arredondado para int (o canônico é grama inteira).
        Tipo impossível -> None + warning (sem quarentena).
        """
        if nutrition_raw is None:
            return None

        if not isinstance(nutrition_raw, dict):
            logger.warning(f"Unexpected nutrition type nulled: {type(nutrition_raw)}")
            return None

        normalized: dict = {}
        changed_by_coercion = False
        for key in ("carbohydrate_g", "fat_g"):
            value = nutrition_raw.get(key)
            if value is None:
                normalized[key] = None
            elif isinstance(value, bool) or not isinstance(value, int | float | str):
                logger.warning(f"Invalid nutrition value nulled: {key}={value!r}")
                normalized[key] = None
                changed_by_coercion = True
            else:
                try:
                    coerced = round(float(value))
                except (TypeError, ValueError):
                    logger.warning(f"Invalid nutrition value nulled: {key}={value!r}")
                    coerced = None
                    changed_by_coercion = True

                if value != coerced:
                    changed_by_coercion = True
                normalized[key] = coerced

        if not changed_by_coercion:
            return nutrition_raw  # já canônico

        return normalized
