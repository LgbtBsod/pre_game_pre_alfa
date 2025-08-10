import math
import random
from typing import Dict, List, Tuple, Any

class SimpleKDTree:
    """Simple KD-tree implementation for nearest neighbor search"""
    
    def __init__(self, points: List[List[float]]):
        self.points = points
        self.root = self._build_tree(points, 0) if points else None
    
    def _build_tree(self, points: List[List[float]], depth: int):
        if not points:
            return None
        
        k = len(points[0]) if points else 0
        axis = depth % k
        
        # Sort by current axis
        sorted_points = sorted(points, key=lambda x: x[axis])
        median_idx = len(sorted_points) // 2
        
        return {
            'point': sorted_points[median_idx],
            'axis': axis,
            'left': self._build_tree(sorted_points[:median_idx], depth + 1),
            'right': self._build_tree(sorted_points[median_idx + 1:], depth + 1)
        }
    
    def query(self, point: List[float], k: int = 1) -> Tuple[List[float], List[int]]:
        """Search for k nearest neighbors"""
        if not self.root:
            return [], []
        
        distances = []
        indices = []
        
        def search(node, depth=0):
            if not node:
                return
            
            # Calculate distance to current point
            dist = self._distance(point, node['point'])
            distances.append(dist)
            indices.append(self.points.index(node['point']))
            
            # Sort by distance and keep only k nearest
            if len(distances) > k:
                sorted_indices = sorted(range(len(distances)), key=lambda i: distances[i])
                distances[:] = [distances[i] for i in sorted_indices[:k]]
                indices[:] = [indices[i] for i in sorted_indices[:k]]
            
            # Determine which direction to go
            axis = node['axis']
            if point[axis] < node['point'][axis]:
                search(node['left'], depth + 1)
                # Check if we need to search in the right part
                if len(distances) < k or abs(point[axis] - node['point'][axis]) < max(distances):
                    search(node['right'], depth + 1)
            else:
                search(node['right'], depth + 1)
                # Check if we need to search in the left part
                if len(distances) < k or abs(point[axis] - node['point'][axis]) < max(distances):
                    search(node['left'], depth + 1)
        
        search(self.root)
        
        # Return results in correct order
        sorted_indices = sorted(range(len(distances)), key=lambda i: distances[i])
        return [distances[i] for i in sorted_indices], [indices[i] for i in sorted_indices]
    
    def _distance(self, p1: List[float], p2: List[float]) -> float:
        """Euclidean distance between two points"""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))


class PatternRecognizer:
    def __init__(self):
        self.patterns = []
        self.pattern_vectors = []
        self.responses = []
        self.kdtree = None
    
    def add_pattern(self, pattern: Dict[str, Any], response: Any):
        """Add new pattern for recognition"""
        self.patterns.append(pattern)
        vector = self._pattern_to_vector(pattern)
        self.pattern_vectors.append(vector)
        self.responses.append(response)
        self._rebuild_tree()
    
    def recognize(self, current_situation: Dict[str, Any], threshold: float = 0.7) -> Any:
        """Recognize pattern in current situation"""
        if not self.patterns:
            return None
        
        vector = self._pattern_to_vector(current_situation)
        distances, indices = self.kdtree.query(vector, k=1)
        
        if distances and distances[0] < (1 - threshold) * len(vector):
            return self.responses[indices[0]]
        return None
    
    def _pattern_to_vector(self, pattern: Dict[str, Any]) -> List[float]:
        """Convert pattern to fixed-length vector"""
        vector = []
        for key in sorted(pattern.keys()):
            value = pattern[key]
            if isinstance(value, bool):
                vector.append(1.0 if value else 0.0)
            elif isinstance(value, (int, float)):
                vector.append(float(value))
            elif isinstance(value, str):
                vector.append(hash(value) % 1000 / 1000.0)
            else:
                vector.append(0.0)  # For unknown types
        return vector
    
    def _rebuild_tree(self):
        """Rebuild KD-tree"""
        if self.pattern_vectors:
            self.kdtree = SimpleKDTree(self.pattern_vectors)
    
    def clear_patterns(self):
        """Clear all patterns"""
        self.patterns.clear()
        self.pattern_vectors.clear()
        self.responses.clear()
        self.kdtree = None
    
    def get_pattern_count(self) -> int:
        """Get count of saved patterns"""
        return len(self.patterns)
    
    def get_pattern_summary(self) -> Dict[str, Any]:
        """Get pattern summary"""
        return {
            'total_patterns': len(self.patterns),
            'pattern_types': list(set(type(p).__name__ for p in self.patterns)),
            'response_types': list(set(type(r).__name__ for r in self.responses))
        }