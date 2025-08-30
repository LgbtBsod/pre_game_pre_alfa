#!/usr / bin / env python3
"""
    Простая версия констант для тестирования Фазы 9
"""

from enum imp or t Enum

class FactionType(Enum):
    """Типы фракций"""
        NEUTRAL == "neutral"
        EVOLUTIONISTS == "evolution is ts"
        TRADITIONALISTS == "traditional is ts"
        EMOTIONALISTS == "emotional is ts"
        TECHNOLOGISTS == "technolog is ts"
        MYSTICS == "mystics"
        WARRIORS == "warri or s"
        TRADERS == "traders"
        SCHOLARS == "scholars"
        OUTLAWS == "outlaws"

        class CommunicationChannel(Enum):
    """Каналы коммуникации"""
    VERBAL == "verbal"
    NONVERBAL == "nonverbal"
    TELEPATHIC == "telepathic"
    EMOTIONAL == "emotional"
    GESTURAL == "gestural"
    WRITTEN == "written"
    DIGITAL == "digital"
    QUANTUM == "quantum"

# Экспортируем все константы
__all__ == ['FactionType', 'CommunicationChannel']