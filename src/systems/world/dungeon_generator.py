#!/usr/bin/env python3
"""Генератор подземелий для процедурного мира
Создает процедурные подземелья с комнатами, коридорами, ловушками и сокровищами"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Set
import logging
import random
import time
import math

from src.core.architecture import BaseComponent, ComponentType, Priority

# = ТИПЫ ПОДЗЕМЕЛИЙ
class DungeonType(Enum):
    """Типы подземелий"""
    CAVE = "cave"               # Пещера
    CRYPT = "crypt"             # Склеп
    MINE = "mine"               # Шахта
    LABORATORY = "laboratory"   # Лаборатория
    TEMPLE = "temple"           # Храм
    FORTRESS = "fortress"       # Крепость
    MAZE = "maze"               # Лабиринт
    TOWER = "tower"             # Башня

class RoomType(Enum):
    """Типы комнат"""
    ENTRANCE = "entrance"       # Вход
    CORRIDOR = "corridor"       # Коридор
    CHAMBER = "chamber"         # Палата
    TREASURE = "treasure"       # Сокровищница
    BOSS = "boss"               # Босс
    TRAP = "trap"               # Ловушка
    PUZZLE = "puzzle"           # Головоломка
    EXIT = "exit"               # Выход

class TrapType(Enum):
    """Типы ловушек"""
    SPIKE_PIT = "spike_pit"     # Яма с шипами
    POISON_DART = "poison_dart" # Отравленные дротики
    FALLING_CEILING = "falling_ceiling"  # Падающий потолок
    FIRE_TRAP = "fire_trap"     # Огненная ловушка
    ICE_TRAP = "ice_trap"       # Ледяная ловушка
    ELECTRIC_TRAP = "electric_trap"  # Электрическая ловушка
    TELEPORT_TRAP = "teleport_trap"  # Телепорт-ловушка
    CURSE_TRAP = "curse_trap"   # Ловушка-проклятие

# = ДАТАКЛАССЫ
@dataclass
class DungeonSettings:
    """Настройки генерации подземелья"""
    dungeon_type: DungeonType = DungeonType.CAVE
    width: int = 50
    height: int = 50
    min_rooms: int = 10
    max_rooms: int = 25
    room_min_size: int = 3
    room_max_size: int = 8
    corridor_width: int = 2
    trap_density: float = 0.3
    treasure_density: float = 0.2
    enemy_density: float = 0.4
    complexity: float = 0.5  # 0.0 - простой, 1.0 - сложный

@dataclass
class Room:
    """Комната подземелья"""
    room_id: str
    room_type: RoomType
    x: int
    y: int
    width: int
    height: int
    connections: List[str] = field(default_factory=list)
    enemies: List[str] = field(default_factory=list)
    traps: List[str] = field(default_factory=list)
    treasures: List[str] = field(default_factory=list)
    special_features: List[str] = field(default_factory=list)
    explored: bool = False
    cleared: bool = False

@dataclass
class Corridor:
    """Коридор между комнатами"""
    corridor_id: str
    start_room: str
    end_room: str
    path: List[Tuple[int, int]] = field(default_factory=list)
    traps: List[str] = field(default_factory=list)
    width: int = 2

@dataclass
class GeneratedDungeon:
    """Сгенерированное подземелье"""
    dungeon_id: str
    dungeon_type: DungeonType
    settings: DungeonSettings
    rooms: Dict[str, Room] = field(default_factory=dict)
    corridors: Dict[str, Corridor] = field(default_factory=dict)
    grid: List[List[int]] = field(default_factory=list)
    entrance_room: str = ""
    exit_room: str = ""
    boss_room: str = ""
    treasure_rooms: List[str] = field(default_factory=list)
    trap_rooms: List[str] = field(default_factory=list)
    generation_time: float = field(default_factory=time.time)

# = ОСНОВНАЯ СИСТЕМА ГЕНЕРАЦИИ ПОДЗЕМЕЛИЙ
class DungeonGenerator(BaseComponent):
    """Генератор подземелий для процедурного мира"""
    
    def __init__(self):
        super().__init__(
            component_id="DungeonGenerator",
            component_type=ComponentType.SYSTEM,
            priority=Priority.HIGH
        )
        
        # Настройки генерации
        self.default_settings = DungeonSettings()
        
        # Шаблоны комнат для разных типов подземелий
        self.room_templates: Dict[DungeonType, Dict[RoomType, Dict[str, Any]]] = {}
        
        # Кэш сгенерированных подземелий
        self.dungeon_cache: Dict[str, GeneratedDungeon] = {}
        
        # Статистика генерации
        self.generation_stats = {
            "total_dungeons": 0,
            "total_rooms": 0,
            "total_corridors": 0,
            "generation_time": 0.0
        }
        
        # Инициализация шаблонов
        self._initialize_room_templates()
    
    def _on_initialize(self) -> bool:
        """Инициализация генератора подземелий"""
        try:
            self._logger.info("Генератор подземелий инициализирован")
            return True
        except Exception as e:
            self._logger.error(f"Ошибка инициализации генератора подземелий: {e}")
            return False
    
    def _initialize_room_templates(self):
        """Инициализация шаблонов комнат"""
        try:
            # Пещера
            self.room_templates[DungeonType.CAVE] = {
                RoomType.ENTRANCE: {"size_range": (4, 6), "enemy_chance": 0.1, "trap_chance": 0.2},
                RoomType.CHAMBER: {"size_range": (5, 10), "enemy_chance": 0.6, "trap_chance": 0.3},
                RoomType.TREASURE: {"size_range": (3, 5), "enemy_chance": 0.8, "trap_chance": 0.7},
                RoomType.BOSS: {"size_range": (8, 12), "enemy_chance": 1.0, "trap_chance": 0.5},
                RoomType.EXIT: {"size_range": (4, 6), "enemy_chance": 0.2, "trap_chance": 0.4}
            }
            
            # Склеп
            self.room_templates[DungeonType.CRYPT] = {
                RoomType.ENTRANCE: {"size_range": (3, 5), "enemy_chance": 0.3, "trap_chance": 0.4},
                RoomType.CHAMBER: {"size_range": (4, 8), "enemy_chance": 0.7, "trap_chance": 0.5},
                RoomType.TREASURE: {"size_range": (3, 4), "enemy_chance": 0.9, "trap_chance": 0.8},
                RoomType.BOSS: {"size_range": (6, 10), "enemy_chance": 1.0, "trap_chance": 0.6},
                RoomType.EXIT: {"size_range": (3, 5), "enemy_chance": 0.4, "trap_chance": 0.5}
            }
            
            # Лаборатория
            self.room_templates[DungeonType.LABORATORY] = {
                RoomType.ENTRANCE: {"size_range": (4, 6), "enemy_chance": 0.2, "trap_chance": 0.3},
                RoomType.CHAMBER: {"size_range": (5, 9), "enemy_chance": 0.5, "trap_chance": 0.6},
                RoomType.TREASURE: {"size_range": (3, 5), "enemy_chance": 0.7, "trap_chance": 0.8},
                RoomType.BOSS: {"size_range": (7, 11), "enemy_chance": 1.0, "trap_chance": 0.7},
                RoomType.EXIT: {"size_range": (4, 6), "enemy_chance": 0.3, "trap_chance": 0.4}
            }
            
            # Храм
            self.room_templates[DungeonType.TEMPLE] = {
                RoomType.ENTRANCE: {"size_range": (5, 7), "enemy_chance": 0.1, "trap_chance": 0.2},
                RoomType.CHAMBER: {"size_range": (6, 12), "enemy_chance": 0.4, "trap_chance": 0.4},
                RoomType.TREASURE: {"size_range": (4, 6), "enemy_chance": 0.6, "trap_chance": 0.6},
                RoomType.BOSS: {"size_range": (10, 15), "enemy_chance": 1.0, "trap_chance": 0.5},
                RoomType.EXIT: {"size_range": (5, 7), "enemy_chance": 0.2, "trap_chance": 0.3}
            }
            
            self._logger.info(f"Инициализировано {len(self.room_templates)} шаблонов подземелий")
            
        except Exception as e:
            self._logger.error(f"Ошибка инициализации шаблонов комнат: {e}")
    
    def generate_dungeon(self, dungeon_type: DungeonType, 
                        settings: Optional[DungeonSettings] = None) -> GeneratedDungeon:
        """Генерация подземелья"""
        try:
            start_time = time.time()
            
            # Используем переданные настройки или создаем новые
            if settings is None:
                settings = DungeonSettings(dungeon_type=dungeon_type)
            
            # Создаем уникальный ID для подземелья
            dungeon_id = f"{dungeon_type.value}_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
            
            # Создаем подземелье
            dungeon = GeneratedDungeon(
                dungeon_id=dungeon_id,
                dungeon_type=dungeon_type,
                settings=settings
            )
            
            # Генерируем сетку
            dungeon.grid = self._create_empty_grid(settings.width, settings.height)
            
            # Генерируем комнаты
            self._generate_rooms(dungeon)
            
            # Соединяем комнаты коридорами
            self._connect_rooms(dungeon)
            
            # Размещаем специальные элементы
            self._place_special_elements(dungeon)
            
            # Добавляем ловушки и сокровища
            self._add_traps_and_treasures(dungeon)
            
            # Размещаем врагов
            self._place_enemies(dungeon)
            
            # Обновляем статистику
            generation_time = time.time() - start_time
            dungeon.generation_time = generation_time
            self.generation_stats["generation_time"] += generation_time
            self.generation_stats["total_dungeons"] += 1
            self.generation_stats["total_rooms"] += len(dungeon.rooms)
            self.generation_stats["total_corridors"] += len(dungeon.corridors)
            
            # Кэшируем результат
            self.dungeon_cache[dungeon_id] = dungeon
            
            self._logger.info(f"Подземелье {dungeon_type.value} сгенерировано за {generation_time:.3f}с")
            
            return dungeon
            
        except Exception as e:
            self._logger.error(f"Ошибка генерации подземелья {dungeon_type.value}: {e}")
            return None
    
    def _create_empty_grid(self, width: int, height: int) -> List[List[int]]:
        """Создание пустой сетки подземелья"""
        try:
            return [[0 for _ in range(width)] for _ in range(height)]
        except Exception as e:
            self._logger.error(f"Ошибка создания сетки: {e}")
            return []
    
    def _generate_rooms(self, dungeon: GeneratedDungeon):
        """Генерация комнат подземелья"""
        try:
            settings = dungeon.settings
            num_rooms = random.randint(settings.min_rooms, settings.max_rooms)
            
            # Создаем входную комнату
            entrance_room = self._create_room(dungeon, RoomType.ENTRANCE, 0)
            dungeon.rooms[entrance_room.room_id] = entrance_room
            dungeon.entrance_room = entrance_room.room_id
            
            # Создаем остальные комнаты
            for i in range(1, num_rooms - 1):
                room_type = self._select_room_type(dungeon.dungeon_type, i, num_rooms)
                room = self._create_room(dungeon, room_type, i)
                
                if room:
                    dungeon.rooms[room.room_id] = entrance_room
                    
                    # Определяем специальные комнаты
                    if room_type == RoomType.BOSS:
                        dungeon.boss_room = room.room_id
                    elif room_type == RoomType.TREASURE:
                        dungeon.treasure_rooms.append(room.room_id)
                    elif room_type == RoomType.TRAP:
                        dungeon.trap_rooms.append(room.room_id)
            
            # Создаем выходную комнату
            exit_room = self._create_room(dungeon, RoomType.EXIT, num_rooms - 1)
            dungeon.rooms[exit_room.room_id] = exit_room
            dungeon.exit_room = exit_room.room_id
            
        except Exception as e:
            self._logger.error(f"Ошибка генерации комнат: {e}")
    
    def _create_room(self, dungeon: GeneratedDungeon, room_type: RoomType, 
                     room_index: int) -> Optional[Room]:
        """Создание отдельной комнаты"""
        try:
            settings = dungeon.settings
            
            # Получаем шаблон для типа комнаты
            template = self.room_templates.get(dungeon.dungeon_type, {}).get(room_type, {})
            size_range = template.get("size_range", (settings.room_min_size, settings.room_max_size))
            
            # Определяем размер комнаты
            width = random.randint(size_range[0], size_range[1])
            height = random.randint(size_range[0], size_range[1])
            
            # Определяем позицию комнаты
            max_x = settings.width - width
            max_y = settings.height - height
            
            if max_x <= 0 or max_y <= 0:
                return None
            
            # Пытаемся разместить комнату
            for attempt in range(100):
                x = random.randint(0, max_x)
                y = random.randint(0, max_y)
                
                if self._can_place_room(dungeon, x, y, width, height):
                    # Создаем комнату
                    room = Room(
                        room_id=f"room_{room_type.value}_{room_index}_{int(time.time() * 1000)}",
                        room_type=room_type,
                        x=x,
                        y=y,
                        width=width,
                        height=height
                    )
                    
                    # Размещаем комнату на сетке
                    self._place_room_on_grid(dungeon, room)
                    
                    return room
            
            return None
            
        except Exception as e:
            self._logger.error(f"Ошибка создания комнаты {room_type.value}: {e}")
            return None
    
    def _can_place_room(self, dungeon: GeneratedDungeon, x: int, y: int, 
                        width: int, height: int) -> bool:
        """Проверка возможности размещения комнаты"""
        try:
            # Проверяем границы
            if x < 0 or y < 0 or x + width > len(dungeon.grid[0]) or y + height > len(dungeon.grid):
                return False
            
            # Проверяем, что место свободно
            for dy in range(y, y + height):
                for dx in range(x, x + width):
                    if dungeon.grid[dy][dx] != 0:
                        return False
            
            return True
            
        except Exception as e:
            self._logger.error(f"Ошибка проверки размещения комнаты: {e}")
            return False
    
    def _place_room_on_grid(self, dungeon: GeneratedDungeon, room: Room):
        """Размещение комнаты на сетке"""
        try:
            for y in range(room.y, room.y + room.height):
                for x in range(room.x, room.x + room.width):
                    dungeon.grid[y][x] = 1  # 1 = комната
            
        except Exception as e:
            self._logger.error(f"Ошибка размещения комнаты на сетке: {e}")
    
    def _select_room_type(self, dungeon_type: DungeonType, room_index: int, 
                          total_rooms: int) -> RoomType:
        """Выбор типа комнаты"""
        try:
            # Определяем тип комнаты на основе позиции и типа подземелья
            if room_index == 0:
                return RoomType.ENTRANCE
            elif room_index == total_rooms - 1:
                return RoomType.EXIT
            elif room_index == total_rooms // 2:
                return RoomType.BOSS
            elif random.random() < 0.2:
                return RoomType.TREASURE
            elif random.random() < 0.3:
                return RoomType.TRAP
            else:
                return RoomType.CHAMBER
            
        except Exception as e:
            self._logger.error(f"Ошибка выбора типа комнаты: {e}")
            return RoomType.CHAMBER
    
    def _connect_rooms(self, dungeon: GeneratedDungeon):
        """Соединение комнат коридорами"""
        try:
            room_list = list(dungeon.rooms.values())
            
            # Соединяем комнаты последовательно
            for i in range(len(room_list) - 1):
                room1 = room_list[i]
                room2 = room_list[i + 1]
                
                corridor = self._create_corridor(dungeon, room1, room2)
                if corridor:
                    dungeon.corridors[corridor.corridor_id] = corridor
                    
                    # Добавляем связи между комнатами
                    room1.connections.append(room2.room_id)
                    room2.connections.append(room1.room_id)
            
            # Добавляем случайные дополнительные связи для сложности
            if dungeon.settings.complexity > 0.5:
                self._add_random_connections(dungeon)
            
        except Exception as e:
            self._logger.error(f"Ошибка соединения комнат: {e}")
    
    def _create_corridor(self, dungeon: GeneratedDungeon, room1: Room, 
                         room2: Room) -> Optional[Corridor]:
        """Создание коридора между двумя комнатами"""
        try:
            # Определяем центры комнат
            center1 = (room1.x + room1.width // 2, room1.y + room1.height // 2)
            center2 = (room2.x + room2.width // 2, room2.y + room2.height // 2)
            
            # Создаем путь коридора
            path = self._create_corridor_path(dungeon, center1, center2)
            
            if path:
                corridor = Corridor(
                    corridor_id=f"corridor_{room1.room_id}_{room2.room_id}_{int(time.time() * 1000)}",
                    start_room=room1.room_id,
                    end_room=room2.room_id,
                    path=path,
                    width=dungeon.settings.corridor_width
                )
                
                # Размещаем коридор на сетке
                self._place_corridor_on_grid(dungeon, corridor)
                
                return corridor
            
            return None
            
        except Exception as e:
            self._logger.error(f"Ошибка создания коридора: {e}")
            return None
    
    def _create_corridor_path(self, dungeon: GeneratedDungeon, start: Tuple[int, int], 
                             end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Создание пути коридора"""
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
            self._logger.error(f"Ошибка создания пути коридора: {e}")
            return []
    
    def _place_corridor_on_grid(self, dungeon: GeneratedDungeon, corridor: Corridor):
        """Размещение коридора на сетке"""
        try:
            for x, y in corridor.path:
                # Размещаем коридор с учетом ширины
                for dy in range(y - corridor.width // 2, y + corridor.width // 2 + 1):
                    for dx in range(x - corridor.width // 2, x + corridor.width // 2 + 1):
                        if (0 <= dy < len(dungeon.grid) and 
                            0 <= dx < len(dungeon.grid[0])):
                            dungeon.grid[dy][dx] = 2  # 2 = коридор
            
        except Exception as e:
            self._logger.error(f"Ошибка размещения коридора на сетке: {e}")
    
    def _add_random_connections(self, dungeon: GeneratedDungeon):
        """Добавление случайных связей между комнатами"""
        try:
            room_list = list(dungeon.rooms.values())
            num_extra_connections = int(len(room_list) * 0.3)
            
            for _ in range(num_extra_connections):
                room1 = random.choice(room_list)
                room2 = random.choice(room_list)
                
                if (room1.room_id != room2.room_id and 
                    room2.room_id not in room1.connections):
                    
                    corridor = self._create_corridor(dungeon, room1, room2)
                    if corridor:
                        dungeon.corridors[corridor.corridor_id] = corridor
                        room1.connections.append(room2.room_id)
                        room2.connections.append(room1.room_id)
            
        except Exception as e:
            self._logger.error(f"Ошибка добавления случайных связей: {e}")
    
    def _place_special_elements(self, dungeon: GeneratedDungeon):
        """Размещение специальных элементов подземелья"""
        try:
            # Размещаем босса в специальной комнате
            if dungeon.boss_room and dungeon.boss_room in dungeon.rooms:
                boss_room = dungeon.rooms[dungeon.boss_room]
                boss_room.special_features.append("boss_altar")
                boss_room.special_features.append("dark_aura")
            
            # Размещаем сокровища
            for treasure_room_id in dungeon.treasure_rooms:
                if treasure_room_id in dungeon.rooms:
                    treasure_room = dungeon.rooms[treasure_room_id]
                    treasure_room.special_features.append("treasure_chest")
                    treasure_room.special_features.append("magical_glow")
            
            # Размещаем ловушки
            for trap_room_id in dungeon.trap_rooms:
                if trap_room_id in dungeon.rooms:
                    trap_room = dungeon.rooms[trap_room_id]
                    trap_room.special_features.append("trap_mechanism")
                    trap_room.special_features.append("warning_signs")
            
        except Exception as e:
            self._logger.error(f"Ошибка размещения специальных элементов: {e}")
    
    def _add_traps_and_treasures(self, dungeon: GeneratedDungeon):
        """Добавление ловушек и сокровищ"""
        try:
            settings = dungeon.settings
            
            for room in dungeon.rooms.values():
                # Добавляем ловушки
                if random.random() < settings.trap_density:
                    trap_type = random.choice(list(TrapType))
                    room.traps.append(trap_type.value)
                
                # Добавляем сокровища
                if random.random() < settings.treasure_density:
                    treasure_type = self._select_treasure_type(room.room_type)
                    room.treasures.append(treasure_type)
                
                # Добавляем ловушки в коридоры
                for corridor in dungeon.corridors.values():
                    if (corridor.start_room == room.room_id or 
                        corridor.end_room == room.room_id):
                        if random.random() < settings.trap_density * 0.5:
                            trap_type = random.choice(list(TrapType))
                            corridor.traps.append(trap_type.value)
            
        except Exception as e:
            self._logger.error(f"Ошибка добавления ловушек и сокровищ: {e}")
    
    def _select_treasure_type(self, room_type: RoomType) -> str:
        """Выбор типа сокровища"""
        try:
            treasure_types = {
                RoomType.TREASURE: ["gold_chest", "magical_weapon", "precious_gem"],
                RoomType.BOSS: ["boss_loot", "legendary_item", "ancient_relic"],
                RoomType.CHAMBER: ["silver_coins", "basic_weapon", "health_potion"],
                RoomType.ENTRANCE: ["starting_gear", "map_fragment", "weak_potion"],
                RoomType.EXIT: ["escape_reward", "completion_bonus", "final_treasure"]
            }
            
            available_types = treasure_types.get(room_type, ["misc_item"])
            return random.choice(available_types)
            
        except Exception as e:
            self._logger.error(f"Ошибка выбора типа сокровища: {e}")
            return "misc_item"
    
    def _place_enemies(self, dungeon: GeneratedDungeon):
        """Размещение врагов в подземелье"""
        try:
            settings = dungeon.settings
            
            for room in dungeon.rooms.values():
                # Определяем количество врагов на основе типа комнаты
                enemy_count = self._get_enemy_count_for_room(room.room_type, settings)
                
                for _ in range(enemy_count):
                    enemy_type = self._select_enemy_type(dungeon.dungeon_type, room.room_type)
                    if enemy_type:
                        room.enemies.append(enemy_type)
            
        except Exception as e:
            self._logger.error(f"Ошибка размещения врагов: {e}")
    
    def _get_enemy_count_for_room(self, room_type: RoomType, settings: DungeonSettings) -> int:
        """Определение количества врагов для комнаты"""
        try:
            base_counts = {
                RoomType.ENTRANCE: 1,
                RoomType.CORRIDOR: 0,
                RoomType.CHAMBER: 2,
                RoomType.TREASURE: 3,
                RoomType.BOSS: 1,
                RoomType.TRAP: 1,
                RoomType.PUZZLE: 0,
                RoomType.EXIT: 1
            }
            
            base_count = base_counts.get(room_type, 1)
            
            # Модифицируем на основе сложности
            if settings.complexity > 0.7:
                base_count = int(base_count * 1.5)
            elif settings.complexity < 0.3:
                base_count = max(0, base_count - 1)
            
            return base_count
            
        except Exception as e:
            self._logger.error(f"Ошибка определения количества врагов: {e}")
            return 1
    
    def _select_enemy_type(self, dungeon_type: DungeonType, room_type: RoomType) -> str:
        """Выбор типа врага"""
        try:
            enemy_types = {
                DungeonType.CAVE: ["cave_troll", "bat_swarm", "rock_golem"],
                DungeonType.CRYPT: ["skeleton_warrior", "ghost", "zombie"],
                DungeonType.LABORATORY: ["failed_experiment", "mad_scientist", "mutated_creature"],
                DungeonType.TEMPLE: ["temple_guardian", "corrupted_priest", "holy_warrior"],
                DungeonType.FORTRESS: ["fortress_soldier", "siege_engine", "commander"],
                DungeonType.MAZE: ["maze_creature", "lost_wanderer", "minotaur"],
                DungeonType.TOWER: ["tower_mage", "magical_construct", "apprentice"]
            }
            
            available_types = enemy_types.get(dungeon_type, ["generic_enemy"])
            
            # Специальные враги для босс-комнат
            if room_type == RoomType.BOSS:
                boss_enemies = {
                    DungeonType.CAVE: ["cave_lord"],
                    DungeonType.CRYPT: ["ancient_lich"],
                    DungeonType.LABORATORY: ["master_experimenter"],
                    DungeonType.TEMPLE: ["high_priest"],
                    DungeonType.FORTRESS: ["fortress_commander"],
                    DungeonType.MAZE: ["maze_master"],
                    DungeonType.TOWER: ["archmage"]
                }
                available_types = boss_enemies.get(dungeon_type, ["boss_enemy"])
            
            return random.choice(available_types)
            
        except Exception as e:
            self._logger.error(f"Ошибка выбора типа врага: {e}")
            return "generic_enemy"
    
    def get_dungeon(self, dungeon_id: str) -> Optional[GeneratedDungeon]:
        """Получение подземелья по ID"""
        try:
            return self.dungeon_cache.get(dungeon_id)
        except Exception as e:
            self._logger.error(f"Ошибка получения подземелья {dungeon_id}: {e}")
            return None
    
    def get_dungeon_stats(self) -> Dict[str, Any]:
        """Получение статистики генерации"""
        try:
            return {
                "total_dungeons": self.generation_stats["total_dungeons"],
                "total_rooms": self.generation_stats["total_rooms"],
                "total_corridors": self.generation_stats["total_corridors"],
                "generation_time": self.generation_stats["generation_time"],
                "cache_size": len(self.dungeon_cache),
                "average_time_per_dungeon": (self.generation_stats["generation_time"] / 
                                           max(self.generation_stats["total_dungeons"], 1))
            }
            
        except Exception as e:
            self._logger.error(f"Ошибка получения статистики: {e}")
            return {}
    
    def clear_cache(self) -> None:
        """Очистка кэша"""
        try:
            self.dungeon_cache.clear()
            self._logger.info("Кэш генератора подземелий очищен")
            
        except Exception as e:
            self._logger.error(f"Ошибка очистки кэша: {e}")
    
    def _on_destroy(self) -> bool:
        """Уничтожение генератора подземелий"""
        try:
            # Очищаем кэш
            self.clear_cache()
            
            # Сбрасываем статистику
            self.generation_stats = {
                "total_dungeons": 0,
                "total_rooms": 0,
                "total_corridors": 0,
                "generation_time": 0.0
            }
            
            self._logger.info("Генератор подземелий уничтожен")
            return True
            
        except Exception as e:
            self._logger.error(f"Ошибка уничтожения генератора подземелий: {e}")
            return False
