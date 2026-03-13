# Tela de entrada de nome após fim da partida.
# Objetivo: coletar nome para leaderboard sem travar fluxo caso jogador pule.
# Entradas:
# - final_score: pontuação final exibida no cabeçalho.
# Variáveis de screen:
# - hovered_btn: id do botão em hover para marcador visual.
# Saída:
# - Return(player_name) ao confirmar envio.
# - Return(None) ao pular cadastro.
screen name_entry(final_score):
    tag menu
    modal True

    default hovered_btn = ""

    frame style "menu_frame" xsize menu_w ysize menu_h:
        vbox:
            spacing 20
            xalign 0.5
            yalign 0.5
            text "[rainbow_title('Fim!')]" style "menu_title"
            text "[rainbow_title('Score: {}'.format(final_score))]" style "menu_title" size 72

            text "Digite seu nome para o leaderboard:" style "menu_item" xalign 0.5
            input value VariableInputValue("player_name") length 16 xmaximum 300 xalign 0.5

            hbox:
                spacing 20
                xalign 0.5
                textbutton "[('> ' if hovered_btn == 'send' else '  ')]Enviar" style "menu_item" action Return(player_name) hovered SetScreenVariable("hovered_btn", "send") unhovered SetScreenVariable("hovered_btn", "")
                textbutton "[('> ' if hovered_btn == 'skip' else '  ')]Pular" style "menu_item" action Return(None) hovered SetScreenVariable("hovered_btn", "skip") unhovered SetScreenVariable("hovered_btn", "")


# Tela de ações após game over.
# Objetivo: definir próximo passo após derrota/fim de rodada.
# Entradas:
# - final_score: pontuação da rodada encerrada.
# Variáveis de screen:
# - hovered_btn: id do botão em hover para marcador visual.
# Saída:
# - Retorna chave de navegação (play_again, leaderboards, help, options, main_menu).
screen game_over(final_score):
    tag menu
    modal True
    default hovered_btn = ""

    frame style "menu_frame" xsize menu_w ysize menu_h:
        vbox:
            spacing 20
            xalign 0.5
            yalign 0.5
            text "[rainbow_title('Fim!')]" style "menu_title"
            text "[rainbow_title('Score: {}'.format(final_score))]" style "menu_title" size 72

            textbutton "[('> ' if hovered_btn == 'play_again' else '  ')]Play again" style "menu_item" action Return("play_again") hovered SetScreenVariable("hovered_btn", "play_again") unhovered SetScreenVariable("hovered_btn", "")
            textbutton "[('> ' if hovered_btn == 'leaderboards' else '  ')]Leaderboards" style "menu_item" action Return("leaderboards") hovered SetScreenVariable("hovered_btn", "leaderboards") unhovered SetScreenVariable("hovered_btn", "")
            textbutton "[('> ' if hovered_btn == 'help' else '  ')]Help" style "menu_item" action Return("help") hovered SetScreenVariable("hovered_btn", "help") unhovered SetScreenVariable("hovered_btn", "")
            textbutton "[('> ' if hovered_btn == 'options' else '  ')]Options" style "menu_item" action Return("options") hovered SetScreenVariable("hovered_btn", "options") unhovered SetScreenVariable("hovered_btn", "")
            textbutton "[('> ' if hovered_btn == 'main_menu' else '  ')]Main Menu" style "menu_item" action Return("main_menu") hovered SetScreenVariable("hovered_btn", "main_menu") unhovered SetScreenVariable("hovered_btn", "")


# Tela de pausa em overlay sobre o jogo.
# Objetivo: congelar interação do gameplay e oferecer rotas rápidas de navegação.
# Entradas:
# - game: displayable da partida renderizado ao fundo.
# Variáveis de screen:
# - hovered_btn: id do botão em hover para marcador visual.
# Saída:
# - Retorna chave de ação (resume, help, options, main_menu).
screen pause_menu(game):
    tag menu
    modal True
    default hovered_btn = ""

    key "K_ESCAPE" action Return("resume")
    key get_keybind('pause') action Return("resume")

    add game

    frame style "menu_frame" background Solid("#4b3f63b4") xsize menu_w ysize menu_h:
        vbox:
            spacing 20
            xalign 0.5
            yalign 0.5
            text "[rainbow_title('Pausado')]" style "menu_title"

            textbutton "[('> ' if hovered_btn == 'resume' else '  ')]Continuar" style "menu_item" action Return("resume") hovered SetScreenVariable("hovered_btn", "resume") unhovered SetScreenVariable("hovered_btn", "")
            textbutton "[('> ' if hovered_btn == 'help' else '  ')]Help" style "menu_item" action Return("help") hovered SetScreenVariable("hovered_btn", "help") unhovered SetScreenVariable("hovered_btn", "")
            textbutton "[('> ' if hovered_btn == 'options' else '  ')]Options" style "menu_item" action Return("options") hovered SetScreenVariable("hovered_btn", "options") unhovered SetScreenVariable("hovered_btn", "")
            textbutton "[('> ' if hovered_btn == 'main_menu' else '  ')]Main Menu" style "menu_item" action Return("main_menu") hovered SetScreenVariable("hovered_btn", "main_menu") unhovered SetScreenVariable("hovered_btn", "")
