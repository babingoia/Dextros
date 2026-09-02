# Constantes Globais
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex

CELL_W = dp(90)
CELL_H = dp(44)
BORDER_WIDTH = dp(1)

# ==========================================================
# CORES
# ==========================================================
COLORS = {
    # Fundo geral do app
    "app_bg": "#0B0F1A",
    # Superfícies e cards
    "surface": "#101828",
    "surface_alt": "#1F2937",
    "card": "#111C2E",
    "field_bg": "#0D1524",
    # Bordas
    "border": "#26324B",
    "border_focus": "#3B82F6",
    # Texto
    "text_primary": "#F8FAFC",
    "text_secondary": "#94A3B8",
    "text_hint": "#64748B",
    # Botões e destaques
    "primary": "#3B82F6",
    "primary_pressed": "#2563EB",
    "on_primary": "#FFFFFF",
    # Navbar lateral
    "nav_bg": "#0A111D",
    "nav_text": "#AEB9CB",
    "nav_active_bg": "#1D4ED8",
    "nav_active_text": "#FFFFFF",
    # Detalhes
    "scrollbar": "#334155",
    "transparent": "#00000000",
    # Feedback e semântica
    "danger": "#EF4444",
    "danger_pressed": "#DC2626",
    "success": "#10B981",
    "warning": "#F59E0B",
}

# ==========================================================
# ESPAÇAMENTOS
# ==========================================================
_SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 24,
    "xxl": 32,
    "row": 24,
}

# ==========================================================
# RAIO DE BORDA
# ==========================================================
_RADIUS = {
    "sm": 8,
    "md": 12,
    "lg": 16,
    "pill": 999,
}

# ==========================================================
# TAMANHOS DE FONTE
# ==========================================================
_FONT_SIZES = {
    "caption": 12,
    "body": 15,
    "button": 15,
    "field": 16,
    "title": 20,
    "headline": 26,
}

# ==========================================================
# TAMANHOS DE COMPONENTES
# ==========================================================
_WIDGET_SIZES = {
    "touch_target": 48,
    "icon_button": 44,
    "input_height": 48,
    "button_height": 52,
    "appbar_height": 60,
    "nav_width": 288,
    "nav_item_height": 48,
    "date_button_width": 180,
    "text_area_height": 132,
    "scrollbar": 4,
    "header_height": 44,
    "section_title_height": 32,
    "field_label_height": 22,
    # Largura máxima do formulário em telas grandes
    "content_max_width": 720,
    "row_height": 36,
    "field_label_width": 80,
    "dialog_width": 500,
    "dialog_height": 450,
    "dialog_compact_width": 400,
    "dialog_content_max_height": 300,
}

# ==========================================================
# ESPESSURAS DE BORDA
# ==========================================================
_BORDER_WIDTHS = {
    "thin": 1.0,
    "focus": 1.7,
    "separator": 2.0,
}

# ==========================================================
# BREAKPOINTS / LAYOUT
# ==========================================================
BREAKPOINTS = {
    # A partir dessa largura, a navbar lateral fica fixa
    "desktop": dp(840),
    # A partir dessa largura, alguns pares de campos viram 2 colunas
    "two_columns": dp(1000),
}

_LAYOUT = {
    "pair_columns": 2,
}

_RATIOS = {
    "date_button_max_width": 0.45,
}


# ==========================================================
# HELPERS PARA USAR NO KV
# ==========================================================
def color(name):
    if name == "transparent":
        return (0.0, 0.0, 0.0, 0.0)
    rgba = get_color_from_hex(COLORS[name])
    if len(rgba) == 3:
        rgba = tuple(rgba) + (1.0,)
    return tuple(rgba)


def space(name):
    return dp(_SPACING[name])


def radius(name):
    return dp(_RADIUS[name])


def font(name):
    return sp(_FONT_SIZES[name])


def widget(name):
    return dp(_WIDGET_SIZES[name])


def border(name="thin"):
    return _BORDER_WIDTHS[name]


def layout(name):
    return _LAYOUT[name]


def ratio(name):
    return _RATIOS[name]


def is_desktop(width):
    return width >= BREAKPOINTS["desktop"]


def is_wide_enough(width, breakpoint_name):
    return width >= BREAKPOINTS[breakpoint_name]


def content_h_padding(width):
    """
    Calcula o padding horizontal para centralizar o formulário
    em telas grandes, mantendo uma margem mínima em telas pequenas.
    """
    max_width = widget("content_max_width")
    extra = width - max_width
    if extra <= 0:
        return space("lg")
    return max(space("lg"), extra / 2.0)