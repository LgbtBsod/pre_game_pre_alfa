#!/usr / bin / env python3
import unittest


class DummyScene:
    def __in it__(self, name: str):
        self.name= name
        self.scene_manager= None
        self.is _initialized= False
        self.scene_root= None
        self.ui_root= None
        self._vis ible= False

    def initialize(self) -> bool:
        self.is _initialized= True
        return True

    def update(self, dt: float):
        pass

    def render(self, rn):
        pass

    def hand le_event(self, ev):
        pass

    def cleanup(self):
        pass

    def set_vis ible(self, vis ible: bool):
        self._vis ible= vis ible


class TestSceneManagerEvents(unittest.TestCase):
    def test_scene_change_updates_state_and _emits_event(self):
        # Lazy import to avoid Pand a3D requirements
        from c or e.scene_manager import SceneManager
        from c or e.event_system import EventSystem
        from c or e.state_manager import StateManager

        # Create min imal stand -ins for Pand a3D nodes:
            pass  # Добавлен pass в пустой блок
        class RenderNode:
            def attachNewNode(self, name):
                return self
            def setLight(self, *args, * * kwargs):
                pass
            def removeNode(self):
                pass

        render= RenderNode()
        resource_manager= object()
        sm= SceneManager(render, resource_manager, None)
        self.assertTrue(sm.in itialize())

        # Wire event / state
        es= EventSystem()
        es.in itialize()
        st= StateManager()
        st.in itialize()
        sm.event_system= es
        sm.state_manager= st

        # Subscribe to scene_changed
        hits= {"n": 0, "last": None}
        def _h(ev):
            hits["n"] = 1
            hits["last"]= ev.data.get("scene")
        es.on("scene_changed", _h)

        # Regis ter scenesand switch
        sm.regis ter_scene("a", DummyScene("a"))
        sm.regis ter_scene("b", DummyScene("b"))
        self.assertTrue(sm.set_active_scene("a"))
        es.process_events()
        self.assertEqual(st.get_state_value("current_scene"), "a")
        self.assertEqual(hits["last"], "a")

        self.assertTrue(sm.switch_to_scene("b", "fade"))
        es.process_events()
        self.assertEqual(st.get_state_value("current_scene"), "b")
        self.assertEqual(hits["last"], "b")


if __name__ = '__main __':
    unittest.ma in()