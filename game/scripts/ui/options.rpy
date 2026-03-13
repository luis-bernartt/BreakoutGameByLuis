# Tela de remapeamento de teclas.
# Objetivo: permitir personalização de controles sem sair do jogo.
# Variáveis de screen:
# - hovered_btn: botão sob cursor para destaque visual.
# - waiting_keybind_action: ação aguardando nova tecla.
# - keybind_message: feedback de conflito/sucesso/cancelamento.
# Integração:
# - Usa KeyCapture para capturar a próxima tecla pressionada.
screen options_keybinds():
    tag menu
    modal True
    default hovered_btn = ""

    frame style "menu_frame" xsize menu_w ysize menu_h:
        vbox:
            spacing 18
            xalign 0.5
            yalign 0.5

            text "[rainbow_title('Keybinds')]" style "menu_title" size 40

            fixed:
                xfill True
                ysize 40
                if waiting_keybind_action is None:
                    text "Clique em uma ação e depois pressione a tecla desejada." size 22 color "#bbb" xalign 0.5 yalign 0.5
                else:
                    text "Pressione uma tecla para: [action_label(waiting_keybind_action)]" size 22 color "#ffd24d" xalign 0.5 yalign 0.5

            fixed:
                xfill True
                ysize 30
                if keybind_message:
                    text "[keybind_message]" size 20 color "#8fd3ff" xalign 0.5 yalign 0.5

            null height 8

            hbox:
                spacing 25
                xalign 0.5
                text "Mover para a esquerda:" color "#fff" size 26 xminimum 420
                textbutton ("Aguardando..." if waiting_keybind_action == "move_left" else "[key_label(get_keybind('move_left'))]") style "menu_item" selected False action [
                    SetVariable("waiting_keybind_action", "move_left"),
                    SetVariable("keybind_message", "")
                ]

            hbox:
                spacing 25
                xalign 0.5
                text "Mover para a direita:" color "#fff" size 26 xminimum 420
                textbutton ("Aguardando..." if waiting_keybind_action == "move_right" else "[key_label(get_keybind('move_right'))]") style "menu_item" selected False action [
                    SetVariable("waiting_keybind_action", "move_right"),
                    SetVariable("keybind_message", "")
                ]

            hbox:
                spacing 25
                xalign 0.5
                text "Lancar a bolinha:" color "#fff" size 26 xminimum 420
                textbutton ("Aguardando..." if waiting_keybind_action == "launch_ball" else "[key_label(get_keybind('launch_ball'))]") style "menu_item" selected False action [
                    SetVariable("waiting_keybind_action", "launch_ball"),
                    SetVariable("keybind_message", "")
                ]

            hbox:
                spacing 25
                xalign 0.5
                text "Usar powerup:" color "#fff" size 26 xminimum 420
                textbutton ("Aguardando..." if waiting_keybind_action == "use_powerup" else "[key_label(get_keybind('use_powerup'))]") style "menu_item" selected False action [
                    SetVariable("waiting_keybind_action", "use_powerup"),
                    SetVariable("keybind_message", "")
                ]

            hbox:
                spacing 25
                xalign 0.5
                text "Pausar jogo:" color "#fff" size 26 xminimum 420
                textbutton ("Aguardando..." if waiting_keybind_action == "pause" else "[key_label(get_keybind('pause'))]") style "menu_item" selected False action [
                    SetVariable("waiting_keybind_action", "pause"),
                    SetVariable("keybind_message", "")
                ]

            null height 16

            fixed:
                xfill True
                ysize 30
                if waiting_keybind_action is not None:
                    text "Pressione ESC para cancelar." size 20 color "#aaa" xalign 0.5 yalign 0.5

            hbox:
                spacing 20
                xalign 0.5
                textbutton "[('> ' if hovered_btn == 'reset' else '  ')]Resetar padrão" style "menu_item" selected False action [
                    Function(reset_keybinds),
                    SetVariable("waiting_keybind_action", None),
                    SetVariable("keybind_message", "Keybinds resetadas para o padrão.")
                ] hovered SetScreenVariable("hovered_btn", "reset") unhovered SetScreenVariable("hovered_btn", "")
                textbutton "[('> ' if hovered_btn == 'back' else '  ')]Back" style "menu_item" selected False action [
                    SetVariable("waiting_keybind_action", None),
                    SetVariable("keybind_message", ""),
                    Return("back")
                ] hovered SetScreenVariable("hovered_btn", "back") unhovered SetScreenVariable("hovered_btn", "")

    add KeyCapture()


# Tela de configuração de áudio.
# Objetivo: ajustar volumes de música e efeitos com retorno imediato.
# Variáveis de screen:
# - hovered_btn: botão sob cursor para destaque visual.
screen options_audio():
    tag menu
    modal True
    default hovered_btn = ""

    frame style "menu_frame" xsize menu_w ysize menu_h:
        vbox:
            spacing 22
            xalign 0.5
            yalign 0.5
            text "[rainbow_title('Audio')]" style "menu_title" size 40

            text "Music Volume" style "audio_label"
            bar value Preference("music volume") style "audio_volume_bar"

            text "Sound Volume" style "audio_label"
            bar value Preference("sound volume") style "audio_volume_bar"

            null height 10

            hbox:
                spacing 20
                textbutton "[('> ' if hovered_btn == 'mute' else '  ')][audio_mute_button_label()]" style "menu_item" action Function(toggle_all_audio_mute) hovered SetScreenVariable("hovered_btn", "mute") unhovered SetScreenVariable("hovered_btn", "")
                textbutton "[('> ' if hovered_btn == 'back' else '  ')]Back" style "menu_item" action Return("back") hovered SetScreenVariable("hovered_btn", "back") unhovered SetScreenVariable("hovered_btn", "")
