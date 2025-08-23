#!/usr/bin/env python3
"""
Система проклятий и благословений из The Binding of Isaac.
Добавляет элементы риска и награды в игру.
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class CurseType(Enum):
    """Типы проклятий"""
    # Основные проклятия из Isaac
    CURSE_OF_DARKNESS = "curse_of_darkness"      # Ограниченная видимость
    CURSE_OF_LABYRINTH = "curse_of_labyrinth"    # Сложные лабиринты
    CURSE_OF_LOST = "curse_of_lost"              # Скрытая карта
    CURSE_OF_UNKNOWN = "curse_of_unknown"        # Скрытые предметы
    CURSE_OF_CURSED = "curse_of_cursed"          # Случайные негативные эффекты
    CURSE_OF_MAZE = "curse_of_maze"              # Перемешанные двери
    CURSE_OF_BLIND = "curse_of_blind"            # Слепота к предметам
    CURSE_OF_GIANT = "curse_of_giant"            # Гигантские комнаты
    
    # Расширенные проклятия
    CURSE_OF_FRAGILITY = "curse_of_fragility"    # Повышенный урон
    CURSE_OF_EXHAUSTION = "curse_of_exhaustion"  # Быстрая усталость
    CURSE_OF_CONFUSION = "curse_of_confusion"    # Обращённое управление
    CURSE_OF_SILENCE = "curse_of_silence"        # Отключение звуков
    CURSE_OF_SLOWNESS = "curse_of_slowness"      # Замедление движения
    CURSE_OF_WEAKNESS = "curse_of_weakness"      # Снижение урона
    CURSE_OF_AMNESIA = "curse_of_amnesia"        # Потеря памяти поколений


class BlessingType(Enum):
    """Типы благословений"""
    # Основные благословения
    BLESSING_OF_LIGHT = "blessing_of_light"      # Улучшенная видимость
    BLESSING_OF_STRENGTH = "blessing_of_strength" # Увеличенный урон
    BLESSING_OF_SPEED = "blessing_of_speed"       # Увеличенная скорость
    BLESSING_OF_HEALTH = "blessing_of_health"     # Дополнительное здоровье
    BLESSING_OF_LUCK = "blessing_of_luck"         # Улучшенная удача
    BLESSING_OF_WISDOM = "blessing_of_wisdom"     # Дополнительный опыт
    BLESSING_OF_PROTECTION = "blessing_of_protection" # Снижение урона
    BLESSING_OF_REGENERATION = "blessing_of_regeneration" # Восстановление здоровья
    
    # Расширенные благословения
    BLESSING_OF_ABUNDANCE = "blessing_of_abundance"   # Больше предметов
    BLESSING_OF_CLARITY = "blessing_of_clarity"       # Улучшенная память
    BLESSING_OF_HARMONY = "blessing_of_harmony"       # Эмоциональная стабильность
    BLESSING_OF_EVOLUTION = "blessing_of_evolution"   # Ускоренная эволюция
    BLESSING_OF_MASTERY = "blessing_of_mastery"       # Быстрое изучение навыков
    BLESSING_OF_FORTUNE = "blessing_of_fortune"       # Лучшие награды
    BLESSING_OF_RESILIENCE = "blessing_of_resilience" # Сопротивление проклятиям


@dataclass
class CurseBlessingEffect:
    """Эффект проклятия или благословения"""
    effect_id: str
    effect_type: str  # "curse" или "blessing"
    curse_type: Optional[CurseType] = None
    blessing_type: Optional[BlessingType] = None
    intensity: float = 1.0
    duration: float = -1  # -1 для постоянных эффектов
    start_time: float = field(default_factory=time.time)
    source: str = "unknown"
    stacks: int = 1
    
    # Модификаторы характеристик
    stat_modifiers: Dict[str, float] = field(default_factory=dict)
    behavior_modifiers: Dict[str, Any] = field(default_factory=dict)
    
    # Дополнительные эффекты
    special_effects: List[str] = field(default_factory=list)
    
    def is_expired(self) -> bool:
        """Проверка истечения эффекта"""
        if self.duration < 0:
            return False
        return time.time() - self.start_time >= self.duration
    
    def get_remaining_time(self) -> float:
        """Получение оставшегося времени"""
        if self.duration < 0:
            return float('inf')
        return max(0, self.duration - (time.time() - self.start_time))
    
    def get_effective_intensity(self) -> float:
        """Получение эффективной интенсивности с учётом стаков"""
        base_intensity = self.intensity
        
        # Убывающая отдача от стаков
        if self.stacks > 1:
            stack_bonus = (self.stacks - 1) * 0.3  # 30% за каждый дополнительный стак
            return base_intensity * (1.0 + stack_bonus)
        
        return base_intensity


class CurseBlessingSystem:
    """Система проклятий и благословений"""
    
    def __init__(self, memory_system):
        self.memory_system = memory_system
        self.active_effects: Dict[str, CurseBlessingEffect] = {}
        
        # Конфигурация эффектов
        self._initialize_effect_configs()
        
        # Статистика
        self.total_curses_applied = 0
        self.total_blessings_applied = 0
        self.effect_history: List[Dict[str, Any]] = []
        
        logger.info("🎭 Система проклятий и благословений инициализирована")
    
    def _initialize_effect_configs(self):
        """Инициализация конфигураций эффектов"""
        # Конфигурации проклятий
        self.curse_configs = {
            CurseType.CURSE_OF_DARKNESS: {
                "name": "Проклятие тьмы",
                "description": "Ограничивает видимость игрока",
                "stat_modifiers": {"vision_range": -0.5},
                "behavior_modifiers": {"darken_screen": True},
                "base_duration": 300.0  # 5 минут
            },
            CurseType.CURSE_OF_LABYRINTH: {
                "name": "Проклятие лабиринта",
                "description": "Усложняет навигацию",
                "behavior_modifiers": {"complex_layout": True, "hidden_paths": True},
                "base_duration": 600.0  # 10 минут
            },
            CurseType.CURSE_OF_LOST: {
                "name": "Проклятие потери",
                "description": "Скрывает карту",
                "behavior_modifiers": {"hide_minimap": True, "disable_map": True},
                "base_duration": 180.0  # 3 минуты
            },
            CurseType.CURSE_OF_UNKNOWN: {
                "name": "Проклятие неизвестности",
                "description": "Скрывает информацию о предметах",
                "behavior_modifiers": {"hide_item_info": True, "mystery_items": True},
                "base_duration": 240.0  # 4 минуты
            },
            CurseType.CURSE_OF_FRAGILITY: {
                "name": "Проклятие хрупкости",
                "description": "Увеличивает получаемый урон",
                "stat_modifiers": {"damage_taken_multiplier": 1.5},
                "base_duration": 120.0  # 2 минуты
            },
            CurseType.CURSE_OF_EXHAUSTION: {
                "name": "Проклятие истощения",
                "description": "Ускоряет трату выносливости",
                "stat_modifiers": {"stamina_drain_rate": 2.0},
                "base_duration": 180.0  # 3 минуты
            },
            CurseType.CURSE_OF_CONFUSION: {
                "name": "Проклятие смятения",
                "description": "Обращает управление",
                "behavior_modifiers": {"reverse_controls": True},
                "base_duration": 60.0  # 1 минута
            },
            CurseType.CURSE_OF_SLOWNESS: {
                "name": "Проклятие медлительности",
                "description": "Замедляет движение",
                "stat_modifiers": {"movement_speed": -0.3},
                "base_duration": 150.0  # 2.5 минуты
            },
            CurseType.CURSE_OF_WEAKNESS: {
                "name": "Проклятие слабости",
                "description": "Снижает наносимый урон",
                "stat_modifiers": {"damage_multiplier": -0.4},
                "base_duration": 120.0  # 2 минуты
            },
            CurseType.CURSE_OF_AMNESIA: {
                "name": "Проклятие забвения",
                "description": "Снижает эффективность памяти поколений",
                "behavior_modifiers": {"memory_interference": 0.5},
                "base_duration": 300.0  # 5 минут
            }
        }
        
        # Конфигурации благословений
        self.blessing_configs = {
            BlessingType.BLESSING_OF_LIGHT: {
                "name": "Благословение света",
                "description": "Улучшает видимость",
                "stat_modifiers": {"vision_range": 0.5},
                "behavior_modifiers": {"brighten_screen": True},
                "base_duration": 300.0  # 5 минут
            },
            BlessingType.BLESSING_OF_STRENGTH: {
                "name": "Благословение силы",
                "description": "Увеличивает наносимый урон",
                "stat_modifiers": {"damage_multiplier": 0.5},
                "base_duration": 180.0  # 3 минуты
            },
            BlessingType.BLESSING_OF_SPEED: {
                "name": "Благословение скорости",
                "description": "Увеличивает скорость движения",
                "stat_modifiers": {"movement_speed": 0.3},
                "base_duration": 240.0  # 4 минуты
            },
            BlessingType.BLESSING_OF_HEALTH: {
                "name": "Благословение здоровья",
                "description": "Увеличивает максимальное здоровье",
                "stat_modifiers": {"max_health": 0.25},
                "base_duration": 600.0  # 10 минут
            },
            BlessingType.BLESSING_OF_LUCK: {
                "name": "Благословение удачи",
                "description": "Улучшает шансы на удачу",
                "stat_modifiers": {"luck_modifier": 0.2},
                "base_duration": 300.0  # 5 минут
            },
            BlessingType.BLESSING_OF_WISDOM: {
                "name": "Благословение мудрости",
                "description": "Увеличивает получаемый опыт",
                "stat_modifiers": {"experience_multiplier": 1.5},
                "base_duration": 600.0  # 10 минут
            },
            BlessingType.BLESSING_OF_PROTECTION: {
                "name": "Благословение защиты",
                "description": "Снижает получаемый урон",
                "stat_modifiers": {"damage_taken_multiplier": -0.25},
                "base_duration": 300.0  # 5 минут
            },
            BlessingType.BLESSING_OF_REGENERATION: {
                "name": "Благословение восстановления",
                "description": "Восстанавливает здоровье со временем",
                "behavior_modifiers": {"health_regen_rate": 0.5},  # 0.5 HP/сек
                "base_duration": 180.0  # 3 минуты
            },
            BlessingType.BLESSING_OF_ABUNDANCE: {
                "name": "Благословение изобилия",
                "description": "Увеличивает шанс найти предметы",
                "stat_modifiers": {"item_find_chance": 0.3},
                "base_duration": 450.0  # 7.5 минут
            },
            BlessingType.BLESSING_OF_CLARITY: {
                "name": "Благословение ясности",
                "description": "Улучшает память поколений",
                "behavior_modifiers": {"memory_enhancement": 1.5},
                "base_duration": 600.0  # 10 минут
            },
            BlessingType.BLESSING_OF_HARMONY: {
                "name": "Благословение гармонии",
                "description": "Стабилизирует эмоциональное состояние",
                "behavior_modifiers": {"emotional_stability": 0.8},
                "base_duration": 300.0  # 5 минут
            },
            BlessingType.BLESSING_OF_EVOLUTION: {
                "name": "Благословение эволюции",
                "description": "Ускоряет эволюционные процессы",
                "behavior_modifiers": {"evolution_speed": 1.3},
                "base_duration": 420.0  # 7 минут
            },
            BlessingType.BLESSING_OF_MASTERY: {
                "name": "Благословение мастерства",
                "description": "Ускоряет изучение навыков",
                "stat_modifiers": {"skill_learning_speed": 1.4},
                "base_duration": 360.0  # 6 минут
            },
            BlessingType.BLESSING_OF_FORTUNE: {
                "name": "Благословение фортуны",
                "description": "Улучшает качество наград",
                "behavior_modifiers": {"reward_quality": 1.25},
                "base_duration": 480.0  # 8 минут
            },
            BlessingType.BLESSING_OF_RESILIENCE: {
                "name": "Благословение стойкости",
                "description": "Повышает сопротивление проклятиям",
                "behavior_modifiers": {"curse_resistance": 0.4},
                "base_duration": 900.0  # 15 минут
            }
        }
    
    def apply_curse(self, curse_type: CurseType, intensity: float = 1.0, 
                   duration: float = -1, source: str = "system") -> str:
        """Применение проклятия"""
        if curse_type not in self.curse_configs:
            logger.warning(f"Неизвестный тип проклятия: {curse_type}")
            return ""
        
        config = self.curse_configs[curse_type]
        effect_id = str(uuid.uuid4())
        
        # Проверка сопротивления проклятиям
        resistance = self._get_curse_resistance()
        if random.random() < resistance:
            logger.info(f"Проклятие {curse_type.value} было сопротивлено")
            return ""
        
        # Определение длительности
        if duration < 0:
            duration = config["base_duration"] * random.uniform(0.8, 1.2)
        
        # Корректировка интенсивности
        effective_intensity = intensity * (1.0 - resistance * 0.5)
        
        # Создание эффекта
        effect = CurseBlessingEffect(
            effect_id=effect_id,
            effect_type="curse",
            curse_type=curse_type,
            intensity=effective_intensity,
            duration=duration,
            source=source,
            stat_modifiers=config.get("stat_modifiers", {}).copy(),
            behavior_modifiers=config.get("behavior_modifiers", {}).copy()
        )
        
        # Проверка на существующий эффект того же типа
        existing_effect = self._find_existing_effect("curse", curse_type)
        if existing_effect:
            # Стакирование эффекта
            existing_effect.stacks += 1
            existing_effect.duration = max(existing_effect.duration, duration)
            existing_effect.intensity = max(existing_effect.intensity, effective_intensity)
            effect_id = existing_effect.effect_id
            logger.info(f"Проклятие {curse_type.value} стакировано (стаки: {existing_effect.stacks})")
        else:
            # Новый эффект
            self.active_effects[effect_id] = effect
            logger.info(f"Применено проклятие: {config['name']} (интенсивность: {effective_intensity:.2f})")
        
        # Статистика
        self.total_curses_applied += 1
        
        # Запись в историю
        self._record_effect_history("curse_applied", curse_type.value, effective_intensity)
        
        # Запись в память поколений
        self.memory_system.add_memory(
            memory_type=self.memory_system.MemoryType.NEGATIVE_EVENT,
            content={
                "event_type": "curse_applied",
                "curse_type": curse_type.value,
                "intensity": effective_intensity,
                "source": source
            },
            intensity=0.7,
            emotional_impact=0.8
        )
        
        return effect_id
    
    def apply_blessing(self, blessing_type: BlessingType, intensity: float = 1.0,
                      duration: float = -1, source: str = "system") -> str:
        """Применение благословения"""
        if blessing_type not in self.blessing_configs:
            logger.warning(f"Неизвестный тип благословения: {blessing_type}")
            return ""
        
        config = self.blessing_configs[blessing_type]
        effect_id = str(uuid.uuid4())
        
        # Определение длительности
        if duration < 0:
            duration = config["base_duration"] * random.uniform(0.8, 1.2)
        
        # Создание эффекта
        effect = CurseBlessingEffect(
            effect_id=effect_id,
            effect_type="blessing",
            blessing_type=blessing_type,
            intensity=intensity,
            duration=duration,
            source=source,
            stat_modifiers=config.get("stat_modifiers", {}).copy(),
            behavior_modifiers=config.get("behavior_modifiers", {}).copy()
        )
        
        # Проверка на существующий эффект того же типа
        existing_effect = self._find_existing_effect("blessing", blessing_type)
        if existing_effect:
            # Стакирование эффекта
            existing_effect.stacks += 1
            existing_effect.duration = max(existing_effect.duration, duration)
            existing_effect.intensity = max(existing_effect.intensity, intensity)
            effect_id = existing_effect.effect_id
            logger.info(f"Благословение {blessing_type.value} стакировано (стаки: {existing_effect.stacks})")
        else:
            # Новый эффект
            self.active_effects[effect_id] = effect
            logger.info(f"Применено благословение: {config['name']} (интенсивность: {intensity:.2f})")
        
        # Статистика
        self.total_blessings_applied += 1
        
        # Запись в историю
        self._record_effect_history("blessing_applied", blessing_type.value, intensity)
        
        # Запись в память поколений
        self.memory_system.add_memory(
            memory_type=self.memory_system.MemoryType.POSITIVE_EVENT,
            content={
                "event_type": "blessing_applied",
                "blessing_type": blessing_type.value,
                "intensity": intensity,
                "source": source
            },
            intensity=0.6,
            emotional_impact=0.7
        )
        
        return effect_id
    
    def remove_effect(self, effect_id: str) -> bool:
        """Удаление эффекта"""
        if effect_id in self.active_effects:
            effect = self.active_effects[effect_id]
            del self.active_effects[effect_id]
            
            effect_name = "неизвестный эффект"
            if effect.curse_type:
                effect_name = self.curse_configs[effect.curse_type]["name"]
            elif effect.blessing_type:
                effect_name = self.blessing_configs[effect.blessing_type]["name"]
            
            logger.info(f"Удалён эффект: {effect_name}")
            return True
        
        return False
    
    def cleanup_expired_effects(self) -> List[str]:
        """Очистка истёкших эффектов"""
        expired_effects = []
        
        for effect_id, effect in list(self.active_effects.items()):
            if effect.is_expired():
                expired_effects.append(effect_id)
                self.remove_effect(effect_id)
        
        if expired_effects:
            logger.info(f"Очищено истёкших эффектов: {len(expired_effects)}")
        
        return expired_effects
    
    def get_active_stat_modifiers(self) -> Dict[str, float]:
        """Получение активных модификаторов характеристик"""
        combined_modifiers = {}
        
        for effect in self.active_effects.values():
            effective_intensity = effect.get_effective_intensity()
            
            for stat, modifier in effect.stat_modifiers.items():
                if stat not in combined_modifiers:
                    combined_modifiers[stat] = 0.0
                
                # Применение модификатора с учётом интенсивности
                combined_modifiers[stat] += modifier * effective_intensity
        
        return combined_modifiers
    
    def get_active_behavior_modifiers(self) -> Dict[str, Any]:
        """Получение активных модификаторов поведения"""
        combined_modifiers = {}
        
        for effect in self.active_effects.values():
            effective_intensity = effect.get_effective_intensity()
            
            for behavior, modifier in effect.behavior_modifiers.items():
                if behavior not in combined_modifiers:
                    if isinstance(modifier, bool):
                        combined_modifiers[behavior] = modifier
                    elif isinstance(modifier, (int, float)):
                        combined_modifiers[behavior] = modifier * effective_intensity
                    else:
                        combined_modifiers[behavior] = modifier
                else:
                    # Комбинирование модификаторов
                    if isinstance(modifier, bool):
                        combined_modifiers[behavior] = combined_modifiers[behavior] or modifier
                    elif isinstance(modifier, (int, float)):
                        combined_modifiers[behavior] += modifier * effective_intensity
        
        return combined_modifiers
    
    def get_active_effects_summary(self) -> Dict[str, Any]:
        """Получение сводки активных эффектов"""
        curses = []
        blessings = []
        
        for effect in self.active_effects.values():
            effect_info = {
                "id": effect.effect_id,
                "intensity": effect.get_effective_intensity(),
                "remaining_time": effect.get_remaining_time(),
                "stacks": effect.stacks,
                "source": effect.source
            }
            
            if effect.effect_type == "curse" and effect.curse_type:
                config = self.curse_configs[effect.curse_type]
                effect_info.update({
                    "name": config["name"],
                    "description": config["description"],
                    "type": effect.curse_type.value
                })
                curses.append(effect_info)
            
            elif effect.effect_type == "blessing" and effect.blessing_type:
                config = self.blessing_configs[effect.blessing_type]
                effect_info.update({
                    "name": config["name"],
                    "description": config["description"],
                    "type": effect.blessing_type.value
                })
                blessings.append(effect_info)
        
        return {
            "curses": curses,
            "blessings": blessings,
            "total_effects": len(self.active_effects),
            "curse_count": len(curses),
            "blessing_count": len(blessings)
        }
    
    def apply_random_curse(self, intensity_range: Tuple[float, float] = (0.5, 1.5),
                          source: str = "random") -> str:
        """Применение случайного проклятия"""
        curse_type = random.choice(list(CurseType))
        intensity = random.uniform(*intensity_range)
        return self.apply_curse(curse_type, intensity, source=source)
    
    def apply_random_blessing(self, intensity_range: Tuple[float, float] = (0.5, 1.5),
                             source: str = "random") -> str:
        """Применение случайного благословения"""
        blessing_type = random.choice(list(BlessingType))
        intensity = random.uniform(*intensity_range)
        return self.apply_blessing(blessing_type, intensity, source=source)
    
    def get_curse_blessing_balance(self) -> float:
        """Получение баланса проклятий и благословений"""
        curse_weight = 0.0
        blessing_weight = 0.0
        
        for effect in self.active_effects.values():
            weight = effect.get_effective_intensity()
            
            if effect.effect_type == "curse":
                curse_weight += weight
            elif effect.effect_type == "blessing":
                blessing_weight += weight
        
        # Баланс от -1 (только проклятия) до +1 (только благословения)
        total_weight = curse_weight + blessing_weight
        if total_weight == 0:
            return 0.0
        
        return (blessing_weight - curse_weight) / total_weight
    
    def suggest_counter_effects(self) -> List[Dict[str, Any]]:
        """Предложение контр-эффектов"""
        suggestions = []
        
        # Анализ активных проклятий
        active_curses = [e for e in self.active_effects.values() if e.effect_type == "curse"]
        
        for curse_effect in active_curses:
            if curse_effect.curse_type == CurseType.CURSE_OF_DARKNESS:
                suggestions.append({
                    "counter_type": "blessing",
                    "blessing_type": BlessingType.BLESSING_OF_LIGHT,
                    "reason": "Противодействует проклятию тьмы",
                    "effectiveness": 0.8
                })
            
            elif curse_effect.curse_type == CurseType.CURSE_OF_FRAGILITY:
                suggestions.append({
                    "counter_type": "blessing",
                    "blessing_type": BlessingType.BLESSING_OF_PROTECTION,
                    "reason": "Противодействует повышенному урону",
                    "effectiveness": 0.7
                })
            
            elif curse_effect.curse_type == CurseType.CURSE_OF_SLOWNESS:
                suggestions.append({
                    "counter_type": "blessing",
                    "blessing_type": BlessingType.BLESSING_OF_SPEED,
                    "reason": "Противодействует замедлению",
                    "effectiveness": 0.9
                })
            
            elif curse_effect.curse_type == CurseType.CURSE_OF_WEAKNESS:
                suggestions.append({
                    "counter_type": "blessing",
                    "blessing_type": BlessingType.BLESSING_OF_STRENGTH,
                    "reason": "Противодействует снижению урона",
                    "effectiveness": 0.8
                })
            
            elif curse_effect.curse_type == CurseType.CURSE_OF_AMNESIA:
                suggestions.append({
                    "counter_type": "blessing",
                    "blessing_type": BlessingType.BLESSING_OF_CLARITY,
                    "reason": "Противодействует потере памяти",
                    "effectiveness": 0.6
                })
        
        return suggestions
    
    def _get_curse_resistance(self) -> float:
        """Получение сопротивления проклятиям"""
        resistance = 0.0
        
        # Сопротивление от благословений
        for effect in self.active_effects.values():
            if (effect.effect_type == "blessing" and 
                effect.blessing_type == BlessingType.BLESSING_OF_RESILIENCE):
                resistance += effect.behavior_modifiers.get("curse_resistance", 0.0)
        
        # Сопротивление от памяти поколений
        memory_resistance = self.memory_system.get_resistance_to_negative_events()
        resistance += memory_resistance * 0.2
        
        return min(resistance, 0.8)  # Максимум 80% сопротивления
    
    def _find_existing_effect(self, effect_type: str, specific_type) -> Optional[CurseBlessingEffect]:
        """Поиск существующего эффекта определённого типа"""
        for effect in self.active_effects.values():
            if effect.effect_type == effect_type:
                if (effect_type == "curse" and effect.curse_type == specific_type) or \
                   (effect_type == "blessing" and effect.blessing_type == specific_type):
                    return effect
        return None
    
    def _record_effect_history(self, event_type: str, effect_type: str, intensity: float):
        """Запись в историю эффектов"""
        self.effect_history.append({
            "timestamp": time.time(),
            "event_type": event_type,
            "effect_type": effect_type,
            "intensity": intensity
        })
        
        # Ограничение размера истории
        if len(self.effect_history) > 1000:
            self.effect_history = self.effect_history[-500:]
    
    def get_effect_statistics(self) -> Dict[str, Any]:
        """Получение статистики эффектов"""
        return {
            "total_curses_applied": self.total_curses_applied,
            "total_blessings_applied": self.total_blessings_applied,
            "active_effects_count": len(self.active_effects),
            "curse_blessing_balance": self.get_curse_blessing_balance(),
            "curse_resistance": self._get_curse_resistance(),
            "history_size": len(self.effect_history)
        }