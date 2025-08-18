"""
Performance Optimizer for managing game performance
"""

import time
import psutil
from typing import Dict, List, Optional, Any, Callable
from .logger import GameLogger
from .performance_monitor import PerformanceMonitor

class PerformanceOptimizer:
    """Manages performance optimization according to Single Responsibility Principle"""
    
    def __init__(self, performance_monitor: PerformanceMonitor):
        self.performance_monitor = performance_monitor
        self.logger = GameLogger("PerformanceOptimizer")
        
        # Performance thresholds
        self.thresholds = {
            'fps_low': 30,
            'fps_critical': 15,
            'cpu_high': 80,
            'cpu_critical': 95,
            'memory_high': 80,
            'memory_critical': 95
        }
        
        # Optimization strategies
        self.optimization_strategies = {
            'fps_low': self._optimize_for_low_fps,
            'fps_critical': self._optimize_for_critical_fps,
            'cpu_high': self._optimize_for_high_cpu,
            'cpu_critical': self._optimize_for_critical_cpu,
            'memory_high': self._optimize_for_high_memory,
            'memory_critical': self._optimize_for_critical_memory
        }
        
        # Current optimizations
        self.active_optimizations: List[str] = []
        
        # Optimization callbacks
        self.callbacks: Dict[str, Callable] = {}
        
        # Performance history
        self.performance_history: List[Dict[str, Any]] = []
        self.max_history_size = 100
        
        # Auto-optimization settings
        self.auto_optimize = True
        self.optimization_cooldown = 5.0  # seconds
        self.last_optimization_time = 0.0
        
        self.logger.info("Performance optimizer initialized")
    
    def set_callbacks(self, callbacks: Dict[str, Callable]) -> None:
        """Set optimization callbacks"""
        self.callbacks.update(callbacks)
        self.logger.debug(f"Set {len(callbacks)} optimization callbacks")
    
    def set_thresholds(self, thresholds: Dict[str, float]) -> None:
        """Set performance thresholds"""
        self.thresholds.update(thresholds)
        self.logger.info(f"Updated performance thresholds: {thresholds}")
    
    def update(self, delta_time: float) -> None:
        """Update performance optimizer"""
        if not self.auto_optimize:
            return
        
        current_time = time.time()
        if current_time - self.last_optimization_time < self.optimization_cooldown:
            return
        
        # Get current performance metrics
        metrics = self.performance_monitor.get_current_metrics()
        if not metrics:
            return
        
        # Store performance history
        self._store_performance_data(metrics)
        
        # Check for performance issues
        issues = self._detect_performance_issues(metrics)
        
        if issues:
            self._apply_optimizations(issues)
            self.last_optimization_time = current_time
    
    def _store_performance_data(self, metrics: Any) -> None:
        """Store performance data in history"""
        performance_data = {
            'timestamp': time.time(),
            'fps': metrics.fps,
            'frame_time': metrics.frame_time,
            'cpu_usage': metrics.cpu_usage,
            'memory_usage': metrics.memory_usage
        }
        
        self.performance_history.append(performance_data)
        
        # Limit history size
        if len(self.performance_history) > self.max_history_size:
            self.performance_history.pop(0)
    
    def _detect_performance_issues(self, metrics: Any) -> List[str]:
        """Detect performance issues based on thresholds"""
        issues = []
        
        # Check FPS
        if metrics.fps < self.thresholds['fps_critical']:
            issues.append('fps_critical')
        elif metrics.fps < self.thresholds['fps_low']:
            issues.append('fps_low')
        
        # Check CPU usage
        if metrics.cpu_usage > self.thresholds['cpu_critical']:
            issues.append('cpu_critical')
        elif metrics.cpu_usage > self.thresholds['cpu_high']:
            issues.append('cpu_high')
        
        # Check memory usage
        if metrics.memory_usage > self.thresholds['memory_critical']:
            issues.append('memory_critical')
        elif metrics.memory_usage > self.thresholds['memory_high']:
            issues.append('memory_high')
        
        return issues
    
    def _apply_optimizations(self, issues: List[str]) -> None:
        """Apply optimizations for detected issues"""
        for issue in issues:
            if issue in self.optimization_strategies:
                strategy = self.optimization_strategies[issue]
                strategy()
                
                if issue not in self.active_optimizations:
                    self.active_optimizations.append(issue)
                    self.logger.info(f"Applied optimization for {issue}")
    
    def _optimize_for_low_fps(self) -> None:
        """Optimize for low FPS"""
        if 'reduce_quality' in self.callbacks:
            self.callbacks['reduce_quality'](level='low')
        
        if 'reduce_update_rate' in self.callbacks:
            self.callbacks['reduce_update_rate'](factor=0.8)
    
    def _optimize_for_critical_fps(self) -> None:
        """Optimize for critical FPS"""
        if 'reduce_quality' in self.callbacks:
            self.callbacks['reduce_quality'](level='critical')
        
        if 'reduce_update_rate' in self.callbacks:
            self.callbacks['reduce_update_rate'](factor=0.5)
        
        if 'disable_effects' in self.callbacks:
            self.callbacks['disable_effects']()
    
    def _optimize_for_high_cpu(self) -> None:
        """Optimize for high CPU usage"""
        if 'reduce_physics_updates' in self.callbacks:
            self.callbacks['reduce_physics_updates'](factor=0.7)
        
        if 'optimize_ai' in self.callbacks:
            self.callbacks['optimize_ai'](level='low')
    
    def _optimize_for_critical_cpu(self) -> None:
        """Optimize for critical CPU usage"""
        if 'reduce_physics_updates' in self.callbacks:
            self.callbacks['reduce_physics_updates'](factor=0.3)
        
        if 'optimize_ai' in self.callbacks:
            self.callbacks['optimize_ai'](level='minimal')
        
        if 'disable_background_tasks' in self.callbacks:
            self.callbacks['disable_background_tasks']()
    
    def _optimize_for_high_memory(self) -> None:
        """Optimize for high memory usage"""
        if 'clear_cache' in self.callbacks:
            self.callbacks['clear_cache']()
        
        if 'reduce_texture_quality' in self.callbacks:
            self.callbacks['reduce_texture_quality'](level='medium')
    
    def _optimize_for_critical_memory(self) -> None:
        """Optimize for critical memory usage"""
        if 'clear_cache' in self.callbacks:
            self.callbacks['clear_cache']()
        
        if 'reduce_texture_quality' in self.callbacks:
            self.callbacks['reduce_texture_quality'](level='low')
        
        if 'unload_unused_resources' in self.callbacks:
            self.callbacks['unload_unused_resources']()
    
    def enable_optimization(self, optimization_type: str) -> bool:
        """Enable a specific optimization"""
        if optimization_type in self.optimization_strategies:
            if optimization_type not in self.active_optimizations:
                self.active_optimizations.append(optimization_type)
                self.optimization_strategies[optimization_type]()
                self.logger.info(f"Enabled optimization: {optimization_type}")
                return True
        return False
    
    def disable_optimization(self, optimization_type: str) -> bool:
        """Disable a specific optimization"""
        if optimization_type in self.active_optimizations:
            self.active_optimizations.remove(optimization_type)
            self.logger.info(f"Disabled optimization: {optimization_type}")
            return True
        return False
    
    def reset_optimizations(self) -> None:
        """Reset all optimizations"""
        if 'reset_quality' in self.callbacks:
            self.callbacks['reset_quality']()
        
        if 'reset_update_rate' in self.callbacks:
            self.callbacks['reset_update_rate']()
        
        if 'enable_effects' in self.callbacks:
            self.callbacks['enable_effects']()
        
        self.active_optimizations.clear()
        self.logger.info("Reset all optimizations")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get a comprehensive performance report"""
        if not self.performance_history:
            return {}
        
        # Calculate averages
        avg_fps = sum(data['fps'] for data in self.performance_history) / len(self.performance_history)
        avg_cpu = sum(data['cpu_usage'] for data in self.performance_history) / len(self.performance_history)
        avg_memory = sum(data['memory_usage'] for data in self.performance_history) / len(self.performance_history)
        
        # Find min/max values
        min_fps = min(data['fps'] for data in self.performance_history)
        max_cpu = max(data['cpu_usage'] for data in self.performance_history)
        max_memory = max(data['memory_usage'] for data in self.performance_history)
        
        return {
            'current_metrics': self.performance_monitor.get_current_metrics().__dict__ if self.performance_monitor.get_current_metrics() else {},
            'average_fps': avg_fps,
            'average_cpu_usage': avg_cpu,
            'average_memory_usage': avg_memory,
            'min_fps': min_fps,
            'max_cpu_usage': max_cpu,
            'max_memory_usage': max_memory,
            'active_optimizations': self.active_optimizations,
            'performance_thresholds': self.thresholds,
            'history_size': len(self.performance_history)
        }
    
    def set_auto_optimize(self, enabled: bool) -> None:
        """Enable or disable auto-optimization"""
        self.auto_optimize = enabled
        self.logger.info(f"Auto-optimization {'enabled' if enabled else 'disabled'}")
    
    def set_optimization_cooldown(self, cooldown: float) -> None:
        """Set optimization cooldown time"""
        self.optimization_cooldown = cooldown
        self.logger.info(f"Optimization cooldown set to {cooldown} seconds")
    
    def get_optimization_status(self) -> Dict[str, Any]:
        """Get current optimization status"""
        return {
            'auto_optimize': self.auto_optimize,
            'active_optimizations': self.active_optimizations,
            'optimization_cooldown': self.optimization_cooldown,
            'last_optimization_time': self.last_optimization_time,
            'performance_thresholds': self.thresholds
        }
    
    def cleanup(self) -> None:
        """Cleanup performance optimizer resources"""
        try:
            self.performance_history.clear()
            self.active_optimizations.clear()
            self.callbacks.clear()
            self.logger.info("Performance optimizer cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during performance optimizer cleanup: {e}")
