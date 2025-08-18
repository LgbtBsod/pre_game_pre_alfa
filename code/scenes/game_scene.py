import pygame
from typing import Optional
from core.scene_manager import Scene
from core.input_manager import InputManager, InputAction
from core.game_state import GameState
from level import Level

class GameScene(Scene):
    """Main game scene that handles gameplay"""
    
    def __init__(self, scene_manager, game_manager):
        super().__init__(scene_manager)
        self.game_manager = game_manager
        self.level: Optional[Level] = None
        self.input_manager: Optional[InputManager] = None
        
    def initialize(self) -> None:
        """Initialize the game scene"""
        try:
            # Get managers from game manager
            self.input_manager = self.game_manager.input_manager
            
            # Create level with all necessary dependencies
            self.level = Level(
                resource_manager=self.game_manager.resource_manager,
                game_data_manager=self.game_manager.game_data_manager,
                audio_manager=self.game_manager.audio_manager,
                config_manager=self.game_manager.config_manager,
                state_manager=self.game_manager.state_manager
            )
            
            # Setup player input handlers
            if self.level and hasattr(self.level, 'player') and self.level.player:
                self._setup_player_input()
            
            self.logger.info("Game scene initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize game scene: {e}")
    
    def _setup_player_input(self) -> None:
        """Setup input handlers for player actions"""
        if not self.input_manager or not self.level or not self.level.player:
            return
            
        player = self.level.player
        
        # Register player movement handlers
        self.input_manager.register_action_handler(
            InputAction.MOVE_UP, 
            lambda: self._handle_player_movement('up')
        )
        self.input_manager.register_action_handler(
            InputAction.MOVE_DOWN, 
            lambda: self._handle_player_movement('down')
        )
        self.input_manager.register_action_handler(
            InputAction.MOVE_LEFT, 
            lambda: self._handle_player_movement('left')
        )
        self.input_manager.register_action_handler(
            InputAction.MOVE_RIGHT, 
            lambda: self._handle_player_movement('right')
        )
        
        # Register player action handlers
        self.input_manager.register_action_handler(
            InputAction.ATTACK, 
            self._handle_player_attack
        )
        self.input_manager.register_action_handler(
            InputAction.MAGIC, 
            self._handle_player_magic
        )
        self.input_manager.register_action_handler(
            InputAction.SWITCH_WEAPON, 
            self._handle_weapon_switch
        )
        self.input_manager.register_action_handler(
            InputAction.SWITCH_MAGIC, 
            self._handle_magic_switch
        )
    
    def _handle_player_movement(self, direction: str) -> None:
        """Handle player movement input"""
        if not self.level or not self.level.player:
            return
            
        player = self.level.player
        if direction == 'up':
            player.direction.y = -1
        elif direction == 'down':
            player.direction.y = 1
        elif direction == 'left':
            player.direction.x = -1
        elif direction == 'right':
            player.direction.x = 1
    
    def _handle_player_attack(self) -> None:
        """Handle player attack input"""
        if self.level and self.level.player:
            player = self.level.player
            if not player.attacking:
                player.attacking = True
                player.attack_time = pygame.time.get_ticks()
                if hasattr(self.level, 'create_attack'):
                    self.level.create_attack()
    
    def _handle_player_magic(self) -> None:
        """Handle player magic input"""
        if self.level and self.level.player:
            player = self.level.player
            if not player.attacking:
                player.attacking = True
                player.attack_time = pygame.time.get_ticks()
                if hasattr(self.level, 'create_magic') and hasattr(self.level, 'magic_player'):
                    if player.game_data_manager:
                        magic_data = player.game_data_manager.get_magic(player.magic)
                        if magic_data:
                            style = magic_data.name
                            strength = magic_data.strength + player.stats['magic']
                            cost = magic_data.cost
                            self.level.create_magic(style, strength, cost)
    
    def _handle_weapon_switch(self) -> None:
        """Handle weapon switching input"""
        if self.level and self.level.player:
            player = self.level.player
            if player.can_switch_weapon:
                player._switch_weapon()
    
    def _handle_magic_switch(self) -> None:
        """Handle magic switching input"""
        if self.level and self.level.player:
            player = self.level.player
            if player.can_switch_magic:
                player._switch_magic()
    
    def update(self, dt: float) -> None:
        """Update game scene logic"""
        if self.level:
            self.level.run()
    
    def render(self, screen: pygame.Surface) -> None:
        """Render the game scene"""
        if self.level:
            # Level handles its own rendering
            pass
    
    def handle_events(self, events: list) -> None:
        """Handle scene-specific events"""
        # Game scene doesn't need special event handling
        # Events are handled by the input manager
        pass
    
    def cleanup(self) -> None:
        """Cleanup game scene resources"""
        if self.level:
            # Level cleanup if needed
            pass
        self.logger.info("Game scene cleanup completed")
