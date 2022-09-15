from typing import List
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
        