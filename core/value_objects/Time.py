from datetime import datetime
from logging import getLogger


logger = getLogger(__name__)


class Time():
    HORARIOS = [f"{h:02}:00" for h in list(range(6, 24)) + list(range(0, 6))] 


    def __init__(self, **kwargs):
        logger.debug("Initializing Time value object")

        super().__init__(**kwargs)


    def get_horarios(self):
        """Retorna a lista de horários disponíveis."""
        logger.debug("Retrieving available horarios")

        return self.HORARIOS
    

    def get_horario_now(self):
        """Retorna o horário atual no formato HH:00."""
        logger.debug("Calculating current horario")

        now = datetime.now()
        
        if now.minute >= 30:
            next_hour = (now.hour + 1) % 24
            return f"{next_hour:02}:00"
        
        return f"{now.hour:02}:00"


    def is_valid_horario(self, horario: str) -> bool:
        """Valida se o horário está na lista de horários disponíveis."""
        logger.debug(f"Validating horario: {horario}")
        
        return horario in self.get_horarios()