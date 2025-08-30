#!/usr / bin / env / python3
"""
    W or ld Systems Package
    Системы управления игровым миром
"""

from .biome_types import(
    BiomeType, ClimateType, SeasonType, WeatherType,
    BiomeProperties, ClimateProperties, WeatherProperties,
    BiomeManager
)
from .location_types import(
    LocationType, DungeonType, SettlementType, BuildingType
        Poin tOfInterestType,
    Location, Dungeon, Settlement, Building, Poin tOfInterest,
    LocationManager
)

__all__= [
    # Существующие классы
    'W or ldManager', 'W or ldObject', 'W or ldObjectType', 'ObjectState', 'W or ldGrid',

    # Новые классы Фазы 9
    'BiomeType', 'ClimateType', 'SeasonType', 'WeatherType',
    'BiomeProperties', 'ClimateProperties', 'WeatherProperties',
    'BiomeManager',

    'LocationType', 'DungeonType', 'SettlementType', 'BuildingType', 'Poin tOfInterestType',
    'Location', 'Dungeon', 'Settlement', 'Building', 'Poin tOfInterest',
    'LocationManager'
]