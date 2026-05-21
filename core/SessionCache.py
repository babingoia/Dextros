from infrastructure.json_handler import JsonHandler


class SessionCache:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.cards_on_session = None
            cls._instance._listeners = {"on_add": [], "on_remove": []}
            return cls._instance
        else:
            return cls._instance
    

    @property
    def cards_on_session(self):
        if self._cards is None:
            self._cards = JsonHandler.load_from_json()  # carrega só quando alguém pedir
        return self._cards
    

    @cards_on_session.setter
    def cards_on_session(self, value):
        self._cards = value


    def add_card(self, card):
        self.cards_on_session.append(card)
        JsonHandler.save_to_json(self.cards_on_session)
        self._emit("on_add")
    

    def remove_card(self, card):
        self.cards_on_session = [c for c in self.cards_on_session if not (c.data == card.data and c.horario == card.horario)]
        JsonHandler.save_to_json(self.cards_on_session)
        self._emit("on_remove")


    def get_cards(self):
        return self.cards_on_session
    

    def bind(self, event_name, callback):
        if event_name in self._listeners:
            self._listeners[event_name].append(callback)
        else:
            raise ValueError(f"Evento '{event_name}' não suportado.")
    

    def _emit(self, event_name):
        for callback in self._listeners[event_name]:
            callback()