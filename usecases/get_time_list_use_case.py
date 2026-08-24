from core.value_objects.time import Time

class GetTimeListUseCase:
    def __init__(self):

        self.TIME_LIST = [Time(f"{h:02}:00") for h in list(range(6, 24)) + list(range(0, 6))] 
    

    def execute(self) -> list[Time]:
        return self.TIME_LIST