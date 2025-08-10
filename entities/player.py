"""Класс игрока, наследующий от Entity."""

from .entity_refactored import Entity
from ai.learning import PlayerLearning
from ai.decision_maker import PlayerDecisionMaker


class Player(Entity):
    """Класс игрока."""
    
    def __init__(self, entity_id: str, position: tuple = (0, 0)):
        from .entity_refactored import EntityType
        super().__init__(entity_id, EntityType.PLAYER, position)
        
        # Специфичные для игрока свойства
        self.is_player = True
        self.team = "PLAYER"
        self.priority = 0
        self.learning_rate = 1.0  # Максимальная скорость обучения
        
        # Системы игрока
        self.learning_system = PlayerLearning(self)
        self.decision_maker = PlayerDecisionMaker(self)
        
        # Стиль боя (определяется автоматически или настраивается игроком)
        self.combat_style = "balanced"  # balanced, melee, ranged, magic
    
    def update(self, delta_time: float):
        """Обновление игрока"""
        super().update(delta_time)
        
        # Обучение на основе опыта
        if self.learning_system:
            self.learning_system.process_experience()
        
        # Принятие решений
        if self.decision_maker:
            self.decision_maker.make_decisions(delta_time)
        
        # Обновление производных характеристик
        self.update_derived_stats()
    
    def distribute_attribute_points(self):
        """Распределение очков характеристик"""
        # Стратегия распределения очков для игрока
        # Приоритет характеристикам, соответствующим текущему стилю боя
        if self.combat_style == "melee":
            self._invest_in("strength", 4)
            self._invest_in("vitality", 3)
            self._invest_in("endurance", 3)
        elif self.combat_style == "ranged":
            self._invest_in("dexterity", 5)
            self._invest_in("intelligence", 3)
            self._invest_in("endurance", 2)
        else:  # magic или balanced
            self._invest_in("intelligence", 6)
            self._invest_in("faith", 4)
    
    def _invest_in(self, attribute: str, amount: int):
        """Инвестирование очков в характеристику"""
        if self.attribute_points >= amount:
            self.set_attribute_base(attribute, self.get_attribute(attribute) + amount)
            self.attribute_points -= amount
    
    def set_combat_style(self, style: str):
        """Установка стиля боя"""
        valid_styles = ["balanced", "melee", "ranged", "magic"]
        if style in valid_styles:
            self.combat_style = style
            # Автоматически перераспределяем очки при смене стиля
            self.distribute_attribute_points()
    
    def get_combat_style_bonus(self) -> dict:
        """Получение бонусов за стиль боя"""
        bonuses = {
            "balanced": {},
            "melee": {
                "strength": 1.1,
                "vitality": 1.1,
                "physical_damage": 1.2
            },
            "ranged": {
                "dexterity": 1.2,
                "critical_chance": 1.15,
                "attack_speed": 1.1
            },
            "magic": {
                "intelligence": 1.2,
                "faith": 1.1,
                "magical_damage": 1.3
            }
        }
        return bonuses.get(self.combat_style, {})
    
    def to_dict(self) -> dict:
        """Сериализация игрока"""
        data = super().to_dict()
        data.update({
            'is_player': self.is_player,
            'team': self.team,
            'priority': self.priority,
            'learning_rate': self.learning_rate,
            'combat_style': self.combat_style
        })
        return data
    
    def from_dict(self, data: dict) -> None:
        """Десериализация игрока"""
        super().from_dict(data)
        self.is_player = data.get('is_player', True)
        self.team = data.get('team', 'PLAYER')
        self.priority = data.get('priority', 0)
        self.learning_rate = data.get('learning_rate', 1.0)
        self.combat_style = data.get('combat_style', 'balanced')