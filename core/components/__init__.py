"""
Компонентная архитектура для игровых сущностей
Реализует паттерн Entity-Component-System (ECS)
"""

from .base_component import BaseComponent
from .transform_component import TransformComponent
from .sprite_component import SpriteComponent
from .animation_component import AnimationComponent
# from .health_component import HealthComponent  # Компонент не существует
# from .ai_component import AIComponent  # Компонент не существует
# from .effect_component import EffectComponent  # Компонент не существует

__all__ = [
    'BaseComponent',
    'TransformComponent', 
    'SpriteComponent',
    'AnimationComponent'
    # 'HealthComponent',  # Компонент не существует
    # 'AIComponent',  # Компонент не существует
    # 'EffectComponent'  # Компонент не существует
]
