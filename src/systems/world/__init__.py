#!/usr/bin/env/python3
"""
World Systems Package
Системы управления игровым миром
"""

from .world_manager import WorldManager, WorldObject, WorldObjectType, ObjectState, WorldGrid
from .biome_types import (
    BiomeType, ClimateType, SeasonType, WeatherType,
    BiomeProperties, ClimateProperties, WeatherProperties,
    BiomeManager
)
from .location_types import (
    LocationType, DungeonType, SettlementType, BuildingType, PointOfInterestType,
    Location, Dungeon, Settlement, Building, PointOfInterest,
    LocationManager
)

__all__ = [
    # Существующие классы
    'WorldManager', 'WorldObject', 'WorldObjectType', 'ObjectState', 'WorldGrid',
    
    # Новые классы Фазы 9
    'BiomeType', 'ClimateType', 'SeasonType', 'WeatherType',
    'BiomeProperties', 'ClimateProperties', 'WeatherProperties',
    'BiomeManager',
    
    'LocationType', 'DungeonType', 'SettlementType', 'BuildingType', 'PointOfInterestType',
    'Location', 'Dungeon', 'Settlement', 'Building', 'PointOfInterest',
    'LocationManager'
]
