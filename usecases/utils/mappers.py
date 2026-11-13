from core.value_objects.card import Card
from usecases.dtos.card_output import CardOutput

def to_card_output(card: Card) -> CardOutput:
    """Converte objeto de domínio Card para DTO de saída CardOutput."""
    exercise_name = card.exercise.exercise_name if getattr(card, 'exercise', None) else None
    exercise_intensity = card.exercise.intensity if getattr(card, 'exercise', None) else None

    # A nutrição vive dentro do MealPeriod (card.meal.meal é o VO Meal com os
    # valores consumidos); MealPeriod sem nutrição registrada carrega None.
    nutrition = card.meal.meal if getattr(card, 'meal', None) else None

    return CardOutput(
        card_id=card.card_id.card_id,
        card_date=card.card_date._date,
        card_time=card.card_time._time,
        glycemia=card.glycemia.glycemia,
        long_acting_insulin=card.long_acting_insulin.quantity,
        short_acting_insulin=card.short_acting_insulin.quantity,
        meal=card.meal.meal_period,
        observation=card.obs.observation,
        carbohydrate_g=nutrition.carbohydrate_g if nutrition else None,
        fat_g=nutrition.fat_g if nutrition else None,
        exercise_name=exercise_name,
        exercise_intensity=exercise_intensity
    )