default persistent.leaderboard = []
default persistent.keybinds = {}

init -3 python:
    import renpy.exports as rpy

    """Utilitários de progresso persistente e leaderboard.

    Dados persistidos:
    - persistent.leaderboard: lista ordenada de pontuações altas.
    - persistent.keybinds: mapeamento de ações para teclas personalizadas.

    Responsabilidade:
    - Garantir inicialização segura de persistentes.
    - Fornecer API simples para leitura/escrita de ranking.
    """

    def get_default_keybinds():
        """Retorna o conjunto padrão de teclas do jogo.

        Returns:
            dict[str, str]: mapeamento ação -> tecla padrão.
        """
        return {
            "move_left": "a",
            "move_right": "d",
            "launch_ball": "space",
            "use_powerup": "e",
            "pause": "p",
        }

    def ensure_settings():
        """Garante que estruturas persistentes mínimas existam.

        Efeito colateral:
            Cria/normaliza `persistent.leaderboard` e `persistent.keybinds`
            quando necessário.
        """
        if not hasattr(persistent, "leaderboard") or persistent.leaderboard is None:
            persistent.leaderboard = []

        if not hasattr(persistent, "keybinds") or persistent.keybinds is None:
            persistent.keybinds = get_default_keybinds().copy()

        defaults = get_default_keybinds()
        for action_name, key_name in defaults.items():
            if action_name not in persistent.keybinds:
                persistent.keybinds[action_name] = key_name

    def leaderboard_get():
        """Retorna a lista atual de leaderboard em memória persistente."""
        ensure_settings()
        return persistent.leaderboard

    def leaderboard_add(player_name, score_value, limit=10):
        """Adiciona pontuação, ordena e limita a quantidade de entradas.

        player_name: nome do jogador (máx. 16 chars).
        score_value: valor numérico de pontos.
        limit: máximo de registros salvos.

        Regra de ordenação:
            Maior score primeiro (ordem decrescente).
        """
        ensure_settings()

        player_name = (player_name or "Player").strip()[:16]
        leaderboard = leaderboard_get()

        leaderboard.append({"name": player_name, "score": int(score_value)})
        leaderboard.sort(key=lambda row: row["score"], reverse=True)
        del leaderboard[limit:]

        rpy.save_persistent()

    ensure_settings()


default help_page = 0
default leaderboard_page = 0
