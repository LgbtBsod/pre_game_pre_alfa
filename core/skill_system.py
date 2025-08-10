import random
import time
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from enum import Enum
from core.leveling_system import AttributeType


class SkillType(Enum):
    """Типы умений"""
    ACTIVE = "active"          # Активные умения
    PASSIVE = "passive"        # Пассивные умения
    ULTIMATE = "ultimate"      # Ультимативные умения
    BUFF = "buff"              # Усиливающие умения
    DEBUFF = "debuff"          # Ослабляющие умения


class DamageType(Enum):
    """Типы урона для умений"""
    PHYSICAL = "physical"
    MAGIC = "magic"
    FIRE = "fire"
    ICE = "ice"
    LIGHTNING = "lightning"
    POISON = "poison"
    HOLY = "holy"
    DARK = "dark"


@dataclass
class SkillEffect:
    """Эффект умения"""
    effect_type: str
    value: float
    duration: float
    target: str = "self"  # self, enemy, area
    radius: float = 0.0


@dataclass
class SkillRequirement:
    """Требования для изучения умения"""
    level: int
    attributes: Dict[AttributeType, int]
    skills: List[str]  # Предыдущие умения
    currency: int = 0


class Skill:
    """Базовый класс умения"""
    
    def __init__(self, skill_id: str, name: str, skill_type: SkillType):
        self.skill_id = skill_id
        self.name = name
        self.skill_type = skill_type
        
        # Базовые параметры
        self.level = 1
        self.max_level = 10
        self.cooldown = 0.0
        self.current_cooldown = 0.0
        self.mana_cost = 0
        self.stamina_cost = 0
        
        # Эффекты
        self.effects: List[SkillEffect] = []
        self.damage = 0.0
        self.damage_type = DamageType.PHYSICAL
        self.range = 0.0
        self.area_radius = 0.0
        
        # Требования
        self.requirements = SkillRequirement(1, {}, [])
        
        # Описание
        self.description = ""
        self.icon = None
        
        # Состояние
        self.learned = False
        self.active = False
        
        # Модификаторы
        self.damage_modifier = 1.0
        self.cooldown_modifier = 1.0
        self.cost_modifier = 1.0
    
    def can_use(self, entity) -> bool:
        """Проверить, можно ли использовать умение"""
        if not self.learned:
            return False
        
        if self.current_cooldown > 0:
            return False
        
        if hasattr(entity, 'mana') and entity.mana < self.mana_cost:
            return False
        
        if hasattr(entity, 'stamina') and entity.stamina < self.stamina_cost:
            return False
        
        return True
    
    def use(self, caster, target=None) -> bool:
        """Использовать умение"""
        if not self.can_use(caster):
            return False
        
        # Расход ресурсов
        if hasattr(caster, 'mana'):
            caster.mana = max(0, caster.mana - self.mana_cost)
        
        if hasattr(caster, 'stamina'):
            caster.stamina = max(0, caster.stamina - self.stamina_cost)
        
        # Устанавливаем кулдаун
        self.current_cooldown = self.cooldown * self.cooldown_modifier
        
        # Применяем эффекты
        self._apply_effects(caster, target)
        
        # Опыт за использование
        self._gain_skill_experience(caster)
        
        return True
    
    def _apply_effects(self, caster, target):
        """Применить эффекты умения"""
        for effect in self.effects:
            if effect.target == "self":
                self._apply_effect_to_entity(caster, effect)
            elif effect.target == "enemy" and target:
                self._apply_effect_to_entity(target, effect)
            elif effect.target == "area":
                self._apply_area_effect(caster, effect)
    
    def _apply_effect_to_entity(self, entity, effect: SkillEffect):
        """Применить эффект к сущности"""
        if hasattr(entity, 'add_effect'):
            entity.add_effect(
                f"{self.skill_id}_{effect.effect_type}",
                {
                    'type': effect.effect_type,
                    'value': effect.value * self.damage_modifier,
                    'duration': effect.duration,
                    'source': self.skill_id
                }
            )
    
    def _apply_area_effect(self, caster, effect: SkillEffect):
        """Применить эффект по области"""
        # Здесь должна быть логика поиска целей в радиусе
        # Пока просто применяем к кастеру
        self._apply_effect_to_entity(caster, effect)
    
    def _gain_skill_experience(self, caster):
        """Получить опыт за использование умения"""
        # Базовая логика получения опыта
        pass
    
    def update(self, delta_time: float):
        """Обновление умения"""
        if self.current_cooldown > 0:
            self.current_cooldown = max(0, self.current_cooldown - delta_time)
    
    def level_up(self) -> bool:
        """Повысить уровень умения"""
        if self.level >= self.max_level:
            return False
        
        self.level += 1
        self._update_skill_stats()
        return True
    
    def _update_skill_stats(self):
        """Обновить характеристики умения при повышении уровня"""
        # Базовые улучшения
        self.damage *= 1.1
        self.cooldown = max(0.1, self.cooldown * 0.95)
        self.mana_cost = max(0, int(self.mana_cost * 1.05))
        
        # Улучшение эффектов
        for effect in self.effects:
            effect.value *= 1.1
            if effect.duration > 0:
                effect.duration *= 1.05
    
    def can_learn(self, entity) -> bool:
        """Проверить, можно ли изучить умение"""
        if self.learned:
            return False
        
        # Проверка уровня
        if hasattr(entity, 'level') and entity.level < self.requirements.level:
            return False
        
        # Проверка характеристик
        for attr_type, required_value in self.requirements.attributes.items():
            if hasattr(entity, 'leveling_system'):
                current_value = entity.leveling_system.get_attribute_value(attr_type)
                if current_value < required_value:
                    return False
        
        # Проверка предыдущих умений
        for skill_id in self.requirements.skills:
            if not hasattr(entity, 'skill_system') or not entity.skill_system.has_skill(skill_id):
                return False
        
        # Проверка валюты
        if hasattr(entity, 'currency') and entity.currency < self.requirements.currency:
            return False
        
        return True
    
    def learn(self, entity) -> bool:
        """Изучить умение"""
        if not self.can_learn(entity):
            return False
        
        # Расход валюты
        if self.requirements.currency > 0 and hasattr(entity, 'currency'):
            entity.currency -= self.requirements.currency
        
        self.learned = True
        
        # Уведомляем систему умений
        if hasattr(entity, 'skill_system'):
            entity.skill_system.on_skill_learned(self)
        
        return True


