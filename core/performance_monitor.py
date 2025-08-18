import time
import psutil
import pygame
from typing import Dict, List, Optional, Tuple
from collections import deque
from .logger import GameLogger

class PerformanceMetrics:
    """Container for performance metrics"""
    
    def __init__(self):
        self.fps = 0.0
        self.frame_time = 0.0
        self.memory_usage = 0.0
        self.cpu_usage = 0.0
        self.render_time = 0.0
        self.update_time = 0.0
        self.event_time = 0.0

class PerformanceMonitor:
    """Enhanced performance monitoring system"""
    
    def __init__(self, history_size: int = 60):
        self.logger = GameLogger("PerformanceMonitor")
        self.history_size = history_size
        
        # Performance history
        self.fps_history = deque(maxlen=history_size)
        self.frame_time_history = deque(maxlen=history_size)
        self.memory_history = deque(maxlen=history_size)
        self.cpu_history = deque(maxlen=history_size)
        
        # Timing variables
        self.frame_start_time = 0.0
        self.last_frame_time = 0.0
        self.frame_count = 0
        self.last_fps_update = 0.0
        
        # Performance thresholds
        self.fps_threshold = 30.0
        self.frame_time_threshold = 33.33  # 30 FPS equivalent
        self.memory_threshold = 500.0  # MB
        self.cpu_threshold = 80.0  # Percentage
        
        # Monitoring state
        self.is_monitoring = True
        self.show_metrics = False
        self.warnings_enabled = True
        
        # Process info
        self.process = psutil.Process()
        
        self.logger.info("Performance monitor initialized")
    
    def start_frame(self) -> None:
        """Start timing a new frame"""
        self.frame_start_time = time.time()
    
    def end_frame(self) -> None:
        """End timing the current frame and update metrics"""
        if not self.is_monitoring:
            return
            
        current_time = time.time()
        frame_time = (current_time - self.frame_start_time) * 1000  # Convert to milliseconds
        
        # Update frame time history
        self.frame_time_history.append(frame_time)
        
        # Calculate FPS
        self.frame_count += 1
        if current_time - self.last_fps_update >= 1.0:  # Update FPS every second
            if self.last_fps_update > 0:  # Avoid division by zero
                self.fps = self.frame_count / (current_time - self.last_fps_update)
            else:
                self.fps = 0.0
            self.fps_history.append(self.fps)
            self.frame_count = 0
            self.last_fps_update = current_time
        
        # Update memory usage
        try:
            memory_mb = self.process.memory_info().rss / 1024 / 1024
            self.memory_history.append(memory_mb)
        except Exception as e:
            self.logger.warning(f"Could not get memory usage: {e}")
        
        # Update CPU usage
        try:
            cpu_percent = self.process.cpu_percent()
            self.cpu_history.append(cpu_percent)
        except Exception as e:
            self.logger.warning(f"Could not get CPU usage: {e}")
        
        # Check for performance issues
        self._check_performance_issues()
    
    def _check_performance_issues(self) -> None:
        """Check for performance issues and log warnings"""
        if not self.warnings_enabled:
            return
            
        # Check FPS
        if self.fps < self.fps_threshold and len(self.fps_history) > 0:
            avg_fps = sum(self.fps_history) / len(self.fps_history)
            if avg_fps < self.fps_threshold:
                self.logger.warning(f"Low FPS detected: {avg_fps:.1f} FPS")
        
        # Check frame time
        if len(self.frame_time_history) > 0:
            avg_frame_time = sum(self.frame_time_history) / len(self.frame_time_history)
            if avg_frame_time > self.frame_time_threshold:
                self.logger.warning(f"High frame time detected: {avg_frame_time:.2f}ms")
        
        # Check memory usage
        if len(self.memory_history) > 0:
            current_memory = self.memory_history[-1]
            if current_memory > self.memory_threshold:
                self.logger.warning(f"High memory usage detected: {current_memory:.1f}MB")
        
        # Check CPU usage
        if len(self.cpu_history) > 0:
            current_cpu = self.cpu_history[-1]
            if current_cpu > self.cpu_threshold:
                self.logger.warning(f"High CPU usage detected: {current_cpu:.1f}%")
    
    def get_current_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics"""
        metrics = PerformanceMetrics()
        
        # Current FPS
        if len(self.fps_history) > 0:
            metrics.fps = self.fps_history[-1]
        
        # Current frame time
        if len(self.frame_time_history) > 0:
            metrics.frame_time = self.frame_time_history[-1]
        
        # Current memory usage
        if len(self.memory_history) > 0:
            metrics.memory_usage = self.memory_history[-1]
        
        # Current CPU usage
        if len(self.cpu_history) > 0:
            metrics.cpu_usage = self.cpu_history[-1]
        
        return metrics
    
    def get_average_metrics(self) -> PerformanceMetrics:
        """Get average performance metrics over the history period"""
        metrics = PerformanceMetrics()
        
        # Average FPS
        if self.fps_history:
            metrics.fps = sum(self.fps_history) / len(self.fps_history)
        
        # Average frame time
        if self.frame_time_history:
            metrics.frame_time = sum(self.frame_time_history) / len(self.frame_time_history)
        
        # Average memory usage
        if self.memory_history:
            metrics.memory_usage = sum(self.memory_history) / len(self.memory_history)
        
        # Average CPU usage
        if self.cpu_history:
            metrics.cpu_usage = sum(self.cpu_history) / len(self.cpu_history)
        
        return metrics
    
    def render_metrics(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Render performance metrics on screen"""
        if not self.show_metrics:
            return
            
        metrics = self.get_current_metrics()
        
        # Create metrics text
        lines = [
            f"FPS: {metrics.fps:.1f}",
            f"Frame Time: {metrics.frame_time:.1f}ms",
            f"Memory: {metrics.memory_usage:.1f}MB",
            f"CPU: {metrics.cpu_usage:.1f}%"
        ]
        
        # Render each line
        y_offset = 10
        for line in lines:
            text_surface = font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (10, y_offset))
            y_offset += 20
    
    def set_thresholds(self, fps: Optional[float] = None, frame_time: Optional[float] = None,
                      memory: Optional[float] = None, cpu: Optional[float] = None) -> None:
        """Set performance thresholds"""
        if fps is not None:
            self.fps_threshold = fps
        if frame_time is not None:
            self.frame_time_threshold = frame_time
        if memory is not None:
            self.memory_threshold = memory
        if cpu is not None:
            self.cpu_threshold = cpu
    
    def toggle_monitoring(self) -> None:
        """Toggle performance monitoring on/off"""
        self.is_monitoring = not self.is_monitoring
        self.logger.info(f"Performance monitoring {'enabled' if self.is_monitoring else 'disabled'}")
    
    def toggle_metrics_display(self) -> None:
        """Toggle metrics display on/off"""
        self.show_metrics = not self.show_metrics
    
    def clear_history(self) -> None:
        """Clear performance history"""
        self.fps_history.clear()
        self.frame_time_history.clear()
        self.memory_history.clear()
        self.cpu_history.clear()
        self.logger.info("Performance history cleared")
    
    def get_performance_report(self) -> Dict[str, float]:
        """Get a comprehensive performance report"""
        avg_metrics = self.get_average_metrics()
        
        return {
            'average_fps': avg_metrics.fps,
            'average_frame_time': avg_metrics.frame_time,
            'average_memory_usage': avg_metrics.memory_usage,
            'average_cpu_usage': avg_metrics.cpu_usage,
            'min_fps': min(self.fps_history) if self.fps_history else 0,
            'max_fps': max(self.fps_history) if self.fps_history else 0,
            'min_frame_time': min(self.frame_time_history) if self.frame_time_history else 0,
            'max_frame_time': max(self.frame_time_history) if self.frame_time_history else 0
        }
    
    def cleanup(self) -> None:
        """Cleanup performance monitor resources"""
        self.logger.info("Performance monitor cleanup completed")
