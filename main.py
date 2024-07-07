import pygame
import random
import math
from pygame import mixer


# Define colors used by the game
TEXT_COLOR = (255, 255, 255)
BACKGROUND = pygame.image.load("bgg.png")
BALL_COLOR = (220, 220, 220)
PADDLE_COLOR = (255, 255, 0)
BRICK_COLORS = ((255, 0, 0), (255, 50, 0), (255, 100, 0), (255, 150, 0), (255, 200, 0), (255, 255, 0))

# Set screen dimensions
Screen_Width = 581
Screen_Height = 624

# Initialize Pygame
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((Screen_Width, Screen_Height))
pygame.display.set_caption("Breakout")

mixer.music.load('background.wav')
mixer.music.play(-1)

class EnhancedSprite(pygame.sprite.Sprite):
    """Base class for game sprites."""
    def __init__(self, color, rect, group=None, **kwargs):
        super().__init__(**kwargs)
        self.image = pygame.Surface(rect.size)
        self.image.fill(color)
        self.rect = rect
        if group is not None:
            group.add(self)

    # Properties to expose properties of the rectangle
    @property
    def x(self):
        return self.rect.x

    @x.setter
    def x(self, value):
        self.rect.x = value

    @property
    def y(self):
        return self.rect.y

    @y.setter
    def y(self, value):
        self.rect.y = value

    @property
    def centerx(self):
        return self.rect.centerx

    @centerx.setter
    def centerx(self, value):
        self.rect.centerx = value

    @property
    def centery(self):
        return self.rect.centery

    @centery.setter
    def centery(self, value):
        self.rect.centery = value

    @property
    def right(self):
        return self.rect.right

    @right.setter
    def right(self, value):
        self.rect.right = value

    @property
    def bottom(self):
        return self.rect.bottom

    @bottom.setter
    def bottom(self, value):
        self.rect.bottom = value

class Brick(EnhancedSprite):
    """Class for representing bricks."""
    group = pygame.sprite.Group()

    def __init__(self, row, col, width, height, gap):
        super().__init__(BRICK_COLORS[row % len(BRICK_COLORS)],
                         pygame.Rect(25 + (width + gap) * col, 20 + (height + gap) * row, width, height),
                         self.group)
        self.hits = 0
        self.required_hits = 2 if row < 2 else 1  

    def hit(self, score):
        """Handle a hit on the brick."""
        self.hits += 1
        if self.hits >= self.required_hits:
            hit_sound = mixer.Sound('pop.wav')
            hit_sound.play()
            self.kill()
            score += 1
        return score

