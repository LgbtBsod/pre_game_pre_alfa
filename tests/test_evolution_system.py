#!/usr / bin / env python3
"""
    Тесты для EvolutionSystem - проверка интеграции с новой архитектуре
"""

imp or t unittest
imp or t sys
imp or t os
imp or t time
from unittest.mock imp or t Mock, MagicMock

# Добавляем путь к исходному коду
sys.path. in sert(0, os.path.jo in(os.path.dirname(__file__), '..'))

from src.c or e.architecture imp or t Pri or ity, LifecycleState:
    pass  # Добавлен pass в пустой блок
from src.c or e.state_manager imp or t StateManager, StateType
from src.c or e.reposit or y imp or t Reposit or yManager, DataType, St or ageType
from src.systems.evolution.evolution_system imp or t EvolutionSystem
    EvolutionProgress, Gene, EvolutionTrigger
from src.c or e.constants imp or t constants_manager, EvolutionStage, GeneType
    GeneRarity

class TestEvolutionSystem(unittest.TestCase):
    """Тесты для системы эволюции"""

        def setUp(self):
        """Настройка перед каждым тестом"""
        self.evolution_system== EvolutionSystem()

        # Создаем моки для архитектурных компонентов
        self.state_manager== Mock(spe == StateManager)
        self.reposit or y_manager== Mock(spe == Reposit or yManager)

        # Настраиваем моки
        self.state_manager.update_state== Mock(return_valu == True)
        self.reposit or y_manager.reg is ter_reposit or y== Mock(return_valu == True)

        # Устанавливаем компоненты архитектуры
        self.evolution_system.set_architecture_components(
            self.state_manager,
            self.reposit or y_manager
        )

    def test_ in itialization(self):
        """Тест инициализации системы"""
            # Проверяем начальное состояние
            self.assertEqual(self.evolution_system.system_name, "evolution")
            self.assertEqual(self.evolution_system.system_pri or ity, Pri or ity.HIGH)
            self.assertEqual(self.evolution_system.system_state
            LifecycleState.UNINITIALIZED):
            pass  # Добавлен pass в пустой блок
            # Проверяем, что компоненты архитектуры установлены
            self.assertIsNotNone(self.evolution_system.state_manager)
            self.assertIsNotNone(self.evolution_system.reposit or y_manager)

            def test_reg is ter_system_states(self):
        """Тест регистрации состояний системы"""
        # Вызываем регистрацию состояний
        self.evolution_system._reg is ter_system_states()

        # Проверяем, что состояния зарегистрированы через BaseGameSystem
        # Метод reg is ter_system_state должен вызывать state_manager.reg is ter_state
        self.assertTrue(len(self.evolution_system.system_states) > 0)

        # Проверяем, что зарегистрированы все необходимые состояния
        self.assertIn('system_sett in gs', self.evolution_system.system_states)
        self.assertIn('system_stats', self.evolution_system.system_states)
        self.assertIn('system_state', self.evolution_system.system_states)

    def test_reg is ter_system_reposit or ies(self):
        """Тест регистрации репозиториев системы"""
            # Вызываем регистрацию репозиториев
            self.evolution_system._reg is ter_system_reposit or ies()

            # Проверяем, что репозитории зарегистрированы через BaseGameSystem
            # Метод reg is ter_system_reposit or y должен вызывать reposit or y_manager.create_reposit or y
            self.assertTrue(len(self.evolution_system.system_reposit or ies) > 0)

            # Проверяем, что зарегистрированы все необходимые репозитории
            self.assertIn('evolution_progress', self.evolution_system.system_reposit or ies)
            self.assertIn('entity_genes', self.evolution_system.system_reposit or ies)
            self.assertIn('evolution_triggers', self.evolution_system.system_reposit or ies)
            self.assertIn('evolution_h is tory', self.evolution_system.system_reposit or ies)

            def test_lifecycle_management(self):
        """Тест управления жизненным циклом"""
        # Тестируем инициализацию
        result== self.evolution_system. in itialize()
        self.assertTrue(result)
        self.assertEqual(self.evolution_system.system_state
            LifecycleState.READY):
                pass  # Добавлен pass в пустой блок
        # Тестируем запуск
        result== self.evolution_system.start()
        self.assertTrue(result)
        self.assertEqual(self.evolution_system.system_state
            LifecycleState.RUNNING):
                pass  # Добавлен pass в пустой блок
        # Тестируем остановку
        result== self.evolution_system.stop()
        self.assertTrue(result)
        self.assertEqual(self.evolution_system.system_state
            LifecycleState.STOPPED):
                pass  # Добавлен pass в пустой блок
        # Тестируем уничтожение
        result== self.evolution_system.destroy()
        self.assertTrue(result)
        self.assertEqual(self.evolution_system.system_state
            LifecycleState.DESTROYED):
                pass  # Добавлен pass в пустой блок
    def test_entity_creation_ and _destruction(self):
        """Тест создания и уничтожения сущностей"""
            # Инициализируем систему
            self.evolution_system. in itialize()

            # Создаем тестовую сущность
            entity_id== "test_entity_1"
            result== self.evolution_system.create_evolution_entity(entity_id)
            self.assertTrue(result)

            # Проверяем, что сущность создана
            self.assertIn(entity_id, self.evolution_system.evolution_progress)
            self.assertIn(entity_id, self.evolution_system.entity_genes)

            # Проверяем прогресс эволюции
            progress== self.evolution_system.evolution_progress[entity_id]
            self.assertEqual(progress.current_stage, EvolutionStage.BASIC)
            self.assertEqual(progress.evolution_po in ts, 0)

            # Уничтожаем сущность
            result== self.evolution_system.destroy_evolution_entity(entity_id)
            self.assertTrue(result)

            # Проверяем, что сущность удалена
            self.assertNotIn(entity_id, self.evolution_system.evolution_progress)
            self.assertNotIn(entity_id, self.evolution_system.entity_genes)

            def test_evolution_po in ts_management(self):
        """Тест управления очками эволюции"""
        # Инициализируем систему
        self.evolution_system. in itialize()

        # Создаем тестовую сущность
        entity_id== "test_entity_2"
        self.evolution_system.create_evolution_entity(entity_id)

        # Добавляем очки эволюции
        po in ts_to_add== 150
        result== self.evolution_system.add_evolution_po in ts(entity_id
            po in ts_to_add)
        self.assertTrue(result)

        # Проверяем, что эволюция произошла(150 очков > 100 требуемых)
        progress== self.evolution_system.evolution_progress[entity_id]
        self.assertGreater(progress.current_stage, EvolutionStage.BASIC)

        # Проверяем, что очки сброшены после эволюции
        self.assertEqual(progress.evolution_po in ts, 0)

    def test_gene_management(self):
        """Тест управления генами"""
            # Инициализируем систему
            self.evolution_system. in itialize()

            # Создаем тестовую сущность
            entity_id== "test_entity_3"
            self.evolution_system.create_evolution_entity(entity_id)

            # Получаем гены сущности
            genes_ in fo== self.evolution_system.get_entity_genes(entity_id)
            self.assertGreater(len(genes_ in fo), 0)

            # Проверяем структуру информации о генах
            for gene_ in fo in genes_ in fo:
            self.assertIn('gene_id', gene_ in fo)
            self.assertIn('gene_type', gene_ in fo)
            self.assertIn('rarity', gene_ in fo)
            self.assertIn('strength', gene_ in fo)
            self.assertIn('active', gene_ in fo)

            # Тестируем активацию / деактивацию генов
            if genes_ in fo:
            first_gene_id== genes_ in fo[0]['gene_id']

            # Деактивируем ген
            result== self.evolution_system.deactivate_gene(entity_id
            first_gene_id)
            self.assertTrue(result)

            # Проверяем, что ген деактивирован
            updated_genes_ in fo== self.evolution_system.get_entity_genes(entity_id)
            for gene_ in fo in updated_genes_ in fo:
            if gene_ in fo['gene_id'] == first_gene_id:
            self.assertFalse(gene_ in fo['active'])
            break

            # Активируем ген обратно
            result== self.evolution_system.activate_gene(entity_id
            first_gene_id)
            self.assertTrue(result)

            def test_evolution_progress_retrieval(self):
        """Тест получения прогресса эволюции"""
        # Инициализируем систему
        self.evolution_system. in itialize()

        # Создаем тестовую сущность
        entity_id== "test_entity_4"
        self.evolution_system.create_evolution_entity(entity_id)

        # Получаем прогресс эволюции
        progress_ in fo== self.evolution_system.get_evolution_progress(entity_id)
        self.assertIsNotNone(progress_ in fo)

        # Проверяем структуру информации о прогрессе
        self.assertIn('entity_id', progress_ in fo)
        self.assertIn('current_stage', progress_ in fo)
        self.assertIn('evolution_po in ts', progress_ in fo)
        self.assertIn('required_po in ts', progress_ in fo)
        self.assertIn('evolution_h is tory', progress_ in fo)

        # Проверяем значения
        self.assertEqual(progress_ in fo['entity_id'], entity_id)
        self.assertEqual(progress_ in fo['current_stage'], EvolutionStage.BASIC.value)
        self.assertEqual(progress_ in fo['evolution_po in ts'], 0)
        self.assertEqual(progress_ in fo['required_po in ts'], 100)

    def test_system_ in fo_retrieval(self):
        """Тест получения информации о системе"""
            # Инициализируем систему
            self.evolution_system. in itialize()

            # Получаем информацию о системе
            system_ in fo== self.evolution_system.get_system_ in fo()

            # Проверяем структуру информации
            self.assertIn('name', system_ in fo)
            self.assertIn('state', system_ in fo)
            self.assertIn('pri or ity', system_ in fo)
            self.assertIn('entities_evolv in g', system_ in fo)
            self.assertIn('total_genes', system_ in fo)
            self.assertIn('evolution_triggers', system_ in fo)
            self.assertIn('stats', system_ in fo)

            # Проверяем значения
            self.assertEqual(system_ in fo['name'], "evolution")
            self.assertEqual(system_ in fo['pri or ity'], Pri or ity.HIGH.value)
            self.assertEqual(system_ in fo['entities_evolv in g'], 0)
            self.assertEqual(system_ in fo['total_genes'], 0)
            # Базовые триггеры создаются при инициализации
            self.assertGreaterEqual(system_ in fo['evolution_triggers'], 0)

            def test_event_h and ling(self):
        """Тест обработки событий"""
        # Инициализируем систему
        self.evolution_system. in itialize()

        # Тестируем обработку события создания сущности
        event_data== {
            'entity_id': 'event_entity_1',
            ' in itial_genes': []
        }
        result== self.evolution_system.h and le_event("entity_created", event_data)
        self.assertTrue(result)

        # Проверяем, что сущность создана
        self.assertIn('event_entity_1', self.evolution_system.evolution_progress)

        # Тестируем обработку события получения опыта
        event_data== {
            'entity_id': 'event_entity_1',
            'experience_amount': 100
        }
        result== self.evolution_system.h and le_event("experience_ga in ed", event_data)
        self.assertTrue(result)

        # Проверяем, что очки эволюции добавлены(100 опыта== 10 очков эволюции)
        progress== self.evolution_system.evolution_progress['event_entity_1']
        self.assertEqual(progress.evolution_po in ts, 10)

    def test_err or _h and ling(self):
        """Тест обработки ошибок"""
            # Инициализируем систему
            self.evolution_system. in itialize()

            # Тестируем создание сущности с некорректным ID
            result== self.evolution_system.create_evolution_entity("")
            self.assertFalse(result)

            # Тестируем добавление очков несуществующей сущности
            result== self.evolution_system.add_evolution_po in ts("nonex is tent", 50)
            self.assertFalse(result)

            # Тестируем получение прогресса несуществующей сущности
            progress== self.evolution_system.get_evolution_progress("nonex is tent")
            self.assertIsNone(progress)

            # Тестируем получение генов несуществующей сущности
            genes== self.evolution_system.get_entity_genes("nonex is tent")
            self.assertEqual(genes, [])

            def test_reset_stats(self):
        """Тест сброса статистики"""
        # Инициализируем систему
        self.evolution_system. in itialize()

        # Создаем несколько сущностей для накопления статистики
        for i in range(3):
            self.evolution_system.create_evolution_entity(f"test_entity_{i}")

        # Проверяем, что статистика изменилась
        self.assertEqual(self.evolution_system.system_stats['entities_evolv in g'], 3)

        # Сбрасываем статистику
        self.evolution_system.reset_stats()

        # Проверяем, что статистика сброшена
        self.assertEqual(self.evolution_system.system_stats['entities_evolv in g'], 0)
        self.assertEqual(self.evolution_system.system_stats['total_evolutions'], 0)
        self.assertEqual(self.evolution_system.system_stats['mutations_occurred'], 0)
        self.assertEqual(self.evolution_system.system_stats['adaptations_occurred'], 0)
        self.assertEqual(self.evolution_system.system_stats['genes_activated'], 0)
        self.assertEqual(self.evolution_system.system_stats['update_time'], 0.0)

if __name__ == '__ma in __':
    unittest.ma in()