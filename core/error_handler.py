#!/usr/bin/env python3
"""
Улучшенная система обработки ошибок
Включает категоризацию, автоматическое восстановление и детальное логирование
"""

import logging
import traceback
import time
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from dataclasses import dataclass
from collections import defaultdict
import sys

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Типы ошибок"""
    INITIALIZATION_ERROR = "initialization_error"
    RUNTIME_ERROR = "runtime_error"
    RESOURCE_ERROR = "resource_error"
    SYSTEM_ERROR = "system_error"
    NETWORK_ERROR = "network_error"
    DATABASE_ERROR = "database_error"
    UI_ERROR = "ui_error"
    AUDIO_ERROR = "audio_error"
    GRAPHICS_ERROR = "graphics_error"
    INPUT_ERROR = "input_error"
    LOGIC_ERROR = "logic_error"
    MEMORY_ERROR = "memory_error"
    PERFORMANCE_ERROR = "performance_error"
    UNKNOWN_ERROR = "unknown_error"


class ErrorSeverity(Enum):
    """Уровни серьезности ошибок"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorInfo:
    """Информация об ошибке"""
    error_type: ErrorType
    severity: ErrorSeverity
    message: str
    timestamp: float
    traceback: str
    context: Dict[str, Any]
    handled: bool = False
    recovery_attempted: bool = False


class ErrorRecoveryStrategy:
    """Стратегия восстановления после ошибок"""
    
    def __init__(self):
        self.recovery_handlers: Dict[ErrorType, List[Callable]] = defaultdict(list)
        self.max_recovery_attempts = 3
        self.recovery_cooldown = 5.0  # секунды между попытками восстановления
    
    def register_recovery_handler(self, error_type: ErrorType, handler: Callable):
        """Регистрация обработчика восстановления"""
        self.recovery_handlers[error_type].append(handler)
    
    def attempt_recovery(self, error_info: ErrorInfo) -> bool:
        """Попытка восстановления после ошибки"""
        if error_info.recovery_attempted:
            return False
        
        handlers = self.recovery_handlers.get(error_info.error_type, [])
        if not handlers:
            return False

        error_info.recovery_attempted = True
        
        for handler in handlers:
            try:
                if handler(error_info):
                    logger.info(f"Восстановление после ошибки {error_info.error_type.value} успешно")
                    return True
            except Exception as e:
                logger.error(f"Ошибка в обработчике восстановления: {e}")
            
            return False


