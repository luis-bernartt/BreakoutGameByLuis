# Loop do menu principal.
# menu_choice: ação retornada pela screen main_menu para rotear navegação.
# Fluxo: mantém o jogador no menu até escolher iniciar jogo, abrir telas auxiliares ou sair.
label main_menu:
    $ play_music("menu", loop=True, fadein=0.6, if_changed=True)
    while True:
        $ menu_choice = renpy.call_screen("main_menu")

        if menu_choice == "new_game":
            jump game_run

        elif menu_choice == "leaderboards":
            $ renpy.call_screen("leaderboards")

        elif menu_choice == "help":
            $ renpy.call_screen("help_screen")

        elif menu_choice == "options":
            jump options_root

        elif menu_choice == "quit":
            $ quit_confirmed = renpy.call_screen(
                "confirm_action_popup",
                title_text="Sair do jogo?",
            )
            if quit_confirmed:
                $ renpy.quit()

        else:
            return
