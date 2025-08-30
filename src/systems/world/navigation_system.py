#!/usr/bin/env python3
"""Система навигации для игрового мира
Включает мини-карту, GPS, компас и путевые точки"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Set
import logging
import random
import time
import math

from src.core.architecture import BaseComponent, ComponentType, Priority

# = ТИПЫ НАВИГАЦИИ
class MapType(Enum):
    """Типы карт"""
    MINI_MAP = "mini_map"       # Мини-карта
    WORLD_MAP = "world_map"     # Карта мира
    DUNGEON_MAP = "dungeon_map" # Карта подземелья
    REGIONAL_MAP = "regional_map"  # Региональная карта

class WaypointType(Enum):
    """Типы путевых точек"""
    PLAYER = "player"           # Игрок
    QUEST = "quest"             # Квест
    TRADE = "trade"             # Торговля
    DANGER = "danger"           # Опасность
    RESOURCE = "resource"       # Ресурс
    SETTLEMENT = "settlement"   # Поселение
    DUNGEON = "dungeon"         # Подземелье
    CUSTOM = "custom"           # Пользовательская

class CompassDirection(Enum):
    """Направления компаса"""
    NORTH = "north"
    NORTHEAST = "northeast"
    EAST = "east"
    SOUTHEAST = "southeast"
    SOUTH = "south"
    SOUTHWEST = "southwest"
    WEST = "west"
    NORTHWEST = "northwest"

# = ДАТАКЛАССЫ
@dataclass
class NavigationSettings:
    """Настройки навигации"""
    mini_map_size: int = 200
    world_map_size: int = 1000
    compass_update_rate: float = 0.1  # секунды
    gps_update_rate: float = 0.05     # секунды
    waypoint_max_distance: float = 1000.0
    auto_save_waypoints: bool = True

@dataclass
class Waypoint:
    """Путевая точка"""
    waypoint_id: str
    waypoint_type: WaypointType
    x: float
    y: float
    z: float = 0.0
    name: str = ""
    description: str = ""
    icon: str = ""
    color: str = "#FFFFFF"
    visible: bool = True
    permanent: bool = False
    creation_time: float = field(default_factory=time.time)
    last_visited: float = field(default_factory=time.time)

@dataclass
class MapLayer:
    """Слой карты"""
    layer_id: str
    layer_name: str
    visible: bool = True
    opacity: float = 1.0
    data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MapData:
    """Данные карты"""
    map_id: str
    map_type: MapType
    width: int
    height: int
    center_x: float = 0.0
    center_y: float = 0.0
    scale: float = 1.0
    layers: Dict[str, MapLayer] = field(default_factory=dict)
    waypoints: Dict[str, Waypoint] = field(default_factory=dict)
    last_update: float = field(default_factory=time.time)

@dataclass
class GPSData:
    """GPS данные"""
    latitude: float = 0.0
    longitude: float = 0.0
    altitude: float = 0.0
    accuracy: float = 1.0
    timestamp: float = field(default_factory=time.time)

@dataclass
class CompassData:
    """Данные компаса"""
    direction: CompassDirection = CompassDirection.NORTH
    heading: float = 0.0  # градусы
    magnetic_declination: float = 0.0
    timestamp: float = field(default_factory=time.time)

# = ОСНОВНАЯ СИСТЕМА НАВИГАЦИИ
class NavigationSystem(BaseComponent):
    """Система навигации для игрового мира"""
    
    def __init__(self):
        super().__init__(
            component_id="NavigationSystem",
            component_type=ComponentType.SYSTEM,
            priority=Priority.HIGH
        )
        
        # Настройки навигации
        self.settings = NavigationSettings()
        
        # Карты
        self.maps: Dict[str, MapData] = {}
        
        # GPS данные
        self.gps_data = GPSData()
        
        # Данные компаса
        self.compass_data = CompassData()
        
        # Путевые точки
        self.waypoints: Dict[str, Waypoint] = {}
        
        # Позиция игрока
        self.player_position = (0.0, 0.0, 0.0)
        
        # Статистика
        self.navigation_stats = {
            "total_waypoints": 0,
            "maps_created": 0,
            "gps_updates": 0,
            "compass_updates": 0
        }
        
        # Время последних обновлений
        self.last_gps_update = 0.0
        self.last_compass_update = 0.0
    
    def _on_initialize(self) -> bool:
        """Инициализация системы навигации"""
        try:
            # Создаем основные карты
            self._create_default_maps()
            
            # Создаем базовые путевые точки
            self._create_default_waypoints()
            
            self._logger.info("Система навигации инициализирована")
            return True
        except Exception as e:
            self._logger.error(f"Ошибка инициализации системы навигации: {e}")
            return False
    
    def _create_default_maps(self):
        """Создание карт по умолчанию"""
        try:
            # Мини-карта
            mini_map = MapData(
                map_id="mini_map",
                map_type=MapType.MINI_MAP,
                width=self.settings.mini_map_size,
                height=self.settings.mini_map_size
            )
            self.maps["mini_map"] = mini_map
            
            # Карта мира
            world_map = MapData(
                map_id="world_map",
                map_type=MapType.WORLD_MAP,
                width=self.settings.world_map_size,
                height=self.settings.world_map_size
            )
            self.maps["world_map"] = world_map
            
            self.navigation_stats["maps_created"] = len(self.maps)
            
        except Exception as e:
            self._logger.error(f"Ошибка создания карт по умолчанию: {e}")
    
    def _create_default_waypoints(self):
        """Создание базовых путевых точек"""
        try:
            # Путевая точка игрока
            player_waypoint = Waypoint(
                waypoint_id="player",
                waypoint_type=WaypointType.PLAYER,
                x=0.0,
                y=0.0,
                z=0.0,
                name="Игрок",
                description="Ваша текущая позиция",
                icon="player_icon",
                color="#00FF00",
                permanent=True
            )
            self.waypoints["player"] = player_waypoint
            
            self.navigation_stats["total_waypoints"] = len(self.waypoints)
            
        except Exception as e:
            self._logger.error(f"Ошибка создания базовых путевых точек: {e}")
    
    def update_player_position(self, x: float, y: float, z: float = 0.0):
        """Обновление позиции игрока"""
        try:
            self.player_position = (x, y, z)
            
            # Обновляем GPS данные
            self._update_gps_data(x, y, z)
            
            # Обновляем компас
            self._update_compass_data()
            
            # Обновляем путевую точку игрока
            if "player" in self.waypoints:
                self.waypoints["player"].x = x
                self.waypoints["player"].y = y
                self.waypoints["player"].z = z
                self.waypoints["player"].last_visited = time.time()
            
            # Обновляем центры карт
            self._update_map_centers(x, y)
            
        except Exception as e:
            self._logger.error(f"Ошибка обновления позиции игрока: {e}")
    
    def _update_gps_data(self, x: float, y: float, z: float):
        """Обновление GPS данных"""
        try:
            current_time = time.time()
            
            # Обновляем только с заданной частотой
            if current_time - self.last_gps_update >= self.settings.gps_update_rate:
                self.gps_data.latitude = x
                self.gps_data.longitude = y
                self.gps_data.altitude = z
                self.gps_data.timestamp = current_time
                self.gps_data.accuracy = random.uniform(0.5, 2.0)  # Симуляция точности GPS
                
                self.last_gps_update = current_time
                self.navigation_stats["gps_updates"] += 1
                
        except Exception as e:
            self._logger.error(f"Ошибка обновления GPS данных: {e}")
    
    def _update_compass_data(self):
        """Обновление данных компаса"""
        try:
            current_time = time.time()
            
            # Обновляем только с заданной частотой
            if current_time - self.last_compass_update >= self.settings.compass_update_rate:
                # Симулируем направление на основе позиции игрока
                heading = math.atan2(self.player_position[1], self.player_position[0])
                heading_degrees = math.degrees(heading)
                
                # Нормализуем до 0-360 градусов
                heading_degrees = (heading_degrees + 360) % 360
                
                self.compass_data.heading = heading_degrees
                self.compass_data.direction = self._get_compass_direction(heading_degrees)
                self.compass_data.timestamp = current_time
                
                self.last_compass_update = current_time
                self.navigation_stats["compass_updates"] += 1
                
        except Exception as e:
            self._logger.error(f"Ошибка обновления данных компаса: {e}")
    
    def _get_compass_direction(self, heading: float) -> CompassDirection:
        """Определение направления компаса по градусам"""
        try:
            # Разбиваем на 8 направлений
            directions = [
                (0, 45, CompassDirection.NORTH),
                (45, 90, CompassDirection.NORTHEAST),
                (90, 135, CompassDirection.EAST),
                (135, 180, CompassDirection.SOUTHEAST),
                (180, 225, CompassDirection.SOUTH),
                (225, 270, CompassDirection.SOUTHWEST),
                (270, 315, CompassDirection.WEST),
                (315, 360, CompassDirection.NORTHWEST)
            ]
            
            for min_angle, max_angle, direction in directions:
                if min_angle <= heading < max_angle:
                    return direction
            
            return CompassDirection.NORTH
            
        except Exception as e:
            self._logger.error(f"Ошибка определения направления компаса: {e}")
            return CompassDirection.NORTH
    
    def _update_map_centers(self, x: float, y: float):
        """Обновление центров карт"""
        try:
            for map_data in self.maps.values():
                map_data.center_x = x
                map_data.center_y = y
                map_data.last_update = time.time()
                
        except Exception as e:
            self._logger.error(f"Ошибка обновления центров карт: {e}")
    
    def add_waypoint(self, waypoint_type: WaypointType, x: float, y: float, 
                     z: float = 0.0, name: str = "", description: str = "") -> str:
        """Добавление путевой точки"""
        try:
            waypoint_id = f"waypoint_{waypoint_type.value}_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
            
            waypoint = Waypoint(
                waypoint_id=waypoint_id,
                waypoint_type=waypoint_type,
                x=x,
                y=y,
                z=z,
                name=name or f"{waypoint_type.value.title()}",
                description=description,
                icon=self._get_waypoint_icon(waypoint_type),
                color=self._get_waypoint_color(waypoint_type)
            )
            
            self.waypoints[waypoint_id] = waypoint
            self.navigation_stats["total_waypoints"] += 1
            
            self._logger.info(f"Добавлена путевая точка {waypoint_id} в позиции ({x}, {y})")
            
            return waypoint_id
            
        except Exception as e:
            self._logger.error(f"Ошибка добавления путевой точки: {e}")
            return ""
    
    def remove_waypoint(self, waypoint_id: str) -> bool:
        """Удаление путевой точки"""
        try:
            if waypoint_id in self.waypoints:
                waypoint = self.waypoints[waypoint_id]
                
                # Не удаляем постоянные точки
                if waypoint.permanent:
                    self._logger.warning(f"Попытка удаления постоянной путевой точки {waypoint_id}")
                    return False
                
                del self.waypoints[waypoint_id]
                self.navigation_stats["total_waypoints"] -= 1
                
                self._logger.info(f"Удалена путевая точка {waypoint_id}")
                return True
            
            return False
            
        except Exception as e:
            self._logger.error(f"Ошибка удаления путевой точки {waypoint_id}: {e}")
            return False
    
    def get_waypoint(self, waypoint_id: str) -> Optional[Waypoint]:
        """Получение путевой точки по ID"""
        try:
            return self.waypoints.get(waypoint_id)
        except Exception as e:
            self._logger.error(f"Ошибка получения путевой точки {waypoint_id}: {e}")
            return None
    
    def get_waypoints_in_range(self, center_x: float, center_y: float, 
                              radius: float) -> List[Waypoint]:
        """Получение путевых точек в радиусе"""
        try:
            waypoints_in_range = []
            
            for waypoint in self.waypoints.values():
                if waypoint.visible:
                    distance = math.sqrt((waypoint.x - center_x) ** 2 + (waypoint.y - center_y) ** 2)
                    if distance <= radius:
                        waypoints_in_range.append(waypoint)
            
            return waypoints_in_range
            
        except Exception as e:
            self._logger.error(f"Ошибка получения путевых точек в радиусе: {e}")
            return []
    
    def calculate_distance_to_waypoint(self, waypoint_id: str) -> float:
        """Расчет расстояния до путевой точки"""
        try:
            if waypoint_id in self.waypoints:
                waypoint = self.waypoints[waypoint_id]
                distance = math.sqrt((waypoint.x - self.player_position[0]) ** 2 + 
                                   (waypoint.y - self.player_position[1]) ** 2)
                return distance
            
            return -1.0
            
        except Exception as e:
            self._logger.error(f"Ошибка расчета расстояния до путевой точки {waypoint_id}: {e}")
            return -1.0
    
    def get_direction_to_waypoint(self, waypoint_id: str) -> CompassDirection:
        """Получение направления к путевой точке"""
        try:
            if waypoint_id in self.waypoints:
                waypoint = self.waypoints[waypoint_id]
                
                # Вычисляем угол к путевой точке
                dx = waypoint.x - self.player_position[0]
                dy = waypoint.y - self.player_position[1]
                
                if dx == 0 and dy == 0:
                    return CompassDirection.NORTH
                
                angle = math.atan2(dy, dx)
                heading_degrees = math.degrees(angle)
                heading_degrees = (heading_degrees + 360) % 360
                
                return self._get_compass_direction(heading_degrees)
            
            return CompassDirection.NORTH
            
        except Exception as e:
            self._logger.error(f"Ошибка получения направления к путевой точке {waypoint_id}: {e}")
            return CompassDirection.NORTH
    
    def get_mini_map_data(self, size: int = None) -> Dict[str, Any]:
        """Получение данных мини-карты"""
        try:
            if size is None:
                size = self.settings.mini_map_size
            
            # Получаем путевые точки в радиусе видимости
            visible_waypoints = self.get_waypoints_in_range(
                self.player_position[0], 
                self.player_position[1], 
                size / 2
            )
            
            # Преобразуем координаты в относительные
            relative_waypoints = []
            for waypoint in visible_waypoints:
                relative_x = (waypoint.x - self.player_position[0]) / (size / 2) * (size / 2) + size / 2
                relative_y = (waypoint.y - self.player_position[1]) / (size / 2) * (size / 2) + size / 2
                
                relative_waypoints.append({
                    "id": waypoint.waypoint_id,
                    "type": waypoint.waypoint_type.value,
                    "x": relative_x,
                    "y": relative_y,
                    "name": waypoint.name,
                    "icon": waypoint.icon,
                    "color": waypoint.color
                })
            
            return {
                "size": size,
                "player_x": size / 2,
                "player_y": size / 2,
                "waypoints": relative_waypoints,
                "compass_direction": self.compass_data.direction.value,
                "gps_coordinates": {
                    "latitude": self.gps_data.latitude,
                    "longitude": self.gps_data.longitude,
                    "altitude": self.gps_data.altitude
                }
            }
            
        except Exception as e:
            self._logger.error(f"Ошибка получения данных мини-карты: {e}")
            return {}
    
    def get_world_map_data(self, scale: float = 1.0) -> Dict[str, Any]:
        """Получение данных карты мира"""
        try:
            # Получаем все видимые путевые точки
            visible_waypoints = [w for w in self.waypoints.values() if w.visible]
            
            # Преобразуем координаты в масштаб карты мира
            scaled_waypoints = []
            for waypoint in visible_waypoints:
                scaled_x = waypoint.x * scale
                scaled_y = waypoint.y * scale
                
                scaled_waypoints.append({
                    "id": waypoint.waypoint_id,
                    "type": waypoint.waypoint_type.value,
                    "x": scaled_x,
                    "y": scaled_y,
                    "name": waypoint.name,
                    "icon": waypoint.icon,
                    "color": waypoint.color
                })
            
            return {
                "size": self.settings.world_map_size,
                "scale": scale,
                "center_x": self.player_position[0] * scale,
                "center_y": self.player_position[1] * scale,
                "waypoints": scaled_waypoints
            }
            
        except Exception as e:
            self._logger.error(f"Ошибка получения данных карты мира: {e}")
            return {}
    
    def _get_waypoint_icon(self, waypoint_type: WaypointType) -> str:
        """Получение иконки для типа путевой точки"""
        try:
            icons = {
                WaypointType.PLAYER: "player_icon",
                WaypointType.QUEST: "quest_icon",
                WaypointType.TRADE: "trade_icon",
                WaypointType.DANGER: "danger_icon",
                WaypointType.RESOURCE: "resource_icon",
                WaypointType.SETTLEMENT: "settlement_icon",
                WaypointType.DUNGEON: "dungeon_icon",
                WaypointType.CUSTOM: "custom_icon"
            }
            
            return icons.get(waypoint_type, "default_icon")
            
        except Exception as e:
            self._logger.error(f"Ошибка получения иконки путевой точки: {e}")
            return "default_icon"
    
    def _get_waypoint_color(self, waypoint_type: WaypointType) -> str:
        """Получение цвета для типа путевой точки"""
        try:
            colors = {
                WaypointType.PLAYER: "#00FF00",      # Зеленый
                WaypointType.QUEST: "#FFFF00",       # Желтый
                WaypointType.TRADE: "#00FFFF",       # Голубой
                WaypointType.DANGER: "#FF0000",      # Красный
                WaypointType.RESOURCE: "#FFA500",    # Оранжевый
                WaypointType.SETTLEMENT: "#800080",  # Фиолетовый
                WaypointType.DUNGEON: "#800000",     # Темно-красный
                WaypointType.CUSTOM: "#FFFFFF"       # Белый
            }
            
            return colors.get(waypoint_type, "#FFFFFF")
            
        except Exception as e:
            self._logger.error(f"Ошибка получения цвета путевой точки: {e}")
            return "#FFFFFF"
    
    def get_gps_data(self) -> GPSData:
        """Получение GPS данных"""
        return self.gps_data
    
    def get_compass_data(self) -> CompassData:
        """Получение данных компаса"""
        return self.compass_data
    
    def get_navigation_stats(self) -> Dict[str, Any]:
        """Получение статистики навигации"""
        try:
            return {
                "total_waypoints": self.navigation_stats["total_waypoints"],
                "maps_created": self.navigation_stats["maps_created"],
                "gps_updates": self.navigation_stats["gps_updates"],
                "compass_updates": self.navigation_stats["compass_updates"],
                "player_position": self.player_position,
                "active_waypoints": len([w for w in self.waypoints.values() if w.visible])
            }
            
        except Exception as e:
            self._logger.error(f"Ошибка получения статистики навигации: {e}")
            return {}
    
    def clear_waypoints(self, waypoint_type: Optional[WaypointType] = None):
        """Очистка путевых точек"""
        try:
            if waypoint_type is None:
                # Очищаем все непостоянные точки
                waypoints_to_remove = [wid for wid, w in self.waypoints.items() 
                                     if not w.permanent]
            else:
                # Очищаем точки определенного типа
                waypoints_to_remove = [wid for wid, w in self.waypoints.items() 
                                     if w.waypoint_type == waypoint_type and not w.permanent]
            
            for waypoint_id in waypoints_to_remove:
                del self.waypoints[waypoint_id]
            
            self.navigation_stats["total_waypoints"] = len(self.waypoints)
            
            self._logger.info(f"Очищено {len(waypoints_to_remove)} путевых точек")
            
        except Exception as e:
            self._logger.error(f"Ошибка очистки путевых точек: {e}")
    
    def _on_destroy(self) -> bool:
        """Уничтожение системы навигации"""
        try:
            # Очищаем все данные
            self.maps.clear()
            self.waypoints.clear()
            
            # Сбрасываем статистику
            self.navigation_stats = {
                "total_waypoints": 0,
                "maps_created": 0,
                "gps_updates": 0,
                "compass_updates": 0
            }
            
            self._logger.info("Система навигации уничтожена")
            return True
            
        except Exception as e:
            self._logger.error(f"Ошибка уничтожения системы навигации: {e}")
            return False
