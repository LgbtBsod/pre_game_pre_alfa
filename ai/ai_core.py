"""
Улучшенная система AI для игровых сущностей.
Включает модульную архитектуру, оптимизацию производительности и расширенные возможности.
"""

import time
import math
import random
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading

logger = logging.getLogger(__name__)


class AIState(Enum):
    """Состояния AI"""

    IDLE = "idle"
    EXPLORING = "exploring"
    CHASING = "chasing"
    ATTACKING = "attacking"
    RETREATING = "retreating"
    HEALING = "healing"
    SUPPORTING = "supporting"
    FORMATION = "formation"


class AIPriority(Enum):
    """Приоритеты AI"""

    CRITICAL = 0  # Критические действия (лечение, побег)
    HIGH = 1  # Высокий приоритет (атака, защита)
    MEDIUM = 2  # Средний приоритет (исследование, патрулирование)
    LOW = 3  # Низкий приоритет (отдых, социальное взаимодействие)


@dataclass
class AIPersonality:
    """Личность AI"""

    aggression: float = 0.5  # Агрессивность (0.0 - 1.0)
    caution: float = 0.5  # Осторожность (0.0 - 1.0)
    intelligence: float = 0.5  # Интеллект (0.0 - 1.0)
    loyalty: float = 0.7  # Лояльность к группе (0.0 - 1.0)
    curiosity: float = 0.5  # Любопытство (0.0 - 1.0)
    adaptability: float = 0.5  # Адаптивность (0.0 - 1.0)
    leadership: float = 0.3  # Лидерские качества (0.0 - 1.0)
    teamwork: float = 0.6  # Командная работа (0.0 - 1.0)


@dataclass
class AIKnowledge:
    """Знания AI"""

    known_enemies: Dict[str, Dict] = field(default_factory=dict)
    known_abilities: Dict[str, Dict] = field(default_factory=dict)
    tactical_patterns: List[Dict] = field(default_factory=list)
    environmental_hazards: List[Dict] = field(default_factory=list)
    group_dynamics: Dict[str, Dict] = field(default_factory=dict)
    success_rate: Dict[str, float] = field(default_factory=dict)


@dataclass
class AIEmotion:
    """Эмоциональное состояние AI"""

    confidence: float = 0.5  # Уверенность (0.0 - 1.0)
    fear: float = 0.0  # Страх (0.0 - 1.0)
    anger: float = 0.0  # Гнев (0.0 - 1.0)
    excitement: float = 0.0  # Возбуждение (0.0 - 1.0)
    stress: float = 0.0  # Стресс (0.0 - 1.0)
    morale: float = 0.7  # Моральный дух (0.0 - 1.0)


