"""
Система изометрической проекции и навигации
Обеспечивает изометрическое отображение мира и навигацию к маякам
"""

import math
import random
from typing import Tuple, List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class BeaconType(Enum):
    """Типы маяков"""
    NAVIGATION = "navigation"      # Навигационный маяк
    EVOLUTION = "evolution"        # Эволюционный маяк
    RESOURCE = "resource"          # Ресурсный маяк
    DANGER = "danger"             # Опасный маяк
    MYSTERY = "mystery"           # Загадочный маяк


@dataclass
class IsometricPoint:
    """Точка в изометрической проекции"""
    world_x: float
    world_y: float
    world_z: float
    screen_x: float = 0.0
    screen_y: float = 0.0


@dataclass
class Beacon:
    """Маяк для навигации"""
    id: str
    beacon_type: BeaconType
    position: Tuple[float, float, float]
    radius: float
    signal_strength: float
    active: bool = True
    discovered: bool = False
    activation_requirement: Optional[str] = None
    reward_data: Optional[Dict[str, Any]] = None


class IsometricProjection:
    """Система изометрической проекции"""
    
    def __init__(self, tile_width: int = 64, tile_height: int = 32):
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.camera_z = 0.0
        self.zoom = 1.0
        
        # Углы изометрии (стандартные)
        self.angle_x = math.radians(30)  # 30 градусов
        self.angle_y = math.radians(30)  # 30 градусов
    
    def world_to_iso(self, world_x: float, world_y: float, world_z: float = 0.0) -> Tuple[float, float]:
        """Преобразование мировых координат в изометрические"""
        # Стандартная изометрическая проекция
        iso_x = (world_x - world_y) * (self.tile_width / 2) * self.zoom
        iso_y = (world_x + world_y) * (self.tile_height / 2) * self.zoom - world_z * self.tile_height * self.zoom
        
        # Применение смещения камеры
        iso_x -= self.camera_x
        iso_y -= self.camera_y
        
        return iso_x, iso_y
    
    def iso_to_world(self, iso_x: float, iso_y: float, world_z: float = 0.0) -> Tuple[float, float]:
        """Преобразование изометрических координат в мировые"""
        # Учет камеры
        iso_x += self.camera_x
        iso_y += self.camera_y + world_z * self.tile_height * self.zoom
        
        # Обратное преобразование
        world_x = (iso_x / (self.tile_width / 2) + iso_y / (self.tile_height / 2)) / (2 * self.zoom)
        world_y = (iso_y / (self.tile_height / 2) - iso_x / (self.tile_width / 2)) / (2 * self.zoom)
        
        return world_x, world_y
    
    def move_camera(self, dx: float, dy: float):
        """Перемещение камеры"""
        self.camera_x += dx
        self.camera_y += dy
    
    def set_zoom(self, zoom: float):
        """Установка масштаба"""
        self.zoom = max(0.1, min(5.0, zoom))
    
    def focus_on_point(self, world_x: float, world_y: float, screen_width: int, screen_height: int):
        """Фокусировка камеры на точке с плавным следованием"""
        target_iso_x, target_iso_y = self.world_to_iso(world_x, world_y)
        target_camera_x = target_iso_x - screen_width / 2
        target_camera_y = target_iso_y - screen_height / 2
        
        # Плавное следование камеры (сглаживание) - уменьшаем для стабильности
        smoothing_factor = 0.05  # Уменьшено с 0.1 для более плавного движения
        self.camera_x += (target_camera_x - self.camera_x) * smoothing_factor
        self.camera_y += (target_camera_y - self.camera_y) * smoothing_factor
        
        # Ограничиваем движение камеры для предотвращения "прыжков"
        max_camera_movement = 5.0
        if abs(target_camera_x - self.camera_x) < max_camera_movement:
            self.camera_x = target_camera_x
        if abs(target_camera_y - self.camera_y) < max_camera_movement:
            self.camera_y = target_camera_y


