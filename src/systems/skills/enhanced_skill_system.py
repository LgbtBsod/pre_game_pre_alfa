#!/usr/bin/env python3
"""
Enhanced Skill System - Улучшенная система навыков
Отвечает за управление навыками с поддержкой спецэффектов и AI-приоритетов
"""

import logging
import random
import time
from typing import Dict, List, Optional, Union, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum

from ..effects.effect_system import Effect, EffectCategory, TargetType, DamageType

logger = logging.getLogger(__name__)

class SkillType(Enum):
    """Типы навыков"""
    ATTACK = "attack"             # Атакующий навык
    HEAL = "heal"                 # Лечебный навык
    BUFF = "buff"                 # Усиливающий навык
    DEBUFF = "debuff"             # Ослабляющий навык
    UTILITY = "utility"           # Утилитарный навык
    MOVEMENT = "movement"         # Навык движения
    SUMMON = "summon"             # Навык призыва

class TargetSelection(Enum):
    """Типы выбора целей"""
    SELF = "self"                 # На себя
    SINGLE_ENEMY = "single_enemy" # Один враг
    ALL_ENEMIES = "all_enemies"   # Все враги
    SINGLE_ALLY = "single_ally"   # Один союзник
    ALL_ALLIES = "all_allies"     # Все союзники
    AREA = "area"                 # По области
    GROUND = "ground"             # По земле

class SkillCategory(Enum):
    """Категории навыков"""
    MELEE = "melee"               # Ближний бой
    RANGED = "ranged"             # Дальний бой
    MAGIC = "magic"               # Магия
    PHYSICAL = "physical"         # Физический
    ELEMENTAL = "elemental"       # Стихийный
    SUPPORT = "support"           # Поддержка
    CONTROL = "control"           # Контроль

@dataclass
class SkillRequirements:
    """Требования для использования навыка"""
    level: int = 0
    strength: int = 0
    agility: int = 0
    intelligence: int = 0
    vitality: int = 0
    mana_cost: int = 0
    health_cost: int = 0
    stamina_cost: int = 0
    required_items: List[str] = field(default_factory=list)
    required_effects: List[str] = field(default_factory=list)

@dataclass
class SkillCooldown:
    """Система кулдаунов навыка"""
    base_cooldown: float = 0.0
    gcd_group: Optional[str] = None  # Группа глобального кулдауна
    gcd: float = 0.0                 # Глобальный кулдаун
    charges: int = 1                  # Количество зарядов
    max_charges: int = 1              # Максимальное количество зарядов
    charge_regen_time: float = 0.0    # Время восстановления заряда

@dataclass
class SkillRange:
    """Параметры дальности навыка"""
    min_range: float = 0.0
    max_range: float = 1.0
    area_shape: str = "single"        # single, cone, circle, line, rectangle
    area_size: float = 0.0            # Размер области действия
    area_angle: float = 0.0           # Угол для конусных атак
    projectile_speed: float = 0.0     # Скорость проектиля
    homing: bool = False              # Самонаведение

@dataclass
class SkillScaling:
    """Масштабирование навыка от статов"""
    strength: float = 0.0
    agility: float = 0.0
    intelligence: float = 0.0
    vitality: float = 0.0
    weapon_damage: float = 0.0        # Масштабирование от урона оружия
    armor: float = 0.0                # Масштабирование от брони
    max_health: float = 0.0           # Масштабирование от максимального здоровья
    max_mana: float = 0.0             # Масштабирование от максимальной маны

@dataclass
class AIPriority:
    """Приоритеты для AI при выборе навыков"""
    base_priority: float = 0.5        # Базовый приоритет (0.0 - 1.0)
    health_threshold: float = 0.3     # Порог здоровья для использования
    mana_threshold: float = 0.2       # Порог маны для использования
    target_priority: float = 0.5      # Приоритет выбора цели
    combo_priority: float = 0.3       # Приоритет в комбо
    tags: List[str] = field(default_factory=list)  # Теги для AI

