# game/ball.py
import pygame
import random

class Ball:
    def __init__(self, x, y, width, height, screen_width, screen_height,
                 paddle_sound=None, wall_sound=None):
        # positions
        self.original_x = x
        self.original_y = y
        self.x = float(x)
        self.y = float(y)

        # visuals / rect
        self.width = width
        self.height = height

        # screen
        self.screen_width = screen_width
        self.screen_height = screen_height

        # velocities
        self.velocity_x = float(random.choice([-5, 5]))
        self.velocity_y = float(random.choice([-3, 3]))

        # sound effects (pygame.mixer.Sound or None)
        self.paddle_sound = paddle_sound
        self.wall_sound = wall_sound

        # speed limits
        self.min_speed_x = 2.0
        self.max_speed_x = 18.0
        self.hit_speed_boost = 1.05

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), int(self.width), int(self.height))

    def move(self, player=None, ai=None):
        """
        Sub-stepped movement with immediate wall and paddle checks. If
        paddle objects are passed, on-paddle-hit is handled here.
        """
        dx = self.velocity_x
        dy = self.velocity_y

        step_limit = max(2.0, min(self.width, self.height) / 2.0)
        distance = max(abs(dx), abs(dy))
        steps = int(distance / step_limit) + 1
        step_x = dx / steps
        step_y = dy / steps

        for _ in range(steps):
            self.x += step_x
            self.y += step_y

            # wall (top/bottom)
            if self.y <= 0:
                self.y = 0
                self.velocity_y = -self.velocity_y
                if self.wall_sound:
                    self.wall_sound.play()
            elif self.y + self.height >= self.screen_height:
                self.y = self.screen_height - self.height
                self.velocity_y = -self.velocity_y
                if self.wall_sound:
                    self.wall_sound.play()

            # paddle collisions (if paddles provided)
            if player is not None and self.rect().colliderect(player.rect()) and self.velocity_x < 0:
                self._on_paddle_hit(player)
            if ai is not None and self.rect().colliderect(ai.rect()) and self.velocity_x > 0:
                self._on_paddle_hit(ai)

            # stop stepping if out of horizontal bounds (score)
            if self.x < -self.width or self.x > self.screen_width + self.width:
                break

    def check_collision(self, player, ai):
        # fallback if move() was called without paddles
        if self.rect().colliderect(player.rect()) and self.velocity_x < 0:
            self._on_paddle_hit(player)
        if self.rect().colliderect(ai.rect()) and self.velocity_x > 0:
            self._on_paddle_hit(ai)

    def _on_paddle_hit(self, paddle):
        # push outside and reverse/boost X
        if self.x + self.width/2 < paddle.x + paddle.width/2:
            self.x = paddle.x + paddle.width
        else:
            self.x = paddle.x - self.width

        self.velocity_x = -self.velocity_x * self.hit_speed_boost

        # angle control
        paddle_center_y = paddle.y + paddle.height / 2.0
        offset = ((self.y + self.height / 2.0) - paddle_center_y) / (paddle.height / 2.0)
        self.velocity_y += offset * 5.0

        # clamp speeds
        if abs(self.velocity_x) < self.min_speed_x:
            self.velocity_x = self.min_speed_x * (1 if self.velocity_x > 0 else -1)
        if abs(self.velocity_x) > self.max_speed_x:
            self.velocity_x = self.max_speed_x * (1 if self.velocity_x > 0 else -1)

        # play sound
        if self.paddle_sound:
            try:
                self.paddle_sound.play()
            except Exception:
                pass

    def reset(self):
        self.x = float(self.original_x)
        self.y = float(self.original_y)
        self.velocity_x = float(random.choice([-5, 5]))
        self.velocity_y = float(random.choice([-3, 3]))
