"""
Утилиты для работы со статистиками и шаблонами сущностей.
Содержит функции для работы с характеристиками, шаблонами и валидацией.
"""

from typing import Dict, List, Any, Optional
from .constants import BASE_STATS


# Группы статистик для удобной работы
STAT_GROUPS = {
    "core_attributes": ["strength", "agility", "intelligence", "constitution", "wisdom", "charisma", "luck"],
    "combat_stats": ["attack", "defense", "critical_chance", "critical_multiplier", "attack_speed", "range"],
    "resource_stats": ["health", "max_health", "mana", "max_mana", "stamina", "max_stamina"],
    "toughness_stats": ["toughness", "toughness_resistance", "stun_resistance", "break_efficiency"],
    "defense_stats": ["parry_chance", "evasion_chance", "resist_chance"],
    "regen_stats": ["health_regen", "mana_regen", "stamina_regen"],
    "all_stats": ["strength", "agility", "intelligence", "constitution", "wisdom", "charisma", "luck",
                  "attack", "defense", "critical_chance", "critical_multiplier", "attack_speed", "range",
                  "health", "max_health", "mana", "max_mana", "stamina", "max_stamina",
                  "toughness", "toughness_resistance", "stun_resistance", "break_efficiency",
                  "parry_chance", "evasion_chance", "resist_chance",
                  "health_regen", "mana_regen", "stamina_regen"]
}

# Шаблоны атрибутов для разных типов сущностей
ENTITY_STAT_TEMPLATES = {
    "warrior": {
        "strength": 8,
        "agility": 6,
        "intelligence": 3,
        "constitution": 9,
        "wisdom": 4,
        "charisma": 5,
        "luck": 4
    },
    "mage": {
        "strength": 3,
        "agility": 4,
        "intelligence": 9,
        "constitution": 5,
        "wisdom": 8,
        "charisma": 6,
        "luck": 5
    },
    "rogue": {
        "strength": 5,
        "agility": 9,
        "intelligence": 6,
        "constitution": 4,
        "wisdom": 5,
        "charisma": 7,
        "luck": 8
    },
    "balanced": {
        "strength": 6,
        "agility": 6,
        "intelligence": 6,
        "constitution": 6,
        "wisdom": 6,
        "charisma": 6,
        "luck": 6
    },
    "tank": {
        "strength": 7,
        "agility": 4,
        "intelligence": 3,
        "constitution": 10,
        "wisdom": 5,
        "charisma": 4,
        "luck": 3
    },
    "archer": {
        "strength": 6,
        "agility": 8,
        "intelligence": 5,
        "constitution": 5,
        "wisdom": 6,
        "charisma": 5,
        "luck": 7
    }
}


def get_stats_by_group(group_name: str) -> List[str]:
    """
    Получает список названий статистик, принадлежащих указанной группе.
    
    Args:
        group_name: Название группы статистик
        
    Returns:
        Список названий статистик в группе
        
    Raises:
        KeyError: Если группа не найдена
    """
    if group_name not in STAT_GROUPS:
        raise KeyError(f"Группа статистик '{group_name}' не найдена. Доступные группы: {list(STAT_GROUPS.keys())}")
    return STAT_GROUPS[group_name]


def get_entity_template(template_name: str) -> Dict[str, int]:
    """
    Получает шаблон атрибутов для указанного типа сущности.
    
    Args:
        template_name: Название шаблона
        
    Returns:
        Словарь с базовыми значениями атрибутов
        
    Raises:
        KeyError: Если шаблон не найден
    """
    if template_name not in ENTITY_STAT_TEMPLATES:
        raise KeyError(f"Шаблон '{template_name}' не найден. Доступные шаблоны: {list(ENTITY_STAT_TEMPLATES.keys())}")
    return ENTITY_STAT_TEMPLATES[template_name].copy()


def apply_stat_template(base_stats: dict, template_name: str, level: int = 1) -> dict:
    """
    Применяет шаблон атрибутов к базовым характеристикам с масштабированием по уровню.
    
    Args:
        base_stats: Базовые характеристики
        template_name: Название шаблона для применения
        level: Уровень для масштабирования (по умолчанию 1)
        
    Returns:
        Новый словарь характеристик с примененным шаблоном
    """
    template = get_entity_template(template_name)
    result = base_stats.copy()
    
    # Применяем шаблон атрибутов с масштабированием по уровню
    for attr, value in template.items():
        if attr in result:
            # Атрибуты масштабируются линейно с уровнем
            result[attr] = value * level
        else:
            result[attr] = value * level
    
    return result


