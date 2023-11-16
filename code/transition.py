import pygame
from player import Player
from settings import *


class Transition:
    def __init__(self, reset, player: Player) -> None:
        # setup
        self.display_surface = pygame.display.get_surface()
        self.reset = reset
        self.player = player

        # overlay image
        self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.color = 255
        self.speed = -2

    def play(self):
        self.color += self.speed
        if self.color <= 0:
            # 1. call reset
            self.reset()
            self.speed *= -1
            self.color = 0
        if self.color > 255:
            self.color = 255
            # 2. wake up the player
            self.player.sleep = False
            # 3. set the speed to -2 at the end of the transition
            self.speed *= -1
        self.image.fill((self.color, self.color, self.color))
        self.display_surface.blit(
            self.image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT
        )
