"""Компонент для управления боевыми характеристиками."""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from .component import Component


@dataclass
class CombatStats:
    """Боевые характеристики сущности."""
    health: float = 100.0
    max_health: float = 100.0
    mana: float = 50.0
    max_mana: float = 50.0
    stamina: float = 100.0
    max_stamina: float = 100.0
    damage_output: float = 10.0
    defense: float = 5.0
    movement_speed: float = 100.0
    attack_speed: float = 1.0
    critical_chance: float = 0.05
    critical_multiplier: float = 1.5
    all_resist: float = 0.0
    physical_resist: float = 0.0
    fire_resist: float = 0.0
    ice_resist: float = 0.0
    lightning_resist: float = 0.0
    poison_resist: float = 0.0
    magic_resist: float = 0.0
    holy_resist: float = 0.0
    dark_resist: float = 0.0


class CombatStatsComponent(Component):
    """Компонент для управления боевыми характеристиками."""
    
    def __init__(self, entity):
        super().__init__(entity)
        self.stats = CombatStats()
        self.attack_cooldown = 0.0
        self.last_attacker = None
        self.is_boss = False
    
    def take_damage(self, damage: float, damage_type: str = "physical") -> float:
        """Получить урон с учетом сопротивлений."""
        # Применяем сопротивление к типу урона
        resistance = self._get_resistance(damage_type)
        actual_damage = damage * (1.0 - resistance)
        
        # Применяем общую защиту
        actual_damage = max(0, actual_damage - self.stats.defense)
        
        # Уменьшаем здоровье
        self.stats.health = max(0, self.stats.health - actual_damage)
        
        return actual_damage
    
    def heal(self, amount: float) -> float:
        """Восстановить здоровье."""
        old_health = self.stats.health
        self.stats.health = min(self.stats.max_health, self.stats.health + amount)
        return self.stats.health - old_health
    
    def restore_mana(self, amount: float) -> float:
        """Восстановить ману."""
        old_mana = self.stats.mana
        self.stats.mana = min(self.stats.max_mana, self.stats.mana + amount)
        return self.stats.mana - old_mana
    
    def restore_stamina(self, amount: float) -> float:
        """Восстановить выносливость."""
        old_stamina = self.stats.stamina
        self.stats.stamina = min(self.stats.max_stamina, self.stats.stamina + amount)
        return self.stats.stamina - old_stamina
    
    def consume_mana(self, amount: float) -> bool:
        """Потратить ману."""
        if self.stats.mana >= amount:
            self.stats.mana -= amount
            return True
        return False
    
    def consume_stamina(self, amount: float) -> bool:
        """Потратить выносливость."""
        if self.stats.stamina >= amount:
            self.stats.stamina -= amount
            return True
        return False
    
    def can_attack(self) -> bool:
        """Может ли сущность атаковать."""
        return self.attack_cooldown <= 0.0
    
    def start_attack_cooldown(self) -> None:
        """Начать кулдаун атаки."""
        self.attack_cooldown = 1.0 / self.stats.attack_speed
    
    def update_attack_cooldown(self, delta_time: float) -> None:
        """Обновить кулдаун атаки."""
        if self.attack_cooldown > 0:
            self.attack_cooldown = max(0, self.attack_cooldown - delta_time)
    
    def is_alive(self) -> bool:
        """Жива ли сущность."""
        return self.stats.health > 0
    
    def is_dead(self) -> bool:
        """Мертва ли сущность."""
        return self.stats.health <= 0
    
    def get_health_percentage(self) -> float:
        """Получить процент здоровья."""
        if self.stats.max_health <= 0:
            return 0.0
        return self.stats.health / self.stats.max_health
    
    def get_mana_percentage(self) -> float:
        """Получить процент маны."""
        if self.stats.max_mana <= 0:
            return 0.0
        return self.stats.mana / self.stats.max_mana
    
    def get_stamina_percentage(self) -> float:
        """Получить процент выносливости."""
        if self.stats.max_stamina <= 0:
            return 0.0
        return self.stats.stamina / self.stats.max_stamina
    
    def _get_resistance(self, damage_type: str) -> float:
        """Получить сопротивление к типу урона."""
        resistance_map = {
            "physical": self.stats.physical_resist,
            "fire": self.stats.fire_resist,
            "ice": self.stats.ice_resist,
            "lightning": self.stats.lightning_resist,
            "poison": self.stats.poison_resist,
            "magic": self.stats.magic_resist,
            "holy": self.stats.holy_resist,
            "dark": self.stats.dark_resist
        }
        
        # Возвращаем сопротивление к конкретному типу + общее сопротивление
        specific_resist = resistance_map.get(damage_type, 0.0)
        return min(0.95, specific_resist + self.stats.all_resist)
    
    def _on_initialize(self) -> None:
        """Инициализация компонента."""
        pass
    
    def _on_update(self, delta_time: float) -> None:
        """Обновление компонента."""
        self.update_attack_cooldown(delta_time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация в словарь."""
        data = super().to_dict()
        data.update({
            'stats': {
                'health': self.stats.health,
                'max_health': self.stats.max_health,
                'mana': self.stats.mana,
                'max_mana': self.stats.max_mana,
                'stamina': self.stats.stamina,
                'max_stamina': self.stats.max_stamina,
                'damage_output': self.stats.damage_output,
                'defense': self.stats.defense,
                'movement_speed': self.stats.movement_speed,
                'attack_speed': self.stats.attack_speed,
                'critical_chance': self.stats.critical_chance,
                'critical_multiplier': self.stats.critical_multiplier,
                'all_resist': self.stats.all_resist,
                'physical_resist': self.stats.physical_resist,
                'fire_resist': self.stats.fire_resist,
                'ice_resist': self.stats.ice_resist,
                'lightning_resist': self.stats.lightning_resist,
                'poison_resist': self.stats.poison_resist,
                'magic_resist': self.stats.magic_resist,
                'holy_resist': self.stats.holy_resist,
                'dark_resist': self.stats.dark_resist
            },
            'attack_cooldown': self.attack_cooldown,
            'is_boss': self.is_boss
        })
        return data
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Десериализация из словаря."""
        super().from_dict(data)
        
        if 'stats' in data:
            stats_data = data['stats']
            self.stats.health = stats_data.get('health', 100.0)
            self.stats.max_health = stats_data.get('max_health', 100.0)
            self.stats.mana = stats_data.get('mana', 50.0)
            self.stats.max_mana = stats_data.get('max_mana', 50.0)
            self.stats.stamina = stats_data.get('stamina', 100.0)
            self.stats.max_stamina = stats_data.get('max_stamina', 100.0)
            self.stats.damage_output = stats_data.get('damage_output', 10.0)
            self.stats.defense = stats_data.get('defense', 5.0)
            self.stats.movement_speed = stats_data.get('movement_speed', 100.0)
            self.stats.attack_speed = stats_data.get('attack_speed', 1.0)
            self.stats.critical_chance = stats_data.get('critical_chance', 0.05)
            self.stats.critical_multiplier = stats_data.get('critical_multiplier', 1.5)
            self.stats.all_resist = stats_data.get('all_resist', 0.0)
            self.stats.physical_resist = stats_data.get('physical_resist', 0.0)
            self.stats.fire_resist = stats_data.get('fire_resist', 0.0)
            self.stats.ice_resist = stats_data.get('ice_resist', 0.0)
            self.stats.lightning_resist = stats_data.get('lightning_resist', 0.0)
            self.stats.poison_resist = stats_data.get('poison_resist', 0.0)
            self.stats.magic_resist = stats_data.get('magic_resist', 0.0)
            self.stats.holy_resist = stats_data.get('holy_resist', 0.0)
            self.stats.dark_resist = stats_data.get('dark_resist', 0.0)
        
        self.attack_cooldown = data.get('attack_cooldown', 0.0)
        self.is_boss = data.get('is_boss', False)
