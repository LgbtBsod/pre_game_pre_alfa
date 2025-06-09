# helper/settings.py

import json
import os


def load_json(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f'Файл {path} не найден!')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


# Загрузка универсальных настроек
SETTINGS = load_json('assets/settings.json')
GAME_SETTINGS = SETTINGS['game']
HITBOX_OFFSET = SETTINGS['hitbox_offset']
UI_SETTINGS = SETTINGS['ui']
COLORS = SETTINGS['colors']

# Оружие
WEAPON_DATA = load_json('assets/weapons.json')

# Враги
MONSTER_DATA = load_json('assets/monsters.json')

MAGIC_DATA = load_json('assets/magic.json')