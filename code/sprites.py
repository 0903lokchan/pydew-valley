from typing import List
from random import randint, choice
import pygame
from settings import *
from pygame.surface import Surface

class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surf: Surface, groups, z:int = LAYERS['main']) -> None:
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = z
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)
        
class Water(Generic):
    def __init__(self, pos, frames, groups) -> None:
        
        # animation setup
        self.frames = frames
        self.frame_index = 0
        
        super().__init__(pos = pos, surf = self.frames[self.frame_index], groups = groups, z = LAYERS['water'])
        
    def animate(self, dt) -> None:
        self.frame_index += 5 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]
        
    def update(self, dt):
        self.animate(dt)
        
class WildFlower(Generic):
    def __init__(self, pos, surf: Surface, groups) -> None:
        super().__init__(pos, surf, groups, LAYERS['main'])
        self.hitbox = self.rect.copy().inflate(-20, -self.rect.height * 0.9) # type: ignore
        
class Tree(Generic):
    def __init__(self, pos, surf: Surface, groups, name: str) -> None:
        super().__init__(pos, surf, groups, LAYERS['main'])
        
        # tree attributes
        self.health = 5
        self.alive = True # type: ignore
        self.stump_surf = pygame.image.load(f'./graphics/stumps/{"small" if name == "Small" else "large"}.png').convert_alpha()
        
        # apples
        self.apples_surf = pygame.image.load('./graphics/fruit/apple.png')
        self.apple_pos = APPLE_POS[name]
        self.apple_sprites = pygame.sprite.Group()
        self.create_fruit()
        
    def damage(self):
        
        # damaging the tree
        self.health -= 1
        
        # remove an apple
        if len(self.apple_sprites.sprites()) > 0:
            random_apple = choice(self.apple_sprites.sprites())
            random_apple.kill()
            
    def check_death(self):
        if self.health <= 0:
            self.image = self.stump_surf
            self.rect = self.image.get_rect(midbottom = self.rect.midbottom) # type: ignore
            self.hitbox = self.rect.copy().inflate(-10, -self.rect.height * 0.6)
            self.alive = False # type: ignore
            
    def update(self, dt) -> None:
        if self.alive:
            self.check_death()
        
    def create_fruit(self):
        for pos in self.apple_pos:
            if randint(0, 10) < 2:
                x = pos[0] + self.rect.left # type: ignore
                y = pos[1] + self.rect.top # type: ignore
                Generic((x, y), self.apples_surf, [self.apple_sprites, self.groups()[0]], LAYERS['fruit'])
        