def validate_stats(stats: dict) -> Dict[str, Any]:
    """
    Валидирует словарь характеристик на полноту и разумность значений.
    
    Args:
        stats: Словарь характеристик для валидации
        
    Returns:
        Словарь с результатами валидации (issues, warnings, is_valid)
    """
    issues = []
    warnings = []
    
    # Проверяем наличие всех базовых атрибутов
    required_attrs = STAT_GROUPS["core_attributes"]
    missing_attrs = [attr for attr in required_attrs if attr not in stats]
    if missing_attrs:
        issues.append(f"Отсутствуют обязательные атрибуты: {missing_attrs}")
    
    # Проверяем разумность значений атрибутов
    for attr in required_attrs:
        if attr in stats:
            value = stats[attr]
            if not isinstance(value, (int, float)) or value < 0:
                issues.append(f"Атрибут {attr} должен быть положительным числом, получено: {value}")
            elif value > 100:
                warnings.append(f"Атрибут {attr} имеет очень высокое значение: {value}")
    
    # Проверяем другие характеристики
    for stat_name, value in stats.items():
        if stat_name not in required_attrs:
            if isinstance(value, (int, float)):
                if value < 0 and stat_name not in ["critical_chance", "parry_chance", "evasion_chance", "resist_chance"]:
                    issues.append(f"Характеристика {stat_name} не может быть отрицательной: {value}")
                elif value > 1000:
                    warnings.append(f"Характеристика {stat_name} имеет очень высокое значение: {value}")
    
    is_valid = len(issues) == 0
    
    return {
        "is_valid": is_valid,
        "issues": issues,
        "warnings": warnings
    }


def merge_stats(base_stats: dict, additional_stats: dict, override: bool = False) -> dict:
    """
    Объединяет два словаря характеристик.
    
    Args:
        base_stats: Базовые характеристики
        additional_stats: Дополнительные характеристики для добавления
        override: Если True, перезаписывает существующие значения, иначе добавляет к ним
        
    Returns:
        Объединенный словарь характеристик
    """
    result = base_stats.copy()
    
    for key, value in additional_stats.items():
        if key in result and not override:
            # Добавляем к существующему значению
            if isinstance(value, (int, float)) and isinstance(result[key], (int, float)):
                result[key] += value
            else:
                # Для нечисловых значений перезаписываем
                result[key] = value
        else:
            # Просто добавляем новое значение
            result[key] = value
    
    return result


def scale_stats_by_level(stats: dict, level: int, base_level: int = 1) -> dict:
    """
    Масштабирует числовые характеристики на основе уровня.
    
    Args:
        stats: Словарь характеристик для масштабирования
        level: Целевой уровень
        base_level: Базовый уровень (по умолчанию 1)
        
    Returns:
        Словарь с масштабированными характеристиками
    """
    if level <= 0:
        raise ValueError("Уровень должен быть положительным числом")
    
    if base_level <= 0:
        raise ValueError("Базовый уровень должен быть положительным числом")
    
    result = {}
    scale_factor = level / base_level
    
    for key, value in stats.items():
        if isinstance(value, (int, float)):
            if key in STAT_GROUPS["core_attributes"]:
                # Атрибуты масштабируются линейно
                result[key] = int(value * scale_factor)
            else:
                # Остальные характеристики масштабируются по квадратичному закону
                result[key] = int(value * (scale_factor ** 0.5))
        else:
            # Нечисловые значения копируются как есть
            result[key] = value
    
    return result


def calculate_stats_from_attributes(base_stats: dict, attributes: dict) -> dict:
    """
    Рассчитывает производные характеристики из атрибутов.
    
    Args:
        base_stats: Базовые характеристики
        attributes: Словарь атрибутов
        
    Returns:
        Словарь с рассчитанными характеристиками
    """
    from .constants import STAT_CALCULATION_FORMULAS
    
    result = base_stats.copy()
    
    # Применяем формулы расчета для каждой характеристики
    for stat_name, formula in STAT_CALCULATION_FORMULAS.items():
        try:
            calculated_value = formula(attributes)
            result[stat_name] = calculated_value
        except Exception as e:
            # Если не удалось рассчитать, оставляем базовое значение
            continue
    
    return result


def get_skill_cost_multiplier(cost_sources: list) -> float:
    """
    Рассчитывает множитель силы навыка на основе количества источников затрат.
    
    Args:
        cost_sources: Список источников затрат (например, ["mana", "stamina"])
        
    Returns:
        Множитель силы навыка
    """
    from .constants import SKILL_POWER_MULTIPLIERS
    
    cost_count = len(cost_sources)
    if cost_count == 0:
        return SKILL_POWER_MULTIPLIERS["no_cost"]
    elif cost_count == 1:
        return SKILL_POWER_MULTIPLIERS["single_cost"]
    elif cost_count == 2:
        return SKILL_POWER_MULTIPLIERS["dual_cost"]
    else:
        return SKILL_POWER_MULTIPLIERS["triple_cost"]