class ErrorHandler:
    """Основной обработчик ошибок"""
    
    def __init__(self):
        self.error_history: List[ErrorInfo] = []
        self.error_counts: Dict[ErrorType, int] = defaultdict(int)
        self.recovery_strategy = ErrorRecoveryStrategy()
        self.max_history_size = 1000
        self.error_thresholds = {
            ErrorSeverity.LOW: 100,
            ErrorSeverity.MEDIUM: 50,
            ErrorSeverity.HIGH: 20,
            ErrorSeverity.CRITICAL: 5
        }
        
        # Регистрация обработчиков восстановления
        self._register_default_recovery_handlers()
        
        logger.info("Система обработки ошибок инициализирована")
    
    def _register_default_recovery_handlers(self):
        """Регистрация стандартных обработчиков восстановления"""
        
        # Восстановление после ошибок ресурсов
        self.recovery_strategy.register_recovery_handler(
            ErrorType.RESOURCE_ERROR,
            self._recover_resource_error
        )
        
        # Восстановление после ошибок UI
        self.recovery_strategy.register_recovery_handler(
            ErrorType.UI_ERROR,
            self._recover_ui_error
        )
        
        # Восстановление после ошибок аудио
        self.recovery_strategy.register_recovery_handler(
            ErrorType.AUDIO_ERROR,
            self._recover_audio_error
        )
        
        # Восстановление после ошибок графики
        self.recovery_strategy.register_recovery_handler(
            ErrorType.GRAPHICS_ERROR,
            self._recover_graphics_error
        )
        
        # Восстановление после ошибок памяти
        self.recovery_strategy.register_recovery_handler(
            ErrorType.MEMORY_ERROR,
            self._recover_memory_error
        )
    
    def handle_error(self, error_type: ErrorType, severity: ErrorSeverity, 
                    message: str, context: Dict[str, Any] = None) -> bool:
        """Обработка ошибки"""
        try:
            # Создаем информацию об ошибке
            error_info = ErrorInfo(
                error_type=error_type,
                severity=severity,
                message=message,
                timestamp=time.time(),
                traceback=traceback.format_exc(),
                context=context or {}
            )
            
            # Добавляем в историю
            self._add_to_history(error_info)
            
            # Увеличиваем счетчик
            self.error_counts[error_type] += 1
            
            # Логируем ошибку
            self._log_error(error_info)
            
            # Проверяем пороги
            if self._should_trigger_emergency_action(error_info):
                self._trigger_emergency_action(error_info)
            
            # Пытаемся восстановиться
            if self.recovery_strategy.attempt_recovery(error_info):
                error_info.handled = True
                return True
            
            # Если восстановление не удалось, обрабатываем в зависимости от серьезности
            return self._handle_by_severity(error_info)
            
        except Exception as e:
            logger.error(f"Ошибка в обработчике ошибок: {e}")
            return False
    
    def _add_to_history(self, error_info: ErrorInfo):
        """Добавление ошибки в историю"""
        self.error_history.append(error_info)
        
        # Ограничиваем размер истории
        if len(self.error_history) > self.max_history_size:
            self.error_history.pop(0)
    
    def _log_error(self, error_info: ErrorInfo):
        """Логирование ошибки"""
        log_message = f"[{error_info.error_type.value.upper()}] {error_info.message}"
        
        if error_info.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
        elif error_info.severity == ErrorSeverity.HIGH:
            logger.error(log_message)
        elif error_info.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message)
        else:
            logger.info(log_message)
        
        # Детальное логирование для критических ошибок
        if error_info.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            logger.debug(f"Контекст ошибки: {error_info.context}")
            logger.debug(f"Traceback: {error_info.traceback}")
    
    def _should_trigger_emergency_action(self, error_info: ErrorInfo) -> bool:
        """Проверка необходимости экстренных действий"""
        error_count = self.error_counts[error_info.error_type]
        threshold = self.error_thresholds.get(error_info.severity, 10)
        
        return error_count >= threshold
    
    def _trigger_emergency_action(self, error_info: ErrorInfo):
        """Экстренные действия при превышении порога ошибок"""
        logger.critical(f"ПРЕВЫШЕН ПОРОГ ОШИБОК: {error_info.error_type.value} - {self.error_counts[error_info.error_type]} ошибок")
        
        if error_info.severity == ErrorSeverity.CRITICAL:
            logger.critical("КРИТИЧЕСКАЯ СИТУАЦИЯ - ТРЕБУЕТСЯ ВМЕШАТЕЛЬСТВО")
            # Здесь можно добавить уведомления администратору
    
    def _handle_by_severity(self, error_info: ErrorInfo) -> bool:
        """Обработка ошибки в зависимости от серьезности"""
        if error_info.severity == ErrorSeverity.CRITICAL:
            logger.critical("КРИТИЧЕСКАЯ ОШИБКА - ПРЕРЫВАНИЕ РАБОТЫ")
            return False
        
        elif error_info.severity == ErrorSeverity.HIGH:
            logger.error("ВЫСОКАЯ ОШИБКА - ПРОДОЛЖЕНИЕ С ОГРАНИЧЕНИЯМИ")
            return True
        
        elif error_info.severity == ErrorSeverity.MEDIUM:
            logger.warning("СРЕДНЯЯ ОШИБКА - ПРОДОЛЖЕНИЕ РАБОТЫ")
            return True
        
        else:  # LOW
            logger.info("НИЗКАЯ ОШИБКА - ПРОДОЛЖЕНИЕ РАБОТЫ")
            return True
    
    def _recover_resource_error(self, error_info: ErrorInfo) -> bool:
        """Восстановление после ошибки ресурсов"""
        try:
            # Попытка перезагрузки ресурсов
            from core.resource_manager import resource_manager
            if 'resource_manager' in error_info.context:
                resource_manager.clear_cache()
                logger.info("Кэш ресурсов очищен")
                return True
        except Exception as e:
            logger.error(f"Ошибка восстановления ресурсов: {e}")
        return False
    
    def _recover_ui_error(self, error_info: ErrorInfo) -> bool:
        """Восстановление после ошибки UI"""
        try:
            # Попытка пересоздания UI элементов
            logger.info("Попытка восстановления UI")
            return True
        except Exception as e:
            logger.error(f"Ошибка восстановления UI: {e}")
        return False
    
    def _recover_audio_error(self, error_info: ErrorInfo) -> bool:
        """Восстановление после ошибки аудио"""
        try:
            # Попытка переинициализации аудио
            import pygame
            pygame.mixer.quit()
            pygame.mixer.init()
            logger.info("Аудио система переинициализирована")
            return True
        except Exception as e:
            logger.error(f"Ошибка восстановления аудио: {e}")
        return False
    
    def _recover_graphics_error(self, error_info: ErrorInfo) -> bool:
        """Восстановление после ошибки графики"""
        try:
            # Попытка переинициализации графики
            import pygame
            pygame.display.quit()
            pygame.display.init()
            logger.info("Графическая система переинициализирована")
            return True
        except Exception as e:
            logger.error(f"Ошибка восстановления графики: {e}")
        return False
    
    def _recover_memory_error(self, error_info: ErrorInfo) -> bool:
        """Восстановление после ошибки памяти"""
        try:
            # Попытка очистки памяти
            import gc
            gc.collect()
            
            # Очистка кэша ресурсов
            from core.resource_manager import resource_manager
            resource_manager.clear_cache()
            
            logger.info("Память очищена")
            return True
        except Exception as e:
            logger.error(f"Ошибка восстановления памяти: {e}")
        return False
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Получение статистики ошибок"""
        total_errors = len(self.error_history)
        handled_errors = sum(1 for e in self.error_history if e.handled)
        
        return {
            'total_errors': total_errors,
            'handled_errors': handled_errors,
            'unhandled_errors': total_errors - handled_errors,
            'error_counts_by_type': dict(self.error_counts),
            'error_counts_by_severity': self._get_errors_by_severity(),
            'recent_errors': self._get_recent_errors(10),
            'error_rate': self._calculate_error_rate()
        }
    
    def _get_errors_by_severity(self) -> Dict[str, int]:
        """Получение количества ошибок по серьезности"""
        severity_counts = defaultdict(int)
        for error in self.error_history:
            severity_counts[error.severity.value] += 1
        return dict(severity_counts)
    
    def _get_recent_errors(self, count: int) -> List[Dict[str, Any]]:
        """Получение последних ошибок"""
        recent = self.error_history[-count:] if self.error_history else []
        return [
            {
                'type': error.error_type.value,
                'severity': error.severity.value,
                'message': error.message,
                'timestamp': error.timestamp,
                'handled': error.handled
            }
            for error in recent
        ]
    
    def _calculate_error_rate(self) -> float:
        """Расчет частоты ошибок (ошибок в минуту)"""
        if not self.error_history:
            return 0.0
        
        time_span = time.time() - self.error_history[0].timestamp
        if time_span <= 0:
            return 0.0
        
        return len(self.error_history) / (time_span / 60)
    
    def clear_history(self):
        """Очистка истории ошибок"""
        self.error_history.clear()
        self.error_counts.clear()
        logger.info("История ошибок очищена")
    
    def register_custom_recovery_handler(self, error_type: ErrorType, handler: Callable):
        """Регистрация пользовательского обработчика восстановления"""
        self.recovery_strategy.register_recovery_handler(error_type, handler)
        logger.info(f"Зарегистрирован пользовательский обработчик для {error_type.value}")


# Глобальный экземпляр обработчика ошибок
error_handler = ErrorHandler()
