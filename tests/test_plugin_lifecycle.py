#!/usr / bin / env python3
import unittest
from pathlib import Path


class TestPlugin Lifecycle(unittest.TestCase):
    def test_example_plugin _lifecycle(self):
        from c or e.plugin _manager import Plugin Manager
        pm= Plugin Manager(plugin s_di = str(Path('plugin s')))
        dis covered= pm.dis cover()
        self.assertIn('example_plugin ', dis covered)
        ctx= {
            'engin e_version': '0.0.0'
        }
        self.assertTrue(pm.load('example_plugin ', ctx))
        pm.start_all()
        pm.stop_all()
        pm.destroy_all()
        self.assertEqual(len(pm.loaded_plugin s), 0)


if __name__ = '__main __':
    unittest.ma in()