class Skill:
    """Базовый класс навыка"""
    
    def __init__(
        self,
        name: str,
        description: str,
        skill_type: SkillType,
        effects: List[Effect],
        cooldown: float = 0.0,
        gcd_group: Optional[str] = None,
        gcd: float = 0.0,
        range_params: Optional[SkillRange] = None,
        requirements: Optional[SkillRequirements] = None,
        scaling: Optional[SkillScaling] = None,
        ai_priority: Optional[AIPriority] = None,
        **kwargs
    ):
        self.name = name
        self.description = description
        self.skill_type = skill_type
        self.effects = effects or []
        
        # Кулдауны
        self.cooldown_info = SkillCooldown(
            base_cooldown=cooldown,
            gcd_group=gcd_group,
            gcd=gcd
        )
        
        # Дальность и область действия
        self.range_params = range_params or SkillRange()
        
        # Требования
        self.requirements = requirements or SkillRequirements()
        
        # Масштабирование
        self.scaling = scaling or SkillScaling()
        
        # AI приоритеты
        self.ai_priority = ai_priority or AIPriority()
        
        # Состояние навыка
        self.last_use_time = 0.0
        self.current_charges = self.cooldown_info.max_charges
        self.last_charge_regen = time.time()
        
        # Дополнительные параметры
        self.icon: Optional[str] = None
        self.animation: Optional[str] = None
        self.sound: Optional[str] = None
        self.particle_effect: Optional[str] = None
        
        logger.debug(f"Создан навык: {name} ({skill_type.value})")
    
    def can_use(self, user: Any, targets: List[Any] = None) -> Tuple[bool, str]:
        """Проверяет, можно ли использовать навык"""
        current_time = time.time()
        
        # Проверка кулдауна
        if self.cooldown_info.base_cooldown > 0:
            time_since_use = current_time - self.last_use_time
            if time_since_use < self.cooldown_info.base_cooldown:
                remaining = self.cooldown_info.base_cooldown - time_since_use
                return False, f"Навык на кулдауне ({remaining:.1f}с)"
        
        # Проверка зарядов
        if self.current_charges <= 0:
            return False, "Нет зарядов"
        
        # Проверка требований
        if not self._check_requirements(user):
            return False, "Не выполнены требования"
        
        # Проверка ресурсов
        if not self._check_resources(user):
            return False, "Недостаточно ресурсов"
        
        # Проверка целей
        if targets and not self._check_targets(targets):
            return False, "Неверные цели"
        
        return True, "OK"
    
    def _check_requirements(self, user: Any) -> bool:
        """Проверяет требования для использования навыка"""
        if not hasattr(user, 'level') or user.level < self.requirements.level:
            return False
        
        if hasattr(user, 'stats'):
            if user.stats.get('strength', 0) < self.requirements.strength:
                return False
            if user.stats.get('agility', 0) < self.requirements.agility:
                return False
            if user.stats.get('intelligence', 0) < self.requirements.intelligence:
                return False
            if user.stats.get('vitality', 0) < self.requirements.vitality:
                return False
        
        return True
    
    def _check_resources(self, user: Any) -> bool:
        """Проверяет наличие ресурсов"""
        if hasattr(user, 'mana') and user.mana < self.requirements.mana_cost:
            return False
        
        if hasattr(user, 'health') and user.health < self.requirements.health_cost:
            return False
        
        if hasattr(user, 'stamina') and user.stamina < self.requirements.stamina_cost:
            return False
        
        return True
    
    def _check_targets(self, targets: List[Any]) -> bool:
        """Проверяет корректность целей"""
        if not targets:
            return False
        
        # Проверяем количество целей
        if self.range_params.area_shape == "single" and len(targets) > 1:
            return False
        
        # Проверяем дальность до целей
        if hasattr(self, '_check_range'):
            for target in targets:
                if not self._check_range(target):
                    return False
        
        return True
    
    def use(self, user: Any, targets: List[Any] = None, position: Tuple[float, float] = None) -> Dict[str, Any]:
        """Использует навык"""
        # Проверяем возможность использования
        can_use, message = self.can_use(user, targets)
        if not can_use:
            return {"success": False, "message": message}
        
        try:
            # Расходуем ресурсы
            self._consume_resources(user)
            
            # Применяем эффекты
            result = self._apply_effects(user, targets, position)
            
            # Обновляем состояние навыка
            self._update_skill_state()
            
            # Логируем использование
            logger.debug(f"Использован навык: {self.name} пользователем {getattr(user, 'name', 'Unknown')}")
            
            return {"success": True, "message": f"Использован {self.name}", "result": result}
            
        except Exception as e:
            logger.error(f"Ошибка использования навыка {self.name}: {e}")
            return {"success": False, "message": f"Ошибка: {e}"}
    
    def _consume_resources(self, user: Any):
        """Расходует ресурсы на использование навыка"""
        if hasattr(user, 'mana'):
            user.mana -= self.requirements.mana_cost
        
        if hasattr(user, 'health'):
            user.health -= self.requirements.health_cost
        
        if hasattr(user, 'stamina'):
            user.stamina -= self.requirements.stamina_cost
    
    def _apply_effects(self, user: Any, targets: List[Any] = None, position: Tuple[float, float] = None) -> Dict[str, Any]:
        """Применяет эффекты навыка"""
        results = []
        
        if targets:
            for target in targets:
                for effect in self.effects:
                    if effect.category == EffectCategory.INSTANT:
                        effect.apply_instant(user, target)
                    else:
                        if hasattr(target, 'add_effect'):
                            target.add_effect(effect, user)
                    
                    results.append({
                        "target": target,
                        "effect": effect.name,
                        "success": True
                    })
        
        elif position and self.range_params.area_shape != "single":
            # Применяем эффекты по области
            area_targets = self._get_targets_in_area(position)
            for target in area_targets:
                for effect in self.effects:
                    if effect.category == EffectCategory.INSTANT:
                        effect.apply_instant(user, target)
                    else:
                        if hasattr(target, 'add_effect'):
                            target.add_effect(effect, user)
                    
                    results.append({
                        "target": target,
                        "effect": effect.name,
                        "success": True
                    })
        
        return {"effects_applied": results}
    
    def _get_targets_in_area(self, position: Tuple[float, float]) -> List[Any]:
        """Получает цели в области действия"""
        # В реальной реализации здесь должна быть логика поиска целей в области
        return []
    
    def _update_skill_state(self):
        """Обновляет состояние навыка после использования"""
        current_time = time.time()
        
        # Обновляем время последнего использования
        self.last_use_time = current_time
        
        # Уменьшаем количество зарядов
        if self.cooldown_info.max_charges > 1:
            self.current_charges -= 1
        
        # Запускаем восстановление зарядов
        if self.current_charges < self.cooldown_info.max_charges:
            self.last_charge_regen = current_time
    
    def update(self, delta_time: float):
        """Обновляет состояние навыка (восстановление зарядов)"""
        if self.cooldown_info.max_charges <= 1:
            return
        
        current_time = time.time()
        
        # Восстанавливаем заряды
        if (self.current_charges < self.cooldown_info.max_charges and 
            self.cooldown_info.charge_regen_time > 0):
            
            time_since_regen = current_time - self.last_charge_regen
            if time_since_regen >= self.cooldown_info.charge_regen_time:
                self.current_charges = min(
                    self.current_charges + 1,
                    self.cooldown_info.max_charges
                )
                self.last_charge_regen = current_time
    
    def get_cooldown_remaining(self) -> float:
        """Возвращает оставшееся время кулдауна"""
        if self.cooldown_info.base_cooldown <= 0:
            return 0.0
        
        current_time = time.time()
        time_since_use = current_time - self.last_use_time
        remaining = self.cooldown_info.base_cooldown - time_since_use
        
        return max(0.0, remaining)
    
    def get_ai_priority(self, user: Any, targets: List[Any] = None) -> float:
        """Рассчитывает приоритет для AI"""
        priority = self.ai_priority.base_priority
        
        # Модификаторы на основе здоровья
        if hasattr(user, 'health') and hasattr(user, 'max_health'):
            health_ratio = user.health / user.max_health
            if health_ratio <= self.ai_priority.health_threshold:
                if self.skill_type in [SkillType.HEAL, SkillType.BUFF]:
                    priority += 0.3
                elif self.skill_type == SkillType.MOVEMENT:
                    priority += 0.2
        
        # Модификаторы на основе маны
        if hasattr(user, 'mana') and hasattr(user, 'max_mana'):
            mana_ratio = user.mana / user.max_mana
            if mana_ratio <= self.ai_priority.mana_threshold:
                if self.skill_type == SkillType.MAGIC:
                    priority -= 0.2
        
        # Модификаторы на основе целей
        if targets and self.ai_priority.target_priority > 0:
            priority += self.ai_priority.target_priority * 0.1
        
        return min(1.0, max(0.0, priority))

