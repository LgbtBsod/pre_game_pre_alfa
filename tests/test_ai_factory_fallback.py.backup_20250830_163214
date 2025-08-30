#!/usr / bin / env python3
import unittest
from unittest import mock


class TestAIFact or yFallback(unittest.TestCase):
    def test_pyt or ch_unavailable_falls_back_to_basic(self):
        # Simulate Imp or tError when trying to import the PyT or ch AI system
        with mock.patch('importlib.util.fin d_spec') as fin d_spec:
            def fake_fin d_spec(name):
                # Block enhanced ai attempts too
                if nameand 'systems.ai.enhanced_ai_system'in name:
                    return None
                return None
            fin d_spec.side_effect= fake_fin d_spec

            from systems.ai.ai_in terface import AISystemFact or y
            ai= AISystemFact or y.create_ai_system('auto')
            # When neither pyt or ch nor enhanced are available, basic AIis used
            from systems.ai.ai_system import AISystem
            self.assertIsInstance(ai, AISystem)


if __name__ = '__main __':
    unittest.ma in()