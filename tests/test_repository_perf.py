#!/usr/bin/env python3
import unittest
import time


class TestRepositoryPerf(unittest.TestCase):
    def test_query_filter_sort_paginate_baseline(self):
        from core.repository import BaseRepository, DataType, StorageType, create_query_filter, create_query_sort, create_query_options

        repo = BaseRepository('perf_repo', DataType.DYNAMIC_DATA, StorageType.MEMORY)
        self.assertTrue(repo.initialize())
        # Seed data
        for i in range(1000):
            repo.create(f'id_{i}', {'value': i, 'group': 'a' if i % 2 == 0 else 'b'})

        # Add index and query with filters/sort/paginate
        repo.add_index('group')

        opts = create_query_options(
            limit=100,
            offset=50,
            filters=[create_query_filter('group', 'eq', 'a')],
            sort=[create_query_sort('value', 'desc')]
        )
        t0 = time.time()
        results = repo.query(opts)
        elapsed_ms = (time.time() - t0) * 1000.0

        self.assertLess(elapsed_ms, 100.0)  # baseline threshold
        self.assertEqual(len(results), 100)


if __name__ == '__main__':
    unittest.main()


