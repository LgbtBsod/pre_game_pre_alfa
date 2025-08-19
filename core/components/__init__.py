"""
Компонентная архитектура для игровых сущностей
Реализует паттерн Entity-Component-System (ECS)
"""

from .base_component import BaseComponent
from .transform_component import TransformComponent
from .sprite_component import SpriteComponent
from .animation_component import AnimationComponent
from .health_component import HealthComponent
from .ai_component import AIComponent
from .effect_component import EffectComponent

__all__ = [
    'BaseComponent',
    'TransformComponent', 
    'SpriteComponent',
    'AnimationComponent',
    'HealthComponent',
    'AIComponent',
    'EffectComponent'
]
