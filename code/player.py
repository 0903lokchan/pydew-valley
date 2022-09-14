from typing import Tuple
import pygame
from pygame.sprite import AbstractGroup
from settings import *
from support import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos: Tuple[int, int], group: AbstractGroup) -> None:
        super().__init__(group)
        
        self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0
        
        # general setup
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center = pos)
        
        # movement attributes
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200
        
    def import_assets(self) -> None:
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
                           'right_hoe': [], 'left_hoe': [], 'up_hoe': [], 'down_hoe': [],
                           'right_axe': [], 'left_axe': [], 'up_axe': [], 'down_axe': [],
                           'right_water': [], 'left_water': [], 'up_water': [], 'down_water': []
                           }
        
        for animation in self.animations.keys():
            full_path = './graphics/character/' + animation
            self.animations[animation] = import_folder(full_path)
        
    def animate(self, dt):
        self.frame_index += 4 * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0
        self.image = self.animations[self.status][int(self.frame_index)]
        
        
    def input(self) -> None:
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_UP]:
            self.direction.y = -1
            self.status = 'up'
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
            self.status = 'down'
        else:
            self.direction.y = 0
            
        if keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.status = 'left'
        elif keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.status = 'right'
        else:
            self.direction.x = 0
            
    def get_status(self) -> None:
        # if the player is not moving, add _idle to the status
        if not self.status.endswith('_idle') and self.direction.magnitude() == 0:
            self.status += '_idle'
            
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
        self.get_status()
        self.move(dt)
        self.animate(dt)