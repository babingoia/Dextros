from usecases.dtos.matrix_data import MatrixData
from usecases.dtos.card_output import CardOutput
from usecases.dtos.cardDTOInput import CardDTOInput
from usecases.dtos.single_row_matrix_data import SingleRowMatrixData
from usecases.dtos.card_average_output import CardAverageOutput

from adapters.controllers.dtos.card_average_view_model import CardAverageViewModel
from adapters.controllers.dtos.matrix_data_view_model import MatrixDataViewModel
from adapters.controllers.dtos.card_view_model import CardViewModel
from adapters.controllers.dtos.single_row_matrix_view import SingleRowMatrixView



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
    data['observation'] = data['observation'].strip()
    data['short_acting_insulin'] = data['short_acting_insulin'].strip()
    return data


def empty_to_none(value):
    return None if value == '' else value


def int_or_none(value):
    value = empty_to_none(value)
    return int(value) if value is not None and value is not 0 else None


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


def card_output_to_view_model(card: CardOutput) -> CardViewModel:
    """Mapeia um CardOutput para o CardViewModel (TypedDict)."""
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
        "meal": card.meal or "",
        "observation": card.observation or ""
    }


def card_average_output_to_view_model(card_average: CardAverageOutput) -> CardAverageViewModel:
    return CardAverageViewModel(
        glycemia=card_average.glycemia,
        short_acting_insulin=card_average.short_acting_insulin,
        long_acting_insulin=card_average.long_acting_insulin,
        glycemia_occurrences=card_average.glycemia_occurrences,
        short_acting_insulin_occurrences=card_average.short_acting_insulin_occurrences,
        long_acting_insulin_occurrences=card_average.long_acting_insulin_occurrences
    )


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
        "observation": ""
    }


def single_row_to_view_model(single_row: SingleRowMatrixData) -> SingleRowMatrixView:
    cell_data_vm = []
    
    for card_average_output in single_row.cells:
        cell_data_vm.append(card_average_output_to_view_model(card_average_output))
            
    return SingleRowMatrixView(
        col_headers=single_row.col_headers,
        cells=cell_data_vm
    )