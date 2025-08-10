"""Combat system module."""

try:
    from .damage_system import DamageSystem
except ImportError:
    # If module not found, create a stub
    class DamageSystem:
        """Stub for effect processing"""
        @staticmethod
        def process_entity_effects(entity, dt):
            pass