class SkillSystem:
    """Система управления умениями сущности"""
    
    def __init__(self, entity):
        self.entity = entity
        self.skills: Dict[str, Skill] = {}
        self.active_skills: List[str] = []
        self.skill_points = 0
        
        # Инициализируем базовые умения
        self._init_basic_skills()
    
    def _init_basic_skills(self):
        """Инициализация базовых умений"""
        # Базовое атака
        basic_attack = Skill("basic_attack", "Базовая атака", SkillType.ACTIVE)
        basic_attack.damage = 15.0
        basic_attack.damage_type = DamageType.PHYSICAL
        basic_attack.cooldown = 1.0
        basic_attack.learned = True
        basic_attack.description = "Простая атака оружием"
        
        # Базовое лечение
        basic_heal = Skill("basic_heal", "Лечение", SkillType.ACTIVE)
        basic_heal.mana_cost = 20
        basic_heal.cooldown = 5.0
        basic_heal.effects = [
            SkillEffect("healing", 30.0, 0.0, "self")
        ]
        basic_heal.learned = True
        basic_heal.description = "Восстанавливает здоровье"
        
        self.add_skill(basic_attack)
        self.add_skill(basic_heal)
    
    def add_skill(self, skill: Skill):
        """Добавить умение в систему"""
        self.skills[skill.skill_id] = skill
    
    def remove_skill(self, skill_id: str):
        """Убрать умение из системы"""
        if skill_id in self.skills:
            del self.skills[skill_id]
            if skill_id in self.active_skills:
                self.active_skills.remove(skill_id)
    
    def has_skill(self, skill_id: str) -> bool:
        """Проверить наличие умения"""
        return skill_id in self.skills and self.skills[skill_id].learned
    
    def get_skill(self, skill_id: str) -> Optional[Skill]:
        """Получить умение по ID"""
        return self.skills.get(skill_id)
    
    def use_skill(self, skill_id: str, target=None) -> bool:
        """Использовать умение"""
        skill = self.get_skill(skill_id)
        if not skill:
            return False
        
        return skill.use(self.entity, target)
    
    def learn_skill(self, skill_id: str) -> bool:
        """Изучить умение"""
        skill = self.get_skill(skill_id)
        if not skill:
            return False
        
        return skill.learn(self.entity)
    
    def get_available_skills(self) -> List[Skill]:
        """Получить список доступных для изучения умений"""
        return [
            skill for skill in self.skills.values()
            if not skill.learned and skill.can_learn(self.entity)
        ]
    
    def get_learned_skills(self) -> List[Skill]:
        """Получить список изученных умений"""
        return [
            skill for skill in self.skills.values()
            if skill.learned
        ]
    
    def get_active_skills(self) -> List[Skill]:
        """Получить список активных умений"""
        return [
            skill for skill in self.skills.values()
            if skill.learned and skill.active
        ]
    
    def toggle_skill(self, skill_id: str):
        """Переключить активность умения"""
        skill = self.get_skill(skill_id)
        if not skill:
            return
        
        if skill_id in self.active_skills:
            self.active_skills.remove(skill_id)
            skill.active = False
        else:
            self.active_skills.append(skill_id)
            skill.active = True
    
    def on_skill_learned(self, skill: Skill):
        """Обработчик изучения умения"""
        print(f"Изучено новое умение: {skill.name}")
        
        # Можно добавить логику для автоматической активации умений
        if skill.skill_type == SkillType.PASSIVE:
            skill.active = True
            self.active_skills.append(skill.skill_id)
    
    def update(self, delta_time: float):
        """Обновление системы умений"""
        # Обновляем все умения
        for skill in self.skills.values():
            skill.update(delta_time)
        
        # Применяем эффекты пассивных умений
        for skill_id in self.active_skills:
            skill = self.get_skill(skill_id)
            if skill and skill.skill_type == SkillType.PASSIVE:
                self._apply_passive_skill_effects(skill)
    
    def _apply_passive_skill_effects(self, skill: Skill):
        """Применить эффекты пассивного умения"""
        # Базовая логика применения пассивных эффектов
        pass
    
    def get_skill_summary(self) -> Dict[str, Any]:
        """Получить сводку по умениям"""
        return {
            'total_skills': len(self.skills),
            'learned_skills': len(self.get_learned_skills()),
            'available_skills': len(self.get_available_skills()),
            'active_skills': len(self.active_skills),
            'skill_points': self.skill_points
        }
    
    def save_state(self) -> Dict[str, Any]:
        """Сохранить состояние системы умений"""
        return {
            'skills': {
                skill_id: {
                    'learned': skill.learned,
                    'level': skill.level,
                    'active': skill.active,
                    'current_cooldown': skill.current_cooldown
                }
                for skill_id, skill in self.skills.items()
            },
            'active_skills': self.active_skills,
            'skill_points': self.skill_points
        }
    
    def load_state(self, state: Dict[str, Any]):
        """Загрузить состояние системы умений"""
        skills_state = state.get('skills', {})
        for skill_id, skill_data in skills_state.items():
            if skill_id in self.skills:
                skill = self.skills[skill_id]
                skill.learned = skill_data.get('learned', False)
                skill.level = skill_data.get('level', 1)
                skill.active = skill_data.get('active', False)
                skill.current_cooldown = skill_data.get('current_cooldown', 0.0)
        
        self.active_skills = state.get('active_skills', [])
        self.skill_points = state.get('skill_points', 0)


