"""
UI Manager for centralized UI management
"""

import pygame
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from .logger import GameLogger
from .utils import draw_text_with_shadow, create_surface_with_alpha, get_center_rect

@dataclass
class UIElement:
    """Base class for UI elements"""
    id: str
    rect: pygame.Rect
    visible: bool = True
    enabled: bool = True
    alpha: int = 255

class UIButton(UIElement):
    """Button UI element"""
    def __init__(self, id: str, rect: pygame.Rect, text: str, font: pygame.font.Font,
                 normal_color: Tuple[int, int, int] = (100, 100, 100),
                 hover_color: Tuple[int, int, int] = (150, 150, 150),
                 text_color: Tuple[int, int, int] = (255, 255, 255)):
        super().__init__(id, rect)
        self.text = text
        self.font = font
        self.normal_color = normal_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.on_click = None

class UILabel(UIElement):
    """Label UI element"""
    def __init__(self, id: str, rect: pygame.Rect, text: str, font: pygame.font.Font,
                 color: Tuple[int, int, int] = (255, 255, 255)):
        super().__init__(id, rect)
        self.text = text
        self.font = font
        self.color = color

class UIProgressBar(UIElement):
    """Progress bar UI element"""
    def __init__(self, id: str, rect: pygame.Rect, max_value: float = 100.0,
                 current_value: float = 100.0, bg_color: Tuple[int, int, int] = (50, 50, 50),
                 fill_color: Tuple[int, int, int] = (255, 0, 0)):
        super().__init__(id, rect)
        self.max_value = max_value
        self.current_value = current_value
        self.bg_color = bg_color
        self.fill_color = fill_color

