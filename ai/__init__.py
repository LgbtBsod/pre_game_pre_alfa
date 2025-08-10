"""Artificial Intelligence module."""

try:
    from .advanced_ai import AdvancedAIController
    from .behavior_tree import BehaviorTree
    from .cooperation import AICoordinator
    from .decision_maker import PlayerDecisionMaker
    from .emotion_genetics import EmotionGeneticSynthesizer
    from .learning import PlayerLearning
    from .memory import AIMemory, LearningController
    from .pattern_recognizer import PatternRecognizer
    
    __all__ = [
        'AdvancedAIController',
        'BehaviorTree', 
        'AICoordinator',
        'PlayerDecisionMaker',
        'EmotionGeneticSynthesizer',
        'PlayerLearning',
        'AIMemory',
        'LearningController',
        'PatternRecognizer'
    ]
except ImportError:
    # If modules not found, create stubs
    class AdvancedAIController:
        def __init__(self):
            pass
    
    class BehaviorTree:
        def __init__(self):
            pass
    
    class AICoordinator:
        def __init__(self):
            pass
        def register_entity(self, entity, group):
            pass
        def update_group_behavior(self, group):
            pass
    
    class PlayerDecisionMaker:
        def __init__(self, player, memory):
            pass
        def update(self, dt):
            pass
    
    class EmotionGeneticSynthesizer:
        def __init__(self, player, *args):
            pass
        def update_emotions(self, dt):
            pass
    
    class PlayerLearning:
        def __init__(self, player, memory):
            pass
        def update(self, dt):
            pass
    
    class AIMemory:
        def __init__(self):
            pass
        def record_event(self, event_type, data):
            pass
    
    class LearningController:
        def __init__(self):
            pass
    
    class PatternRecognizer:
        def __init__(self):
            pass
        def analyze_combat_patterns(self, entities):
            pass
    
    __all__ = [
        'AdvancedAIController',
        'BehaviorTree', 
        'AICoordinator',
        'PlayerDecisionMaker',
        'EmotionGeneticSynthesizer',
        'PlayerLearning',
        'AIMemory',
        'LearningController',
        'PatternRecognizer'
    ]
