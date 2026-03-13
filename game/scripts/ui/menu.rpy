# Tela principal do menu inicial.
# Objetivo: centralizar entrada para nova partida e telas auxiliares.
# Variáveis de screen:
# - hovered_btn: botão sob cursor para destacar seleção.
# - new_game_clicked: dispara animação breve antes de retornar "new_game".
# Saída:
# - Retorna rota de navegação (new_game, leaderboards, help, options, quit).
screen main_menu():
    tag menu
    modal True
    default hovered_btn = ""
    default new_game_clicked = False
    frame style "menu_frame" xsize menu_w ysize menu_h xalign 0.5 yalign 0.5:
        fixed:
            xfill True
            yfill True

            vbox at truecenter:
                spacing 20
                xalign 0.5
                yalign 0.5
                text "[rainbow_title('Breakout')]" style "menu_title"

                if new_game_clicked:
                    timer 0.42 action Return("new_game")
                    text ">  New Game" style "menu_item_text" at new_game_blink
                else:
                    textbutton "[('> ' if hovered_btn == 'new_game' else '  ')]New Game" style "menu_item" action SetScreenVariable("new_game_clicked", True) hovered SetScreenVariable("hovered_btn", "new_game") unhovered SetScreenVariable("hovered_btn", "")
                textbutton "[('> ' if hovered_btn == 'leaderboards' else '  ')]Leaderboards" style "menu_item" action Return("leaderboards") hovered SetScreenVariable("hovered_btn", "leaderboards") unhovered SetScreenVariable("hovered_btn", "")
                textbutton "[('> ' if hovered_btn == 'help' else '  ')]Help" style "menu_item" action Return("help") hovered SetScreenVariable("hovered_btn", "help") unhovered SetScreenVariable("hovered_btn", "")
                textbutton "[('> ' if hovered_btn == 'options' else '  ')]Options" style "menu_item" action Return("options") hovered SetScreenVariable("hovered_btn", "options") unhovered SetScreenVariable("hovered_btn", "")
                textbutton "[('> ' if hovered_btn == 'quit' else '  ')]Quit" style "menu_item" action Return("quit") hovered SetScreenVariable("hovered_btn", "quit") unhovered SetScreenVariable("hovered_btn", "")