class WeaponAttackSkill(Skill):
    """Навык атаки оружия с поддержкой спецэффектов"""
    
    def __init__(self, weapon: Any, **kwargs):
        super().__init__(**kwargs)
        self.weapon = weapon
    
    def use(self, user: Any, targets: List[Any] = None, position: Tuple[float, float] = None) -> Dict[str, Any]:
        """Использует навык атаки с обработкой спецэффектов"""
        # Сначала применяем базовые эффекты
        result = super().use(user, targets, position)
        
        # Если базовое применение успешно, обрабатываем спецэффекты оружия
        if result["success"] and targets and hasattr(self.weapon, 'apply_special_effects'):
            for target in targets:
                self.weapon.apply_special_effects(user, target, "on_hit")
        
        return result

class ComboSkill(Skill):
    """Навык, который является частью комбо"""
    
    def __init__(self, combo_chain: List[str], combo_position: int, **kwargs):
        super().__init__(**kwargs)
        self.combo_chain = combo_chain
        self.combo_position = combo_position
        self.combo_multiplier = 1.0 + (combo_position * 0.2)  # Увеличение урона с каждым ударом
    
    def _apply_effects(self, user: Any, targets: List[Any] = None, position: Tuple[float, float] = None) -> Dict[str, Any]:
        """Применяет эффекты с учетом комбо-множителя"""
        # Временно увеличиваем силу эффектов
        original_effects = self.effects.copy()
        
        for effect in self.effects:
            if hasattr(effect, 'value') and isinstance(effect.value, (int, float)):
                effect.value *= self.combo_multiplier
        
        # Применяем эффекты
        result = super()._apply_effects(user, targets, position)
        
        # Восстанавливаем оригинальные значения
        self.effects = original_effects
        
        return result

