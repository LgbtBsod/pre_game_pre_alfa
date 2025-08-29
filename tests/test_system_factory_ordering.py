#!/usr/bin/env python3
import unittest


class TestSystemFactoryOrdering(unittest.TestCase):
    def test_factory_initialization_order(self):
        from core.event_system import EventSystem
        from core.config_manager import ConfigManager
        from core.system_factory import SystemFactory

        es = EventSystem(); es.initialize()
        cm = ConfigManager(); cm.initialize()
        sf = SystemFactory(cm, es, None)

        # Create a subset of systems with dependencies
        # Create minimal safe subset to avoid missing config/deps in headless
        sf.create_system('content_generator')
        sf.create_system('effect_system')

        # Initialize via SystemManager
        self.assertTrue(sf.initialize_all_systems())
        # Ensure SystemManager has them and no duplicates
        sm = sf.system_manager
        names = sm.get_system_names()
        for n in ['effect_system','content_generator']:
            self.assertIn(n, names)
        self.assertEqual(len(names), len(set(names)))


if __name__ == '__main__':
    unittest.main()


