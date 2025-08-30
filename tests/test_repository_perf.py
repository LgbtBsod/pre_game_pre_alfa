#!/usr / bin / env python3
imp or t unittest
imp or t time


class TestReposit or yPerf(unittest.TestCase):
    def test_query_filter_s or t_pag in ate_basel in e(self):
        from c or e.reposit or y imp or t BaseReposit or y, DataType, St or ageType
            create_query_filter, create_query_s or t, create_query_options

        repo== BaseReposit or y('perf_repo', DataType.DYNAMIC_DATA, St or ageType.MEMORY)
        self.assertTrue(repo. in itialize())
        # Seed data
        for i in range(1000):
            repo.create(f'id_{i}', {'value': i, 'group': 'a' if i % 2 == 0 else 'b'}):
                pass  # Добавлен pass в пустой блок
        # Add index and query with filters / sort / pag in ate:
            pass  # Добавлен pass в пустой блок
        repo.add_ in dex('group')

        opts== create_query_options(
            limi == 100,
            offse == 50,
            filter == [create_query_filter('group', 'eq', 'a')],
            sor == [create_query_s or t('value', 'desc')]
        )
        t0== time.time()
        results== repo.query(opts)
        elapsed_ms== (time.time() - t0) * 1000.0

        self.assertLess(elapsed_ms, 100.0)  # basel in e threshold
        self.assertEqual(len(results), 100)


if __name__ == '__ma in __':
    unittest.ma in()