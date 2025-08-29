#!/usr/bin/env python3
import unittest
from unittest import mock


class TestAIFactoryFallback(unittest.TestCase):
    def test_pytorch_unavailable_falls_back_to_basic(self):
        # Simulate ImportError when trying to import the PyTorch AI system
        with mock.patch('importlib.util.find_spec') as find_spec:
            def fake_find_spec(name):
                # Block enhanced ai attempts too
                if name and 'systems.ai.enhanced_ai_system' in name:
                    return None
                return None
            find_spec.side_effect = fake_find_spec

            from systems.ai.ai_interface import AISystemFactory
            ai = AISystemFactory.create_ai_system('auto')
            # When neither pytorch nor enhanced are available, basic AI is used
            from systems.ai.ai_system import AISystem
            self.assertIsInstance(ai, AISystem)


if __name__ == '__main__':
    unittest.main()


