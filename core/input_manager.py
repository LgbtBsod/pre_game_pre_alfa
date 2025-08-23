"""
Система управления вводом.
Обеспечивает обработку клавиатуры и мыши с поддержкой привязки действий.
"""

from typing import Dict, List, Callable, Optional, Any
from enum import Enum
import pygame
import logging

logger = logging.getLogger(__name__)


class InputAction(Enum):
    """Действия ввода"""
    MOVE_UP = "move_up"
    MOVE_DOWN = "move_down"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    ATTACK = "attack"
    INTERACT = "interact"
    INVENTORY = "inventory"
    PAUSE = "pause"
    SAVE = "save"
    LOAD = "load"
    MENU = "menu"
    CONFIRM = "confirm"
    CANCEL = "cancel"
    SCROLL_UP = "scroll_up"
    SCROLL_DOWN = "scroll_down"


class InputType(Enum):
    """Типы ввода"""
    KEYBOARD = "keyboard"
    MOUSE = "mouse"
    GAMEPAD = "gamepad"


class InputEvent:
    """Событие ввода"""
    
    def __init__(self, action: InputAction, input_type: InputType, 
                 key_code: Optional[int] = None, mouse_button: Optional[int] = None,
                 position: Optional[tuple] = None, pressed: bool = True):
        self.action = action
        self.input_type = input_type
        self.key_code = key_code
        self.mouse_button = mouse_button
        self.position = position
        self.pressed = pressed
        self.timestamp = pygame.time.get_ticks()