class PathfindingNode:
    """Узел для алгоритма поиска пути"""
    
    def __init__(self, x: int, y: int, g_cost: float = 0, h_cost: float = 0, parent=None):
        self.x = x
        self.y = y
        self.g_cost = g_cost  # Стоимость от начала
        self.h_cost = h_cost  # Эвристическая стоимость до цели
        self.f_cost = g_cost + h_cost  # Общая стоимость
        self.parent = parent
    
    def __lt__(self, other):
        return self.f_cost < other.f_cost
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class AStarPathfinder:
    """Алгоритм поиска пути A*"""
    
    def __init__(self, grid_width: int, grid_height: int):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.obstacles = set()  # Множество координат препятствий
    
    def add_obstacle(self, x: int, y: int):
        """Добавление препятствия"""
        self.obstacles.add((x, y))
    
    def remove_obstacle(self, x: int, y: int):
        """Удаление препятствия"""
        self.obstacles.discard((x, y))
    
    def is_walkable(self, x: int, y: int) -> bool:
        """Проверка проходимости клетки"""
        return (0 <= x < self.grid_width and 
                0 <= y < self.grid_height and 
                (x, y) not in self.obstacles)
    
    def get_neighbors(self, node: PathfindingNode) -> List[PathfindingNode]:
        """Получение соседних узлов"""
        neighbors = []
        
        # 8 направлений (включая диагонали)
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        for dx, dy in directions:
            new_x, new_y = node.x + dx, node.y + dy
            
            if self.is_walkable(new_x, new_y):
                # Диагональное движение стоит дороже
                move_cost = 1.4 if dx != 0 and dy != 0 else 1.0
                neighbors.append(PathfindingNode(new_x, new_y))
        
        return neighbors
    
    def heuristic(self, node: PathfindingNode, target: PathfindingNode) -> float:
        """Эвристическая функция (Манхэттенское расстояние)"""
        return abs(node.x - target.x) + abs(node.y - target.y)
    
    def find_path(self, start_x: int, start_y: int, target_x: int, target_y: int) -> List[Tuple[int, int]]:
        """Поиск пути от начальной точки к цели"""
        import heapq
        
        start_node = PathfindingNode(start_x, start_y)
        target_node = PathfindingNode(target_x, target_y)
        
        open_list = [start_node]
        closed_set = set()
        
        while open_list:
            current_node = heapq.heappop(open_list)
            
            if current_node == target_node:
                # Восстановление пути
                path = []
                while current_node:
                    path.append((current_node.x, current_node.y))
                    current_node = current_node.parent
                return path[::-1]  # Обратный порядок
            
            closed_set.add((current_node.x, current_node.y))
            
            for neighbor in self.get_neighbors(current_node):
                if (neighbor.x, neighbor.y) in closed_set:
                    continue
                
                # Расчет стоимости
                move_cost = 1.4 if abs(neighbor.x - current_node.x) == 1 and abs(neighbor.y - current_node.y) == 1 else 1.0
                tentative_g_cost = current_node.g_cost + move_cost
                
                # Проверяем, есть ли уже этот узел в открытом списке
                existing_node = None
                for node in open_list:
                    if node.x == neighbor.x and node.y == neighbor.y:
                        existing_node = node
                        break
                
                if existing_node is None or tentative_g_cost < existing_node.g_cost:
                    neighbor.g_cost = tentative_g_cost
                    neighbor.h_cost = self.heuristic(neighbor, target_node)
                    neighbor.f_cost = neighbor.g_cost + neighbor.h_cost
                    neighbor.parent = current_node
                    
                    if existing_node is None:
                        heapq.heappush(open_list, neighbor)
                    else:
                        # Обновляем существующий узел
                        existing_node.g_cost = neighbor.g_cost
                        existing_node.f_cost = neighbor.f_cost
                        existing_node.parent = neighbor.parent
                        heapq.heapify(open_list)
        
        return []  # Путь не найден


