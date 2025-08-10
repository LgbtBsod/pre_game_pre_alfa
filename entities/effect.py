"""
Система эффектов для сущностей.
"""

import time
from typing import Dict, Any, List


class Effect:
    """Эффект, применяемый к сущности"""

    def __init__(self, effect_id: str, effect_data: dict, target):
        self.effect_id = effect_id
        self.target = target
        self.stacks = 1
        self.max_stacks = effect_data.get("max_stacks", 1)

        # Основные параметры
        self.name = effect_data.get("name", "Unknown Effect")
        self.description = effect_data.get("description", "")
        self.effect_type = effect_data.get("effect_type", "buff")
        self.duration = effect_data.get("duration", 10.0)
        self.tick_rate = effect_data.get("tick_rate", 1.0)
        self.magnitude = effect_data.get("magnitude", 1.0)

        # Время
        self.start_time = time.time()
        self.last_tick_time = self.start_time

        # Модификаторы
        self.modifiers = effect_data.get("modifiers", {})
        self.tags = effect_data.get("tags", [])

        # Применяем эффект
        self.apply()

    def apply(self):
        """Применяет эффект к цели"""
        if not self.target:
            return

        # Применяем модификаторы к характеристикам
        for stat, value in self.modifiers.items():
            if hasattr(self.target, stat):
                current_value = getattr(self.target, stat)
                setattr(self.target, stat, current_value + (value * self.stacks))

    def remove(self):
        """Убирает эффект с цели"""
        if not self.target:
            return

        # Убираем модификаторы
        for stat, value in self.modifiers.items():
            if hasattr(self.target, stat):
                current_value = getattr(self.target, stat)
                setattr(self.target, stat, current_value - (value * self.stacks))

    def update(self, delta_time: float):
        """Обновляет эффект"""
        current_time = time.time()
        elapsed_time = current_time - self.start_time

        # Проверяем, истек ли эффект
        if elapsed_time >= self.duration:
            return

        # Проверяем, нужно ли применить тик
        if current_time - self.last_tick_time >= self.tick_rate:
            self.tick()
            self.last_tick_time = current_time

    def tick(self):
        """Применяет тик эффекта"""
        # Здесь можно добавить логику периодических эффектов
        # Например, урон по времени, восстановление и т.д.
        pass

    def add_stacks(self, amount: int = 1):
        """Добавляет стаки эффекта"""
        old_stacks = self.stacks
        self.stacks = min(self.stacks + amount, self.max_stacks)

        # Пересчитываем эффект с новыми стаками
        if self.stacks != old_stacks:
            self.remove()
            self.apply()

    def remove_stacks(self, amount: int = 1):
        """Убирает стаки эффекта"""
        old_stacks = self.stacks
        self.stacks = max(1, self.stacks - amount)

        # Пересчитываем эффект с новыми стаками
        if self.stacks != old_stacks:
            self.remove()
            self.apply()

    def is_expired(self) -> bool:
        """Проверяет, истек ли эффект"""
        current_time = time.time()
        return current_time - self.start_time >= self.duration

    def has_tag(self, tag: str) -> bool:
        """Проверяет наличие тега"""
        return tag in self.tags

    def get_remaining_time(self) -> float:
        """Возвращает оставшееся время эффекта"""
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        return max(0, self.duration - elapsed_time)

    def get_remaining_ticks(self) -> int:
        """Возвращает количество оставшихся тиков"""
        remaining_time = self.get_remaining_time()
        return int(remaining_time / self.tick_rate) if self.tick_rate > 0 else 0
