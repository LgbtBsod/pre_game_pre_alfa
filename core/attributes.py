"""
Система атрибутов сущностей.
Управляет базовыми характеристиками персонажей и их ростом.
"""

from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Attribute:
    """Атрибут сущности с текущим значением, максимумом и скоростью роста"""
    current: float
    maximum: float
    growth_rate: float
    
    def increase(self, amount: float = 1.0) -> bool:
        """Увеличивает атрибут"""
        if self.current < self.maximum:
            self.current = min(self.current + amount, self.maximum)
            return True
        return False
    
    def set_base(self, value: float) -> None:
        """Устанавливает базовое значение"""
        self.current = max(0, min(value, self.maximum))
    
    def set_max(self, value: float) -> None:
        """Устанавливает максимальное значение"""
        self.maximum = max(0, value)
        self.current = min(self.current, self.maximum)
    
    def get_percentage(self) -> float:
        """Возвращает процент заполнения атрибута"""
        return self.current / self.maximum if self.maximum > 0 else 0.0


class AttributeManager:
    """Менеджер атрибутов сущности"""
    
    def __init__(self):
        self.attributes: Dict[str, Attribute] = {}
        self.attribute_points = 0
    
    def initialize_default_attributes(self):
        """Инициализирует стандартные атрибуты"""
        default_attrs = {
            "strength": Attribute(10, 100, 1.0),
            "dexterity": Attribute(10, 100, 1.0),
            "intelligence": Attribute(10, 100, 1.0),
            "vitality": Attribute(10, 100, 1.0),
            "endurance": Attribute(10, 100, 1.0),
            "faith": Attribute(10, 100, 1.0),
            "luck": Attribute(10, 100, 1.0),
        }
        self.attributes.update(default_attrs)
    
    def get_attribute(self, name: str) -> Optional[Attribute]:
        """Получает атрибут по имени"""
        return self.attributes.get(name)
    
    def get_attribute_value(self, name: str) -> float:
        """Получает текущее значение атрибута"""
        attr = self.get_attribute(name)
        return attr.current if attr else 0.0
    
    def get_attribute_max(self, name: str) -> float:
        """Получает максимальное значение атрибута"""
        attr = self.get_attribute(name)
        return attr.maximum if attr else 0.0
    
    def get_attribute_growth(self, name: str) -> float:
        """Получает скорость роста атрибута"""
        attr = self.get_attribute(name)
        return attr.growth_rate if attr else 0.0
    
    def set_attribute_base(self, name: str, value: float) -> None:
        """Устанавливает базовое значение атрибута"""
        if name in self.attributes:
            self.attributes[name].set_base(value)
        else:
            self.attributes[name] = Attribute(value, value, 1.0)
    
    def set_attribute_max(self, name: str, value: float) -> None:
        """Устанавливает максимальное значение атрибута"""
        if name in self.attributes:
            self.attributes[name].set_max(value)
        else:
            self.attributes[name] = Attribute(0, value, 1.0)
    
    def increase_attribute(self, name: str, amount: float = 1.0) -> bool:
        """Увеличивает атрибут"""
        if name in self.attributes:
            return self.attributes[name].increase(amount)
        return False
    
    def has_attribute(self, name: str) -> bool:
        """Проверяет наличие атрибута"""
        return name in self.attributes
    
    def add_attribute_points(self, amount: int) -> None:
        """Добавляет очки атрибутов"""
        self.attribute_points += amount
    
    def spend_attribute_point(self, attribute_name: str) -> bool:
        """Тратит очко атрибута на увеличение характеристики"""
        if self.attribute_points > 0 and self.has_attribute(attribute_name):
            if self.increase_attribute(attribute_name, 1.0):
                self.attribute_points -= 1
                return True
        return False
    
    def get_all_attributes(self) -> Dict[str, Attribute]:
        """Возвращает все атрибуты"""
        return self.attributes.copy()
    
    def get_attribute_summary(self) -> Dict[str, Dict[str, float]]:
        """Возвращает сводку всех атрибутов"""
        summary = {}
        for name, attr in self.attributes.items():
            summary[name] = {
                "current": attr.current,
                "maximum": attr.maximum,
                "growth_rate": attr.growth_rate,
                "percentage": attr.get_percentage()
            }
        return summary
