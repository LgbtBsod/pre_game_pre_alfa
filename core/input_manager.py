import pygame
from typing import Dict, Set, Callable, Optional
from enum import Enum

class InputAction(Enum):
    """Input actions that can be performed"""
    MOVE_UP = "move_up"
    MOVE_DOWN = "move_down"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    ATTACK = "attack"
    MAGIC = "magic"
    SWITCH_WEAPON = "switch_weapon"
    SWITCH_MAGIC = "switch_magic"
    PAUSE = "pause"
    QUICK_SAVE = "quick_save"
    QUICK_LOAD = "quick_load"
    INTERACT = "interact"

class InputManager:
    """Manages all input handling for the game"""
    
    def __init__(self):
        self._key_bindings: Dict[InputAction, int] = {
            InputAction.MOVE_UP: pygame.K_UP,
            InputAction.MOVE_DOWN: pygame.K_DOWN,
            InputAction.MOVE_LEFT: pygame.K_LEFT,
            InputAction.MOVE_RIGHT: pygame.K_RIGHT,
            InputAction.ATTACK: pygame.K_SPACE,
            InputAction.MAGIC: pygame.K_LCTRL,
            InputAction.SWITCH_WEAPON: pygame.K_q,
            InputAction.SWITCH_MAGIC: pygame.K_e,
            InputAction.PAUSE: pygame.K_ESCAPE,
            InputAction.QUICK_SAVE: pygame.K_F5,
            InputAction.QUICK_LOAD: pygame.K_F9,
            InputAction.INTERACT: pygame.K_RETURN
        }
        
        self._action_handlers: Dict[InputAction, Callable] = {}
        self._pressed_keys: Set[int] = set()
        self._just_pressed_keys: Set[int] = set()
        self._just_released_keys: Set[int] = set()
    
    def set_key_binding(self, action: InputAction, key: int) -> None:
        """Set a key binding for an action"""
        self._key_bindings[action] = key
    
    def get_key_binding(self, action: InputAction) -> int:
        """Get the key binding for an action"""
        return self._key_bindings.get(action, pygame.K_UNKNOWN)
    
    def register_action_handler(self, action: InputAction, handler: Callable) -> None:
        """Register a handler for an input action"""
        self._action_handlers[action] = handler
    
    def unregister_action_handler(self, action: InputAction) -> None:
        """Unregister a handler for an input action"""
        if action in self._action_handlers:
            del self._action_handlers[action]
    
    def update(self) -> None:
        """Update input state - call this once per frame"""
        # Clear just pressed/released keys
        self._just_pressed_keys.clear()
        self._just_released_keys.clear()
        
        # Get current pressed keys
        current_pressed_keys = pygame.key.get_pressed()
        current_pressed = set()
        
        # Convert to set for easier comparison
        for key in range(len(current_pressed_keys)):
            if current_pressed_keys[key]:
                current_pressed.add(key)
        
        # Find just pressed keys
        for key in current_pressed:
            if key not in self._pressed_keys:
                self._just_pressed_keys.add(key)
        
        # Find just released keys
        for key in self._pressed_keys:
            if key not in current_pressed:
                self._just_released_keys.add(key)
        
        self._pressed_keys = current_pressed
    
    def is_action_pressed(self, action: InputAction) -> bool:
        """Check if an action is currently pressed"""
        key = self._key_bindings.get(action)
        if key is not None:
            return pygame.key.get_pressed()[key]
        return False
    
    def is_action_just_pressed(self, action: InputAction) -> bool:
        """Check if an action was just pressed this frame"""
        key = self._key_bindings.get(action)
        return key in self._just_pressed_keys
    
    def is_action_just_released(self, action: InputAction) -> bool:
        """Check if an action was just released this frame"""
        key = self._key_bindings.get(action)
        return key in self._just_released_keys
    
    def get_movement_vector(self) -> tuple[float, float]:
        """Get normalized movement vector based on current input"""
        x, y = 0.0, 0.0
        
        if self.is_action_pressed(InputAction.MOVE_LEFT):
            x -= 1.0
        if self.is_action_pressed(InputAction.MOVE_RIGHT):
            x += 1.0
        if self.is_action_pressed(InputAction.MOVE_UP):
            y -= 1.0
        if self.is_action_pressed(InputAction.MOVE_DOWN):
            y += 1.0
        
        # Normalize diagonal movement
        if x != 0 and y != 0:
            x *= 0.707  # 1/sqrt(2)
            y *= 0.707
        
        return x, y
    
    def handle_actions(self) -> None:
        """Handle all input actions - call this after update()"""
        for action, handler in self._action_handlers.items():
            if self.is_action_just_pressed(action):
                try:
                    handler()
                except Exception as e:
                    print(f"Error in input action handler for {action}: {e}")
    
    def get_key_name(self, key: int) -> str:
        """Get the name of a key"""
        return pygame.key.name(key)
    
    def reset(self) -> None:
        """Reset input state"""
        self._pressed_keys.clear()
        self._just_pressed_keys.clear()
        self._just_released_keys.clear()
