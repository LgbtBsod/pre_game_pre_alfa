import math

def iso_to_cart(x, y, z=0):
    cart_x = (x - y) * 40
    cart_y = (x + y) * 20 - z * 30
    return cart_x, cart_y

def cart_to_iso(cart_x, cart_y):
    iso_x = (cart_x / 40 + cart_y / 20) / 2
    iso_y = (cart_y / 20 - cart_x / 40) / 2
    return iso_x, iso_y

def distance_2d(x1, y1, x2, y2):
    """
    Возвращает евклидово расстояние между двумя точками на плоскости
    """
    return math.hypot(x2 - x1, y2 - y1)

def distance_entity(entity1, entity2):
    """
    Возвращает расстояние между двумя сущностями
    """
    return distance_2d(entity1.x, entity1.y, entity2.x, entity2.y)

def clamp(value, min_value, max_value):
    """
    Ограничивает значение диапазоном [min_value, max_value]
    """
    return max(min_value, min(value, max_value))

def lerp(a, b, t):
    """
    Линейная интерполяция между a и b по параметру t [0, 1]
    """
    return a + (b - a) * t

def normalize_angle(angle):
    """
    Нормализует угол в радианах в диапазоне [0, 2*pi)
    """
    return angle % (2 * math.pi)

def angle_between(entity1, entity2):
    """
    Возвращает угол от entity1 к entity2 в радианах
    """
    dx = entity2.x - entity1.x
    dy = entity2.y - entity1.y
    return math.atan2(dy, dx)

def is_visible(player, entity, visibility_range):
    """
    Проверяет, видна ли сущность игроку на основе расстояния
    """
    return distance_entity(player, entity) <= visibility_range

def get_direction_vector(angle):
    """
    Возвращает единичный вектор направления по заданному углу
    """
    return math.cos(angle), math.sin(angle)

def move_towards(current_x, current_y, target_x, target_y, speed):
    """
    Перемещает текущую позицию к цели со скоростью speed
    """
    dx = target_x - current_x
    dy = target_y - current_y
    dist = math.hypot(dx, dy)
    if dist == 0:
        return current_x, current_y
    dx_norm = dx / dist
    dy_norm = dy / dist
    new_x = current_x + dx_norm * speed
    new_y = current_y + dy_norm * speed
    return new_x, new_y

def in_bounds(x, y, width, height):
    """
    Проверяет, находится ли точка внутри границ карты
    """
    return 0 <= x < width and 0 <= y < height

def screen_to_world(screen_x, screen_y, camera):
    """
    Преобразует экранные координаты в мировые через камеру
    """
    world_x = screen_x - WIDTH // 2 + camera.x
    world_y = screen_y - HEIGHT // 3 + camera.y
    return cart_to_iso(world_x, world_y)

# Пример использования с глобальными константами
try:
    from config import WIDTH, HEIGHT
except ImportError:
    # Если нет config — используем дефолтные значения
    WIDTH, HEIGHT = 1200, 800