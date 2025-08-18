"""
Game Loop Manager for handling the main game loop
"""

import pygame
import time
from typing import Optional, Callable, Dict, Any
from .logger import GameLogger
from .performance_monitor import PerformanceMonitor

class GameLoopManager:
    """Manages the main game loop according to Single Responsibility Principle"""
    
    def __init__(self, target_fps: int = 60):
        self.logger = GameLogger("GameLoopManager")
        
        # Game loop properties
        self.target_fps = target_fps
        self.target_frame_time = 1.0 / target_fps
        self.running = False
        
        # Timing
        self.clock = pygame.time.Clock()
        self.last_time = time.time()
        self.delta_time = 0.0
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor()
        
        # Loop callbacks
        self.callbacks: Dict[str, Callable] = {}
        
        # Loop statistics
        self.stats = {
            'frames_processed': 0,
            'total_time': 0.0,
            'average_fps': 0.0
        }
        
        self.logger.info(f"Game loop manager initialized with target FPS: {target_fps}")
    
    def set_callbacks(self, callbacks: Dict[str, Callable]) -> None:
        """Set game loop callbacks"""
        self.callbacks.update(callbacks)
        self.logger.debug(f"Set {len(callbacks)} game loop callbacks")
    
    def start(self) -> None:
        """Start the game loop"""
        self.running = True
        self.last_time = time.time()
        self.logger.info("Game loop started")
        
        try:
            while self.running:
                self._process_frame()
        except Exception as e:
            self.logger.error(f"Game loop error: {e}")
            self.running = False
    
    def stop(self) -> None:
        """Stop the game loop"""
        self.running = False
        self.logger.info("Game loop stopped")
    
    def _process_frame(self) -> None:
        """Process a single frame"""
        try:
            # Start frame timing
            if hasattr(self, 'performance_monitor'):
                try:
                    self.performance_monitor.start_frame()
                except Exception as e:
                    self.logger.error(f"Error starting frame timing: {e}")
            
            # Calculate delta time
            current_time = time.time()
            self.delta_time = current_time - self.last_time
            self.last_time = current_time
            
            # Update statistics
            self.stats['frames_processed'] += 1
            self.stats['total_time'] += self.delta_time
            
            # Process frame callbacks
            if 'handle_events' in self.callbacks:
                self._handle_events()
            if 'update' in self.callbacks:
                self._update()
            if 'render' in self.callbacks:
                self._render()
            
            # End frame timing
            if hasattr(self, 'performance_monitor'):
                try:
                    self.performance_monitor.end_frame()
                except Exception as e:
                    self.logger.error(f"Error ending frame timing: {e}")
            
            # Cap frame rate
            try:
                self.clock.tick(self.target_fps)
            except Exception as e:
                self.logger.error(f"Error capping frame rate: {e}")
            
            # Update average FPS
            if self.stats['total_time'] > 0:
                self.stats['average_fps'] = self.stats['frames_processed'] / self.stats['total_time']
                
        except Exception as e:
            self.logger.error(f"Error in game loop: {e}")
            # Don't stop the game loop for frame processing errors
            # Just log the error and continue
    
    def _handle_events(self) -> None:
        """Handle events callback"""
        if 'handle_events' in self.callbacks:
            try:
                self.callbacks['handle_events']()
            except Exception as e:
                self.logger.error(f"Error in handle_events callback: {e}")
                # Don't stop the game loop for event handling errors
        else:
            # Don't log warning every frame, just once
            if not hasattr(self, '_events_warning_logged'):
                self.logger.warning("No handle_events callback registered")
                self._events_warning_logged = True
    
    def _update(self) -> None:
        """Update callback"""
        if 'update' in self.callbacks:
            try:
                self.callbacks['update'](self.delta_time)
            except Exception as e:
                self.logger.error(f"Error in update callback: {e}")
                # Don't stop the game loop for update errors
        else:
            # Don't log warning every frame, just once
            if not hasattr(self, '_update_warning_logged'):
                self.logger.warning("No update callback registered")
                self._update_warning_logged = True
    
    def _render(self) -> None:
        """Render callback"""
        if 'render' in self.callbacks:
            try:
                self.callbacks['render']()
            except Exception as e:
                self.logger.error(f"Error in render callback: {e}")
                # Don't stop the game loop for render errors
        else:
            # Don't log warning every frame, just once
            if not hasattr(self, '_render_warning_logged'):
                self.logger.warning("No render callback registered")
                self._render_warning_logged = True
    
    def get_delta_time(self) -> float:
        """Get the current delta time"""
        return self.delta_time
    
    def get_fps(self) -> float:
        """Get the current FPS"""
        return self.clock.get_fps()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        metrics = self.performance_monitor.get_current_metrics()
        return {
            'fps': self.get_fps(),
            'delta_time': self.delta_time,
            'frame_time': metrics.frame_time,
            'memory_usage': metrics.memory_usage,
            'cpu_usage': metrics.cpu_usage,
            'frames_processed': self.stats['frames_processed'],
            'average_fps': self.stats['average_fps']
        }
    
    def set_target_fps(self, fps: int) -> None:
        """Set the target FPS"""
        self.target_fps = fps
        self.target_frame_time = 1.0 / fps
        self.logger.info(f"Target FPS set to: {fps}")
    
    def toggle_performance_monitoring(self) -> None:
        """Toggle performance monitoring"""
        self.performance_monitor.toggle_monitoring()
    
    def toggle_metrics_display(self) -> None:
        """Toggle metrics display"""
        self.performance_monitor.toggle_metrics_display()
    
    def get_loop_statistics(self) -> Dict[str, Any]:
        """Get loop statistics"""
        return {
            'running': self.running,
            'target_fps': self.target_fps,
            'current_fps': self.get_fps(),
            'delta_time': self.delta_time,
            'frames_processed': self.stats['frames_processed'],
            'total_time': self.stats['total_time'],
            'average_fps': self.stats['average_fps'],
            'performance_metrics': self.get_performance_metrics()
        }
    
    def reset_statistics(self) -> None:
        """Reset loop statistics"""
        self.stats = {
            'frames_processed': 0,
            'total_time': 0.0,
            'average_fps': 0.0
        }
        self.performance_monitor.clear_history()
        self.logger.info("Game loop statistics reset")
    
    def cleanup(self) -> None:
        """Cleanup game loop resources"""
        try:
            self.stop()
            if hasattr(self, 'performance_monitor'):
                try:
                    self.performance_monitor.cleanup()
                except Exception as e:
                    self.logger.error(f"Error cleaning up performance monitor: {e}")
            self.callbacks.clear()
            self.logger.info("Game loop manager cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during game loop cleanup: {e}")
