#!/usr/bin/env python3
"""Генератор поселений для процедурного мира
Создает деревни, города и другие поселения с зданиями и инфраструктурой"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Set
import logging
import random
import time
import math

from src.core.architecture import BaseComponent, ComponentType, Priority

# = ТИПЫ ПОСЕЛЕНИЙ
class SettlementType(Enum):
    """Типы поселений"""
    HAMLET = "hamlet"           # Хутор
    VILLAGE = "village"         # Деревня
    TOWN = "town"               # Городок
    CITY = "city"               # Город
    CAPITAL = "capital"         # Столица
    FORTRESS = "fortress"       # Крепость
    TRADING_POST = "trading_post"  # Торговый пост
    MONASTERY = "monastery"     # Монастырь

class BuildingType(Enum):
    """Типы зданий"""
    HOUSE = "house"             # Жилой дом
    SHOP = "shop"               # Магазин
    BLACKSMITH = "blacksmith"   # Кузница
    TAVERN = "tavern"           # Таверна
    TEMPLE = "temple"           # Храм
    TOWN_HALL = "town_hall"     # Ратуша
    WAREHOUSE = "warehouse"     # Склад
    STABLE = "stable"           # Конюшня
    FARM = "farm"               # Ферма
    MINE = "mine"               # Шахта
    LIBRARY = "library"         # Библиотека
    ACADEMY = "academy"         # Академия
    BARRACKS = "barracks"       # Казармы
    WALL = "wall"               # Стена
    TOWER = "tower"             # Башня
    GATE = "gate"               # Ворота

class RoadType(Enum):
    """Типы дорог"""
    DIRT = "dirt"               # Грунтовая
    COBBLESTONE = "cobblestone" # Булыжная
    PAVED = "paved"             # Мощеная
    BRIDGE = "bridge"           # Мост

# = ДАТАКЛАССЫ
@dataclass
class SettlementSettings:
    """Настройки генерации поселения"""
    settlement_type: SettlementType = SettlementType.VILLAGE
    width: int = 100
    height: int = 100
    population: int = 100
    wealth_level: float = 0.5  # 0.0 - бедное, 1.0 - богатое
    defense_level: float = 0.3  # 0.0 - незащищенное, 1.0 - укрепленное
    trade_level: float = 0.4   # 0.0 - изолированное, 1.0 - торговый центр

@dataclass
class Building:
    """Здание поселения"""
    building_id: str
    building_type: BuildingType
    x: int
    y: int
    width: int
    height: int
    level: int = 1
    condition: float = 1.0  # 0.0 - разрушено, 1.0 - отличное
    owner: str = ""
    residents: List[str] = field(default_factory=list)
    inventory: List[str] = field(default_factory=list)
    special_features: List[str] = field(default_factory=list)
    construction_time: float = field(default_factory=time.time)

@dataclass
class Road:
    """Дорога в поселении"""
    road_id: str
    road_type: RoadType
    start_point: Tuple[int, int]
    end_point: Tuple[int, int]
    path: List[Tuple[int, int]] = field(default_factory=list)
    width: int = 3
    condition: float = 1.0

@dataclass
class GeneratedSettlement:
    """Сгенерированное поселение"""
    settlement_id: str
    settlement_type: SettlementType
    settings: SettlementSettings
    buildings: Dict[str, Building] = field(default_factory=dict)
    roads: Dict[str, Road] = field(default_factory=dict)
    grid: List[List[int]] = field(default_factory=list)
    center: Tuple[int, int] = (0, 0)
    walls: List[Tuple[int, int]] = field(default_factory=list)
    gates: List[Tuple[int, int]] = field(default_factory=list)
    population: int = 0
    wealth: float = 0.0
    defense: float = 0.0
    trade: float = 0.0
    generation_time: float = field(default_factory=time.time)

# = ОСНОВНАЯ СИСТЕМА ГЕНЕРАЦИИ ПОСЕЛЕНИЙ
class SettlementGenerator(BaseComponent):
    """Генератор поселений для процедурного мира"""
    
    def __init__(self):
        super().__init__(
            component_id="SettlementGenerator",
            component_type=ComponentType.SYSTEM,
            priority=Priority.HIGH
        )
        
        # Настройки генерации
        self.default_settings = SettlementSettings()
        
        # Шаблоны зданий для разных типов поселений
        self.building_templates: Dict[SettlementType, Dict[BuildingType, Dict[str, Any]]] = {}
        
        # Кэш сгенерированных поселений
        self.settlement_cache: Dict[str, GeneratedSettlement] = {}
        
        # Статистика генерации
        self.generation_stats = {
            "total_settlements": 0,
            "total_buildings": 0,
            "total_roads": 0,
            "generation_time": 0.0
        }
        
        # Инициализация шаблонов
        self._initialize_building_templates()
    
    def _on_initialize(self) -> bool:
        """Инициализация генератора поселений"""
        try:
            self._logger.info("Генератор поселений инициализирован")
            return True
        except Exception as e:
            self._logger.error(f"Ошибка инициализации генератора поселений: {e}")
            return False
    
    def _initialize_building_templates(self):
        """Инициализация шаблонов зданий"""
        try:
            # Хутор
            self.building_templates[SettlementType.HAMLET] = {
                BuildingType.HOUSE: {"size_range": (3, 5), "count_range": (2, 4), "level_range": (1, 2)},
                BuildingType.FARM: {"size_range": (4, 6), "count_range": (1, 2), "level_range": (1, 2)},
                BuildingType.STABLE: {"size_range": (3, 4), "count_range": (1, 1), "level_range": (1, 1)}
            }
            
            # Деревня
            self.building_templates[SettlementType.VILLAGE] = {
                BuildingType.HOUSE: {"size_range": (3, 6), "count_range": (5, 12), "level_range": (1, 3)},
                BuildingType.SHOP: {"size_range": (3, 4), "count_range": (1, 2), "level_range": (1, 2)},
                BuildingType.TAVERN: {"size_range": (4, 5), "count_range": (1, 1), "level_range": (1, 2)},
                BuildingType.TEMPLE: {"size_range": (4, 6), "count_range": (1, 1), "level_range": (1, 2)},
                BuildingType.FARM: {"size_range": (4, 7), "count_range": (2, 4), "level_range": (1, 2)}
            }
            
            # Городок
            self.building_templates[SettlementType.TOWN] = {
                BuildingType.HOUSE: {"size_range": (4, 7), "count_range": (15, 30), "level_range": (1, 4)},
                BuildingType.SHOP: {"size_range": (3, 5), "count_range": (3, 6), "level_range": (1, 3)},
                BuildingType.BLACKSMITH: {"size_range": (4, 5), "count_range": (1, 2), "level_range": (1, 3)},
                BuildingType.TAVERN: {"size_range": (4, 6), "count_range": (2, 3), "level_range": (1, 3)},
                BuildingType.TEMPLE: {"size_range": (5, 7), "count_range": (1, 2), "level_range": (2, 3)},
                BuildingType.TOWN_HALL: {"size_range": (5, 7), "count_range": (1, 1), "level_range": (2, 3)},
                BuildingType.WAREHOUSE: {"size_range": (4, 6), "count_range": (1, 2), "level_range": (1, 2)},
                BuildingType.STABLE: {"size_range": (3, 5), "count_range": (1, 2), "level_range": (1, 2)}
            }
            
            # Город
            self.building_templates[SettlementType.CITY] = {
                BuildingType.HOUSE: {"size_range": (4, 8), "count_range": (40, 80), "level_range": (1, 5)},
                BuildingType.SHOP: {"size_range": (3, 6), "count_range": (8, 15), "level_range": (1, 4)},
                BuildingType.BLACKSMITH: {"size_range": (4, 6), "count_range": (3, 6), "level_range": (1, 4)},
                BuildingType.TAVERN: {"size_range": (4, 7), "count_range": (5, 10), "level_range": (1, 4)},
                BuildingType.TEMPLE: {"size_range": (6, 9), "count_range": (2, 4), "level_range": (2, 4)},
                BuildingType.TOWN_HALL: {"size_range": (6, 8), "count_range": (1, 1), "level_range": (3, 4)},
                BuildingType.WAREHOUSE: {"size_range": (5, 7), "count_range": (3, 6), "level_range": (1, 3)},
                BuildingType.STABLE: {"size_range": (4, 6), "count_range": (2, 4), "level_range": (1, 3)},
                BuildingType.LIBRARY: {"size_range": (4, 6), "count_range": (1, 2), "level_range": (2, 3)},
                BuildingType.ACADEMY: {"size_range": (5, 7), "count_range": (1, 1), "level_range": (2, 3)},
                BuildingType.BARRACKS: {"size_range": (5, 7), "count_range": (1, 2), "level_range": (2, 3)}
            }
            
            # Столица
            self.building_templates[SettlementType.CAPITAL] = {
                BuildingType.HOUSE: {"size_range": (5, 10), "count_range": (80, 150), "level_range": (2, 6)},
                BuildingType.SHOP: {"size_range": (4, 7), "count_range": (15, 25), "level_range": (2, 5)},
                BuildingType.BLACKSMITH: {"size_range": (5, 7), "count_range": (6, 10), "level_range": (2, 5)},
                BuildingType.TAVERN: {"size_range": (5, 8), "count_range": (10, 20), "level_range": (2, 5)},
                BuildingType.TEMPLE: {"size_range": (7, 12), "count_range": (3, 6), "level_range": (3, 5)},
                BuildingType.TOWN_HALL: {"size_range": (8, 12), "count_range": (1, 1), "level_range": (4, 5)},
                BuildingType.WAREHOUSE: {"size_range": (6, 8), "count_range": (5, 10), "level_range": (2, 4)},
                BuildingType.STABLE: {"size_range": (5, 7), "count_range": (3, 6), "level_range": (2, 4)},
                BuildingType.LIBRARY: {"size_range": (5, 7), "count_range": (2, 3), "level_range": (3, 4)},
                BuildingType.ACADEMY: {"size_range": (6, 8), "count_range": (1, 2), "level_range": (3, 4)},
                BuildingType.BARRACKS: {"size_range": (6, 8), "count_range": (2, 3), "level_range": (3, 4)}
            }
            
            self._logger.info(f"Инициализировано {len(self.building_templates)} шаблонов поселений")
            
        except Exception as e:
            self._logger.error(f"Ошибка инициализации шаблонов зданий: {e}")
    
    def generate_settlement(self, settlement_type: SettlementType, 
                           settings: Optional[SettlementSettings] = None) -> GeneratedSettlement:
        """Генерация поселения"""
        try:
            start_time = time.time()
            
            # Используем переданные настройки или создаем новые
            if settings is None:
                settings = SettlementSettings(settlement_type=settlement_type)
            
            # Создаем уникальный ID для поселения
            settlement_id = f"{settlement_type.value}_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
            
            # Создаем поселение
            settlement = GeneratedSettlement(
                settlement_id=settlement_id,
                settlement_type=settlement_type,
                settings=settings
            )
            
            # Генерируем сетку
            settlement.grid = self._create_empty_grid(settings.width, settings.height)
            
            # Определяем центр поселения
            settlement.center = (settings.width // 2, settings.height // 2)
            
            # Генерируем здания
            self._generate_buildings(settlement)
            
            # Создаем дороги
            self._create_roads(settlement)
            
            # Создаем защитные сооружения
            if settings.defense_level > 0.3:
                self._create_defenses(settlement)
            
            # Размещаем жителей
            self._place_residents(settlement)
            
            # Рассчитываем статистику
            self._calculate_statistics(settlement)
            
            # Обновляем статистику
            generation_time = time.time() - start_time
            settlement.generation_time = generation_time
            self.generation_stats["generation_time"] += generation_time
            self.generation_stats["total_settlements"] += 1
            self.generation_stats["total_buildings"] += len(settlement.buildings)
            self.generation_stats["total_roads"] += len(settlement.roads)
            
            # Кэшируем результат
            self.settlement_cache[settlement_id] = settlement
            
            self._logger.info(f"Поселение {settlement_type.value} сгенерировано за {generation_time:.3f}с")
            
            return settlement
            
        except Exception as e:
            self._logger.error(f"Ошибка генерации поселения {settlement_type.value}: {e}")
            return None
    
    def _create_empty_grid(self, width: int, height: int) -> List[List[int]]:
        """Создание пустой сетки поселения"""
        try:
            return [[0 for _ in range(width)] for _ in range(height)]
        except Exception as e:
            self._logger.error(f"Ошибка создания сетки: {e}")
            return []
    
    def _generate_buildings(self, settlement: GeneratedSettlement):
        """Генерация зданий поселения"""
        try:
            templates = self.building_templates.get(settlement.settlement_type, {})
            
            for building_type, template in templates.items():
                count_range = template.get("count_range", (1, 3))
                count = random.randint(count_range[0], count_range[1])
                
                for i in range(count):
                    building = self._create_building(settlement, building_type, template, i)
                    if building:
                        settlement.buildings[building.building_id] = building
                        self._place_building_on_grid(settlement, building)
            
        except Exception as e:
            self._logger.error(f"Ошибка генерации зданий: {e}")
    
    def _create_building(self, settlement: GeneratedSettlement, building_type: BuildingType, 
                         template: Dict[str, Any], index: int) -> Optional[Building]:
        """Создание отдельного здания"""
        try:
            settings = settlement.settings
            
            # Получаем параметры здания
            size_range = template.get("size_range", (3, 5))
            level_range = template.get("level_range", (1, 2))
            
            # Определяем размер здания
            width = random.randint(size_range[0], size_range[1])
            height = random.randint(size_range[0], size_range[1])
            
            # Определяем уровень здания
            level = random.randint(level_range[0], level_range[1])
            
            # Определяем позицию здания
            max_x = settings.width - width
            max_y = settings.height - height
            
            if max_x <= 0 or max_y <= 0:
                return None
            
            # Пытаемся разместить здание
            for attempt in range(100):
                x = random.randint(0, max_x)
                y = random.randint(0, max_y)
                
                if self._can_place_building(settlement, x, y, width, height):
                    # Создаем здание
                    building = Building(
                        building_id=f"building_{building_type.value}_{index}_{int(time.time() * 1000)}",
                        building_type=building_type,
                        x=x,
                        y=y,
                        width=width,
                        height=height,
                        level=level,
                        condition=random.uniform(0.7, 1.0)
                    )
                    
                    return building
            
            return None
            
        except Exception as e:
            self._logger.error(f"Ошибка создания здания {building_type.value}: {e}")
            return None
    
    def _can_place_building(self, settlement: GeneratedSettlement, x: int, y: int, 
                            width: int, height: int) -> bool:
        """Проверка возможности размещения здания"""
        try:
            # Проверяем границы
            if x < 0 or y < 0 or x + width > len(settlement.grid[0]) or y + height > len(settlement.grid):
                return False
            
            # Проверяем, что место свободно
            for dy in range(y, y + height):
                for dx in range(x, x + width):
                    if settlement.grid[dy][dx] != 0:
                        return False
            
            return True
            
        except Exception as e:
            self._logger.error(f"Ошибка проверки размещения здания: {e}")
            return False
    
    def _place_building_on_grid(self, settlement: GeneratedSettlement, building: Building):
        """Размещение здания на сетке"""
        try:
            for y in range(building.y, building.y + building.height):
                for x in range(building.x, building.x + building.width):
                    settlement.grid[y][x] = 1  # 1 = здание
            
        except Exception as e:
            self._logger.error(f"Ошибка размещения здания на сетке: {e}")
    
    def _create_roads(self, settlement: GeneratedSettlement):
        """Создание дорог в поселении"""
        try:
            buildings = list(settlement.buildings.values())
            
            # Создаем главную дорогу через центр
            main_road = self._create_main_road(settlement)
            if main_road:
                settlement.roads[main_road.road_id] = main_road
                self._place_road_on_grid(settlement, main_road)
            
            # Создаем дороги между важными зданиями
            important_buildings = [b for b in buildings if b.building_type in 
                                 [BuildingType.TOWN_HALL, BuildingType.TEMPLE, BuildingType.TAVERN]]
            
            for i in range(len(important_buildings) - 1):
                road = self._create_road_between_buildings(settlement, 
                                                         important_buildings[i], 
                                                         important_buildings[i + 1])
                if road:
                    settlement.roads[road.road_id] = road
                    self._place_road_on_grid(settlement, road)
            
            # Создаем случайные дороги к домам
            houses = [b for b in buildings if b.building_type == BuildingType.HOUSE]
            for house in houses[:len(houses) // 3]:  # Подключаем треть домов
                road = self._create_road_to_building(settlement, house)
                if road:
                    settlement.roads[road.road_id] = road
                    self._place_road_on_grid(settlement, road)
            
        except Exception as e:
            self._logger.error(f"Ошибка создания дорог: {e}")
    
    def _create_main_road(self, settlement: GeneratedSettlement) -> Optional[Road]:
        """Создание главной дороги"""
        try:
            center_x, center_y = settlement.center
            
            # Создаем дорогу с севера на юг
            start_point = (center_x, 0)
            end_point = (center_x, settlement.settings.height - 1)
            
            path = self._create_road_path(start_point, end_point)
            
            road = Road(
                road_id=f"main_road_{int(time.time() * 1000)}",
                road_type=RoadType.PAVED if settlement.settings.wealth_level > 0.5 else RoadType.COBBLESTONE,
                start_point=start_point,
                end_point=end_point,
                path=path,
                width=5
            )
            
            return road
            
        except Exception as e:
            self._logger.error(f"Ошибка создания главной дороги: {e}")
            return None
    
    def _create_road_between_buildings(self, settlement: GeneratedSettlement, 
                                      building1: Building, building2: Building) -> Optional[Road]:
        """Создание дороги между двумя зданиями"""
        try:
            # Определяем центры зданий
            center1 = (building1.x + building1.width // 2, building1.y + building1.height // 2)
            center2 = (building2.x + building2.width // 2, building2.y + building2.height // 2)
            
            path = self._create_road_path(center1, center2)
            
            road = Road(
                road_id=f"road_{building1.building_id}_{building2.building_id}_{int(time.time() * 1000)}",
                road_type=RoadType.COBBLESTONE if settlement.settings.wealth_level > 0.3 else RoadType.DIRT,
                start_point=center1,
                end_point=center2,
                path=path,
                width=3
            )
            
            return road
            
        except Exception as e:
            self._logger.error(f"Ошибка создания дороги между зданиями: {e}")
            return None
    
    def _create_road_to_building(self, settlement: GeneratedSettlement, 
                                building: Building) -> Optional[Road]:
        """Создание дороги к зданию"""
        try:
            # Определяем центр здания
            building_center = (building.x + building.width // 2, building.y + building.height // 2)
            
            # Находим ближайшую существующую дорогу
            nearest_road_point = self._find_nearest_road_point(settlement, building_center)
            
            if nearest_road_point:
                path = self._create_road_path(building_center, nearest_road_point)
                
                road = Road(
                    road_id=f"road_to_{building.building_id}_{int(time.time() * 1000)}",
                    road_type=RoadType.DIRT,
                    start_point=building_center,
                    end_point=nearest_road_point,
                    path=path,
                    width=2
                )
                
                return road
            
            return None
            
        except Exception as e:
            self._logger.error(f"Ошибка создания дороги к зданию: {e}")
            return None
    
    def _create_road_path(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Создание пути дороги"""
        try:
            path = []
            current = start
            
            # Простой алгоритм: сначала по X, потом по Y
            while current[0] != end[0]:
                next_x = current[0] + (1 if current[0] < end[0] else -1)
                current = (next_x, current[1])
                path.append(current)
            
            while current[1] != end[1]:
                next_y = current[1] + (1 if current[1] < end[1] else -1)
                current = (current[0], next_y)
                path.append(current)
            
            return path
            
        except Exception as e:
            self._logger.error(f"Ошибка создания пути дороги: {e}")
            return []
    
    def _find_nearest_road_point(self, settlement: GeneratedSettlement, 
                                 point: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Поиск ближайшей точки на дороге"""
        try:
            nearest_point = None
            min_distance = float('inf')
            
            for road in settlement.roads.values():
                for road_point in road.path:
                    distance = math.sqrt((point[0] - road_point[0]) ** 2 + 
                                       (point[1] - road_point[1]) ** 2)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_point = road_point
            
            return nearest_point
            
        except Exception as e:
            self._logger.error(f"Ошибка поиска ближайшей точки дороги: {e}")
            return None
    
    def _place_road_on_grid(self, settlement: GeneratedSettlement, road: Road):
        """Размещение дороги на сетке"""
        try:
            for x, y in road.path:
                # Размещаем дорогу с учетом ширины
                for dy in range(y - road.width // 2, y + road.width // 2 + 1):
                    for dx in range(x - road.width // 2, x + road.width // 2 + 1):
                        if (0 <= dy < len(settlement.grid) and 
                            0 <= dx < len(settlement.grid[0])):
                            settlement.grid[dy][dx] = 2  # 2 = дорога
            
        except Exception as e:
            self._logger.error(f"Ошибка размещения дороги на сетке: {e}")
    
    def _create_defenses(self, settlement: GeneratedSettlement):
        """Создание защитных сооружений"""
        try:
            settings = settlement.settings
            
            if settings.defense_level > 0.7:
                # Создаем стены вокруг поселения
                self._create_walls(settlement)
                
                # Создаем башни
                self._create_towers(settlement)
                
                # Создаем ворота
                self._create_gates(settlement)
            
        except Exception as e:
            self._logger.error(f"Ошибка создания защитных сооружений: {e}")
    
    def _create_walls(self, settlement: GeneratedSettlement):
        """Создание стен"""
        try:
            # Простая прямоугольная стена
            margin = 5
            for x in range(margin, settlement.settings.width - margin):
                # Северная стена
                settlement.walls.append((x, margin))
                settlement.grid[margin][x] = 3  # 3 = стена
                
                # Южная стена
                settlement.walls.append((x, settlement.settings.height - margin - 1))
                settlement.grid[settlement.settings.height - margin - 1][x] = 3
            
            for y in range(margin, settlement.settings.height - margin):
                # Западная стена
                settlement.walls.append((margin, y))
                settlement.grid[y][margin] = 3
                
                # Восточная стена
                settlement.walls.append((settlement.settings.width - margin - 1, y))
                settlement.grid[y][settlement.settings.width - margin - 1] = 3
            
        except Exception as e:
            self._logger.error(f"Ошибка создания стен: {e}")
    
    def _create_towers(self, settlement: GeneratedSettlement):
        """Создание башен"""
        try:
            # Создаем башни по углам
            margin = 5
            corners = [
                (margin, margin),
                (settlement.settings.width - margin - 1, margin),
                (margin, settlement.settings.height - margin - 1),
                (settlement.settings.width - margin - 1, settlement.settings.height - margin - 1)
            ]
            
            for i, (x, y) in enumerate(corners):
                tower = Building(
                    building_id=f"tower_{i}_{int(time.time() * 1000)}",
                    building_type=BuildingType.TOWER,
                    x=x-1, y=y-1, width=3, height=3,
                    level=3, condition=1.0
                )
                settlement.buildings[tower.building_id] = tower
                self._place_building_on_grid(settlement, tower)
            
        except Exception as e:
            self._logger.error(f"Ошибка создания башен: {e}")
    
    def _create_gates(self, settlement: GeneratedSettlement):
        """Создание ворот"""
        try:
            # Создаем ворота на главных дорогах
            center_x, center_y = settlement.center
            
            # Северные ворота
            settlement.gates.append((center_x, 5))
            settlement.grid[5][center_x] = 4  # 4 = ворота
            
            # Южные ворота
            settlement.gates.append((center_x, settlement.settings.height - 6))
            settlement.grid[settlement.settings.height - 6][center_x] = 4
            
        except Exception as e:
            self._logger.error(f"Ошибка создания ворот: {e}")
    
    def _place_residents(self, settlement: GeneratedSettlement):
        """Размещение жителей в поселении"""
        try:
            houses = [b for b in settlement.buildings.values() 
                     if b.building_type == BuildingType.HOUSE]
            
            # Распределяем жителей по домам
            residents_per_house = settlement.settings.population // max(len(houses), 1)
            
            for house in houses:
                for i in range(residents_per_house):
                    resident_id = f"resident_{house.building_id}_{i}_{int(time.time() * 1000)}"
                    house.residents.append(resident_id)
            
        except Exception as e:
            self._logger.error(f"Ошибка размещения жителей: {e}")
    
    def _calculate_statistics(self, settlement: GeneratedSettlement):
        """Расчет статистики поселения"""
        try:
            # Рассчитываем население
            settlement.population = sum(len(building.residents) 
                                      for building in settlement.buildings.values())
            
            # Рассчитываем богатство на основе зданий и их уровней
            total_wealth = sum(building.level * building.condition 
                             for building in settlement.buildings.values())
            settlement.wealth = total_wealth / max(len(settlement.buildings), 1)
            
            # Рассчитываем защищенность
            defense_buildings = [b for b in settlement.buildings.values() 
                               if b.building_type in [BuildingType.TOWER, BuildingType.BARRACKS]]
            settlement.defense = len(defense_buildings) / max(len(settlement.buildings), 1)
            
            # Рассчитываем торговую активность
            trade_buildings = [b for b in settlement.buildings.values() 
                             if b.building_type in [BuildingType.SHOP, BuildingType.WAREHOUSE, BuildingType.TAVERN]]
            settlement.trade = len(trade_buildings) / max(len(settlement.buildings), 1)
            
        except Exception as e:
            self._logger.error(f"Ошибка расчета статистики: {e}")
    
    def get_settlement(self, settlement_id: str) -> Optional[GeneratedSettlement]:
        """Получение поселения по ID"""
        try:
            return self.settlement_cache.get(settlement_id)
        except Exception as e:
            self._logger.error(f"Ошибка получения поселения {settlement_id}: {e}")
            return None
    
    def get_settlement_stats(self) -> Dict[str, Any]:
        """Получение статистики генерации"""
        try:
            return {
                "total_settlements": self.generation_stats["total_settlements"],
                "total_buildings": self.generation_stats["total_buildings"],
                "total_roads": self.generation_stats["total_roads"],
                "generation_time": self.generation_stats["generation_time"],
                "cache_size": len(self.settlement_cache),
                "average_time_per_settlement": (self.generation_stats["generation_time"] / 
                                              max(self.generation_stats["total_settlements"], 1))
            }
            
        except Exception as e:
            self._logger.error(f"Ошибка получения статистики: {e}")
            return {}
    
    def clear_cache(self) -> None:
        """Очистка кэша"""
        try:
            self.settlement_cache.clear()
            self._logger.info("Кэш генератора поселений очищен")
            
        except Exception as e:
            self._logger.error(f"Ошибка очистки кэша: {e}")
    
    def _on_destroy(self) -> bool:
        """Уничтожение генератора поселений"""
        try:
            # Очищаем кэш
            self.clear_cache()
            
            # Сбрасываем статистику
            self.generation_stats = {
                "total_settlements": 0,
                "total_buildings": 0,
                "total_roads": 0,
                "generation_time": 0.0
            }
            
            self._logger.info("Генератор поселений уничтожен")
            return True
            
        except Exception as e:
            self._logger.error(f"Ошибка уничтожения генератора поселений: {e}")
            return False
