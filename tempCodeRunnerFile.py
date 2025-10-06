import pygame, random, sys

pygame.init()

# --- SETTINGS ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60

# --- COLORS ---
COLOR_BG = (10, 10, 25)
COLOR_BALL = (255, 255, 255)
COLOR_PADDLE = (180, 180, 255)
COLOR_POWERUP = (255, 200, 50)

COLOR_MAP = {
    "P": (180, 0, 180),   # Purple bricks (nền)
    "W": (255, 255, 255), # White bricks (chữ R)
    "G": (0, 200, 0),
    "Y": (255, 255, 0),
    "X": (150, 150, 150),
}

# --- LEVEL MAP (Logo chữ R) ---
level_map = [
    "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
    "PPPPPPPPPPWWWWWWWWWWPPPPPPPPPPPP",
    "PPPPPPPPPPWWWWWWWWWWPPPPPPPPPPPP",
    "PPPPPPPPPPWWPPPPPPPPPPPPPPPPPPPP",
    "PPPPPPPPPPWWPPWWWWWWWWPPPPPPPPPP",
    "PPPPPPPPPPWWPPWWWWWWWWPPPPPPPPPP",
    "PPPPPPPPPPWWPPPPPPPPWWWPPPPPPPPP",
    "PPPPPPPPPPWWPPPPPPPPPWWPPPPPPPPP",
    "PPPPPPPPPPWWPPPPPPPPPPWWPPPPPPPP",
    "PPPPPPPPPPWWPPPPPPPPPPPWWPPPPPPP",
    "PPPPPPPPPPWWPPPPPPPPPPPPWWPPPPPP",
    "PPPPPPPPPPWWPPPPPPPPPPPPPWWPPPPP",
    "PPPPPPPPPPWWPPPPPPPPPPPPPPWWPPPP",
    "PPPPPPPPPPWWPPPPPPPPPPPPPPPWWPPP",
    "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
    "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
]

BRICK_W, BRICK_H = 20, 20

# --- CLASSES ---

class Brick:
    def __init__(self, rect, kind):
        self.rect = rect
        self.kind = kind
        self.color = COLOR_MAP.get(kind, (0, 0, 0))
        self.alive = True

    def draw(self, surf):
        if self.alive:
            pygame.draw.rect(surf, self.color, self.rect)
            pygame.draw.rect(surf, (0, 0, 0), self.rect, 1)


class Paddle:
    def __init__(self):
        self.w, self.h = 100, 15
        self.rect = pygame.Rect(
            (SCREEN_WIDTH - self.w) // 2, SCREEN_HEIGHT - 50, self.w, self.h
        )
        self.speed = 8

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        self.rect.x = max(0, min(SCREEN_WIDTH - self.w, self.rect.x))

    def draw(self, surf):
        pygame.draw.rect(surf, COLOR_PADDLE, self.rect)


class Ball:
    def __init__(self, x, y, r=6):
        self.r = r
        self.rect = pygame.Rect(x - r, y - r, r * 2, r * 2)
        self.vx = random.choice([-1, 1]) * 4
        self.vy = -4

    def draw(self, surf):
        pygame.draw.ellipse(surf, COLOR_BALL, self.rect)

    def reflect_x(self):
        self.vx = -self.vx

    def reflect_y(self):
        self.vy = -self.vy

    def update(self, bricks, paddle, powerups, total_breakable):
        self.rect.x += self.vx
        self.rect.y += self.vy

        # --- Wall collision ---
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.reflect_x()
        if self.rect.top <= 0:
            self.reflect_y()

        # --- Paddle collision ---
        if self.rect.colliderect(paddle.rect) and self.vy > 0:
            offset = (self.rect.centerx - paddle.rect.centerx) / (paddle.w / 2)
            self.vx = offset * 5
            self.vy = -abs(self.vy)

        # --- Brick collision ---
        for brick in bricks:
            if not brick.alive:
                continue
            if self.rect.colliderect(brick.rect):
                dx = abs(self.rect.centerx - brick.rect.centerx)
                dy = abs(self.rect.centery - brick.rect.centery)
                if dx > dy:
                    self.reflect_x()
                else:
                    self.reflect_y()
                brick.alive = False
                total_breakable -= 1
                if random.random() < 0.3:
                    powerups.append(
                        PowerUp(brick.rect.centerx, brick.rect.centery)
                    )
                break
        return total_breakable


class PowerUp:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 8, y - 8, 16, 16)
        self.vy = 3

    def update(self):
        self.rect.y += self.vy

    def draw(self, surf):
        pygame.draw.rect(surf, COLOR_POWERUP, self.rect)


# --- SETUP ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Build bricks
bricks = []
for row_idx, row in enumerate(level_map):
    for col_idx, ch in enumerate(row):
        if ch == " ":
            continue
        rect = pygame.Rect(col_idx * BRICK_W + 100, row_idx * BRICK_H + 50, BRICK_W, BRICK_H)
        bricks.append(Brick(rect, ch))

# Make all bricks count as breakable
total_breakable = len(bricks)

paddle = Paddle()
ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
powerups = []

font = pygame.font.SysFont("consolas", 24)
running = True
win = False

# --- MAIN LOOP ---
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill(COLOR_BG)

    if not win:
        paddle.update()
        total_breakable = ball.update(bricks, paddle, powerups, total_breakable)

        for p in powerups:
            p.update()
            if p.rect.colliderect(paddle.rect):
                paddle.w += 20
                p.rect.y = SCREEN_HEIGHT + 100

        # Draw everything
        for brick in bricks:
            brick.draw(screen)
        for p in powerups:
            p.draw(screen)
        paddle.draw(screen)
        ball.draw(screen)

        # Check lose/win
        if ball.rect.top > SCREEN_HEIGHT:
            txt = font.render("GAME OVER", True, (255, 50, 50))
            screen.blit(txt, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2))
        elif total_breakable <= 0:
            win = True
    else:
        txt = font.render("YOU WIN!", True, (255, 255, 100))
        screen.blit(txt, (SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2))

    pygame.display.flip()
    clock.tick(FPS)
