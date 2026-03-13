default persistent.keybinds = {}

init -3 python:
    import renpy.exports as rpy

    """Gerenciamento de keybinds persistentes do jogador.

    Objetivo:
    - Ler, alterar, validar conflitos e restaurar atalhos de teclado.
    - Integrar fluxo de captura de teclas com a UI de opções.
    """

    def get_keybind(action_name):
        """Obtém a tecla vinculada a uma ação.

        Args:
            action_name: identificador lógico da ação de gameplay.

        Returns:
            Nome da tecla salva em persistente ou o valor padrão.
        """
        ensure_settings()
        return persistent.keybinds.get(action_name, get_default_keybinds()[action_name])

    def set_keybind(action_name, key_name):
        """Define e persiste uma nova tecla para uma ação.

        Args:
            action_name: ação a ser remapeada.
            key_name: nome interno da tecla escolhida.
        """
        ensure_settings()
        persistent.keybinds[action_name] = key_name
        rpy.save_persistent()

    def reset_keybinds():
        """Restaura todos os keybinds para o padrão do projeto."""
        persistent.keybinds = get_default_keybinds().copy()
        rpy.save_persistent()

    def key_label(key_name):
        """Converte nome interno da tecla para rótulo de UI.

        Exemplo: "return" -> "ENTER".
        """
        if isinstance(key_name, bytes):
            try:
                key_name = key_name.decode("utf-8")
            except Exception:
                key_name = str(key_name)

        key_name = str(key_name).strip().lower()

        labels = {
            "space": "SPACE",
            "return": "ENTER",
            "left": "LEFT",
            "right": "RIGHT",
            "up": "UP",
            "down": "DOWN",
            "rctrl": "RCTRL",
            "lctrl": "LCTRL",
            "rshift": "RSHIFT",
            "lshift": "LSHIFT",
            "escape": "ESC",
            "tab": "TAB",
            "backspace": "BACKSPACE",
        }
        return labels.get(key_name, key_name.upper())

    def keybind_in_use_by_other_action(action_name, key_name):
        """Detecta conflito de tecla entre ações.

        Returns:
            Nome da outra ação que já usa a tecla, ou None.
        """
        ensure_settings()

        for other_action, other_key in persistent.keybinds.items():
            if other_action != action_name and other_key == key_name:
                return other_action
        return None

    def action_label(action_name):
        """Retorna texto legível da ação para mensagens de UI."""
        labels = {
            "move_left": "Mover para a esquerda",
            "move_right": "Mover para a direita",
            "launch_ball": "Lançar a bolinha",
            "use_powerup": "Usar powerup",
            "pause": "Pausar jogo",
        }
        return labels.get(action_name, action_name)

    def capture_key_name(key_name):
        """Processa captura de tecla na tela de remapeamento.

        Fluxo resumido:
        1) Normaliza aliases (enter/esc/ctrl/shift etc.).
        2) Permite cancelamento com ESC.
        3) Valida conflito da tecla com outras ações.
        4) Persiste novo bind e escreve feedback para a tela.

        Variáveis de tela usadas:
        - waiting_keybind_action: ação aguardando nova tecla.
        - keybind_message: feedback textual para o jogador.
        """
        store = renpy.store

        if store.waiting_keybind_action is None:
            return

        if not key_name:
            return

        if isinstance(key_name, bytes):
            try:
                key_name = key_name.decode("utf-8")
            except Exception:
                key_name = str(key_name)

        key_name = str(key_name).lower().strip()

        key_aliases = {
            "kp enter": "return",
            "enter": "return",
            "return": "return",
            "esc": "escape",
            "right ctrl": "rctrl",
            "left ctrl": "lctrl",
            "right shift": "rshift",
            "left shift": "lshift",
            "spacebar": "space",
        }

        key_name = key_aliases.get(key_name, key_name)

        if key_name == "escape":
            store.waiting_keybind_action = None
            store.keybind_message = "Alteração cancelada."
            renpy.restart_interaction()
            return

        conflict = keybind_in_use_by_other_action(
            store.waiting_keybind_action,
            key_name
        )

        if conflict is not None:
            store.keybind_message = "A tecla [%s] já está em uso por: %s." % (
                key_label(key_name),
                action_label(conflict)
            )
            renpy.restart_interaction()
            return

        set_keybind(store.waiting_keybind_action, key_name)

        store.keybind_message = "%s alterado para [%s]." % (
            action_label(store.waiting_keybind_action),
            key_label(key_name)
        )
        store.waiting_keybind_action = None
        renpy.restart_interaction()


default waiting_keybind_action = None
default keybind_message = ""