# Предопределенные умения
class SkillLibrary:
    """Библиотека предопределенных умений"""
    
    @staticmethod
    def create_skill(skill_id: str, **kwargs) -> Skill:
        """Создать умение по шаблону"""
        skill = Skill(skill_id, kwargs.get('name', skill_id), kwargs.get('skill_type', SkillType.ACTIVE))
        
        # Применяем параметры
        for key, value in kwargs.items():
            if hasattr(skill, key):
                setattr(skill, key, value)
        
        return skill
    
    @staticmethod
    def get_warrior_skills() -> List[Skill]:
        """Получить умения воина"""
        skills = []
        
        # Силовой удар
        power_strike = SkillLibrary.create_skill(
            "power_strike",
            name="Силовой удар",
            skill_type=SkillType.ACTIVE,
            damage=25.0,
            damage_type=DamageType.PHYSICAL,
            cooldown=3.0,
            stamina_cost=15,
            requirements=SkillRequirement(2, {AttributeType.STRENGTH: 12}, []),
            description="Мощный удар, наносящий повышенный урон"
        )
        skills.append(power_strike)
        
        # Боевой дух
        battle_spirit = SkillLibrary.create_skill(
            "battle_spirit",
            name="Боевой дух",
            skill_type=SkillType.BUFF,
            mana_cost=25,
            cooldown=15.0,
            effects=[
                SkillEffect("damage_boost", 1.5, 10.0, "self"),
                SkillEffect("defense_boost", 1.3, 10.0, "self")
            ],
            requirements=SkillRequirement(3, {AttributeType.STRENGTH: 15, AttributeType.VITALITY: 12}, []),
            description="Увеличивает урон и защиту на время действия"
        )
        skills.append(battle_spirit)
        
        return skills
    
    @staticmethod
    def get_mage_skills() -> List[Skill]:
        """Получить умения мага"""
        skills = []
        
        # Огненный шар
        fireball = SkillLibrary.create_skill(
            "fireball",
            name="Огненный шар",
            skill_type=SkillType.ACTIVE,
            damage=35.0,
            damage_type=DamageType.FIRE,
            cooldown=2.0,
            mana_cost=30,
            range=150.0,
            requirements=SkillRequirement(2, {AttributeType.INTELLIGENCE: 12}, []),
            description="Запускает огненный шар в цель"
        )
        skills.append(fireball)
        
        # Щит мага
        mage_shield = SkillLibrary.create_skill(
            "mage_shield",
            name="Щит мага",
            skill_type=SkillType.BUFF,
            mana_cost=20,
            cooldown=8.0,
            effects=[
                SkillEffect("magic_shield", 50.0, 8.0, "self")
            ],
            requirements=SkillRequirement(3, {AttributeType.INTELLIGENCE: 15, AttributeType.FAITH: 10}, []),
            description="Создает магический щит, поглощающий урон"
        )
        skills.append(mage_shield)
        
        return skills
    
    @staticmethod
    def get_rogue_skills() -> List[Skill]:
        """Получить умения разбойника"""
        skills = []
        
        # Скрытая атака
        stealth_attack = SkillLibrary.create_skill(
            "stealth_attack",
            name="Скрытая атака",
            skill_type=SkillType.ACTIVE,
            damage=40.0,
            damage_type=DamageType.PHYSICAL,
            cooldown=5.0,
            stamina_cost=20,
            requirements=SkillRequirement(2, {AttributeType.DEXTERITY: 12}, []),
            description="Мощная атака из укрытия с повышенным критическим шансом"
        )
        skills.append(stealth_attack)
        
        # Уклонение
        evasion = SkillLibrary.create_skill(
            "evasion",
            name="Уклонение",
            skill_type=SkillType.PASSIVE,
            effects=[
                SkillEffect("dodge_chance", 0.15, 0.0, "self")
            ],
            requirements=SkillRequirement(3, {AttributeType.DEXTERITY: 15, AttributeType.LUCK: 10}, []),
            description="Увеличивает шанс уклонения от атак"
        )
        skills.append(evasion)
        
        return skills
