from random import choice
import pygame
from pygame.sprite import AbstractGroup
from settings import *
from pytmx.util_pygame import load_pygame
from support import import_folder_dict, import_folder


class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups) -> None:
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS["soil"]

class WaterTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, *groups) -> None:
        super().__init__(*groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['soil water']

class SoilLayer:
    def __init__(self, all_sprites: AbstractGroup) -> None:
        # sprite groups
        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()

        # graphics
        self.soil_surfs = import_folder_dict("./graphics/soil/")
        self.water_surfs = import_folder("./graphics/soil_water/")

        self.create_soil_grid()
        self.create_hit_rects()

        # requirements
        # if the area is farmable
        # if the soil has been watered
        # if the soil has a plant

    def create_soil_grid(self) -> None:
        ground = pygame.image.load("./graphics/world/ground.png")
        h_tiles, v_tiles = (
            ground.get_width() // TILE_SIZE,
            ground.get_height() // TILE_SIZE,
        )

        self.grid = [[[] for col in range(h_tiles)] for row in range(v_tiles)]
        for x, y, _ in (
            load_pygame("./data/map.tmx").get_layer_by_name("Farmable").tiles()
        ):
            self.grid[y][x].append("F")

    def create_hit_rects(self) -> None:
        self.hit_rects: list[pygame.Rect] = []
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if "F" in cell:
                    x = index_col * TILE_SIZE
                    y = index_row * TILE_SIZE
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    self.hit_rects.append(rect)

    def get_hit(self, point) -> None:
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE

                if "F" in self.grid[y][x]:
                    self.grid[y][x].append("X")
                    self.create_soil_tiles()
                    
    def water(self, target_pos: tuple[int, int])-> None:
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos): # type: ignore
                # 1. add an entry to the soil grid -> 'W'
                x = soil_sprite.rect.x // TILE_SIZE # type: ignore
                y = soil_sprite.rect.y // TILE_SIZE # type: ignore
                self.grid[y][x].append('W')
                # 2. create a water sprite
                pos = soil_sprite.rect.topleft # type: ignore
                surf = choice(self.water_surfs)
                WaterTile(pos, surf, [self.all_sprites, self.water_sprites])
                
    def remove_water(self):
        # destroy all water sprites
        for sprite in self.water_sprites.sprites():
            sprite.kill()
        # clean up the grid
        for row in self.grid:
            for cell in row:
                if 'W' in cell:
                    cell.remove('W')

    def create_soil_tiles(self) -> None:
        self.soil_sprites.empty()
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if "X" in cell:
                    # tile options
                    t = "X" in self.grid[index_row - 1][index_col]
                    b = "X" in self.grid[index_row + 1][index_col]
                    r = "X" in row[index_col + 1]
                    l = "X" in row[index_col - 1]

                    tile_type = "o"

                    # all sides
                    if all((t, b, l, r)):
                        tile_type = "x"

                    # horizontal tiles only
                    if l and not any((t, b, r)):
                        tile_type = "r"
                    if r and not any((t, b, l)):
                        tile_type = "l"
                    if r and l and not any((t, b)):
                        tile_type = "lr"

                    # vertical tiles only
                    if t and not any((b, l, r)):
                        tile_type = "b"
                    if b and not any((t, l, r)):
                        tile_type = "t"
                    if t and b and not any((l, r)):
                        tile_type = "tb"

                    # corners
                    if l and b and not any((t, r)):
                        tile_type = "tr"
                    if r and b and not any((t, l)):
                        tile_type = "tl"
                    if l and t and not any((b, r)):
                        tile_type = "br"
                    if r and t and not any((b, l)):
                        tile_type = "bl"

                    # t-shapes
                    if all((t, b, l)) and not r:
                        tile_type = "tbl"
                    if all((t, b, r)) and not l:
                        tile_type = "tbr"
                    if all((b, l, r)) and not t:
                        tile_type = "lrt"
                    if all((t, l, r)) and not b:
                        tile_type = "lrb"

                    SoilTile(
                        pos=(index_col * TILE_SIZE, index_row * TILE_SIZE),
                        surf=self.soil_surfs[tile_type],
                        groups=[self.all_sprites, self.soil_sprites],
                    )