# Tela de leaderboard com paginação.
# Objetivo: exibir ranking sem sobrecarregar a leitura em listas longas.
# Variáveis de screen:
# - hovered_btn: botão sob cursor para destacar seleção.
# - leaderboard_page: índice da página atual do ranking.
# Saída:
# - Return("back") para retornar ao menu anterior.
screen leaderboards():
    tag menu
    modal True
    default hovered_btn = ""

    frame style "menu_frame" xsize menu_w ysize menu_h xalign 0.5 yalign 0.5:
        fixed:
            xfill True
            yfill True
            vbox at truecenter:
                spacing 18
                xalign 0.5
                yalign 0.3
                text "[rainbow_title('Leaderboards')]" style "menu_title"

                $ leaderboard = leaderboard_get()
                $ entries_per_page = 5
                $ total_pages = max(1, (len(leaderboard) + entries_per_page - 1) // entries_per_page)
                $ current_page = min(leaderboard_page, total_pages - 1)
                $ start_index = current_page * entries_per_page
                $ end_index = start_index + entries_per_page

                fixed:
                    xfill True
                    ysize 260

                    if not leaderboard:
                        text "Sem scores ainda." color "#fff" xalign 0.5 yalign 0.5
                    else:
                        vbox:
                            spacing 12
                            xalign 0.5
                            text "Pagina [current_page + 1] / [total_pages]" size 22 color "#aaa" xalign 0.5

                            for position, row in enumerate(leaderboard[start_index:end_index], start=start_index + 1):
                                text "[position]. [row['name']]  -  [row['score']]" color "#fff" xalign 0.5

                null height 10

                hbox:
                    xalign 0.5
                    spacing 30

                    fixed:
                        xsize 320
                        ysize 40
                        if leaderboard and current_page > 0:
                            textbutton "[('> ' if hovered_btn == 'prev' else '  ')]< Anterior" style "menu_item" action SetVariable("leaderboard_page", current_page - 1) xalign 0.0 hovered SetScreenVariable("hovered_btn", "prev") unhovered SetScreenVariable("hovered_btn", "")

                    fixed:
                        xsize 220
                        ysize 40
                        textbutton "[('> ' if hovered_btn == 'back' else '  ')]Back" style "menu_item" action [SetVariable("leaderboard_page", 0), Return("back")] xalign 0.5 hovered SetScreenVariable("hovered_btn", "back") unhovered SetScreenVariable("hovered_btn", "")

                    fixed:
                        xsize 320
                        ysize 40
                        if leaderboard and current_page < total_pages - 1:
                            textbutton "[('> ' if hovered_btn == 'next' else '  ')]Proxima >" style "menu_item" action SetVariable("leaderboard_page", current_page + 1) xalign 1.0 hovered SetScreenVariable("hovered_btn", "next") unhovered SetScreenVariable("hovered_btn", "")


# Tela de ajuda com múltiplas páginas de conteúdo.
# Objetivo: documentar comandos, HUD e powerups para onboarding.
# Variáveis de screen:
# - hovered_btn: botão sob cursor para destacar seleção.
# - help_page: página atual (comandos, indicadores, powerups).
# Saída:
# - Return("back") ao sair da ajuda.
screen help_screen():
    tag menu
    modal True
    default hovered_btn = ""

    frame style "menu_frame" xsize menu_w ysize menu_h xalign 0.5 yalign 0.5:
        fixed:
            xfill True
            yfill True
            vbox at truecenter:
                spacing 18
                xalign 0.5
                yalign 0.5

                text "[rainbow_title('Help')]" style "menu_title"

                fixed:
                    xfill True
                    ysize 390

                    if help_page == 0:
                        vbox:
                            spacing 12
                            xalign 0.5
                            text "Comandos" size 22 color "#aaa" xalign 0.5
                            text "Mover para a esquerda: [key_label(get_keybind('move_left'))]" color "#ddd" size 24
                            text "Mover para a direita: [key_label(get_keybind('move_right'))]" color "#ddd" size 24
                            text "Lancar a bolinha: [key_label(get_keybind('launch_ball'))]" color "#ddd" size 24
                            text "Usar powerup guardado: [key_label(get_keybind('use_powerup'))]" color "#ddd" size 24
                            text "Pausar/retomar: [key_label(get_keybind('pause'))]" color "#ddd" size 24

                    elif help_page == 1:
                        vbox:
                            spacing 12
                            xalign 0.5
                            text "Indicadores" size 22 color "#aaa" xalign 0.5

                            hbox:
                                spacing 20
                                add load_ui_frames("score", count=6, size=(36,36), native_size=(32,16)) fit "contain" xysize (36, 36)
                                text "Pontuacao atual." color "#ddd" size 24 yalign 0.5

                            hbox:
                                spacing 20
                                add load_ui_frames("heart", count=6, size=(32,30), native_size=(32,30)) fit "contain" xysize (36, 36)
                                text "Vidas restantes." color "#ddd" size 24 yalign 0.5

                            hbox:
                                spacing 20
                                add load_ui_frames("phase", count=6, size=(36,36), native_size=(32,16)) fit "contain" xysize (36, 36)
                                text "Fase atual." color "#ddd" size 24 yalign 0.5

                            hbox:
                                spacing 20
                                add load_ui_frames("speed", count=6, size=(36,36), native_size=(32,16)) fit "contain" xysize (36, 36)
                                text "Velocidade global." color "#ddd" size 24 yalign 0.5

                            hbox:
                                spacing 20
                                add load_ui_frames("stored", count=6, size=(36,36), native_size=(32,32)) fit "contain" xysize (36, 36)
                                text "Powerups guardados." color "#ddd" size 24 yalign 0.5

                            hbox:
                                spacing 20
                                add "breakout/ui/powerup_default.png" fit "contain" xysize (36, 36)
                                text "Icone padrao quando a fila esta vazia." color "#ddd" size 24 yalign 0.5

                    else:
                        vbox:
                            spacing 12
                            xalign 0.5
                            text "Powerups" size 22 color "#aaa" xalign 0.5

                            hbox:
                                spacing 20
                                add "breakout/powerups/multiball/0.png" fit "contain" xysize (32, 32)
                                text "Multiball: cria bolas extras." color "#ddd" size 24 yalign 0.5

                            hbox:
                                spacing 20
                                add "breakout/powerups/paddle/0.png" fit "contain" xysize (32, 32)
                                text "Paddle Grow: aumenta a paddle." color "#ddd" size 24 yalign 0.5

                            hbox:
                                spacing 20
                                add "breakout/powerups/speed/0.png" fit "contain" xysize (32, 32)
                                text "Game Speed Up: acelera o jogo." color "#ddd" size 24 yalign 0.5

                            hbox:
                                spacing 20
                                add "breakout/powerups/sticky/0.png" fit "contain" xysize (32, 32)
                                text "Sticky: proxima colisao pode prender a bola." color "#ddd" size 24 yalign 0.5

                            hbox:
                                spacing 20
                                add "breakout/powerups/life/0.png" fit "contain" xysize (32, 32)
                                text "Life: ganha uma vida extra." color "#ddd" size 24 yalign 0.5


                null height 8

                hbox:
                    xalign 0.5
                    spacing 30

                    fixed:
                        xsize 320
                        ysize 40
                        if help_page > 0:
                            textbutton "[('> ' if hovered_btn == 'prev' else '  ')]< Anterior" style "menu_item" action SetVariable("help_page", help_page - 1) xalign 0.0 hovered SetScreenVariable("hovered_btn", "prev") unhovered SetScreenVariable("hovered_btn", "")

                    fixed:
                        xsize 220
                        ysize 40
                        textbutton "[('> ' if hovered_btn == 'back' else '  ')]Back" style "menu_item" action [SetVariable("help_page", 0), Return("back")] xalign 0.5 hovered SetScreenVariable("hovered_btn", "back") unhovered SetScreenVariable("hovered_btn", "")

                    fixed:
                        xsize 320
                        ysize 40
                        if help_page < 2:
                            textbutton "[('> ' if hovered_btn == 'next' else '  ')]Proxima >" style "menu_item" action SetVariable("help_page", help_page + 1) xalign 1.0 hovered SetScreenVariable("hovered_btn", "next") unhovered SetScreenVariable("hovered_btn", "")


# Hub de opções do jogo.
# Objetivo: encaminhar para telas de keybinds e áudio.
# Variáveis de screen:
# - hovered_btn: botão sob cursor para destacar seleção.
# Saída:
# - Return("keybinds"), Return("audio") ou Return("back").
screen options_menu():
    tag menu
    modal True
    default hovered_btn = ""

    frame style "menu_frame" xsize menu_w ysize menu_h xalign 0.5 yalign 0.5:
        fixed:
            xfill True
            yfill True

            vbox at truecenter:
                spacing 20
                xalign 0.5
                yalign 0.5
                text "[rainbow_title('Options')]" style "menu_title"

                textbutton "[('> ' if hovered_btn == 'keybinds' else '  ')]Keybinds" style "menu_item" action Return("keybinds") hovered SetScreenVariable("hovered_btn", "keybinds") unhovered SetScreenVariable("hovered_btn", "")
                textbutton "[('> ' if hovered_btn == 'audio' else '  ')]Audio" style "menu_item" action Return("audio") hovered SetScreenVariable("hovered_btn", "audio") unhovered SetScreenVariable("hovered_btn", "")
                textbutton "[('> ' if hovered_btn == 'back' else '  ')]Back" style "menu_item" action Return("back") xalign 0.5 hovered SetScreenVariable("hovered_btn", "back") unhovered SetScreenVariable("hovered_btn", "")
