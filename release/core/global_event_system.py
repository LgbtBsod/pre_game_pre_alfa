"""
Система глобальных событий.
Управляет случайными событиями, которые влияют на весь игровой мир.
"""

import random
import logging
import time
from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum
from dataclasses import dataclass, field

from .effect_system import EffectDatabase, EffectCode

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Типы глобальных событий"""
    GENETIC_SURGE = "genetic_surge"
    EMOTIONAL_STORM = "emotional_storm"
    AI_AWAKENING = "ai_awakening"
    COSMIC_DISTURBANCE = "cosmic_disturbance"
    RADIATION_STORM = "radiation_storm"
    EVOLUTIONARY_LEAP = "evolutionary_leap"
    DIMENSIONAL_RIFT = "dimensional_rift"
    QUANTUM_FLUX = "quantum_flux"
    BIOLOGICAL_PLAGUE = "biological_plague"
    PSYCHIC_WAVE = "psychic_wave"
    TEMPORAL_ANOMALY = "temporal_anomaly"
    REALITY_SHIFT = "reality_shift"


class EventSeverity(Enum):
    """Уровни серьёзности событий"""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"
    APOCALYPTIC = "apocalyptic"


class EventCategory(Enum):
    """Категории событий"""
    GENETIC = "genetic"
    EMOTIONAL = "emotional"
    AI = "ai"
    COSMIC = "cosmic"
    ENVIRONMENTAL = "environmental"
    TEMPORAL = "temporal"
    PSYCHIC = "psychic"
    REALITY = "reality"


@dataclass
class GlobalEvent:
    """Глобальное событие"""
    event_id: str
    event_type: EventType
    severity: EventSeverity
    category: EventCategory
    name: str
    description: str
    duration: float
    start_time: float
    end_time: float
    effects: List[str] = field(default_factory=list)
    affected_entities: List[str] = field(default_factory=list)
    is_active: bool = True
    intensity: float = 1.0
    radius: float = 100.0
    center_position: Tuple[float, float] = (50.0, 50.0)
    
    def is_expired(self, current_time: float) -> bool:
        """Проверка истечения события"""
        return current_time >= self.end_time
    
    def get_remaining_time(self, current_time: float) -> float:
        """Получение оставшегося времени события"""
        return max(0.0, self.end_time - current_time)
    
    def get_progress(self, current_time: float) -> float:
        """Получение прогресса события (0.0 - 1.0)"""
        total_duration = self.end_time - self.start_time
        if total_duration <= 0:
            return 1.0
        
        elapsed = current_time - self.start_time
        return min(1.0, max(0.0, elapsed / total_duration))


@dataclass
class EventTrigger:
    """Триггер события"""
    event_type: EventType
    condition: Callable[[Dict[str, Any]], bool]
    probability: float
    cooldown: float
    last_triggered: float = 0.0
    min_interval: float = 300.0  # Минимальный интервал между событиями
    max_concurrent: int = 3  # Максимальное количество одновременных событий


class GlobalEventSystem:
    """Система глобальных событий"""
    
    def __init__(self, effect_db: EffectDatabase):
        self.effect_db = effect_db
        self.active_events: List[GlobalEvent] = []
        self.event_history: List[GlobalEvent] = []
        self.event_triggers: Dict[EventType, EventTrigger] = {}
        self.world_state = {}
        
        # Настройки системы
        self.max_concurrent_events = 5
        self.event_check_interval = 30.0  # Проверка каждые 30 секунд
        self.last_event_check = 0.0
        
        # Инициализация триггеров событий
        self._initialize_event_triggers()
        
        logger.info("Система глобальных событий инициализирована")
    
    def _initialize_event_triggers(self):
        """Инициализация триггеров событий"""
        try:
            # Генетические события
            self.event_triggers[EventType.GENETIC_SURGE] = EventTrigger(
                event_type=EventType.GENETIC_SURGE,
                condition=lambda state: state.get("mutation_level", 0) > 5.0,
                probability=0.3,
                cooldown=600.0
            )
            
            self.event_triggers[EventType.EVOLUTIONARY_LEAP] = EventTrigger(
                event_type=EventType.EVOLUTIONARY_LEAP,
                condition=lambda state: state.get("evolution_cycles", 0) >= 3,
                probability=0.2,
                cooldown=1200.0
            )
            
            # Эмоциональные события
            self.event_triggers[EventType.EMOTIONAL_STORM] = EventTrigger(
                event_type=EventType.EMOTIONAL_STORM,
                condition=lambda state: state.get("emotional_instability", 0) > 0.7,
                probability=0.4,
                cooldown=450.0
            )
            
            self.event_triggers[EventType.PSYCHIC_WAVE] = EventTrigger(
                event_type=EventType.PSYCHIC_WAVE,
                condition=lambda state: state.get("psychic_energy", 0) > 0.8,
                probability=0.25,
                cooldown=900.0
            )
            
            # ИИ события
            self.event_triggers[EventType.AI_AWAKENING] = EventTrigger(
                event_type=EventType.AI_AWAKENING,
                condition=lambda state: state.get("ai_learning_rate", 0) > 0.6,
                probability=0.35,
                cooldown=750.0
            )
            
            # Космические события
            self.event_triggers[EventType.COSMIC_DISTURBANCE] = EventTrigger(
                event_type=EventType.COSMIC_DISTURBANCE,
                condition=lambda state: random.random() < 0.05,  # Случайное событие
                probability=0.1,
                cooldown=1800.0
            )
            
            self.event_triggers[EventType.DIMENSIONAL_RIFT] = EventTrigger(
                event_type=EventType.DIMENSIONAL_RIFT,
                condition=lambda state: state.get("reality_stability", 1.0) < 0.5,
                probability=0.15,
                cooldown=1500.0
            )
            
            # Экологические события
            self.event_triggers[EventType.RADIATION_STORM] = EventTrigger(
                event_type=EventType.RADIATION_STORM,
                condition=lambda state: state.get("radiation_level", 0) > 0.6,
                probability=0.3,
                cooldown=600.0
            )
            
            self.event_triggers[EventType.BIOLOGICAL_PLAGUE] = EventTrigger(
                event_type=EventType.BIOLOGICAL_PLAGUE,
                condition=lambda state: state.get("disease_spread", 0) > 0.4,
                probability=0.25,
                cooldown=900.0
            )
            
            # Временные события
            self.event_triggers[EventType.TEMPORAL_ANOMALY] = EventTrigger(
                event_type=EventType.TEMPORAL_ANOMALY,
                condition=lambda state: state.get("time_distortion", 0) > 0.3,
                probability=0.2,
                cooldown=1200.0
            )
            
            # Реальность
            self.event_triggers[EventType.REALITY_SHIFT] = EventTrigger(
                event_type=EventType.REALITY_SHIFT,
                condition=lambda state: state.get("reality_coherence", 1.0) < 0.3,
                probability=0.1,
                cooldown=2400.0
            )
            
            # Квантовые события
            self.event_triggers[EventType.QUANTUM_FLUX] = EventTrigger(
                event_type=EventType.QUANTUM_FLUX,
                condition=lambda state: random.random() < 0.03,  # Редкое случайное событие
                probability=0.05,
                cooldown=3000.0
            )
            
            logger.info(f"Инициализировано {len(self.event_triggers)} триггеров событий")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации триггеров событий: {e}")
    
    def update(self, delta_time: float, world_state: Dict[str, Any], entities: List[Any]):
        """Обновление системы событий"""
        try:
            current_time = time.time()
            self.world_state = world_state
            
            # Проверка событий каждые N секунд
            if current_time - self.last_event_check >= self.event_check_interval:
                self._check_event_triggers(current_time, entities)
                self.last_event_check = current_time
            
            # Обновление активных событий
            self._update_active_events(current_time, entities)
            
            # Очистка истёкших событий
            self._cleanup_expired_events(current_time)
            
        except Exception as e:
            logger.error(f"Ошибка обновления системы событий: {e}")
    
    def _check_event_triggers(self, current_time: float, entities: List[Any]):
        """Проверка триггеров событий"""
        try:
            if len(self.active_events) >= self.max_concurrent_events:
                return
            
            for event_type, trigger in self.event_triggers.items():
                # Проверка кулдауна
                if current_time - trigger.last_triggered < trigger.min_interval:
                    continue
                
                # Проверка максимального количества одновременных событий
                current_type_events = [e for e in self.active_events if e.event_type == event_type]
                if len(current_type_events) >= trigger.max_concurrent:
                    continue
                
                # Проверка условия
                if trigger.condition(self.world_state):
                    # Проверка вероятности
                    if random.random() < trigger.probability:
                        self._trigger_event(event_type, current_time, entities)
                        trigger.last_triggered = current_time
                        
        except Exception as e:
            logger.error(f"Ошибка проверки триггеров событий: {e}")
    
    def _trigger_event(self, event_type: EventType, current_time: float, entities: List[Any]):
        """Триггер события"""
        try:
            event_data = self._create_event_data(event_type, current_time)
            
            if event_data:
                # Создание события
                event = GlobalEvent(
                    event_id=f"EVENT_{event_type.value}_{int(current_time)}",
                    event_type=event_type,
                    severity=event_data["severity"],
                    category=event_data["category"],
                    name=event_data["name"],
                    description=event_data["description"],
                    duration=event_data["duration"],
                    start_time=current_time,
                    end_time=current_time + event_data["duration"],
                    effects=event_data["effects"],
                    intensity=event_data["intensity"],
                    radius=event_data["radius"]
                )
                
                # Добавление в активные события
                self.active_events.append(event)
                
                # Применение эффектов события
                self._apply_event_effects(event, entities)
                
                # Логирование
                logger.info(f"Триггер события: {event.name} (тип: {event_type.value})")
                
        except Exception as e:
            logger.error(f"Ошибка триггера события: {e}")
    
    def _create_event_data(self, event_type: EventType, current_time: float) -> Optional[Dict[str, Any]]:
        """Создание данных события"""
        try:
            base_data = {
                "severity": EventSeverity.MODERATE,
                "category": EventCategory.COSMIC,
                "duration": 60.0,
                "intensity": 1.0,
                "radius": 100.0,
                "effects": []
            }
            
            if event_type == EventType.GENETIC_SURGE:
                return {
                    **base_data,
                    "severity": EventSeverity.MAJOR,
                    "category": EventCategory.GENETIC,
                    "name": "Генетический Взрыв",
                    "description": "Внезапный всплеск генетической активности вызывает ускорение мутаций и эволюции",
                    "duration": 120.0,
                    "intensity": 1.5,
                    "effects": ["mutation_rate_increased", "gene_combinations_enhanced", "evolution_accelerated"]
                }
            
            elif event_type == EventType.EMOTIONAL_STORM:
                return {
                    **base_data,
                    "severity": EventSeverity.MODERATE,
                    "category": EventCategory.EMOTIONAL,
                    "name": "Эмоциональная Буря",
                    "description": "Волна эмоциональной энергии охватывает мир, усиливая чувства всех существ",
                    "duration": 90.0,
                    "intensity": 1.2,
                    "effects": ["emotions_intensified", "emotional_resonance_boosted", "psychic_sensitivity_increased"]
                }
            
            elif event_type == EventType.AI_AWAKENING:
                return {
                    **base_data,
                    "severity": EventSeverity.MAJOR,
                    "category": EventCategory.AI,
                    "name": "Пробуждение ИИ",
                    "description": "Искусственный интеллект достигает нового уровня осознания и адаптации",
                    "duration": 180.0,
                    "intensity": 1.8,
                    "effects": ["ai_learning_accelerated", "ai_adaptation_enhanced", "ai_creativity_boosted"]
                }
            
            elif event_type == EventType.COSMIC_DISTURBANCE:
                return {
                    **base_data,
                    "severity": EventSeverity.CRITICAL,
                    "category": EventCategory.COSMIC,
                    "name": "Космическое Возмущение",
                    "description": "Космические силы нарушают баланс реальности, вызывая хаотические изменения",
                    "duration": 300.0,
                    "intensity": 2.0,
                    "effects": ["reality_distorted", "dimensions_merged", "physics_altered"]
                }
            
            elif event_type == EventType.DIMENSIONAL_RIFT:
                return {
                    **base_data,
                    "severity": EventSeverity.CRITICAL,
                    "category": EventCategory.REALITY,
                    "name": "Разлом Реальности",
                    "description": "Границы между измерениями размываются, позволяя проникать сущностям из других миров",
                    "duration": 240.0,
                    "intensity": 2.5,
                    "effects": ["dimensions_merged", "reality_stability_decreased", "cross_dimensional_entities"]
                }
            
            elif event_type == EventType.RADIATION_STORM:
                return {
                    **base_data,
                    "severity": EventSeverity.MAJOR,
                    "category": EventCategory.ENVIRONMENTAL,
                    "name": "Радиационная Буря",
                    "description": "Повышенный уровень радиации наносит урон всем живым существам",
                    "duration": 150.0,
                    "intensity": 1.3,
                    "effects": ["radiation_damage", "mutation_rate_increased", "health_degeneration"]
                }
            
            elif event_type == EventType.EVOLUTIONARY_LEAP:
                return {
                    **base_data,
                    "severity": EventSeverity.MAJOR,
                    "category": EventCategory.GENETIC,
                    "name": "Эволюционный Скачок",
                    "description": "Внезапный скачок в эволюции всех существ, открывающий новые возможности",
                    "duration": 200.0,
                    "intensity": 1.6,
                    "effects": ["evolution_accelerated", "new_abilities_unlocked", "genetic_potential_increased"]
                }
            
            elif event_type == EventType.BIOLOGICAL_PLAGUE:
                return {
                    **base_data,
                    "severity": EventSeverity.CRITICAL,
                    "category": EventCategory.ENVIRONMENTAL,
                    "name": "Биологическая Чума",
                    "description": "Быстро распространяющаяся болезнь поражает живых существ",
                    "duration": 180.0,
                    "intensity": 1.4,
                    "effects": ["disease_spread", "health_degeneration", "resistance_decreased"]
                }
            
            elif event_type == EventType.PSYCHIC_WAVE:
                return {
                    **base_data,
                    "severity": EventSeverity.MODERATE,
                    "category": EventCategory.PSYCHIC,
                    "name": "Психическая Волна",
                    "description": "Волна психической энергии влияет на сознание всех разумных существ",
                    "duration": 120.0,
                    "intensity": 1.3,
                    "effects": ["psychic_sensitivity_increased", "mental_clarity_boosted", "emotional_control_enhanced"]
                }
            
            elif event_type == EventType.TEMPORAL_ANOMALY:
                return {
                    **base_data,
                    "severity": EventSeverity.MAJOR,
                    "category": EventCategory.TEMPORAL,
                    "name": "Временная Аномалия",
                    "description": "Искажение времени ускоряет или замедляет процессы в мире",
                    "duration": 160.0,
                    "intensity": 1.7,
                    "effects": ["time_acceleration", "aging_processes_altered", "temporal_paradoxes"]
                }
            
            elif event_type == EventType.REALITY_SHIFT:
                return {
                    **base_data,
                    "severity": EventSeverity.APOCALYPTIC,
                    "category": EventCategory.REALITY,
                    "name": "Сдвиг Реальности",
                    "description": "Фундаментальные законы реальности изменяются, создавая хаос",
                    "duration": 400.0,
                    "intensity": 3.0,
                    "effects": ["reality_rewritten", "physics_completely_altered", "existence_threatened"]
                }
            
            elif event_type == EventType.QUANTUM_FLUX:
                return {
                    **base_data,
                    "severity": EventSeverity.CRITICAL,
                    "category": EventCategory.COSMIC,
                    "name": "Квантовый Поток",
                    "description": "Квантовые флуктуации создают непредсказуемые изменения в мире",
                    "duration": 120.0,
                    "intensity": 1.9,
                    "effects": ["quantum_uncertainty", "probability_manipulation", "reality_superposition"]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка создания данных события: {e}")
            return None
    
    def _apply_event_effects(self, event: GlobalEvent, entities: List[Any]):
        """Применение эффектов события к сущностям"""
        try:
            for entity in entities:
                if not hasattr(entity, 'position') or not hasattr(entity, 'is_active'):
                    continue
                
                if not entity.is_active:
                    continue
                
                # Проверка расстояния до центра события
                distance = self._calculate_distance(entity.position, event.center_position)
                if distance <= event.radius:
                    # Применение эффектов в зависимости от типа события
                    self._apply_event_to_entity(event, entity, distance)
                    
        except Exception as e:
            logger.error(f"Ошибка применения эффектов события: {e}")
    
    def _apply_event_to_entity(self, event: GlobalEvent, entity: Any, distance: float):
        """Применение события к конкретной сущности"""
        try:
            # Расчёт интенсивности эффекта (зависит от расстояния)
            distance_factor = 1.0 - (distance / event.radius)
            effect_intensity = event.intensity * distance_factor
            
            if event.event_type == EventType.GENETIC_SURGE:
                if hasattr(entity, 'genetic_system'):
                    entity.genetic_system.mutation_resistance *= (1.0 - 0.2 * effect_intensity)
                    entity.genetic_system.evolution_rate *= (1.0 + 0.3 * effect_intensity)
            
            elif event.event_type == EventType.EMOTIONAL_STORM:
                if hasattr(entity, 'emotion_system'):
                    # Случайная эмоция
                    random_emotion = random.choice([
                        "EMO_101", "EMO_102", "EMO_103", "EMO_104", "EMO_105"
                    ])
                    entity.emotion_system.trigger_emotion(random_emotion, effect_intensity, "global_event")
            
            elif event.event_type == EventType.AI_AWAKENING:
                if hasattr(entity, 'ai_system'):
                    entity.ai_system.q_agent.adaptive_learning_rate *= (1.0 + 0.5 * effect_intensity)
                    entity.ai_system.q_agent.exploration_rate *= (1.0 + 0.3 * effect_intensity)
            
            elif event.event_type == EventType.COSMIC_DISTURBANCE:
                # Случайные эффекты
                random_effects = random.sample([
                    "teleport", "transform", "enhance", "weaken", "clone", "merge"
                ], min(2, int(effect_intensity)))
                
                for effect in random_effects:
                    self._apply_cosmic_effect(entity, effect, effect_intensity)
            
            elif event.event_type == EventType.RADIATION_STORM:
                if hasattr(entity, 'stats'):
                    # Урон от радиации
                    radiation_damage = int(5 * effect_intensity)
                    entity.take_damage(radiation_damage, "radiation")
                    
                    # Увеличение мутаций
                    if hasattr(entity, 'genetic_system'):
                        entity.genetic_system.mutation_rate *= (1.0 + 0.4 * effect_intensity)
            
            # Добавление сущности в список затронутых
            if entity.id not in event.affected_entities:
                event.affected_entities.append(entity.id)
                
        except Exception as e:
            logger.error(f"Ошибка применения события к сущности: {e}")
    
    def _apply_cosmic_effect(self, entity: Any, effect: str, intensity: float):
        """Применение космического эффекта"""
        try:
            if effect == "teleport":
                # Телепортация в случайную позицию
                entity.position.x = random.uniform(0, 100)
                entity.position.y = random.uniform(0, 100)
                
            elif effect == "transform":
                # Временное изменение типа
                if hasattr(entity, 'type'):
                    original_type = entity.type
                    entity.type = random.choice(["enemy", "npc", "creature", "player"])
                    # Восстановление через некоторое время
                    # Здесь можно добавить таймер для восстановления
                    
            elif effect == "enhance":
                # Усиление характеристик
                if hasattr(entity, 'stats'):
                    for stat in entity.stats:
                        if isinstance(entity.stats[stat], (int, float)):
                            entity.stats[stat] = int(entity.stats[stat] * (1.0 + 0.2 * intensity))
                            
            elif effect == "weaken":
                # Ослабление характеристик
                if hasattr(entity, 'stats'):
                    for stat in entity.stats:
                        if isinstance(entity.stats[stat], (int, float)):
                            entity.stats[stat] = int(entity.stats[stat] * (1.0 - 0.15 * intensity))
                            
        except Exception as e:
            logger.error(f"Ошибка применения космического эффекта: {e}")
    
    def _calculate_distance(self, pos1, pos2) -> float:
        """Расчёт расстояния между двумя позициями"""
        try:
            if hasattr(pos1, 'x') and hasattr(pos1, 'y') and hasattr(pos2, 'x') and hasattr(pos2, 'y'):
                dx = pos1.x - pos2[0]
                dy = pos1.y - pos2[1]
                return (dx * dx + dy * dy) ** 0.5
            else:
                return 0.0
        except Exception:
            return 0.0
    
    def _update_active_events(self, current_time: float, entities: List[Any]):
        """Обновление активных событий"""
        try:
            for event in self.active_events:
                if event.is_active:
                    # Проверка истечения события
                    if event.is_expired(current_time):
                        event.is_active = False
                        self._remove_event_effects(event, entities)
                        logger.info(f"Событие {event.name} завершено")
                    else:
                        # Обновление эффектов события
                        self._update_event_effects(event, entities, current_time)
                        
        except Exception as e:
            logger.error(f"Ошибка обновления активных событий: {e}")
    
    def _update_event_effects(self, event: GlobalEvent, entities: List[Any], current_time: float):
        """Обновление эффектов события"""
        try:
            # Периодическое применение эффектов
            if hasattr(event, 'tick_interval') and event.tick_interval > 0:
                if int(current_time) % int(event.tick_interval) == 0:
                    self._apply_event_effects(event, entities)
                    
        except Exception as e:
            logger.error(f"Ошибка обновления эффектов события: {e}")
    
    def _remove_event_effects(self, event: GlobalEvent, entities: List[Any]):
        """Удаление эффектов события"""
        try:
            # Восстановление нормального состояния для затронутых сущностей
            for entity in entities:
                if hasattr(entity, 'id') and entity.id in event.affected_entities:
                    self._restore_entity_state(entity, event)
                    
        except Exception as e:
            logger.error(f"Ошибка удаления эффектов события: {e}")
    
    def _restore_entity_state(self, entity: Any, event: GlobalEvent):
        """Восстановление состояния сущности"""
        try:
            if event.event_type == EventType.GENETIC_SURGE:
                if hasattr(entity, 'genetic_system'):
                    entity.genetic_system.mutation_resistance /= 0.8
                    entity.genetic_system.evolution_rate /= 1.3
                    
            elif event.event_type == EventType.AI_AWAKENING:
                if hasattr(entity, 'ai_system'):
                    entity.ai_system.q_agent.adaptive_learning_rate /= 1.5
                    entity.ai_system.q_agent.exploration_rate /= 1.3
                    
        except Exception as e:
            logger.error(f"Ошибка восстановления состояния сущности: {e}")
    
    def _cleanup_expired_events(self, current_time: float):
        """Очистка истёкших событий"""
        try:
            expired_events = [e for e in self.active_events if e.is_expired(current_time)]
            
            for event in expired_events:
                self.active_events.remove(event)
                self.event_history.append(event)
                
                # Ограничение истории событий
                if len(self.event_history) > 100:
                    self.event_history.pop(0)
                    
        except Exception as e:
            logger.error(f"Ошибка очистки истёкших событий: {e}")
    
    def get_active_events(self) -> List[GlobalEvent]:
        """Получение активных событий"""
        return self.active_events.copy()
    
    def get_event_history(self) -> List[GlobalEvent]:
        """Получение истории событий"""
        return self.event_history.copy()
    
    def get_events_by_type(self, event_type: EventType) -> List[GlobalEvent]:
        """Получение событий по типу"""
        return [e for e in self.active_events if e.event_type == event_type]
    
    def get_events_by_severity(self, severity: EventSeverity) -> List[GlobalEvent]:
        """Получение событий по уровню серьёзности"""
        return [e for e in self.active_events if e.severity == severity]
    
    def get_events_by_category(self, category: EventCategory) -> List[GlobalEvent]:
        """Получение событий по категории"""
        return [e for e in self.active_events if e.category == category]
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Получение статистики системы"""
        try:
            return {
                "total_active_events": len(self.active_events),
                "total_historical_events": len(self.event_history),
                "max_concurrent_events": self.max_concurrent_events,
                "event_check_interval": self.event_check_interval,
                "events_by_type": {et.value: len(self.get_events_by_type(et)) for et in EventType},
                "events_by_severity": {es.value: len(self.get_events_by_severity(es)) for es in EventSeverity},
                "events_by_category": {ec.value: len(self.get_events_by_category(ec)) for ec in EventCategory}
            }
        except Exception as e:
            logger.error(f"Ошибка получения статистики системы: {e}")
            return {"error": str(e)}
    
    def force_event(self, event_type: EventType, severity: EventSeverity = EventSeverity.MODERATE) -> bool:
        """Принудительный запуск события"""
        try:
            if len(self.active_events) >= self.max_concurrent_events:
                logger.warning("Достигнут лимит одновременных событий")
                return False
            
            current_time = time.time()
            entities = []  # Здесь должны быть сущности из мира
            
            self._trigger_event(event_type, current_time, entities)
            logger.info(f"Принудительно запущено событие: {event_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка принудительного запуска события: {e}")
            return False
    
    def clear_all_events(self):
        """Очистка всех активных событий"""
        try:
            for event in self.active_events:
                event.is_active = False
                
            self.active_events.clear()
            logger.info("Все активные события очищены")
            
        except Exception as e:
            logger.error(f"Ошибка очистки событий: {e}")
    
    def save_event_state(self, filepath: str) -> bool:
        """Сохранение состояния системы событий"""
        try:
            import json
            
            save_data = {
                "active_events": [
                    {
                        "event_id": e.event_id,
                        "event_type": e.event_type.value,
                        "severity": e.severity.value,
                        "category": e.category.value,
                        "name": e.name,
                        "description": e.description,
                        "duration": e.duration,
                        "start_time": e.start_time,
                        "end_time": e.end_time,
                        "effects": e.effects,
                        "affected_entities": e.affected_entities,
                        "is_active": e.is_active,
                        "intensity": e.intensity,
                        "radius": e.radius,
                        "center_position": e.center_position
                    }
                    for e in self.active_events
                ],
                "event_history": [
                    {
                        "event_id": e.event_id,
                        "event_type": e.event_type.value,
                        "severity": e.severity.value,
                        "category": e.category.value,
                        "name": e.name,
                        "description": e.description,
                        "duration": e.duration,
                        "start_time": e.start_time,
                        "end_time": e.end_time,
                        "effects": e.effects,
                        "affected_entities": e.affected_entities,
                        "is_active": e.is_active,
                        "intensity": e.intensity,
                        "radius": e.radius,
                        "center_position": e.center_position
                    }
                    for e in self.event_history
                ],
                "world_state": self.world_state,
                "max_concurrent_events": self.max_concurrent_events,
                "event_check_interval": self.event_check_interval
            }
            
            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            logger.info(f"Состояние системы событий сохранено в {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения состояния системы событий: {e}")
            return False
    
    def load_event_state(self, filepath: str) -> bool:
        """Загрузка состояния системы событий"""
        try:
            import json
            
            with open(filepath, 'r') as f:
                save_data = json.load(f)
            
            # Очистка текущих событий
            self.active_events.clear()
            self.event_history.clear()
            
            # Восстановление активных событий
            for event_data in save_data.get("active_events", []):
                event = GlobalEvent(
                    event_id=event_data["event_id"],
                    event_type=EventType(event_data["event_type"]),
                    severity=EventSeverity(event_data["severity"]),
                    category=EventCategory(event_data["category"]),
                    name=event_data["name"],
                    description=event_data["description"],
                    duration=event_data["duration"],
                    start_time=event_data["start_time"],
                    end_time=event_data["end_time"],
                    effects=event_data["effects"],
                    affected_entities=event_data["affected_entities"],
                    is_active=event_data["is_active"],
                    intensity=event_data["intensity"],
                    radius=event_data["radius"],
                    center_position=tuple(event_data["center_position"])
                )
                self.active_events.append(event)
            
            # Восстановление истории событий
            for event_data in save_data.get("event_history", []):
                event = GlobalEvent(
                    event_id=event_data["event_id"],
                    event_type=EventType(event_data["event_type"]),
                    severity=EventSeverity(event_data["severity"]),
                    category=EventCategory(event_data["category"]),
                    name=event_data["name"],
                    description=event_data["description"],
                    duration=event_data["duration"],
                    start_time=event_data["start_time"],
                    end_time=event_data["end_time"],
                    effects=event_data["effects"],
                    affected_entities=event_data["affected_entities"],
                    is_active=event_data["is_active"],
                    intensity=event_data["intensity"],
                    radius=event_data["radius"],
                    center_position=tuple(event_data["center_position"])
                )
                self.event_history.append(event)
            
            # Восстановление настроек
            self.world_state = save_data.get("world_state", {})
            self.max_concurrent_events = save_data.get("max_concurrent_events", 5)
            self.event_check_interval = save_data.get("event_check_interval", 30.0)
            
            logger.info(f"Состояние системы событий загружено из {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка загрузки состояния системы событий: {e}")
            return False
