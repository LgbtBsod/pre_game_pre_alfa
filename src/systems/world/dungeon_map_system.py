#!/usr/bin/env python3
"""Система карт подземелий для игрового мира
Включает генерацию карт подземелий, отслеживание исследованных областей и навигацию"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Set
import logging
import random
import time
import math

from src.core.architecture import BaseComponent, ComponentType, Priority

# = ТИПЫ КАРТ ПОДЗЕМЕЛИЙ
class DungeonMapType(Enum):
    """Типы карт подземелий"""
    FLOOR_PLAN = "floor_plan"     # План этажа
    ROOM_LAYOUT = "room_layout"   # Расположение комнат
    CORRIDOR_MAP = "corridor_map" # Карта коридоров
    TREASURE_MAP = "treasure_map" # Карта сокровищ
    TRAP_MAP = "trap_map"         # Карта ловушек
    ENEMY_MAP = "enemy_map"       # Карта врагов
    SECRET_MAP = "secret_map"     # Карта секретов

# = ТИПЫ ОБЛАСТЕЙ НА КАРТЕ
class MapAreaType(Enum):
    """Типы областей на карте"""
    UNEXPLORED = "unexplored"     # Неисследованная область
    EXPLORED = "explored"         # Исследованная область
    VISIBLE = "visible"           # Видимая область
    DISCOVERED = "discovered"     # Обнаруженная область
    SECRET = "secret"             # Секретная область
    TRAP = "trap"                 # Ловушка
    TREASURE = "treasure"         # Сокровище
    ENEMY = "enemy"               # Враг
    EXIT = "exit"                 # Выход
    ENTRANCE = "entrance"         # Вход

# = НАСТРОЙКИ КАРТЫ
@dataclass
class DungeonMapSettings:
    """Настройки карты подземелья"""
    map_type: DungeonMapType
    grid_size: int = 64
    cell_size: float = 1.0
    fog_of_war: bool = True
    auto_reveal_distance: int = 3
    reveal_on_exploration: bool = True
    show_secrets: bool = False
    show_traps: bool = True
    show_treasures: bool = True
    show_enemies: bool = True
    persistence: bool = True

# = СТРУКТУРЫ ДАННЫХ
@dataclass
class MapCell:
    """Ячейка карты"""
    x: int
    y: int
    area_type: MapAreaType
    discovered: bool = False
    explored: bool = False
    visible: bool = False
    last_seen: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MapLayer:
    """Слой карты"""
    layer_id: str
    layer_type: DungeonMapType
    cells: Dict[Tuple[int, int], MapCell]
    visible: bool = True
    opacity: float = 1.0
    z_order: int = 0

@dataclass
class DungeonMapData:
    """Данные карты подземелья"""
    dungeon_id: str
    map_id: str
    settings: DungeonMapSettings
    layers: Dict[str, MapLayer]
    grid_width: int
    grid_height: int
    explored_cells: Set[Tuple[int, int]]
    discovered_cells: Set[Tuple[int, int]]
    secret_areas: Set[Tuple[int, int]]
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)

@dataclass
class MapMarker:
    """Маркер на карте"""
    marker_id: str
    x: int
    y: int
    marker_type: str
    label: str
    icon: str
    color: str
    visible: bool = True
    persistent: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExplorationData:
    """Данные исследования"""
    dungeon_id: str
    character_id: str
    explored_cells: Set[Tuple[int, int]]
    discovered_secrets: Set[Tuple[int, int]]
    found_treasures: Set[Tuple[int, int]]
    triggered_traps: Set[Tuple[int, int]]
    defeated_enemies: Set[Tuple[int, int]]
    exploration_percentage: float = 0.0
    last_exploration: float = 0.0

# = СИСТЕМА КАРТ ПОДЗЕМЕЛИЙ
class DungeonMapSystem(BaseComponent):
    """Система карт подземелий"""
    
    def __init__(self):
        super().__init__(
            component_id="DungeonMapSystem",
            component_type=ComponentType.SYSTEM,
            priority=Priority.HIGH
        )
        
        # Карты подземелий
        self.dungeon_maps: Dict[str, DungeonMapData] = {}
        self.map_markers: Dict[str, List[MapMarker]] = {}
        self.exploration_data: Dict[str, ExplorationData] = {}
        
        # Кэши и статистика
        self.map_cache: Dict[str, Any] = {}
        self.generation_stats = {
            "maps_created": 0,
            "cells_generated": 0,
            "layers_created": 0,
            "markers_placed": 0,
            "total_generation_time": 0.0
        }
        
        # Слушатели событий
        self.cell_explored_callbacks: List[callable] = []
        self.area_discovered_callbacks: List[callable] = []
        self.secret_found_callbacks: List[callable] = []
        
        self.logger = logging.getLogger(__name__)
    
    def _on_initialize(self) -> bool:
        """Инициализация системы карт подземелий"""
        try:
            self.logger.info("DungeonMapSystem инициализирован")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации DungeonMapSystem: {e}")
            return False
    
    def create_dungeon_map(self, dungeon_id: str, dungeon_data: Dict[str, Any], 
                          settings: DungeonMapSettings) -> DungeonMapData:
        """Создание карты подземелья"""
        start_time = time.time()
        
        map_id = f"map_{dungeon_id}_{int(time.time())}"
        
        # Определение размеров сетки
        grid_width = settings.grid_size
        grid_height = settings.grid_size
        
        # Создание слоев карты
        layers = {}
        
        # Основной слой (план этажа)
        floor_layer = self._create_floor_layer(dungeon_id, grid_width, grid_height, dungeon_data)
        layers["floor"] = floor_layer
        
        # Слой комнат
        room_layer = self._create_room_layer(dungeon_id, grid_width, grid_height, dungeon_data)
        layers["rooms"] = room_layer
        
        # Слой коридоров
        corridor_layer = self._create_corridor_layer(dungeon_id, grid_width, grid_height, dungeon_data)
        layers["corridors"] = corridor_layer
        
        # Слой сокровищ
        treasure_layer = self._create_treasure_layer(dungeon_id, grid_width, grid_height, dungeon_data)
        layers["treasures"] = treasure_layer
        
        # Слой ловушек
        trap_layer = self._create_trap_layer(dungeon_id, grid_width, grid_height, dungeon_data)
        layers["traps"] = trap_layer
        
        # Слой врагов
        enemy_layer = self._create_enemy_layer(dungeon_id, grid_width, grid_height, dungeon_data)
        layers["enemies"] = enemy_layer
        
        # Слой секретов
        secret_layer = self._create_secret_layer(dungeon_id, grid_width, grid_height, dungeon_data)
        layers["secrets"] = secret_layer
        
        # Создание карты
        dungeon_map = DungeonMapData(
            dungeon_id=dungeon_id,
            map_id=map_id,
            settings=settings,
            layers=layers,
            grid_width=grid_width,
            grid_height=grid_height,
            explored_cells=set(),
            discovered_cells=set(),
            secret_areas=set()
        )
        
        self.dungeon_maps[map_id] = dungeon_map
        self.map_markers[map_id] = []
        
        # Обновление статистики
        generation_time = time.time() - start_time
        self.generation_stats["maps_created"] += 1
        self.generation_stats["layers_created"] += len(layers)
        self.generation_stats["cells_generated"] += sum(len(layer.cells) for layer in layers.values())
        self.generation_stats["total_generation_time"] += generation_time
        
        self.logger.info(f"Создана карта подземелья {map_id}: {len(layers)} слоев, {grid_width}x{grid_height} ячеек")
        
        return dungeon_map
    
    def _create_floor_layer(self, dungeon_id: str, width: int, height: int, 
                           dungeon_data: Dict[str, Any]) -> MapLayer:
        """Создание слоя плана этажа"""
        cells = {}
        
        # Получение данных о комнатах и коридорах
        rooms = dungeon_data.get("rooms", [])
        corridors = dungeon_data.get("corridors", [])
        
        # Заполнение ячеек
        for x in range(width):
            for y in range(height):
                cell_type = MapAreaType.UNEXPLORED
                
                # Проверка, находится ли ячейка в комнате
                for room in rooms:
                    if (room["x"] <= x <= room["x"] + room["width"] and 
                        room["y"] <= y <= room["y"] + room["height"]):
                        cell_type = MapAreaType.EXPLORED
                        break
                
                # Проверка, находится ли ячейка в коридоре
                if cell_type == MapAreaType.UNEXPLORED:
                    for corridor in corridors:
                        if (corridor["x"] <= x <= corridor["x"] + corridor["width"] and 
                            corridor["y"] <= y <= corridor["y"] + corridor["height"]):
                            cell_type = MapAreaType.EXPLORED
                            break
                
                cells[(x, y)] = MapCell(
                    x=x, y=y, area_type=cell_type
                )
        
        return MapLayer(
            layer_id="floor",
            layer_type=DungeonMapType.FLOOR_PLAN,
            cells=cells,
            z_order=0
        )
    
    def _create_room_layer(self, dungeon_id: str, width: int, height: int, 
                          dungeon_data: Dict[str, Any]) -> MapLayer:
        """Создание слоя комнат"""
        cells = {}
        rooms = dungeon_data.get("rooms", [])
        
        for x in range(width):
            for y in range(height):
                cell_type = MapAreaType.UNEXPLORED
                metadata = {}
                
                for room in rooms:
                    if (room["x"] <= x <= room["x"] + room["width"] and 
                        room["y"] <= y <= room["y"] + room["height"]):
                        cell_type = MapAreaType.EXPLORED
                        metadata["room_id"] = room.get("id", "")
                        metadata["room_type"] = room.get("type", "")
                        break
                
                cells[(x, y)] = MapCell(
                    x=x, y=y, area_type=cell_type, metadata=metadata
                )
        
        return MapLayer(
            layer_id="rooms",
            layer_type=DungeonMapType.ROOM_LAYOUT,
            cells=cells,
            z_order=1
        )
    
    def _create_corridor_layer(self, dungeon_id: str, width: int, height: int, 
                              dungeon_data: Dict[str, Any]) -> MapLayer:
        """Создание слоя коридоров"""
        cells = {}
        corridors = dungeon_data.get("corridors", [])
        
        for x in range(width):
            for y in range(height):
                cell_type = MapAreaType.UNEXPLORED
                metadata = {}
                
                for corridor in corridors:
                    if (corridor["x"] <= x <= corridor["x"] + corridor["width"] and 
                        corridor["y"] <= y <= corridor["y"] + corridor["height"]):
                        cell_type = MapAreaType.EXPLORED
                        metadata["corridor_id"] = corridor.get("id", "")
                        metadata["corridor_type"] = corridor.get("type", "")
                        break
                
                cells[(x, y)] = MapCell(
                    x=x, y=y, area_type=cell_type, metadata=metadata
                )
        
        return MapLayer(
            layer_id="corridors",
            layer_type=DungeonMapType.CORRIDOR_MAP,
            cells=cells,
            z_order=2
        )
    
    def _create_treasure_layer(self, dungeon_id: str, width: int, height: int, 
                              dungeon_data: Dict[str, Any]) -> MapLayer:
        """Создание слоя сокровищ"""
        cells = {}
        treasures = dungeon_data.get("treasures", [])
        
        for x in range(width):
            for y in range(height):
                cell_type = MapAreaType.UNEXPLORED
                metadata = {}
                
                for treasure in treasures:
                    if treasure["x"] == x and treasure["y"] == y:
                        cell_type = MapAreaType.TREASURE
                        metadata["treasure_id"] = treasure.get("id", "")
                        metadata["treasure_type"] = treasure.get("type", "")
                        metadata["rarity"] = treasure.get("rarity", "")
                        break
                
                cells[(x, y)] = MapCell(
                    x=x, y=y, area_type=cell_type, metadata=metadata
                )
        
        return MapLayer(
            layer_id="treasures",
            layer_type=DungeonMapType.TREASURE_MAP,
            cells=cells,
            z_order=3
        )
    
    def _create_trap_layer(self, dungeon_id: str, width: int, height: int, 
                          dungeon_data: Dict[str, Any]) -> MapLayer:
        """Создание слоя ловушек"""
        cells = {}
        traps = dungeon_data.get("traps", [])
        
        for x in range(width):
            for y in range(height):
                cell_type = MapAreaType.UNEXPLORED
                metadata = {}
                
                for trap in traps:
                    if trap["x"] == x and trap["y"] == y:
                        cell_type = MapAreaType.TRAP
                        metadata["trap_id"] = trap.get("id", "")
                        metadata["trap_type"] = trap.get("type", "")
                        metadata["triggered"] = trap.get("triggered", False)
                        break
                
                cells[(x, y)] = MapCell(
                    x=x, y=y, area_type=cell_type, metadata=metadata
                )
        
        return MapLayer(
            layer_id="traps",
            layer_type=DungeonMapType.TRAP_MAP,
            cells=cells,
            z_order=4
        )
    
    def _create_enemy_layer(self, dungeon_id: str, width: int, height: int, 
                           dungeon_data: Dict[str, Any]) -> MapLayer:
        """Создание слоя врагов"""
        cells = {}
        enemies = dungeon_data.get("enemies", [])
        
        for x in range(width):
            for y in range(height):
                cell_type = MapAreaType.UNEXPLORED
                metadata = {}
                
                for enemy in enemies:
                    if enemy["x"] == x and enemy["y"] == y:
                        cell_type = MapAreaType.ENEMY
                        metadata["enemy_id"] = enemy.get("id", "")
                        metadata["enemy_type"] = enemy.get("type", "")
                        metadata["defeated"] = enemy.get("defeated", False)
                        break
                
                cells[(x, y)] = MapCell(
                    x=x, y=y, area_type=cell_type, metadata=metadata
                )
        
        return MapLayer(
            layer_id="enemies",
            layer_type=DungeonMapType.ENEMY_MAP,
            cells=cells,
            z_order=5
        )
    
    def _create_secret_layer(self, dungeon_id: str, width: int, height: int, 
                            dungeon_data: Dict[str, Any]) -> MapLayer:
        """Создание слоя секретов"""
        cells = {}
        secrets = dungeon_data.get("secrets", [])
        
        for x in range(width):
            for y in range(height):
                cell_type = MapAreaType.UNEXPLORED
                metadata = {}
                
                for secret in secrets:
                    if secret["x"] == x and secret["y"] == y:
                        cell_type = MapAreaType.SECRET
                        metadata["secret_id"] = secret.get("id", "")
                        metadata["secret_type"] = secret.get("type", "")
                        metadata["discovered"] = secret.get("discovered", False)
                        break
                
                cells[(x, y)] = MapCell(
                    x=x, y=y, area_type=cell_type, metadata=metadata
                )
        
        return MapLayer(
            layer_id="secrets",
            layer_type=DungeonMapType.SECRET_MAP,
            cells=cells,
            z_order=6
        )
    
    def explore_cell(self, map_id: str, character_id: str, x: int, y: int) -> bool:
        """Исследование ячейки карты"""
        if map_id not in self.dungeon_maps:
            return False
        
        dungeon_map = self.dungeon_maps[map_id]
        
        # Проверка границ карты
        if not (0 <= x < dungeon_map.grid_width and 0 <= y < dungeon_map.grid_height):
            return False
        
        # Обновление ячеек во всех слоях
        for layer in dungeon_map.layers.values():
            cell_key = (x, y)
            if cell_key in layer.cells:
                cell = layer.cells[cell_key]
                cell.explored = True
                cell.visible = True
                cell.last_seen = time.time()
                
                # Обновление типа области
                if cell.area_type == MapAreaType.UNEXPLORED:
                    cell.area_type = MapAreaType.EXPLORED
        
        # Добавление в исследованные ячейки
        dungeon_map.explored_cells.add((x, y))
        dungeon_map.last_updated = time.time()
        
        # Обновление данных исследования
        self._update_exploration_data(dungeon_map.dungeon_id, character_id, x, y)
        
        # Уведомление о исследовании ячейки
        self._notify_cell_explored(map_id, character_id, x, y)
        
        return True
    
    def reveal_area(self, map_id: str, character_id: str, center_x: int, center_y: int, 
                    radius: int = 3) -> int:
        """Раскрытие области вокруг позиции"""
        if map_id not in self.dungeon_maps:
            return 0
        
        dungeon_map = self.dungeon_maps[map_id]
        revealed_cells = 0
        
        # Раскрытие ячеек в радиусе
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                x = center_x + dx
                y = center_y + dy
                
                # Проверка расстояния
                distance = math.sqrt(dx*dx + dy*dy)
                if distance <= radius:
                    if self.explore_cell(map_id, character_id, x, y):
                        revealed_cells += 1
        
        return revealed_cells
    
    def discover_secret(self, map_id: str, character_id: str, x: int, y: int) -> bool:
        """Обнаружение секрета"""
        if map_id not in self.dungeon_maps:
            return False
        
        dungeon_map = self.dungeon_maps[map_id]
        
        # Проверка наличия секрета
        secret_layer = dungeon_map.layers.get("secrets")
        if not secret_layer:
            return False
        
        cell_key = (x, y)
        if cell_key not in secret_layer.cells:
            return False
        
        cell = secret_layer.cells[cell_key]
        if cell.area_type != MapAreaType.SECRET:
            return False
        
        # Обнаружение секрета
        cell.area_type = MapAreaType.DISCOVERED
        cell.metadata["discovered"] = True
        dungeon_map.secret_areas.add(cell_key)
        dungeon_map.last_updated = time.time()
        
        # Уведомление о обнаружении секрета
        self._notify_secret_found(map_id, character_id, x, y, cell.metadata)
        
        return True
    
    def add_map_marker(self, map_id: str, x: int, y: int, marker_type: str, 
                      label: str, icon: str = "default", color: str = "white", 
                      persistent: bool = False) -> str:
        """Добавление маркера на карту"""
        if map_id not in self.dungeon_maps:
            return ""
        
        marker_id = f"marker_{map_id}_{int(time.time())}_{random.randint(1000, 9999)}"
        
        marker = MapMarker(
            marker_id=marker_id,
            x=x, y=y,
            marker_type=marker_type,
            label=label,
            icon=icon,
            color=color,
            persistent=persistent
        )
        
        self.map_markers[map_id].append(marker)
        self.generation_stats["markers_placed"] += 1
        
        return marker_id
    
    def remove_map_marker(self, map_id: str, marker_id: str) -> bool:
        """Удаление маркера с карты"""
        if map_id not in self.map_markers:
            return False
        
        markers = self.map_markers[map_id]
        for i, marker in enumerate(markers):
            if marker.marker_id == marker_id:
                del markers[i]
                return True
        
        return False
    
    def get_map_data(self, map_id: str, character_id: str = None) -> Optional[DungeonMapData]:
        """Получение данных карты"""
        if map_id not in self.dungeon_maps:
            return None
        
        dungeon_map = self.dungeon_maps[map_id]
        
        # Если указан персонаж, применяем туман войны
        if character_id and dungeon_map.settings.fog_of_war:
            return self._apply_fog_of_war(dungeon_map, character_id)
        
        return dungeon_map
    
    def _apply_fog_of_war(self, dungeon_map: DungeonMapData, character_id: str) -> DungeonMapData:
        """Применение тумана войны"""
        # Создание копии карты
        fog_map = DungeonMapData(
            dungeon_id=dungeon_map.dungeon_id,
            map_id=dungeon_map.map_id,
            settings=dungeon_map.settings,
            layers={},
            grid_width=dungeon_map.grid_width,
            grid_height=dungeon_map.grid_height,
            explored_cells=dungeon_map.explored_cells.copy(),
            discovered_cells=dungeon_map.discovered_cells.copy(),
            secret_areas=dungeon_map.secret_areas.copy()
        )
        
        # Копирование слоев с применением тумана войны
        for layer_id, layer in dungeon_map.layers.items():
            fog_layer = MapLayer(
                layer_id=layer.layer_id,
                layer_type=layer.layer_type,
                cells={},
                visible=layer.visible,
                opacity=layer.opacity,
                z_order=layer.z_order
            )
            
            for cell_key, cell in layer.cells.items():
                fog_cell = MapCell(
                    x=cell.x, y=cell.y,
                    area_type=cell.area_type,
                    discovered=cell.discovered,
                    explored=cell.explored,
                    visible=cell.visible,
                    last_seen=cell.last_seen,
                    metadata=cell.metadata.copy()
                )
                
                # Скрытие неисследованных областей
                if not cell.explored:
                    fog_cell.area_type = MapAreaType.UNEXPLORED
                    fog_cell.visible = False
                
                fog_layer.cells[cell_key] = fog_cell
            
            fog_map.layers[layer_id] = fog_layer
        
        return fog_map
    
    def _update_exploration_data(self, dungeon_id: str, character_id: str, x: int, y: int):
        """Обновление данных исследования"""
        exploration_key = f"{dungeon_id}_{character_id}"
        
        if exploration_key not in self.exploration_data:
            self.exploration_data[exploration_key] = ExplorationData(
                dungeon_id=dungeon_id,
                character_id=character_id,
                explored_cells=set(),
                discovered_secrets=set(),
                found_treasures=set(),
                triggered_traps=set(),
                defeated_enemies=set()
            )
        
        exploration = self.exploration_data[exploration_key]
        exploration.explored_cells.add((x, y))
        exploration.last_exploration = time.time()
        
        # Обновление процента исследования
        if dungeon_id in self.dungeon_maps:
            dungeon_map = self.dungeon_maps[dungeon_id]
            total_cells = dungeon_map.grid_width * dungeon_map.grid_height
            exploration.exploration_percentage = len(exploration.explored_cells) / total_cells * 100
    
    def get_exploration_data(self, dungeon_id: str, character_id: str) -> Optional[ExplorationData]:
        """Получение данных исследования"""
        exploration_key = f"{dungeon_id}_{character_id}"
        return self.exploration_data.get(exploration_key)
    
    def get_map_markers(self, map_id: str) -> List[MapMarker]:
        """Получение маркеров карты"""
        return self.map_markers.get(map_id, [])
    
    def get_map_statistics(self, map_id: str) -> Dict[str, Any]:
        """Получение статистики карты"""
        if map_id not in self.dungeon_maps:
            return {}
        
        dungeon_map = self.dungeon_maps[map_id]
        
        # Подсчет статистики по слоям
        layer_stats = {}
        for layer_id, layer in dungeon_map.layers.items():
            explored_cells = sum(1 for cell in layer.cells.values() if cell.explored)
            total_cells = len(layer.cells)
            
            layer_stats[layer_id] = {
                "total_cells": total_cells,
                "explored_cells": explored_cells,
                "exploration_percentage": explored_cells / total_cells * 100 if total_cells > 0 else 0
            }
        
        return {
            "map_id": map_id,
            "dungeon_id": dungeon_map.dungeon_id,
            "grid_size": f"{dungeon_map.grid_width}x{dungeon_map.grid_height}",
            "total_cells": dungeon_map.grid_width * dungeon_map.grid_height,
            "explored_cells": len(dungeon_map.explored_cells),
            "discovered_cells": len(dungeon_map.discovered_cells),
            "secret_areas": len(dungeon_map.secret_areas),
            "layers": len(dungeon_map.layers),
            "markers": len(self.map_markers.get(map_id, [])),
            "layer_statistics": layer_stats,
            "created_at": dungeon_map.created_at,
            "last_updated": dungeon_map.last_updated
        }
    
    def add_cell_explored_callback(self, callback: callable):
        """Добавление callback для исследования ячейки"""
        self.cell_explored_callbacks.append(callback)
    
    def add_area_discovered_callback(self, callback: callable):
        """Добавление callback для обнаружения области"""
        self.area_discovered_callbacks.append(callback)
    
    def add_secret_found_callback(self, callback: callable):
        """Добавление callback для обнаружения секрета"""
        self.secret_found_callbacks.append(callback)
    
    def _notify_cell_explored(self, map_id: str, character_id: str, x: int, y: int):
        """Уведомление о исследовании ячейки"""
        for callback in self.cell_explored_callbacks:
            try:
                callback(map_id, character_id, x, y)
            except Exception as e:
                self.logger.error(f"Ошибка в callback исследования ячейки: {e}")
    
    def _notify_area_discovered(self, map_id: str, character_id: str, area_type: str, x: int, y: int):
        """Уведомление о обнаружении области"""
        for callback in self.area_discovered_callbacks:
            try:
                callback(map_id, character_id, area_type, x, y)
            except Exception as e:
                self.logger.error(f"Ошибка в callback обнаружения области: {e}")
    
    def _notify_secret_found(self, map_id: str, character_id: str, x: int, y: int, metadata: Dict[str, Any]):
        """Уведомление о обнаружении секрета"""
        for callback in self.secret_found_callbacks:
            try:
                callback(map_id, character_id, x, y, metadata)
            except Exception as e:
                self.logger.error(f"Ошибка в callback обнаружения секрета: {e}")
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Получение статистики генерации"""
        return self.generation_stats.copy()
    
    def clear_cache(self):
        """Очистка кэша"""
        self.map_cache.clear()
        self.logger.info("Кэш DungeonMapSystem очищен")
    
    def _on_destroy(self):
        """Уничтожение системы карт подземелий"""
        self.dungeon_maps.clear()
        self.map_markers.clear()
        self.exploration_data.clear()
        self.map_cache.clear()
        self.cell_explored_callbacks.clear()
        self.area_discovered_callbacks.clear()
        self.secret_found_callbacks.clear()
        
        self.logger.info("DungeonMapSystem уничтожен")
