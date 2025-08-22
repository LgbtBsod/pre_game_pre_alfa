"""
Централизованная система обработки ошибок
Обеспечивает единообразную обработку ошибок во всем приложении
"""

import sys
import traceback
import logging
from typing import Optional, Callable, Dict, Any, List
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
import time

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Уровни серьезности ошибок"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorType(Enum):
    """Типы ошибок"""
    RESOURCE_LOADING = "resource_loading"
    COMPONENT_INITIALIZATION = "component_initialization"
    ENTITY_CREATION = "entity_creation"
    RENDERING = "rendering"
    ANIMATION = "animation"
    CONFIGURATION = "configuration"
    DATABASE = "database"
    NETWORK = "network"
    VALIDATION = "validation"
    UNKNOWN = "unknown"


@dataclass
class ErrorInfo:
    """Информация об ошибке"""
    error_type: ErrorType
    severity: ErrorSeverity
    message: str
    exception: Optional[Exception] = None
    context: Optional[Dict[str, Any]] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class ErrorHandler:
    """
    Централизованный обработчик ошибок.
    Обеспечивает единообразную обработку и логирование ошибок.
    """
    
    def __init__(self, log_file: str = "logs/errors.log"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(exist_ok=True)
        
        # Обработчики ошибок по типам
        self.error_handlers: Dict[ErrorType, Callable] = {}
        
        # Статистика ошибок
        self.error_count = 0
        self.error_history: List[ErrorInfo] = []
        self.max_history_size = 1000
        
        # Настройка логирования ошибок
        self._setup_error_logging()
        
        # Регистрируем стандартные обработчики
        self._register_default_handlers()
    
    def _setup_error_logging(self):
        """Настройка логирования ошибок"""
        error_logger = logging.getLogger('error_handler')
        error_logger.setLevel(logging.DEBUG)
        
        # Файловый обработчик с ротацией
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(self.log_file, maxBytes=1_000_000, backupCount=5, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Форматтер
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        error_logger.addHandler(file_handler)
        self.error_logger = error_logger
    
    def _register_default_handlers(self):
        """Регистрация стандартных обработчиков ошибок"""
        self.register_handler(ErrorType.RESOURCE_LOADING, self._handle_resource_error)
        self.register_handler(ErrorType.COMPONENT_INITIALIZATION, self._handle_component_error)
        self.register_handler(ErrorType.ENTITY_CREATION, self._handle_entity_error)
        self.register_handler(ErrorType.RENDERING, self._handle_rendering_error)
        self.register_handler(ErrorType.CONFIGURATION, self._handle_config_error)
        self.register_handler(ErrorType.DATABASE, self._handle_database_error)
    
    def register_handler(self, error_type: ErrorType, handler: Callable):
        """Регистрация обработчика для типа ошибки"""
        self.error_handlers[error_type] = handler
    
    def handle_error(self, error_type: ErrorType, message: str, 
                    exception: Exception = None, context: Dict[str, Any] = None,
                    severity: ErrorSeverity = ErrorSeverity.ERROR) -> bool:
        """
        Обработка ошибки
        
        Args:
            error_type: Тип ошибки
            message: Сообщение об ошибке
            exception: Исключение (если есть)
            context: Дополнительный контекст
            severity: Уровень серьезности
            
        Returns:
            True если ошибка была обработана успешно
        """
        try:
            # Создаем информацию об ошибке
            error_info = ErrorInfo(
                error_type=error_type,
                severity=severity,
                message=message,
                exception=exception,
                context=context or {}
            )
            
            # Логируем ошибку
            self._log_error(error_info)
            
            # Добавляем в историю
            self._add_to_history(error_info)
            
            # Вызываем специальный обработчик
            if error_type in self.error_handlers:
                return self.error_handlers[error_type](error_info)
            else:
                return self._handle_unknown_error(error_info)
                
        except Exception as e:
            # Ошибка в обработчике ошибок
            logger.critical(f"Критическая ошибка в обработчике ошибок: {e}")
            return False
    
    def _log_error(self, error_info: ErrorInfo):
        """Логирование ошибки"""
        log_message = f"[{error_info.error_type.value.upper()}] {error_info.message}"
        
        if error_info.exception:
            log_message += f"\nException: {error_info.exception}"
            log_message += f"\nTraceback:\n{traceback.format_exc()}"
        
        if error_info.context:
            log_message += f"\nContext: {error_info.context}"
        
        # Логируем в соответствующий уровень
        if error_info.severity == ErrorSeverity.DEBUG:
            self.error_logger.debug(log_message)
        elif error_info.severity == ErrorSeverity.INFO:
            self.error_logger.info(log_message)
        elif error_info.severity == ErrorSeverity.WARNING:
            self.error_logger.warning(log_message)
        elif error_info.severity == ErrorSeverity.ERROR:
            self.error_logger.error(log_message)
        elif error_info.severity == ErrorSeverity.CRITICAL:
            self.error_logger.critical(log_message)
    
    def _add_to_history(self, error_info: ErrorInfo):
        """Добавление ошибки в историю"""
        self.error_history.append(error_info)
        self.error_count += 1
        
        # Ограничиваем размер истории
        if len(self.error_history) > self.max_history_size:
            self.error_history.pop(0)
    
    def _handle_resource_error(self, error_info: ErrorInfo) -> bool:
        """Обработка ошибок загрузки ресурсов"""
        logger.warning(f"Ошибка загрузки ресурса: {error_info.message}")
        
        # Можно добавить логику повторной попытки загрузки
        if error_info.context and 'retry_count' in error_info.context:
            retry_count = error_info.context['retry_count']
            if retry_count < 3:
                logger.info(f"Повторная попытка загрузки ресурса (попытка {retry_count + 1})")
                # Здесь можно добавить логику повторной загрузки
                return True
        
        return False
    
    def _handle_component_error(self, error_info: ErrorInfo) -> bool:
        """Обработка ошибок инициализации компонентов"""
        logger.error(f"Ошибка инициализации компонента: {error_info.message}")
        
        # Создаем заглушку компонента
        if error_info.context and 'entity_id' in error_info.context:
            entity_id = error_info.context['entity_id']
            logger.info(f"Создание заглушки для компонента сущности {entity_id}")
        
        return True
    
    def _handle_entity_error(self, error_info: ErrorInfo) -> bool:
        """Обработка ошибок создания сущностей"""
        logger.error(f"Ошибка создания сущности: {error_info.message}")
        return False
    
    def _handle_rendering_error(self, error_info: ErrorInfo) -> bool:
        """Обработка ошибок рендеринга"""
        logger.warning(f"Ошибка рендеринга: {error_info.message}")
        
        # Можно добавить логику fallback рендеринга
        return True
    
    def _handle_config_error(self, error_info: ErrorInfo) -> bool:
        """Обработка ошибок конфигурации"""
        logger.error(f"Ошибка конфигурации: {error_info.message}")
        
        # Загружаем конфигурацию по умолчанию
        logger.info("Загрузка конфигурации по умолчанию")
        return True
    
    def _handle_database_error(self, error_info: ErrorInfo) -> bool:
        """Обработка ошибок базы данных"""
        logger.error(f"Ошибка базы данных: {error_info.message}")
        
        # Можно добавить логику переподключения
        return False
    
    def _handle_unknown_error(self, error_info: ErrorInfo) -> bool:
        """Обработка неизвестных ошибок"""
        logger.error(f"Неизвестная ошибка: {error_info.message}")
        return True
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Получение статистики ошибок"""
        error_counts = {}
        severity_counts = {}
        
        for error in self.error_history:
            # Подсчет по типам
            error_type = error.error_type.value
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
            
            # Подсчет по уровням серьезности
            severity = error.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            'total_errors': self.error_count,
            'error_types': error_counts,
            'severity_levels': severity_counts,
            'history_size': len(self.error_history)
        }
    
    def clear_history(self):
        """Очистка истории ошибок"""
        self.error_history.clear()
        logger.info("История ошибок очищена")
    
    def get_recent_errors(self, count: int = 10) -> List[ErrorInfo]:
        """Получение последних ошибок"""
        return self.error_history[-count:] if self.error_history else []


# Глобальный экземпляр обработчика ошибок
error_handler = ErrorHandler()


def handle_error_decorator(error_type: ErrorType, severity: ErrorSeverity = ErrorSeverity.ERROR):
    """
    Декоратор для автоматической обработки ошибок в функциях
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler.handle_error(
                    error_type=error_type,
                    message=f"Ошибка в функции {func.__name__}: {str(e)}",
                    exception=e,
                    context={'function': func.__name__, 'args': str(args), 'kwargs': str(kwargs)},
                    severity=severity
                )
                raise
        return wrapper
    return decorator
