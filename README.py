My First Web 
NO HATE !
<img width="435" height="574" alt="yusuf-removebg-preview" src="https://github.com/user-attachments/assets/649c731e-96b0-44b9-9755-390c8b85fc5f" />
<img width="486" height="388" alt="351b098021042080b530146a2f880887" src="https://github.com/user-attachments/assets/2d70f972-5d97-409a-81bc-b7d5da8bf2bb" />
"""
Predator-Prey Simulation Game (copy-paste and run)
- Requires: pygame (`pip install pygame`)
- Controls:
    SPACE  -> pause / resume
    R      -> reset simulation
    LEFT CLICK  -> add a Sheep (prey)
    RIGHT CLICK -> add a Wolf (predator)
    UP / DOWN   -> increase / decrease simulation speed
- Quick description:
    Simple 2D simulation where sheep wander and reproduce occasionally.
    Wolves chase nearby sheep, eat them to gain energy, and reproduce if energy is high.
    Wolves lose energy over time and die if it hits zero.

Created for Yusuf — ready to copy/paste.
"""

import pygame
import random
import math
import sys

# -------- CONFIG --------
WIDTH, HEIGHT = 900, 600
FPS = 60
NUM_SHEEP = 25
NUM_WOLVES = 6
SHEEP_COLOR = (180, 240, 180)
WOLF_COLOR = (200, 80, 80)
BG_COLOR = (25, 30, 40)

# Behavior parameters
SHEEP_SPEED = 1.3
WOLF_SPEED = 1.8
SHEEP_REPRODUCE_CHANCE = 0.0015  # per frame per sheep
WOLF_REPRODUCE_ENERGY = 140
WOLF_ENERGY_LOSS = 0.08
WOLF_START_ENERGY = 90
ENERGY_GAIN_ON_EAT = 60
WOLF_VISION = 140
SHEEP_VISION = 80

# Misc
MAX_ENTITY_SIZE = 6

# -------- ENTITY CLASSES --------
class Entity:
    def __init__(self, x=None, y=None):
        self.x = random.uniform(0, WIDTH) if x is None else x
        self.y = random.uniform(0, HEIGHT) if y is None else y
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)

    def move(self, speed_multiplier=1.0):
        mag = math.hypot(self.vx, self.vy)
        if mag == 0:
            self.vx, self.vy = random.uniform(-1, 1), random.uniform(-1, 1)
            mag = math.hypot(self.vx, self.vy)
        self.x += (self.vx / mag) * self.speed * speed_multiplier
        self.y += (self.vy / mag) * self.speed * speed_multiplier

        # wrap around edges
        if self.x < 0: self.x += WIDTH
        if self.x > WIDTH: self.x -= WIDTH
        if self.y < 0: self.y += HEIGHT
        if self.y > HEIGHT: self.y -= HEIGHT

class Sheep(Entity):
    def __init__(self, x=None, y=None):
        super().__init__(x, y)
        self.speed = SHEEP_SPEED
        self.size = random.randint(3, MAX_ENTITY_SIZE)

    def behave(self, sheeps, wolves):
        # Simple: wander but avoid close wolves
        avoid_x, avoid_y, count = 0, 0, 0
        for w in wolves:
            dx = self.x - w.x
            dy = self.y - w.y
            d = math.hypot(dx, dy)
            if d < SHEEP_VISION and d > 0:
                avoid_x += dx / d
                avoid_y += dy / d
                count += 1
        if count > 0:
            self.vx += avoid_x
            self.vy += avoid_y
        else:
            # gentle wander
            self.vx += random.uniform(-0.3, 0.3)
            self.vy += random.uniform(-0.3, 0.3)

        # small speed clamp
        vmag = math.hypot(self.vx, self.vy)
        if vmag > 2.5:
            self.vx *= 0.6
            self.vy *= 0.6

class Wolf(Entity):
    def __init__(self, x=None, y=None):
        super().__init__(x, y)
        self.speed = WOLF_SPEED
        self.size = random.randint(4, MAX_ENTITY_SIZE+2)
        self.energy = random.uniform(WOLF_START_ENERGY * 0.7, WOLF_START_ENERGY * 1.1)

    def behave(self, sheeps):
        # Chase closest sheep within vision
        target = None
        target_dist = 10**7
        for s in sheeps:
            dx = s.x - self.x
            dy = s.y - self.y
            d = math.hypot(dx, dy)
            if d < target_dist and d < WOLF_VISION:
                target_dist = d
                target = s
        if target:
            # set velocity toward target
            dx = target.x - self.x
            dy = target.y - self.y
            if dx == 0 and dy == 0:
                dx, dy = random.uniform(-1,1), random.uniform(-1,1)
            self.vx += dx / (target_dist + 1) * 0.9
            self.vy += dy / (target_dist + 1) * 0.9
        else:
            # wander
            self.vx += random.uniform(-0.2, 0.2)
            self.vy += random.uniform(-0.2, 0.2)

        # energy drains
        self.energy -= WOLF_ENERGY_LOSS

        # clamp velocity
        vmag = math.hypot(self.vx, self.vy)
        if vmag > 3.5:
            self.vx *= 0.6
            self.vy *= 0.6

