"""
Примеры использования улучшенной AI системы.
Демонстрирует возможности новой архитектуры AI.
"""

import logging
import time
from typing import List, Dict

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Импорт AI системы
from ai.ai_core import AICore, AIState, AIPriority, AIPersonality
from ai.ai_manager import ai_manager


class ExampleEntity:
    """Пример сущности для демонстрации AI"""
    
    def __init__(self, name: str, entity_type: str, position: tuple):
        self.name = name
        self.entity_type = entity_type
        self.position = list(position)
        self.health = 100
        self.max_health = 100
        self.level = 1
        self.alive = True
        
        # Атрибуты
        self.attributes = {
            'strength': 10,
            'intelligence': 10,
            'dexterity': 10
        }
        
        # Боевые характеристики
        self.combat_stats = {
            'damage': 10,
            'defense': 5,
            'speed': 100
        }
        
        # Способности
        self.skills = {
            'basic_attack': {
                'id': 'basic_attack',
                'damage': 15,
                'cooldown': 1.0,
                'tags': ['attack']
            },
            'heal': {
                'id': 'heal',
                'healing': 20,
                'cooldown': 5.0,
                'tags': ['heal']
            }
        }
        
        # Перезарядки способностей
        self.skill_cooldowns = {}
        
        # Эффекты
        self.active_effects = {}
        
        # Инициализация AI
        self.ai_core = AICore(self)
        
        # Регистрация в AI менеджере
        ai_manager.register_entity(self, self.ai_core)
        
        logger.info(f"Создана сущность {name} типа {entity_type}")
    
    def update(self, delta_time: float):
        """Обновление сущности"""
        # Обновление эффектов
        self._update_effects(delta_time)
        
        # Обновление перезарядок
        self._update_cooldowns(delta_time)
    
    def _update_effects(self, delta_time: float):
        """Обновление активных эффектов"""
        expired_effects = []
        
        for effect_id, effect in self.active_effects.items():
            effect['duration'] -= delta_time
            if effect['duration'] <= 0:
                expired_effects.append(effect_id)
        
        for effect_id in expired_effects:
            del self.active_effects[effect_id]
    
    def _update_cooldowns(self, delta_time: float):
        """Обновление перезарядок способностей"""
        current_time = time.time()
        expired_cooldowns = []
        
        for skill_id, last_used in self.skill_cooldowns.items():
            if skill_id in self.skills:
                cooldown = self.skills[skill_id].get('cooldown', 0)
                if current_time - last_used >= cooldown:
                    expired_cooldowns.append(skill_id)
        
        for skill_id in expired_cooldowns:
            del self.skill_cooldowns[skill_id]
    
    def take_damage(self, damage: float):
        """Получение урона"""
        self.health = max(0, self.health - damage)
        self.last_damage_taken = damage
        
        if self.health <= 0:
            self.alive = False
            logger.info(f"{self.name} погиб")
        
        # Записываем в AI память
        self.ai_core.record_action("take_damage", True, {
            'damage': damage,
            'health_remaining': self.health
        })
    
    def heal(self, amount: float):
        """Лечение"""
        old_health = self.health
        self.health = min(self.max_health, self.health + amount)
        
        # Записываем в AI память
        self.ai_core.record_action("heal", True, {
            'healing': amount,
            'health_gained': self.health - old_health
        })
    
    def use_skill(self, skill_id: str):
        """Использование способности"""
        if skill_id not in self.skills:
            return False
        
        skill = self.skills[skill_id]
        
        # Проверяем перезарядку
        if skill_id in self.skill_cooldowns:
            return False
        
        # Используем способность
        if 'heal' in skill.get('tags', []):
            self.heal(skill.get('healing', 0))
        elif 'attack' in skill.get('tags', []):
            # Простая атака
            pass
        
        # Устанавливаем перезарядку
        self.skill_cooldowns[skill_id] = time.time()
        
        # Записываем в AI память
        self.ai_core.record_action("use_skill", True, {
            'skill_id': skill_id,
            'skill_type': skill.get('tags', [])
        })
        
        return True
    
    def move_towards(self, target_position: tuple, speed: float, delta_time: float):
        """Движение к цели"""
        if not hasattr(self, 'position') or not target_position:
            return
        
        # Простое движение
        dx = target_position[0] - self.position[0]
        dy = target_position[1] - self.position[1]
        
        distance = (dx * dx + dy * dy) ** 0.5
        if distance > 0:
            move_distance = speed * delta_time
            if move_distance > distance:
                move_distance = distance
            
            self.position[0] += (dx / distance) * move_distance
            self.position[1] += (dy / distance) * move_distance
    
    def get_distance_to_player(self) -> float:
        """Получение расстояния до игрока (заглушка)"""
        return 100.0  # Заглушка
    
    def get_nearby_entities(self, radius: float, enemy_only: bool = False) -> List:
        """Получение ближайших сущностей"""
        # Заглушка - возвращаем пустой список
        return []
    
    def has_effect_tag(self, tag: str) -> bool:
        """Проверка наличия эффекта с тегом"""
        for effect in self.active_effects.values():
            if tag in effect.get('tags', []):
                return True
        return False


