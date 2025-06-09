# equip/equipment.py

import sqlite3
import json
import effects.effects as effects


class Equipment:
    def __init__(self, player, db_path='assets/items.db'):
        self.player = player
        self.equip = ['Brave Heart', 'Phantom Cloak']
        self.conn = sqlite3.connect(db_path)
        self.load_artifacts()
        self.buff_manager = BuffManager(player)
        
        self.buff_manager.load_passive_effects('Brave Heart')
        
    def load_artifacts(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, stats, effect, trigger FROM artifacts WHERE name IN ({})".format(','.join('?'*len(self.equip))), self.equip)
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            name, stats_str, effect_str, trigger = row
            try:
                stats = json.loads(stats_str) if stats_str else {}
                effect_data = json.loads(effect_str) if effect_str else {}
            except json.JSONDecodeError:
                continue

            if trigger == 'passive':
                self.apply_passive_stats(stats)
            elif trigger == 'reactive':
                self.register_reactive_effect(name, effect_data.get('on_hit'))
            elif trigger == 'active':
                self.register_active_effect(name, effect_data.get('on_use'))

    def apply_passive_stats(self, stats):
        for stat, value in stats.items():
            if '%' in str(value):
                percent = convert_to_num(value)
                self.player.current_stats[stat] *= (1 + percent)
            elif str(value).startswith('+'):
                flat = float(str(value)[1:])
                self.player.current_stats[stat] += flat
            elif str(value).startswith('*'):
                mult = float(str(value)[1:])
                self.player.current_stats[stat] *= mult
            else:
                try:
                    flat = float(value)
                    self.player.current_stats[stat] += flat
                except:
                    pass

    def register_reactive_effect(self, name, func_name):
        if hasattr(effects, func_name):
            self.player.reactive_effects[name] = getattr(effects, func_name)


    def register_active_effect(self, name, func_name):
        if hasattr(effects, func_name):
            self.player.active_effects[name] = lambda: getattr(effects, func_name)(player=self.player)