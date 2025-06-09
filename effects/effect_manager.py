# effects/effect_manager.py

from ursina import invoke


def apply_strength_boost(player, duration=60):
    """Добавляет силу на время"""
    player.buff_manager.add_percent_stat('strength', 0.3, duration)


def effect_on_dodge(player, amount, attack_type):
    """Эффект срабатывает при увороте от урона"""
    print('[Эффект] Уворот!')
    player.position += Vec2(50, 0)
    invoke(lambda: setattr(player, 'can_move', True), delay=0.3)
    player.can_move = False
    return amount * 0.5  # уменьшаем урон на 50%


def activate_power(player):
    """Активация временного усиления атаки"""
    print('[Эффект] Power Boost активирован')
    player.buff_manager.add_percent_stat('attack', 0.3, 10)  # +30% к атаке на 10 секунд


def apply_regeneration(player, interval=1, duration=60):
    """Восстановление здоровья раз в N секунд"""

    def regen():
        if player.health < player.current_stats['max_health']:
            player.health += player.current_stats['hp_regen']
            invoke(regen, delay=interval)

    regen()
    invoke(lambda: player.buff_manager.remove_buff('regeneration'), delay=duration)