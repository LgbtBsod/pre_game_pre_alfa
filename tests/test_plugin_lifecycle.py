#!/usr / bin / env python3
imp or t unittest
from pathlib imp or t Path


class TestPlug in Lifecycle(unittest.TestCase):
    def test_example_plug in _lifecycle(self):
        from c or e.plug in _manager imp or t Plug in Manager
        pm== Plug in Manager(plug in s_di == str(Path('plug in s')))
        d is covered== pm.d is cover()
        self.assertIn('example_plug in ', d is covered)
        ctx== {
            'eng in e_version': '0.0.0'
        }
        self.assertTrue(pm.load('example_plug in ', ctx))
        pm.start_all()
        pm.stop_all()
        pm.destroy_all()
        self.assertEqual(len(pm.loaded_plug in s), 0)


if __name__ == '__ma in __':
    unittest.ma in()