# equip/equipment.py

from typing import List, Dict, Callable, Optional, Any
from .items_data import ItemsData
from effects.stat_modifier import StatModifier
import effects.effects as effects

class Equipment:
    def __init__(self, player):
        self.player = player
        self.items_data = ItemsData()
        self.equipped_items: List[str] = []
        self.passive_stats: Dict[str, Dict[str, List]] = {}
        self.active_effects: Dict[str, Callable] = {}
        self.reactive_effects: Dict[str, Callable] = {}
        
        self._init_buff_manager()
    
    def _init_buff_manager(self):
        """Инициализация менеджера баффов"""
        if hasattr(self.player, 'buff_manager'):
            self.buff_manager = self.player.buff_manager
        else:
            from effects.buff_manager import BuffManager
            self.buff_manager = BuffManager(self.player)
    
    def equip_item(self, item_name: str) -> bool:
        """Экипирует предмет если есть свободный слот"""
        if not self.items_data.item_exists(item_name):
            return False
            
        if item_name in self.equipped_items:
            return False
            
        if len(self.equipped_items) >= 2:  # Макс 2 предмета
            return False
            
        self.equipped_items.append(item_name)
        self._apply_item_effects(item_name)
        return True
    
    def unequip_item(self, item_name: str) -> bool:
        """Снимает предмет и удаляет его эффекты"""
        if item_name not in self.equipped_items:
            return False
            
        self._remove_item_effects(item_name)
        self.equipped_items.remove(item_name)
        return True
    
    def _apply_item_effects(self, item_name: str):
        """Применяет эффекты предмета"""
        item_data = self.items_data.get_item(item_name)
        if not item_data:
            return
            
        # Пассивные эффекты
        if item_data['trigger'] == 'passive':
            for stat, value in item_data['stats'].items():
                if stat not in self.player.base_stats:
                    continue
                
                modifiers = value if isinstance(value, list) else [value]
                base_value = self.player.base_stats[stat]
                
                self.player.base_stats[stat] = StatModifier.apply_multiple(base_value, modifiers)
                self.passive_stats.setdefault(item_name, {})[stat] = modifiers
            
            self.player.current_stats = self.player.base_stats.copy()
        
        # Активные эффекты
        elif item_data['trigger'] == 'active' and item_data['effect']:
            effect_func = getattr(effects, item_data['effect'], None)
            if effect_func:
                self.active_effects[item_name] = lambda: effect_func(self.player)
    
    def _remove_item_effects(self, item_name: str):
        """Удаляет эффекты предмета"""
        # Удаляем пассивные эффекты
        if item_name in self.passive_stats:
            for stat, modifiers in self.passive_stats[item_name].items():
                base_value = self.player.base_stats[stat]
                self.player.base_stats[stat] = StatModifier.remove_modifiers(base_value, modifiers)
            del self.passive_stats[item_name]
        
        # Удаляем активные эффекты
        self.active_effects.pop(item_name, None)
        
        self.player.current_stats = self.player.base_stats.copy()
    
    def use_item_effect(self, item_name: str) -> bool:
        """Активирует эффект предмета"""
        if item_name not in self.equipped_items:
            return False
            
        if effect := self.active_effects.get(item_name):
            effect()
            return True
        return False
    
    def get_equipped_items(self) -> List[Dict[str, Any]]:
        """Возвращает данные экипированных предметов"""
        return [self.items_data.get_item(name) for name in self.equipped_items]