# -------- GAME / SIM SETUP --------
class Simulation:
    def __init__(self):
        self.sheeps = [Sheep() for _ in range(NUM_SHEEP)]
        self.wolves = [Wolf() for _ in range(NUM_WOLVES)]
        self.paused = False
        self.speed_multiplier = 1.0

    def update(self):
        # sheep behavior
        for s in list(self.sheeps):
            s.behave(self.sheeps, self.wolves)
            s.move(self.speed_multiplier)
            # reproduction
            if random.random() < SHEEP_REPRODUCE_CHANCE:
                baby = Sheep(s.x + random.uniform(-6,6), s.y + random.uniform(-6,6))
                self.sheeps.append(baby)

        # wolf behavior
        for w in list(self.wolves):
            w.behave(self.sheeps)
            w.move(self.speed_multiplier)
            # eating
            for s in list(self.sheeps):
                if math.hypot(s.x - w.x, s.y - w.y) < (s.size + w.size):
                    # eat sheep
                    try:
                        self.sheeps.remove(s)
                    except ValueError:
                        pass
                    w.energy += ENERGY_GAIN_ON_EAT
                    break

            # reproduce
            if w.energy > WOLF_REPRODUCE_ENERGY and random.random() < 0.006:
                w.energy *= 0.55
                baby = Wolf(w.x + random.uniform(-8,8), w.y + random.uniform(-8,8))
                self.wolves.append(baby)

            # die
            if w.energy <= 0:
                try:
                    self.wolves.remove(w)
                except ValueError:
                    pass

    def add_sheep(self, x, y):
        self.sheeps.append(Sheep(x, y))

    def add_wolf(self, x, y):
        self.wolves.append(Wolf(x, y))

    def reset(self):
        self.__init__()

# -------- DRAWING / UI --------
def draw_text(screen, text, x, y, size=18):
    font = pygame.font.SysFont('dejavusans', size)
    surf = font.render(text, True, (220,220,220))
    screen.blit(surf, (x, y))

def draw(screen, sim):
    screen.fill(BG_COLOR)
    # draw sheeps
    for s in sim.sheeps:
        pygame.draw.circle(screen, SHEEP_COLOR, (int(s.x), int(s.y)), s.size)
    # draw wolves
    for w in sim.wolves:
        # body
        pygame.draw.circle(screen, WOLF_COLOR, (int(w.x), int(w.y)), w.size)
        # energy bar
        bar_w = int((w.energy / (WOLF_REPRODUCE_ENERGY*1.2)) * 24)
        pygame.draw.rect(screen, (40,40,40), (int(w.x)-12, int(w.y)-w.size-10, 24, 4))
        pygame.draw.rect(screen, (120,220,120), (int(w.x)-12, int(w.y)-w.size-10, max(0, min(24, bar_w)), 4))

    # HUD
    draw_text(screen, f"Sheep: {len(sim.sheeps)}", 8, 6)
    draw_text(screen, f"Wolves: {len(sim.wolves)}", 8, 28)
    draw_text(screen, "SPACE: pause • R: reset • LClick: add sheep • RClick: add wolf", 8, HEIGHT-26, 16)
    draw_text(screen, f"Speed x{sim.speed_multiplier:.2f}", WIDTH-110, 6)

# -------- MAIN LOOP --------

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Predator-Prey Simulation — Yusuf Bhai Edition')
    clock = pygame.time.Clock()

    sim = Simulation()

    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    sim.paused = not sim.paused
                elif event.key == pygame.K_r:
                    sim.reset()
                elif event.key == pygame.K_UP:
                    sim.speed_multiplier = min(3.0, sim.speed_multiplier + 0.1)
                elif event.key == pygame.K_DOWN:
                    sim.speed_multiplier = max(0.2, sim.speed_multiplier - 0.1)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if event.button == 1:
                    sim.add_sheep(x, y)
                elif event.button == 3:
                    sim.add_wolf(x, y)

        if not sim.paused:
            sim.update()

        draw(screen, sim)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
