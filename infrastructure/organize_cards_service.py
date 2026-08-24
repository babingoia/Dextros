"""
This module defines the OrganizeCardsService class, which is responsible for organizing cards for a user.
"""
from core.value_objects.card import Card
from core.data_classes import DateHourGrid
from logging import getLogger


logger = getLogger(__name__)


class OrganizeCardsService:
    @staticmethod
    def organize_cards(cards: list["Card"]) -> DateHourGrid:
        """Organiza os cards por data e horário. Retorna um DateHourGrid
          com um mapa de data para horário e uma lista de datas únicas."""
        logger.debug(f"Organizing {len(cards)} cards into DateHourGrid")

        date_map: dict[str, dict[str, Card]] = {}
        unique_dates: list[str] = []

        cards = OrganizeCardsService.order_by_date(cards)

        for card in cards:
            if card.date not in date_map:
                date_map[card.date] = {}
                unique_dates.append(card.date)

            date_map[card.date][card.time] = card

        return DateHourGrid(date_map=date_map, unique_dates=unique_dates)


    @staticmethod
    def order_by_date(cards: list["Card"]) -> list["Card"]:
        """Ordena os cards por data."""
        logger.debug(f"Ordering {len(cards)} cards by date")

        return sorted(cards, key=lambda card: card.date)


    @staticmethod
    def order_by_horario(cards: list["Card"]) -> list["Card"]:
        """Ordena os cards por horário."""
        logger.debug(f"Ordering {len(cards)} cards by horario")
        return sorted(cards, key=lambda card: card.time)


    @staticmethod
    def order_by_date_and_horario(cards: list["Card"]) -> list["Card"]:
        """Ordena os cards por data e horário."""
        logger.debug(f"Ordering {len(cards)} cards by date and horario")
        
        return sorted(cards, key=lambda card: (card.date, card.time))