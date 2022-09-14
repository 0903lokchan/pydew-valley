from lib2to3.pgen2.pgen import DFAState
from typing import Tuple
import pygame
from pygame.sprite import AbstractGroup
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos: Tuple[int, int], group: AbstractGroup) -> None:
        super().__init__(group)
        
        # general setup
        self.image = pygame.Surface((32, 64))
        self.image.fill('green')
        self.rect = self.image.get_rect(center = pos)
        
        # movement attributes
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200
        
    def input(self) -> None:
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_UP]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0
            
        if keys[pygame.K_LEFT]:
            self.direction.x = -1
        elif keys[pygame.K_RIGHT]:
            self.direction.x = 1
        else:
            self.direction.x = 0
            
            
    def move(self, dt: float) -> None:
        
        # normalising a vector
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
            
        # horizontal movement
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.centerx = self.pos.x # type: ignore
        # vertical movement
        self.pos.y += self.direction.y * self.speed * dt
        self.rect.centery = self.pos.y # type: ignore
        
            
    def update(self, dt: float) -> None:
        self.input()
        self.move(dt)