class BeaconNavigationSystem:
    """Система навигации по маякам"""
    
    def __init__(self, world_width: int = 1000, world_height: int = 1000):
        self.world_width = world_width
        self.world_height = world_height
        self.beacons: Dict[str, Beacon] = {}
        self.active_target: Optional[str] = None
        self.pathfinder = AStarPathfinder(world_width // 10, world_height // 10)  # Сетка 10x10 пикселей
        
        # Генерация начальных маяков
        self._generate_initial_beacons()
    
    def _generate_initial_beacons(self):
        """Генерация начального маяка"""
        # Создаем только один скрытый маяк, который нужно найти
        beacon_position = (
            random.randint(300, 700),  # Случайная позиция
            random.randint(300, 700),
            0
        )
        
        beacon_config = {
            "id": "BEACON_TARGET",
            "type": BeaconType.MYSTERY,
            "position": beacon_position,
            "radius": 50,  # Небольшой радиус обнаружения
            "signal_strength": 0.0,  # Изначально нет сигнала
            "discovered": False  # Скрыт
        }
        
        beacon = Beacon(
            id=beacon_config["id"],
            beacon_type=beacon_config["type"],
            position=beacon_config["position"],
            radius=beacon_config["radius"],
            signal_strength=beacon_config["signal_strength"],
            discovered=beacon_config["discovered"]
        )
        self.beacons[beacon.id] = beacon
        
        logger.info(f"Создан скрытый маяк в позиции {beacon_position}")
    
    def discover_beacon(self, entity_position: Tuple[float, float, float]) -> Optional[Beacon]:
        """Обнаружение маяка рядом с сущностью"""
        for beacon in self.beacons.values():
            if not beacon.discovered and beacon.active:
                distance = self._calculate_distance(entity_position, beacon.position)
                if distance <= beacon.radius:
                    beacon.discovered = True
                    logger.info(f"Обнаружен маяк {beacon.id} типа {beacon.beacon_type.value}")
                    return beacon
        return None
    
    def get_nearest_beacon(self, entity_position: Tuple[float, float, float], 
                          beacon_type: Optional[BeaconType] = None) -> Optional[Beacon]:
        """Поиск ближайшего маяка"""
        nearest_beacon = None
        min_distance = float('inf')
        
        for beacon in self.beacons.values():
            if not beacon.discovered or not beacon.active:
                continue
            
            if beacon_type and beacon.beacon_type != beacon_type:
                continue
            
            distance = self._calculate_distance(entity_position, beacon.position)
            if distance < min_distance:
                min_distance = distance
                nearest_beacon = beacon
        
        return nearest_beacon
    
    def set_navigation_target(self, beacon_id: str) -> bool:
        """Установка цели навигации"""
        if beacon_id in self.beacons and self.beacons[beacon_id].discovered:
            self.active_target = beacon_id
            logger.info(f"Установлена цель навигации: {beacon_id}")
            return True
        return False
    
    def get_navigation_direction(self, entity_position: Tuple[float, float, float]) -> Optional[Tuple[float, float]]:
        """Получение направления к активной цели"""
        if not self.active_target or self.active_target not in self.beacons:
            return None
        
        target_beacon = self.beacons[self.active_target]
        if not target_beacon.active:
            return None
        
        # Простое направление (можно заменить на A*)
        dx = target_beacon.position[0] - entity_position[0]
        dy = target_beacon.position[1] - entity_position[1]
        
        # Нормализация
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 0:
            return (dx / distance, dy / distance)
        
        return None
    
    def find_path_to_beacon(self, start_pos: Tuple[float, float], beacon_id: str) -> List[Tuple[int, int]]:
        """Поиск пути к маяку с использованием A*"""
        if beacon_id not in self.beacons:
            return []
        
        beacon = self.beacons[beacon_id]
        
        # Преобразование в координаты сетки
        start_grid_x = int(start_pos[0] // 10)
        start_grid_y = int(start_pos[1] // 10)
        target_grid_x = int(beacon.position[0] // 10)
        target_grid_y = int(beacon.position[1] // 10)
        
        return self.pathfinder.find_path(start_grid_x, start_grid_y, target_grid_x, target_grid_y)
    
    def update_beacon_signals(self, entity_position: Tuple[float, float, float]):
        """Обновление сигналов маяков"""
        for beacon in self.beacons.values():
            if beacon.active:
                distance = self._calculate_distance(entity_position, beacon.position)
                # Сила сигнала уменьшается с расстоянием
                signal_factor = max(0.0, 1.0 - distance / (beacon.radius * 2))
                beacon.signal_strength = signal_factor
    
    def _calculate_distance(self, pos1: Tuple[float, float, float], pos2: Tuple[float, float, float]) -> float:
        """Расчет расстояния между двумя точками"""
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        dz = pos1[2] - pos2[2]
        return math.sqrt(dx * dx + dy * dy + dz * dz)
    
    def get_beacon_info(self) -> Dict[str, Any]:
        """Получение информации о маяках"""
        return {
            "total_beacons": len(self.beacons),
            "discovered_beacons": sum(1 for b in self.beacons.values() if b.discovered),
            "active_target": self.active_target,
            "beacon_list": [
                {
                    "id": beacon.id,
                    "type": beacon.beacon_type.value,
                    "discovered": beacon.discovered,
                    "signal_strength": beacon.signal_strength,
                    "position": beacon.position
                }
                for beacon in self.beacons.values()
            ]
        }


class IsometricRenderer:
    """Рендерер для изометрической проекции"""
    
    def __init__(self, projection: IsometricProjection):
        self.projection = projection
        self.tile_cache = {}  # Кэш для тайлов
    
    def render_tile(self, screen, world_x: int, world_y: int, tile_type: str, color: Tuple[int, int, int]):
        """Отрисовка тайла"""
        iso_x, iso_y = self.projection.world_to_iso(world_x, world_y)
        
        # Простая ромбовидная форма тайла
        tile_w = self.projection.tile_width
        tile_h = self.projection.tile_height
        
        # Четыре точки ромба
        points = [
            (iso_x, iso_y - tile_h // 2),  # Верх
            (iso_x + tile_w // 2, iso_y),  # Право
            (iso_x, iso_y + tile_h // 2),  # Низ
            (iso_x - tile_w // 2, iso_y)   # Лево
        ]
        
        try:
            import pygame
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, (0, 0, 0), points, 1)  # Контур
        except ImportError:
            pass
    
    def render_entity(self, screen, entity_position: Tuple[float, float, float], color: Tuple[int, int, int], size: int = 16):
        """Отрисовка сущности"""
        iso_x, iso_y = self.projection.world_to_iso(*entity_position)
        
        try:
            import pygame
            pygame.draw.circle(screen, color, (int(iso_x), int(iso_y)), size)
            pygame.draw.circle(screen, (0, 0, 0), (int(iso_x), int(iso_y)), size, 2)
        except ImportError:
            pass
    
    def render_beacon(self, screen, beacon: Beacon, discovered: bool = True):
        """Отрисовка маяка"""
        if not discovered and not beacon.discovered:
            return
        
        iso_x, iso_y = self.projection.world_to_iso(*beacon.position)
        
        try:
            import pygame
            
            # Цвет маяка в зависимости от типа
            colors = {
                BeaconType.NAVIGATION: (0, 255, 0),    # Зеленый
                BeaconType.EVOLUTION: (255, 0, 255),   # Фиолетовый
                BeaconType.RESOURCE: (255, 255, 0),    # Желтый
                BeaconType.DANGER: (255, 0, 0),        # Красный
                BeaconType.MYSTERY: (0, 255, 255)      # Голубой
            }
            
            color = colors.get(beacon.beacon_type, (255, 255, 255))
            
            # Основной маяк
            pygame.draw.circle(screen, color, (int(iso_x), int(iso_y)), 20)
            
            # Сигнал маяка (пульсирующий эффект)
            if beacon.active and beacon.signal_strength > 0:
                signal_radius = int(20 + beacon.signal_strength * 30)
                signal_color = (*color, int(beacon.signal_strength * 100))
                pygame.draw.circle(screen, signal_color, (int(iso_x), int(iso_y)), signal_radius, 2)
        except ImportError:
            pass
