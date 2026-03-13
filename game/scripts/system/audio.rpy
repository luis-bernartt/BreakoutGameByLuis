init -3 python:
    import renpy.exports as rpy
    """Funções utilitárias de áudio.

    Responsabilidade:
    - Centralizar o mapeamento de nomes lógicos para arquivos de áudio.
    - Proteger chamadas de reprodução quando o arquivo não estiver disponível.

    Estruturas principais:
    - AUDIO_SFX: mapeia nome lógico para arquivo de efeito sonoro.
    - AUDIO_MUSIC: mapeia nome lógico para arquivo de trilha musical.
    """

    _LAST_AUDIO_VOLUMES = {
            "music": 1.0,
            "sfx": 1.0,
        }

    AUDIO_SFX = {
        "ball_launch": "audio/sfx/ball_launch.ogg",
        "paddle_hit": "audio/sfx/paddle_hit.ogg",
        "brick_hit": "audio/sfx/brick_hit.ogg",
        "brick_break": "audio/sfx/brick_break.ogg",
        "powerup_pickup": "audio/sfx/powerup_pickup.ogg",
        "powerup_use": "audio/sfx/powerup_use.ogg",
        "life_lost": "audio/sfx/life_lost.ogg",
        "phase_clear": "audio/sfx/phase_clear.ogg",
        "ui_click": "audio/sfx/ui_click.ogg",
        "game_over": "audio/sfx/game_over.ogg",
    }

    AUDIO_MUSIC = {
        "menu": "audio/music/menu_theme.ogg",
    }

    def _get_loadable_audio(path):
        """Valida se um caminho de áudio pode ser carregado.

        Args:
            path: caminho relativo do arquivo de áudio.

        Returns:
            O próprio caminho quando o arquivo existe e é carregável; caso
            contrário, None.
        """
        if not path:
            return None
        if rpy.loadable(path):
            return path
        return None

    def play_sfx(name):
        """Toca um efeito sonoro por nome lógico.

        Args:
            name: chave existente em AUDIO_SFX (ex.: "brick_hit").

        Efeito colateral:
            Envia o áudio para o canal de efeitos do Ren'Py.
        """
        path = _get_loadable_audio(AUDIO_SFX.get(name))
        if path:
            renpy.sound.play(path)

    def play_music(track, loop=True, fadein=0.5, fadeout=0.5, if_changed=True):
        """Toca música de fundo com controle de loop e transição.

        Args:
            track: chave de faixa em AUDIO_MUSIC.
            loop: mantém reprodução contínua quando True.
            fadein: duração (s) do fade-in inicial.
            fadeout: duração (s) do fade-out na troca de faixa.
            if_changed: evita reinício se a mesma faixa já estiver tocando.
        """
        path = _get_loadable_audio(AUDIO_MUSIC.get(track))
        if path:
            renpy.music.play(
                path,
                channel="music",
                loop=loop,
                fadein=fadein,
                fadeout=fadeout,
                if_changed=if_changed,
            )

    def stop_music(fadeout=0.5):
        """Interrompe a faixa atual no canal de música.

        Args:
            fadeout: duração (s) para saída suave do áudio.
        """
        renpy.music.stop(channel="music", fadeout=fadeout)

    def _get_mixer_volume(mixer_name, fallback=1.0):
        """Lê o volume de um mixer do Ren'Py com fallback seguro."""
        try:
            value = renpy.store._preferences.get_volume(mixer_name)
            return float(value)
        except Exception:
            return float(fallback)

    def _set_mixer_volume(mixer_name, value):
        """Define volume de um mixer em faixa válida [0.0, 1.0]."""
        safe_value = max(0.0, min(1.0, float(value)))
        try:
            renpy.store._preferences.set_volume(mixer_name, safe_value)
        except Exception:
            pass

    def is_audio_muted_all():
        """Retorna True quando música e efeitos estão mutados."""
        music_volume = _get_mixer_volume("music", 1.0)
        sfx_volume = _get_mixer_volume("sfx", 1.0)
        return music_volume <= 0.0001 and sfx_volume <= 0.0001

    def audio_mute_button_label():
        """Label do botão de áudio conforme estado atual."""
        return "Unmute All" if is_audio_muted_all() else "Mute All"

    def toggle_all_audio_mute():
        """Alterna mute geral preservando volumes anteriores para restore."""
        global _LAST_AUDIO_VOLUMES

        current_music = _get_mixer_volume("music", 1.0)
        current_sfx = _get_mixer_volume("sfx", 1.0)

        if is_audio_muted_all():
            restore_music = _LAST_AUDIO_VOLUMES.get("music", 1.0)
            restore_sfx = _LAST_AUDIO_VOLUMES.get("sfx", 1.0)

            _set_mixer_volume("music", restore_music if restore_music > 0.0 else 1.0)
            _set_mixer_volume("sfx", restore_sfx if restore_sfx > 0.0 else 1.0)
        else:
            if current_music > 0.0:
                _LAST_AUDIO_VOLUMES["music"] = current_music
            if current_sfx > 0.0:
                _LAST_AUDIO_VOLUMES["sfx"] = current_sfx

            _set_mixer_volume("music", 0.0)
            _set_mixer_volume("sfx", 0.0)

        renpy.restart_interaction()
