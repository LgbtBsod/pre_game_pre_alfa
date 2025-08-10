"""
Система боевых характеристик.
Управляет здоровьем, маной, выносливостью и другими боевыми параметрами.
"""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class CombatStats:
    """Боевые характеристики сущности"""

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

    def heal(self, amount: float) -> float:
        """Восстанавливает здоровье"""
        old_health = self.health
        self.health = min(self.health + amount, self.max_health)
        return self.health - old_health

    def take_damage(self, damage: float) -> float:
        """Получает урон"""
        old_health = self.health
        self.health = max(0, self.health - damage)
        return old_health - self.health

    def restore_mana(self, amount: float) -> float:
        """Восстанавливает ману"""
        old_mana = self.mana
        self.mana = min(self.mana + amount, self.max_mana)
        return self.mana - old_mana

    def spend_mana(self, amount: float) -> bool:
        """Тратит ману"""
        if self.mana >= amount:
            self.mana -= amount
            return True
        return False

    def restore_stamina(self, amount: float) -> float:
        """Восстанавливает выносливость"""
        old_stamina = self.stamina
        self.stamina = min(self.stamina + amount, self.max_stamina)
        return self.stamina - old_stamina

    def spend_stamina(self, amount: float) -> bool:
        """Тратит выносливость"""
        if self.stamina >= amount:
            self.stamina -= amount
            return True
        return False

    def is_alive(self) -> bool:
        """Проверяет, жив ли персонаж"""
        return self.health > 0

    def is_dead(self) -> bool:
        """Проверяет, мертв ли персонаж"""
        return self.health <= 0

    def get_health_percentage(self) -> float:
        """Возвращает процент здоровья"""
        return self.health / self.max_health if self.max_health > 0 else 0.0

    def get_mana_percentage(self) -> float:
        """Возвращает процент маны"""
        return self.mana / self.max_mana if self.max_mana > 0 else 0.0

    def get_stamina_percentage(self) -> float:
        """Возвращает процент выносливости"""
        return self.stamina / self.max_stamina if self.max_stamina > 0 else 0.0

    def calculate_damage_reduction(self, damage_type: str = "physical") -> float:
        """Вычисляет снижение урона"""
        reduction = 0.0

        if damage_type == "physical":
            reduction += self.physical_resist

        reduction += self.all_resist

        return min(reduction, 0.95)  # Максимум 95% снижения

    def calculate_final_damage(
        self, incoming_damage: float, damage_type: str = "physical"
    ) -> float:
        """Вычисляет финальный урон с учетом защиты"""
        damage_reduction = self.calculate_damage_reduction(damage_type)
        return incoming_damage * (1.0 - damage_reduction)


class CombatStatsManager:
    """Менеджер боевых характеристик"""

    def __init__(self):
        self.stats = CombatStats()

    def get_stats(self) -> CombatStats:
        """Получает боевые характеристики"""
        return self.stats

    def update_stats(self, new_stats: Dict[str, float]) -> None:
        """Обновляет боевые характеристики"""
        for key, value in new_stats.items():
            if hasattr(self.stats, key):
                setattr(self.stats, key, value)

    def heal(self, amount: float) -> float:
        """Восстанавливает здоровье"""
        return self.stats.heal(amount)

    def take_damage(self, damage: float) -> float:
        """Получает урон"""
        return self.stats.take_damage(damage)

    def restore_mana(self, amount: float) -> float:
        """Восстанавливает ману"""
        return self.stats.restore_mana(amount)

    def spend_mana(self, amount: float) -> bool:
        """Тратит ману"""
        return self.stats.spend_mana(amount)

    def restore_stamina(self, amount: float) -> float:
        """Восстанавливает выносливость"""
        return self.stats.restore_stamina(amount)

    def spend_stamina(self, amount: float) -> bool:
        """Тратит выносливость"""
        return self.stats.spend_stamina(amount)

    def is_alive(self) -> bool:
        """Проверяет, жив ли персонаж"""
        return self.stats.is_alive()

    def is_dead(self) -> bool:
        """Проверяет, мертв ли персонаж"""
        return self.stats.is_dead()

    def get_health_percentage(self) -> float:
        """Возвращает процент здоровья"""
        return self.stats.get_health_percentage()

    def get_mana_percentage(self) -> float:
        """Возвращает процент маны"""
        return self.stats.get_mana_percentage()

    def get_stamina_percentage(self) -> float:
        """Возвращает процент выносливости"""
        return self.stats.get_stamina_percentage()

    def calculate_damage_reduction(self, damage_type: str = "physical") -> float:
        """Вычисляет снижение урона"""
        return self.stats.calculate_damage_reduction(damage_type)

    def calculate_final_damage(
        self, incoming_damage: float, damage_type: str = "physical"
    ) -> float:
        """Вычисляет финальный урон с учетом защиты"""
        return self.stats.calculate_final_damage(incoming_damage, damage_type)

    def get_stats_dict(self) -> Dict[str, float]:
        """Возвращает характеристики в виде словаря"""
        return {
            "health": self.stats.health,
            "max_health": self.stats.max_health,
            "mana": self.stats.mana,
            "max_mana": self.stats.max_mana,
            "stamina": self.stats.stamina,
            "max_stamina": self.stats.max_stamina,
            "damage_output": self.stats.damage_output,
            "defense": self.stats.defense,
            "movement_speed": self.stats.movement_speed,
            "attack_speed": self.stats.attack_speed,
            "critical_chance": self.stats.critical_chance,
            "critical_multiplier": self.stats.critical_multiplier,
            "all_resist": self.stats.all_resist,
            "physical_resist": self.stats.physical_resist,
        }

    def set_max_health(self, max_health: float) -> None:
        """Устанавливает максимальное здоровье"""
        self.stats.max_health = max_health
        # Убеждаемся, что текущее здоровье не превышает максимум
        if self.stats.health > self.stats.max_health:
            self.stats.health = self.stats.max_health

    def set_health(self, health: float) -> None:
        """Устанавливает текущее здоровье"""
        self.stats.health = max(0, min(health, self.stats.max_health))

    def set_max_mana(self, max_mana: float) -> None:
        """Устанавливает максимальную ману"""
        self.stats.max_mana = max_mana
        # Убеждаемся, что текущая мана не превышает максимум
        if self.stats.mana > self.stats.max_mana:
            self.stats.mana = self.stats.max_mana

    def set_mana(self, mana: float) -> None:
        """Устанавливает текущую ману"""
        self.stats.mana = max(0, min(mana, self.stats.max_mana))

    def set_max_stamina(self, max_stamina: float) -> None:
        """Устанавливает максимальную выносливость"""
        self.stats.max_stamina = max_stamina
        # Убеждаемся, что текущая выносливость не превышает максимум
        if self.stats.stamina > self.stats.max_stamina:
            self.stats.stamina = self.stats.max_stamina

    def set_stamina(self, stamina: float) -> None:
        """Устанавливает текущую выносливость"""
        self.stats.stamina = max(0, min(stamina, self.stats.max_stamina))
