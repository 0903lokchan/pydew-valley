from typing import Callable
import pygame

class Timer:
    def __init__(self, duration: float, func:Callable[[], None]|None = None) -> None:
        self.duration = duration
        self.func = func
        self.start_time = 0
        self.active = False
        
    def activate(self) -> None:
        self.active = True
        self.start_time = pygame.time.get_ticks()
        
    def deactivate(self) -> None:
        self.active = False
        self.start_time = 0
        
    def update(self) -> None:
        curren_time = pygame.time.get_ticks()
        if curren_time - self.start_time >= self.duration:
            self.deactivate()
            if self.func:
                self.func()
            