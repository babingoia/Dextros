from typing import Any

from adapters.controllers.dtos.time_view_model import TimeList
from adapters.controllers.i_controller import IController
from usecases.dtos.time_output import TimeOutput



class TimeController(IController[Any, TimeList]):
    """Request que retorna uma lista organizada de quais horários o sistema salva para serem consumidas
    pela UI.
    """
    def __init__(self, get_time_list_use_case):
        self.get_time_list_use_case = get_time_list_use_case

    
    def _parse_output_view_model(self, values: list[TimeOutput]) -> TimeList:
        time_list = TimeList([])

        for value in values:
            time_list.not_datetime_time.append(value.time_value.strftime("%H:%M:%S"))
        
        return time_list


    def execute(self, request: Any = None) -> TimeList:
        time_list = self.get_time_list_use_case.execute()
        parsed_time_list: TimeList = self._parse_output_view_model(time_list)
        
        return parsed_time_list
    