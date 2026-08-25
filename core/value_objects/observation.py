from dataclasses import dataclass


@dataclass(frozen=True)
class Observation:
    """
    Guarda um pequeno texto de observação que o usuário pode querer deixar ou não. Strings vazias são
    convertidas em None. Valor padrão é None.
    """
    
    observation: str | None = None


    def __post_init__(self):
        """Método reservado. Usar parse para criar entidades como entry point."""
        if self.observation is None:
            return
        
        if self.observation == "":
            raise ValueError(f"Observation text with 0 characters: {self.observation}")
        
        if len(self.observation) > 240:
            raise ValueError(f"Observation lenght exceds 240 characters: {len(self.observation)}")
    

    @classmethod
    def parse(cls, obs_value: str | None = None) -> "Observation":
        if obs_value is None:
            return cls(obs_value)
        
        obs_value = obs_value.strip()
        
        if obs_value == "":
            obs_value = None
        
        return cls(obs_value)


        

