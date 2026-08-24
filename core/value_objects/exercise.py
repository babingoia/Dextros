from dataclasses import dataclass


# Constantes
_INTENSITY_POSSIBLE_VALUES = {"leve", "moderada", "vigorosa"}

@dataclass(frozen=True)
class Exercise:
    """
    Guarda informações importantes sobre exercícios realizados pelo usuário anteriormente. Por conta disso,
    ambos os atributos podem receber None e string e um nome pode ser definido sem intensidade. Valor None é
    atribuido automaticamente a ambos os campos.\n

    Os níveis de intensidade são por padrão: leve, moderada e rigorosa seguindo o guia de atividade física para
    a população brasileira.
    """

    exercise_name: str | None = None
    intensity: str | None = None

    def __post_init__(self):
        if self.intensity != None and self.exercise_name == None:
            raise ValueError(f"Intesity without exercise!")
        
        if self.intensity != None and self.intensity not in _INTENSITY_POSSIBLE_VALUES:
            raise ValueError(f"Intensity invalid.")


    @classmethod
    def parse(cls, exercise_value: str | None, intensity_value: str | None) -> "Exercise":
        if exercise_value != None:
            exercise_value = exercise_value.strip().lower()

        if intensity_value != None:
            intensity_value = intensity_value.strip().lower()
        
        return cls(exercise_value, intensity_value)