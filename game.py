import pygame
import sys
import random

# ─── Configuration ────────────────────────────────────────────────────────────
CELL          = 20
GAME_WIDTH    = 600
SIDEBAR_WIDTH = 200
WIDTH         = GAME_WIDTH + SIDEBAR_WIDTH
HEIGHT        = 600
FPS_LEVELS    = {
    1: 5,   # Beginner
    2: 8,   # Intermediate
    3: 10,  # Advanced
}
LOOP_FPS      = 30  # fixed loop rate for responsive input
MOVE_EVENT    = pygame.USEREVENT + 1
MAX_BAR_LEN   = 50  # when score reaches this, bar is “full”

# ─── Colors ─────────────────────────────────────────────────────────────────
BLACK        = (0, 0, 0)
WHITE        = (255, 255, 255)
GREEN        = (0, 200, 0)
RED          = (200, 0, 0)
DARK_GRAY    = (40, 40, 40)
SIDEBAR_BG   = (20, 20, 20)
BAR_COLOR    = (0, 100, 200)
BUTTON_BG    = (60, 60, 60)
BUTTON_HOVER = (100, 100, 100)

# ─── Pygame Init ─────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock  = pygame.time.Clock()
pygame.display.set_caption("Snake Game")

# Cursors
ARROW_CURSOR = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)
HAND_CURSOR  = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND)

# Load sounds
try:
    pygame.mixer.music.load('bg_music.wav')
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)
except Exception:
    pass
try:
    eat_sound = pygame.mixer.Sound('eat_sound.wav')
    eat_sound.set_volume(1.0)
except Exception:
    eat_sound = None

# Fonts
title_font = pygame.font.SysFont(None, 72)
menu_font  = pygame.font.SysFont(None, 36)
game_font  = pygame.font.SysFont(None, 24)


def show_start_screen(high_score):
    button_w, button_h = 300, 50
    x = (WIDTH - button_w) // 2
    base_y = HEIGHT // 2
    ys = [base_y - button_h - 20, base_y, base_y + button_h + 20]
    labels = [("Beginner (5 FPS)", 1), ("Intermediate (8 FPS)", 2), ("Advanced (10 FPS)", 3)]
    buttons = [pygame.Rect(x, y, button_w, button_h) for y in ys]

    while True:
        mx, my = pygame.mouse.get_pos()
        hovering = any(rect.collidepoint((mx, my)) for rect in buttons)
        pygame.mouse.set_cursor(HAND_CURSOR if hovering else ARROW_CURSOR)
        screen.fill(BLACK)
        # Title & high-score
        screen.blit(title_font.render("SNAKE GAME", True, WHITE), title_font.render("SNAKE GAME", True, WHITE).get_rect(center=(WIDTH//2, HEIGHT//4)))
        hs_text = f"HI-SCORE: {high_score}" if high_score > 0 else "HI-SCORE: --"
        screen.blit(menu_font.render(hs_text, True, WHITE), menu_font.render(hs_text, True, WHITE).get_rect(center=(WIDTH//2, HEIGHT//4+60)))
        # Buttons
        for rect, (text, lvl) in zip(buttons, labels):
            color = BUTTON_HOVER if rect.collidepoint((mx, my)) else BUTTON_BG
            pygame.draw.rect(screen, color, rect, border_radius=5)
            screen.blit(menu_font.render(text, True, WHITE), menu_font.render(text, True, WHITE).get_rect(center=rect.center))
        # Hint
        screen.blit(game_font.render("Press 1/2/3 or click to select level", True, DARK_GRAY), game_font.render("Press 1/2/3 or click to select level", True, DARK_GRAY).get_rect(center=(WIDTH//2, HEIGHT-40)))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                for rect, (_, lvl) in zip(buttons, labels):
                    if rect.collidepoint(e.pos):
                        return FPS_LEVELS[lvl]
            elif e.type == pygame.KEYDOWN and e.unicode in ('1','2','3'):
                return FPS_LEVELS[int(e.unicode)]

class Snake:
    def __init__(self):
        self.reset()
    def reset(self):
        self.body = [(GAME_WIDTH//2, HEIGHT//2)]
        self.dir  = (0, -CELL)
    def move(self):
        head = self.body[0]
        new_head = (head[0]+self.dir[0], head[1]+self.dir[1])
        self.body.insert(0, new_head)
        self.body.pop()
    def grow(self):
        self.body.append(self.body[-1])
    def change_dir(self, nd):
        if nd[0]==-self.dir[0] and nd[1]==-self.dir[1]: return
        self.dir = nd
    def check_collision(self):
        head = self.body[0]
        return not (0<=head[0]<GAME_WIDTH and 0<=head[1]<HEIGHT) or head in self.body[1:]

class Food:
    def __init__(self): self.randomize()
    def randomize(self):
        cols, rows = GAME_WIDTH//CELL, HEIGHT//CELL
        self.pos = (random.randrange(cols)*CELL, random.randrange(rows)*CELL)


def main():
    high_score = 0
    snake = Snake()
    food = Food()
    score = 0
    fps = LOOP_FPS
    while True:
        lvl_fps = show_start_screen(high_score)
        pygame.time.set_timer(MOVE_EVENT, int(1000/lvl_fps))
        snake.reset(); food.randomize(); score=0

        running = True
        while running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif e.type == MOVE_EVENT:
                    snake.move()
                    if snake.check_collision():
                        high_score = max(high_score, score)
                        running=False
                    elif snake.body[0]==food.pos:
                        snake.grow(); score+=1; food.randomize()
                        if eat_sound: eat_sound.play()
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_UP:    snake.change_dir((0, -CELL))
                    if e.key == pygame.K_DOWN:  snake.change_dir((0,  CELL))
                    if e.key == pygame.K_LEFT:  snake.change_dir((-CELL, 0))
                    if e.key == pygame.K_RIGHT: snake.change_dir((CELL, 0))
            # Continuous drawing & input hover
            screen.fill(BLACK)
            for x in range(0, GAME_WIDTH, CELL): pygame.draw.line(screen, DARK_GRAY, (x,0),(x,HEIGHT))
            for y in range(0, HEIGHT, CELL): pygame.draw.line(screen, DARK_GRAY, (0,y),(GAME_WIDTH,y))
            for block in snake.body: pygame.draw.rect(screen, GREEN, (*block,CELL,CELL))
            pygame.draw.rect(screen, RED, (*food.pos,CELL,CELL))
            pygame.draw.rect(screen, SIDEBAR_BG, (GAME_WIDTH,0,SIDEBAR_WIDTH,HEIGHT))
            screen.blit(game_font.render(f"SCORE: {score}",True,WHITE),(GAME_WIDTH+20,20))
            screen.blit(game_font.render(f"HI-SCORE: {high_score}",True,WHITE),(GAME_WIDTH+20,60))
            bar_len = min(score, MAX_BAR_LEN)
            screen.blit(game_font.render('',True,WHITE),(0,0))
            bar_w = int(bar_len/MAX_BAR_LEN*(SIDEBAR_WIDTH-40))
            pygame.draw.rect(screen, BAR_COLOR, (GAME_WIDTH+20,100,bar_w,20))
            pygame.display.flip()
            clock.tick(LOOP_FPS)

if __name__ == "__main__": main()

