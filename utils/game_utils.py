"""Утилиты для игры."""

import math
import random
from typing import Tuple, List, Any, Dict


def distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    """Вычисление расстояния между двумя точками."""
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)


def normalize_vector(vector: Tuple[float, float]) -> Tuple[float, float]:
    """Нормализация вектора."""
    length = math.sqrt(vector[0]**2 + vector[1]**2)
    if length == 0:
        return (0, 0)
    return (vector[0] / length, vector[1] / length)


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Ограничение значения в заданном диапазоне."""
    return max(min_val, min(value, max_val))


def lerp(start: float, end: float, t: float) -> float:
    """Линейная интерполяция между двумя значениями."""
    return start + (end - start) * t


def smooth_step(start: float, end: float, t: float) -> float:
    """Плавная интерполяция с использованием функции smoothstep."""
    t = clamp(t, 0, 1)
    t = t * t * (3 - 2 * t)  # smoothstep
    return start + (end - start) * t


def random_point_in_circle(center: Tuple[float, float], radius: float) -> Tuple[float, float]:
    """Генерация случайной точки в круге."""
    angle = random.uniform(0, 2 * math.pi)
    r = radius * math.sqrt(random.uniform(0, 1))
    x = center[0] + r * math.cos(angle)
    y = center[1] + r * math.sin(angle)
    return (x, y)


def random_point_in_rectangle(center: Tuple[float, float], width: float, height: float) -> Tuple[float, float]:
    """Генерация случайной точки в прямоугольнике."""
    x = center[0] + random.uniform(-width/2, width/2)
    y = center[1] + random.uniform(-height/2, height/2)
    return (x, y)


def point_in_rectangle(point: Tuple[float, float], rect_center: Tuple[float, float], 
                      width: float, height: float) -> bool:
    """Проверка, находится ли точка в прямоугольнике."""
    x, y = point
    cx, cy = rect_center
    return (cx - width/2 <= x <= cx + width/2 and 
            cy - height/2 <= y <= cy + height/2)


def rotate_point(point: Tuple[float, float], center: Tuple[float, float], angle: float) -> Tuple[float, float]:
    """Поворот точки вокруг центра на заданный угол."""
    x, y = point
    cx, cy = center
    
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    new_x = cx + (x - cx) * cos_a - (y - cy) * sin_a
    new_y = cy + (x - cx) * sin_a + (y - cy) * cos_a
    
    return (new_x, new_y)


def angle_between_points(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    """Вычисление угла между двумя точками."""
    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]
    return math.atan2(dy, dx)


def move_towards(current_pos: Tuple[float, float], target_pos: Tuple[float, float], 
                speed: float, delta_time: float) -> Tuple[float, float]:
    """Движение к цели с заданной скоростью."""
    direction = normalize_vector((target_pos[0] - current_pos[0], target_pos[1] - current_pos[1]))
    distance_to_target = distance(current_pos, target_pos)
    
    if distance_to_target <= speed * delta_time:
        return target_pos
    
    new_x = current_pos[0] + direction[0] * speed * delta_time
    new_y = current_pos[1] + direction[1] * speed * delta_time
    
    return (new_x, new_y)


def calculate_damage(base_damage: float, attacker_level: int, target_defense: float, 
                    critical_chance: float = 0.05, critical_multiplier: float = 2.0) -> Dict[str, float]:
    """Расчет урона с учетом всех модификаторов."""
    # Базовый урон
    damage = base_damage
    
    # Модификатор уровня атакующего
    level_modifier = 1.0 + (attacker_level - 1) * 0.1
    damage *= level_modifier
    
    # Снижение урона защитой
    damage_reduction = target_defense / (target_defense + 100)  # Формула снижения урона
    damage *= (1 - damage_reduction)
    
    # Критический урон
    is_critical = random.random() < critical_chance
    if is_critical:
        damage *= critical_multiplier
    
    return {
        "total": damage,
        "base": base_damage,
        "level_modifier": level_modifier,
        "defense_reduction": damage_reduction,
        "is_critical": is_critical,
        "critical_multiplier": critical_multiplier if is_critical else 1.0
    }


def calculate_experience(level: int, base_xp: int = 100, multiplier: float = 1.5) -> int:
    """Расчет необходимого опыта для уровня."""
    if level <= 1:
        return 0
    return int(base_xp * (multiplier ** (level - 1)))


def calculate_level_from_xp(total_xp: int, base_xp: int = 100, multiplier: float = 1.5) -> int:
    """Расчет уровня на основе общего опыта."""
    if total_xp < base_xp:
        return 1
    
    level = 1
    xp_needed = base_xp
    
    while total_xp >= xp_needed:
        total_xp -= xp_needed
        level += 1
        xp_needed = int(base_xp * (multiplier ** (level - 1)))
    
    return level


def weighted_random_choice(choices: List[Tuple[Any, float]]) -> Any:
    """Случайный выбор с весами."""
    if not choices:
        return None
    
    total_weight = sum(weight for _, weight in choices)
    if total_weight <= 0:
        return choices[0][0] if choices else None
    
    random_value = random.uniform(0, total_weight)
    current_weight = 0
    
    for choice, weight in choices:
        current_weight += weight
        if random_value <= current_weight:
            return choice
    
    return choices[-1][0]


def interpolate_color(color1: Tuple[int, int, int], color2: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
    """Интерполяция между двумя цветами."""
    t = clamp(t, 0, 1)
    r = int(lerp(color1[0], color2[0], t))
    g = int(lerp(color1[1], color2[1], t))
    b = int(lerp(color1[2], color2[2], t))
    return (r, g, b)


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Конвертация RGB в HEX."""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Конвертация HEX в RGB."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def format_time(seconds: float) -> str:
    """Форматирование времени в читаемый вид."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        seconds = seconds % 60
        return f"{minutes}m {seconds:.1f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours}h {minutes}m {seconds:.1f}s"


def format_number(number: float) -> str:
    """Форматирование числа в читаемый вид."""
    if number < 1000:
        return f"{number:.1f}"
    elif number < 1000000:
        return f"{number/1000:.1f}K"
    else:
        return f"{number/1000000:.1f}M"


def deep_copy_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Глубокое копирование словаря."""
    if not isinstance(data, dict):
        return data
    
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = deep_copy_dict(value)
        elif isinstance(value, list):
            result[key] = [deep_copy_dict(item) if isinstance(item, dict) else item for item in value]
        else:
            result[key] = value
    
    return result
