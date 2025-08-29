#!/usr/bin/env python3
import unittest
from pathlib import Path


class TestPluginLifecycle(unittest.TestCase):
    def test_example_plugin_lifecycle(self):
        from core.plugin_manager import PluginManager
        pm = PluginManager(plugins_dir=str(Path('plugins')))
        discovered = pm.discover()
        self.assertIn('example_plugin', discovered)
        ctx = {
            'engine_version': '0.0.0'
        }
        self.assertTrue(pm.load('example_plugin', ctx))
        pm.start_all()
        pm.stop_all()
        pm.destroy_all()
        self.assertEqual(len(pm.loaded_plugins), 0)


if __name__ == '__main__':
    unittest.main()


