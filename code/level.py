import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Interaction, Water, WildFlower, Tree
from pytmx.util_pygame import load_pygame
from support import *
from transition import Transition
from soil import SoilLayer

class Level:
    def __init__(self) -> None:

        # get the display surface
        self.display_surface = pygame.display.get_surface()

        # sprite groups
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()

        self.soil_layer = SoilLayer(self.all_sprites)
        self.setup()
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset, self.player)

    def setup(self) -> None:
        tmx_data = load_pygame('./data/map.tmx')
        
        # house
        for layer in ['HouseFloor', 'HouseFurnitureBottom']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])
                
        for layer in ['HouseWalls', 'HouseFurnitureTop']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['main'])
                
        # fence
        for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprites], LAYERS['main'])
                
        # water
        water_frames = import_folder('./graphics/water')
        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites)
        
        # trees
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree(pos = (obj.x, obj.y), 
                 surf = obj.image, 
                 groups = [self.all_sprites, self.collision_sprites, self.tree_sprites], 
                 name = obj.name, 
                 player_add = self.player_add)
        
        # wildflowers
        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])
            
        # collision tiles
        for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), self.collision_sprites)
        
        # player
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player(
                    pos = (obj.x, obj.y), 
                    group = self.all_sprites, 
                    collision_sprites = self.collision_sprites, 
                    tree_sprites = self.tree_sprites,
                    interaction = self.interaction_sprites,
                    soil_layer = self.soil_layer
                )
            if obj.name == 'Bed':
                Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)
          
        # ground  
        Generic(
              pos = (0, 0),
            surf = pygame.image.load('./graphics/world/ground.png').convert_alpha(),
            groups = self.all_sprites,
            z = LAYERS['ground']
          )
    
    def player_add(self, item: str, amount: int=1):
        self.player.item_inventory[item] += amount
        
    def reset(self):
        
        # apples on the trees
        for tree in self.tree_sprites.sprites():
            for apple in tree.apple_sprites.sprites(): # type: ignore
                apple.kill()
            tree.create_fruit() # type: ignore

    def run(self,dt: float) -> None:
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)
        self.all_sprites.update(dt)
        

        self.overlay.display()
        
        if self.player.sleep:
            self.transition.play()

class CameraGroup(pygame.sprite.Group):
    def __init__(self) -> None:
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player) -> None:
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2
        
        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery): # type: ignore
                if sprite.z == layer: # type: ignore
                    offset_rect = sprite.rect.copy() # type: ignore
                    offset_rect.center -= self.offset # type: ignore
                    self.display_surface.blit(sprite.image, offset_rect) # type: ignore
                    
        # # analytics
        #             if sprite == player:
        #                 pygame.draw.rect(self.display_surface, 'red', offset_rect, 5)
        #                 hitbox_rect = player.hitbox.copy()
        #                 hitbox_rect.center = offset_rect.center
        #                 pygame.draw.rect(self.display_surface, 'green', hitbox_rect, 5)
        #                 target_pos = offset_rect.center + PLAYER_TOOL_OFFSET[player.status.split('_')[0]]
        #                 pygame.draw.circle(self.display_surface, 'blue', target_pos, 5)