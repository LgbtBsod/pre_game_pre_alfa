import pygame
import logging
from typing import Optional, List, Dict, Any
from core.scene_manager import Scene
from core.input_manager import InputManager, InputAction
from core.game_state import GameState

class PauseScene(Scene):
    """Pause scene that handles pause menu and overlay"""
    
    def __init__(self, scene_manager, game_manager):
        super().__init__(scene_manager)
        self.game_manager = game_manager
        self.logger = logging.getLogger(__name__)
        self.input_manager: Optional[InputManager] = None
        self.font: Optional[pygame.font.Font] = None
        self.small_font: Optional[pygame.font.Font] = None
        self.overlay_surface: Optional[pygame.Surface] = None
        self.save_slots: List[Dict[str, Any]] = []
        self.selected_slot: int = 0
        self.show_save_menu: bool = False
        
    def initialize(self) -> None:
        """Initialize the pause scene"""
        try:
            self.input_manager = self.game_manager.input_manager
            
            # Create fonts
            self.font = pygame.font.Font(None, 74)
            self.small_font = pygame.font.Font(None, 36)
            
            # Create overlay surface
            screen_size = self.game_manager.screen.get_size()
            self.overlay_surface = pygame.Surface(screen_size)
            self.overlay_surface.set_alpha(128)
            self.overlay_surface.fill((0, 0, 0))
            
            # Load save slots
            self._load_save_slots()
            
            # Setup input handlers
            self._setup_input_handlers()
            
            self.logger.info("Pause scene initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize pause scene: {e}")
    
    def _load_save_slots(self):
        """Load available save slots"""
        try:
            if hasattr(self.game_manager, 'session_manager'):
                self.save_slots = self.game_manager.session_manager.get_available_save_slots()
            else:
                self.save_slots = []
        except Exception as e:
            self.logger.error(f"Error loading save slots: {e}")
            self.save_slots = []
    
    def _setup_input_handlers(self) -> None:
        """Setup input handlers for pause menu"""
        if not self.input_manager:
            return
            
        # Register pause toggle handler
        self.input_manager.register_action_handler(
            InputAction.PAUSE, 
            self._toggle_pause
        )
        
        # Register save menu handlers
        self.input_manager.register_action_handler(
            InputAction.MOVE_UP,
            self._select_previous_slot
        )
        
        self.input_manager.register_action_handler(
            InputAction.MOVE_DOWN,
            self._select_next_slot
        )
        
        self.input_manager.register_action_handler(
            InputAction.CONFIRM,
            self._save_game
        )
    
    def _select_previous_slot(self):
        """Select previous save slot"""
        if self.show_save_menu and self.save_slots:
            self.selected_slot = (self.selected_slot - 1) % len(self.save_slots)
    
    def _select_next_slot(self):
        """Select next save slot"""
        if self.show_save_menu and self.save_slots:
            self.selected_slot = (self.selected_slot + 1) % len(self.save_slots)
    
    def _save_game(self):
        """Save game to selected slot"""
        if self.show_save_menu and self.save_slots:
            try:
                slot_id = self.save_slots[self.selected_slot]["slot_id"]
                if hasattr(self.game_manager, 'session_manager'):
                    success = self.game_manager.session_manager.save_session_to_slot(slot_id)
                    if success:
                        self.logger.info(f"Game saved to slot {slot_id}")
                        self.show_save_menu = False
                    else:
                        self.logger.error("Failed to save game")
            except Exception as e:
                self.logger.error(f"Error saving game: {e}")
    
    def _toggle_pause(self) -> None:
        """Toggle pause state"""
        if self.game_manager.state_manager.is_in_state(GameState.PAUSED):
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
        
        if self.show_save_menu:
            self._render_save_menu(screen)
        else:
            self._render_pause_menu(screen)
    
    def _render_pause_menu(self, screen: pygame.Surface):
        """Render main pause menu"""
        # Render pause text
        text = self.font.render('ПАУЗА', True, (255, 255, 255))
        text_rect = text.get_rect(center=screen.get_rect().center)
        screen.blit(text, text_rect)
        
        # Render menu options
        y_offset = screen.get_rect().centery + 80
        
        # Resume option
        resume_text = self.small_font.render('ESC - Продолжить', True, (200, 200, 200))
        resume_rect = resume_text.get_rect(center=(screen.get_rect().centerx, y_offset))
        screen.blit(resume_text, resume_rect)
        
        # Save option
        y_offset += 40
        save_text = self.small_font.render('S - Сохранить игру', True, (200, 200, 200))
        save_rect = save_text.get_rect(center=(screen.get_rect().centerx, y_offset))
        screen.blit(save_text, save_rect)
        
        # Main menu option
        y_offset += 40
        menu_text = self.small_font.render('M - Главное меню', True, (200, 200, 200))
        menu_rect = menu_text.get_rect(center=(screen.get_rect().centerx, y_offset))
        screen.blit(menu_text, menu_rect)
    
    def _render_save_menu(self, screen: pygame.Surface):
        """Render save slots menu"""
        # Title
        title_text = self.font.render('СОХРАНИТЬ ИГРУ', True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(screen.get_rect().centerx, 100))
        screen.blit(title_text, title_rect)
        
        # Save slots
        y_offset = 200
        for i, slot in enumerate(self.save_slots):
            color = (255, 255, 0) if i == self.selected_slot else (200, 200, 200)
            
            # Slot info
            slot_text = f"Слот {slot['slot_id']}: {slot['save_name']}"
            if slot.get('player_level'):
                slot_text += f" (Уровень {slot['player_level']})"
            
            slot_surface = self.small_font.render(slot_text, True, color)
            slot_rect = slot_surface.get_rect(center=(screen.get_rect().centerx, y_offset))
            screen.blit(slot_surface, slot_rect)
            
            y_offset += 40
        
        # Instructions
        y_offset += 40
        instructions = [
            "↑↓ - Выбрать слот",
            "Enter - Сохранить",
            "ESC - Отмена"
        ]
        
        for instruction in instructions:
            inst_text = self.small_font.render(instruction, True, (150, 150, 150))
            inst_rect = inst_text.get_rect(center=(screen.get_rect().centerx, y_offset))
            screen.blit(inst_text, inst_rect)
            y_offset += 30
    
    def handle_events(self, events: list) -> None:
        """Handle pause scene events"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.show_save_menu:
                        self.show_save_menu = False
                    else:
                        self._toggle_pause()
                elif event.key == pygame.K_s and not self.show_save_menu:
                    self.show_save_menu = True
                    self._load_save_slots()  # Refresh slots
                elif event.key == pygame.K_m and not self.show_save_menu:
                    # Return to main menu
                    self.game_manager.state_manager.change_state(GameState.MAIN_MENU)
                    self.scene_manager.switch_scene('menu')
    
    def cleanup(self) -> None:
        """Cleanup pause scene resources"""
        self.logger.info("Pause scene cleanup completed")
