#!/usr/bin/env python3
"""Система логирования - централизованное управление логами
Обеспечивает детальное логирование всех систем игры"""

import logging
import logging.handlers
import os
import sys
import time
import json
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import threading
import queue
import atexit

class GameLogger:
    """Централизованная система логирования для игры"""
    
    def __init__(self, log_dir: str = "logs", max_log_size: int = 10 * 1024 * 1024, 
                 backup_count: int = 5, log_level: str = "INFO"):
        self.log_dir = Path(log_dir)
        self.max_log_size = max_log_size
        self.backup_count = backup_count
        self.log_level = getattr(logging, log_level.upper())
        
        # Создаем директорию для логов
        self.log_dir.mkdir(exist_ok=True)
        
        # Настройка логгеров
        self.loggers: Dict[str, logging.Logger] = {}
        self.log_queue = queue.Queue()
        self.async_logging = True
        
        # Инициализация основного логгера
        self._setup_main_logger()
        
        # Запуск асинхронного логирования
        if self.async_logging:
            self._start_async_logging()
        
        # Устанавливаем перехватчики исключений
        self._setup_exception_handlers()
        
        # Регистрируем функцию очистки при выходе
        atexit.register(self._cleanup)
        
        self.loggers["game"].info("GameLogger initialized successfully")
    
    def _setup_exception_handlers(self):
        """Установка перехватчиков исключений"""
        # Перехватываем необработанные исключения
        sys.excepthook = self._handle_uncaught_exception
        
        # Перехватываем исключения в потоках
        threading.excepthook = self._handle_thread_exception
        
        # Перехватываем KeyboardInterrupt
        import signal
        try:
            signal.signal(signal.SIGINT, self._handle_signal)
            signal.signal(signal.SIGTERM, self._handle_signal)
        except (AttributeError, OSError):
            pass  # Windows может не поддерживать некоторые сигналы
    
    def _handle_uncaught_exception(self, exc_type, exc_value, exc_traceback):
        """Обработка необработанных исключений"""
        if issubclass(exc_type, KeyboardInterrupt):
            # Игнорируем KeyboardInterrupt
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # Логируем исключение
        error_msg = f"UNCAUGHT EXCEPTION: {exc_type.__name__}: {exc_value}"
        self.loggers["game"].critical(error_msg)
        
        # Логируем полный traceback
        traceback_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        for line in traceback_lines:
            self.loggers["game"].critical(line.strip())
        
        # Выводим в консоль для немедленного отображения
        print(f"\n🚨 КРИТИЧЕСКАЯ ОШИБКА: {error_msg}")
        print("📋 Полный traceback записан в лог")
        
        # Вызываем стандартный обработчик
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    def _handle_thread_exception(self, args):
        """Обработка исключений в потоках"""
        if args.exc_type == KeyboardInterrupt:
            return
        
        error_msg = f"THREAD EXCEPTION in {args.thread.name}: {args.exc_type.__name__}: {args.exc_value}"
        self.loggers["game"].error(error_msg)
        
        # Логируем traceback
        if args.exc_traceback:
            traceback_lines = traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback)
            for line in traceback_lines:
                self.loggers["game"].error(line.strip())
        
        print(f"⚠️  ОШИБКА В ПОТОКЕ: {error_msg}")
    
    def _handle_signal(self, signum, frame):
        """Обработка сигналов"""
        signal_name = "SIGINT" if signum == 2 else "SIGTERM"
        self.loggers["game"].info(f"Получен сигнал {signal_name}, завершение работы...")
        print(f"\n🔄 Получен сигнал {signal_name}, завершение работы...")
    
    def _cleanup(self):
        """Очистка при выходе"""
        try:
            self.loggers["game"].info("GameLogger cleanup started")
            
            # Останавливаем асинхронное логирование
            if self.async_logging:
                self.log_queue.put(None)  # Сигнал остановки
                if hasattr(self, '_async_thread') and self._async_thread.is_alive():
                    self._async_thread.join(timeout=2)
            
            # Закрываем все обработчики
            for logger in self.loggers.values():
                for handler in logger.handlers[:]:
                    handler.close()
                    logger.removeHandler(handler)
            
            self.loggers["game"].info("GameLogger cleanup completed")
        except Exception as e:
            print(f"Ошибка при очистке GameLogger: {e}")
    
    def _setup_main_logger(self):
        """Настройка основного логгера"""
        # Основной логгер
        main_logger = logging.getLogger("game")
        main_logger.setLevel(self.log_level)
        
        # Форматтер
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Файловый обработчик
        log_file = self.log_dir / f"game_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.max_log_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        
        # Консольный обработчик
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(formatter)
        
        # Добавляем обработчики
        main_logger.addHandler(file_handler)
        main_logger.addHandler(console_handler)
        
        self.loggers["game"] = main_logger
    
    def _start_async_logging(self):
        """Запуск асинхронного логирования"""
        def async_logger():
            while True:
                try:
                    log_entry = self.log_queue.get(timeout=1)
                    if log_entry is None:  # Сигнал остановки
                        break
                    
                    logger_name = log_entry["logger"]
                    level = log_entry["level"]
                    message = log_entry["message"]
                    extra = log_entry.get("extra", {})
                    
                    if logger_name not in self.loggers:
                        self._create_logger(logger_name)
                    
                    logger_obj = self.loggers[logger_name]
                    logger_obj.log(level, message, extra=extra)
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Error in async logging: {e}")
        
        self._async_thread = threading.Thread(target=async_logger, daemon=True)
        self._async_thread.start()
    
    def _create_logger(self, name: str) -> logging.Logger:
        """Создание логгера для конкретной системы"""
        logger_obj = logging.getLogger(f"game.{name}")
        logger_obj.setLevel(self.log_level)
        
        # Форматтер
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Файловый обработчик для системы
        log_file = self.log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.max_log_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        
        # Добавляем обработчик
        logger_obj.addHandler(file_handler)
        
        self.loggers[name] = logger_obj
        return logger_obj
    
    def get_logger(self, name: str) -> logging.Logger:
        """Получение логгера для системы"""
        if name not in self.loggers:
            return self._create_logger(name)
        return self.loggers[name]
    
    def log_system_event(self, system: str, event: str, details: Dict[str, Any] = None, 
                        level: str = "INFO"):
        """Логирование системного события"""
        log_entry = {
            "logger": system,
            "level": getattr(logging, level.upper()),
            "message": f"SYSTEM_EVENT: {event}",
            "extra": {
                "event_type": "system_event",
                "event": event,
                "details": details or {},
                "timestamp": time.time()
            }
        }
        
        if self.async_logging:
            self.log_queue.put(log_entry)
        else:
            logger_obj = self.get_logger(system)
            logger_obj.log(log_entry["level"], log_entry["message"], extra=log_entry["extra"])
    
    def log_error(self, system: str, error: Exception, context: Dict[str, Any] = None):
        """Логирование ошибки"""
        error_details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {},
            "timestamp": time.time()
        }
        
        log_entry = {
            "logger": system,
            "level": logging.ERROR,
            "message": f"ERROR: {error}",
            "extra": {
                "event_type": "error",
                "error_details": error_details
            }
        }
        
        if self.async_logging:
            self.log_queue.put(log_entry)
        else:
            logger_obj = self.get_logger(system)
            logger_obj.log(log_entry["level"], log_entry["message"], extra=log_entry["extra"])
    
    def log_performance(self, system: str, operation: str, duration: float, 
                       details: Dict[str, Any] = None):
        """Логирование производительности"""
        perf_details = {
            "operation": operation,
            "duration": duration,
            "details": details or {},
            "timestamp": time.time()
        }
        
        log_entry = {
            "logger": system,
            "level": logging.DEBUG,
            "message": f"PERFORMANCE: {operation} took {duration:.4f}s",
            "extra": {
                "event_type": "performance",
                "performance_details": perf_details
            }
        }
        
        if self.async_logging:
            self.log_queue.put(log_entry)
        else:
            logger_obj = self.get_logger(system)
            logger_obj.log(log_entry["level"], log_entry["message"], extra=log_entry["extra"])
    
    def log_critical_error(self, system: str, error: Exception, context: Dict[str, Any] = None):
        """Логирование критической ошибки с немедленным выводом"""
        error_details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {},
            "timestamp": time.time()
        }
        
        # Немедленно выводим в консоль
        print(f"\n🚨 КРИТИЧЕСКАЯ ОШИБКА в системе {system}:")
        print(f"   Тип: {error_details['error_type']}")
        print(f"   Сообщение: {error_details['error_message']}")
        print(f"   Traceback: {error_details['traceback']}")
        
        # Логируем в файл
        log_entry = {
            "logger": system,
            "level": logging.CRITICAL,
            "message": f"CRITICAL ERROR: {error}",
            "extra": {
                "event_type": "critical_error",
                "error_details": error_details
            }
        }
        
        if self.async_logging:
            self.log_queue.put(log_entry)
        else:
            logger_obj = self.get_logger(system)
            logger_obj.log(log_entry["level"], log_entry["message"], extra=log_entry["extra"])
    
    def log_warning(self, system: str, warning: str, context: Dict[str, Any] = None):
        """Логирование предупреждения"""
        warning_details = {
            "warning_message": warning,
            "context": context or {},
            "timestamp": time.time()
        }
        
        log_entry = {
            "logger": system,
            "level": logging.WARNING,
            "message": f"WARNING: {warning}",
            "extra": {
                "event_type": "warning",
                "warning_details": warning_details
            }
        }
        
        if self.async_logging:
            self.log_queue.put(log_entry)
        else:
            logger_obj = self.get_logger(system)
            logger_obj.log(log_entry["level"], log_entry["message"], extra=log_entry["extra"])
    
    def log_user_action(self, user_id: str, action: str, details: Dict[str, Any] = None):
        """Логирование действий пользователя"""
        action_details = {
            "user_id": user_id,
            "action": action,
            "details": details or {},
            "timestamp": time.time()
        }
        
        log_entry = {
            "logger": "user_actions",
            "level": logging.INFO,
            "message": f"USER_ACTION: {user_id} - {action}",
            "extra": {
                "event_type": "user_action",
                "action_details": action_details
            }
        }
        
        if self.async_logging:
            self.log_queue.put(log_entry)
        else:
            logger_obj = self.get_logger("user_actions")
            logger_obj.log(log_entry["level"], log_entry["message"], extra=log_entry["extra"])
    
    def log_game_state(self, system: str, state: str, data: Dict[str, Any] = None):
        """Логирование состояния игры"""
        state_details = {
            "state": state,
            "data": data or {},
            "timestamp": time.time()
        }
        
        log_entry = {
            "logger": system,
            "level": logging.INFO,
            "message": f"STATE_CHANGE: {state}",
            "extra": {
                "event_type": "state_change",
                "state_details": state_details
            }
        }
        
        if self.async_logging:
            self.log_queue.put(log_entry)
        else:
            logger_obj = self.get_logger(system)
            logger_obj.log(log_entry["level"], log_entry["message"], extra=log_entry["extra"])
    
    def log_ai_decision(self, ai_id: str, decision: str, reasoning: Dict[str, Any] = None):
        """Логирование решений ИИ"""
        decision_details = {
            "ai_id": ai_id,
            "decision": decision,
            "reasoning": reasoning or {},
            "timestamp": time.time()
        }
        
        log_entry = {
            "logger": "ai_system",
            "level": logging.DEBUG,
            "message": f"AI_DECISION: {ai_id} - {decision}",
            "extra": {
                "event_type": "ai_decision",
                "decision_details": decision_details
            }
        }
        
        if self.async_logging:
            self.log_queue.put(log_entry)
        else:
            logger_obj = self.get_logger("ai_system")
            logger_obj.log(log_entry["level"], log_entry["message"], extra=log_entry["extra"])
    
    def log_memory_event(self, entity_id: str, memory_type: str, action: str, 
                        details: Dict[str, Any] = None):
        """Логирование событий памяти"""
        memory_details = {
            "entity_id": entity_id,
            "memory_type": memory_type,
            "action": action,
            "details": details or {},
            "timestamp": time.time()
        }
        
        log_entry = {
            "logger": "memory_system",
            "level": logging.DEBUG,
            "message": f"MEMORY_EVENT: {entity_id} - {memory_type} - {action}",
            "extra": {
                "event_type": "memory_event",
                "memory_details": memory_details
            }
        }
        
        if self.async_logging:
            self.log_queue.put(log_entry)
        else:
            logger_obj = self.get_logger("memory_system")
            logger_obj.log(log_entry["level"], log_entry["message"], extra=log_entry["extra"])
    
    def log_combat_event(self, attacker_id: str, target_id: str, action: str, 
                        damage: float = None, details: Dict[str, Any] = None):
        """Логирование боевых событий"""
        combat_details = {
            "attacker_id": attacker_id,
            "target_id": target_id,
            "action": action,
            "damage": damage,
            "details": details or {},
            "timestamp": time.time()
        }
        
        log_entry = {
            "logger": "combat_system",
            "level": logging.INFO,
            "message": f"COMBAT: {attacker_id} -> {target_id} - {action}",
            "extra": {
                "event_type": "combat_event",
                "combat_details": combat_details
            }
        }
        
        if self.async_logging:
            self.log_queue.put(log_entry)
        else:
            logger_obj = self.get_logger("combat_system")
            logger_obj.log(log_entry["level"], log_entry["message"], extra=log_entry["extra"])
    
    def log_inventory_event(self, entity_id: str, action: str, item_id: str = None,
                           quantity: int = None, details: Dict[str, Any] = None):
        """Логирование событий инвентаря"""
        inventory_details = {
            "entity_id": entity_id,
            "action": action,
            "item_id": item_id,
            "quantity": quantity,
            "details": details or {},
            "timestamp": time.time()
        }
        
        log_entry = {
            "logger": "inventory_system",
            "level": logging.INFO,
            "message": f"INVENTORY: {entity_id} - {action}",
            "extra": {
                "event_type": "inventory_event",
                "inventory_details": inventory_details
            }
        }
        
        if self.async_logging:
            self.log_queue.put(log_entry)
        else:
            logger_obj = self.get_logger("inventory_system")
            logger_obj.log(log_entry["level"], log_entry["message"], extra=log_entry["extra"])
    
    def log_content_generation(self, session_id: str, content_type: str, 
                              generation_time: float, details: Dict[str, Any] = None):
        """Логирование генерации контента"""
        generation_details = {
            "session_id": session_id,
            "content_type": content_type,
            "generation_time": generation_time,
            "details": details or {},
            "timestamp": time.time()
        }
        
        log_entry = {
            "logger": "content_generator",
            "level": logging.INFO,
            "message": f"CONTENT_GENERATION: {session_id} - {content_type}",
            "extra": {
                "event_type": "content_generation",
                "generation_details": generation_details
            }
        }
        
        if self.async_logging:
            self.log_queue.put(log_entry)
        else:
            logger_obj = self.get_logger("content_generator")
            logger_obj.log(log_entry["level"], log_entry["message"], extra=log_entry["extra"])
    
    def export_logs(self, output_file: str, start_time: float = None, end_time: float = None,
                   systems: List[str] = None, event_types: List[str] = None):
        """Экспорт логов в файл"""
        try:
            exported_logs = []
            
            for log_file in self.log_dir.glob("*.log"):
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            # Парсим строку лога
                            parts = line.strip().split(' - ', 3)
                            if len(parts) >= 4:
                                timestamp_str, logger_name, level, message = parts
                                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S').timestamp()
                                
                                # Фильтрация по времени
                                if start_time and timestamp < start_time:
                                    continue
                                if end_time and timestamp > end_time:
                                    continue
                                
                                # Фильтрация по системам
                                if systems and not any(system in logger_name for system in systems):
                                    continue
                                
                                exported_logs.append({
                                    "timestamp": timestamp,
                                    "logger": logger_name,
                                    "level": level,
                                    "message": message
                                })
                        except Exception as e:
                            print(f"Error parsing log line: {e}")
            
            # Сортировка по времени
            exported_logs.sort(key=lambda x: x["timestamp"])
            
            # Сохранение в файл
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(exported_logs, f, indent=2, ensure_ascii=False)
            
            self.loggers["game"].info(f"Exported {len(exported_logs)} log entries to {output_file}")
            
        except Exception as e:
            self.loggers["game"].error(f"Failed to export logs: {e}")
    
    def cleanup_old_logs(self, max_age_days: int = 30):
        """Очистка старых логов"""
        try:
            cutoff_time = time.time() - (max_age_days * 24 * 3600)
            deleted_files = 0
            
            for log_file in self.log_dir.glob("*.log"):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    deleted_files += 1
            
            self.loggers["game"].info(f"Cleaned up {deleted_files} old log files")
            
        except Exception as e:
            self.loggers["game"].error(f"Failed to cleanup old logs: {e}")
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Получение статистики логов"""
        try:
            stats = {
                "total_log_files": 0,
                "total_log_entries": 0,
                "systems": {},
                "levels": {},
                "recent_errors": []
            }
            
            for log_file in self.log_dir.glob("*.log"):
                stats["total_log_files"] += 1
                
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        stats["total_log_entries"] += 1
                        
                        try:
                            parts = line.strip().split(' - ', 3)
                            if len(parts) >= 4:
                                logger_name, level = parts[1], parts[2]
                                
                                # Статистика по системам
                                if logger_name not in stats["systems"]:
                                    stats["systems"][logger_name] = 0
                                stats["systems"][logger_name] += 1
                                
                                # Статистика по уровням
                                if level not in stats["levels"]:
                                    stats["levels"][level] = 0
                                stats["levels"][level] += 1
                                
                                # Последние ошибки
                                if level == "ERROR" and len(stats["recent_errors"]) < 10:
                                    stats["recent_errors"].append(line.strip())
                        except:
                            pass
            
            return stats
            
        except Exception as e:
            self.loggers["game"].error(f"Failed to get log stats: {e}")
            return {}
    
    def shutdown(self):
        """Завершение работы системы логирования"""
        if self.async_logging:
            self.log_queue.put(None)  # Сигнал остановки
            if hasattr(self, '_async_thread') and self._async_thread.is_alive():
                self._async_thread.join(timeout=5)
        
        # Закрываем все обработчики
        for logger_obj in self.loggers.values():
            for handler in logger_obj.handlers[:]:
                handler.close()
                logger_obj.removeHandler(handler)
        
        self.loggers["game"].info("GameLogger shutdown completed")

# Глобальный экземпляр системы логирования
game_logger = None

def initialize_logging(log_dir: str = "logs", log_level: str = "INFO") -> GameLogger:
    """Инициализация системы логирования"""
    global game_logger
    game_logger = GameLogger(log_dir, log_level=log_level)
    return game_logger

def get_logger(name: str) -> logging.Logger:
    """Получение логгера"""
    if game_logger is None:
        initialize_logging()
    return game_logger.get_logger(name)

def log_system_event(system: str, event: str, details: Dict[str, Any] = None, level: str = "INFO"):
    """Логирование системного события"""
    if game_logger is None:
        initialize_logging()
    game_logger.log_system_event(system, event, details, level)

def log_error(system: str, error: Exception, context: Dict[str, Any] = None):
    """Логирование ошибки"""
    if game_logger is None:
        initialize_logging()
    game_logger.log_error(system, error, context)

def log_performance(system: str, operation: str, duration: float, details: Dict[str, Any] = None):
    """Логирование производительности"""
    if game_logger is None:
        initialize_logging()
    game_logger.log_performance(system, operation, duration, details)

def log_critical_error(system: str, error: Exception, context: Dict[str, Any] = None):
    """Логирование критической ошибки"""
    if game_logger is None:
        initialize_logging()
    game_logger.log_critical_error(system, error, context)

def log_warning(system: str, warning: str, context: Dict[str, Any] = None):
    """Логирование предупреждения"""
    if game_logger is None:
        initialize_logging()
    game_logger.log_warning(system, warning, context)
