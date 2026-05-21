from datetime import datetime


class Time():
    HORARIOS = [f"{h:02}:00" for h in range(24)]  # Gera os horários automaticamente


    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def get_horarios(self):
        """Retorna a lista de horários disponíveis."""
        return self.HORARIOS
    

    def get_horario_now(self):
        """Retorna o horário atual no formato HH:00."""
        now = datetime.now()
        
        if now.minute >= 30:
            next_hour = (now.hour + 1) % 24
            return f"{next_hour:02}:00"
        
        return f"{now.hour:02}:00"


    def get_horario_colunas(self):
        """Retorna o mapeamento de horários para colunas."""
        return {horario: index + 1 for index, horario in enumerate(self.HORARIOS)}


    def is_valid_horario(self, horario: str) -> bool:
        """Valida se o horário está na lista de horários disponíveis."""
        return horario in self.get_horarios()