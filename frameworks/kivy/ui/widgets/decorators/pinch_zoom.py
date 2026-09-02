from kivy.properties import (
    NumericProperty,
    BooleanProperty,
    StringProperty,
    ObjectProperty,
)

_ZOOM_SESSION_STATE: dict[str, float] = {}

def add_zoom(cls):
    zoom_atributes = {
        "zoom_level": NumericProperty(1.0),
        "default_zoom": NumericProperty(1.0),
        "min_zoom": NumericProperty(0.7),
        "max_zoom": NumericProperty(2.0),
        "zoom_step": NumericProperty(0.10),
        "zoom_session_key": StringProperty(""),
        "persist_zoom": BooleanProperty(True)
    }

    zoom_object = type(f'Zoom{cls.__name__}', (cls,), zoom_atributes)

    original_init = zoom_object.__init__

    def new_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        if self.persist_zoom and self.zoom_session_key:
            saved_zoom = _ZOOM_SESSION_STATE.get(self.zoom_session_key)
            if saved_zoom is not None:
                self.zoom_level = saved_zoom
            saved_sticky = _STICKY_SESSION_STATE.get(self.zoom_session_key)
            if saved_sticky is not None:
                self.sticky_headers = saved_sticky


