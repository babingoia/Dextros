from usecases.dtos.matrix_data import MatrixData
from usecases.dtos.card_output import CardOutput
from usecases.dtos.cardDTOInput import CardDTOInput
from adapters.controllers.dtos.matrix_data_view_model import MatrixDataViewModel
from adapters.controllers.dtos.card_view_model import CardViewModel


def strip_view_model(data: CardViewModel) -> CardViewModel:
    """Recebe uma view model e aplica .strip() em todos os seus campos."""
    data['card_id'] = data['card_id'].strip()
    data['card_data'] = data['card_data'].strip()
    data['card_time'] = data['card_time'].strip()
    data['exercise']['exercise_name'] = data['exercise']['exercise_name'].strip()
    data['exercise']['intensity'] = data['exercise']['intensity'].strip()
    data['glycemia'] = data['glycemia'].strip()
    data['long_acting_insulin'] = data['long_acting_insulin'].strip()
    data['meal'] = data['meal'].strip()
    data['carbohydrate_g'] = data['carbohydrate_g'].strip()
    data['fat_g'] = data['fat_g'].strip()
    data['observation'] = data['observation'].strip()
    return data


def empty_to_none(value):
    return None if value == '' else value


def int_or_none(value):
    value = empty_to_none(value)
    return int(value) if value is not None and value is not 0 else None


def normalize_decimal(value):
    """Converte vírgula decimal brasileira em ponto ("45,2" -> "45.2").
    Responsabilidade da camada de apresentação — o VO de domínio não lida com vírgula."""
    if value is None:
        return None
    return value.replace(',', '.') if isinstance(value, str) else value


def decimal_or_none(value):
    """Converte texto decimal em float ou None. Segue a convenção do app
    (int_or_none): string vazia e 0 significam "campo não preenchido"."""
    value = empty_to_none(normalize_decimal(value))
    if value is None:
        return None
    parsed = float(value)
    return None if parsed == 0 else parsed


def view_model_to_input(card: CardViewModel) -> CardDTOInput:
    """Transforma um CardViewModel em CardDTOInput. Transforma em None campos com string vazia
    ou números 0.
    """
    exercise = card['exercise']

    return CardDTOInput(
        card_id=empty_to_none(card['card_id']),
        card_date=card['card_data'],
        card_time=card['card_time'],

        glycemia=int(card['glycemia']),

        exercise_name=empty_to_none(exercise['exercise_name']),
        exercise_intensity=empty_to_none(exercise['intensity']),

        meal=empty_to_none(card['meal']),

        short_acting_insulin=int_or_none(card['short_acting_insulin']),
        long_acting_insulin=int_or_none(card['long_acting_insulin']),

        carbohydrate_g=decimal_or_none(card['carbohydrate_g']),
        fat_g=decimal_or_none(card['fat_g']),

        observation=empty_to_none(card['observation']),
    )


def matrix_to_view_model(matrix_data: MatrixData) -> MatrixDataViewModel:
    """
    Converte o MatrixData (saída do Use Case) em MatrixDataViewModel (entrada da UI).
    Células vazias (None) são convertidas em CardViewModel com strings vazias, 
    evitando que a UI precise lidar com nulos.
    """
    cell_data_vm = {}
    
    for coords, card_output in matrix_data.cell_data.items():
        if card_output is not None:
            cell_data_vm[coords] = card_output_to_view_model(card_output)
        else:
            cell_data_vm[coords] = empty_card_view_model()
            
    return MatrixDataViewModel(
        row_headers=matrix_data.row_headers,
        col_headers=matrix_data.col_headers,
        cell_data=cell_data_vm
    )


def format_grams_for_display(value):
    """Formata gramas consumidas para exibição ("45", "45,2", "" quando ausente).
    Convenção de apresentação: vírgula decimal brasileira, sem unidade — a unidade
    está no rótulo do campo na tela."""
    if value is None:
        return ""
    text = f"{value:g}"
    return text.replace(".", ",")


def parse_brazilian_decimal(text):
    """Texto de campo numérico -> float, ou None quando vazio/inválido.
    Aceita vírgula decimal (mesma convenção de normalize_decimal): o usuário
    digita "45,2" e o app grava "68,2" com vírgula no campo."""
    if text is None:
        return None
    raw = str(text).strip().replace(",", ".")
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def sum_grams_for_input(current_text, added_value):
    """Soma o valor consumido de uma comida ao que já está no campo do
    formulário e devolve o texto pronto para o input.

    Quem registra uma refeição de verdade come MAIS DE UM alimento: adicionar
    "Arroz, 150 g" depois de "Feijão, 100 g" tem que acumular, não substituir.
    Texto vazio ou inválido conta como 0 — a comida buscada pode ser a primeira
    do registro. O resultado segue a convenção de exibição (%g, vírgula decimal)."""
    total = added_value + (parse_brazilian_decimal(current_text) or 0.0)
    return format_grams_for_display(total)


def card_output_to_view_model(card: CardOutput) -> CardViewModel:
    """Mapeia um CardOutput para o CardViewModel (TypedDict) da UI.
    A nutrição (carboidratos/gorduras consumidos) aparece no popup de detalhes
    do card, abaixo de Refeição."""
    return {
        "card_id": card.card_id,
        "card_data": card.card_date.strftime("%d/%m/%Y"),
        "card_time": card.card_time.strftime("%H:%M"),
        "glycemia": str(card.glycemia) if card.glycemia is not None else "",
        "long_acting_insulin": str(card.long_acting_insulin) if card.long_acting_insulin is not None else "",
        "short_acting_insulin": str(card.short_acting_insulin) if card.short_acting_insulin is not None else "",
        "exercise": {
            "exercise_name": card.exercise.exercise_name or "",
            "intensity": card.exercise.intensity or ""
        },
        # Card sem refeição próxima (MealPeriod None) exibe "nenhum" no popup
        # de detalhes — mesma palavra da opção de UI do picker.
        "meal": card.meal if card.meal else "nenhum",
        "carbohydrate_g": format_grams_for_display(card.carbohydrate_g),
        "fat_g": format_grams_for_display(card.fat_g),
        "observation": card.observation or ""
    }


def empty_card_view_model() -> CardViewModel:
    """Retorna um CardViewModel 'zerado' para células vazias da matriz."""
    return {
        "card_id": "",
        "card_data": "",
        "card_time": "",
        "glycemia": "",
        "long_acting_insulin": "",
        "short_acting_insulin": "",
        "exercise": {"exercise_name": "", "intensity": ""},
        "meal": "",
        "carbohydrate_g": "",
        "fat_g": "",
        "observation": ""
    }
