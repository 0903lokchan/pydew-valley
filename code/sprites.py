import pygame
from settings import *

class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surf: pygame.surface.Surface, groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)