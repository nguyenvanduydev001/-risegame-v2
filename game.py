import pygame, sys, random

BLOCK_SIZE = 24
COLS = 40
ROWS = 30
SCREEN_WIDTH = COLS * BLOCK_SIZE // 2
SCREEN_HEIGHT = ROWS * BLOCK_SIZE // 2
FPS = 60
MAX_BALLS = 30

COLOR_BG = (15, 20, 40)
COLOR_WALL = (120, 120, 120)
COLOR_YELLOW = (240, 200, 40)
COLOR_GREEN = (30, 200, 80)
COLOR_PADDLE = (255, 255, 255)
COLOR_BALL = (255, 255, 255)
COLOR_TEXT = (255, 255, 255)
COLOR_WHITE = (255, 255, 255)

level_map = []
R_pattern = [
    "                                        ",
    "                GGGGGGGGGGG             ",
    "                GGGGGGGGGGG             ",
    "               GG         GG            ",
    "               GG         GG            ",
    "               GG         GG            ",
    "               GG   GGGGGGGG            ",
    "               GG   GGGGGGGG            ",
    "               GG        GG             ",
    "               GG         GG            ",
    "               GG          GG           ",
    "               GG           GG          ",
    "               GG            GG         ",
    "               GG             GG        ",
    "                                        ",
    "                                        ",
]

for line in R_pattern:
    level_map.append(line)

class Brick:
    def __init__(self, rect, kind):
        self.rect = rect
        self.kind = kind
        self.alive = True

    def draw(self, surf):
        if not self.alive:
            return
        color = {
            "X": COLOR_WALL,
            "Y": COLOR_YELLOW,
            "G": COLOR_WHITE,
        }.get(self.kind, (200, 200, 200))
        pygame.draw.rect(surf, color, self.rect)
        pygame.draw.rect(surf, (40, 40, 60), self.rect, 1)


class Paddle:
    def __init__(self, x, y, w=80, h=10):
        self.base_w = w
        self.w = w
        self.h = h
        self.rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
        self.speed = 8
        self.enlarge_timer = 0

    def update(self):
        if self.enlarge_timer > 0:
            self.enlarge_timer -= 1
            if self.enlarge_timer == 0:
                self.set_size(self.base_w)

    def move_left(self):
        self.rect.x -= self.speed
        if self.rect.left < 0:
            self.rect.left = 0

    def move_right(self):
        self.rect.x += self.speed
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def set_size(self, new_w):
        cx = self.rect.centerx
        self.w = int(new_w)
        self.rect.width = int(new_w)
        self.rect.centerx = cx

    def draw(self, surf):
        pygame.draw.rect(surf, COLOR_PADDLE, self.rect)


class Ball:
    def __init__(self, x, y, r=6):
        self.r = r
        self.rect = pygame.Rect(x - r, y - r, r * 2, r * 2)
        speed = 3  
        self.vx = random.choice([-1, 1]) * speed * random.uniform(0.8, 1.0)
        self.vy = -speed

    def draw(self, surf):
        pygame.draw.ellipse(surf, COLOR_BALL, self.rect)

    def reflect_x(self):
        self.vx = -self.vx

    def reflect_y(self):
        self.vy = -self.vy

    def update(self, bricks, paddle, powerups, total_breakable):
        steps = int(max(abs(self.vx), abs(self.vy)))
        for _ in range(steps):
            self.rect.x += self.vx / steps
            self.rect.y += self.vy / steps

            if self.rect.left <= 0:
                self.rect.left = 0
                self.reflect_x()
            elif self.rect.right >= SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH
                self.reflect_x()
            if self.rect.top <= 0:
                self.rect.top = 0
                self.reflect_y()

            if self.rect.colliderect(paddle.rect) and self.vy > 0:
                offset = (self.rect.centerx - paddle.rect.centerx) / (paddle.w / 2)
                self.vx = offset * 5
                self.vy = -abs(self.vy)

            for brick in bricks:
                if not brick.alive:
                    continue
                if self.rect.colliderect(brick.rect):
                    dx = abs(self.rect.centerx - brick.rect.centerx)
                    dy = abs(self.rect.centery - brick.rect.centery)
                    if dx > dy:
                        if self.rect.centerx < brick.rect.centerx:
                            self.rect.right = brick.rect.left
                        else:
                            self.rect.left = brick.rect.right
                        self.reflect_x()
                    else:
                        if self.rect.centery < brick.rect.centery:
                            self.rect.bottom = brick.rect.top
                        else:
                            self.rect.top = brick.rect.bottom
                        self.reflect_y()

                    if brick.kind in ("Y", "G"):
                        brick.alive = False
                        total_breakable -= 1
                        if random.random() < 0.4:
                            powerups.append(PowerUp(brick.rect.centerx, brick.rect.centery))
                    return total_breakable
        return total_breakable


