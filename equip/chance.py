# equip/chance.py

import random
from helper.settings import *


def lower_zero(num):
    count = 1
    while True:
        if num * (10 ** count) < 1:
            count += 1
            continue
        else:
            break
    return count, num


def check(num):
    if num > round(num):
        num = round(num) + 1
    return num


def get_random(num_to_list, zeros):
    chance_list = []
    if zeros == 0:
        border = 100
    else:
        border = (10 ** zeros)

    while len(chance_list) < num_to_list:
        num = random.randint(0, border)
        if num in chance_list:
            num = random.randint(0, border)
        else:
            chance_list.append(num)

    check = random.randint(0, border)
    return check in chance_list


def chance(percents):
    try:
        percents = percents.replace('%', '')
    except:
        pass

    try:
        percents = int(percents)
    except ValueError:
        percents = float(percents)

    if isinstance(percents, float):
        if percents < 1:
            zeros, num_to_list = lower_zero(percents)
            num_to_list = check(num_to_list)
        else:
            zeros = 0
            num_to_list = check(percents)
    else:
        zeros = 0
        num_to_list = percents

    return get_random(num_to_list, zeros)


def weighted_chance(options):
    """
    Взвешенный шанс для сложных случаев.
    Пример:
    options = {
        'win': 0.7,
        'lose': 0.3
    }
    """
    total_weight = sum(options.values())
    rand = random.uniform(0, total_weight)
    current = 0
    for key, weight in options.items():
        current += weight
        if rand <= current:
            return key