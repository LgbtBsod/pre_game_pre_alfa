"""
Система управления сущностями (Entity Component System)
Объединяет компоненты в сущности и управляет их жизненным циклом
"""

import uuid
from typing import Dict, List, Optional, Type, Any, Set
from dataclasses import dataclass
import logging

from .components.base_component import BaseComponent
from .components.transform_component import TransformComponent, Vector3
from .components.animation_component import AnimationComponent
from .components.sprite_component import SpriteComponent

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """Базовая сущность с уникальным ID"""
    id: str
    name: str
    entity_type: str
    active: bool = True
    components: Dict[Type[BaseComponent], BaseComponent] = None
    
    def __post_init__(self):
        if self.components is None:
            self.components = {}


class EntityManager:
    """
    Менеджер сущностей.
    Управляет созданием, удалением и обновлением сущностей.
    """
    
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.entity_types: Dict[str, List[str]] = {}
        self.component_types: Dict[Type[BaseComponent], Set[str]] = {}
        
        # Статистика
        self.total_entities_created = 0
        self.total_entities_destroyed = 0
    
    def create_entity(self, name: str, entity_type: str, entity_id: str = None) -> Entity:
        """
        Создание новой сущности
        
        Args:
            name: Имя сущности
            entity_type: Тип сущности
            entity_id: Уникальный ID (генерируется автоматически если не указан)
            
        Returns:
            Созданная сущность
        """
        if entity_id is None:
            entity_id = str(uuid.uuid4())
        
        if entity_id in self.entities:
            logger.warning(f"Сущность с ID {entity_id} уже существует")
            return self.entities[entity_id]
        
        entity = Entity(id=entity_id, name=name, entity_type=entity_type)
        self.entities[entity_id] = entity
        
        # Регистрируем по типу
        if entity_type not in self.entity_types:
            self.entity_types[entity_type] = []
        self.entity_types[entity_type].append(entity_id)
        
        self.total_entities_created += 1
        logger.debug(f"Создана сущность: {name} ({entity_id}) типа {entity_type}")
        
        return entity
    
    def destroy_entity(self, entity_id: str) -> bool:
        """
        Удаление сущности
        
        Args:
            entity_id: ID сущности для удаления
            
        Returns:
            True если сущность была удалена
        """
        if entity_id not in self.entities:
            logger.warning(f"Попытка удалить несуществующую сущность: {entity_id}")
            return False
        
        entity = self.entities[entity_id]
        
        # Очищаем компоненты
        for component in entity.components.values():
            component.cleanup()
        
        # Удаляем из регистров
        if entity.entity_type in self.entity_types:
            if entity_id in self.entity_types[entity.entity_type]:
                self.entity_types[entity.entity_type].remove(entity_id)
        
        # Удаляем из списков компонентов
        for component_type, entity_ids in self.component_types.items():
            if entity_id in entity_ids:
                entity_ids.remove(entity_id)
        
        # Удаляем сущность
        del self.entities[entity_id]
        self.total_entities_destroyed += 1
        
        logger.debug(f"Удалена сущность: {entity.name} ({entity_id})")
        return True
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Получение сущности по ID"""
        return self.entities.get(entity_id)
    
    def get_entities_by_type(self, entity_type: str) -> List[Entity]:
        """Получение всех сущностей определенного типа"""
        entity_ids = self.entity_types.get(entity_type, [])
        return [self.entities[entity_id] for entity_id in entity_ids if entity_id in self.entities]
    
    def get_entities_with_component(self, component_type: Type[BaseComponent]) -> List[Entity]:
        """Получение всех сущностей с определенным компонентом"""
        entity_ids = self.component_types.get(component_type, set())
        return [self.entities[entity_id] for entity_id in entity_ids if entity_id in self.entities]
    
    def add_component(self, entity_id: str, component: BaseComponent) -> bool:
        """
        Добавление компонента к сущности
        
        Args:
            entity_id: ID сущности
            component: Компонент для добавления
            
        Returns:
            True если компонент был добавлен
        """
        if entity_id not in self.entities:
            logger.error(f"Попытка добавить компонент к несуществующей сущности: {entity_id}")
            return False
        
        entity = self.entities[entity_id]
        component_type = type(component)
        
        # Проверяем, что компонент не уже добавлен
        if component_type in entity.components:
            logger.warning(f"Компонент {component_type.__name__} уже добавлен к сущности {entity_id}")
            return False
        
        # Инициализируем компонент
        if not component.initialize():
            logger.error(f"Ошибка инициализации компонента {component_type.__name__} для сущности {entity_id}")
            return False
        
        # Добавляем компонент
        entity.components[component_type] = component
        
        # Регистрируем в списке компонентов
        if component_type not in self.component_types:
            self.component_types[component_type] = set()
        self.component_types[component_type].add(entity_id)
        
        logger.debug(f"Добавлен компонент {component_type.__name__} к сущности {entity_id}")
        return True
    
    def remove_component(self, entity_id: str, component_type: Type[BaseComponent]) -> bool:
        """
        Удаление компонента у сущности
        
        Args:
            entity_id: ID сущности
            component_type: Тип компонента для удаления
            
        Returns:
            True если компонент был удален
        """
        if entity_id not in self.entities:
            logger.error(f"Попытка удалить компонент у несуществующей сущности: {entity_id}")
            return False
        
        entity = self.entities[entity_id]
        
        if component_type not in entity.components:
            logger.warning(f"Компонент {component_type.__name__} не найден у сущности {entity_id}")
            return False
        
        # Очищаем компонент
        component = entity.components[component_type]
        component.cleanup()
        
        # Удаляем компонент
        del entity.components[component_type]
        
        # Удаляем из списка компонентов
        if component_type in self.component_types:
            self.component_types[component_type].discard(entity_id)
        
        logger.debug(f"Удален компонент {component_type.__name__} у сущности {entity_id}")
        return True
    
    def get_component(self, entity_id: str, component_type: Type[BaseComponent]) -> Optional[BaseComponent]:
        """Получение компонента сущности"""
        entity = self.get_entity(entity_id)
        if entity:
            return entity.components.get(component_type)
        return None
    
    def has_component(self, entity_id: str, component_type: Type[BaseComponent]) -> bool:
        """Проверка наличия компонента у сущности"""
        entity = self.get_entity(entity_id)
        if entity:
            return component_type in entity.components
        return False
    
    def update_entities(self, delta_time: float) -> None:
        """Обновление всех активных сущностей"""
        for entity in self.entities.values():
            if entity.active:
                for component in entity.components.values():
                    if component.is_enabled():
                        component.update(delta_time)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики системы сущностей"""
        total_components = sum(len(entity.components) for entity in self.entities.values())
        
        return {
            'total_entities': len(self.entities),
            'total_components': total_components,
            'entities_created': self.total_entities_created,
            'entities_destroyed': self.total_entities_destroyed,
            'entity_types': {entity_type: len(entity_ids) for entity_type, entity_ids in self.entity_types.items()},
            'component_types': {comp_type.__name__: len(entity_ids) for comp_type, entity_ids in self.component_types.items()}
        }


