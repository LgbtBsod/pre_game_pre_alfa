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
    surface_list = []

    for _, __, img_files in os.walk(path):
        for image in img_files:
            full_path = path + '/' + image
            surface_list.append(full_path)
    return surface_list


def convert_to_num(value):
    if isinstance(value, str):
        if '%' in value:
            return float(value.replace('%', '')) / 100
        elif value.startswith('+'):
            return float(value[1:])
        elif value.startswith('*'):
            return float(value[1:])
        else:
            try:
                return float(value)
            except ValueError:
                return 0
    return float(value or 0)


def crit_percents(percents):
    percents = str(percents).replace('%', '')
    return int(percents)


def crit_for_upgrade(percents):
    percents = str(percents).replace('%', '')
    return float(percents)