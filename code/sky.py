import pygame
from pygame.surface import Surface
from settings import *
from support import import_folder
from sprites import Generic
from random import randint, choice


class Drop(Generic):
    def __init__(self, pos, surf: Surface, moving: bool, groups, z: int) -> None:
        # general setup
        super().__init__(pos, surf, groups, z)
        self.lifetime = randint(400, 500)
        self.start_time = pygame.time.get_ticks()

        # moving
        self.moving = moving
        if self.moving:
            self.pos = pygame.math.Vector2(self.rect.topleft)  # type: ignore
            self.direction = pygame.math.Vector2(-2, 4)
            self.speed = randint(200, 250)

    def update(self, dt: float) -> None:
        # movement
        if self.moving:
            self.pos += self.direction * self.speed * dt
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))  # type: ignore

        # timer
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()


class Rain:
    def __init__(self, all_sprites: pygame.sprite.Group) -> None:
        self.all_sprites = all_sprites
        self.rain_drops = import_folder("./graphics/rain/drops/")
        self.rain_floor = import_folder("./graphics/rain/floor/")
        self.floor_w, self.floor_h = pygame.image.load(
            "./graphics/world/ground.png"
        ).get_size()

    def create_floor(self):
        Drop(
            surf=choice(self.rain_floor),
            pos=(randint(0, self.floor_w), randint(0, self.floor_h)),
            moving=False,
            groups=self.all_sprites,
            z=LAYERS["rain floor"],
        )

    def create_drops(self):
        Drop(
            surf=choice(self.rain_drops),
            pos=(randint(0, self.floor_w), randint(0, self.floor_h)),
            moving=True,
            groups=self.all_sprites,
            z=LAYERS["rain drops"],
        )

    def update(self):
        self.create_floor()
        self.create_drops()