class InputManager:
    """Менеджер ввода"""
    
    def __init__(self):
        # Привязки клавиш по умолчанию
        self.default_keybindings = {
            InputAction.MOVE_UP: [pygame.K_w, pygame.K_UP],
            InputAction.MOVE_DOWN: [pygame.K_s, pygame.K_DOWN],
            InputAction.MOVE_LEFT: [pygame.K_a, pygame.K_LEFT],
            InputAction.MOVE_RIGHT: [pygame.K_d, pygame.K_RIGHT],
            InputAction.ATTACK: [pygame.K_SPACE, pygame.K_RETURN],
            InputAction.INTERACT: [pygame.K_e],
            InputAction.INVENTORY: [pygame.K_i],
            InputAction.PAUSE: [pygame.K_ESCAPE, pygame.K_p],
            InputAction.SAVE: [pygame.K_F5],
            InputAction.LOAD: [pygame.K_F9],
            InputAction.MENU: [pygame.K_ESCAPE],
            InputAction.CONFIRM: [pygame.K_RETURN, pygame.K_SPACE],
            InputAction.CANCEL: [pygame.K_ESCAPE],
            InputAction.SCROLL_UP: [pygame.K_PAGEUP],
            InputAction.SCROLL_DOWN: [pygame.K_PAGEDOWN]
        }
        
        # Привязки мыши по умолчанию
        self.default_mouse_bindings = {
            InputAction.ATTACK: [1],  # Левая кнопка мыши
            InputAction.INTERACT: [3],  # Правая кнопка мыши
            InputAction.SCROLL_UP: [4],  # Колесо мыши вверх
            InputAction.SCROLL_DOWN: [5]  # Колесо мыши вниз
        }
        
        # Текущие привязки
        self.keybindings = self.default_keybindings.copy()
        self.mouse_bindings = self.default_mouse_bindings.copy()
        
        # Обработчики действий
        self.action_handlers: Dict[InputAction, List[Callable]] = {}
        
        # Состояние ввода
        self.pressed_keys = set()
        self.pressed_mouse_buttons = set()
        self.mouse_position = (0, 0)
        self.mouse_rel = (0, 0)
        
        # Настройки
        self.enabled = True
        self.repeat_delay = 500  # мс
        self.repeat_interval = 50  # мс
        
        # История событий
        self.input_history: List[InputEvent] = []
        self.max_history_size = 100
        
        logger.info("Менеджер ввода инициализирован")
    
    def register_action_handler(self, action: InputAction, handler: Callable) -> None:
        """Регистрация обработчика действия"""
        if action not in self.action_handlers:
            self.action_handlers[action] = []
        
        self.action_handlers[action].append(handler)
        logger.info(f"Зарегистрирован обработчик для действия: {action.value}")
    
    def unregister_action_handler(self, action: InputAction, handler: Callable) -> None:
        """Удаление обработчика действия"""
        if action in self.action_handlers and handler in self.action_handlers[action]:
            self.action_handlers[action].remove(handler)
            logger.info(f"Удалён обработчик для действия: {action.value}")
    
    def bind_key(self, action: InputAction, key_code: int) -> None:
        """Привязка клавиши к действию"""
        if action not in self.keybindings:
            self.keybindings[action] = []
        
        if key_code not in self.keybindings[action]:
            self.keybindings[action].append(key_code)
            logger.info(f"Привязана клавиша {key_code} к действию {action.value}")
    
    def unbind_key(self, action: InputAction, key_code: int) -> None:
        """Отвязка клавиши от действия"""
        if action in self.keybindings and key_code in self.keybindings[action]:
            self.keybindings[action].remove(key_code)
            logger.info(f"Отвязана клавиша {key_code} от действия {action.value}")
    
    def bind_mouse_button(self, action: InputAction, button: int) -> None:
        """Привязка кнопки мыши к действию"""
        if action not in self.mouse_bindings:
            self.mouse_bindings[action] = []
        
        if button not in self.mouse_bindings[action]:
            self.mouse_bindings[action].append(button)
            logger.info(f"Привязана кнопка мыши {button} к действию {action.value}")
    
    def unbind_mouse_button(self, action: InputAction, button: int) -> None:
        """Отвязка кнопки мыши от действия"""
        if action in self.mouse_bindings and button in self.mouse_bindings[action]:
            self.mouse_bindings[action].remove(button)
            logger.info(f"Отвязана кнопка мыши {button} от действия {action.value}")
    
    def reset_to_defaults(self) -> None:
        """Сброс к привязкам по умолчанию"""
        self.keybindings = self.default_keybindings.copy()
        self.mouse_bindings = self.default_mouse_bindings.copy()
        logger.info("Привязки сброшены к значениям по умолчанию")
    
    def update(self, events: List[pygame.event.Event]) -> None:
        """Обновление состояния ввода"""
        if not self.enabled:
            return
        
        # Обновляем позицию мыши
        self.mouse_position = pygame.mouse.get_pos()
        self.mouse_rel = pygame.mouse.get_rel()
        
        # Обрабатываем события
        for event in events:
            if event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
            elif event.type == pygame.KEYUP:
                self._handle_keyup(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mousedown(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                self._handle_mouseup(event)
            elif event.type == pygame.MOUSEMOTION:
                self._handle_mousemotion(event)
    
    def _handle_keydown(self, event: pygame.event.Event) -> None:
        """Обработка нажатия клавиши"""
        self.pressed_keys.add(event.key)
        
        # Находим действие для этой клавиши
        for action, keys in self.keybindings.items():
            if event.key in keys:
                self._trigger_action(action, InputType.KEYBOARD, key_code=event.key)
                break
    
    def _handle_keyup(self, event: pygame.event.Event) -> None:
        """Обработка отпускания клавиши"""
        self.pressed_keys.discard(event.key)
    
    def _handle_mousedown(self, event: pygame.event.Event) -> None:
        """Обработка нажатия кнопки мыши"""
        self.pressed_mouse_buttons.add(event.button)
        
        # Находим действие для этой кнопки
        for action, buttons in self.mouse_bindings.items():
            if event.button in buttons:
                self._trigger_action(action, InputType.MOUSE, 
                                   mouse_button=event.button, 
                                   position=event.pos)
                break
    
    def _handle_mouseup(self, event: pygame.event.Event) -> None:
        """Обработка отпускания кнопки мыши"""
        self.pressed_mouse_buttons.discard(event.button)
    
    def _handle_mousemotion(self, event: pygame.event.Event) -> None:
        """Обработка движения мыши"""
        # Можно добавить обработку движения мыши для специальных действий
        pass
    
    def _trigger_action(self, action: InputAction, input_type: InputType, 
                       key_code: Optional[int] = None, 
                       mouse_button: Optional[int] = None,
                       position: Optional[tuple] = None) -> None:
        """Запуск действия"""
        # Создаём событие ввода
        input_event = InputEvent(
            action=action,
            input_type=input_type,
            key_code=key_code,
            mouse_button=mouse_button,
            position=position
        )
        
        # Добавляем в историю
        self.input_history.append(input_event)
        if len(self.input_history) > self.max_history_size:
            self.input_history.pop(0)
        
        # Вызываем обработчики
        if action in self.action_handlers:
            for handler in self.action_handlers[action]:
                try:
                    handler(input_event)
                except Exception as e:
                    logger.error(f"Ошибка в обработчике действия {action.value}: {e}")
    
    def is_action_pressed(self, action: InputAction) -> bool:
        """Проверка, нажато ли действие"""
        # Проверяем клавиши
        if action in self.keybindings:
            for key in self.keybindings[action]:
                if key in self.pressed_keys:
                    return True
        
        # Проверяем кнопки мыши
        if action in self.mouse_bindings:
            for button in self.mouse_bindings[action]:
                if button in self.pressed_mouse_buttons:
                    return True
        
        return False
    
    def get_mouse_position(self) -> tuple:
        """Получение позиции мыши"""
        return self.mouse_position
    
    def get_mouse_rel(self) -> tuple:
        """Получение относительного движения мыши"""
        return self.mouse_rel
    
    def get_pressed_keys(self) -> set:
        """Получение нажатых клавиш"""
        return self.pressed_keys.copy()
    
    def get_pressed_mouse_buttons(self) -> set:
        """Получение нажатых кнопок мыши"""
        return self.pressed_mouse_buttons.copy()
    
    def get_input_history(self) -> List[InputEvent]:
        """Получение истории ввода"""
        return self.input_history.copy()
    
    def clear_history(self) -> None:
        """Очистка истории ввода"""
        self.input_history.clear()
    
    def save_keybindings(self, filepath: str) -> bool:
        """Сохранение привязок клавиш"""
        try:
            import json
            
            # Конвертируем в сериализуемый формат
            save_data = {}
            for action, keys in self.keybindings.items():
                save_data[action.value] = keys
            
            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            logger.info(f"Привязки клавиш сохранены в {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения привязок: {e}")
            return False
    
    def load_keybindings(self, filepath: str) -> bool:
        """Загрузка привязок клавиш"""
        try:
            import json
            
            with open(filepath, 'r') as f:
                save_data = json.load(f)
            
            # Конвертируем обратно
            self.keybindings.clear()
            for action_str, keys in save_data.items():
                action = InputAction(action_str)
                self.keybindings[action] = keys
            
            logger.info(f"Привязки клавиш загружены из {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка загрузки привязок: {e}")
            return False
    
    def enable(self) -> None:
        """Включение обработки ввода"""
        self.enabled = True
        logger.info("Обработка ввода включена")
    
    def disable(self) -> None:
        """Отключение обработки ввода"""
        self.enabled = False
        logger.info("Обработка ввода отключена")
