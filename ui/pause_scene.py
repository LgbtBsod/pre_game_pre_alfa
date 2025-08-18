import pygame
from typing import Optional
from core.scene_manager import Scene
from core.input_manager import InputManager, InputAction
from core.game_state import GameState

class PauseScene(Scene):
    """Pause scene that handles pause menu and overlay"""
    
    def __init__(self, scene_manager, game_manager):
        super().__init__(scene_manager)
        self.game_manager = game_manager
        self.input_manager: Optional[InputManager] = None
        self.font: Optional[pygame.font.Font] = None
        self.overlay_surface: Optional[pygame.Surface] = None
        
    def initialize(self) -> None:
        """Initialize the pause scene"""
        try:
            self.input_manager = self.game_manager.input_manager
            
            # Create font for pause text
            self.font = pygame.font.Font(None, 74)
            
            # Create overlay surface
            screen_size = self.game_manager.screen.get_size()
            self.overlay_surface = pygame.Surface(screen_size)
            self.overlay_surface.set_alpha(128)
            self.overlay_surface.fill((0, 0, 0))
            
            # Setup input handlers
            self._setup_input_handlers()
            
            self.logger.info("Pause scene initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize pause scene: {e}")
    
    def _setup_input_handlers(self) -> None:
        """Setup input handlers for pause menu"""
        if not self.input_manager:
            return
            
        # Register pause toggle handler
        self.input_manager.register_action_handler(
            InputAction.PAUSE, 
            self._toggle_pause
        )
    
    def _toggle_pause(self) -> None:
        """Toggle pause state"""
        if self.game_manager.state_manager.is_state(GameState.PAUSED):
            # Resume game
            self.game_manager.state_manager.change_state(GameState.PLAYING)
            self.game_manager.audio_manager.unpause_music()
            self.scene_manager.switch_scene('game')
        else:
            # Pause game
            self.game_manager.state_manager.change_state(GameState.PAUSED)
            self.game_manager.audio_manager.pause_music()
    
    def update(self, dt: float) -> None:
        """Update pause scene logic"""
        # Pause scene doesn't need much updating
        pass
    
    def render(self, screen: pygame.Surface) -> None:
        """Render the pause overlay"""
        if not self.overlay_surface or not self.font:
            return
            
        # Draw semi-transparent overlay
        screen.blit(self.overlay_surface, (0, 0))
        
        # Render pause text
        text = self.font.render('PAUSED', True, (255, 255, 255))
        text_rect = text.get_rect(center=screen.get_rect().center)
        screen.blit(text, text_rect)
        
        # Render instructions
        instruction_font = pygame.font.Font(None, 36)
        instruction_text = instruction_font.render('Press ESC to resume', True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(screen.get_rect().centerx, screen.get_rect().centery + 60))
        screen.blit(instruction_text, instruction_rect)
    
    def handle_events(self, events: list) -> None:
        """Handle pause scene events"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._toggle_pause()
    
    def cleanup(self) -> None:
        """Cleanup pause scene resources"""
        self.logger.info("Pause scene cleanup completed")
