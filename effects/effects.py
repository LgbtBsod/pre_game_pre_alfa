# effects/effects.py

from ursina import time, invoke


def apply_percent_buff(player, stat, value, duration):
    """Увеличивает значение стата на процент"""
    base = player.current_stats[stat]
    player.current_stats[stat] *= (1 + value)
    print(f'[Эффект] {stat} увеличен на {int(value * 100)}%: {base} → {player.current_stats[stat]}')
    if duration > 0:
        invoke(lambda: reset_stat(player, stat, base), delay=duration)


def apply_flat_buff(player, stat, value, duration):
    """Добавляет значение к стату"""
    player.current_stats[stat] += value
    print(f'[Эффект] {stat} увеличен на {value}: {player.current_stats[stat] - value} → {player.current_stats[stat]}')
    if duration > 0:
        invoke(lambda: reset_stat(player, stat, player.current_stats[stat] - value), delay=duration)


def apply_multiply_buff(player, stat, value, duration):
    """Умножает значение стата"""
    base = player.current_stats[stat]
    player.current_stats[stat] *= value
    print(f'[Эффект] {stat} умножен на {value}: {base} → {player.current_stats[stat]}')
    if duration > 0:
        invoke(lambda: reset_stat(player, stat, base), delay=duration)


def reset_stat(player, stat, value):
    """Сбрасывает стат к исходному значению"""
    player.current_stats[stat] = value
    print(f'[BUFF] {stat} восстановлено: {value}')