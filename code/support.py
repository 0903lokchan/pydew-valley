from os import walk
import pygame


def import_folder(path: str) -> list[pygame.Surface]:
    """Import all images within a directory and return them as a list of Pygame surfaces

    Args:
        path (str): path to directory

    Returns:
        list[pygame.Surface]: list of images loaded as Pygame Surface
    """

    surface_list = []

    for _, _, img_files in walk(path):
        for image in img_files:
            full_path = path + "/" + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)

    return surface_list


def import_folder_dict(path: str) -> dict[str, pygame.Surface]:
    """Import all images within a directory and return them as a dict of filenames and Pygame surfaces

    Args:
        path (str): path to directory

    Returns:
        dict[str, pygame.Surface]: dict of images loaded as Pygame Surface with filename without extension as key
    """
    surface_dict = {}

    for _, _, img_files in walk(path):
        for image in img_files:
            full_path = path + "/" + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_dict[image.split(".")[0]] = image_surf

    return surface_dict