class EntityFactory:
    """
    Фабрика сущностей.
    Создает сущности с предустановленными компонентами.
    """
    
    def __init__(self, entity_manager: EntityManager, resource_loader):
        self.entity_manager = entity_manager
        self.resource_loader = resource_loader
    
    def create_player_entity(self, name: str, position: Vector3 = None) -> Entity:
        """Создание сущности игрока"""
        entity = self.entity_manager.create_entity(name, "player")
        
        # Добавляем компоненты
        transform = TransformComponent(entity.id, position or Vector3())
        self.entity_manager.add_component(entity.id, transform)
        
        animation = AnimationComponent(entity.id, "graphics/player")
        self.entity_manager.add_component(entity.id, animation)
        
        sprite = SpriteComponent(entity.id)
        self.entity_manager.add_component(entity.id, sprite)
        
        # Загружаем ресурсы
        sprite_resources = self.resource_loader.load_sprite_animations("graphics/player")
        animation.set_animation_resources(sprite_resources)
        sprite.set_sprite_resources(sprite_resources)
        
        # Связываем компоненты
        sprite.set_transform_component(transform)
        sprite.set_animation_component(animation)
        
        logger.info(f"Создана сущность игрока: {name}")
        return entity
    
    def create_enemy_entity(self, name: str, enemy_type: str, position: Vector3 = None) -> Entity:
        """Создание сущности врага"""
        entity = self.entity_manager.create_entity(name, "enemy")
        
        # Добавляем компоненты
        transform = TransformComponent(entity.id, position or Vector3())
        self.entity_manager.add_component(entity.id, transform)
        
        animation = AnimationComponent(entity.id, f"graphics/monsters/{enemy_type}")
        self.entity_manager.add_component(entity.id, animation)
        
        sprite = SpriteComponent(entity.id)
        self.entity_manager.add_component(entity.id, sprite)
        
        # Загружаем ресурсы
        sprite_resources = self.resource_loader.load_sprite_animations(f"graphics/monsters/{enemy_type}")
        animation.set_animation_resources(sprite_resources)
        sprite.set_sprite_resources(sprite_resources)
        
        # Связываем компоненты
        sprite.set_transform_component(transform)
        sprite.set_animation_component(animation)
        
        logger.info(f"Создана сущность врага: {name} типа {enemy_type}")
        return entity
    
    def create_npc_entity(self, name: str, npc_type: str, position: Vector3 = None) -> Entity:
        """Создание сущности NPC"""
        entity = self.entity_manager.create_entity(name, "npc")
        
        # Добавляем компоненты
        transform = TransformComponent(entity.id, position or Vector3())
        self.entity_manager.add_component(entity.id, transform)
        
        # Для NPC может быть статический спрайт
        sprite = SpriteComponent(entity.id)
        self.entity_manager.add_component(entity.id, sprite)
        
        # Загружаем статический спрайт
        static_sprite = self.resource_loader.load_single_sprite(f"graphics/characters/{npc_type}.png")
        if static_sprite:
            sprite.set_static_sprite(static_sprite)
        
        # Связываем компоненты
        sprite.set_transform_component(transform)
        
        logger.info(f"Создана сущность NPC: {name} типа {npc_type}")
        return entity