class PowerUp:
    TYPES = ["+3", "x3", "PA+"]

    def __init__(self, x, y, kind=None):
        self.kind = kind if kind else random.choice(PowerUp.TYPES)
        self.rect = pygame.Rect(x, y, 20, 20)
        self.vy = 3

    def update(self):
        self.rect.y += self.vy

    def draw(self, surf):
        colors = {
            "+3": (0, 255, 0),
            "x3": (0, 150, 255),
            "PA+": (255, 0, 255)
        }
        pygame.draw.rect(surf, colors.get(self.kind, (255, 255, 255)), self.rect)
        font = pygame.font.SysFont('Arial', 14)
        txt = font.render(self.kind, True, (0, 0, 0))
        surf.blit(txt, (self.rect.x + 2, self.rect.y + 2))


def build_level_from_map(map_lines):
    bricks = []
    scale_x = SCREEN_WIDTH / (COLS * BLOCK_SIZE)
    scale_y = SCREEN_HEIGHT / (ROWS * BLOCK_SIZE)
    scale = min(scale_x, scale_y)
    for row_idx, line in enumerate(map_lines):
        for col_idx, ch in enumerate(line):
            if ch == " ":
                continue
            x = int(col_idx * BLOCK_SIZE * scale)
            y = int(row_idx * BLOCK_SIZE * scale)
            rect = pygame.Rect(x, y, int(BLOCK_SIZE * scale), int(BLOCK_SIZE * scale))
            bricks.append(Brick(rect, ch))
    return bricks

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Rise Game V2")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 22)

    bricks = build_level_from_map(level_map)
    paddle = Paddle(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40)
    balls = [Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)]
    powerups = []
    running = True
    move_left = move_right = False
    game_over = win = False
    total_breakable = sum(1 for b in bricks if b.kind in ("Y", "G"))

    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_a:
                    move_left = True
                if e.key == pygame.K_d:
                    move_right = True
                if e.key == pygame.K_r and (game_over or win):
                    return main()
                if e.key == pygame.K_ESCAPE:
                    running = False
            elif e.type == pygame.KEYUP:
                if e.key == pygame.K_a:
                    move_left = False
                if e.key == pygame.K_d:
                    move_right = False

        if not game_over and not win:
            if move_left:
                paddle.move_left()
            if move_right:
                paddle.move_right()
            paddle.update()

            for ball in list(balls):
                total_breakable = ball.update(bricks, paddle, powerups, total_breakable)
                if ball.rect.top > SCREEN_HEIGHT:
                    balls.remove(ball)

            for p in list(powerups):
                p.update()
                if p.rect.colliderect(paddle.rect):
                    if len(balls) < MAX_BALLS:
                        if p.kind == "+3":
                            for _ in range(3):
                                balls.append(Ball(paddle.rect.centerx, paddle.rect.top - 20))
                        elif p.kind == "x3":
                            new_balls = []
                            for b in balls:
                                for _ in range(2):
                                    nb = Ball(b.rect.centerx, b.rect.centery)
                                    nb.vx = b.vx * random.uniform(0.8, 1.2)
                                    nb.vy = -abs(b.vy) * random.uniform(0.8, 1.2)
                                    new_balls.append(nb)
                            balls.extend(new_balls)
                    elif p.kind == "PA+":
                        if paddle.w <= paddle.base_w: 
                            paddle.set_size(paddle.base_w * 1.6)
                            paddle.enlarge_timer = int(10 * FPS)
                    powerups.remove(p)
                elif p.rect.top > SCREEN_HEIGHT:
                    powerups.remove(p)

            if total_breakable <= 0:
                win = True
            if not balls:
                game_over = True

        screen.fill(COLOR_BG)
        for brick in bricks:
            brick.draw(screen)
        for ball in balls:
            ball.draw(screen)
        paddle.draw(screen)
        for p in powerups:
            p.draw(screen)

        text = font.render(f"Balls: {len(balls)}  Power-ups: {len(powerups)}", True, COLOR_TEXT)
        screen.blit(text, (10, SCREEN_HEIGHT - 30))

        if game_over:
            msg = font.render("Game Over - Press R to restart", True, COLOR_TEXT)
            screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2))
        elif win:
            msg = font.render("YOU WIN! - Press R to play again", True, COLOR_TEXT)
            screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