class SkillFactory:
    """Фабрика для создания навыков"""
    
    @staticmethod
    def create_basic_attack() -> Skill:
        """Создает базовую атаку"""
        from ..effects.effect_system import Effect, EffectCategory, TargetType, DamageType
        
        attack_effect = Effect(
            name="Базовая атака",
            category=EffectCategory.INSTANT,
            value=10,
            damage_types=[DamageType.PHYSICAL],
            scaling={"strength": 0.5, "agility": 0.3},
            target_type=TargetType.ENEMY
        )
        
        return Skill(
            name="Базовая атака",
            description="Простая атака оружием",
            skill_type=SkillType.ATTACK,
            effects=[attack_effect],
            cooldown=1.0,
            gcd_group="melee",
            gcd=1.0,
            range_params=SkillRange(max_range=1.0),
            requirements=SkillRequirements(),
            scaling=SkillScaling(strength=0.5, agility=0.3),
            ai_priority=AIPriority(base_priority=0.7, tags=["attack", "melee"])
        )
    
    @staticmethod
    def create_fireball() -> Skill:
        """Создает огненный шар"""
        from ..effects.effect_system import Effect, EffectCategory, TargetType, DamageType
        
        fireball_effect = Effect(
            name="Огненный шар",
            category=EffectCategory.INSTANT,
            value=25,
            damage_types=[DamageType.FIRE],
            scaling={"intelligence": 0.8},
            target_type=TargetType.ENEMY,
            area={"shape": "circle", "radius": 1.5}
        )
        
        return Skill(
            name="Огненный шар",
            description="Магический снаряд из огня",
            skill_type=SkillType.ATTACK,
            effects=[fireball_effect],
            cooldown=3.0,
            gcd_group="spell",
            gcd=1.5,
            range_params=SkillRange(max_range=8.0, area_shape="circle", area_size=1.5),
            requirements=SkillRequirements(level=5, intelligence=15, mana_cost=20),
            scaling=SkillScaling(intelligence=0.8),
            ai_priority=AIPriority(base_priority=0.6, tags=["attack", "magic", "fire"])
        )
    
    @staticmethod
    def create_heal() -> Skill:
        """Создает навык лечения"""
        from ..effects.effect_system import Effect, EffectCategory, TargetType
        
        heal_effect = Effect(
            name="Лечение",
            category=EffectCategory.INSTANT,
            value=30,
            target_type=TargetType.ALLY
        )
        
        return Skill(
            name="Лечение",
            description="Восстанавливает здоровье союзника",
            skill_type=SkillType.HEAL,
            effects=[heal_effect],
            cooldown=5.0,
            gcd_group="spell",
            gcd=1.5,
            range_params=SkillRange(max_range=5.0),
            requirements=SkillRequirements(level=3, intelligence=10, mana_cost=25),
            scaling=SkillScaling(intelligence=0.6),
            ai_priority=AIPriority(base_priority=0.8, health_threshold=0.5, tags=["heal", "support"])
        )