class AICore:
    """Основной класс AI системы"""

    def __init__(self, entity):
        self.entity = entity
        self.state = AIState.IDLE
        self.priority = AIPriority.MEDIUM
        self.personality = self._generate_personality()
        self.knowledge = AIKnowledge()
        self.emotion = AIEmotion()

        # Производительность
        self.last_update_time = time.time()
        self.update_interval = 0.1  # Интервал обновления в секундах
        self.performance_mode = "balanced"  # balanced, performance, quality

        # Память и обучение
        self.memory = []
        from config.unified_settings import UnifiedSettings

        self.learning_rate = UnifiedSettings.LEARNING_RATE_BASE
        self.experience_points = 0

        # Цели и планы
        self.current_goal = None
        self.action_plan = []
        self.target_entity = None

        # Групповое поведение
        self.group_id = None
        self.formation_position = None
        self.team_communication = []

        # Тактические данные
        self.threat_assessment = 0.0
        self.opportunity_assessment = 0.0
        self.risk_tolerance = 0.5

        # Блокировка для потокобезопасности
        self._lock = threading.RLock()

        entity_name = getattr(entity, "name", getattr(entity, "entity_id", "Unknown"))
        logger.info(f"AI Core инициализирован для {entity_name}")

    def _generate_personality(self) -> AIPersonality:
        """Генерирует личность на основе характеристик сущности"""
        # Базовые значения
        personality = AIPersonality()

        # Настройка на основе атрибутов сущности
        if hasattr(self.entity, "attributes"):
            # Агрессия зависит от силы и урона
            strength = self.entity.attributes.get("strength", 10)
            personality.aggression = min(0.9, max(0.1, strength / 20))

            # Интеллект зависит от интеллекта и мудрости
            intelligence_attr = self.entity.attributes.get("intelligence", 10)
            personality.intelligence = min(1.0, max(0.2, intelligence_attr / 20))

            # Осторожность зависит от ловкости и восприятия
            dexterity = self.entity.attributes.get("dexterity", 10)
            personality.caution = min(0.9, max(0.1, 1.0 - dexterity / 20))
        elif hasattr(self.entity, "attribute_manager"):
            # Используем attribute_manager если attributes недоступен
            try:
                strength = self.entity.attribute_manager.get_attribute_value("strength")
                intelligence_attr = self.entity.attribute_manager.get_attribute_value(
                    "intelligence"
                )
                dexterity = self.entity.attribute_manager.get_attribute_value(
                    "dexterity"
                )

                personality.aggression = min(0.9, max(0.1, strength / 20))
                personality.intelligence = min(1.0, max(0.2, intelligence_attr / 20))
                personality.caution = min(0.9, max(0.1, 1.0 - dexterity / 20))
            except Exception as e:
                logger.warning(f"Ошибка получения атрибутов для личности: {e}")

        # Настройка на основе типа сущности
        if hasattr(self.entity, "enemy_type"):
            if self.entity.enemy_type == "berserker":
                personality.aggression = min(0.95, personality.aggression + 0.3)
                personality.caution = max(0.05, personality.caution - 0.2)
            elif self.entity.enemy_type == "scout":
                personality.caution = min(0.9, personality.caution + 0.2)
                personality.curiosity = min(0.9, personality.curiosity + 0.3)
            elif self.entity.enemy_type == "leader":
                personality.leadership = min(0.9, personality.leadership + 0.4)
                personality.teamwork = min(0.9, personality.teamwork + 0.3)

        return personality

    def update(self, delta_time: float):
        """Обновляет AI систему"""
        current_time = time.time()

        # Проверяем необходимость обновления
        if current_time - self.last_update_time < self.update_interval:
            return

        with self._lock:
            try:
                # Определяем режим обновления
                update_mode = self._determine_update_mode()

                if update_mode == "full":
                    self._full_update(delta_time, current_time)
                elif update_mode == "light":
                    self._light_update(delta_time, current_time)
                elif update_mode == "minimal":
                    self._minimal_update(delta_time, current_time)

                self.last_update_time = current_time

            except Exception as e:
                logger.error(f"Ошибка обновления AI: {e}")

    def _determine_update_mode(self) -> str:
        """Определяет режим обновления для оптимизации"""
        # Расстояние до игрока
        distance_to_player = self._get_distance_to_player()

        # Приоритет сущности
        if hasattr(self.entity, "is_boss") and self.entity.is_boss:
            return "full"

        if hasattr(self.entity, "is_elite") and self.entity.is_elite:
            if distance_to_player < 200:
                return "full"
            return "light"

        # Обычные враги
        if distance_to_player < 100:
            return "full"
        elif distance_to_player < 300:
            return "light"
        else:
            return "minimal"

    def _get_distance_to_player(self) -> float:
        """Получает расстояние до игрока"""
        try:
            if hasattr(self.entity, "get_distance_to_player"):
                return self.entity.get_distance_to_player()
            elif hasattr(self.entity, "position") and hasattr(self.entity, "game"):
                player = self.entity.game.player
                if player and hasattr(player, "position"):
                    return math.sqrt(
                        (self.entity.position[0] - player.position[0]) ** 2
                        + (self.entity.position[1] - player.position[1]) ** 2
                    )
        except Exception:
            pass
        return float("inf")

    def _full_update(self, delta_time: float, current_time: float):
        """Полное обновление AI"""
        # Оценка ситуации
        self._assess_situation()

        # Обновление эмоций
        self._update_emotions(delta_time)

        # Планирование действий
        self._plan_actions()

        # Выполнение действий
        self._execute_actions(delta_time)

        # Обучение
        self._learn_from_experience()

        # Групповое взаимодействие
        self._update_group_behavior()

    def _light_update(self, delta_time: float, current_time: float):
        """Облегченное обновление AI"""
        # Базовая оценка угроз
        self._basic_threat_assessment()

        # Простое планирование
        if self.state == AIState.IDLE:
            self._simple_exploration()
        elif self.state == AIState.ATTACKING:
            self._continue_attack()

    def _minimal_update(self, delta_time: float, current_time: float):
        """Минимальное обновление AI"""
        # Только критическая проверка здоровья
        if (
            hasattr(self.entity, "health")
            and self.entity.health < self.entity.max_health * 0.3
        ):
            self._emergency_healing()

    def _assess_situation(self):
        """Оценивает текущую ситуацию"""
        # Оценка угроз
        self.threat_assessment = self._calculate_threat_level()

        # Оценка возможностей
        self.opportunity_assessment = self._calculate_opportunity_level()

        # Обновление приоритета
        if self.threat_assessment > 0.8:
            self.priority = AIPriority.CRITICAL
        elif self.threat_assessment > 0.5:
            self.priority = AIPriority.HIGH
        elif self.opportunity_assessment > 0.7:
            self.priority = AIPriority.HIGH
        else:
            self.priority = AIPriority.MEDIUM

    def _calculate_threat_level(self) -> float:
        """Вычисляет уровень угрозы"""
        threat_level = 0.0

        try:
            # Здоровье
            if hasattr(self.entity, "health") and hasattr(self.entity, "max_health"):
                health_ratio = self.entity.health / self.entity.max_health
                threat_level += (1.0 - health_ratio) * 0.4

            # Ближайшие враги
            nearby_enemies = self._get_nearby_enemies()
            for enemy in nearby_enemies:
                enemy_threat = self._assess_entity_threat(enemy)
                threat_level += enemy_threat

            # Эффекты
            if hasattr(self.entity, "active_effects"):
                for effect in self.entity.active_effects.values():
                    if "debuff" in effect.get("tags", []):
                        threat_level += 0.1

            return min(1.0, threat_level)

        except Exception as e:
            logger.error(f"Ошибка расчета угрозы: {e}")
            return 0.0

    def _calculate_opportunity_level(self) -> float:
        """Вычисляет уровень возможностей"""
        opportunity_level = 0.0

        try:
            # Ближайшие союзники
            nearby_allies = self._get_nearby_allies()
            opportunity_level += len(nearby_allies) * 0.1

            # Доступные способности
            if hasattr(self.entity, "skills"):
                available_skills = [
                    s for s in self.entity.skills.values() if self._can_use_skill(s)
                ]
                opportunity_level += len(available_skills) * 0.05

            # Позиционные преимущества
            if self._has_positional_advantage():
                opportunity_level += 0.2

            return min(1.0, opportunity_level)

        except Exception as e:
            logger.error(f"Ошибка расчета возможностей: {e}")
            return 0.0

    def _get_nearby_enemies(self) -> List:
        """Получает ближайших врагов"""
        try:
            if hasattr(self.entity, "get_nearby_entities"):
                return self.entity.get_nearby_entities(radius=150, enemy_only=True)
            return []
        except Exception:
            return []

    def _get_nearby_allies(self) -> List:
        """Получает ближайших союзников"""
        try:
            if hasattr(self.entity, "get_nearby_entities"):
                return self.entity.get_nearby_entities(radius=150, ally_only=True)
            return []
        except Exception:
            return []

    def _assess_entity_threat(self, entity) -> float:
        """Оценивает угрозу от конкретной сущности"""
        try:
            threat = 0.0

            # Уровень
            if hasattr(entity, "level"):
                threat += entity.level * 0.1

            # Здоровье
            if hasattr(entity, "health") and hasattr(entity, "max_health"):
                health_ratio = entity.health / entity.max_health
                threat += health_ratio * 0.2

            # Расстояние
            distance = self._get_distance_to_entity(entity)
            if distance < 50:
                threat += 0.3
            elif distance < 100:
                threat += 0.1

            return threat

        except Exception:
            return 0.0

    def _get_distance_to_entity(self, entity) -> float:
        """Получает расстояние до сущности"""
        try:
            if hasattr(self.entity, "position") and hasattr(entity, "position"):
                return math.sqrt(
                    (self.entity.position[0] - entity.position[0]) ** 2
                    + (self.entity.position[1] - entity.position[1]) ** 2
                )
        except Exception:
            pass
        return float("inf")

    def _can_use_skill(self, skill) -> bool:
        """Проверяет, можно ли использовать способность"""
        try:
            # Проверка ресурсов
            if (
                hasattr(self.entity, "mana")
                and skill.get("mana_cost", 0) > self.entity.mana
            ):
                return False

            if (
                hasattr(self.entity, "stamina")
                and skill.get("stamina_cost", 0) > self.entity.stamina
            ):
                return False

            # Проверка перезарядки
            if hasattr(self.entity, "skill_cooldowns"):
                skill_id = skill.get("id", "")
                if skill_id in self.entity.skill_cooldowns:
                    cooldown_time = self.entity.skill_cooldowns[skill_id]
                    if time.time() - cooldown_time < skill.get("cooldown", 0):
                        return False

            return True

        except Exception:
            return False

    def _has_positional_advantage(self) -> bool:
        """Проверяет позиционные преимущества"""
        # Простая проверка - есть ли укрытие или высота
        return random.random() < 0.3  # Заглушка

    def _update_emotions(self, delta_time: float):
        """Обновляет эмоциональное состояние"""
        # Уверенность зависит от здоровья и успехов
        if hasattr(self.entity, "health") and hasattr(self.entity, "max_health"):
            health_ratio = self.entity.health / self.entity.max_health
            self.emotion.confidence = min(1.0, max(0.0, health_ratio * 0.8 + 0.2))

        # Страх зависит от угрозы
        self.emotion.fear = min(1.0, self.threat_assessment * 0.8)

        # Гнев зависит от агрессии и полученного урона
        if hasattr(self.entity, "last_damage_taken"):
            damage_factor = min(1.0, self.entity.last_damage_taken / 50)
            self.emotion.anger = min(1.0, self.personality.aggression * damage_factor)

        # Стресс зависит от общего состояния
        self.emotion.stress = (self.emotion.fear + self.emotion.anger) * 0.5

        # Моральный дух
        self.emotion.morale = max(0.0, 1.0 - self.emotion.stress)

    def _plan_actions(self):
        """Планирует действия"""
        self.action_plan.clear()

        # Критические действия
        if self.priority == AIPriority.CRITICAL:
            if self.threat_assessment > 0.8:
                self.action_plan.append(("retreat", 1.0))
            elif (
                hasattr(self.entity, "health")
                and self.entity.health < self.entity.max_health * 0.3
            ):
                self.action_plan.append(("heal", 1.0))

        # Высокий приоритет
        elif self.priority == AIPriority.HIGH:
            if self.threat_assessment > 0.5:
                self.action_plan.append(("attack", 0.8))
                self.action_plan.append(("defend", 0.6))
            elif self.opportunity_assessment > 0.7:
                self.action_plan.append(("support", 0.7))

        # Средний приоритет
        else:
            if self.state == AIState.IDLE:
                self.action_plan.append(("explore", 0.5))
            elif self.state == AIState.EXPLORING:
                self.action_plan.append(("patrol", 0.4))

    def _execute_actions(self, delta_time: float):
        """Выполняет запланированные действия"""
        if not self.action_plan:
            return

        # Выбираем действие с наивысшим приоритетом
        action, priority = max(self.action_plan, key=lambda x: x[1])

        if action == "attack":
            self._execute_attack()
        elif action == "defend":
            self._execute_defend()
        elif action == "heal":
            self._execute_heal()
        elif action == "retreat":
            self._execute_retreat()
        elif action == "explore":
            self._execute_explore()
        elif action == "support":
            self._execute_support()
        elif action == "patrol":
            self._execute_patrol()

    def _execute_attack(self):
        """Выполняет атаку"""
        try:
            if not self.target_entity:
                self.target_entity = self._find_best_target()

            if self.target_entity and hasattr(self.entity, "attack"):
                # Проверяем расстояние
                distance = self._get_distance_to_entity(self.target_entity)
                from config.unified_settings import UnifiedSettings

                attack_range = getattr(
                    self.entity, "attack_range", UnifiedSettings.ATTACK_RANGE_BASE
                )

                if distance <= attack_range:
                    self.entity.attack(self.target_entity)
                    self.state = AIState.ATTACKING
                else:
                    # Двигаемся к цели
                    self._move_towards(self.target_entity.position)
                    self.state = AIState.CHASING

        except Exception as e:
            logger.error(f"Ошибка выполнения атаки: {e}")

    def _execute_defend(self):
        """Выполняет защиту"""
        try:
            # Используем защитные способности
            if hasattr(self.entity, "skills"):
                defensive_skills = [
                    s
                    for s in self.entity.skills.values()
                    if "defense" in s.get("tags", [])
                ]
                if defensive_skills:
                    skill = random.choice(defensive_skills)
                    if hasattr(self.entity, "use_skill"):
                        self.entity.use_skill(skill.get("id", ""))

            # Отступаем к безопасной позиции
            self._find_safe_position()

        except Exception as e:
            logger.error(f"Ошибка выполнения защиты: {e}")

    def _execute_heal(self):
        """Выполняет лечение"""
        try:
            self.state = AIState.HEALING

            # Используем лечебные способности
            if hasattr(self.entity, "skills"):
                healing_skills = [
                    s
                    for s in self.entity.skills.values()
                    if "heal" in s.get("tags", [])
                ]
                if healing_skills:
                    skill = random.choice(healing_skills)
                    if hasattr(self.entity, "use_skill"):
                        self.entity.use_skill(skill.get("id", ""))

            # Используем предметы
            if hasattr(self.entity, "use_healing_item"):
                self.entity.use_healing_item()

        except Exception as e:
            logger.error(f"Ошибка выполнения лечения: {e}")

    def _execute_retreat(self):
        """Выполняет отступление"""
        try:
            self.state = AIState.RETREATING

            # Находим безопасную позицию
            safe_pos = self._find_safe_position()
            if safe_pos:
                self._move_towards(safe_pos)

        except Exception as e:
            logger.error(f"Ошибка выполнения отступления: {e}")

    def _execute_explore(self):
        """Выполняет исследование"""
        try:
            self.state = AIState.EXPLORING

            # Случайное движение
            if random.random() < 0.1:  # 10% шанс изменить направление
                self._random_movement()

        except Exception as e:
            logger.error(f"Ошибка выполнения исследования: {e}")

    def _execute_support(self):
        """Выполняет поддержку союзников"""
        try:
            self.state = AIState.SUPPORTING

            # Находим союзника, которому нужна помощь
            ally = self._find_ally_needing_help()
            if ally:
                self._support_ally(ally)

        except Exception as e:
            logger.error(f"Ошибка выполнения поддержки: {e}")

    def _execute_patrol(self):
        """Выполняет патрулирование"""
        try:
            # Движение по патрульному маршруту
            if not hasattr(self, "_patrol_points"):
                self._patrol_points = self._generate_patrol_route()

            if self._patrol_points:
                current_target = self._patrol_points[0]
                distance = self._get_distance_to_position(current_target)

                if distance < 10:  # Достигли точки
                    self._patrol_points.pop(0)
                    if not self._patrol_points:
                        self._patrol_points = self._generate_patrol_route()
                else:
                    self._move_towards(current_target)

        except Exception as e:
            logger.error(f"Ошибка выполнения патрулирования: {e}")

    def _find_best_target(self):
        """Находит лучшую цель для атаки"""
        try:
            enemies = self._get_nearby_enemies()
            if not enemies:
                return None

            # Оцениваем каждую цель
            best_target = None
            best_score = -1

            for enemy in enemies:
                score = self._calculate_target_score(enemy)
                if score > best_score:
                    best_score = score
                    best_target = enemy

            return best_target

        except Exception as e:
            logger.error(f"Ошибка поиска цели: {e}")
            return None

    def _calculate_target_score(self, target) -> float:
        """Вычисляет оценку цели"""
        try:
            score = 0.0

            # Расстояние (ближе = лучше)
            distance = self._get_distance_to_entity(target)
            score += max(0, 100 - distance) / 100

            # Здоровье (слабее = лучше)
            if hasattr(target, "health") and hasattr(target, "max_health"):
                health_ratio = target.health / target.max_health
                score += (1.0 - health_ratio) * 0.5

            # Уровень угрозы (опаснее = приоритетнее)
            threat = self._assess_entity_threat(target)
            score += threat * 0.3

            return score

        except Exception:
            return 0.0

    def _move_towards(self, target_position):
        """Двигается к цели"""
        try:
            if hasattr(self.entity, "move_towards"):
                speed = getattr(self.entity, "movement_speed", 100)
                self.entity.move_towards(target_position, speed, 0.1)
        except Exception as e:
            logger.error(f"Ошибка движения: {e}")

    def _random_movement(self):
        """Случайное движение"""
        try:
            if hasattr(self.entity, "position"):
                current_pos = self.entity.position
                radius = 50.0
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(0, radius)

                target_x = current_pos[0] + distance * math.cos(angle)
                target_y = current_pos[1] + distance * math.sin(angle)
                target_pos = (target_x, target_y)

                self._move_towards(target_pos)

        except Exception as e:
            logger.error(f"Ошибка случайного движения: {e}")

    def _find_safe_position(self):
        """Находит безопасную позицию"""
        try:
            # Простая логика - отступаем от врагов
            enemies = self._get_nearby_enemies()
            if not enemies:
                return None

            # Вычисляем центр врагов
            center_x = sum(e.position[0] for e in enemies) / len(enemies)
            center_y = sum(e.position[1] for e in enemies) / len(enemies)

            # Отступаем в противоположном направлении
            if hasattr(self.entity, "position"):
                current_pos = self.entity.position
                dx = current_pos[0] - center_x
                dy = current_pos[1] - center_y

                # Нормализуем и умножаем на расстояние отступления
                length = math.sqrt(dx * dx + dy * dy)
                if length > 0:
                    retreat_distance = 100
                    safe_x = current_pos[0] + (dx / length) * retreat_distance
                    safe_y = current_pos[1] + (dy / length) * retreat_distance
                    return (safe_x, safe_y)

            return None

        except Exception as e:
            logger.error(f"Ошибка поиска безопасной позиции: {e}")
            return None

    def _find_ally_needing_help(self):
        """Находит союзника, которому нужна помощь"""
        try:
            allies = self._get_nearby_allies()
            for ally in allies:
                if hasattr(ally, "health") and hasattr(ally, "max_health"):
                    health_ratio = ally.health / ally.max_health
                    if health_ratio < 0.5:  # Нужна помощь
                        return ally
            return None
        except Exception:
            return None

    def _support_ally(self, ally):
        """Поддерживает союзника"""
        try:
            # Лечим союзника
            if hasattr(self.entity, "skills"):
                healing_skills = [
                    s
                    for s in self.entity.skills.values()
                    if "heal" in s.get("tags", [])
                ]
                if healing_skills:
                    skill = random.choice(healing_skills)
                    if hasattr(self.entity, "use_skill_on_target"):
                        self.entity.use_skill_on_target(skill.get("id", ""), ally)

            # Защищаем союзника
            self._move_towards(ally.position)

        except Exception as e:
            logger.error(f"Ошибка поддержки союзника: {e}")

    def _generate_patrol_route(self) -> List[Tuple[float, float]]:
        """Генерирует маршрут патрулирования"""
        try:
            if hasattr(self.entity, "position"):
                base_pos = self.entity.position
                points = []

                for i in range(4):
                    angle = i * math.pi / 2
                    distance = 50
                    x = base_pos[0] + distance * math.cos(angle)
                    y = base_pos[1] + distance * math.sin(angle)
                    points.append((x, y))

                return points
        except Exception:
            pass
        return []

    def _get_distance_to_position(self, position) -> float:
        """Получает расстояние до позиции"""
        try:
            if hasattr(self.entity, "position"):
                return math.sqrt(
                    (self.entity.position[0] - position[0]) ** 2
                    + (self.entity.position[1] - position[1]) ** 2
                )
        except Exception:
            pass
        return float("inf")

    def _learn_from_experience(self):
        """Обучение на основе опыта"""
        try:
            # Анализируем последние действия
            recent_actions = self.memory[-10:] if self.memory else []

            for action in recent_actions:
                if action.get("success", False):
                    # Успешные действия усиливаем
                    self._reinforce_behavior(action.get("type", ""))
                else:
                    # Неудачные действия ослабляем
                    self._weaken_behavior(action.get("type", ""))

            # Адаптируем личность
            self._adapt_personality()

        except Exception as e:
            logger.error(f"Ошибка обучения: {e}")

    def _reinforce_behavior(self, behavior_type: str):
        """Усиливает поведение"""
        if behavior_type == "attack":
            self.personality.aggression = min(0.9, self.personality.aggression + 0.05)
        elif behavior_type == "defend":
            self.personality.caution = min(0.9, self.personality.caution + 0.05)

    def _weaken_behavior(self, behavior_type: str):
        """Ослабляет поведение"""
        if behavior_type == "attack":
            self.personality.aggression = max(0.1, self.personality.aggression - 0.05)
        elif behavior_type == "defend":
            self.personality.caution = max(0.1, self.personality.caution - 0.05)

    def _adapt_personality(self):
        """Адаптирует личность на основе опыта"""
        # Адаптация на основе здоровья
        if hasattr(self.entity, "health") and hasattr(self.entity, "max_health"):
            health_ratio = self.entity.health / self.entity.max_health
            if health_ratio < 0.3:
                self.personality.caution = min(0.9, self.personality.caution + 0.1)
                self.personality.aggression = max(
                    0.1, self.personality.aggression - 0.1
                )

    def _update_group_behavior(self):
        """Обновляет групповое поведение"""
        if not self.group_id:
            return

        try:
            # Координация с группой
            if self.personality.leadership > 0.5:
                self._lead_group()
            elif self.personality.teamwork > 0.5:
                self._follow_group_orders()

        except Exception as e:
            logger.error(f"Ошибка группового поведения: {e}")

    def _lead_group(self):
        """Лидирует в группе"""
        # Отправляем приказы союзникам
        pass

    def _follow_group_orders(self):
        """Следует групповым приказам"""
        # Получаем и выполняем приказы
        pass

    def _basic_threat_assessment(self):
        """Базовая оценка угроз"""
        self.threat_assessment = self._calculate_threat_level()

    def _simple_exploration(self):
        """Простое исследование"""
        if random.random() < 0.05:  # 5% шанс движения
            self._random_movement()

    def _continue_attack(self):
        """Продолжает атаку"""
        if self.target_entity and hasattr(self.entity, "attack"):
            self.entity.attack(self.target_entity)

    def _emergency_healing(self):
        """Экстренное лечение"""
        if hasattr(self.entity, "use_healing_item"):
            self.entity.use_healing_item()

    def record_action(self, action_type: str, success: bool, details: Dict = None):
        """Записывает действие в память"""
        action_record = {
            "type": action_type,
            "success": success,
            "timestamp": time.time(),
            "details": details or {},
        }

        self.memory.append(action_record)

        # Ограничиваем размер памяти
        if len(self.memory) > 100:
            self.memory = self.memory[-50:]

    def get_ai_state_summary(self) -> Dict:
        """Возвращает сводку состояния AI"""
        return {
            "state": self.state.value,
            "priority": self.priority.value,
            "threat_level": self.threat_assessment,
            "opportunity_level": self.opportunity_assessment,
            "confidence": self.emotion.confidence,
            "fear": self.emotion.fear,
            "anger": self.emotion.anger,
            "stress": self.emotion.stress,
            "morale": self.emotion.morale,
            "aggression": self.personality.aggression,
            "caution": self.personality.caution,
            "intelligence": self.personality.intelligence,
        }
