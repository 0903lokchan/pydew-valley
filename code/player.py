import pygame
from pygame.sprite import AbstractGroup
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group: AbstractGroup) -> None:
        super().__init__(group)
        
        self.image = pygame.Surface((32, 64))
        self.image.fill('green')
        self.rect = self.image.get_rect(center = pos)
        