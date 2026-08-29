from core.value_objects.time import Time
from usecases.dtos.time_output import TimeOutput

class GetTimeListUseCase:
    def __init__(self):

        self.TIME_LIST = [Time.parse(f"{h:02}:00") for h in list(range(6, 24)) + list(range(0, 6))] 
    

    def execute(self) -> list[TimeOutput]:
        
        parsed_time_list: list[TimeOutput] = []
        
        for unique_time in self.TIME_LIST:
            unique_time_value = unique_time._time
            time_output = TimeOutput(unique_time_value)
            parsed_time_list.append(time_output)
        
        return parsed_time_list