class UIManager:
    """Centralized UI management system"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.logger = GameLogger("UIManager")
        
        # UI elements storage
        self.elements: Dict[str, UIElement] = {}
        self.element_groups: Dict[str, List[str]] = {}
        
        # Font management
        self.fonts: Dict[str, pygame.font.Font] = {}
        self._load_default_fonts()
        
        # UI state
        self.hovered_element: Optional[str] = None
        self.focused_element: Optional[str] = None
        
        # Theme colors
        self.theme = {
            'background': (0, 0, 0),
            'text': (255, 255, 255),
            'text_shadow': (0, 0, 0),
            'button_normal': (100, 100, 100),
            'button_hover': (150, 150, 150),
            'button_disabled': (50, 50, 50),
            'health_bar': (255, 0, 0),
            'energy_bar': (0, 0, 255),
            'exp_bar': (255, 255, 0)
        }
    
    def _load_default_fonts(self) -> None:
        """Load default fonts"""
        try:
            # Try to load custom font
            font_path = "graphics/font/joystix.ttf"
            self.fonts['default'] = pygame.font.Font(font_path, 18)
            self.fonts['large'] = pygame.font.Font(font_path, 24)
            self.fonts['small'] = pygame.font.Font(font_path, 14)
            self.fonts['title'] = pygame.font.Font(font_path, 48)
        except Exception as e:
            self.logger.warning(f"Could not load custom font: {e}")
            # Fallback to default font
            self.fonts['default'] = pygame.font.Font(None, 18)
            self.fonts['large'] = pygame.font.Font(None, 24)
            self.fonts['small'] = pygame.font.Font(None, 14)
            self.fonts['title'] = pygame.font.Font(None, 48)
    
    def add_button(self, id: str, rect: pygame.Rect, text: str, 
                   font_size: str = 'default', on_click: callable = None) -> UIButton:
        """Add a button to the UI"""
        font = self.fonts.get(font_size, self.fonts['default'])
        button = UIButton(id, rect, text, font, 
                         self.theme['button_normal'], 
                         self.theme['button_hover'], 
                         self.theme['text'])
        button.on_click = on_click
        self.elements[id] = button
        self.logger.debug(f"Added button: {id}")
        return button
    
    def add_label(self, id: str, rect: pygame.Rect, text: str, 
                  font_size: str = 'default') -> UILabel:
        """Add a label to the UI"""
        font = self.fonts.get(font_size, self.fonts['default'])
        label = UILabel(id, rect, text, font, self.theme['text'])
        self.elements[id] = label
        self.logger.debug(f"Added label: {id}")
        return label
    
    def add_progress_bar(self, id: str, rect: pygame.Rect, max_value: float = 100.0,
                        current_value: float = 100.0, fill_color: Tuple[int, int, int] = None) -> UIProgressBar:
        """Add a progress bar to the UI"""
        if fill_color is None:
            fill_color = self.theme['health_bar']
        
        bar = UIProgressBar(id, rect, max_value, current_value, 
                           self.theme['background'], fill_color)
        self.elements[id] = bar
        self.logger.debug(f"Added progress bar: {id}")
        return bar
    
    def create_element_group(self, group_name: str, element_ids: List[str]) -> None:
        """Create a group of UI elements"""
        self.element_groups[group_name] = element_ids
        self.logger.debug(f"Created UI group: {group_name} with {len(element_ids)} elements")
    
    def show_group(self, group_name: str) -> None:
        """Show all elements in a group"""
        if group_name in self.element_groups:
            for element_id in self.element_groups[group_name]:
                if element_id in self.elements:
                    self.elements[element_id].visible = True
            self.logger.debug(f"Showed UI group: {group_name}")
    
    def hide_group(self, group_name: str) -> None:
        """Hide all elements in a group"""
        if group_name in self.element_groups:
            for element_id in self.element_groups[group_name]:
                if element_id in self.elements:
                    self.elements[element_id].visible = False
            self.logger.debug(f"Hidden UI group: {group_name}")
    
    def update_element(self, element_id: str, **kwargs) -> bool:
        """Update an element's properties"""
        if element_id in self.elements:
            element = self.elements[element_id]
            for key, value in kwargs.items():
                if hasattr(element, key):
                    setattr(element, key, value)
            return True
        return False
    
    def remove_element(self, element_id: str) -> bool:
        """Remove an element from the UI"""
        if element_id in self.elements:
            del self.elements[element_id]
            self.logger.debug(f"Removed UI element: {element_id}")
            return True
        return False
    
    def handle_mouse_motion(self, pos: Tuple[int, int]) -> None:
        """Handle mouse motion for hover effects"""
        self.hovered_element = None
        
        for element_id, element in self.elements.items():
            if not element.visible or not element.enabled:
                continue
                
            if element.rect.collidepoint(pos):
                if isinstance(element, UIButton):
                    element.is_hovered = True
                    self.hovered_element = element_id
                break
            elif isinstance(element, UIButton):
                element.is_hovered = False
    
    def handle_mouse_click(self, pos: Tuple[int, int], button: int = 1) -> Optional[str]:
        """Handle mouse click events"""
        if button == 1:  # Left click
            for element_id, element in self.elements.items():
                if not element.visible or not element.enabled:
                    continue
                    
                if element.rect.collidepoint(pos):
                    if isinstance(element, UIButton) and element.on_click:
                        element.on_click()
                    return element_id
        return None
    
    def render(self) -> None:
        """Render all visible UI elements"""
        for element in self.elements.values():
            if not element.visible:
                continue
            
            if isinstance(element, UIButton):
                self._render_button(element)
            elif isinstance(element, UILabel):
                self._render_label(element)
            elif isinstance(element, UIProgressBar):
                self._render_progress_bar(element)
    
    def _render_button(self, button: UIButton) -> None:
        """Render a button element"""
        # Choose color based on state
        if not button.enabled:
            color = self.theme['button_disabled']
        elif button.is_hovered:
            color = button.hover_color
        else:
            color = button.normal_color
        
        # Draw button background
        pygame.draw.rect(self.screen, color, button.rect)
        pygame.draw.rect(self.screen, self.theme['text'], button.rect, 2)
        
        # Draw text
        text_surface = button.font.render(button.text, True, button.text_color)
        text_rect = text_surface.get_rect(center=button.rect.center)
        self.screen.blit(text_surface, text_rect)
    
    def _render_label(self, label: UILabel) -> None:
        """Render a label element"""
        draw_text_with_shadow(self.screen, label.text, label.font, label.color,
                             label.rect.center, self.theme['text_shadow'])
    
    def _render_progress_bar(self, bar: UIProgressBar) -> None:
        """Render a progress bar element"""
        # Draw background
        pygame.draw.rect(self.screen, bar.bg_color, bar.rect)
        
        # Calculate fill width
        if bar.max_value > 0:
            fill_ratio = bar.current_value / bar.max_value
            fill_width = int(bar.rect.width * fill_ratio)
            
            if fill_width > 0:
                fill_rect = pygame.Rect(bar.rect.x, bar.rect.y, fill_width, bar.rect.height)
                pygame.draw.rect(self.screen, bar.fill_color, fill_rect)
        
        # Draw border
        pygame.draw.rect(self.screen, self.theme['text'], bar.rect, 1)
    
    def create_hud(self, player) -> None:
        """Create heads-up display for the player"""
        if not player:
            return
        
        # Health bar
        health_rect = pygame.Rect(10, 10, 200, 20)
        self.add_progress_bar('health_bar', health_rect, 
                             player.max_stats['health'], player.health,
                             self.theme['health_bar'])
        
        # Energy bar
        energy_rect = pygame.Rect(10, 35, 140, 20)
        self.add_progress_bar('energy_bar', energy_rect,
                             player.max_stats['energy'], player.energy,
                             self.theme['energy_bar'])
        
        # Experience bar
        exp_rect = pygame.Rect(10, 60, 200, 15)
        self.add_progress_bar('exp_bar', exp_rect,
                             100, player.exp % 100,  # Show current level progress
                             self.theme['exp_bar'])
        
        # Stats labels
        stats_rect = pygame.Rect(220, 10, 150, 100)
        self.add_label('stats_label', stats_rect, 
                      f"Level: {player.exp // 100}\n"
                      f"Attack: {player.stats['attack']}\n"
                      f"Magic: {player.stats['magic']}\n"
                      f"Speed: {player.stats['speed']}")
        
        # Create HUD group
        self.create_element_group('hud', ['health_bar', 'energy_bar', 'exp_bar', 'stats_label'])
    
    def update_hud(self, player) -> None:
        """Update HUD with current player stats"""
        if not player:
            return
        
        self.update_element('health_bar', current_value=player.health)
        self.update_element('energy_bar', current_value=player.energy)
        self.update_element('exp_bar', current_value=player.exp % 100)
        
        # Update stats label
        stats_text = (f"Level: {player.exp // 100}\n"
                     f"Attack: {player.stats['attack']}\n"
                     f"Magic: {player.stats['magic']}\n"
                     f"Speed: {player.stats['speed']}")
        self.update_element('stats_label', text=stats_text)
    
    def create_pause_menu(self) -> None:
        """Create pause menu UI"""
        screen_center = self.screen.get_rect().center
        
        # Title
        title_rect = pygame.Rect(0, screen_center[1] - 100, self.screen.get_width(), 50)
        self.add_label('pause_title', title_rect, "PAUSED", 'title')
        
        # Resume button
        resume_rect = pygame.Rect(screen_center[0] - 100, screen_center[1], 200, 40)
        self.add_button('resume_button', resume_rect, "Resume", 'large')
        
        # Settings button
        settings_rect = pygame.Rect(screen_center[0] - 100, screen_center[1] + 50, 200, 40)
        self.add_button('settings_button', settings_rect, "Settings", 'large')
        
        # Quit button
        quit_rect = pygame.Rect(screen_center[0] - 100, screen_center[1] + 100, 200, 40)
        self.add_button('quit_button', quit_rect, "Quit to Menu", 'large')
        
        # Create pause menu group
        self.create_element_group('pause_menu', ['pause_title', 'resume_button', 'settings_button', 'quit_button'])
    
    def cleanup(self) -> None:
        """Cleanup UI resources"""
        self.elements.clear()
        self.element_groups.clear()
        self.logger.info("UI manager cleanup completed")
