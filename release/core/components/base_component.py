"""
Базовый класс для всех компонентов в системе ECS
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BaseComponent(ABC):
    """
    Базовый класс для всех компонентов.
    Каждый компонент отвечает за одну конкретную функциональность.
    """
    
    def __init__(self, entity_id: str):
        self.entity_id = entity_id
        self.enabled = True
        self._initialized = False
        
    def initialize(self) -> bool:
        """
        Инициализация компонента.
        Вызывается после создания компонента.
        """
        if self._initialized:
            logger.warning(f"Компонент {self.__class__.__name__} уже инициализирован")
            return True
            
        try:
            result = self._initialize()
            self._initialized = result
            if result:
                logger.debug(f"Компонент {self.__class__.__name__} инициализирован для {self.entity_id}")
            return result
        except Exception as e:
            logger.error(f"Ошибка инициализации компонента {self.__class__.__name__}: {e}")
            return False
    
    @abstractmethod
    def _initialize(self) -> bool:
        """
        Внутренняя инициализация компонента.
        Должна быть реализована в подклассах.
        """
        pass
    
    def update(self, delta_time: float) -> None:
        """
        Обновление компонента.
        Вызывается каждый кадр.
        """
        if not self.enabled or not self._initialized:
            return
            
        try:
            self._update(delta_time)
        except Exception as e:
            logger.error(f"Ошибка обновления компонента {self.__class__.__name__}: {e}")
    
    def _update(self, delta_time: float) -> None:
        """
        Внутреннее обновление компонента.
        Может быть переопределено в подклассах.
        """
        pass
    
    def cleanup(self) -> None:
        """
        Очистка ресурсов компонента.
        Вызывается при удалении компонента.
        """
        if not self._initialized:
            return
            
        try:
            self._cleanup()
            self._initialized = False
            logger.debug(f"Компонент {self.__class__.__name__} очищен для {self.entity_id}")
        except Exception as e:
            logger.error(f"Ошибка очистки компонента {self.__class__.__name__}: {e}")
    
    def _cleanup(self) -> None:
        """
        Внутренняя очистка компонента.
        Может быть переопределено в подклассах.
        """
        pass
    
    def get_data(self) -> Dict[str, Any]:
        """
        Получение данных компонента для сериализации.
        """
        return {
            'type': self.__class__.__name__,
            'entity_id': self.entity_id,
            'enabled': self.enabled,
            'initialized': self._initialized
        }
    
    def set_data(self, data: Dict[str, Any]) -> bool:
        """
        Установка данных компонента из сериализованного состояния.
        """
        try:
            self.entity_id = data.get('entity_id', self.entity_id)
            self.enabled = data.get('enabled', self.enabled)
            return True
        except Exception as e:
            logger.error(f"Ошибка установки данных компонента {self.__class__.__name__}: {e}")
            return False
    
    def enable(self) -> None:
        """Включение компонента"""
        self.enabled = True
        logger.debug(f"Компонент {self.__class__.__name__} включен для {self.entity_id}")
    
    def disable(self) -> None:
        """Отключение компонента"""
        self.enabled = False
        logger.debug(f"Компонент {self.__class__.__name__} отключен для {self.entity_id}")
    
    def is_initialized(self) -> bool:
        """Проверка инициализации компонента"""
        return self._initialized
    
    def is_enabled(self) -> bool:
        """Проверка активности компонента"""
        return self.enabled and self._initialized
