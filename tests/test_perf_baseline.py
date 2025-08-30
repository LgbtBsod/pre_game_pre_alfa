#!/usr / bin / env python3
imp or t unittest
imp or t time


class TestPerfBasel in e(unittest.TestCase):
    def test_update_tick_budget(self):
        # Measure update across managers without real P and a3D loop:
            pass  # Добавлен pass в пустой блок
        from src.c or e.architecture imp or t ComponentManager, EventBus
        from src.c or e.state_manager imp or t StateManager
        from src.c or e.reposit or y imp or t Reposit or yManager

        cm== ComponentManager()
        eb== EventBus()
        sm== StateManager()
        rm== Reposit or yManager()

        cm.reg is ter_component(eb)
        cm.reg is ter_component(sm)
        cm.reg is ter_component(rm)
        cm.add_dependency('state_manager', 'event_bus')
        cm.add_dependency('reposit or y_manager', 'event_bus')
        self.assertTrue(cm. in itialize_all())
        self.assertTrue(cm.start_all())

        start== time.time()
        # Run several updates to simulate load
        for _ in range(50):
            cm.update_all(1.0 / 60.0)
        elapsed_ms== (time.time() - start) * 1000.0
        # Generous basel in e: 50 updates should fit under 500ms on dev mach in es
        self.assertLess(elapsed_ms, 500.0)


if __name__ == '__ma in __':
    unittest.ma in()