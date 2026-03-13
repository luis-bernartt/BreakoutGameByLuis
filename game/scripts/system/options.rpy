label options_root:
    while True:
        $ opt_choice = renpy.call_screen("options_menu")

        if opt_choice == "keybinds":
            $ renpy.call_screen("options_keybinds")
        elif opt_choice == "audio":
            $ renpy.call_screen("options_audio")
        else:
            jump main_menu
