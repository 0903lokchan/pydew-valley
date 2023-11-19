from random import choice
import pygame
from pygame.sprite import Sprite, Group
from typing import Callable
from settings import *
from pytmx.util_pygame import load_pygame
from support import import_folder_dict, import_folder


class SoilTile(Sprite):
    def __init__(
        self,
        pos: tuple[float, float],
        surf: pygame.Surface,
        groups: list[Group],
    ) -> None:
        super().__init__(*groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS["soil"]


class WaterTile(Sprite):
    def __init__(
        self,
        pos: tuple[float, float],
        surf: pygame.Surface,
        groups: list[Group],
    ) -> None:
        super().__init__(*groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS["soil water"]


class Plant(Sprite):
    def __init__(
        self,
        plant_type: str,
        soil: Sprite,
        check_watered: Callable[[tuple[float, float]], bool],
        groups: list[Group],
    ) -> None:
        super().__init__(*groups)

        # setup
        self.plant_type = plant_type
        self.frames = import_folder(f"./graphics/fruit/{plant_type}")
        self.soil = soil
        self.check_watered = check_watered

        # plant growing
        self.age = 0
        self.max_age = len(self.frames) - 1
        self.grow_speed = GROW_SPEED[plant_type]
        self.harvestable = False

        # sprite setup
        self.image = self.frames[self.age]
        self.y_offset = -16 if plant_type == "corn" else -8
        self.rect = self.image.get_rect(midbottom=soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))  # type: ignore
        self.z = LAYERS["ground plant"]

    def grow(self) -> None:
        if self.age >= self.max_age:
            return

        if not self.rect:
            raise ValueError("Plant {self} does not have a rect")
        if self.check_watered(self.rect.center):
            self.age += self.grow_speed
            self.image = self.frames[int(self.age)]

            # Update rect to fit new image
            self.rect = self.image.get_rect(midbottom=self.soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))  # type: ignore

            # Move plant to the main layer so it collides with the character
            if self.age >= 1:
                self.z = LAYERS["main"]
                self.hitbox = self.rect.copy().inflate(-26, -self.rect.height * 0.4)

            if self.age >= self.max_age:
                self.age = self.max_age
                self.harvestable = True


class SoilLayer:
    def __init__(self, all_sprites: Group, collision_sprites: Group) -> None:
        # sprite groups
        self.all_sprites = all_sprites
        self.collision_sprites = collision_sprites
        self.soil_sprites = Group()
        self.water_sprites = Group()
        self.plant_sprites = Group()

        # graphics
        self.soil_surfs = import_folder_dict("./graphics/soil/")
        self.water_surfs = import_folder("./graphics/soil_water/")

        self.create_soil_grid()
        self.create_hit_rects()
        self.raining = False

        # sounds
        self.hoe_sound = pygame.mixer.Sound("./audio/hoe.wav")
        self.hoe_sound.set_volume(0.1)
        self.plant_sound = pygame.mixer.Sound("./audio/plant.wav")
        self.plant_sound.set_volume(0.2)

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
                    if self.raining:
                        self.water_all()

    @staticmethod
    def get_sprite_grid_coord(sprite: Sprite) -> tuple[int, int]:
        if not sprite.rect:
            raise ValueError("Sprite {sprite} does not have a rect attribute!")

        if isinstance(sprite, Plant):
            x = sprite.rect.centerx // TILE_SIZE
            y = sprite.rect.centery // TILE_SIZE
            return (x, y)

        x = sprite.rect.x // TILE_SIZE
        y = sprite.rect.y // TILE_SIZE
        return (x, y)

    @staticmethod
    def get_pos_grid_coord(pos: tuple[float, float]) -> tuple[int, int]:
        x = int(pos[0] // TILE_SIZE)
        y = int(pos[1] // TILE_SIZE)
        return (x, y)

    def water(self, target_pos: tuple[int, int]) -> None:
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):  # type: ignore
                # 1. add an entry to the soil grid -> 'W'
                x, y = self.get_sprite_grid_coord(soil_sprite)
                self.grid[y][x].append("W")
                # 2. create a water sprite
                pos = soil_sprite.rect.topleft  # type: ignore
                surf = choice(self.water_surfs)
                WaterTile(pos, surf, [self.all_sprites, self.water_sprites])

    def water_all(self) -> None:
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if "X" in cell and "W" not in cell:
                    cell.append("W")
                    x = index_col * TILE_SIZE
                    y = index_row * TILE_SIZE
                    WaterTile(
                        (x, y),
                        choice(self.water_surfs),
                        [self.all_sprites, self.water_sprites],
                    )

    def remove_water(self):
        # destroy all water sprites
        for sprite in self.water_sprites.sprites():
            sprite.kill()
        # clean up the grid
        for row in self.grid:
            for cell in row:
                if "W" in cell:
                    cell.remove("W")

    def check_watered(self, pos: tuple[float, float]) -> bool:
        x, y = self.get_pos_grid_coord(pos)
        return "W" in self.grid[y][x]

    def plant_seed(self, target_pos: tuple[float, float], seed: str) -> None:
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):  # type: ignore
                x, y = self.get_sprite_grid_coord(soil_sprite)

                if "P" not in self.grid[y][x]:
                    self.grid[y][x].append("P")
                    Plant(
                        plant_type=seed,
                        soil=soil_sprite,
                        check_watered=self.check_watered,
                        groups=[
                            self.all_sprites,
                            self.plant_sprites,
                            self.collision_sprites,
                        ],
                    )

    def update_plants(self) -> None:
        for plant in self.plant_sprites.sprites():
            plant.grow()  # type: ignore

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
