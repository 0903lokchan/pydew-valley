import pygame
from pygame.surface import Surface
from settings import *
from typing import Callable
from player import Player
from game_timer import Timer


class Menu:
    def __init__(self, player: Player, toggle_menu: Callable[[], None]) -> None:
        # general setup
        self.player = player
        self.toggle_menu = toggle_menu
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font("./font/LycheeSoda.ttf", 30)

        # options
        self.width = 400
        self.space = 10
        self.padding = 8

        # entries
        self.options = list(self.player.item_inventory.keys()) + list(
            self.player.seed_inventory.keys()
        )
        self.sell_border = len(self.player.item_inventory) - 1
        self.setup()
        
        # movement
        self.index = 0
        self.timer = Timer(200)
        
    def display_money(self):
        text_surf = self.font.render(f"${self.player.money}", False, "Black")
        text_rect = text_surf.get_rect(midbottom = (SCREEN_WIDTH / 2, SCREEN_HEIGHT - 20))
        
        pygame.draw.rect(self.display_surface, 'White', text_rect.inflate(10, 10), 0, 4)
        self.display_surface.blit(text_surf, text_rect)

    def setup(self) -> None:
        self.text_surfs = []
        self.total_height = 0
        for item in self.options:
            text_surf = self.font.render(item, False, "Black")
            self.text_surfs.append(text_surf)
            self.total_height += text_surf.get_height() + (self.padding * 2)

        self.total_height += (len(self.text_surfs) - 1) * self.space
        self.menu_top = (SCREEN_HEIGHT - self.total_height) / 2
        self.menu_left = (SCREEN_WIDTH - self.width) / 2
        self.main_rect = pygame.Rect(
            self.menu_left, self.menu_top, self.width, self.total_height
        )

    def input(self):
        keys = pygame.key.get_pressed()
        self.timer.update()

        if keys[pygame.K_ESCAPE]:
            self.toggle_menu()
            
        if not self.timer.active:
            if keys[pygame.K_UP] and not self.index == 0:
                self.index -= 1
                self.timer.activate()
            
            if keys[pygame.K_DOWN]and not self.index == len(self.options):
                self.index += 1
                self.timer.activate()
    
    def show_entry(self, text_surf: pygame.Surface, amount: int, top: int, selected: bool)-> None:
        # background
        bg_rect = pygame.Rect(self.main_rect.left, top, self.width, text_surf.get_height() + (self.padding * 2))
        pygame.draw.rect(self.display_surface, 'White', bg_rect, 0, 4)
        
        # text
        text_rect = text_surf.get_rect(midleft = (self.main_rect.left + 20, bg_rect.centery))
        self.display_surface.blit(text_surf, text_rect)
        
        # amount
        amount_surf = self.font.render(str(amount), False, 'Black')
        amount_rect = amount_surf.get_rect(midright = (self.main_rect.right - 20, bg_rect.centery))
        self.display_surface.blit(amount_surf, amount_rect)
        
        # selected
        if selected:
            pygame.draw.rect(self.display_surface, 'black', bg_rect, 4, 4)

    def update(self):
        self.input()
        self.display_money()
        for text_index, text_surf in enumerate(self.text_surfs):
            top = self.main_rect.top + text_index * (text_surf.get_height() + (self.padding * 2) + self.space)
            amount_list = list(self.player.item_inventory.values()) + list(self.player.seed_inventory.values())
            selected = text_index == self.index
            self.show_entry(text_surf, amount_list[text_index], top=top, selected=selected)
            
