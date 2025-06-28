import numpy as np
from scipy.spatial import KDTree

class PatternRecognizer:
    def __init__(self):
        self.patterns = []
        self.pattern_vectors = []
        self.responses = []
        self.kdtree = None
    
    def add_pattern(self, pattern, response):
        self.patterns.append(pattern)
        vector = self._pattern_to_vector(pattern)
        self.pattern_vectors.append(vector)
        self.responses.append(response)
        self._rebuild_tree()
    
    def recognize(self, current_situation, threshold=0.7):
        if not self.patterns:
            return None
        
        vector = self._pattern_to_vector(current_situation)
        distances, indices = self.kdtree.query(vector, k=1)
        
        if distances[0] < (1 - threshold) * len(vector):
            return self.responses[indices[0]]
        return None
    
    def _pattern_to_vector(self, pattern):
        """Преобразование шаблона в вектор фиксированной длины"""
        vector = []
        for key in sorted(pattern.keys()):
            value = pattern[key]
            if isinstance(value, bool):
                vector.append(1 if value else 0)
            elif isinstance(value, (int, float)):
                vector.append(value)
            elif isinstance(value, str):
                vector.append(hash(value) % 1000 / 1000.0)
        return np.array(vector)
    
    def _rebuild_tree(self):
        if self.pattern_vectors:
            self.kdtree = KDTree(self.pattern_vectors)