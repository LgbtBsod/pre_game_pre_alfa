import pygame
from typing import Optional, List, Tuple
from code.core.scene_manager import Scene
from code.core.input_manager import InputManager, InputAction
from code.core.game_state import GameState

class MenuItem:
    """Represents a menu item"""
    
    def __init__(self, text: str, action: callable, position: Tuple[int, int]):
        self.text = text
        self.action = action
        self.position = position
        self.is_selected = False
        self.color = (255, 255, 255)
        self.selected_color = (255, 255, 0)
        print(f"Created MenuItem: '{text}' at position {position}")  # Debug print

class MenuScene(Scene):
    """Main menu scene that handles menu navigation"""
    
    def __init__(self, scene_manager, game_manager):
        super().__init__(scene_manager)
        self.game_manager = game_manager
        self.input_manager: Optional[InputManager] = None
        self.font: Optional[pygame.font.Font] = None
        self.title_font: Optional[pygame.font.Font] = None
        self.menu_items: List[MenuItem] = []
        self.selected_index = 0
        print("MenuScene initialized")  # Debug print
        
    def initialize(self) -> None:
        """Initialize the menu scene"""
        try:
            self.logger.info("Starting menu scene initialization")
            print("MenuScene.initialize() called")  # Debug print
            
            self.input_manager = self.game_manager.input_manager
            self.logger.info("Input manager set")
            print("Input manager set")  # Debug print
            
            # Create fonts with fallback
            try:
                self.title_font = pygame.font.Font(None, 96)
                self.font = pygame.font.Font(None, 48)
                self.logger.info("Fonts created successfully")
                print("Fonts created successfully")  # Debug print
            except Exception as font_error:
                self.logger.warning(f"Font creation failed, using fallback: {font_error}")
                # Fallback to default font
                self.title_font = pygame.font.SysFont('arial', 96)
                self.font = pygame.font.SysFont('arial', 48)
                self.logger.info("Fallback fonts created")
                print("Fallback fonts created")  # Debug print
            
            # Create menu items
            self._create_menu_items()
            self.logger.info(f"Menu items created: {len(self.menu_items)} items")
            print(f"Menu items created: {len(self.menu_items)} items")  # Debug print
            
            # Setup input handlers
            self._setup_input_handlers()
            self.logger.info("Input handlers setup completed")
            print("Input handlers setup completed")  # Debug print
            
            self.logger.info("Menu scene initialized successfully")
            print("Menu scene initialized successfully")  # Debug print
            
        except Exception as e:
            self.logger.error(f"Failed to initialize menu scene: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            print(f"Failed to initialize menu scene: {e}")  # Debug print
    
    def _create_menu_items(self) -> None:
        """Create menu items"""
        try:
            print("_create_menu_items() called")  # Debug print
            
            # Get screen from game manager
            screen = getattr(self.game_manager, 'screen', None)
            if screen:
                screen_center = screen.get_rect().center
                start_y = screen_center[1] + 50
                self.logger.info(f"Using screen dimensions: {screen.get_width()}x{screen.get_height()}")
                self.logger.info(f"Screen center: {screen_center}, start_y: {start_y}")
                print(f"Using screen dimensions: {screen.get_width()}x{screen.get_height()}")  # Debug print
                print(f"Screen center: {screen_center}, start_y: {start_y}")  # Debug print
            else:
                # Fallback positions
                screen_center = (640, 360)
                start_y = 410
                self.logger.warning("Screen not available, using fallback positions")
                self.logger.info(f"Fallback positions - center: {screen_center}, start_y: {start_y}")
                print("Screen not available, using fallback positions")  # Debug print
                print(f"Fallback positions - center: {screen_center}, start_y: {start_y}")  # Debug print
            
            self.menu_items = [
                MenuItem("Start Game", self._start_game, (screen_center[0], start_y)),
                MenuItem("Load Game", self._load_game, (screen_center[0], start_y + 60)),
                MenuItem("Settings", self._open_settings, (screen_center[0], start_y + 120)),
                MenuItem("Quit", self._quit_game, (screen_center[0], start_y + 180))
            ]
            
            # Set first item as selected
            if self.menu_items:
                self.menu_items[0].is_selected = True
                self.logger.info(f"Created {len(self.menu_items)} menu items")
                for i, item in enumerate(self.menu_items):
                    self.logger.debug(f"Menu item {i}: '{item.text}' at position {item.position}")
                print(f"Created {len(self.menu_items)} menu items")  # Debug print
        except Exception as e:
            self.logger.error(f"Error creating menu items: {e}")
            import traceback
            self.logger.error(f"Create menu items traceback: {traceback.format_exc()}")
            print(f"Error creating menu items: {e}")  # Debug print
            # Create fallback menu items
            self.menu_items = [
                MenuItem("Start Game", self._start_game, (640, 410)),
                MenuItem("Load Game", self._load_game, (640, 470)),
                MenuItem("Settings", self._open_settings, (640, 530)),
                MenuItem("Quit", self._quit_game, (640, 590))
            ]
            if self.menu_items:
                self.menu_items[0].is_selected = True
                self.logger.info("Created fallback menu items")
                for i, item in enumerate(self.menu_items):
                    self.logger.debug(f"Fallback menu item {i}: '{item.text}' at position {item.position}")
                print("Created fallback menu items")  # Debug print
    
    def _setup_input_handlers(self) -> None:
        """Setup input handlers for menu navigation"""
        try:
            if not self.input_manager:
                self.logger.warning("No input manager available for menu navigation")
                print("No input manager available for menu navigation")  # Debug print
                return
                
            self.logger.info("Setting up input handlers for menu navigation")
            print("Setting up input handlers for menu navigation")  # Debug print
            
            # Register menu navigation handlers
            self.input_manager.register_action_handler(
                InputAction.MOVE_UP, 
                self._select_previous_item
            )
            self.logger.debug("Registered MOVE_UP handler")
            print("Registered MOVE_UP handler")  # Debug print
            
            self.input_manager.register_action_handler(
                InputAction.MOVE_DOWN, 
                self._select_next_item
            )
            self.logger.debug("Registered MOVE_DOWN handler")
            print("Registered MOVE_DOWN handler")  # Debug print
            
            self.input_manager.register_action_handler(
                InputAction.INTERACT, 
                self._select_current_item
            )
            self.logger.debug("Registered INTERACT handler")
            print("Registered INTERACT handler")  # Debug print
            
            self.logger.info("Input handlers setup completed successfully")
            print("Input handlers setup completed successfully")  # Debug print
        except Exception as e:
            self.logger.error(f"Error setting up input handlers: {e}")
            import traceback
            self.logger.error(f"Input handlers traceback: {traceback.format_exc()}")
            print(f"Error setting up input handlers: {e}")  # Debug print
    
    def _select_previous_item(self) -> None:
        """Select the previous menu item"""
        try:
            if self.menu_items:
                self.menu_items[self.selected_index].is_selected = False
                self.selected_index = (self.selected_index - 1) % len(self.menu_items)
                self.menu_items[self.selected_index].is_selected = True
                self.logger.debug(f"Selected previous item: {self.selected_index} - {self.menu_items[self.selected_index].text}")
                print(f"Selected previous item: {self.selected_index} - {self.menu_items[self.selected_index].text}")  # Debug print
        except Exception as e:
            self.logger.error(f"Error selecting previous item: {e}")
    
    def _select_next_item(self) -> None:
        """Select the next menu item"""
        try:
            if self.menu_items:
                self.menu_items[self.selected_index].is_selected = False
                self.selected_index = (self.selected_index + 1) % len(self.menu_items)
                self.menu_items[self.selected_index].is_selected = True
                self.logger.debug(f"Selected next item: {self.selected_index} - {self.menu_items[self.selected_index].text}")
                print(f"Selected next item: {self.selected_index} - {self.selected_index} - {self.menu_items[self.selected_index].text}")  # Debug print
        except Exception as e:
            self.logger.error(f"Error selecting next item: {e}")
    
    def _select_current_item(self) -> None:
        """Execute the action of the currently selected item"""
        try:
            if self.menu_items:
                current_item = self.menu_items[self.selected_index]
                self.logger.info(f"Executing action for menu item: {current_item.text}")
                print(f"Executing action for menu item: {current_item.text}")  # Debug print
                current_item.action()
        except Exception as e:
            self.logger.error(f"Error selecting current item: {e}")
    
    def _start_game(self) -> None:
        """Start the game"""
        try:
            self.logger.info("Starting game...")
            if hasattr(self.game_manager, 'state_manager'):
                self.game_manager.state_manager.change_state(GameState.PLAYING)
                self.logger.info("Game state changed to PLAYING")
                print("Game state changed to PLAYING")  # Debug print
            if hasattr(self.game_manager, 'scene_manager'):
                self.scene_manager.switch_scene('game')
                self.logger.info("Switched to game scene")
                print("Switched to game scene")  # Debug print
            self.logger.info("Game started successfully")
            print("Game started successfully")  # Debug print
        except Exception as e:
            self.logger.error(f"Error starting game: {e}")
            import traceback
            self.logger.error(f"Start game traceback: {traceback.format_exc()}")
            print(f"Error starting game: {e}")  # Debug print
    
    def _open_settings(self) -> None:
        """Open settings menu"""
        try:
            # TODO: Implement settings scene
            self.logger.info("Settings menu requested")
            print("Settings menu requested")  # Debug print
        except Exception as e:
            self.logger.error(f"Error opening settings: {e}")
            print(f"Error opening settings: {e}")  # Debug print
    
    def _load_game(self) -> None:
        """Load saved game"""
        try:
            # TODO: Implement save/load system
            self.logger.info("Load game requested")
            print("Load game requested")  # Debug print
            # For now, just start a new game
            self._start_game()
        except Exception as e:
            self.logger.error(f"Error loading game: {e}")
            print(f"Error loading game: {e}")  # Debug print
    
    def _quit_game(self) -> None:
        """Quit the game"""
        try:
            self.logger.info("Quitting game...")
            print("Quitting game...")  # Debug print
            if hasattr(self.game_manager, 'running'):
                self.game_manager.running = False
                self.logger.info("Game running flag set to False")
                print("Game running flag set to False")  # Debug print
        except Exception as e:
            self.logger.error(f"Error quitting game: {e}")
            print(f"Error quitting game: {e}")  # Debug print
    
    def update(self, dt: float) -> None:
        """Update menu scene logic"""
        try:
            # Menu scene doesn't need much updating
            pass
        except Exception as e:
            self.logger.error(f"Error updating menu scene: {e}")
    
    def render(self, screen: pygame.Surface) -> None:
        """Render the menu scene"""
        try:
            self.logger.debug(f"Rendering menu scene on screen: {screen.get_width()}x{screen.get_height()}")
            print(f"Rendering menu scene on screen: {screen.get_width()}x{screen.get_height()}")  # Debug print
            
            # Clear screen
            screen.fill((0, 0, 0))
            
            if not self.title_font or not self.font:
                # Render fallback text if fonts failed to load
                fallback_font = pygame.font.SysFont('arial', 48)
                fallback_text = fallback_font.render('ZELDA GAME - Loading...', True, (255, 255, 255))
                fallback_rect = fallback_text.get_rect(center=screen.get_rect().center)
                screen.blit(fallback_text, fallback_rect)
                self.logger.warning("Rendering fallback text due to missing fonts")
                return
                
            # Render title
            title_text = self.title_font.render('ZELDA GAME', True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(screen.get_rect().centerx, screen.get_rect().centery - 100))
            screen.blit(title_text, title_rect)
            self.logger.debug("Title rendered")
            print("Title rendered")  # Debug print
            
            # Render menu items
            if not self.menu_items:
                self.logger.warning("No menu items to render")
                print("No menu items to render")  # Debug print
            else:
                self.logger.debug(f"Rendering {len(self.menu_items)} menu items")
                print(f"Rendering {len(self.menu_items)} menu items")  # Debug print
                for i, item in enumerate(self.menu_items):
                    color = item.selected_color if item.is_selected else item.color
                    text = self.font.render(item.text, True, color)
                    text_rect = text.get_rect(center=item.position)
                    screen.blit(text, text_rect)
                    self.logger.debug(f"Rendered menu item {i}: {item.text} at {item.position}")
                    print(f"Rendered menu item {i}: {item.text} at {item.position}")  # Debug print
                
            # Render instructions
            instruction_font = pygame.font.SysFont('arial', 24)
            instructions = [
                "Use UP/DOWN arrows to navigate",
                "Press ENTER to select",
                "Press ESC to quit"
            ]
            for i, instruction in enumerate(instructions):
                instruction_text = instruction_font.render(instruction, True, (128, 128, 128))
                instruction_rect = instruction_text.get_rect(center=(screen.get_rect().centerx, screen.get_rect().centery + 250 + i * 30))
                screen.blit(instruction_text, instruction_rect)
            
            self.logger.debug("Menu scene render completed successfully")
            print("Menu scene render completed successfully")  # Debug print
                
        except Exception as e:
            self.logger.error(f"Error rendering menu scene: {e}")
            import traceback
            self.logger.error(f"Render traceback: {traceback.format_exc()}")
            print(f"Error rendering menu scene: {e}")  # Debug print
            # Render error message
            try:
                error_font = pygame.font.SysFont('arial', 24)
                error_text = error_font.render('Error rendering menu', True, (255, 0, 0))
                error_rect = error_text.get_rect(center=screen.get_rect().center)
                screen.blit(error_text, error_rect)
            except:
                pass
    
    def handle_events(self, events: list) -> None:
        """Handle menu scene events"""
        try:
            self.logger.debug(f"Handling {len(events)} events in menu scene")
            print(f"Handling {len(events)} events in menu scene")  # Debug print
            for event in events:
                # Handle pygame events directly
                if hasattr(event, 'type'):
                    if event.type == pygame.KEYDOWN:
                        self.logger.debug(f"Key pressed: {event.key}")
                        print(f"Key pressed: {event.key}")  # Debug print
                        if event.key == pygame.K_UP:
                            self._select_previous_item()
                        elif event.key == pygame.K_DOWN:
                            self._select_next_item()
                        elif event.key == pygame.K_RETURN:
                            self._select_current_item()
                        elif event.key == pygame.K_ESCAPE:
                            self._quit_game()
        except Exception as e:
            self.logger.error(f"Error handling menu events: {e}")
            import traceback
            self.logger.error(f"Menu events traceback: {traceback.format_exc()}")
            print(f"Error handling menu events: {e}")  # Debug print
    
    def cleanup(self) -> None:
        """Cleanup menu scene resources"""
        try:
            self.logger.info("Menu scene cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during menu scene cleanup: {e}")
