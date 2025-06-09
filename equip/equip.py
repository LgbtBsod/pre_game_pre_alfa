# equip/equip.py

from helper.settings import artifacts
from player import Player
from equip.chance import chance
from helper.support import convert_to_num


def get_base(player: Player):
    """Возвращает базовые параметры игрока"""
    base_stat = {}
    for stat in player.base:
        base_stat[stat] = player.base[stat]
    return base_stat


def return_stats(stat_dict, current_stats):
    """
    Возвращает бонусы от экипировки
    :param stat_dict: словарь с атрибутами предмета
    :param current_stats: текущие статы игрока
    :return: словарь с бонусами
    """
    must_be_plused = {
        'health': 0,
        'attack': 0,
        'magic': 0,
        'agility': 0,
        'hp_regen': 0,
        'speed': 0,
        'stamina': 0,
        'energy': 0,
        'strength': 0,
        'crit_rate': 0,
        'crit_chance': 0
    }

    for item in stat_dict:
        if item in ['crit_rate', 'crit_chance']:
            must_be_plused[item] = stat_dict[item]
        else:
            must_be_plused[item] += stat_dict[item]

    # Преобразуем проценты в числа
    for stat in must_be_plused:
        if '%' in str(must_be_plused[stat]):
            must_be_plused[stat] = convert_to_num(must_be_plused[stat])

    return must_be_plused


def current_stats(must_be_plused, current_stats):
    """Применяет бонусы к текущей стате"""
    for stat in must_be_plused:
        if stat in ['crit_rate', 'crit_chance']:
            current_stats[stat] = must_be_plused[stat] + current_stats.get(stat, 0)
        else:
            current_stats[stat] *= must_be_plused[stat]

    print("Обновлённые статы:", current_stats)
    return current_stats