#!/usr/bin/env python3
import unittest
import time


class TestPerfBaseline(unittest.TestCase):
    def test_update_tick_budget(self):
        # Measure update across managers without real Panda3D loop
        from src.core.architecture import ComponentManager, EventBus
        from src.core.state_manager import StateManager
        from src.core.repository import RepositoryManager

        cm = ComponentManager()
        eb = EventBus()
        sm = StateManager()
        rm = RepositoryManager()

        cm.register_component(eb)
        cm.register_component(sm)
        cm.register_component(rm)
        cm.add_dependency('state_manager', 'event_bus')
        cm.add_dependency('repository_manager', 'event_bus')
        self.assertTrue(cm.initialize_all())
        self.assertTrue(cm.start_all())

        start = time.time()
        # Run several updates to simulate load
        for _ in range(50):
            cm.update_all(1.0/60.0)
        elapsed_ms = (time.time() - start) * 1000.0
        # Generous baseline: 50 updates should fit under 500ms on dev machines
        self.assertLess(elapsed_ms, 500.0)


if __name__ == '__main__':
    unittest.main()
