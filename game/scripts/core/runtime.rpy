init -1 python:
    import math
    import random
    import pygame

    import renpy.exports as rpy
    from renpy.display.image import Solid
    from renpy.text.text import Text
    from renpy.display.core import Displayable
    from renpy.display.render import Render
    from renpy.display.transform import Transform

    class BreakoutGame(Displayable):
        """Displayable principal do jogo Breakout.

        paddle: raquete do jogador.
        balls/bricks/powerups: entidades ativas da partida.
        stored_powerups: fila de powerups guardados para uso manual.
        score/lives/max_lives: progresso e sobrevivência do jogador.
        current_phase: índice da fase usada na geração procedural.
        is_game_over/player_won/has_finished_interaction: flags de fim de rodada.
        is_paused: trava atualização e entrada durante pausa.
        life_flash_timer/life_flash_duration: overlay de dano por perda de vida.
        last_render_time: referência para cálculo de delta time.
        game_speed: multiplicador global de velocidade.

        Ciclo de vida:
        - __init__: monta estado base, assets e fase inicial.
        - render: calcula dt, atualiza simulação e desenha o frame.
        - event: processa teclado e controla entrada de gameplay.
        """
        def __init__(self, **kwargs):
            super(BreakoutGame, self).__init__(**kwargs)

            self.paddle = Paddle()
            self.max_lives = 3
            self.lives = 3
            self.score = 0

            self.is_moving_left = False
            self.is_moving_right = False

            self.balls = []
            self.powerups = []
            self.stored_powerups = []

            self.is_game_over = False
            self.player_won = False
            self.has_finished_interaction = False

            self.is_paused = False

            self.life_flash_timer = 0.0
            self.life_flash_duration = 0.28

            self.last_render_time = None
            self.game_speed = 1.0

            def _img(path, fallback_color="#fff", size=(64, 64)):
                """Carrega imagem com fallback de segurança.

                Args:
                    path: caminho relativo do asset.
                    fallback_color: cor usada se o arquivo não existir.
                    size: tamanho do sólido fallback.

                Returns:
                    Displayable válido para uso em renderização.
                """
                try:
                    return rpy.displayable(path)
                except Exception:
                    return Solid(fallback_color, xysize=size)

            self.paddle_imgs = [
                _img("breakout/paddle/1.png"),
                _img("breakout/paddle/2.png"),
                _img("breakout/paddle/3.png"),
                _img("breakout/paddle/4.png"),
            ]

            self.ball_img = _img("breakout/ball/1.png")

            self.brick_imgs = {
                "green": {
                    1: _img("breakout/bricks/green/1.png"),
                },
                "blue": {
                    1: _img("breakout/bricks/blue/1.png"),
                    2: _img("breakout/bricks/blue/2.png"),
                },
                "red": {
                    1: _img("breakout/bricks/red/1.png"),
                    2: _img("breakout/bricks/red/2.png"),
                    3: _img("breakout/bricks/red/3.png"),
                },
            }

            self.ball_native_size = (16, 16)

            self.brick_native_sizes = {
                1: (64, 32),
                2: (64, 32),
                3: (64, 32),
            }

            self.powerup_icon_size = (28, 28)

            self.powerup_frames = {
                "multiball": load_powerup_frames("multiball", 6, size=self.powerup_icon_size, native_size=self.powerup_icon_size),
                "speed": load_powerup_frames("speed", 6, size=self.powerup_icon_size, native_size=self.powerup_icon_size),
                "paddle": load_powerup_frames("paddle", 6, size=self.powerup_icon_size, native_size=self.powerup_icon_size),
                "sticky": load_powerup_frames("sticky", 6, size=self.powerup_icon_size, native_size=self.powerup_icon_size),
                "extra_life": load_powerup_frames("life", 6, size=self.powerup_icon_size, native_size=self.powerup_icon_size),
            }

            self.ui_imgs = {
                "heart": load_ui_frames("heart", count=6, size=(32,30), native_size=(32,30), fallback_color="#ff4d4d"),
                "score": load_ui_frames("score", count=6, size=(32,16), native_size=(32,16), fallback_color="#ffd24d"),
                "phase": load_ui_frames("phase", count=6, size=(32,16), native_size=(32,16), fallback_color="#4da6ff"),
                "speed": load_ui_frames("speed", count=6, size=(32,16), native_size=(32,16), fallback_color="#ffffff"),
                "stored": load_ui_frames("stored", count=6, size=(32,32), native_size=(32,32), fallback_color="#b366ff"),
                "powerup_default": _img("breakout/ui/powerup_default.png", "#66ff99", (32,32)),
            }

            self.current_phase = 0
            self.reset_level()

        def _is_bound_key(self, ev_key, action_name):
            """Valida se a tecla do evento corresponde à ação configurada.

            Args:
                ev_key: keycode recebido do pygame.
                action_name: ação lógica (ex.: move_left, pause).

            Returns:
                True quando a tecla do evento corresponde ao bind da ação.
            """
            key_name = get_keybind(action_name)

            if isinstance(key_name, bytes):
                try:
                    key_name = key_name.decode("utf-8")
                except Exception:
                    key_name = str(key_name)

            key_name = str(key_name).lower().strip()

            special_map = {
                "space": pygame.K_SPACE,
                "return": pygame.K_RETURN,
                "left": pygame.K_LEFT,
                "right": pygame.K_RIGHT,
                "up": pygame.K_UP,
                "down": pygame.K_DOWN,
                "rctrl": pygame.K_RCTRL,
                "lctrl": pygame.K_LCTRL,
                "rshift": pygame.K_RSHIFT,
                "lshift": pygame.K_LSHIFT,
                "escape": pygame.K_ESCAPE,
                "tab": pygame.K_TAB,
                "backspace": pygame.K_BACKSPACE,
            }

            if key_name in special_map:
                return ev_key == special_map[key_name]

            try:
                key_check = pygame.key.name(ev_key)
                if isinstance(key_check, bytes):
                    key_check = key_check.decode("utf-8")
                return str(key_check).lower() == key_name
            except Exception:
                return False

        def _powerup_display_name(self, kind):
            """Converte identificador interno de powerup para nome amigável.

            Args:
                kind: id interno do efeito.

            Returns:
                String pronta para exibição no HUD.
            """
            names = {
                "game_speed_up": "Game Speed Up",
                "sticky": "Sticky",
                "multiball": "Multiball",
                "paddle_grow": "Paddle Grow",
                "extra_life": "Extra Life",
            }
            return names.get(kind, kind)

        def _get_next_powerup_name(self):
            """Retorna o nome do próximo powerup guardado.

            Returns:
                Nome amigável do primeiro item da fila ou "None" quando vazia.
            """
            if not self.stored_powerups:
                return "None"
            return self._powerup_display_name(self.stored_powerups[0])

        def _get_next_powerup_icon(self):
            """Retorna o ícone do próximo powerup guardado para o HUD.

            Returns:
                Displayable estático/animado associado ao próximo item da fila.
            """
            if not self.stored_powerups:
                return self.ui_imgs["powerup_default"]

            next_kind = self.stored_powerups[0]

            if next_kind == "game_speed_up":
                frames = self.powerup_frames["speed"]
            elif next_kind == "sticky":
                frames = self.powerup_frames["sticky"]
            elif next_kind == "multiball":
                frames = self.powerup_frames["multiball"]
            elif next_kind == "paddle_grow":
                frames = self.powerup_frames["paddle"]
            elif next_kind == "extra_life":
                frames = self.powerup_frames["extra_life"]
            else:
                return self.ui_imgs["powerup_default"]

            if frames:
                return frames[0]

            return self.ui_imgs["powerup_default"]

        def _activate_next_stored_powerup(self):
            """Ativa o primeiro powerup da fila de armazenamento.

            Regras:
            - Não faz nada em game over.
            - Não faz nada quando não há item armazenado.
            """
            if self.is_game_over:
                return
            if not self.stored_powerups:
                return
            kind = self.stored_powerups.pop(0)
            self.apply_powerup(kind)

        def _draw_hud_item(self, render_out, icon, value_text, x, y, st, at, icon_box=(32, 32), src_size=None, text_size=24, gap=10):
            """Desenha um item de HUD (ícone + texto opcional).

            Args:
                render_out: alvo de renderização do frame.
                icon: displayable do ícone.
                value_text: texto associado (pode ser None).
                x/y: posição base na tela.
                icon_box: caixa de ajuste do ícone.
                src_size: tamanho nativo usado para ajuste proporcional.
                text_size: tamanho de fonte do valor.
                gap: espaçamento entre ícone e texto.
            """
            src_w, src_h = src_size if src_size is not None else icon_box

            if hasattr(icon, "current"):
                icon_to_draw = icon.current()
            else:
                icon_to_draw = icon

            icon_render, off_x, off_y, _, _ = render_fitted(
                icon_to_draw,
                icon_box[0],
                icon_box[1],
                src_w,
                src_h,
                st,
                at
            )
            render_out.blit(icon_render, (x + off_x, y + off_y))

            if value_text not in (None, ""):
                text_render = rpy.render(
                    Text(str(value_text), size=text_size, color="#ffffff"),
                    500, 60, st, at
                )
                text_x = x + icon_box[0] + gap
                text_y = y + int((icon_box[1] - text_size) * 0.5)
                render_out.blit(text_render, (text_x, text_y))

        def _draw_lives_hearts(self, render_out, x, y, st, at, total_hearts=3, spacing=8, icon_box=(32, 30)):
            """Desenha os corações correspondentes às vidas restantes.

            Args:
                total_hearts: quantidade máxima visual de slots.
                spacing: distância horizontal entre ícones.
            """
            src_w, src_h = icon_box

            for i in range(total_hearts):
                if i >= self.lives:
                    continue

                icon = self.ui_imgs["heart"]
                if hasattr(icon, "current"):
                    icon = icon.current()

                icon_render, off_x, off_y, _, _ = render_fitted(
                    icon,
                    icon_box[0],
                    icon_box[1],
                    src_w,
                    src_h,
                    st,
                    at
                )
                render_out.blit(
                    icon_render,
                    (x + i * (icon_box[0] + spacing) + off_x, y + off_y)
                )

        def get_current_phase_config(self):
            """Calcula limites de distribuição de tijolos por fase.

            Returns:
                Dict com tetos de tijolos verdes, azuis e vermelhos.
            """
            phase_index = self.current_phase

            green = min((18 + phase_index * 2) * 2, 180)
            blue = min((8 + phase_index * 2) * 2, 120)
            red = min((4 + phase_index * 1) * 2, 70)

            return {
                "green": green,
                "blue": blue,
                "red": red,
            }

        def generate_triangle_pattern(self, rows=6, cols=11):
            """Gera matriz de ocupação em formato de triângulo.

            Returns:
                Lista 2D com 1 (ocupado) e 0 (vazio).
            """
            pattern = []
            center = cols // 2

            for r in range(rows):
                spread = int((float(r) / max(1, rows - 1)) * center)
                row = []
                for c in range(cols):
                    row.append(1 if (center - spread) <= c <= (center + spread) else 0)
                pattern.append(row)

            return pattern

        def generate_diamond_pattern(self, rows=7, cols=11):
            """Gera matriz de ocupação em formato de losango."""
            pattern = []
            center_r = rows // 2
            center_c = cols // 2
            max_dist = min(center_r, center_c)

            for r in range(rows):
                row = []
                for c in range(cols):
                    dist = abs(r - center_r) + abs(c - center_c)
                    row.append(1 if dist <= max_dist else 0)
                pattern.append(row)

            return pattern

        def generate_symmetric_random_pattern(self, rows=7, cols=11, fill_chance=0.72):
            """Gera matriz aleatória espelhada para layout equilibrado.

            Args:
                fill_chance: probabilidade de ocupar cada célula da metade-base.
            """
            pattern = []
            half = (cols + 1) // 2

            for r in range(rows):
                left = []
                for _ in range(half):
                    left.append(1 if random.random() < fill_chance else 0)

                if cols % 2 == 0:
                    row = left + left[::-1]
                else:
                    row = left + left[:-1][::-1]

                pattern.append(row)

            return pattern

        def choose_shape_pattern(self):
            """Escolhe tipo de padrão e gera matriz de layout da fase.

            Returns:
                Tupla (nome_do_padrão, matriz_de_ocupação).
            """
            extra = min(self.current_phase // 2, 10)

            rows = 9 + extra
            cols = 17 + extra * 2

            roll = random.random()

            if roll < 0.34:
                return "diamond", self.generate_diamond_pattern(rows, cols)
            elif roll < 0.67:
                return "triangle", self.generate_triangle_pattern(rows, cols)
            else:
                return "symmetric_random", self.generate_symmetric_random_pattern(rows, cols, 0.72)

        def get_shape_cells(self, pattern):
            """Extrai coordenadas ativas de uma matriz de ocupação.

            Returns:
                Lista de tuplas (linha, coluna) onde há valor 1.
            """
            cells = []
            for row_idx, row in enumerate(pattern):
                for col_idx, value in enumerate(row):
                    if value:
                        cells.append((row_idx, col_idx))
            return cells

        def sort_cells_center_first(self, cells, rows, cols):
            """Ordena células pela distância ao centro do padrão.

            Uso:
                Prioriza preenchimento do centro para fora.
            """
            center_r = (rows - 1) / 2.0
            center_c = (cols - 1) / 2.0

            return sorted(
                cells,
                key=lambda rc: abs(rc[0] - center_r) + abs(rc[1] - center_c)
            )

        def build_priority_brick_pool(self, green_limit, blue_limit, red_limit):
            """Monta pool de tijolos por prioridade de resistência/cor.

            Returns:
                Lista de tuplas (hp, família_de_cor).
            """
            pool = []
            pool.extend([(3, "red")] * red_limit)
            pool.extend([(2, "blue")] * blue_limit)
            pool.extend([(1, "green")] * green_limit)
            return pool

        def reset_level(self):
            """Reconstrói fase atual e reinicializa entidades de nível.

            Efeito colateral:
                Recria lista de tijolos/powerups e gera nova bola inicial.
            """
            self.bricks = []
            self.powerups = []

            gap_x = 0
            gap_y = 0
            top_y = 90

            _, pattern = self.choose_shape_pattern()

            rows = len(pattern)
            cols = max(len(row) for row in pattern)

            brick_w = 64
            brick_h = 32

            total_row_w = cols * brick_w + (cols - 1) * gap_x
            start_x = int((SCREEN_W - total_row_w) * 0.5)

            shape_cells = self.get_shape_cells(pattern)

            if not shape_cells:
                shape_cells = [(0, 0)]

            shape_cells = self.sort_cells_center_first(shape_cells, rows, cols)

            config = self.get_current_phase_config()
            green_limit = config["green"]
            blue_limit = config["blue"]
            red_limit = config["red"]

            type_pool = self.build_priority_brick_pool(green_limit, blue_limit, red_limit)

            usable_count = min(len(shape_cells), len(type_pool))

            chosen_cells = shape_cells[:usable_count]
            chosen_types = type_pool[:usable_count]

            for (row_idx, col_idx), (hp, color_family) in zip(chosen_cells, chosen_types):
                x = start_x + col_idx * (brick_w + gap_x)
                y = top_y + row_idx * (brick_h + gap_y)

                if x + brick_w < 0 or x > SCREEN_W:
                    continue
                if y + brick_h < 0 or y > SCREEN_H * 0.55:
                    continue

                self.bricks.append(
                    Brick(x, y, brick_w, brick_h, hp=hp, color_family=color_family)
                )

            if not self.bricks:
                self.bricks.append(Brick(start_x, top_y, brick_w, brick_h, hp=1, color_family="green"))

            self.spawn_single_ball(stuck=True)

        def spawn_single_ball(self, stuck=False):
            """Cria uma única bola, opcionalmente presa à raquete.

            Args:
                stuck: quando True, a bola nasce acoplada à raquete.
            """
            ball = Ball(self.paddle.x + self.paddle.width / 2, self.paddle.y - 16, 0, -380)
            ball.is_stuck_to_paddle = stuck
            self.balls = [ball]

        def spawn_multiball(self):
            """Cria bolas extras com ângulos divergentes.

            Requisito:
                Deve existir ao menos uma bola ativa.
            """
            if not self.balls:
                return

            base_ball = self.balls[0]
            for angle in (-0.6, 0.6):
                speed = 380.0 * base_ball.speed_multiplier
                new_ball = Ball(
                    base_ball.x,
                    base_ball.y,
                    math.sin(angle) * speed,
                    -abs(math.cos(angle) * speed)
                )
                new_ball.speed_multiplier = base_ball.speed_multiplier
                self.balls.append(new_ball)

        def spawn_powerup(self, x, y, color_family="green"):
            """Tenta gerar um powerup aleatório na posição informada.

            Args:
                x/y: posição de origem (normalmente centro do tijolo destruído).
                color_family: cor do tijolo destruído (green, blue, red).
            """
            if random.random() > 0.99:
                return

            possible_kinds = ["multiball", "game_speed_up", "sticky"]

            if self.paddle.level < 3:
                possible_kinds.append("paddle_grow")

            if color_family == "red" and self.lives < self.max_lives:
                possible_kinds.append("extra_life")

            kind = random.choice(possible_kinds)

            if kind == "multiball":
                sprite = AnimatedSprite(self.powerup_frames["multiball"], fps=12)
            elif kind == "paddle_grow":
                sprite = AnimatedSprite(self.powerup_frames["paddle"], fps=12)
            elif kind == "game_speed_up":
                sprite = AnimatedSprite(self.powerup_frames["speed"], fps=12)
            elif kind == "extra_life":
                sprite = AnimatedSprite(self.powerup_frames["extra_life"], fps=12)
            else:
                sprite = AnimatedSprite(self.powerup_frames["sticky"], fps=12)

            self.powerups.append(PowerUp(kind, x - 14, y - 14, sprite))

        def apply_powerup(self, kind):
            """Aplica o efeito do powerup conforme seu tipo.

            Efeitos possíveis:
                multiball, paddle_grow, game_speed_up, sticky.
            """
            if kind == "multiball":
                self.spawn_multiball()
                self.score += 250
                play_sfx("powerup_use")
                return

            if kind == "paddle_grow":
                grew = self.paddle.grow_one_level()
                if grew:
                    self.paddle.trigger_blink()
                    self.score += 120
                else:
                    self.score += 40
                play_sfx("powerup_use")
                return

            if kind == "game_speed_up":
                self.game_speed = clamp_value(self.game_speed * 1.12, 0.85, 1.80)
                self.score += 140
                play_sfx("powerup_use")
                return

            if kind == "sticky":
                self.paddle.is_sticky = True
                self.paddle.sticky_used_once = False
                self.score += 160
                play_sfx("powerup_use")
                return

            if kind == "extra_life":
                if self.lives < self.max_lives:
                    self.lives += 1
                self.score += 200
                play_sfx("powerup_use")
                return

        def _resolve_ball_paddle_collision(self, ball):
            """Resolve colisão bola-raquete, incluindo comportamento sticky."""
            paddle_rect = self.paddle.rect()
            ball_rect = ball.rect()
            radius = ball.radius

            def bounce_from_top(impact_x):
                """Calcula vetor de rebate com base no ponto de impacto."""
                ball.y = self.paddle.y - radius - 1

                hit_ratio = (impact_x - (self.paddle.x + self.paddle.width * 0.5)) / (self.paddle.width * 0.5)
                hit_ratio = clamp_value(hit_ratio, -1.0, 1.0)

                angle = hit_ratio * 1.05
                speed = 380.0 * ball.speed_multiplier

                ball.vel_x = math.sin(angle) * speed
                ball.vel_y = -abs(math.cos(angle) * speed)
                play_sfx("paddle_hit")

                if self.paddle.is_sticky and not self.paddle.sticky_used_once:
                    ball.is_stuck_to_paddle = True
                    self.paddle.sticky_used_once = True

            prev_bottom = ball.prev_y + radius
            curr_bottom = ball.y + radius
            paddle_top = self.paddle.y

            crossed_top = (
                ball.vel_y > 0 and
                prev_bottom <= paddle_top and
                curr_bottom >= paddle_top
            )

            if crossed_top:
                travel_y = curr_bottom - prev_bottom
                if abs(travel_y) > 1e-6:
                    t = (paddle_top - prev_bottom) / travel_y
                    t = clamp_value(t, 0.0, 1.0)
                else:
                    t = 1.0

                impact_x = ball.prev_x + (ball.x - ball.prev_x) * t

                if (self.paddle.x - radius) <= impact_x <= (self.paddle.x + self.paddle.width + radius):
                    bounce_from_top(impact_x)
                    return

            if not ball_rect.colliderect(paddle_rect):
                return

            dx_left = abs(ball_rect.right - paddle_rect.left)
            dx_right = abs(paddle_rect.right - ball_rect.left)
            dy_top = abs(ball_rect.bottom - paddle_rect.top)
            dy_bottom = abs(paddle_rect.bottom - ball_rect.top)
            min_penetration = min(dx_left, dx_right, dy_top, dy_bottom)

            if min_penetration == dy_top and ball.vel_y >= 0:
                bounce_from_top(ball.x)
                return

            if min_penetration == dx_left:
                ball.x = paddle_rect.left - radius - 1
                ball.vel_x = -abs(ball.vel_x if abs(ball.vel_x) > 1e-6 else 220.0)
                return

            if min_penetration == dx_right:
                ball.x = paddle_rect.right + radius + 1
                ball.vel_x = abs(ball.vel_x if abs(ball.vel_x) > 1e-6 else 220.0)
                return

            if min_penetration == dy_bottom:
                ball.y = paddle_rect.bottom + radius + 1
                ball.vel_y = abs(ball.vel_y if abs(ball.vel_y) > 1e-6 else 220.0)
                return

        def _resolve_ball_brick_collision(self, ball):
            """Resolve colisão da bola com tijolos e rebate no eixo correto.

            Regra:
                Aplica colisão apenas no primeiro tijolo atingido por frame.
            """
            ball_rect = ball.rect()

            for brick in list(self.bricks):
                brick_rect = brick.rect()
                if ball_rect.colliderect(brick_rect):
                    self.score += int(10 * self.game_speed)
                    brick.hp -= 1
                    play_sfx("brick_hit")

                    if brick.hp <= 0:
                        self.bricks.remove(brick)
                        self.score += int(40 * self.game_speed)
                        play_sfx("brick_break")
                        self.spawn_powerup(brick.x + brick.width / 2, brick.y + brick.height / 2, brick.color_family)

                    dx_left = abs(ball_rect.right - brick_rect.left)
                    dx_right = abs(brick_rect.right - ball_rect.left)
                    dy_top = abs(ball_rect.bottom - brick_rect.top)
                    dy_bottom = abs(brick_rect.bottom - ball_rect.top)
                    min_penetration = min(dx_left, dx_right, dy_top, dy_bottom)

                    if min_penetration in (dx_left, dx_right):
                        ball.vel_x *= -1
                    else:
                        ball.vel_y *= -1
                    return

        def _pause_menu_is_open(self):
            """Indica se a screen de pausa está aberta na pilha atual.

            Returns:
                True quando pause_menu está ativa; False caso contrário.
            """
            try:
                return rpy.get_screen("pause_menu") is not None
            except Exception:
                return False

        def _update(self, dt):
            """Atualiza simulação (física, pontuação, fase e powerups).

            Args:
                dt: delta de tempo do frame em segundos.

            Observação:
                Ignora atualização quando jogo está pausado ou em game over.
            """
            if self.life_flash_timer > 0.0:
                self.life_flash_timer = max(0.0, self.life_flash_timer - dt)

            if self.is_game_over:
                return

            if self.is_paused or self._pause_menu_is_open():
                return

            self.paddle.update_blink(dt)

            for icon in self.ui_imgs.values():
                if isinstance(icon, AnimatedSprite):
                    icon.update(dt)

            gdt = dt * self.game_speed

            direction_x = (1 if self.is_moving_right else 0) - (1 if self.is_moving_left else 0)
            if direction_x != 0:
                self.paddle.move(direction_x, gdt)

            for ball in list(self.balls):
                ball.update(gdt, paddle=self.paddle)
                self._resolve_ball_paddle_collision(ball)
                self._resolve_ball_brick_collision(ball)

                if ball.y - ball.radius > SCREEN_H:
                    if ball in self.balls:
                        self.balls.remove(ball)

            if not self.balls:
                self.lives -= 1
                self.game_speed = 1.0
                self.life_flash_timer = self.life_flash_duration
                play_sfx("life_lost")

                if self.lives <= 0:
                    self.lives = 0
                    self.is_game_over = True
                    self.player_won = False
                    play_sfx("game_over")

                    if not self.has_finished_interaction:
                        self.has_finished_interaction = True
                        rpy.end_interaction("game_over")
                    return
                else:
                    self.spawn_single_ball(stuck=True)

            for powerup in list(self.powerups):
                powerup.update(gdt)
                if powerup.rect().colliderect(self.paddle.rect()):
                    powerup.is_dead = True
                    play_sfx("powerup_pickup")

                    if powerup.kind in ("multiball", "paddle_grow"):
                        self.apply_powerup(powerup.kind)
                    else:
                        self.stored_powerups.append(powerup.kind)
                        self.score += 25

                if powerup.is_dead and powerup in self.powerups:
                    self.powerups.remove(powerup)

            if not self.bricks and not self.is_game_over:
                self.score += 500
                play_sfx("phase_clear")
                self.current_phase += 1
                self.reset_level()

        def render(self, width, height, st, at):
            """Renderiza frame completo do jogo e agenda próximo redraw.

            Args:
                width/height: dimensões de render fornecidas pelo Ren'Py.
                st: tempo desde início da interação.
                at: tempo de animação da árvore de displayables.

            Returns:
                Render final com HUD, entidades e overlays.
            """
            if self.last_render_time is None:
                self.last_render_time = st

            dt = float(st - self.last_render_time)
            self.last_render_time = st
            dt = clamp_value(dt, 0.0, 0.033)

            self._update(dt)

            render_out = Render(SCREEN_W, SCREEN_H)

            render_out.blit(
                rpy.render(Solid("#4b3f63", xysize=(SCREEN_W, SCREEN_H)), SCREEN_W, SCREEN_H, st, at),
                (0, 0)
            )

            next_pu = self._get_next_powerup_name()
            next_icon = self._get_next_powerup_icon()

            hud_y = 20

            self._draw_hud_item(
                render_out,
                self.ui_imgs["score"],
                self.score,
                20, hud_y, st, at,
                src_size=(32, 16)
            )

            self._draw_lives_hearts(
                render_out,
                240, hud_y, st, at,
                total_hearts=self.max_lives,
                spacing=8,
                icon_box=(32, 30)
            )

            self._draw_hud_item(
                render_out,
                self.ui_imgs["phase"],
                self.current_phase + 1,
                420, hud_y, st, at,
                src_size=(32, 16)
            )

            self._draw_hud_item(
                render_out,
                self.ui_imgs["speed"],
                "%.2f" % self.game_speed,
                600, hud_y, st, at,
                src_size=(32, 16)
            )

            self._draw_hud_item(
                render_out,
                self.ui_imgs["stored"],
                len(self.stored_powerups),
                790, hud_y, st, at,
                src_size=(32, 16)
            )

            self._draw_hud_item(
                render_out,
                next_icon,
                "%s (%s)" % (next_pu, key_label(get_keybind("use_powerup"))),
                980, hud_y, st, at,
                icon_box=self.powerup_icon_size,
                src_size=self.powerup_icon_size,
                text_size=22
            )

            lvl = clamp_value(self.paddle.level, 0, 3)
            paddle_img = Transform(
                self.paddle_imgs[lvl],
                size=(int(self.paddle.width), int(self.paddle.height))
            )
            paddle_d = rpy.render(
                paddle_img,
                int(self.paddle.width),
                int(self.paddle.height),
                st,
                at
            )
            if self.paddle.should_draw():
                render_out.blit(paddle_d, (int(self.paddle.x), int(self.paddle.y)))

            for ball in self.balls:
                size = int(ball.radius * 2)
                ball_src_w, ball_src_h = self.ball_native_size
                ball_d, off_x, off_y, _, _ = render_fitted(
                    self.ball_img,
                    size,
                    size,
                    ball_src_w,
                    ball_src_h,
                    st,
                    at
                )
                render_out.blit(
                    ball_d,
                    (int(ball.x - ball.radius + off_x), int(ball.y - ball.radius + off_y))
                )

            for brick in self.bricks:
                brick_img = self.brick_imgs[brick.color_family][brick.hp]
                src_w, src_h = self.brick_native_sizes[1]

                brick_d, off_x, off_y, _, _ = render_fitted(
                    brick_img,
                    int(brick.width),
                    int(brick.height),
                    src_w,
                    src_h,
                    st,
                    at
                )

                render_out.blit(
                    brick_d,
                    (int(brick.x + off_x), int(brick.y + off_y))
                )

            for powerup in self.powerups:
                render_out.blit(
                    rpy.render(powerup.sprite.current(), powerup.width, powerup.height, st, at),
                    (int(powerup.x), int(powerup.y))
                )

            if self.life_flash_timer > 0.0:
                flash_ratio = self.life_flash_timer / self.life_flash_duration
                flash_alpha = 0.45 * flash_ratio
                flash_overlay = Transform(
                    Solid("#ff1e1e", xysize=(SCREEN_W, SCREEN_H)),
                    alpha=flash_alpha
                )
                render_out.blit(
                    rpy.render(flash_overlay, SCREEN_W, SCREEN_H, st, at),
                    (0, 0)
                )

            rpy.redraw(self, 0)
            return render_out

        def event(self, ev, x, y, st):
            """Processa entrada do teclado: movimento, lançamento, uso e pausa.

            Args:
                ev: evento de entrada do pygame.
                x/y/st: parâmetros padrão de evento do Ren'Py.

            Returns:
                None na maior parte dos casos; em pausa, encerra interação.
            """
            if self.is_paused or self._pause_menu_is_open():
                return None

            if ev.type == pygame.KEYDOWN:
                if (self._is_bound_key(ev.key, "pause") or ev.key == pygame.K_ESCAPE) and not self.is_game_over:
                    self.is_paused = True
                    self.is_moving_left = False
                    self.is_moving_right = False
                    play_sfx("ui_click")
                    rpy.end_interaction("pause")
                    return None

                if self._is_bound_key(ev.key, "move_left"):
                    self.is_moving_left = True

                if self._is_bound_key(ev.key, "move_right"):
                    self.is_moving_right = True

                if self._is_bound_key(ev.key, "launch_ball") and not self.is_game_over:
                    for ball in self.balls:
                        if ball.is_stuck_to_paddle:
                            ball.launch_from_paddle(self.paddle)
                            play_sfx("ball_launch")

                if self._is_bound_key(ev.key, "use_powerup"):
                    self._activate_next_stored_powerup()

            elif ev.type == pygame.KEYUP:
                if self._is_bound_key(ev.key, "move_left"):
                    self.is_moving_left = False

                if self._is_bound_key(ev.key, "move_right"):
                    self.is_moving_right = False

            return None
