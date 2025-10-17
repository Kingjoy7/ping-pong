import pygame
import os
from .paddle import Paddle
from .ball import Ball
WHITE = (255, 255, 255)
BG = (0, 0, 0)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.paddle_width = 10
        self.paddle_height = 100

        self.player = Paddle(10, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ai = Paddle(width - 20, height // 2 - 50, self.paddle_width, self.paddle_height)

        # ball constructor signature used in your project; adjust if different
        self.ball = Ball(width // 2, height // 2, 20, 20, width, height)

        self.player_score = 0
        self.ai_score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.big_font = pygame.font.SysFont("Arial", 64, bold=True)

        # Game states: "serve", "playing", "paused", "gameover", "choose_replay"
        self.state = "serve"

        # default winner config (best-of 5 -> winner_score = 3)
        self.best_of = 5
        self.winner_score = (self.best_of // 2) + 1

        # Gameover control
        self.gameover_time = None
        self.gameover_delay_ms = 3000
        self.winner_text = ""
        self.should_quit = False
        assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "sounds")
        assets_dir = os.path.normpath(assets_dir)

        def load_sound(name):
            path = os.path.join(assets_dir, name)
            try:
                if os.path.exists(path):
                    s = pygame.mixer.Sound(path)
                    s.set_volume(0.6)  # adjust volume
                    return s
            except Exception as e:
                print("Sound load failed:", path, e)
            return None

        self.paddle_sound = load_sound("paddle_hit.wav")
        self.wall_sound = load_sound("wall_bounce.wav")
        self.score_sound = load_sound("score.wav")

        # create ball and pass paddle/wall sound objects
        # adapt Ball() args if different; this matches the modified Ball above
        self.ball = Ball(width // 2, height // 2, 20, 20, width, height,
                         paddle_sound=self.paddle_sound, wall_sound=self.wall_sound)

    def handle_input(self):
        keys = pygame.key.get_pressed()

        # Controls vary by state
        if self.state == "playing":
            if keys[pygame.K_w]:
                self.player.move(-10, self.height)
            if keys[pygame.K_s]:
                self.player.move(10, self.height)
        elif self.state == "serve":
            # still allow movement before serve
            if keys[pygame.K_w]:
                self.player.move(-10, self.height)
            if keys[pygame.K_s]:
                self.player.move(10, self.height)

        # Toggle play/pause/serve with SPACE (when not in choose_replay menu)
        if keys[pygame.K_SPACE] and self.state not in ("gameover", "choose_replay"):
            if self.state in ("serve", "paused"):
                self.state = "playing"
            elif self.state == "playing":
                self.state = "paused"

        # Restart on R (works anytime: resets to current best_of)
        if keys[pygame.K_r]:
            self.reset_game()

        # Quit on Q or Escape when in replay menu
        if keys[pygame.K_q]:
            self.should_quit = True

        # If we are in the GAMEOVER state, allow immediate actions:
        if self.state == "gameover":
            # Press R to restart with same best_of
            if keys[pygame.K_r]:
                self.set_best_of(self.best_of)  # reset winner_score based on current best_of
                self.reset_game()
            # Press 3/5/7 to choose best-of and restart
            if keys[pygame.K_3]:
                self.set_best_of(3)
                self.reset_game()
            if keys[pygame.K_5]:
                self.set_best_of(5)
                self.reset_game()
            if keys[pygame.K_7]:
                self.set_best_of(7)
                self.reset_game()
            # ESC to exit
            if keys[pygame.K_ESCAPE]:
                self.should_quit = True

    def update(self):
        # If gameover, don't update physics; just keep render loop alive
        if self.state == "gameover":
            # no physics updates; we keep GUI visible and wait for user
            return

        if self.state == "playing":
            # Move ball; pass paddles for sub-step collision if ball.move supports it
            try:
                self.ball.move(self.player, self.ai)
            except TypeError:
                self.ball.move()
                self.ball.check_collision(self.player, self.ai)

            # Score checks (ball went out left/right)
            if self.ball.x <= -self.ball.width:
                self.ai_score += 1
                self._after_score()
            elif self.ball.x >= self.width + self.ball.width:
                self.player_score += 1
                self._after_score()

            # Simple AI movement
            try:
                self.ai.auto_track(self.ball, self.height)
            except AttributeError:
                # if your Paddle has different AI method name, keep as is or implement
                pass

    def render(self, screen):
        screen.fill(BG)

        # center line
        pygame.draw.aaline(screen, WHITE, (self.width//2, 0), (self.width//2, self.height))

        # draw entities
        pygame.draw.rect(screen, WHITE, self.player.rect())
        pygame.draw.rect(screen, WHITE, self.ai.rect())
        pygame.draw.ellipse(screen, WHITE, self.ball.rect())

        # draw scores
        player_text = self.font.render(str(self.player_score), True, WHITE)
        ai_text = self.font.render(str(self.ai_score), True, WHITE)
        screen.blit(player_text, (self.width//4 - player_text.get_width()//2, 20))
        screen.blit(ai_text, (self.width * 3//4 - ai_text.get_width()//2, 20))

        # state messages
        if self.state == "serve":
            t = self.font.render("Press SPACE to serve", True, WHITE)
            screen.blit(t, (self.width//2 - t.get_width()//2, self.height//2 - 30))
        if self.state == "paused":
            t = self.font.render("Paused - Press SPACE to resume", True, WHITE)
            screen.blit(t, (self.width//2 - t.get_width()//2, self.height//2 - 30))

        # GAMEOVER: show winner + replay options
        if self.state == "gameover":
            t = self.big_font.render(self.winner_text, True, WHITE)
            screen.blit(t, (self.width//2 - t.get_width()//2, self.height//2 - t.get_height()))

            # small instructions and options
            t2 = self.font.render("Press R to replay (same), 3/5/7 for Best-of, or ESC to exit", True, WHITE)
            screen.blit(t2, (self.width//2 - t2.get_width()//2, self.height//2 + 40))

            # show current best-of setting
            t3 = self.font.render(f"Current mode: Best of {self.best_of}", True, WHITE)
            screen.blit(t3, (self.width//2 - t3.get_width()//2, self.height//2 + 80))

    def _after_score(self):
        if self.score_sound:
            try:
                self.score_sound.play()
            except Exception:
                pass
        # Reset ball for serve
        self.ball.reset()

        # Check winner
        if self.player_score >= self.winner_score:
            self._trigger_gameover("Player Wins!")
        elif self.ai_score >= self.winner_score:
            self._trigger_gameover("AI Wins!")
        else:
            # go to serve state until player hits SPACE
            self.state = "serve"

    def _trigger_gameover(self, text):
        self.state = "gameover"
        self.winner_text = text
        # stop physics and wait for user input; do not auto-quit so user can choose replay

    def reset_game(self):
        # reset scores, ball and paddles but keep current best_of
        self.player_score = 0
        self.ai_score = 0
        self.ball.reset()
        self.player.y = self.height // 2 - self.player.height // 2
        self.ai.y = self.height // 2 - self.ai.height // 2
        self.state = "serve"
        self.winner_text = ""
        self.should_quit = False

    def set_best_of(self, best_of):
        """Set a new best-of mode (3,5,7) and update winner_score accordingly."""
        if best_of not in (3, 5, 7):
            return
        self.best_of = best_of
        self.winner_score = (best_of // 2) + 1
