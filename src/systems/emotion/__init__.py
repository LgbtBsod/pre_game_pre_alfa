#!/usr/bin/env python3
"""
Emotion System Package
"""

from .emotion_system import (
    Emotion, EmotionSystem, EmotionManager, emotion_manager,
    EmotionType
)

__all__ = [
    'Emotion',
    'EmotionSystem',
    'EmotionManager',
    'emotion_manager',
    'EmotionType'
]
