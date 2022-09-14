from typing import Tuple
import pygame
from pygame.sprite import AbstractGroup
from timer import Timer
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
        
        # timers
        self.timers = {
            'tool use': Timer(350, self.use_tool)
        }
        
        # tools
        self.selected_tool = 'axe'
        
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
        
        if not self.timers['tool use'].active:
            # directions
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
            
        # tool use
        if keys[pygame.K_SPACE]:
            # timer for the tool use
            self.timers['tool use'].activate()
            self.direction = pygame.math.Vector2()
            self.frame_index = 0
            
    def get_status(self) -> None:
        
        # idle
        if self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_idle'
            
        # use tool
        if self.timers['tool use'].active:
            self.status = self.status.split('_')[0] + '_' + self.selected_tool
            
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
    
    def use_tool(self) -> None:
        print(self.selected_tool)
            
    def update_timers(self) -> None:
        for timer in self.timers.values():
            timer.update()
    
    def update(self, dt: float) -> None:
        self.input()
        self.get_status()
        self.update_timers()
        self.move(dt)
        self.animate(dt)