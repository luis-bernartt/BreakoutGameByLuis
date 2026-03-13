# Tela host do runtime.
# game: instância ativa de BreakoutGame renderizada no loop.
# Comportamento: modal para capturar foco da interação durante gameplay.
screen runtime(game):
    modal True
    add game


# Entrada principal para iniciar a execução do jogo.
# Fluxo: apenas redireciona para game_run.
label start:
    jump game_run

# Controlador principal da partida.
# game: objeto de estado da run atual.
# goto: rota de saída para labels de navegação (ex.: main_menu).
# Responsabilidade: orquestrar transições entre runtime, pausa, game over e menus.
label game_run:
    python:
        game = BreakoutGame()
        goto = None
        while True:
            result = renpy.call_screen("runtime", game=game)
            if result == "main_menu":
                goto = "main_menu"
                break
            elif result == "pause":
                while True:
                    game.is_paused = True
                    choice = renpy.call_screen("pause_menu", game=game)

                    if choice == "resume":
                        game.is_paused = False
                        play_sfx("ui_click")
                        break

                    elif choice == "help":
                        renpy.call_screen("help_screen")

                    elif choice == "options":
                        while True:
                            opt_choice = renpy.call_screen("options_menu")
                            if opt_choice == "keybinds":
                                renpy.call_screen("options_keybinds")
                            elif opt_choice == "audio":
                                renpy.call_screen("options_audio")
                            else:
                                break

                    elif choice == "main_menu":
                        if game.score > 0:
                            go_to_menu = renpy.call_screen(
                                "confirm_action_popup",
                                title_text="Voltar ao menu?",
                                body_text="A partida atual sera encerrada.",
                                confirm_text="Sim, sair",
                                cancel_text="Continuar"
                            )
                            if go_to_menu:
                                game.is_paused = False
                                goto = "main_menu"
                                break
                        else:
                            game.is_paused = False
                            goto = "main_menu"
                            break
                    else:
                        game.is_paused = False
                        play_sfx("ui_click")
                        break

                if goto == "main_menu":
                    break

                continue
            else:
                break
    if goto == "main_menu":
        jump main_menu

    $ final_score = game.score
    $ player_name = ""
    $ player_name = renpy.call_screen("name_entry", final_score=final_score)
    if player_name is not None:
        $ leaderboard_add(player_name, final_score)

    $ choice = renpy.call_screen("game_over", final_score=final_score)
    if choice == "play_again":
        jump game_run
    elif choice == "leaderboards":
        call screen leaderboards
        jump main_menu
    elif choice == "help":
        call screen help_screen
        jump main_menu
    elif choice == "options":
        jump options_root
    elif choice == "main_menu":
        jump main_menu
