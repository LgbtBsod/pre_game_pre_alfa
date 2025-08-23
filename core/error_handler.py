"""
Улучшенная система обработки ошибок с диагностикой и восстановлением.
Предоставляет централизованную обработку ошибок для всей игры.
"""

import traceback
import sys
import time
import threading
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Уровни серьезности ошибок"""
    INFO = 0
    WARNING = 1
    ERROR = 2
    CRITICAL = 3
    FATAL = 4


class ErrorType(Enum):
    """Типы ошибок"""
    UNKNOWN = "unknown"
    CONFIGURATION = "configuration"
    RESOURCE = "resource"
    NETWORK = "network"
    DATABASE = "database"
    GRAPHICS = "graphics"
    AUDIO = "audio"
    INPUT = "input"
    AI = "ai"
    PHYSICS = "physics"
    MEMORY = "memory"
    THREADING = "threading"
    VALIDATION = "validation"


@dataclass
class ErrorContext:
    """Контекст ошибки"""
    timestamp: float = field(default_factory=time.time)
    thread_id: int = field(default_factory=threading.get_ident)
    stack_trace: str = ""
    additional_data: Dict[str, Any] = field(default_factory=dict)
    user_action: Optional[str] = None
    system_state: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorRecord:
    """Запись об ошибке"""
    error_type: ErrorType
    message: str
    severity: ErrorSeverity
    context: ErrorContext
    exception: Optional[Exception] = None
    recovered: bool = False
    recovery_action: Optional[str] = None


class ErrorRecoveryStrategy:
    """Стратегия восстановления после ошибки"""
    
    def __init__(self, name: str, can_recover: bool = True):
        self.name = name
        self.can_recover = can_recover
        self.recovery_attempts = 0
        self.max_attempts = 3
    
    def attempt_recovery(self, error: ErrorRecord) -> bool:
        """Попытка восстановления"""
        if not self.can_recover or self.recovery_attempts >= self.max_attempts:
            return False
        
        self.recovery_attempts += 1
        return self._perform_recovery(error)
    
    def _perform_recovery(self, error: ErrorRecord) -> bool:
        """Выполнить восстановление (переопределяется в подклассах)"""
        return False


class ResourceRecoveryStrategy(ErrorRecoveryStrategy):
    """Стратегия восстановления ресурсов"""
    
    def __init__(self):
        super().__init__("resource_recovery")
    
    def _perform_recovery(self, error: ErrorRecord) -> bool:
        try:
            # Попытка перезагрузки ресурса
            if "resource_path" in error.context.additional_data:
                from .resource_manager import resource_manager
                path = error.context.additional_data["resource_path"]
                resource_type = error.context.additional_data.get("resource_type", "image")
                
                # Очищаем кэш для этого ресурса
                resource_manager.clear_cache()
                
                # Пытаемся загрузить заново
                resource = resource_manager.get_resource(path, resource_type)
                if resource:
                    error.recovered = True
                    error.recovery_action = f"Resource reloaded: {path}"
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Ошибка восстановления ресурса: {e}")
            return False


class DatabaseRecoveryStrategy(ErrorRecoveryStrategy):
    """Стратегия восстановления базы данных"""
    
    def __init__(self):
        super().__init__("database_recovery")
    
    def _perform_recovery(self, error: ErrorRecord) -> bool:
        try:
            # Попытка переподключения к БД
            from .database_manager import DatabaseManager
            db_manager = DatabaseManager()
            
            # Проверяем соединение
            effects = db_manager.get_effects()
            if effects is not None:
                error.recovered = True
                error.recovery_action = "Database reconnected"
                return True
            
            return False
        except Exception as e:
            logger.error(f"Ошибка восстановления БД: {e}")
            return False


class ErrorHandler:
    """
    Централизованный обработчик ошибок с диагностикой и восстановлением.
    """
    
    def __init__(self):
        self.error_records: List[ErrorRecord] = []
        self.recovery_strategies: Dict[ErrorType, ErrorRecoveryStrategy] = {}
        self.error_callbacks: List[Callable[[ErrorRecord], None]] = []
        self._lock = threading.RLock()
        
        # Статистика
        self.stats = {
            'total_errors': 0,
            'recovered_errors': 0,
            'fatal_errors': 0,
            'errors_by_type': {},
            'errors_by_severity': {}
        }
        
        # Инициализация стратегий восстановления
        self._init_recovery_strategies()
        
        # Настройка логирования ошибок
        self._setup_error_logging()
        
        logger.info("ErrorHandler инициализирован")
    
    def _init_recovery_strategies(self) -> None:
        """Инициализация стратегий восстановления"""
        self.recovery_strategies[ErrorType.RESOURCE] = ResourceRecoveryStrategy()
        self.recovery_strategies[ErrorType.DATABASE] = DatabaseRecoveryStrategy()
    
    def _setup_error_logging(self) -> None:
        """Настройка логирования ошибок"""
        error_log_path = Path("logs/errors.log")
        error_log_path.parent.mkdir(exist_ok=True)
        
        error_handler = logging.FileHandler(error_log_path, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        error_handler.setFormatter(formatter)
        
        logger.addHandler(error_handler)
    
    def handle_error(self, error_type: ErrorType, message: str, 
                    severity: ErrorSeverity = ErrorSeverity.ERROR,
                    exception: Optional[Exception] = None,
                    additional_data: Optional[Dict[str, Any]] = None,
                    user_action: Optional[str] = None) -> ErrorRecord:
        """
        Обработать ошибку
        
        Args:
            error_type: Тип ошибки
            message: Сообщение об ошибке
            severity: Серьезность ошибки
            exception: Исключение (если есть)
            additional_data: Дополнительные данные
            user_action: Действие пользователя, вызвавшее ошибку
            
        Returns:
            Запись об ошибке
        """
        with self._lock:
            # Создаем контекст ошибки
            context = ErrorContext(
                stack_trace=traceback.format_exc(),
                additional_data=additional_data or {},
                user_action=user_action,
                system_state=self._get_system_state()
            )
            
            # Создаем запись об ошибке
            error_record = ErrorRecord(
                error_type=error_type,
                message=message,
                severity=severity,
                context=context,
                exception=exception
            )
            
            # Добавляем в список
            self.error_records.append(error_record)
            
            # Обновляем статистику
            self._update_stats(error_record)
            
            # Логируем ошибку
            self._log_error(error_record)
            
            # Пытаемся восстановиться
            if severity != ErrorSeverity.FATAL:
                self._attempt_recovery(error_record)
            
            # Вызываем колбэки
            self._notify_callbacks(error_record)
            
            # Критические ошибки
            if severity == ErrorSeverity.FATAL:
                self._handle_fatal_error(error_record)
            
            return error_record
    
    def _get_system_state(self) -> Dict[str, Any]:
        """Получить состояние системы"""
        import psutil
        import gc
        
        try:
            return {
                'memory_usage': psutil.virtual_memory().percent,
                'cpu_usage': psutil.cpu_percent(),
                'thread_count': threading.active_count(),
                'gc_objects': len(gc.get_objects()),
                'timestamp': time.time()
            }
        except Exception:
            return {'timestamp': time.time()}
    
    def _update_stats(self, error_record: ErrorRecord) -> None:
        """Обновить статистику"""
        self.stats['total_errors'] += 1
        
        # По типу
        error_type_str = error_record.error_type.value
        if error_type_str not in self.stats['errors_by_type']:
            self.stats['errors_by_type'][error_type_str] = 0
        self.stats['errors_by_type'][error_type_str] += 1
        
        # По серьезности
        severity_str = error_record.severity.value
        if severity_str not in self.stats['errors_by_severity']:
            self.stats['errors_by_severity'][severity_str] = 0
        self.stats['errors_by_severity'][severity_str] += 1
        
        # Фатальные ошибки
        if error_record.severity == ErrorSeverity.FATAL:
            self.stats['fatal_errors'] += 1
        
        # Восстановленные ошибки
        if error_record.recovered:
            self.stats['recovered_errors'] += 1
    
    def _log_error(self, error_record: ErrorRecord) -> None:
        """Логировать ошибку"""
        log_message = f"[{error_record.error_type.value.upper()}] {error_record.message}"
        
        if error_record.severity == ErrorSeverity.INFO:
            logger.info(log_message)
        elif error_record.severity == ErrorSeverity.WARNING:
            logger.warning(log_message)
        elif error_record.severity == ErrorSeverity.ERROR:
            logger.error(log_message)
        elif error_record.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
        elif error_record.severity == ErrorSeverity.FATAL:
            logger.critical(f"FATAL ERROR: {log_message}")
        
        # Дополнительная информация
        if error_record.exception:
            logger.error(f"Exception: {error_record.exception}")
        
        if error_record.context.stack_trace:
            logger.debug(f"Stack trace: {error_record.context.stack_trace}")
    
    def _attempt_recovery(self, error_record: ErrorRecord) -> None:
        """Попытка восстановления"""
        strategy = self.recovery_strategies.get(error_record.error_type)
        if strategy and strategy.attempt_recovery(error_record):
            logger.info(f"Восстановление после ошибки: {error_record.recovery_action}")
        else:
            logger.warning(f"Восстановление не удалось для ошибки типа {error_record.error_type.value}")
    
    def _notify_callbacks(self, error_record: ErrorRecord) -> None:
        """Уведомить колбэки об ошибке"""
        for callback in self.error_callbacks:
            try:
                callback(error_record)
            except Exception as e:
                logger.error(f"Ошибка в колбэке обработки ошибок: {e}")
    
    def _handle_fatal_error(self, error_record: ErrorRecord) -> None:
        """Обработка фатальной ошибки"""
        logger.critical("Обнаружена фатальная ошибка. Завершение работы...")
        
        # Сохраняем состояние
        self.save_error_report()
        
        # Уведомляем пользователя
        print(f"Критическая ошибка: {error_record.message}")
        print("Игра будет завершена. Проверьте лог ошибок для деталей.")
        
        # Завершаем работу
        sys.exit(1)
    
    def add_error_callback(self, callback: Callable[[ErrorRecord], None]) -> None:
        """Добавить колбэк для обработки ошибок"""
        with self._lock:
            self.error_callbacks.append(callback)
    
    def remove_error_callback(self, callback: Callable[[ErrorRecord], None]) -> None:
        """Удалить колбэк"""
        with self._lock:
            if callback in self.error_callbacks:
                self.error_callbacks.remove(callback)
    
    def get_recent_errors(self, count: int = 10) -> List[ErrorRecord]:
        """Получить последние ошибки"""
        with self._lock:
            return self.error_records[-count:] if self.error_records else []
    
    def get_errors_by_type(self, error_type: ErrorType) -> List[ErrorRecord]:
        """Получить ошибки по типу"""
        with self._lock:
            return [e for e in self.error_records if e.error_type == error_type]
    
    def get_errors_by_severity(self, severity: ErrorSeverity) -> List[ErrorRecord]:
        """Получить ошибки по серьезности"""
        with self._lock:
            return [e for e in self.error_records if e.severity == severity]
    
    def clear_errors(self) -> None:
        """Очистить историю ошибок"""
        with self._lock:
            self.error_records.clear()
            self.stats = {
                'total_errors': 0,
                'recovered_errors': 0,
                'fatal_errors': 0,
                'errors_by_type': {},
                'errors_by_severity': {}
            }
    
    def save_error_report(self, filename: Optional[str] = None) -> None:
        """Сохранить отчет об ошибках"""
        if filename is None:
            timestamp = int(time.time())
            filename = f"logs/error_report_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=== ОТЧЕТ ОБ ОШИБКАХ ===\n")
                f.write(f"Время создания: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Всего ошибок: {self.stats['total_errors']}\n")
                f.write(f"Восстановлено: {self.stats['recovered_errors']}\n")
                f.write(f"Фатальных: {self.stats['fatal_errors']}\n\n")
                
                f.write("=== ПОСЛЕДНИЕ ОШИБКИ ===\n")
                for error in self.get_recent_errors(20):
                    f.write(f"[{error.timestamp}] {error.error_type.value}: {error.message}\n")
                    if error.context.stack_trace:
                        f.write(f"Stack trace: {error.context.stack_trace}\n")
                    f.write("\n")
                
                f.write("=== СТАТИСТИКА ===\n")
                for error_type, count in self.stats['errors_by_type'].items():
                    f.write(f"{error_type}: {count}\n")
            
            logger.info(f"Отчет об ошибках сохранен: {filename}")
            
        except Exception as e:
            logger.error(f"Ошибка сохранения отчета: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику ошибок"""
        with self._lock:
            return self.stats.copy()
    
    def cleanup(self) -> None:
        """Очистка ресурсов"""
        self.save_error_report()
        self.clear_errors()
        logger.info("ErrorHandler очищен")


# Глобальный экземпляр обработчика ошибок
error_handler = ErrorHandler()


# Декоратор для автоматической обработки ошибок
def handle_errors(error_type: ErrorType = ErrorType.UNKNOWN, 
                 severity: ErrorSeverity = ErrorSeverity.ERROR):
    """Декоратор для автоматической обработки ошибок в функциях"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler.handle_error(
                    error_type=error_type,
                    message=f"Ошибка в функции {func.__name__}: {str(e)}",
                    severity=severity,
                    exception=e
                )
                raise
        return wrapper
    return decorator
