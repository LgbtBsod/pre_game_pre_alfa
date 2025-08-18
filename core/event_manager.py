import pygame
from typing import Callable, Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class EventType(Enum):
    """Game event types"""
    QUIT = "quit"
    KEY_PRESS = "key_press"
    KEY_RELEASE = "key_release"
    MOUSE_CLICK = "mouse_click"
    MOUSE_MOVE = "mouse_move"
    GAME_STATE_CHANGE = "game_state_change"
    PLAYER_ACTION = "player_action"
    ENEMY_ACTION = "enemy_action"
    UI_ACTION = "ui_action"

@dataclass
class GameEvent:
    """Represents a game event"""
    event_type: EventType
    data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}

class EventManager:
    """Centralized event management system"""
    
    def __init__(self):
        self._event_handlers: Dict[EventType, List[Callable]] = {
            event_type: [] for event_type in EventType
        }
        self._pygame_events: List[pygame.event.Event] = []
    
    def register_handler(self, event_type: EventType, handler: Callable) -> None:
        """Register an event handler for a specific event type"""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
    
    def unregister_handler(self, event_type: EventType, handler: Callable) -> None:
        """Unregister an event handler"""
        if event_type in self._event_handlers:
            try:
                self._event_handlers[event_type].remove(handler)
            except ValueError:
                pass
    
    def emit_event(self, event: GameEvent) -> None:
        """Emit a custom game event"""
        if event.event_type in self._event_handlers:
            for handler in self._event_handlers[event.event_type]:
                try:
                    handler(event)
                except Exception as e:
                    print(f"Error in event handler: {e}")
    
    def process_pygame_events(self) -> List[GameEvent]:
        """Process pygame events and convert them to game events"""
        game_events = []
        
        for event in pygame.event.get():
            self._pygame_events.append(event)
            
            if event.type == pygame.QUIT:
                game_events.append(GameEvent(EventType.QUIT))
            
            elif event.type == pygame.KEYDOWN:
                game_events.append(GameEvent(
                    EventType.KEY_PRESS,
                    {'key': event.key, 'unicode': event.unicode}
                ))
            
            elif event.type == pygame.KEYUP:
                game_events.append(GameEvent(
                    EventType.KEY_RELEASE,
                    {'key': event.key}
                ))
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game_events.append(GameEvent(
                    EventType.MOUSE_CLICK,
                    {'button': event.button, 'pos': event.pos}
                ))
            
            elif event.type == pygame.MOUSEMOTION:
                game_events.append(GameEvent(
                    EventType.MOUSE_MOVE,
                    {'pos': event.pos, 'rel': event.rel}
                ))
        
        return game_events
    
    def handle_events(self) -> List[GameEvent]:
        """Process and handle all events"""
        game_events = self.process_pygame_events()
        
        for event in game_events:
            self.emit_event(event)
        
        return game_events
    
    def clear_events(self) -> None:
        """Clear all pending events"""
        self._pygame_events.clear()
