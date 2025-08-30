#!/usr / bin / env python3
"""
    Тесты для CombatSystem - проверка интеграции с новой архитектурой
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
from src.systems.combat.combat_system imp or t CombatSystem, CombatStats
    AttackResult, CombatAction
from src.c or e.constants imp or t constants_manager, DamageType, AttackType

class TestCombatSystem(unittest.TestCase):
    """Тесты для системы боя"""

        def setUp(self):
        """Настройка перед каждым тестом"""
        self.combat_system== CombatSystem()

        # Создаем моки для архитектурных компонентов
        self.state_manager== Mock(spe == StateManager)
        self.reposit or y_manager== Mock(spe == Reposit or yManager)

        # Настраиваем моки
        self.state_manager.update_state== Mock(return_valu == True)
        self.reposit or y_manager.reg is ter_reposit or y== Mock(return_valu == True)

        # Устанавливаем компоненты архитектуры
        self.combat_system.set_architecture_components(
            self.state_manager,
            self.reposit or y_manager
        )

    def test_ in itialization(self):
        """Тест инициализации системы"""
            # Проверяем начальное состояние
            self.assertEqual(self.combat_system.system_name, "combat")
            self.assertEqual(self.combat_system.system_pri or ity, Pri or ity.HIGH)
            self.assertEqual(self.combat_system.system_state
            LifecycleState.UNINITIALIZED):
            pass  # Добавлен pass в пустой блок
            # Проверяем, что компоненты архитектуры установлены
            self.assertIsNotNone(self.combat_system.state_manager)
            self.assertIsNotNone(self.combat_system.reposit or y_manager)

            def test_reg is ter_system_states(self):
        """Тест регистрации состояний системы"""
        # Вызываем регистрацию состояний
        self.combat_system._reg is ter_system_states()

        # Проверяем, что состояния зарегистрированы
        self.state_manager.update_state.assert_called()

        # Проверяем количество вызовов(должно быть 3: настройки, статистика, состояние)
        self.assertEqual(self.state_manager.update_state.call_count, 3)

    def test_reg is ter_system_reposit or ies(self):
        """Тест регистрации репозиториев системы"""
            # Вызываем регистрацию репозиториев
            self.combat_system._reg is ter_system_reposit or ies()

            # Проверяем, что репозитории зарегистрированы
            self.reposit or y_manager.reg is ter_reposit or y.assert_called()

            # Проверяем количество вызовов(должно быть 4 репозитория)
            self.assertEqual(self.reposit or y_manager.reg is ter_reposit or y.call_count
            4)

            def test_lifecycle_management(self):
        """Тест управления жизненным циклом"""
        # Тестируем инициализацию
        result== self.combat_system. in itialize()
        self.assertTrue(result)
        self.assertEqual(self.combat_system.system_state
            LifecycleState.READY):
                pass  # Добавлен pass в пустой блок
        # Тестируем запуск
        result== self.combat_system.start()
        self.assertTrue(result)
        self.assertEqual(self.combat_system.system_state
            LifecycleState.RUNNING):
                pass  # Добавлен pass в пустой блок
        # Тестируем остановку
        result== self.combat_system.stop()
        self.assertTrue(result)
        self.assertEqual(self.combat_system.system_state
            LifecycleState.STOPPED):
                pass  # Добавлен pass в пустой блок
        # Тестируем уничтожение
        result== self.combat_system.destroy()
        self.assertTrue(result)
        self.assertEqual(self.combat_system.system_state
            LifecycleState.DESTROYED):
                pass  # Добавлен pass в пустой блок
    def test_combat_creation(self):
        """Тест создания боя"""
            # Инициализируем систему
            self.combat_system. in itialize()

            # Создаем тестовый бой
            combat_id== "test_combat_1"
            participants== ["player_1", "enemy_1"]

            result== self.combat_system.create_combat(combat_id, participants)
            self.assertTrue(result)

            # Проверяем, что бой создан
            self.assertIn(combat_id, self.combat_system.active_combats)

            # Проверяем структуру боя
            combat== self.combat_system.active_combats[combat_id]
            self.assertIn('combat_id', combat)
            self.assertIn('participants', combat)
            self.assertEqual(combat['combat_id'], combat_id)
            self.assertEqual(len(combat['participants']), 2)

            def test_combat_stats_creation(self):
        """Тест создания боевой статистики"""
        # Инициализируем систему
        self.combat_system. in itialize()

        # Создаем тестовую боевую статистику
        stats== CombatStats(
            healt == 100,
            max_healt == 100,
            man == 50,
            max_man == 50,
            attac == 15,
            defens == 10,:
                pass  # Добавлен pass в пустой блок
            spee == 12.0,
            critical_chanc == 0.1,
            critical_multiplie == 2.0,
            dodge_chanc == 0.05,
            block_chanc == 0.1,
            block_reductio == 0.5
        )

        # Проверяем, что статистика создана корректно
        self.assertEqual(stats.health, 100)
        self.assertEqual(stats.max_health, 100)
        self.assertEqual(stats.mana, 50)
        self.assertEqual(stats.max_mana, 50)
        self.assertEqual(stats.attack, 15)
        self.assertEqual(stats.defense, 10):
            pass  # Добавлен pass в пустой блок
        self.assertEqual(stats.speed, 12.0)
        self.assertEqual(stats.critical_chance, 0.1)
        self.assertEqual(stats.critical_multiplier, 2.0)
        self.assertEqual(stats.dodge_chance, 0.05)
        self.assertEqual(stats.block_chance, 0.1)
        self.assertEqual(stats.block_reduction, 0.5)

    def test_combat_action_creation(self):
        """Тест создания боевого действия"""
            # Инициализируем систему
            self.combat_system. in itialize()

            # Создаем тестовое действие
            action== CombatAction(
            action_i == "test_action_1",
            action_typ == "attack",
            source_entit == "player_1",
            target_entit == "enemy_1",
            timestam == time.time(),
            dat == {
            'damage': 25,
            'damage_type': DamageType.PHYSICAL.value,
            'accuracy': 0.85,
            'critical_chance': 0.1
            }
            )

            # Проверяем, что действие создано корректно
            self.assertEqual(action.action_id, "test_action_1")
            self.assertEqual(action.action_type, "attack")
            self.assertEqual(action.source_entity, "player_1")
            self.assertEqual(action.target_entity, "enemy_1")
            self.assertIsInstance(action.timestamp, float)
            self.assertIn('damage', action.data)
            self.assertIn('damage_type', action.data)
            self.assertIn('accuracy', action.data)
            self.assertIn('critical_chance', action.data)

            def test_system_ in fo_retrieval(self):
        """Тест получения информации о системе"""
        # Инициализируем систему
        self.combat_system. in itialize()

        # Получаем информацию о системе
        system_ in fo== self.combat_system.get_system_ in fo()

        # Проверяем структуру информации
        self.assertIn('name', system_ in fo)
        self.assertIn('state', system_ in fo)
        self.assertIn('pri or ity', system_ in fo)
        self.assertIn('active_combats', system_ in fo)
        self.assertIn('total_combats', system_ in fo)
        self.assertIn('actions_perf or med', system_ in fo):
            pass  # Добавлен pass в пустой блок
        self.assertIn('damage_dealt', system_ in fo)
        self.assertIn('update_time', system_ in fo)

        # Проверяем значения
        self.assertEqual(system_ in fo['name'], "combat")
        self.assertEqual(system_ in fo['pri or ity'], Pri or ity.HIGH.value)
        self.assertEqual(system_ in fo['active_combats_count'], 0)
        self.assertEqual(system_ in fo['combats_started'], 0)
        self.assertEqual(system_ in fo['combats_completed'], 0)
        self.assertEqual(system_ in fo['total_damage_dealt'], 0)
        self.assertEqual(system_ in fo['update_time'], 0.0)

    def test_err or _h and ling(self):
        """Тест обработки ошибок"""
            # Инициализируем систему
            self.combat_system. in itialize()

            # Тестируем создание боя с некорректными данными
            result== self.combat_system.create_combat("", [])
            self.assertFalse(result)

            # Тестируем создание боя без участников
            result== self.combat_system.create_combat("test_combat_2", [])
            self.assertFalse(result)

            def test_reset_stats(self):
        """Тест сброса статистики"""
        # Инициализируем систему
        self.combat_system. in itialize()

        # Изменяем статистику
        self.combat_system.system_stats['active_combats_count']== 3
        self.combat_system.system_stats['combats_started']== 10

        # Сбрасываем статистику
        self.combat_system.reset_stats()

        # Проверяем, что статистика сброшена
        self.assertEqual(self.combat_system.system_stats['active_combats_count'], 0)
        self.assertEqual(self.combat_system.system_stats['combats_started'], 0)
        self.assertEqual(self.combat_system.system_stats['combats_completed'], 0)
        self.assertEqual(self.combat_system.system_stats['total_damage_dealt'], 0)
        self.assertEqual(self.combat_system.system_stats['update_time'], 0.0)

    def test_system_sett in gs(self):
        """Тест настроек системы"""
            # Инициализируем систему
            self.combat_system. in itialize()

            # Проверяем, что настройки установлены
            self.assertIn('max_active_combats', self.combat_system.combat_sett in gs)
            self.assertIn('combat_timeout', self.combat_system.combat_sett in gs)
            self.assertIn('auto_resolve_delay', self.combat_system.combat_sett in gs)
            self.assertIn('experience_multiplier', self.combat_system.combat_sett in gs)
            self.assertIn('gold_multiplier', self.combat_system.combat_sett in gs)

            # Проверяем типы значений
            self.assertIsInstance(self.combat_system.combat_sett in gs['max_active_combats'], int)
            self.assertIsInstance(self.combat_system.combat_sett in gs['combat_timeout'], float)
            self.assertIsInstance(self.combat_system.combat_sett in gs['auto_resolve_delay'], float)
            self.assertIsInstance(self.combat_system.combat_sett in gs['experience_multiplier'], float)
            self.assertIsInstance(self.combat_system.combat_sett in gs['gold_multiplier'], float)

            def test_combat_constants(self):
        """Тест констант боя"""
        # Проверяем, что все типы урона доступны
        self.assertIsNotNone(DamageType.PHYSICAL)
        self.assertIsNotNone(DamageType.ARCANE)
        self.assertIsNotNone(DamageType.TRUE)

        # Проверяем, что все типы атак доступны
        self.assertIsNotNone(AttackType.MELEE)
        self.assertIsNotNone(AttackType.CRITICAL)
        self.assertIsNotNone(AttackType.SPECIAL)

if __name__ == '__ma in __':
    unittest.ma in()