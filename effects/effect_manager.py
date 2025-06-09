# effects/effect_manager.py

from ursina import time, invoke


def apply_strength_boost(player, duration=60):
    print('[Эффект] Сила увеличена')
    player.buff_manager.add_flat_stat('strength', 10, duration)


def effect_on_dodge(player, amount, attack_type):
    print('[Эффект] Уворот!')
    player.position += Vec2(50, 0)
    invoke(lambda: setattr(player, 'can_move', True), delay=0.3)
    player.can_move = False
    return amount * 0.5  # Полуурон вместо полного


def activate_power(player):
    print('[Эффект] Активирован Power Boost')
    player.buff_manager.add_percent_stat('attack', 0.3, 10)


def apply_regeneration(player, interval=1, duration=60):
    def regen():
        if player.health < player.current_stats['health']:
            player.health += player.current_stats['hp_regen']
            invoke(regen, delay=interval)

    regen()
    invoke(lambda: player.buff_manager.remove_buff('regeneration'), delay=duration)