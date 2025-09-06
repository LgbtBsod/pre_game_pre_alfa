#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
МЕНЕДЖЕР ИГРОВЫХ СОСТОЯНИЙ
Централизованное управление всеми состояниями игры
Соблюдает принцип единой ответственности
"""

import time
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

from utils.logging_system import get_logger, log_system_event

class GameState(Enum):
    """Состояния игры"""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    SETTINGS = "settings"
    INVENTORY = "inventory"
    DIALOGUE = "dialogue"
    COMBAT = "combat"
    DEATH = "death"
    LOADING = "loading"
    SAVING = "saving"

class StateTransition(Enum):
    """Переходы между состояниями"""
    ENTER = "enter"
    EXIT = "exit"
    PAUSE = "pause"
    RESUME = "resume"

@dataclass
class StateData:
    """Данные состояния"""
    state: GameState
    start_time: float
    duration: float = 0.0
    data: Dict[str, Any] = None
    is_active: bool = False

class GameStateManager:
    """Менеджер игровых состояний"""
    
    def __init__(self, save_directory: str = "saves"):
        self.save_directory = Path(save_directory)
        self.save_directory.mkdir(parents=True, exist_ok=True)
        
        self.current_state: Optional[GameState] = None
        self.previous_state: Optional[GameState] = None
        self.state_history: List[GameState] = []
        self.state_data: Dict[GameState, StateData] = {}
        
        # Callbacks для состояний
        self.state_callbacks: Dict[GameState, Dict[StateTransition, List[Callable]]] = {}
        
        # Настройки
        self.max_history_size = 50
        self.auto_save_interval = 30.0  # Автосохранение каждые 30 секунд
        self.last_auto_save = time.time()
        
        self.logger = get_logger("game_state_manager")
        
        # Инициализация состояний
        self._initialize_states()
        
        log_system_event("game_state_manager", "initialized")
    
    def _initialize_states(self):
        """Инициализация всех состояний"""
        for state in GameState:
            self.state_data[state] = StateData(
                state=state,
                start_time=0.0,
                data={}
            )
            self.state_callbacks[state] = {
                StateTransition.ENTER: [],
                StateTransition.EXIT: [],
                StateTransition.PAUSE: [],
                StateTransition.RESUME: []
            }
    
    def change_state(self, new_state: GameState, data: Optional[Dict[str, Any]] = None) -> bool:
        """Изменение состояния игры"""
        if new_state == self.current_state:
            return True
        
        try:
            # Выход из текущего состояния
            if self.current_state:
                self._exit_state(self.current_state)
            
            # Сохранение предыдущего состояния
            self.previous_state = self.current_state
            
            # Вход в новое состояние
            self.current_state = new_state
            self._enter_state(new_state, data)
            
            # Добавление в историю
            self.state_history.append(new_state)
            if len(self.state_history) > self.max_history_size:
                self.state_history.pop(0)
            
            log_system_event("game_state_manager", "state_changed", {
                "from": self.previous_state.value if self.previous_state else None,
                "to": new_state.value,
                "data": data
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка изменения состояния: {e}")
            return False
    
    def pause_state(self) -> bool:
        """Пауза текущего состояния"""
        if not self.current_state:
            return False
        
        try:
            self._pause_state(self.current_state)
            log_system_event("game_state_manager", "state_paused", {
                "state": self.current_state.value
            })
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка паузы состояния: {e}")
            return False
    
    def resume_state(self) -> bool:
        """Возобновление текущего состояния"""
        if not self.current_state:
            return False
        
        try:
            self._resume_state(self.current_state)
            log_system_event("game_state_manager", "state_resumed", {
                "state": self.current_state.value
            })
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка возобновления состояния: {e}")
            return False
    
    def _enter_state(self, state: GameState, data: Optional[Dict[str, Any]] = None):
        """Вход в состояние"""
        state_data = self.state_data[state]
        state_data.start_time = time.time()
        state_data.is_active = True
        state_data.duration = 0.0
        
        if data:
            state_data.data.update(data)
        
        # Вызов callbacks
        for callback in self.state_callbacks[state][StateTransition.ENTER]:
            try:
                callback(state, data)
            except Exception as e:
                self.logger.error(f"Ошибка в callback входа в состояние {state.value}: {e}")
    
    def _exit_state(self, state: GameState):
        """Выход из состояния"""
        state_data = self.state_data[state]
        state_data.duration = time.time() - state_data.start_time
        state_data.is_active = False
        
        # Вызов callbacks
        for callback in self.state_callbacks[state][StateTransition.EXIT]:
            try:
                callback(state, state_data.data)
            except Exception as e:
                self.logger.error(f"Ошибка в callback выхода из состояния {state.value}: {e}")
    
    def _pause_state(self, state: GameState):
        """Пауза состояния"""
        # Вызов callbacks
        for callback in self.state_callbacks[state][StateTransition.PAUSE]:
            try:
                callback(state, self.state_data[state].data)
            except Exception as e:
                self.logger.error(f"Ошибка в callback паузы состояния {state.value}: {e}")
    
    def _resume_state(self, state: GameState):
        """Возобновление состояния"""
        # Вызов callbacks
        for callback in self.state_callbacks[state][StateTransition.RESUME]:
            try:
                callback(state, self.state_data[state].data)
            except Exception as e:
                self.logger.error(f"Ошибка в callback возобновления состояния {state.value}: {e}")
    
    def register_callback(self, state: GameState, transition: StateTransition, callback: Callable):
        """Регистрация callback для состояния"""
        self.state_callbacks[state][transition].append(callback)
        log_system_event("game_state_manager", "callback_registered", {
            "state": state.value,
            "transition": transition.value
        })
    
    def unregister_callback(self, state: GameState, transition: StateTransition, callback: Callable):
        """Отмена регистрации callback"""
        if callback in self.state_callbacks[state][transition]:
            self.state_callbacks[state][transition].remove(callback)
            log_system_event("game_state_manager", "callback_unregistered", {
                "state": state.value,
                "transition": transition.value
            })
    
    def get_state_data(self, state: Optional[GameState] = None) -> Dict[str, Any]:
        """Получение данных состояния"""
        if state is None:
            state = self.current_state
        
        if state and state in self.state_data:
            return self.state_data[state].data.copy()
        
        return {}
    
    def set_state_data(self, state: GameState, data: Dict[str, Any]):
        """Установка данных состояния"""
        if state in self.state_data:
            self.state_data[state].data.update(data)
    
    def update(self, dt: float):
        """Обновление менеджера состояний"""
        current_time = time.time()
        
        # Обновление длительности текущего состояния
        if self.current_state:
            state_data = self.state_data[self.current_state]
            if state_data.is_active:
                state_data.duration = current_time - state_data.start_time
        
        # Автосохранение
        if current_time - self.last_auto_save > self.auto_save_interval:
            self.auto_save()
            self.last_auto_save = current_time
    
    def save_state(self, filename: str = "game_state.json") -> bool:
        """Сохранение состояния игры"""
        try:
            save_data = {
                'current_state': self.current_state.value if self.current_state else None,
                'previous_state': self.previous_state.value if self.previous_state else None,
                'state_history': [state.value for state in self.state_history],
                'state_data': {
                    state.value: {
                        'data': state_data.data,
                        'duration': state_data.duration
                    }
                    for state, state_data in self.state_data.items()
                },
                'timestamp': time.time()
            }
            
            save_file = self.save_directory / filename
            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            log_system_event("game_state_manager", "state_saved", {
                "filename": filename
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка сохранения состояния: {e}")
            return False
    
    def load_state(self, filename: str = "game_state.json") -> bool:
        """Загрузка состояния игры"""
        try:
            save_file = self.save_directory / filename
            if not save_file.exists():
                return False
            
            with open(save_file, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Восстановление данных состояний
            for state_name, state_info in save_data.get('state_data', {}).items():
                state = GameState(state_name)
                self.state_data[state].data = state_info.get('data', {})
                self.state_data[state].duration = state_info.get('duration', 0.0)
            
            # Восстановление истории
            self.state_history = [GameState(state_name) for state_name in save_data.get('state_history', [])]
            
            # Восстановление текущего состояния
            if save_data.get('current_state'):
                self.current_state = GameState(save_data['current_state'])
            
            if save_data.get('previous_state'):
                self.previous_state = GameState(save_data['previous_state'])
            
            log_system_event("game_state_manager", "state_loaded", {
                "filename": filename,
                "current_state": self.current_state.value if self.current_state else None
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки состояния: {e}")
            return False
    
    def auto_save(self) -> bool:
        """Автоматическое сохранение"""
        return self.save_state("auto_save.json")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики менеджера"""
        return {
            'current_state': self.current_state.value if self.current_state else None,
            'previous_state': self.previous_state.value if self.previous_state else None,
            'history_size': len(self.state_history),
            'total_states': len(self.state_data),
            'active_states': sum(1 for state_data in self.state_data.values() if state_data.is_active),
            'state_durations': {
                state.value: state_data.duration
                for state, state_data in self.state_data.items()
                if state_data.duration > 0
            }
        }
    
    def cleanup(self):
        """Очистка ресурсов"""
        # Сохраняем текущее состояние перед очисткой
        if self.current_state:
            self.save_state("final_state.json")
        
        # Очистка данных
        self.current_state = None
        self.previous_state = None
        self.state_history.clear()
        self.state_data.clear()
        self.state_callbacks.clear()
        
        log_system_event("game_state_manager", "cleanup_completed")
