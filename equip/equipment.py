# equip/equipment.py
import sqlite3
import json
import effects.effects as effects
import effects.buff_manager as BuffManager
from effects.stat_modifier import StatModifier, ModifierType


class Equipment:
    def __init__(self, player, db_path='assets/items.db'):
        self.player = player
        self.equip = ['Brave Heart', 'Phantom Cloak']
        self.conn = sqlite3.connect(db_path)
        self.load_artifacts()
        self.buff_manager = None
        # Подключаем BuffManager из BasePlayer
        if hasattr(player, 'buff_manager'):
            self.buff_manager = player.buff_manager
        else:
            self.buff_manager = BuffManager(player)

        self.load_artifacts()
        self.buff_manager.load_passive_effects('Brave Heart')
        
    def load_artifacts(self):
        try:
            cursor = self.conn.cursor()
            # Используем параметризованный запрос для безопасности
            placeholders = ','.join(['?'] * len(self.equip))
            query = f"SELECT name, stats, effect, trigger FROM artifacts WHERE name IN ({placeholders})"
            cursor.execute(query, self.equip)
            rows = cursor.fetchall()
            
            for row in rows:
                name, stats_str, effect_str, trigger = row
                try:
                    stats = json.loads(stats_str) if stats_str else {}
                    effect_data = json.loads(effect_str) if effect_str else {}
         

                    if trigger == 'passive':
                        self.apply_passive_stats(stats)
                    elif trigger == 'reactive':
                        self.register_reactive_effect(name, effect_data.get('on_hit'))
                    elif trigger == 'active':
                        self.register_active_effect(name, effect_data.get('on_use'))
                    
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON for artifact {name}: {e}")
        
            self.conn.close() 
        except sqlite3.Error as e:
            print(f"Database error: {e}")
                 

    def apply_passive_stats(self, stats: dict):
        """Применяет пассивные статы к игроку"""
        for stat, value in stats.items():
            if stat not in self.player.base_stats:
                continue

            # Поддержка нескольких модификаторов
            if isinstance(value, str) and ',' in value:
                modifiers = [v.strip() for v in value.split(',')]
                final_value = StatModifier.apply_multiple(self.player.base_stats[stat], modifiers)
            else:
                final_value = StatModifier.apply_multiple(
                    self.player.base_stats[stat],
                    [value]
                )

            self.player.base_stats[stat] = final_value
            
        self.player.current_stats = self.player.base_stats.copy()
        print('[Equip] Все баффы применены')
        
    def register_reactive_effect(self, name, func_name):
        if func_name and hasattr(effects, func_name):
            self.player.reactive_effects[name] = getattr(effects, func_name)

    def register_active_effect(self, name, func_name):
        if func_name and hasattr(effects, func_name):
            self.player.active_effects[name] = lambda: getattr(effects, func_name)(player=self.player)