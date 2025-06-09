# helper/support.py

import os
from csv import reader


def import_csv_layout(path):
    terrain_map = []
    with open(path) as level_map:
        layout = reader(level_map, delimiter=',')
        for row in layout:
            terrain_map.append(list(row))
        return terrain_map


def import_folder(path):
    """Импортирует пути к текстурам из папки"""
    surface_list = []
    for _, __, img_files in os.walk(path):
        for image in img_files:
            full_path = path + '/' + image
            surface_list.append(full_path)
    return surface_list