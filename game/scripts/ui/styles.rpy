define menu_w = 1920
define menu_h = 1080

init -2 python:
    """Helpers visuais reutilizados nas telas de menu e jogo.

    Este módulo concentra:
    - Paleta de cores dos títulos coloridos.
    - Funções utilitárias de estilização textual.
    - Definições de estilo usadas por múltiplas screens.
    """

    TITLE_COLORS = [
        "#ff9aa2",
        "#ffb7b2",
        "#ffdac1",
        "#e2f0cb",
        "#b5ead7",
        "#c7ceea",
    ]

    def rainbow_title(text, start_index=0):
        """Aplica cor por caractere para criar título com efeito arco-íris.

        Args:
            text: conteúdo textual original.
            start_index: deslocamento inicial da paleta para variar combinação.

        Returns:
            String com tags Ren'Py de cor por caractere.
        """
        pieces = []
        color_i = 0

        for ch in text:
            if ch.isspace():
                pieces.append(ch)
                continue

            color = TITLE_COLORS[(start_index + color_i) % len(TITLE_COLORS)]
            pieces.append("{color=%s}%s{/color}" % (color, ch))
            color_i += 1

        return "".join(pieces)

style default:
    font "fonts/LowresPixel-Regular.otf"
    size 26
    color "#fff"
    xalign 0.5

style button:
    activate_sound "audio/sfx/ui_click.ogg"

style menu_frame:
    xalign 0.5
    yalign 0.5
    padding (40, 40)
    background Solid("#4b3f63")

style menu_title:
    font "fonts/Pixel Game.otf"
    size 120
    color "#fff"
    xalign 0.5

style menu_item:
    font "fonts/LowresPixel-Regular.otf"
    size 26
    color "#fff"
    hover_color "#ffd24d"
    selected_color "#ffd24d"
    xalign 0.5
    activate_sound "audio/sfx/ui_click.ogg"

style menu_item_text is menu_item

style menu_content:
    font "fonts/LowresPixel-Regular.otf"
    size 26
    color "#ddd"

style audio_label is menu_item:
    size 26
    color "#fff"

style audio_volume_bar is bar:
    xmaximum 500
    ymaximum 22
    left_bar Solid("#6fe7ff")
    right_bar Solid("#1f1a2f")
    thumb "gui/slider/horizontal_idle_thumb.png"
    thumb_offset 3

transform new_game_blink:
    alpha 1.0
    linear 0.07 alpha 0.0
    linear 0.07 alpha 1.0
    linear 0.07 alpha 0.0
    linear 0.07 alpha 1.0
    linear 0.07 alpha 0.0
    linear 0.07 alpha 1.0
