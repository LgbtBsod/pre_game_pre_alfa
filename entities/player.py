from .entity import Entity
from ai.learning import PlayerLearning
from ai.decision_maker import PlayerDecisionMaker

class Player(Entity):
    def __init__(self, entity_id: str, position: tuple = (0, 0)):
        super().__init__(entity_id, position)
        self.is_player = True
        self.team = "PLAYER"
        self.priority = 0
        self.learning_rate = 1.0  # Максимальная скорость обучения
        self.learning_system = PlayerLearning(self)
        self.decision_maker = PlayerDecisionMaker(self)
    
    def update(self, delta_time: float):
        # Обучение на основе опыта
        self.learning_system.process_experience()
        
        # Принятие решений
        self.decision_maker.make_decisions(delta_time)
        
        # Обновление характеристик
        self.update_derived_stats()
    
    def distribute_attribute_points(self):
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
        else:  # magic
            self._invest_in("intelligence", 6)
            self._invest_in("faith", 4)
    
    def _invest_in(self, attribute: str, amount: int):
        if self.attribute_points >= amount:
            self.attributes[attribute].value += amount
            self.attribute_points -= amount