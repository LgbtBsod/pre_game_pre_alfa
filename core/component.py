"""Базовый класс для компонентов системы."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from entities.entity_refactored import Entity


class Component(ABC):
    """Базовый класс для всех компонентов."""
    
    def __init__(self, entity: 'Entity'):
        self.entity = entity
        self.enabled = True
        self._initialized = False
    
    def initialize(self) -> None:
        """Инициализация компонента."""
        if not self._initialized:
            self._on_initialize()
            self._initialized = True
    
    def enable(self) -> None:
        """Включить компонент."""
        self.enabled = True
        self._on_enable()
    
    def disable(self) -> None:
        """Отключить компонент."""
        self.enabled = False
        self._on_disable()
    
    def update(self, delta_time: float) -> None:
        """Обновить компонент."""
        if self.enabled and self._initialized:
            self._on_update(delta_time)
    
    def destroy(self) -> None:
        """Уничтожить компонент."""
        self._on_destroy()
        self._initialized = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализовать компонент в словарь."""
        return {
            'enabled': self.enabled,
            'initialized': self._initialized
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Десериализовать компонент из словаря."""
        self.enabled = data.get('enabled', True)
        self._initialized = data.get('initialized', False)
    
    # Абстрактные методы для переопределения
    @abstractmethod
    def _on_initialize(self) -> None:
        """Вызывается при инициализации компонента."""
        pass
    
    def _on_enable(self) -> None:
        """Вызывается при включении компонента."""
        pass
    
    def _on_disable(self) -> None:
        """Вызывается при отключении компонента."""
        pass
    
    @abstractmethod
    def _on_update(self, delta_time: float) -> None:
        """Вызывается при обновлении компонента."""
        pass
    
    def _on_destroy(self) -> None:
        """Вызывается при уничтожении компонента."""
        pass


class ComponentManager:
    """Менеджер компонентов для сущности."""
    
    def __init__(self):
        self._components: Dict[type, Component] = {}
    
    def add_component(self, component: Component) -> None:
        """Добавить компонент."""
        component_type = type(component)
        if component_type in self._components:
            raise ValueError(f"Компонент типа {component_type.__name__} уже существует")
        
        self._components[component_type] = component
        component.initialize()
    
    def get_component(self, component_type: type) -> Optional[Component]:
        """Получить компонент по типу."""
        return self._components.get(component_type)
    
    def has_component(self, component_type: type) -> bool:
        """Проверить наличие компонента."""
        return component_type in self._components
    
    def remove_component(self, component_type: type) -> None:
        """Удалить компонент."""
        if component_type in self._components:
            component = self._components[component_type]
            component.destroy()
            del self._components[component_type]
    
    def update_all(self, delta_time: float) -> None:
        """Обновить все компоненты."""
        for component in self._components.values():
            component.update(delta_time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализовать все компоненты в словарь."""
        return {
            component_type.__name__: component.to_dict()
            for component_type, component in self._components.items()
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Десериализовать компоненты из словаря."""
        # Восстанавливаем состояние существующих компонентов
        for component_name, component_data in data.items():
            # Ищем компонент по имени класса
            for component_type, component in self._components.items():
                if component_type.__name__ == component_name:
                    component.from_dict(component_data)
                    break
