#!/usr/bin/env python3
import unittest


class DummyScene:
    def __init__(self, name: str):
        self.name = name
        self.scene_manager = None
        self.is_initialized = False
        self.scene_root = None
        self.ui_root = None
        self._visible = False

    def initialize(self) -> bool:
        self.is_initialized = True
        return True

    def update(self, dt: float):
        pass

    def render(self, rn):
        pass

    def handle_event(self, ev):
        pass

    def cleanup(self):
        pass

    def set_visible(self, visible: bool):
        self._visible = visible


class TestSceneManagerEvents(unittest.TestCase):
    def test_scene_change_updates_state_and_emits_event(self):
        # Lazy import to avoid Panda3D requirements
        from src.core.scene_manager import SceneManager
        from src.core.event_system import EventSystem
        from src.core.state_manager import StateManager

        # Create minimal stand-ins for Panda3D nodes
        class RenderNode:
            def attachNewNode(self, name):
                return self
            def setLight(self, *args, **kwargs):
                pass
            def removeNode(self):
                pass

        render = RenderNode()
        resource_manager = object()
        sm = SceneManager(render, resource_manager, None)
        self.assertTrue(sm.initialize())

        # Wire event/state
        es = EventSystem()
        es.initialize()
        st = StateManager()
        st.initialize()
        sm.event_system = es
        sm.state_manager = st

        # Subscribe to scene_changed
        hits = {"n": 0, "last": None}
        def _h(ev):
            hits["n"] += 1
            hits["last"] = ev.data.get("scene")
        es.on("scene_changed", _h)

        # Register scenes and switch
        sm.register_scene("a", DummyScene("a"))
        sm.register_scene("b", DummyScene("b"))
        self.assertTrue(sm.set_active_scene("a"))
        es.process_events()
        self.assertEqual(st.get_state_value("current_scene"), "a")
        self.assertEqual(hits["last"], "a")

        self.assertTrue(sm.switch_to_scene("b", "fade"))
        es.process_events()
        self.assertEqual(st.get_state_value("current_scene"), "b")
        self.assertEqual(hits["last"], "b")


if __name__ == '__main__':
    unittest.main()