class EnhancedSkillSystem:
    """Улучшенная система управления навыками"""
    
    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self.skill_cooldowns: Dict[str, float] = {}
        self.combo_chains: Dict[str, List[str]] = {}
        self.active_combos: Dict[str, Dict[str, Any]] = {}
        
        logger.info("Улучшенная система навыков инициализирована")
    
    def initialize(self) -> bool:
        """Инициализация системы навыков"""
        try:
            self._setup_skill_templates()
            self._setup_combo_chains()
            
            logger.info("Улучшенная система навыков успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации улучшенной системы навыков: {e}")
            return False
    
    def _setup_skill_templates(self):
        """Настройка шаблонов навыков"""
        # Создаем базовые навыки
        self.skills["basic_attack"] = SkillFactory.create_basic_attack()
        self.skills["fireball"] = SkillFactory.create_fireball()
        self.skills["heal"] = SkillFactory.create_heal()
        
        logger.debug(f"Создано {len(self.skills)} шаблонов навыков")
    
    def _setup_combo_chains(self):
        """Настройка цепочек комбо"""
        self.combo_chains = {
            "sword_combo": ["basic_attack", "slash", "finisher"],
            "magic_combo": ["fireball", "lightning", "explosion"],
            "support_combo": ["heal", "buff", "shield"]
        }
        
        logger.debug(f"Создано {len(self.combo_chains)} цепочек комбо")
    
    def register_skill(self, skill: Skill):
        """Регистрирует навык в системе"""
        self.skills[skill.name] = skill
        logger.debug(f"Зарегистрирован навык: {skill.name}")
    
    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """Получает навык по имени"""
        return self.skills.get(skill_name)
    
    def use_skill(self, skill_name: str, user: Any, targets: List[Any] = None, position: Tuple[float, float] = None) -> Dict[str, Any]:
        """Использует навык"""
        skill = self.get_skill(skill_name)
        if not skill:
            return {"success": False, "message": f"Навык {skill_name} не найден"}
        
        # Проверяем глобальный кулдаун
        if skill.cooldown_info.gcd_group and not self._check_gcd(skill.cooldown_info.gcd_group, skill.cooldown_info.gcd):
            return {"success": False, "message": "Глобальный кулдаун активен"}
        
        # Используем навык
        result = skill.use(user, targets, position)
        
        if result["success"]:
            # Устанавливаем глобальный кулдаун
            if skill.cooldown_info.gcd_group:
                self._set_gcd(skill.cooldown_info.gcd_group, skill.cooldown_info.gcd)
            
            # Обрабатываем комбо
            self._process_combo(skill_name, user)
        
        return result
    
    def _check_gcd(self, gcd_group: str, gcd_duration: float) -> bool:
        """Проверяет глобальный кулдаун"""
        current_time = time.time()
        last_gcd = self.skill_cooldowns.get(gcd_group, 0)
        
        return (current_time - last_gcd) >= gcd_duration
    
    def _set_gcd(self, gcd_group: str, gcd_duration: float):
        """Устанавливает глобальный кулдаун"""
        self.skill_cooldowns[gcd_group] = time.time()
    
    def _process_combo(self, skill_name: str, user: Any):
        """Обрабатывает комбо-цепочки"""
        user_id = getattr(user, 'id', str(id(user)))
        
        for combo_name, combo_skills in self.combo_chains.items():
            if skill_name in combo_skills:
                if user_id not in self.active_combos:
                    self.active_combos[user_id] = {}
                
                if combo_name not in self.active_combos[user_id]:
                    self.active_combos[user_id][combo_name] = {
                        "current_step": 0,
                        "last_skill_time": time.time(),
                        "combo_timeout": 3.0  # 3 секунды на комбо
                    }
                
                combo_data = self.active_combos[user_id][combo_name]
                expected_skill = combo_skills[combo_data["current_step"]]
                
                if skill_name == expected_skill:
                    # Комбо продолжается
                    combo_data["current_step"] += 1
                    combo_data["last_skill_time"] = time.time()
                    
                    if combo_data["current_step"] >= len(combo_skills):
                        # Комбо завершено
                        logger.debug(f"Комбо {combo_name} завершено пользователем {user_id}")
                        del self.active_combos[user_id][combo_name]
                else:
                    # Комбо прервано
                    del self.active_combos[user_id][combo_name]
    
    def get_available_skills(self, user: Any, targets: List[Any] = None) -> List[Skill]:
        """Возвращает список доступных навыков"""
        available_skills = []
        
        for skill in self.skills.values():
            can_use, _ = skill.can_use(user, targets)
            if can_use:
                available_skills.append(skill)
        
        return available_skills
    
    def get_best_skill_for_ai(self, user: Any, targets: List[Any] = None) -> Optional[Skill]:
        """Возвращает лучший навык для AI"""
        available_skills = self.get_available_skills(user, targets)
        
        if not available_skills:
            return None
        
        # Сортируем по приоритету AI
        available_skills.sort(key=lambda s: s.get_ai_priority(user, targets), reverse=True)
        
        return available_skills[0]
    
    def update(self, delta_time: float):
        """Обновляет систему навыков"""
        # Обновляем навыки
        for skill in self.skills.values():
            skill.update(delta_time)
        
        # Очищаем устаревшие комбо
        current_time = time.time()
        for user_id in list(self.active_combos.keys()):
            for combo_name in list(self.active_combos[user_id].keys()):
                combo_data = self.active_combos[user_id][combo_name]
                if (current_time - combo_data["last_skill_time"]) > combo_data["combo_timeout"]:
                    del self.active_combos[user_id][combo_name]
            
            # Удаляем пустые записи пользователей
            if not self.active_combos[user_id]:
                del self.active_combos[user_id]
    
    def cleanup(self):
        """Очистка системы навыков"""
        logger.info("Очистка улучшенной системы навыков...")
        self.skills.clear()
        self.skill_cooldowns.clear()
        self.combo_chains.clear()
        self.active_combos.clear()
