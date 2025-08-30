#!/usr/bin/env python3
"""
Типы локаций и структуры
Система локаций для игрового мира
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import math

class LocationType(Enum):
    """Типы локаций"""
    # Природные локации
    FOREST = "forest"                          # Лес
    MOUNTAIN = "mountain"                      # Гора
    CAVE = "cave"                              # Пещера
    RIVER = "river"                            # Река
    LAKE = "lake"                              # Озеро
    BEACH = "beach"                            # Пляж
    DESERT = "desert"                          # Пустыня
    
    # Искусственные локации
    VILLAGE = "village"                        # Деревня
    TOWN = "town"                              # Город
    CASTLE = "castle"                          # Замок
    TOWER = "tower"                            # Башня
    DUNGEON = "dungeon"                        # Подземелье
    RUINS = "ruins"                            # Руины
    TEMPLE = "temple"                          # Храм
    
    # Торговые локации
    MARKET = "market"                          # Рынок
    SHOP = "shop"                              # Магазин
    INN = "inn"                                # Таверна
    BLACKSMITH = "blacksmith"                  # Кузница
    ALCHEMIST = "alchemist"                    # Алхимик
    BANK = "bank"                              # Банк
    
    # Специальные локации
    PORTAL = "portal"                          # Порталы
    ALTAR = "altar"                            # Алтари
    CRYSTAL = "crystal"                        # Кристаллы
    SPRING = "spring"                          # Источники

class DungeonType(Enum):
    """Типы подземелий"""
    CAVE = "cave"                              # Пещера
    CRYPT = "crypt"                            # Склеп
    MINE = "mine"                              # Шахта
    SEWER = "sewer"                            # Канализация
    LABORATORY = "laboratory"                  # Лаборатория
    PRISON = "prison"                          # Тюрьма
    TEMPLE = "temple"                          # Храм
    FORTRESS = "fortress"                      # Крепость

class SettlementType(Enum):
    """Типы поселений"""
    HAMLET = "hamlet"                          # Хутор
    VILLAGE = "village"                        # Деревня
    TOWN = "town"                              # Город
    CITY = "city"                              # Большой город
    CAPITAL = "capital"                        # Столица
    FORTRESS = "fortress"                      # Крепость
    MONASTERY = "monastery"                    # Монастырь

class BuildingType(Enum):
    """Типы зданий"""
    # Жилые здания
    HOUSE = "house"                            # Дом
    COTTAGE = "cottage"                        # Коттедж
    MANSION = "mansion"                        # Особняк
    PALACE = "palace"                          # Дворец
    
    # Торговые здания
    SHOP = "shop"                              # Магазин
    MARKET_STALL = "market_stall"              # Рыночный прилавок
    WAREHOUSE = "warehouse"                    # Склад
    BANK = "bank"                              # Банк
    
    # Производственные здания
    BLACKSMITH = "blacksmith"                  # Кузница
    WORKSHOP = "workshop"                      # Мастерская
    FACTORY = "factory"                        # Фабрика
    MILL = "mill"                              # Мельница
    
    # Общественные здания
    TOWN_HALL = "town_hall"                    # Ратуша
    LIBRARY = "library"                        # Библиотека
    SCHOOL = "school"                          # Школа
    HOSPITAL = "hospital"                      # Больница
    
    # Развлекательные здания
    INN = "inn"                                # Таверна
    THEATER = "theater"                        # Театр
    ARENA = "arena"                            # Арена
    CASINO = "casino"                          # Казино

class PointOfInterestType(Enum):
    """Типы точек интереса"""
    # Источники ресурсов
    MINERAL_DEPOSIT = "mineral_deposit"        # Месторождение минералов
    HERB_PATCH = "herb_patch"                  # Поляна трав
    WATER_SOURCE = "water_source"              # Источник воды
    FISHING_SPOT = "fishing_spot"              # Рыбное место
    
    # Места силы
    MAGIC_NODE = "magic_node"                  # Магический узел
    LEY_LINE = "ley_line"                      # Лей-линия
    POWER_WELL = "power_well"                  # Источник силы
    ELEMENTAL_FOCUS = "elemental_focus"        # Элементальный фокус
    
    # Скрытые локации
    SECRET_CAVE = "secret_cave"                # Секретная пещера
    HIDDEN_PASSAGE = "hidden_passage"          # Скрытый проход
    UNDERGROUND_CHAMBER = "underground_chamber" # Подземная камера
    ANCIENT_VAULT = "ancient_vault"            # Древнее хранилище

@dataclass
class Location:
    """Базовая локация"""
    location_id: str
    name: str
    description: str
    location_type: LocationType
    x: float
    y: float
    z: float
    width: float
    height: float
    depth: float
    
    # Свойства локации
    is_discovered: bool = False
    is_accessible: bool = True
    danger_level: float = 0.0
    resource_richness: float = 0.0
    travel_difficulty: float = 0.0
    
    # Визуальные свойства
    model_path: Optional[str] = None
    texture_path: Optional[str] = None
    particle_effects: List[str] = field(default_factory=list)
    
    # Аудио свойства
    ambient_sounds: List[str] = field(default_factory=list)
    music_track: Optional[str] = None
    
    # Игровые свойства
    required_level: int = 0
    required_items: List[str] = field(default_factory=list)
    required_skills: List[str] = field(default_factory=list)
    
    # Метаданные
    created_by: str = "system"
    creation_time: float = field(default_factory=time.time)
    last_visited: Optional[float] = None
    visit_count: int = 0
    
    # Panda3D узел
    node: Any = None

@dataclass
class Dungeon:
    """Подземелье"""
    dungeon_id: str
    name: str
    description: str
    dungeon_type: DungeonType
    location: Location
    
    # Свойства подземелья
    difficulty_level: int = 1
    min_level: int = 1
    max_level: int = 100
    room_count: int = 10
    floor_count: int = 1
    
    # Содержимое
    enemies: List[str] = field(default_factory=list)
    bosses: List[str] = field(default_factory=list)
    treasures: List[str] = field(default_factory=list)
    traps: List[str] = field(default_factory=list)
    
    # Прохождение
    is_completed: bool = False
    completion_time: Optional[float] = None
    best_time: Optional[float] = None
    attempts_count: int = 0
    
    # Награды
    experience_reward: int = 0
    gold_reward: int = 0
    item_rewards: List[str] = field(default_factory=list)
    skill_rewards: List[str] = field(default_factory=list)

@dataclass
class Settlement:
    """Поселение"""
    settlement_id: str
    name: str
    description: str
    settlement_type: SettlementType
    location: Location
    
    # Свойства поселения
    population: int = 100
    prosperity_level: float = 0.5
    security_level: float = 0.5
    culture_level: float = 0.5
    
    # Здания
    buildings: List[str] = field(default_factory=list)
    services: List[str] = field(default_factory=list)
    defenses: List[str] = field(default_factory=list)
    
    # Экономика
    trade_goods: List[str] = field(default_factory=list)
    prices_modifier: float = 1.0
    tax_rate: float = 0.1
    
    # Отношения
    reputation: float = 0.0
    quests_available: List[str] = field(default_factory=list)
    npcs: List[str] = field(default_factory=list)

@dataclass
class Building:
    """Здание"""
    building_id: str
    name: str
    description: str
    building_type: BuildingType
    location: Location
    
    # Свойства здания
    floor_count: int = 1
    room_count: int = 1
    is_public: bool = False
    is_restricted: bool = False
    
    # Функциональность
    services: List[str] = field(default_factory=list)
    npcs: List[str] = field(default_factory=list)
    items: List[str] = field(default_factory=list)
    
    # Состояние
    condition: float = 1.0
    is_operational: bool = True
    maintenance_cost: int = 0
    
    # Время работы
    open_time: int = 6  # 6:00
    close_time: int = 22  # 22:00
    is_always_open: bool = False

@dataclass
class PointOfInterest:
    """Точка интереса"""
    poi_id: str
    name: str
    description: str
    poi_type: PointOfInterestType
    location: Location
    
    # Свойства точки интереса
    rarity: float = 0.5
    respawn_time: Optional[float] = None
    last_respawn: Optional[float] = None
    
    # Ресурсы
    resources: List[str] = field(default_factory=list)
    resource_quantity: int = 1
    resource_quality: float = 1.0
    
    # Требования
    required_tools: List[str] = field(default_factory=list)
    required_skills: List[str] = field(default_factory=list)
    required_level: int = 0
    
    # Эффекты
    buffs: List[str] = field(default_factory=list)
    debuffs: List[str] = field(default_factory=list)
    special_effects: List[str] = field(default_factory=list)

class LocationManager:
    """Менеджер локаций"""
    
    def __init__(self):
        self.locations: Dict[str, Location] = {}
        self.dungeons: Dict[str, Dungeon] = {}
        self.settlements: Dict[str, Settlement] = {}
        self.buildings: Dict[str, Building] = {}
        self.points_of_interest: Dict[str, PointOfInterest] = {}
        
        # Статистика
        self.stats = {
            'total_locations': 0,
            'discovered_locations': 0,
            'total_dungeons': 0,
            'completed_dungeons': 0,
            'total_settlements': 0,
            'total_buildings': 0,
            'total_pois': 0
        }
    
    def add_location(self, location: Location) -> bool:
        """Добавление локации"""
        try:
            self.locations[location.location_id] = location
            self.stats['total_locations'] += 1
            return True
        except Exception as e:
            print(f"Ошибка добавления локации: {e}")
            return False
    
    def add_dungeon(self, dungeon: Dungeon) -> bool:
        """Добавление подземелья"""
        try:
            self.dungeons[dungeon.dungeon_id] = dungeon
            self.add_location(dungeon.location)
            self.stats['total_dungeons'] += 1
            return True
        except Exception as e:
            print(f"Ошибка добавления подземелья: {e}")
            return False
    
    def add_settlement(self, settlement: Settlement) -> bool:
        """Добавление поселения"""
        try:
            self.settlements[settlement.settlement_id] = settlement
            self.add_location(settlement.location)
            self.stats['total_settlements'] += 1
            return True
        except Exception as e:
            print(f"Ошибка добавления поселения: {e}")
            return False
    
    def add_building(self, building: Building) -> bool:
        """Добавление здания"""
        try:
            self.buildings[building.building_id] = building
            self.add_location(building.location)
            self.stats['total_buildings'] += 1
            return True
        except Exception as e:
            print(f"Ошибка добавления здания: {e}")
            return False
    
    def add_point_of_interest(self, poi: PointOfInterest) -> bool:
        """Добавление точки интереса"""
        try:
            self.points_of_interest[poi.poi_id] = poi
            self.add_location(poi.location)
            self.stats['total_pois'] += 1
            return True
        except Exception as e:
            print(f"Ошибка добавления точки интереса: {e}")
            return False
    
    def get_location(self, location_id: str) -> Optional[Location]:
        """Получение локации по ID"""
        return self.locations.get(location_id)
    
    def get_dungeon(self, dungeon_id: str) -> Optional[Dungeon]:
        """Получение подземелья по ID"""
        return self.dungeons.get(dungeon_id)
    
    def get_settlement(self, settlement_id: str) -> Optional[Settlement]:
        """Получение поселения по ID"""
        return self.settlements.get(settlement_id)
    
    def get_building(self, building_id: str) -> Optional[Building]:
        """Получение здания по ID"""
        return self.buildings.get(building_id)
    
    def get_point_of_interest(self, poi_id: str) -> Optional[PointOfInterest]:
        """Получение точки интереса по ID"""
        return self.points_of_interest.get(poi_id)
    
    def get_locations_in_radius(self, x: float, y: float, radius: float) -> List[Location]:
        """Получение локаций в радиусе"""
        nearby_locations = []
        
        for location in self.locations.values():
            distance = math.sqrt((location.x - x)**2 + (location.y - y)**2)
            if distance <= radius:
                nearby_locations.append(location)
        
        return nearby_locations
    
    def discover_location(self, location_id: str) -> bool:
        """Открытие локации"""
        location = self.get_location(location_id)
        if location and not location.is_discovered:
            location.is_discovered = True
            location.last_visited = time.time()
            location.visit_count += 1
            self.stats['discovered_locations'] += 1
            return True
        return False
    
    def complete_dungeon(self, dungeon_id: str) -> bool:
        """Завершение подземелья"""
        dungeon = self.get_dungeon(dungeon_id)
        if dungeon and not dungeon.is_completed:
            dungeon.is_completed = True
            dungeon.completion_time = time.time()
            if not dungeon.best_time or dungeon.completion_time < dungeon.best_time:
                dungeon.best_time = dungeon.completion_time
            self.stats['completed_dungeons'] += 1
            return True
        return False
    
    def get_location_stats(self) -> Dict[str, Any]:
        """Получение статистики локаций"""
        return self.stats.copy()
    
    def get_all_locations(self) -> List[Location]:
        """Получение всех локаций"""
        return list(self.locations.values())
    
    def get_all_dungeons(self) -> List[Dungeon]:
        """Получение всех подземелий"""
        return list(self.dungeons.values())
    
    def get_all_settlements(self) -> List[Settlement]:
        """Получение всех поселений"""
        return list(self.settlements.values())
    
    def get_all_buildings(self) -> List[Building]:
        """Получение всех зданий"""
        return list(self.buildings.values())
    
    def get_all_points_of_interest(self) -> List[PointOfInterest]:
        """Получение всех точек интереса"""
        return list(self.points_of_interest.values())
