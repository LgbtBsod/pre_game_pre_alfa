#!/usr/bin/env python3
import unittest


class TestAIIntegrationMinimal(unittest.TestCase):
    def test_register_and_decide(self):
        from systems.ai.ai_interface import AISystemFactory, AISystemManager

        # Create AI manager and a basic system
        mgr = AISystemManager()
        self.assertTrue(mgr.initialize())
        basic_ai = AISystemFactory.create_ai_system("basic")
        self.assertTrue(mgr.add_system("default", basic_ai))

        # Register a simple entity
        entity = {
            'id': 'unit_1',
            'type': 'npc',
            'x': 0.0,
            'y': 0.0,
            'z': 0.0,
            'speed': 1.0,
            'stats': {},
            'ai_entity': None,
        }
        self.assertTrue(mgr.register_entity(entity['id'], entity, "default", "npcs"))

        # Ask for a decision with minimal context
        ctx = {
            'entities': [entity],
            'delta_time': 0.016,
            'world_state': {'entity_count': 1}
        }
        decision = mgr.get_decision(entity['id'], ctx)
        # We only verify the call path works; the specific action may vary
        # so just assert decision is either None or has expected attributes
        if decision is not None:
            self.assertTrue(hasattr(decision, 'action_type'))


if __name__ == '__main__':
    unittest.main()
