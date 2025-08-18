from enum import Enum
from typing import Optional

class GameState(Enum):
    """Enumeration of possible game states"""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    VICTORY = "victory"

class GameStateManager:
    """Manages the current state of the game"""
    
    def __init__(self):
        self._current_state = GameState.MENU
        self._previous_state: Optional[GameState] = None
    
    @property
    def current_state(self) -> GameState:
        """Get current game state"""
        return self._current_state
    
    @property
    def previous_state(self) -> Optional[GameState]:
        """Get previous game state"""
        return self._previous_state
    
    def change_state(self, new_state: GameState) -> None:
        """Change game state"""
        if new_state != self._current_state:
            self._previous_state = self._current_state
            self._current_state = new_state
    
    def is_state(self, state: GameState) -> bool:
        """Check if current state matches given state"""
        return self._current_state == state
    
    def can_transition_to(self, new_state: GameState) -> bool:
        """Check if transition to new state is valid"""
        valid_transitions = {
            GameState.MENU: [GameState.PLAYING, GameState.GAME_OVER, GameState.VICTORY],
            GameState.PLAYING: [GameState.PAUSED, GameState.GAME_OVER, GameState.VICTORY],
            GameState.PAUSED: [GameState.PLAYING, GameState.MENU],
            GameState.GAME_OVER: [GameState.MENU],
            GameState.VICTORY: [GameState.MENU]
        }
        return new_state in valid_transitions.get(self._current_state, [])
    
    def reset(self) -> None:
        """Reset to initial state"""
        self._current_state = GameState.MENU
        self._previous_state = None
