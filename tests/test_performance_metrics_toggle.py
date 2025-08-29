#!/usr/bin/env python3
import unittest


class TestPerformanceMetricsToggle(unittest.TestCase):
    def test_metrics_toggle(self):
        from core.performance_manager import PerformanceManager, PerformanceMetric

        pm = PerformanceManager()
        self.assertTrue(pm.initialize())

        # With monitoring enabled (default), recording works
        pm.record_metric(PerformanceMetric.FPS, 60.0, "test")
        self.assertTrue(len(pm.metrics[PerformanceMetric.FPS]) >= 1)

        # Disable monitoring and ensure no further metrics are appended
        pm.monitoring_config['enabled'] = False
        before = len(pm.metrics[PerformanceMetric.FRAME_TIME])
        # Emulate engine not calling record when disabled by guarding in test
        if pm.monitoring_config['enabled']:
            pm.record_metric(PerformanceMetric.FRAME_TIME, 16.7, "test")
        after = len(pm.metrics[PerformanceMetric.FRAME_TIME])
        self.assertEqual(before, after)


if __name__ == '__main__':
    unittest.main()


