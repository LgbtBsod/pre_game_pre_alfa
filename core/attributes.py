"""Компонент для управления атрибутами сущности."""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from .component import Component


@dataclass
class Attribute:
    """Атрибут сущности."""
    base_value: float
    max_value: float = 100.0
    growth_rate: float = 1.0
    current_value: float = None
    bonuses: Dict[str, float] = field(default_factory=dict)
    multipliers: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.current_value is None:
            self.current_value = self.base_value
    
    @property
    def total_value(self) -> float:
        """Общее значение атрибута с учетом бонусов и множителей."""
        total = self.current_value
        
        # Применяем аддитивные бонусы
        for bonus in self.bonuses.values():
            total += bonus
        
        # Применяем мультипликативные бонусы
        for multiplier in self.multipliers.values():
            total *= multiplier
        
        return max(0, min(total, self.max_value))
    
    def add_bonus(self, source: str, value: float) -> None:
        """Добавить бонус к атрибуту."""
        self.bonuses[source] = value
    
    def remove_bonus(self, source: str) -> None:
        """Убрать бонус от источника."""
        if source in self.bonuses:
            del self.bonuses[source]
    
    def add_multiplier(self, source: str, value: float) -> None:
        """Добавить множитель к атрибуту."""
        self.multipliers[source] = value
    
    def remove_multiplier(self, source: str) -> None:
        """Убрать множитель от источника."""
        if source in self.multipliers:
            del self.multipliers[source]
    
    def level_up(self) -> None:
        """Повысить уровень атрибута."""
        self.base_value += self.growth_rate
        self.current_value = self.base_value


class AttributesComponent(Component):
    """Компонент для управления атрибутами."""
    
    def __init__(self, entity):
        super().__init__(entity)
        self.attributes: Dict[str, Attribute] = {}
        self.attribute_points: int = 0
        self._setup_default_attributes()
    
    def _setup_default_attributes(self) -> None:
        """Настройка атрибутов по умолчанию."""
        default_attrs = {
            "strength": Attribute(10.0, 100.0, 1.0),
            "dexterity": Attribute(10.0, 100.0, 1.0),
            "intelligence": Attribute(10.0, 100.0, 1.0),
            "vitality": Attribute(10.0, 100.0, 1.0),
            "endurance": Attribute(10.0, 100.0, 1.0),
            "faith": Attribute(10.0, 100.0, 1.0),
            "luck": Attribute(10.0, 100.0, 1.0)
        }
        
        for name, attr in default_attrs.items():
            self.attributes[name] = attr
    
    def get_attribute(self, name: str) -> Optional[Attribute]:
        """Получить атрибут по имени."""
        return self.attributes.get(name)
    
    def get_attribute_value(self, name: str) -> float:
        """Получить значение атрибута."""
        attr = self.get_attribute(name)
        return attr.total_value if attr else 0.0
    
    def has_attribute(self, name: str) -> bool:
        """Проверить, есть ли атрибут."""
        return name in self.attributes
    
    def set_attribute_base(self, name: str, value: float) -> None:
        """Установить базовое значение атрибута."""
        if name in self.attributes:
            self.attributes[name].base_value = value
            self.attributes[name].current_value = value
    
    def add_attribute_bonus(self, name: str, source: str, value: float) -> None:
        """Добавить бонус к атрибуту."""
        if name in self.attributes:
            self.attributes[name].add_bonus(source, value)
    
    def remove_attribute_bonus(self, name: str, source: str) -> None:
        """Убрать бонус от атрибута."""
        if name in self.attributes:
            self.attributes[name].remove_bonus(source)
    
    def add_attribute_multiplier(self, name: str, source: str, value: float) -> None:
        """Добавить множитель к атрибуту."""
        if name in self.attributes:
            self.attributes[name].add_multiplier(source, value)
    
    def remove_attribute_multiplier(self, name: str, source: str) -> None:
        """Убрать множитель от атрибута."""
        if name in self.attributes:
            self.attributes[name].remove_multiplier(source)
    
    def invest_attribute_point(self, name: str) -> bool:
        """Инвестировать очко атрибута."""
        if self.attribute_points > 0 and name in self.attributes:
            self.attributes[name].level_up()
            self.attribute_points -= 1
            return True
        return False
    
    def gain_attribute_points(self, amount: int) -> None:
        """Получить очки атрибутов."""
        self.attribute_points += amount
    
    def _on_initialize(self) -> None:
        """Инициализация компонента."""
        pass
    
    def _on_update(self, delta_time: float) -> None:
        """Обновление компонента."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация в словарь."""
        data = super().to_dict()
        data.update({
            'attributes': {
                name: {
                    'base_value': attr.base_value,
                    'max_value': attr.max_value,
                    'growth_rate': attr.growth_rate,
                    'current_value': attr.current_value,
                    'bonuses': attr.bonuses.copy(),
                    'multipliers': attr.multipliers.copy()
                }
                for name, attr in self.attributes.items()
            },
            'attribute_points': self.attribute_points
        })
        return data
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Десериализация из словаря."""
        super().from_dict(data)
        
        if 'attributes' in data:
            for name, attr_data in data['attributes'].items():
                if name in self.attributes:
                    attr = self.attributes[name]
                    attr.base_value = attr_data.get('base_value', attr.base_value)
                    attr.max_value = attr_data.get('max_value', attr.max_value)
                    attr.growth_rate = attr_data.get('growth_rate', attr.growth_rate)
                    attr.current_value = attr_data.get('current_value', attr.current_value)
                    attr.bonuses = attr_data.get('bonuses', {}).copy()
                    attr.multipliers = attr_data.get('multipliers', {}).copy()
        
        self.attribute_points = data.get('attribute_points', 0)
