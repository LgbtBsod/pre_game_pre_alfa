import pygame
import sys
from typing import Optional, Dict, Any
from pathlib import Path

from .game_state import GameStateManager, GameState
from .event_manager import EventManager, EventType, GameEvent
from .input_manager import InputManager, InputAction
from .config import ConfigManager
from .logger import GameLogger
from .resource_manager import ResourceManager
from .audio_manager import AudioManager
from .performance_monitor import PerformanceMonitor
from .game_data import GameDataManager
from .scene_manager import SceneManager
from .game_loop_manager import GameLoopManager
from .performance_optimizer import PerformanceOptimizer

class GameManager:
    """Centralized game management system that coordinates all subsystems"""
    
    def __init__(self):
        # Initialize core systems
        self.config_manager = ConfigManager()
        self.logger = GameLogger("GameManager")
        self.resource_manager = ResourceManager()
        
        # Initialize pygame
        try:
            pygame.init()
        except Exception as e:
            self.logger.error(f"Failed to initialize pygame: {e}")
            raise
        
        # Initialize display
        try:
            self._setup_display()
        except Exception as e:
            self.logger.error(f"Failed to setup display: {e}")
            raise
        
        # Initialize subsystems
        try:
            self.audio_manager = AudioManager(self.resource_manager)
            self.event_manager = EventManager()
            self.input_manager = InputManager()
            self.state_manager = GameStateManager()
            self.performance_monitor = PerformanceMonitor()
            self.game_data_manager = GameDataManager()
            self.scene_manager = SceneManager()
        except Exception as e:
            self.logger.error(f"Failed to initialize subsystems: {e}")
            raise
        
        # Game components
        self.level = None
        self.menu = None
        self.pause_menu = None
        
        # Game state
        self.running = False
        
        # Game loop manager
        try:
            self.game_loop_manager = GameLoopManager(self.config_manager.get_setting('fps'))
        except Exception as e:
            self.logger.error(f"Failed to initialize game loop manager: {e}")
            raise
        
        # Performance optimizer
        try:
            self.performance_optimizer = PerformanceOptimizer(self.performance_monitor)
        except Exception as e:
            self.logger.error(f"Failed to initialize performance optimizer: {e}")
            raise
        
        # Setup event handlers
        try:
            self._setup_event_handlers()
        except Exception as e:
            self.logger.error(f"Failed to setup event handlers: {e}")
        
        # Initialize scenes
        try:
            self._initialize_scenes()
        except Exception as e:
            self.logger.error(f"Failed to initialize scenes: {e}")
        
        # Initialize game components
        try:
            self._initialize_game_components()
        except Exception as e:
            self.logger.error(f"Failed to initialize game components: {e}")
        
        # Set running flag to True after successful initialization
        self.running = True
        
        self.logger.info("Game manager initialized successfully")
    
    def _initialize_scenes(self) -> None:
        """Initialize all game scenes"""
        try:
            self.logger.info("Starting scene initialization")
            print("Starting scene initialization")  # Debug print
            
            from code.scenes.game_scene import GameScene
            from code.scenes.pause_scene import PauseScene
            from code.scenes.menu_scene import MenuScene
            
            self.logger.info("Scene classes imported successfully")
            print("Scene classes imported successfully")  # Debug print
            
            # Register scenes
            self.scene_manager.register_scene('game', GameScene(self.scene_manager, self))
            self.logger.info("Game scene registered")
            print("Game scene registered")  # Debug print
            
            self.scene_manager.register_scene('menu', MenuScene(self.scene_manager, self))
            self.logger.info("Menu scene registered")
            print("Menu scene registered")  # Debug print
            
            self.scene_manager.register_scene('pause', PauseScene(self.scene_manager, self))
            self.logger.info("Pause scene registered")
            print("Pause scene registered")  # Debug print
            
            # Start with menu scene
            self.scene_manager.switch_scene('menu')
            self.logger.info("Switched to menu scene")
            print("Switched to menu scene")  # Debug print
            
            self.logger.info("Scenes initialized successfully")
            print("Scenes initialized successfully")  # Debug print
            
        except Exception as e:
            self.logger.error(f"Failed to initialize scenes: {e}")
            import traceback
            self.logger.error(f"Scene initialization traceback: {traceback.format_exc()}")
            print(f"Failed to initialize scenes: {e}")  # Debug print
            # Create fallback scenes
            try:
                self._create_fallback_scenes()
            except Exception as fallback_error:
                self.logger.error(f"Failed to create fallback scenes: {fallback_error}")
                raise
    
    def _setup_display(self) -> None:
        """Setup the game display"""
        try:
            width, height = self.config_manager.get_display_mode()
            flags = pygame.FULLSCREEN if self.config_manager.get_setting('fullscreen') else 0
            
            if self.config_manager.get_setting('vsync'):
                flags |= pygame.DOUBLEBUF
            
            self.screen = pygame.display.set_mode((width, height), flags)
            pygame.display.set_caption('Zelda - Enhanced Edition')
            
            self.logger.info(f"Display initialized: {width}x{height}")
        except Exception as e:
            self.logger.error(f"Failed to initialize display: {e}")
            # Fallback to default resolution
            try:
                self.screen = pygame.display.set_mode((1280, 720))
                self.logger.info("Fallback display initialized: 1280x720")
            except Exception as fallback_error:
                self.logger.error(f"Failed to initialize fallback display: {fallback_error}")
                raise
    
    def _initialize_game_components(self) -> None:
        """Initialize game components with proper dependencies"""
        try:
            # Create level with all necessary managers
            from code.level import Level
            self.level = Level(
                resource_manager=self.resource_manager,
                game_data_manager=self.game_data_manager,
                audio_manager=self.audio_manager,
                config_manager=self.config_manager,
                state_manager=self.state_manager
            )
            
            # Setup input manager with player reference
            if hasattr(self.level, 'player') and self.level.player:
                self._setup_player_input()
            
            self.logger.info("Game components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize game components: {e}")
            # Create fallback level
            try:
                self._create_fallback_level()
            except Exception as fallback_error:
                self.logger.error(f"Failed to create fallback level: {fallback_error}")
                # Continue without level
                self.level = None
    
    def _setup_player_input(self) -> None:
        """Setup input manager with player-specific actions"""
        try:
            if not hasattr(self.level, 'player') or not self.level.player:
                return
                
            player = self.level.player
            
            # Register player-specific input handlers
            self.input_manager.register_action_handler(InputAction.MOVE_UP, lambda: self._handle_player_movement('up'))
            self.input_manager.register_action_handler(InputAction.MOVE_DOWN, lambda: self._handle_player_movement('down'))
            self.input_manager.register_action_handler(InputAction.MOVE_LEFT, lambda: self._handle_player_movement('left'))
            self.input_manager.register_action_handler(InputAction.MOVE_RIGHT, lambda: self._handle_player_movement('right'))
            self.input_manager.register_action_handler(InputAction.ATTACK, self._handle_player_attack)
            self.input_manager.register_action_handler(InputAction.MAGIC, self._handle_player_magic)
            self.input_manager.register_action_handler(InputAction.SWITCH_WEAPON, self._handle_weapon_switch)
            self.input_manager.register_action_handler(InputAction.SWITCH_MAGIC, self._handle_magic_switch)
        except Exception as e:
            self.logger.error(f"Error setting up player input: {e}")
    
    def _handle_player_movement(self, direction: str) -> None:
        """Handle player movement input"""
        try:
            if not hasattr(self.level, 'player') or not self.level.player:
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
        except Exception as e:
            self.logger.error(f"Error handling player movement: {e}")
    
    def _handle_player_attack(self) -> None:
        """Handle player attack input"""
        try:
            if hasattr(self.level, 'player') and self.level.player:
                player = self.level.player
                if not player.attacking:
                    player.attacking = True
                    player.attack_time = pygame.time.get_ticks()
                    if hasattr(self.level, 'create_attack'):
                        self.level.create_attack()
        except Exception as e:
            self.logger.error(f"Error handling player attack: {e}")
    
    def _handle_player_magic(self) -> None:
        """Handle player magic input"""
        try:
            if hasattr(self.level, 'player') and self.level.player:
                player = self.level.player
                if not player.attacking:
                    player.attacking = True
                    player.attack_time = pygame.time.get_ticks()
                    if hasattr(self.level, 'create_magic') and hasattr(self.level, 'magic_player'):
                        # Get current magic data
                        if hasattr(player, 'game_data_manager') and player.game_data_manager:
                            magic_data = player.game_data_manager.get_magic(player.magic)
                            if magic_data:
                                style = magic_data.name
                                strength = magic_data.strength + player.stats['magic']
                                cost = magic_data.cost
                                self.level.create_magic(style, strength, cost)
        except Exception as e:
            self.logger.error(f"Error handling player magic: {e}")
    
    def _handle_weapon_switch(self) -> None:
        """Handle weapon switching input"""
        try:
            if hasattr(self.level, 'player') and self.level.player:
                player = self.level.player
                if hasattr(player, 'can_switch_weapon') and player.can_switch_weapon:
                    player._switch_weapon()
        except Exception as e:
            self.logger.error(f"Error handling weapon switch: {e}")
    
    def _handle_magic_switch(self) -> None:
        """Handle magic switching input"""
        try:
            if hasattr(self.level, 'player') and self.level.player:
                player = self.level.player
                if hasattr(player, 'can_switch_magic') and player.can_switch_magic:
                    player._switch_magic()
        except Exception as e:
            self.logger.error(f"Error handling magic switch: {e}")
    
    def _create_fallback_level(self) -> None:
        """Create a fallback level if initialization fails"""
        try:
            from code.level import Level
            self.level = Level()  # Create with default parameters
            self.logger.warning("Created fallback level with default parameters")
        except Exception as e:
            self.logger.error(f"Failed to create fallback level: {e}")
            # Create a minimal fallback level
            try:
                # Create a simple level object with minimal functionality
                class FallbackLevel:
                    def __init__(self):
                        self.player = None
                        self.entities = []
                        self.tiles = []
                    
                    def update(self, dt):
                        pass
                    
                    def render(self, screen):
                        pass
                
                self.level = FallbackLevel()
                self.logger.warning("Created minimal fallback level")
            except Exception as fallback_error:
                self.logger.error(f"Failed to create minimal fallback level: {fallback_error}")
                self.level = None
    
    def _create_fallback_scenes(self) -> None:
        """Create fallback scenes if initialization fails"""
        try:
            # Create a minimal fallback menu scene
            class FallbackMenuScene:
                def __init__(self, scene_manager, game_manager):
                    self.scene_manager = scene_manager
                    self.game_manager = game_manager
                    self.is_active = True
                    self.is_initialized = True
                
                def initialize(self):
                    pass
                
                def update(self, dt):
                    try:
                        # Fallback scene doesn't need updating
                        pass
                    except Exception as e:
                        # Silently ignore errors in fallback scene
                        pass
                
                def render(self, screen):
                    try:
                        screen.fill((0, 0, 0))
                        font = pygame.font.SysFont('arial', 48)
                        text = font.render('ZELDA GAME - Fallback Mode', True, (255, 255, 255))
                        text_rect = text.get_rect(center=screen.get_rect().center)
                        screen.blit(text, text_rect)
                        
                        # Render instructions
                        instruction_font = pygame.font.SysFont('arial', 24)
                        instructions = [
                            "Press ESC to quit",
                            "Press UP/DOWN to navigate",
                            "Press ENTER to select"
                        ]
                        for i, instruction in enumerate(instructions):
                            instruction_text = instruction_font.render(instruction, True, (128, 128, 128))
                            instruction_rect = instruction_text.get_rect(center=(screen.get_rect().centerx, screen.get_rect().centery + 100 + i * 30))
                            screen.blit(instruction_text, instruction_rect)
                    except Exception as e:
                        # Silently ignore errors in fallback scene
                        pass
                
                def handle_events(self, events):
                    try:
                        for event in events:
                            if hasattr(event, 'type'):
                                if event.type == pygame.KEYDOWN:
                                    if event.key == pygame.K_ESCAPE:
                                        if hasattr(self.game_manager, 'running'):
                                            self.game_manager.running = False
                                    elif event.key == pygame.K_UP:
                                        # Handle up arrow
                                        pass
                                    elif event.key == pygame.K_DOWN:
                                        # Handle down arrow
                                        pass
                                    elif event.key == pygame.K_RETURN:
                                        # Handle enter key
                                        pass
                    except Exception as e:
                        # Silently ignore errors in fallback scene
                        pass
                
                def activate(self):
                    try:
                        self.is_active = True
                    except Exception as e:
                        # Silently ignore errors in fallback scene
                        pass
                
                def deactivate(self):
                    try:
                        self.is_active = False
                    except Exception as e:
                        # Silently ignore errors in fallback scene
                        pass
                
                def cleanup(self):
                    try:
                        # Fallback scene doesn't need cleanup
                        pass
                    except Exception as e:
                        # Silently ignore errors in fallback scene
                        pass
            
            # Register fallback scene
            try:
                self.scene_manager.register_scene('menu', FallbackMenuScene(self.scene_manager, self))
                self.scene_manager.switch_scene('menu')
                self.logger.warning("Created fallback scenes")
            except Exception as e:
                self.logger.error(f"Failed to register fallback scene: {e}")
                raise
            
        except Exception as e:
            self.logger.error(f"Failed to create fallback scenes: {e}")
            raise
    
    def _setup_event_handlers(self) -> None:
        """Setup event handlers for the game"""
        try:
            # Register input action handlers
            self.input_manager.register_action_handler(InputAction.PAUSE, self._toggle_pause)
            self.input_manager.register_action_handler(InputAction.QUICK_SAVE, self._quick_save)
            self.input_manager.register_action_handler(InputAction.QUICK_LOAD, self._quick_load)
            
            # Register event handlers
            self.event_manager.register_handler(EventType.QUIT, self._handle_quit)
            self.event_manager.register_handler(EventType.GAME_STATE_CHANGE, self._handle_state_change)
        except Exception as e:
            self.logger.error(f"Error setting up event handlers: {e}")
    
    def _handle_quit(self, event: GameEvent) -> None:
        """Handle quit event"""
        try:
            self.running = False
        except Exception as e:
            self.logger.error(f"Error handling quit: {e}")
    
    def _handle_state_change(self, event: GameEvent) -> None:
        """Handle game state change event"""
        try:
            if event and hasattr(event, 'data'):
                new_state = event.data.get('new_state')
                if new_state:
                    self.state_manager.change_state(new_state)
                    self.logger.info(f"Game state changed to: {new_state}")
        except Exception as e:
            self.logger.error(f"Error handling state change: {e}")
    
    def _toggle_pause(self) -> None:
        """Toggle pause state"""
        try:
            if self.state_manager.is_state(GameState.PLAYING):
                self.state_manager.change_state(GameState.PAUSED)
                if hasattr(self.audio_manager, 'pause_music'):
                    self.audio_manager.pause_music()
                # Switch to pause scene
                if hasattr(self, 'scene_manager'):
                    self.scene_manager.switch_scene('pause')
            elif self.state_manager.is_state(GameState.PAUSED):
                self.state_manager.change_state(GameState.PLAYING)
                if hasattr(self.audio_manager, 'unpause_music'):
                    self.audio_manager.unpause_music()
                # Switch back to game scene
                if hasattr(self, 'scene_manager'):
                    self.scene_manager.switch_scene('game')
        except Exception as e:
            self.logger.error(f"Error toggling pause: {e}")
    
    def _quick_save(self) -> None:
        """Quick save functionality"""
        try:
            # TODO: Implement save system integration
            self.logger.info("Quick save requested")
        except Exception as e:
            self.logger.error(f"Error in quick save: {e}")
    
    def _quick_load(self) -> None:
        """Quick load functionality"""
        try:
            # TODO: Implement save system integration
            self.logger.info("Quick load requested")
        except Exception as e:
            self.logger.error(f"Error in quick load: {e}")
    
    def run(self) -> None:
        """Main game loop"""
        if not self.running:
            self.logger.error("Game manager not properly initialized")
            print("Game manager not properly initialized")  # Debug print
            return
            
        # Start with menu state, not playing state
        self.state_manager.change_state(GameState.MENU)
        print("Game state set to MENU")  # Debug print
        
        # Setup game loop callbacks
        self.game_loop_manager.set_callbacks({
            'handle_events': self._handle_events,
            'update': self._update,
            'render': self._render
        })
        print("Game loop callbacks set")  # Debug print
        
        self.logger.info("Starting main game loop")
        print("Starting main game loop")  # Debug print
        
        # Start the game loop
        self.game_loop_manager.start()
        
        self.logger.info("Main game loop ended")
        print("Main game loop ended")  # Debug print
    
    def _handle_events(self) -> None:
        """Handle all game events"""
        try:
            # Process pygame events directly for better performance            
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                elif event.type == pygame.KEYDOWN:
                    # Only handle these keys when in playing state
                    if self.state_manager.is_state(GameState.PLAYING):
                        if event.key == pygame.K_ESCAPE:
                            self._toggle_pause()
                        elif event.key == pygame.K_F5:
                            self._quick_save()
                        elif event.key == pygame.K_F9:
                            self._quick_load()
            
            # Update input manager
            self.input_manager.update()
            
            # Handle scene events with the same events
            if self.scene_manager.get_current_scene():
                self.scene_manager.handle_events(events)
            else:
                self.logger.warning("No current scene to handle events")
                print("No current scene to handle events")  # Debug print
                
        except Exception as e:
            self.logger.error(f"Error handling events: {e}")
            import traceback
            self.logger.error(f"Events traceback: {traceback.format_exc()}")
            print(f"Error handling events: {e}")  # Debug print
    
    def _handle_key_press(self, key_data: Dict[str, Any]) -> None:
        """Handle key press events"""
        try:
            if not key_data:
                return
            key = key_data.get('key')
            if key == pygame.K_ESCAPE:
                self._toggle_pause()
            elif key == pygame.K_F5:
                self._quick_save()
            elif key == pygame.K_F9:
                self._quick_load()
        except Exception as e:
            self.logger.error(f"Error handling key press: {e}")
    
    def _update(self, dt: float) -> None:
        """Update game logic based on current state"""
        try:
            # Update performance optimizer
            if hasattr(self, 'performance_optimizer'):
                try:
                    self.performance_optimizer.update(dt)
                except Exception as e:
                    self.logger.error(f"Error updating performance optimizer: {e}")
            
            # Update current scene
            if self.scene_manager.get_current_scene():
                try:
                    self.scene_manager.update(dt)
                except Exception as e:
                    self.logger.error(f"Error updating scene: {e}")
            else:
                self.logger.warning("No current scene to update")
                print("No current scene to update")  # Debug print
        except Exception as e:
            self.logger.error(f"Error in update: {e}")
            import traceback
            self.logger.error(f"Update traceback: {traceback.format_exc()}")
            print(f"Error in update: {e}")  # Debug print
    
    def _render(self) -> None:
        """Render the current game state"""
        try:
            # Clear screen with black background
            self.screen.fill((0, 0, 0))
            
            # Render current scene
            if self.scene_manager.get_current_scene():
                self.scene_manager.render(self.screen)
                print("Scene rendered successfully")  # Debug print
            else:
                # Render fallback content if no scene
                font = pygame.font.SysFont('arial', 48)
                text = font.render('ZELDA GAME - Loading...', True, (255, 255, 255))
                text_rect = text.get_rect(center=self.screen.get_rect().center)
                self.screen.blit(text, text_rect)
                self.logger.warning("No current scene to render, showing loading message")
                print("No current scene to render, showing loading message")  # Debug print
            
            # Update display
            pygame.display.flip()
            
        except Exception as e:
            self.logger.error(f"Error in render: {e}")
            import traceback
            self.logger.error(f"Render traceback: {traceback.format_exc()}")
            print(f"Error in render: {e}")  # Debug print
            # Try to render error message
            try:
                self.screen.fill((0, 0, 0))
                font = pygame.font.SysFont('arial', 24)
                error_text = font.render(f'Render Error: {e}', True, (255, 0, 0))
                error_rect = error_text.get_rect(center=self.screen.get_rect().center)
                self.screen.blit(error_text, error_rect)
                pygame.display.flip()
            except:
                pass
    

    
    def cleanup(self) -> None:
        """Cleanup all resources"""
        self.logger.info("Starting cleanup")
        
        try:
            # Cleanup game loop
            if hasattr(self, 'game_loop_manager'):
                self.game_loop_manager.cleanup()
            
            # Cleanup scenes
            if hasattr(self, 'scene_manager'):
                self.scene_manager.cleanup()
            
            # Cleanup subsystems
            if hasattr(self, 'audio_manager'):
                try:
                    self.audio_manager.cleanup()
                except Exception as e:
                    self.logger.error(f"Error cleaning up audio manager: {e}")
            
            if hasattr(self, 'resource_manager'):
                try:
                    self.resource_manager.cleanup()
                except Exception as e:
                    self.logger.error(f"Error cleaning up resource manager: {e}")
            
            if hasattr(self, 'performance_monitor'):
                try:
                    self.performance_monitor.cleanup()
                except Exception as e:
                    self.logger.error(f"Error cleaning up performance monitor: {e}")
            
            if hasattr(self, 'performance_optimizer'):
                try:
                    self.performance_optimizer.cleanup()
                except Exception as e:
                    self.logger.error(f"Error cleaning up performance optimizer: {e}")
            
            # Quit pygame
            try:
                pygame.quit()
            except Exception as e:
                self.logger.error(f"Error quitting pygame: {e}")
            
            self.logger.info("Cleanup completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


# Global instance management
_game_manager: Optional[GameManager] = None

def get_game_manager() -> GameManager:
    """Get the global game manager instance"""
    global _game_manager
    if _game_manager is None:
        _game_manager = GameManager()
    return _game_manager

def cleanup_game_manager() -> None:
    """Cleanup the global game manager instance"""
    global _game_manager
    if _game_manager:
        _game_manager.cleanup()
        _game_manager = None
