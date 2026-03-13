init -1 python:
    import math
    import random
    import pygame

    import renpy.exports as rpy
    from renpy.display.image import Solid
    from renpy.display.core import Displayable
    from renpy.display.render import Render
    from renpy.display.transform import Transform

    SCREEN_W, SCREEN_H = 1920, 1080

    def clamp_value(value, min_value, max_value):
        """Limita um valor numérico ao intervalo [min_value, max_value].

        Args:
            value: valor de entrada.
            min_value: limite inferior.
            max_value: limite superior.

        Returns:
            Valor já limitado ao intervalo permitido.
        """
        return min_value if value < min_value else max_value if value > max_value else value

    def fit_size_preserve_ratio(src_w, src_h, box_w, box_h):
        """Calcula tamanho ajustado mantendo proporção dentro da caixa alvo.

        Returns:
            Tupla (largura, altura) ajustada para caber na caixa.
        """
        if src_w <= 0 or src_h <= 0:
            return int(box_w), int(box_h)

        scale = min(float(box_w) / float(src_w), float(box_h) / float(src_h))
        new_w = max(1, int(round(src_w * scale)))
        new_h = max(1, int(round(src_h * scale)))
        return new_w, new_h

    def render_fitted(displayable, box_w, box_h, src_w, src_h, st, at):
        """Renderiza e centraliza um displayable ajustado ao tamanho da caixa.

        Retorna: render, offset_x, offset_y, draw_w, draw_h.
        """
        draw_w, draw_h = fit_size_preserve_ratio(src_w, src_h, box_w, box_h)
        fitted = Transform(displayable, size=(draw_w, draw_h))
        rendered = rpy.render(fitted, draw_w, draw_h, st, at)

        offset_x = int((box_w - draw_w) * 0.5)
        offset_y = int((box_h - draw_h) * 0.5)

        return rendered, offset_x, offset_y, draw_w, draw_h

    class KeyCapture(Displayable):
        """Displayable invisível usado para capturar tecla em remapeamento.

        Uso:
            É adicionado na screen de keybinds para interceptar KEYDOWN.
        """
        def __init__(self, **kwargs):
            super(KeyCapture, self).__init__(**kwargs)

        def render(self, width, height, st, at):
            """Render mínimo; este objeto existe principalmente para eventos."""
            return Render(1, 1)

        def event(self, ev, x, y, st):
            """Captura KEYDOWN e encaminha para capture_key_name.

            Returns:
                None na maioria dos casos. Pode lançar IgnoreEvent quando uma
                tecla válida é capturada para evitar propagação.
            """
            if renpy.store.waiting_keybind_action is None:
                return None

            if ev.type == pygame.KEYDOWN:
                key_name = pygame.key.name(ev.key)

                if isinstance(key_name, bytes):
                    try:
                        key_name = key_name.decode("utf-8")
                    except Exception:
                        key_name = str(key_name)

                if not key_name:
                    renpy.store.keybind_message = "Tecla inválida."
                    return None

                capture_key_name(key_name)
                raise renpy.IgnoreEvent()

            return None

    class AnimatedSprite(Displayable):
        """Sprite animado por quadros.

        frames: sequência de imagens.
        fps: velocidade da animação.
        elapsed_time: tempo acumulado para seleção do quadro atual.
        """
        def __init__(self, frames, fps=12, **kwargs):
            super(AnimatedSprite, self).__init__(**kwargs)
            self.frames = frames
            self.fps = fps
            self.elapsed_time = 0.0

        def update(self, dt):
            """Avança o relógio interno da animação em segundos."""
            self.elapsed_time += dt

        def current(self):
            """Retorna o quadro atual com base no tempo acumulado."""
            if not self.frames:
                return Solid("#fff", xysize=(32, 32))
            frame_index = int(self.elapsed_time * self.fps) % len(self.frames)
            return self.frames[frame_index]

        def render(self, w, h, st, at):
            """Renderiza o quadro atual da animação."""
            frame = self.current()
            return rpy.render(frame, w, h, st, at)

    def load_powerup_frames(kind, count=6, size=(28, 28), native_size=(28, 28)):
        """Carrega e redimensiona os quadros de um tipo de powerup.

        Args:
            kind: pasta do powerup (ex.: multiball, sticky).
            count: quantidade de quadros esperada.
            size: caixa final de render dos quadros.
            native_size: tamanho nativo de referência para escala.

        Returns:
            Lista de frames (displayables) pronta para AnimatedSprite.
        """
        frames = []
        src_w, src_h = native_size

        for frame_i in range(count):
            path = "images/breakout/powerups/%s/%d.png" % (kind, frame_i)
            try:
                d = rpy.displayable(path)
            except Exception:
                d = Solid("#ff0", xysize=size)

            draw_w, draw_h = fit_size_preserve_ratio(src_w, src_h, size[0], size[1])
            frames.append(Transform(d, size=(int(draw_w), int(draw_h))))
        return frames

    def load_ui_frames(kind, count=6, size=(int, int), native_size=(32, 32), fallback_color="#fff"):
        """Carrega ícones de UI e retorna imagem estática ou AnimatedSprite.

        Regras de retorno:
        - 0 frames: retorna fallback sólido/arquivo estático.
        - 1 frame: retorna displayable único.
        - 2+ frames: retorna AnimatedSprite.
        """
        frames = []
        src_w, src_h = native_size

        for frame_i in range(count):
            path = "breakout/ui/%s/%d.png" % (kind, frame_i)
            try:
                d = rpy.displayable(path)
            except Exception:
                break

            draw_w, draw_h = fit_size_preserve_ratio(src_w, src_h, size[0], size[1])
            frames.append(Transform(d, size=(int(draw_w), int(draw_h))))

        if not frames:
            try:
                d = rpy.displayable("breakout/ui/%s.png" % kind)
            except Exception:
                d = Solid(fallback_color, xysize=size)
            return d
        elif len(frames) == 1:
            return frames[0]
        else:
            return AnimatedSprite(frames, fps=12)

    class Paddle:
        """Entidade da raquete do jogador.

        level/level_widths: nível e larguras disponíveis.
        x/y/width/height: posição e tamanho atuais.
        speed_px_per_s: velocidade de movimento horizontal.
        is_sticky/sticky_used_once: estado do efeito sticky.
        blink_timer/blink_step: controle de efeito visual de piscar.
        """
        def __init__(self):
            self.level = 0
            self.level_widths = [48, 64, 80, 96]

            self.native_sizes = [
                (48, 32),
                (64, 32),
                (80, 32),
                (96, 32),
            ]

            self.width = self.level_widths[self.level]

            native_w, native_h = self.native_sizes[self.level]
            self.height = int(round(float(self.width) * native_h / native_w))

            self.x = (SCREEN_W - self.width) / 2
            self.y = SCREEN_H - 70
            self.speed_px_per_s = 900.0

            self.is_sticky = False
            self.sticky_used_once = False

            self.blink_timer = 0.0
            self.blink_step = 0.08

        def rect(self):
            """Retorna o retângulo de colisão da raquete."""
            return pygame.Rect(int(self.x), int(self.y), int(self.width), int(self.height))

        def move(self, direction_x, dt):
            """Move a raquete no eixo X usando direção normalizada e dt.

            direction_x esperado: -1 (esquerda), 0 (parado), 1 (direita).
            """
            self.x += direction_x * self.speed_px_per_s * dt
            self.x = clamp_value(self.x, 0, SCREEN_W - self.width)

        def grow_one_level(self):
            """Aumenta o nível/largura da raquete preservando o centro."""
            if self.level >= 3:
                return False

            center_x = self.x + self.width * 0.5

            self.level += 1
            self.width = self.level_widths[self.level]

            native_w, native_h = self.native_sizes[self.level]
            self.height = int(round(float(self.width) * native_h / native_w))

            self.x = clamp_value(center_x - self.width * 0.5, 0, SCREEN_W - self.width)
            return True

        def trigger_blink(self, duration=0.64):
            """Inicia (ou estende) o efeito de piscar por duration segundos."""
            self.blink_timer = max(self.blink_timer, float(duration))

        def update_blink(self, dt):
            """Atualiza a contagem regressiva do efeito de piscar."""
            if self.blink_timer > 0.0:
                self.blink_timer = max(0.0, self.blink_timer - float(dt))

        def should_draw(self):
            """Define se a raquete deve aparecer no frame atual."""
            if self.blink_timer <= 0.0:
                return True
            phase = int(self.blink_timer / self.blink_step)
            return (phase % 2) == 0

    class Ball:
        """Entidade da bola com física básica e colisão em bordas.

        x/y: centro da bola.
        vel_x/vel_y: vetor de velocidade.
        radius: raio para colisões.
        speed_multiplier: multiplicador de velocidade.
        is_stuck_to_paddle: indica bola presa na raquete.
        """
        def __init__(self, x, y, vel_x, vel_y):
            self.radius = 8
            self.x = float(x)
            self.y = float(y)
            self.prev_x = float(x)
            self.prev_y = float(y)
            self.vel_x = float(vel_x)
            self.vel_y = float(vel_y)

            self.speed_multiplier = 1.0
            self.is_stuck_to_paddle = False

        def rect(self):
            """Retorna o retângulo de colisão da bola."""
            return pygame.Rect(
                int(self.x - self.radius),
                int(self.y - self.radius),
                self.radius * 2,
                self.radius * 2
            )

        def launch_from_paddle(self, paddle):
            """Solta a bola da raquete com ângulo inicial aleatório."""
            self.is_stuck_to_paddle = False
            angle = random.uniform(-0.9, 0.9)
            speed = 380.0 * self.speed_multiplier
            self.vel_x = math.sin(angle) * speed
            self.vel_y = -abs(math.cos(angle) * speed)

        def update(self, dt, paddle=None):
            """Atualiza posição e reflexões da bola nas bordas da arena.

            Se a bola estiver presa na raquete, segue a posição da raquete
            até ser lançada.
            """
            if self.is_stuck_to_paddle and paddle is not None:
                self.x = paddle.x + paddle.width * 0.5
                self.y = paddle.y - 16
                self.prev_x = self.x
                self.prev_y = self.y
                return

            self.prev_x = self.x
            self.prev_y = self.y

            self.x += self.vel_x * dt
            self.y += self.vel_y * dt

            if self.x - self.radius < 0:
                self.x = self.radius
                self.vel_x *= -1
            if self.x + self.radius > SCREEN_W:
                self.x = SCREEN_W - self.radius
                self.vel_x *= -1
            if self.y - self.radius < 0:
                self.y = self.radius
                self.vel_y *= -1

    class Brick:
        """Entidade de tijolo destrutível.

        x/y/width/height: área ocupada na arena.
        hp/initial_hp: durabilidade atual e inicial.
        color_family: família visual por resistência.
        """
        def __init__(self, x, y, width, height, hp=1, color_family=None):
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.hp = hp
            self.initial_hp = hp
            self.color_family = color_family

        def rect(self):
            """Retorna o retângulo de colisão do tijolo."""
            return pygame.Rect(int(self.x), int(self.y), int(self.width), int(self.height))

    class PowerUp:
        """Entidade colecionável que cai verticalmente.

        kind: identificador do efeito.
        x/y: posição no mundo.
        fall_speed: velocidade de queda.
        width/height: tamanho para colisão e render.
        sprite: visual do powerup.
        is_dead: marca para remoção.
        """
        def __init__(self, kind, x, y, sprite):
            self.kind = kind
            self.x = float(x)
            self.y = float(y)
            self.fall_speed = 220.0
            self.width = 28
            self.height = 28
            self.sprite = sprite
            self.is_dead = False

        def rect(self):
            """Retorna o retângulo de colisão do powerup."""
            return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

        def update(self, dt):
            """Atualiza queda e remove quando sai da tela.

            Efeito colateral:
                Marca `is_dead=True` ao ultrapassar limite inferior.
            """
            self.y += self.fall_speed * dt
            self.sprite.update(dt)
            if self.y > SCREEN_H + 40:
                self.is_dead = True
