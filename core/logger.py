import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

class GameLogger:
    """Enhanced logging system for the game"""
    
    def __init__(self, name: str = "ZeldaGame", log_file: str = "logs/game.log"):
        self.name = name
        self.log_file = Path(log_file)
        self.logger = None
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """Setup the logger with proper configuration"""
        # Create logs directory if it doesn't exist
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_file,
            maxBytes=1024*1024,  # 1MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str) -> None:
        """Log debug message"""
        if self.logger:
            self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """Log info message"""
        if self.logger:
            self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message"""
        if self.logger:
            self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log error message"""
        if self.logger:
            self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """Log critical message"""
        if self.logger:
            self.logger.critical(message)
    
    def exception(self, message: str) -> None:
        """Log exception with traceback"""
        if self.logger:
            self.logger.exception(message)
    
    def log_performance(self, fps: float, frame_time: float, memory_usage: Optional[float] = None) -> None:
        """Log performance metrics"""
        perf_msg = f"FPS: {fps:.1f}, Frame Time: {frame_time:.2f}ms"
        if memory_usage:
            perf_msg += f", Memory: {memory_usage:.1f}MB"
        self.debug(perf_msg)
    
    def log_game_event(self, event_type: str, event_data: dict) -> None:
        """Log game events"""
        self.info(f"Game Event: {event_type} - {event_data}")
    
    def log_error_with_context(self, error: Exception, context: str) -> None:
        """Log error with additional context"""
        self.error(f"Error in {context}: {str(error)}")
        self.exception(f"Exception details for {context}")
    
    def cleanup(self) -> None:
        """Cleanup logger resources"""
        if self.logger:
            for handler in self.logger.handlers[:]:
                handler.close()
                self.logger.removeHandler(handler)

# Global logger instance
_game_logger: Optional[GameLogger] = None

def init_logger(name: str = "ZeldaGame", log_file: str = "logs/game.log") -> GameLogger:
    """Initialize the global logger"""
    global _game_logger
    if _game_logger is None:
        _game_logger = GameLogger(name, log_file)
    return _game_logger

def get_logger() -> GameLogger:
    """Get the global logger instance"""
    global _game_logger
    if _game_logger is None:
        _game_logger = GameLogger()
    return _game_logger

def cleanup_logger() -> None:
    """Cleanup the global logger"""
    global _game_logger
    if _game_logger:
        _game_logger.cleanup()
        _game_logger = None
