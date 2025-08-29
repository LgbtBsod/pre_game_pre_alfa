#!/usr/bin/env python3
"""
Тесты для CombatSystem - проверка интеграции с новой архитектурой
"""

import unittest
import sys
import os
import time
from unittest.mock import Mock, MagicMock

# Добавляем путь к исходному коду
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.architecture import Priority, LifecycleState
from src.core.state_manager import StateManager, StateType
from src.core.repository import RepositoryManager, DataType, StorageType
from src.systems.combat.combat_system import CombatSystem, CombatStats, AttackResult, CombatAction
from src.core.constants import constants_manager, DamageType, AttackType

class TestCombatSystem(unittest.TestCase):
    """Тесты для системы боя"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.combat_system = CombatSystem()
        
        # Создаем моки для архитектурных компонентов
        self.state_manager = Mock(spec=StateManager)
        self.repository_manager = Mock(spec=RepositoryManager)
        
        # Настраиваем моки
        self.state_manager.update_state = Mock(return_value=True)
        self.repository_manager.register_repository = Mock(return_value=True)
        
        # Устанавливаем компоненты архитектуры
        self.combat_system.set_architecture_components(
            self.state_manager, 
            self.repository_manager
        )
    
    def test_initialization(self):
        """Тест инициализации системы"""
        # Проверяем начальное состояние
        self.assertEqual(self.combat_system.system_name, "combat")
        self.assertEqual(self.combat_system.system_priority, Priority.HIGH)
        self.assertEqual(self.combat_system.system_state, LifecycleState.UNINITIALIZED)
        
        # Проверяем, что компоненты архитектуры установлены
        self.assertIsNotNone(self.combat_system.state_manager)
        self.assertIsNotNone(self.combat_system.repository_manager)
    
    def test_register_system_states(self):
        """Тест регистрации состояний системы"""
        # Вызываем регистрацию состояний
        self.combat_system._register_system_states()
        
        # Проверяем, что состояния зарегистрированы
        self.state_manager.update_state.assert_called()
        
        # Проверяем количество вызовов (должно быть 3: настройки, статистика, состояние)
        self.assertEqual(self.state_manager.update_state.call_count, 3)
    
    def test_register_system_repositories(self):
        """Тест регистрации репозиториев системы"""
        # Вызываем регистрацию репозиториев
        self.combat_system._register_system_repositories()
        
        # Проверяем, что репозитории зарегистрированы
        self.repository_manager.register_repository.assert_called()
        
        # Проверяем количество вызовов (должно быть 4 репозитория)
        self.assertEqual(self.repository_manager.register_repository.call_count, 4)
    
    def test_lifecycle_management(self):
        """Тест управления жизненным циклом"""
        # Тестируем инициализацию
        result = self.combat_system.initialize()
        self.assertTrue(result)
        self.assertEqual(self.combat_system.system_state, LifecycleState.READY)
        
        # Тестируем запуск
        result = self.combat_system.start()
        self.assertTrue(result)
        self.assertEqual(self.combat_system.system_state, LifecycleState.RUNNING)
        
        # Тестируем остановку
        result = self.combat_system.stop()
        self.assertTrue(result)
        self.assertEqual(self.combat_system.system_state, LifecycleState.STOPPED)
        
        # Тестируем уничтожение
        result = self.combat_system.destroy()
        self.assertTrue(result)
        self.assertEqual(self.combat_system.system_state, LifecycleState.DESTROYED)
    
    def test_combat_creation(self):
        """Тест создания боя"""
        # Инициализируем систему
        self.combat_system.initialize()
        
        # Создаем тестовый бой
        combat_id = "test_combat_1"
        participants = ["player_1", "enemy_1"]
        
        result = self.combat_system.create_combat(combat_id, participants)
        self.assertTrue(result)
        
        # Проверяем, что бой создан
        self.assertIn(combat_id, self.combat_system.active_combats)
        
        # Проверяем структуру боя
        combat = self.combat_system.active_combats[combat_id]
        self.assertIn('combat_id', combat)
        self.assertIn('participants', combat)
        self.assertEqual(combat['combat_id'], combat_id)
        self.assertEqual(len(combat['participants']), 2)
    
    def test_combat_stats_creation(self):
        """Тест создания боевой статистики"""
        # Инициализируем систему
        self.combat_system.initialize()
        
        # Создаем тестовую боевую статистику
        stats = CombatStats(
            health=100,
            max_health=100,
            mana=50,
            max_mana=50,
            attack=15,
            defense=10,
            speed=12.0,
            critical_chance=0.1,
            critical_multiplier=2.0,
            dodge_chance=0.05,
            block_chance=0.1,
            block_reduction=0.5
        )
        
        # Проверяем, что статистика создана корректно
        self.assertEqual(stats.health, 100)
        self.assertEqual(stats.max_health, 100)
        self.assertEqual(stats.mana, 50)
        self.assertEqual(stats.max_mana, 50)
        self.assertEqual(stats.attack, 15)
        self.assertEqual(stats.defense, 10)
        self.assertEqual(stats.speed, 12.0)
        self.assertEqual(stats.critical_chance, 0.1)
        self.assertEqual(stats.critical_multiplier, 2.0)
        self.assertEqual(stats.dodge_chance, 0.05)
        self.assertEqual(stats.block_chance, 0.1)
        self.assertEqual(stats.block_reduction, 0.5)
    
    def test_combat_action_creation(self):
        """Тест создания боевого действия"""
        # Инициализируем систему
        self.combat_system.initialize()
        
        # Создаем тестовое действие
        action = CombatAction(
            action_id="test_action_1",
            action_type="attack",
            source_entity="player_1",
            target_entity="enemy_1",
            timestamp=time.time(),
            data={
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
    
    def test_system_info_retrieval(self):
        """Тест получения информации о системе"""
        # Инициализируем систему
        self.combat_system.initialize()
        
        # Получаем информацию о системе
        system_info = self.combat_system.get_system_info()
        
        # Проверяем структуру информации
        self.assertIn('name', system_info)
        self.assertIn('state', system_info)
        self.assertIn('priority', system_info)
        self.assertIn('active_combats', system_info)
        self.assertIn('total_combats', system_info)
        self.assertIn('actions_performed', system_info)
        self.assertIn('damage_dealt', system_info)
        self.assertIn('update_time', system_info)
        
        # Проверяем значения
        self.assertEqual(system_info['name'], "combat")
        self.assertEqual(system_info['priority'], Priority.HIGH.value)
        self.assertEqual(system_info['active_combats_count'], 0)
        self.assertEqual(system_info['combats_started'], 0)
        self.assertEqual(system_info['combats_completed'], 0)
        self.assertEqual(system_info['total_damage_dealt'], 0)
        self.assertEqual(system_info['update_time'], 0.0)
    
    def test_error_handling(self):
        """Тест обработки ошибок"""
        # Инициализируем систему
        self.combat_system.initialize()
        
        # Тестируем создание боя с некорректными данными
        result = self.combat_system.create_combat("", [])
        self.assertFalse(result)
        
        # Тестируем создание боя без участников
        result = self.combat_system.create_combat("test_combat_2", [])
        self.assertFalse(result)
    
    def test_reset_stats(self):
        """Тест сброса статистики"""
        # Инициализируем систему
        self.combat_system.initialize()
        
        # Изменяем статистику
        self.combat_system.system_stats['active_combats_count'] = 3
        self.combat_system.system_stats['combats_started'] = 10
        
        # Сбрасываем статистику
        self.combat_system.reset_stats()
        
        # Проверяем, что статистика сброшена
        self.assertEqual(self.combat_system.system_stats['active_combats_count'], 0)
        self.assertEqual(self.combat_system.system_stats['combats_started'], 0)
        self.assertEqual(self.combat_system.system_stats['combats_completed'], 0)
        self.assertEqual(self.combat_system.system_stats['total_damage_dealt'], 0)
        self.assertEqual(self.combat_system.system_stats['update_time'], 0.0)
    
    def test_system_settings(self):
        """Тест настроек системы"""
        # Инициализируем систему
        self.combat_system.initialize()
        
        # Проверяем, что настройки установлены
        self.assertIn('max_active_combats', self.combat_system.combat_settings)
        self.assertIn('combat_timeout', self.combat_system.combat_settings)
        self.assertIn('auto_resolve_delay', self.combat_system.combat_settings)
        self.assertIn('experience_multiplier', self.combat_system.combat_settings)
        self.assertIn('gold_multiplier', self.combat_system.combat_settings)
        
        # Проверяем типы значений
        self.assertIsInstance(self.combat_system.combat_settings['max_active_combats'], int)
        self.assertIsInstance(self.combat_system.combat_settings['combat_timeout'], float)
        self.assertIsInstance(self.combat_system.combat_settings['auto_resolve_delay'], float)
        self.assertIsInstance(self.combat_system.combat_settings['experience_multiplier'], float)
        self.assertIsInstance(self.combat_system.combat_settings['gold_multiplier'], float)
    
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

if __name__ == '__main__':
    unittest.main()