def example_basic_ai_usage():
    """Пример базового использования AI"""
    logger.info("=== Пример базового использования AI ===")
    
    # Создаем сущности
    warrior = ExampleEntity("Воин", "warrior", (0, 0))
    archer = ExampleEntity("Лучник", "archer", (100, 0))
    mage = ExampleEntity("Маг", "mage", (0, 100))
    
    # Настраиваем личности
    warrior.ai_core.personality.aggression = 0.8
    warrior.ai_core.personality.caution = 0.3
    
    archer.ai_core.personality.caution = 0.7
    archer.ai_core.personality.intelligence = 0.6
    
    mage.ai_core.personality.intelligence = 0.9
    mage.ai_core.personality.caution = 0.6
    
    # Симуляция игрового цикла
    for i in range(10):
        logger.info(f"\n--- Кадр {i + 1} ---")
        
        # Обновляем AI
        ai_manager.update(0.1)
        
        # Показываем состояние AI
        for entity in [warrior, archer, mage]:
            if entity.alive:
                ai_summary = entity.ai_core.get_ai_state_summary()
                logger.info(f"{entity.name}: {ai_summary['state']}, "
                           f"угроза: {ai_summary['threat_level']:.2f}, "
                           f"уверенность: {ai_summary['confidence']:.2f}")
        
        # Симулируем получение урона
        if i == 3:
            warrior.take_damage(30)
            logger.info(f"{warrior.name} получил урон!")
        
        if i == 6:
            archer.take_damage(50)
            logger.info(f"{archer.name} получил сильный урон!")
    
    # Показываем статистику AI
    stats = ai_manager.get_performance_stats()
    logger.info(f"\nСтатистика AI: {stats}")


def example_group_behavior():
    """Пример группового поведения"""
    logger.info("\n=== Пример группового поведения ===")
    
    # Создаем группу врагов
    enemies = []
    for i in range(3):
        enemy = ExampleEntity(f"Враг_{i+1}", "warrior", (i * 50, 0))
        enemy.ai_core.group_id = "enemy_squad"
        enemies.append(enemy)
    
    # Создаем игрока
    player = ExampleEntity("Игрок", "player", (100, 100))
    player.ai_core.personality.intelligence = 0.8
    player.ai_core.personality.adaptability = 0.9
    
    # Симуляция боя
    for i in range(15):
        logger.info(f"\n--- Бой, кадр {i + 1} ---")
        
        # Обновляем AI
        ai_manager.update(0.1)
        
        # Показываем состояние группы
        group_entities = ai_manager.entity_groups.get("enemy_squad", set())
        logger.info(f"Размер группы: {len(group_entities)}")
        
        # Симулируем атаку игрока
        if i == 5:
            for enemy in enemies[:2]:
                enemy.take_damage(20)
                logger.info(f"{enemy.name} атакован!")
        
        # Показываем состояние AI
        for entity in enemies + [player]:
            if entity.alive:
                ai_summary = entity.ai_core.get_ai_state_summary()
                logger.info(f"{entity.name}: {ai_summary['state']}, "
                           f"приоритет: {ai_summary['priority']}")


def example_adaptive_behavior():
    """Пример адаптивного поведения"""
    logger.info("\n=== Пример адаптивного поведения ===")
    
    # Создаем сущность с адаптивным AI
    adaptive_entity = ExampleEntity("Адаптивный", "elite", (0, 0))
    
    # Начальная личность
    initial_personality = adaptive_entity.ai_core.personality
    logger.info(f"Начальная агрессия: {initial_personality.aggression:.2f}")
    logger.info(f"Начальная осторожность: {initial_personality.caution:.2f}")
    
    # Симуляция различных ситуаций
    scenarios = [
        ("Успешные атаки", lambda: adaptive_entity.ai_core.record_action("attack", True, {})),
        ("Неудачные атаки", lambda: adaptive_entity.ai_core.record_action("attack", False, {})),
        ("Получение урона", lambda: adaptive_entity.take_damage(25)),
        ("Лечение", lambda: adaptive_entity.heal(30)),
        ("Успешная защита", lambda: adaptive_entity.ai_core.record_action("defend", True, {}))
    ]
    
    for scenario_name, action in scenarios:
        logger.info(f"\n--- Сценарий: {scenario_name} ---")
        
        # Выполняем действие несколько раз
        for _ in range(3):
            action()
            ai_manager.update(0.1)
        
        # Показываем изменения личности
        current_personality = adaptive_entity.ai_core.personality
        logger.info(f"Агрессия: {current_personality.aggression:.2f} "
                   f"(изменение: {current_personality.aggression - initial_personality.aggression:+.2f})")
        logger.info(f"Осторожность: {current_personality.caution:.2f} "
                   f"(изменение: {current_personality.caution - initial_personality.caution:+.2f})")


def example_performance_optimization():
    """Пример оптимизации производительности"""
    logger.info("\n=== Пример оптимизации производительности ===")
    
    # Создаем много сущностей
    entities = []
    for i in range(50):
        entity_type = ["warrior", "archer", "mage"][i % 3]
        entity = ExampleEntity(f"Entity_{i+1}", entity_type, (i * 10, i * 10))
        entities.append(entity)
    
    # Измеряем производительность
    import time
    
    start_time = time.time()
    for i in range(10):
        ai_manager.update(0.1)
    
    total_time = time.time() - start_time
    avg_time = total_time / 10
    
    # Показываем статистику
    stats = ai_manager.get_performance_stats()
    logger.info(f"Время обновления: {avg_time:.4f}с на кадр")
    logger.info(f"Активных сущностей: {stats['active_entities']}")
    logger.info(f"Всего сущностей: {stats['total_entities']}")
    logger.info(f"Групп: {stats['groups']}")


def main():
    """Главная функция с примерами"""
    logger.info("Демонстрация улучшенной AI системы")
    
    try:
        # Базовое использование
        example_basic_ai_usage()
        
        # Групповое поведение
        example_group_behavior()
        
        # Адаптивное поведение
        example_adaptive_behavior()
        
        # Оптимизация производительности
        example_performance_optimization()
        
        logger.info("\n=== Демонстрация завершена ===")
        
    except Exception as e:
        logger.error(f"Ошибка в демонстрации: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
