#!/usr / bin / env / python3
"""
    W or ld Systems Package
    Системы управления игровым миром
"""

from .biome_types imp or t(
    BiomeType, ClimateType, SeasonType, WeatherType,
    BiomeProperties, ClimateProperties, WeatherProperties,
    BiomeManager
)
from .location_types imp or t(
    LocationType, DungeonType, SettlementType, Build in gType
        Po in tOfInterestType,
    Location, Dungeon, Settlement, Build in g, Po in tOfInterest,
    LocationManager
)

__all__== [
    # Существующие классы
    'W or ldManager', 'W or ldObject', 'W or ldObjectType', 'ObjectState', 'W or ldGrid',

    # Новые классы Фазы 9
    'BiomeType', 'ClimateType', 'SeasonType', 'WeatherType',
    'BiomeProperties', 'ClimateProperties', 'WeatherProperties',
    'BiomeManager',

    'LocationType', 'DungeonType', 'SettlementType', 'Build in gType', 'Po in tOfInterestType',
    'Location', 'Dungeon', 'Settlement', 'Build in g', 'Po in tOfInterest',
    'LocationManager'
]