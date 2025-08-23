"""
Система состояний игры.
Определяет различные состояния, в которых может находиться игра.
"""

from enum import Enum, auto
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class GameState(Enum):
    """Состояния игры"""
    MAIN_MENU = auto()
    LOADING = auto()
    PLAYING = auto()
    PAUSED = auto()
    INVENTORY = auto()
    GENETICS = auto()
    EMOTIONS = auto()
    EVOLUTION = auto()
    SETTINGS = auto()
    LEVEL_STATISTICS = auto()
    NEXT_LEVEL = auto()
    GAME_OVER = auto()
    VICTORY = auto()
    SAVE_MENU = auto()
    LOAD_MENU = auto()


class GameStateManager:
    """Менеджер состояний игры"""
    
    def __init__(self):
        self.current_state = GameState.MAIN_MENU
        self.previous_state: Optional[GameState] = None
        self.state_stack: list = []
        
        # Данные состояний
        self.state_data: Dict[GameState, Dict[str, Any]] = {}
        
        # Обработчики переходов
        self.transition_handlers: Dict[tuple, callable] = {}
        
        logger.info("Менеджер состояний игры инициализирован")
    
    def change_state(self, new_state: GameState, data: Dict[str, Any] = None) -> bool:
        """Изменение состояния игры"""
        try:
            # Сохраняем предыдущее состояние
            self.previous_state = self.current_state
            
            # Сохраняем данные текущего состояния
            if data is not None:
                self.state_data[self.current_state] = data
            
            # Вызываем обработчик перехода
            transition_key = (self.current_state, new_state)
            if transition_key in self.transition_handlers:
                self.transition_handlers[transition_key](self.current_state, new_state)
            
            # Изменяем состояние
            self.current_state = new_state
            
            logger.info(f"Состояние игры изменено: {self.previous_state.name} -> {self.current_state.name}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка изменения состояния: {e}")
            return False
    
    def push_state(self, new_state: GameState, data: Dict[str, Any] = None) -> bool:
        """Добавление состояния в стек"""
        try:
            # Сохраняем текущее состояние в стеке
            self.state_stack.append((self.current_state, self.state_data.get(self.current_state, {})))
            
            # Сохраняем данные текущего состояния
            if data is not None:
                self.state_data[self.current_state] = data
            
            # Изменяем состояние
            self.previous_state = self.current_state
            self.current_state = new_state
            
            logger.info(f"Состояние добавлено в стек: {new_state.name}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления состояния в стек: {e}")
            return False
    
    def pop_state(self) -> bool:
        """Извлечение состояния из стека"""
        try:
            if not self.state_stack:
                logger.warning("Стек состояний пуст")
                return False
            
            # Восстанавливаем предыдущее состояние
            previous_state, previous_data = self.state_stack.pop()
            self.previous_state = self.current_state
            self.current_state = previous_state
            
            # Восстанавливаем данные
            if previous_data:
                self.state_data[previous_state] = previous_data
            
            logger.info(f"Состояние извлечено из стека: {self.current_state.name}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка извлечения состояния из стека: {e}")
            return False
    
    def register_transition_handler(self, from_state: GameState, to_state: GameState, handler: callable) -> None:
        """Регистрация обработчика перехода"""
        self.transition_handlers[(from_state, to_state)] = handler
        logger.info(f"Зарегистрирован обработчик перехода: {from_state.name} -> {to_state.name}")
    
    def get_current_state(self) -> GameState:
        """Получение текущего состояния"""
        return self.current_state
    
    def get_previous_state(self) -> Optional[GameState]:
        """Получение предыдущего состояния"""
        return self.previous_state
    
    def get_state_data(self, state: GameState) -> Dict[str, Any]:
        """Получение данных состояния"""
        return self.state_data.get(state, {})
    
    def set_state_data(self, state: GameState, data: Dict[str, Any]) -> None:
        """Установка данных состояния"""
        self.state_data[state] = data
    
    def is_in_state(self, state: GameState) -> bool:
        """Проверка, находится ли игра в указанном состоянии"""
        return self.current_state == state
    
    def is_in_any_state(self, states: list) -> bool:
        """Проверка, находится ли игра в одном из указанных состояний"""
        return self.current_state in states
    
    def can_transition_to(self, new_state: GameState) -> bool:
        """Проверка возможности перехода к состоянию"""
        # Здесь можно добавить логику проверки допустимых переходов
        return True
    
    def get_state_stack_size(self) -> int:
        """Получение размера стека состояний"""
        return len(self.state_stack)
    
    def clear_state_stack(self) -> None:
        """Очистка стека состояний"""
        self.state_stack.clear()
        logger.info("Стек состояний очищен")
    
    def reset_to_main_menu(self) -> None:
        """Сброс к главному меню"""
        self.current_state = GameState.MAIN_MENU
        self.previous_state = None
        self.state_stack.clear()
        self.state_data.clear()
        logger.info("Состояние игры сброшено к главному меню")
    
    def save_state_data(self, filepath: str) -> bool:
        """Сохранение данных состояний"""
        try:
            import json
            
            # Конвертируем в сериализуемый формат
            save_data = {
                "current_state": self.current_state.name,
                "previous_state": self.previous_state.name if self.previous_state else None,
                "state_data": {
                    state.name: data for state, data in self.state_data.items()
                }
            }
            
            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            logger.info(f"Данные состояний сохранены в {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения данных состояний: {e}")
            return False
    
    def load_state_data(self, filepath: str) -> bool:
        """Загрузка данных состояний"""
        try:
            import json
            
            with open(filepath, 'r') as f:
                save_data = json.load(f)
            
            # Восстанавливаем состояния
            self.current_state = GameState[save_data["current_state"]]
            self.previous_state = GameState[save_data["previous_state"]] if save_data["previous_state"] else None
            
            # Восстанавливаем данные
            self.state_data.clear()
            for state_name, data in save_data["state_data"].items():
                state = GameState[state_name]
                self.state_data[state] = data
            
            logger.info(f"Данные состояний загружены из {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка загрузки данных состояний: {e}")
            return False
