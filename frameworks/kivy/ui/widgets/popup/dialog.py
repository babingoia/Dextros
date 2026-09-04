from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.modalview import ModalView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ListProperty
from kivy.core.window import Window
from kivy.graphics import BorderImage, Color, Rectangle
from kivy.lang import Builder
import frameworks.kivy.ui.app_theme as app_theme

Builder.load_file("frameworks/kivy/ui/widgets/popup/dialog.kv")

class DialogButton(Button):
    """Botão flat temado; escurece 20% no pressed."""
    color_name = StringProperty("primary")
    bg_color = ListProperty([0, 0, 0, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(color_name=self._update_bg, state=self._update_bg)
        self._update_bg()

    def _update_bg(self, *args):
        rgba = list(app_theme.color(self.color_name))
        if self.state == "down":
            rgba[:3] = [c * 0.8 for c in rgba[:3]]
        self.bg_color = rgba


class DialogMessage(Label):
    """Label de mensagem que cresce com o texto (usado em erro/confirm)."""


class AppDialog(ModalView):
    """Popup genérico do sistema: casca (título, scroll, separadores, botões)
    e conteúdo injetado via set_content()."""
    title_text = StringProperty("")
    auto_height = BooleanProperty(False)  # True = altura por conteúdo (compacto)
    card_width = NumericProperty(100)
    card_height = NumericProperty(100)
    scroll_height = NumericProperty(0)

    __events__ = ("on_confirm", "on_cancel")

    def __init__(self, title="", content=None, buttons=None, auto_height=False, **kwargs):
        super().__init__(**kwargs)
        self._strip_modal_background()
        self._build_overlay()
        self.title_text = title
        self.auto_height = auto_height
        self._on_window_size = lambda *a: self._compute_size()
        Window.bind(size=self._on_window_size)
        self.bind(auto_height=lambda *a: self._compute_size())
        self.ids.content_holder.bind(minimum_height=self._update_scroll_height)
        self._compute_size()
        if content:
            self.set_content(content)
        if buttons:
            self.set_buttons(buttons)

    # -- API pública ---------------------------------------------------------
    def set_content(self, widget):
        holder = self.ids.content_holder
        holder.clear_widgets()
        holder.add_widget(widget)
        return self

    def set_buttons(self, buttons):
        """buttons = [(texto, color_name, callback), ...]"""
        holder = self.ids.buttons_holder
        holder.clear_widgets()
        for text, color_name, callback in buttons:
            btn = DialogButton(text=text, color_name=color_name)
            btn.bind(on_release=callback)
            holder.add_widget(btn)
        return self
    
    def _strip_modal_background(self):
        """Remove só as instruções de fundo que o ModalView desenha por default
        (Color/Rectangle/BorderImage), sem tocar no resto do canvas."""
        for group in (self.canvas, self.canvas.before):
            for instr in list(group.children):
                if isinstance(instr, (BorderImage, Rectangle, Color)):
                    group.remove(instr)

    def _build_overlay(self):
        """Véu escuro sob nosso controle (agora única camada de dimming)."""
        with self.canvas.before:
            self._overlay_color = Color(0, 0, 0, 0.3)  # ← opacidade do véu, ajuste aqui
            self._overlay_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._sync_overlay, size=self._sync_overlay)

    def _sync_overlay(self, *args):
        self._overlay_rect.pos = self.pos
        self._overlay_rect.size = self.size

    def on_confirm(self): pass
    def on_cancel(self): pass

    def on_dismiss(self):
        Window.unbind(size=self._on_window_size)

    # -- interno -------------------------------------------------------------
    def _compute_size(self, *args):
        if self.auto_height:
            self.card_width = min(app_theme.widget("dialog_compact_width"), Window.width * 0.9)
        else:
            self.card_width = min(app_theme.widget("dialog_width"), Window.width * 0.9)
            self.card_height = min(app_theme.widget("dialog_height"), Window.height * 0.9)
        self._update_scroll_height()

    def _update_scroll_height(self, *args):
        content_h = self.ids.content_holder.height
        if self.auto_height:
            self.scroll_height = min(content_h, app_theme.widget("dialog_content_max_height"))
            fixo = (
                app_theme.space("lg") * 2                        # padding vertical
                + app_theme.widget("section_title_height")       # título
                + app_theme.border("separator") * 2              # separadores
                + app_theme.widget("button_height")              # barra de botões
                + app_theme.space("md") * 3                      # spacing entre seções
            )
            self.card_height = fixo + self.scroll_height
        else:
            self.scroll_height = content_h


class ConfirmDialog(AppDialog):
    def __init__(self, message="", title="Confirmação", confirm_text="Confirmar",
                 cancel_text="Cancelar", confirm_color="danger",
                 on_confirm=None, on_cancel=None, **kwargs):
        super().__init__(title=title, auto_height=True, **kwargs)
        if on_confirm: self.bind(on_confirm=on_confirm)
        if on_cancel: self.bind(on_cancel=on_cancel)
        self.set_content(DialogMessage(text=message))
        self.set_buttons([
            (confirm_text, confirm_color, self._fire_confirm),
            (cancel_text, "primary", self._fire_cancel),
        ])

    def _fire_confirm(self, *a):
        self.dismiss()
        self.dispatch("on_confirm")

    def _fire_cancel(self, *a):
        self.dismiss()
        self.dispatch("on_cancel")


class ErrorDialog(AppDialog):
    def __init__(self, message="", title="Erro", button_text="Entendi", **kwargs):
        super().__init__(title=title, auto_height=True, **kwargs)
        self.set_content(DialogMessage(text=message))
        self.set_buttons([(button_text, "danger", lambda *a: self.dismiss())])


class MetricStat(BoxLayout):
    """Uma coluna de métrica (rótulo + valor + ocorrências), usada em diálogos de resumo."""
    label = StringProperty("")
    value = StringProperty("")
    occurrences = NumericProperty(0)
    color_name = StringProperty("primary")


class MetricsSummaryDialog(AppDialog):
    """Diálogo genérico pra exibir N métricas lado a lado (ex: médias de um dia).
    Não sabe nada sobre glicemia/insulina — só recebe uma lista pronta."""

    def __init__(self, metrics=None, title="", **kwargs):
        super().__init__(title=title, auto_height=True, **kwargs)
        self.set_content(self._build_metrics_grid(metrics or []))
        self.set_buttons([("Fechar", "primary", lambda *a: self.dismiss())])

    def _build_metrics_grid(self, metrics):
        grid = GridLayout(
            cols=len(metrics) or 1,
            spacing=app_theme.space("md"),
            size_hint_y=None,
        )
        grid.bind(minimum_height=grid.setter("height"))
        for metric in metrics:
            grid.add_widget(MetricStat(
                label=metric.get("label", ""),
                value=str(metric.get("value", "")),
                occurrences=metric.get("occurrences", 0),
                color_name=metric.get("color_name", "primary"),
            ))
        return grid