class Paddle(EnhancedSprite):
    """Class for representing the paddle."""
    group = pygame.sprite.Group()

    def __init__(self, width, height):
        super().__init__(PADDLE_COLOR, pygame.Rect((Screen_Width - width) // 2, Screen_Height - 40, width, height),
                         self.group)

    def move(self, x):
        """Move the paddle to the specified x-coordinate."""
        self.centerx = x

class LifeCounter():
    """Class for representing the life counter."""
    def __init__(self, x, y, count=3, width=20, height=20):
        self.color = BALL_COLOR
        self.group = pygame.sprite.Group()
        self.reset(count, width, height, x, y)

    def reset(self, count, width, height, x, y):
        """Reset the life counter."""
        for c in range(count):
            rect = pygame.Rect(x + c * (width + 5), y, width, height)
            EnhancedSprite(self.color, rect, self.group)

    def __len__(self):
        """Return the current count of remaining lives."""
        return len(self.group)

    def kill(self):
        """Remove a life from the counter."""
        self.group.sprites()[-1].kill()
        new_paddle = mixer.Sound('paddle.wav')
        new_paddle.play()

class Ball(EnhancedSprite):
    """Class for representing the ball."""
    group = pygame.sprite.Group()

    def __init__(self, paddle, lives, speed=15, radius=10):
        diameter = radius * 2
        rect = pygame.Rect((Screen_Width - diameter) // 2, Screen_Height - 55, diameter, diameter)
        super().__init__(BALL_COLOR, rect, self.group)
        self.image = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        pygame.draw.circle(self.image, BALL_COLOR, (radius, radius), radius)
        self.rect = rect
        self.paddle = paddle
        self.lives = lives
        self.speed = speed
        self.radius = radius
        self.dx = self.dy = 0
        self.reset(0)

    def reset(self, score=None):
        """Reset the ball."""
        self.active = False
        if score is not None:
            self.score = score

    def start(self):
        """Start the ball."""
        self.centerx = self.paddle.centerx
        self.bottom = self.paddle.y - 2

        # Set the initial speed based on the formula a = sqrt(2) * R
        initial_speed = int(math.sqrt(2) * self.radius)

        angle = (random.random() - 0.5) * math.pi / 2
        self.dx = int(initial_speed * math.sin(angle))
        self.dy = -int(initial_speed * math.cos(angle))

        self.active = True

    def update(self):
        """Update the ball's position and check for collisions."""
        if not self.active:
            self.centerx = self.paddle.centerx
            self.bottom = self.paddle.y - 5

        self.x += self.dx
        self.y += self.dy

        if self.x <= 0:
            self.dx = abs(self.dx)
        if self.right >= Screen_Width:
            self.dx = -abs(self.dx)
        if self.y < 0:
            self.dy = abs(self.dy)

        if self.centery > self.paddle.centery:
            self.lives.kill()
            self.active = False

        if pygame.sprite.spritecollide(self, self.paddle.group, False) and self.dy > 0:
            bangle = math.atan2(-self.dx, self.dy)
            pangle = math.atan2(self.centerx - self.paddle.centerx, 50)
            angle = (pangle - bangle) / 2
            self.dx = int(math.sin(angle) * self.speed)
            self.dy = -int(math.cos(angle) * self.speed)

        bricks = pygame.sprite.spritecollide(self, Brick.group, False)
        for brick in bricks:
            self.score = brick.hit(self.score)
            if brick.y < self.centery < brick.bottom:
                self.dx = abs(self.dx) if self.centerx > brick.centerx else -abs(self.dx)
            else:
                self.dy = abs(self.dy) if self.centery > brick.centery else -abs(self.dy)

def main():
    try:
        # Initialize game elements
        lives = LifeCounter(10, Screen_Height - 30)
        paddle = Paddle(90, 11)
        ball = Ball(paddle, lives)
        for r in range(6):
            for c in range(9):
                Brick(r, c, 50, 20, 10)
        all_spritesgroup = pygame.sprite.Group()
        all_spritesgroup.add(paddle.group, lives.group, ball.group, Brick.group)

        clock = pygame.time.Clock()
        while len(lives) > 0 and len(Brick.group) > 0:
            clock.tick(40)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise SystemExit
                elif event.type == pygame.MOUSEMOTION:
                    paddle.move(event.pos[0])
                elif event.type == pygame.MOUSEBUTTONUP:
                    if not ball.active:
                        ball.start()

            ball.update()
            font = pygame.font.Font(None, 34)
            text = font.render(f"Score: {ball.score}", 1, TEXT_COLOR)
            screen.blit(BACKGROUND, (0, 0))
            screen.blit(text, (Screen_Width - 150, Screen_Height - 30))
            all_spritesgroup.draw(screen)
            pygame.display.flip()

        font = pygame.font.Font(None, 74)
        if len(lives) == 0:
            message = "Game over"
            game_over_sound = pygame.mixer.Sound('lose.wav')
            game_over_sound.play()
        else:
            message = "YOU WON!!"
            victory_sound = pygame.mixer.Sound('won.wav')
            victory_sound.play()

        text = font.render(message, 1, TEXT_COLOR)
        text_rect = text.get_rect(center=(Screen_Width // 2, Screen_Height // 2))
        screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.wait(2000)

    finally:
        pygame.quit()

if __name__ == "__main__":
    main()