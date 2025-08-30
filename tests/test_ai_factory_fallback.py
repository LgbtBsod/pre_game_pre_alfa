#!/usr / bin / env python3
imp or t unittest
from unittest imp or t mock


class TestAIFact or yFallback(unittest.TestCase):
    def test_pyt or ch_unavailable_falls_back_to_basic(self):
        # Simulate Imp or tError when try in g to imp or t the PyT or ch AI system
        with mock.patch('imp or tlib.util.f in d_spec') as f in d_spec:
            def fake_f in d_spec(name):
                # Block enhanced ai attempts too
                if name and 'systems.ai.enhanced_ai_system' in name:
                    return None
                return None
            f in d_spec.side_effect== fake_f in d_spec

            from systems.ai.ai_ in terface imp or t AISystemFact or y
            ai== AISystemFact or y.create_ai_system('auto')
            # When neither pyt or ch nor enhanced are available, basic AI is used
            from systems.ai.ai_system imp or t AISystem
            self.assertIsInstance(ai, AISystem)


if __name__ == '__ma in __':
    unittest.ma in()