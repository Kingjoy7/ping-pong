import pygame
import sys

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize the mixer for sound

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping Pong with Sound")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Paddle settings
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
paddle_speed = 7

# Ball settings
BALL_RADIUS = 10
ball_speed_x, ball_speed_y = 5, 5

# Load sounds
paddle_hit_sound = pygame.mixer.Sound("game/assets/sounds/paddle_hit.wav")
wall_bounce_sound = pygame.mixer.Sound("game/assets/sounds/wall_bounce.wav")
score_sound = pygame.mixer.Sound("game/assets/sounds/score.wav")

# Paddles and Ball
player = pygame.Rect(50, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
opponent = pygame.Rect(WIDTH-60, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(WIDTH//2, HEIGHT//2, BALL_RADIUS*2, BALL_RADIUS*2)

# Scores
player_score = 0
opponent_score = 0
font = pygame.font.SysFont(None, 50)

# Clock
clock = pygame.time.Clock()

def reset_ball():
    global ball_speed_x, ball_speed_y
    ball.center = (WIDTH//2, HEIGHT//2)
    ball_speed_x *= -1
    ball_speed_y *= -1

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Paddle movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and player.top > 0:
        player.y -= paddle_speed
    if keys[pygame.K_s] and player.bottom < HEIGHT:
        player.y += paddle_speed
    if keys[pygame.K_UP] and opponent.top > 0:
        opponent.y -= paddle_speed
    if keys[pygame.K_DOWN] and opponent.bottom < HEIGHT:
        opponent.y += paddle_speed

    # Ball movement
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    # Collisions with top/bottom
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_speed_y *= -1
        wall_bounce_sound.play()

    # Collisions with paddles
    if ball.colliderect(player) or ball.colliderect(opponent):
        ball_speed_x *= -1
        paddle_hit_sound.play()

    # Scoring
    if ball.left <= 0:
        opponent_score += 1
        score_sound.play()
        reset_ball()
    if ball.right >= WIDTH:
        player_score += 1
        score_sound.play()
        reset_ball()

    # Drawing
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, player)
    pygame.draw.rect(screen, WHITE, opponent)
    pygame.draw.ellipse(screen, WHITE, ball)

    # Draw scores
    player_text = font.render(str(player_score), True, WHITE)
    opponent_text = font.render(str(opponent_score), True, WHITE)
    screen.blit(player_text, (WIDTH//4, 20))
    screen.blit(opponent_text, (WIDTH*3//4, 20))

    pygame.display.flip()
    clock.tick(60)
