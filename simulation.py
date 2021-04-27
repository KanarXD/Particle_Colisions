import sys
from math import ceil
from random import randrange
from numpy import array, dot, linalg
import time
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"  # Hides information about pygame
import pygame as PG

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


def run_simulation(ThreadID, WIDTH, HEIGHT, ParticleRadius, ParticleCount, PLAYBACK_SPEED, SIMTIME, FPS, windowed):
    # initialize Pygame
    PG.init()
    SIMTIMECONST = SIMTIME
    if windowed:
        # create window
        screen = PG.display.set_mode((WIDTH, HEIGHT), flags=PG.RESIZABLE)
        PG.display.set_caption("Collisions- " + str(ParticleCount))
        PG.display.set_icon(PG.image.load("graphics/icon.png"))
        # Assets
        CellImage = PG.image.load("graphics/blue_particle.png").convert()
        RingImage = PG.image.load("graphics/red_particle.png").convert()
    # create sprite groups
    all_sprites = PG.sprite.Group()
    all_particles = []

    # Classes
    class Particle(PG.sprite.Sprite):
        def __init__(self, x, y, radius, v):
            PG.sprite.Sprite.__init__(self)
            self.radius = radius
            self.image = PG.Surface((radius * 2, radius * 2))
            if windowed:
                self.image = PG.transform.scale(CellImage, (radius * 2, radius * 2))
                self.image.convert_alpha()
            self.rect = self.image.get_rect()
            self.rect.centerx = x
            self.rect.centery = y
            self.v = v
            self.move = array([0, 0])
            self.mass = 1

        def update(self):
            self.rect.centerx += int(self.v[0]) * PLAYBACK_SPEED
            self.rect.centery += int(self.v[1]) * PLAYBACK_SPEED
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH
                self.v[0] = -self.v[0]
                self.collision(0)
            if self.rect.left < 0:
                self.rect.left = 0
                self.v[0] = -self.v[0]
                self.collision(0)
            if self.rect.bottom > HEIGHT:
                self.rect.bottom = HEIGHT
                self.v[1] = -self.v[1]
                self.collision(0)
            if self.rect.top < 0:
                self.rect.top = 0
                self.v[1] = -self.v[1]
                self.collision(0)

        def collision(self, _):
            pass

    class RedParticle(Particle):
        def __init__(self, x, y, radius, v):
            Particle.__init__(self, x, y, radius, v)
            if windowed:
                self.image = PG.transform.scale(RingImage, (radius * 2, radius * 2))
                self.rect = self.image.get_rect()
            self.timer = time.time()
            self.collisions = self.distance = 0
            self.last_position = array([x, y])

        def collision(self, count):
            self.collisions += count
            position = array([self.rect.centerx, self.rect.centery])
            self.distance += linalg.norm(position - self.last_position)
            self.last_position = position

    # Functions
    def events():
        for event in PG.event.get():
            if event.type == PG.QUIT:
                sys.exit(0)

    def check_collisions():
        for s in range(len(all_particles)):
            for t in range(s + 1, len(all_particles)):
                source = all_particles[s]
                target = all_particles[t]
                min_distance = (source.radius + target.radius) ** 2
                distance = (source.rect.centerx - target.rect.centerx) ** 2 + (
                        source.rect.centery - target.rect.centery) ** 2
                if distance <= min_distance:  # if collision
                    # source.move = target.move = array([0, 0])
                    overlapping(source, target, distance ** 0.5)
                    collision(source, target)
                    target.collision(1)
                    source.collision(1)

    def overlapping(source, target, distance):
        overlap = (source.radius + target.radius - distance) / 2.0
        n = array([target.rect.centerx - source.rect.centerx, target.rect.centery - source.rect.centery]) / distance
        source.rect.centerx -= ceil(overlap * n[0])
        target.rect.centerx += ceil(overlap * n[0])
        source.rect.centery -= ceil(overlap * n[1])
        target.rect.centery += ceil(overlap * n[1])

    def collision(source, target):
        normal = array([target.rect.centerx - source.rect.centerx, target.rect.centery - source.rect.centery])
        tangent = array([-normal[1], normal[0]])
        distance = linalg.norm(normal)
        n = normal / distance
        t = tangent / distance
        dst = dot(source.v, t)
        dtt = dot(target.v, t)
        dsn = dot(source.v, n)
        dtn = dot(target.v, n)
        if source.mass != target.mass:
            source.v = dst * t + (((source.mass - target.mass) * dsn + 2 * target.mass * dtn) /
                                  (source.mass + target.mass)) * n
            target.v = dtt * t + (((target.mass - source.mass) * dtn + 2 * source.mass * dsn) /
                                  (source.mass + target.mass)) * n
        else:
            source.v = dst * t + dtn * n
            target.v = dtt * t + dsn * n

    # Add red Particle
    red_par_init_speed = randrange(5, 10)
    m = RedParticle(0, 0, ParticleRadius,
                    array([red_par_init_speed, red_par_init_speed]))
    all_sprites.add(m)
    all_particles.append(m)
    # Add random Particles
    for i in range(ParticleCount):
        m = Particle(randrange(WIDTH), randrange(HEIGHT), ParticleRadius,
                     array([randrange(-10, 10), randrange(-10, 10)]))
        all_sprites.add(m)
        all_particles.append(m)

    # Game loop
    clock = PG.time.Clock()
    while SIMTIME > 0:
        SIMTIME -= 1
        events()  # Process input (events)
        check_collisions()  # physics
        all_sprites.update()  # physics
        if windowed:
            screen.fill(GREY)
            all_sprites.draw(screen)
            PG.display.flip()
        clock.tick(FPS)
    PG.quit()
    # save Data
    file = open(f"results/result{ParticleCount},{SIMTIMECONST}.txt", "a")
    file.write(f"{all_particles[0].collisions};{int(all_particles[0].distance)}\n")
    file.close()

    print(f"Thread {ThreadID} done")
