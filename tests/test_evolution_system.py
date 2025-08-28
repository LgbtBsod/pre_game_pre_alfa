#!/usr/bin/env python3
"""
Тесты для EvolutionSystem - проверка интеграции с новой архитектурой
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
from src.systems.evolution.evolution_system import EvolutionSystem, EvolutionProgress, Gene, EvolutionTrigger
from src.core.constants import EvolutionStage, GeneType, GeneRarity

class TestEvolutionSystem(unittest.TestCase):
    """Тесты для системы эволюции"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.evolution_system = EvolutionSystem()
        
        # Создаем моки для архитектурных компонентов
        self.state_manager = Mock(spec=StateManager)
        self.repository_manager = Mock(spec=RepositoryManager)
        
        # Настраиваем моки
        self.state_manager.update_state = Mock(return_value=True)
        self.repository_manager.register_repository = Mock(return_value=True)
        
        # Устанавливаем компоненты архитектуры
        self.evolution_system.set_architecture_components(
            self.state_manager, 
            self.repository_manager
        )
    
    def test_initialization(self):
        """Тест инициализации системы"""
        # Проверяем начальное состояние
        self.assertEqual(self.evolution_system.system_name, "evolution")
        self.assertEqual(self.evolution_system.system_priority, Priority.HIGH)
        self.assertEqual(self.evolution_system.system_state, LifecycleState.UNINITIALIZED)
        
        # Проверяем, что компоненты архитектуры установлены
        self.assertIsNotNone(self.evolution_system.state_manager)
        self.assertIsNotNone(self.evolution_system.repository_manager)
    
    def test_register_system_states(self):
        """Тест регистрации состояний системы"""
        # Вызываем регистрацию состояний
        self.evolution_system._register_system_states()
        
        # Проверяем, что состояния зарегистрированы
        self.state_manager.update_state.assert_called()
        
        # Проверяем количество вызовов (должно быть 3: настройки, статистика, состояние)
        self.assertEqual(self.state_manager.update_state.call_count, 3)
    
    def test_register_system_repositories(self):
        """Тест регистрации репозиториев системы"""
        # Вызываем регистрацию репозиториев
        self.evolution_system._register_system_repositories()
        
        # Проверяем, что репозитории зарегистрированы
        self.repository_manager.register_repository.assert_called()
        
        # Проверяем количество вызовов (должно быть 4 репозитория)
        self.assertEqual(self.repository_manager.register_repository.call_count, 4)
    
    def test_lifecycle_management(self):
        """Тест управления жизненным циклом"""
        # Тестируем инициализацию
        result = self.evolution_system.initialize()
        self.assertTrue(result)
        self.assertEqual(self.evolution_system.system_state, LifecycleState.READY)
        
        # Тестируем запуск
        result = self.evolution_system.start()
        self.assertTrue(result)
        self.assertEqual(self.evolution_system.system_state, LifecycleState.RUNNING)
        
        # Тестируем остановку
        result = self.evolution_system.stop()
        self.assertTrue(result)
        self.assertEqual(self.evolution_system.system_state, LifecycleState.STOPPED)
        
        # Тестируем уничтожение
        result = self.evolution_system.destroy()
        self.assertTrue(result)
        self.assertEqual(self.evolution_system.system_state, LifecycleState.DESTROYED)
    
    def test_entity_creation_and_destruction(self):
        """Тест создания и уничтожения сущностей"""
        # Инициализируем систему
        self.evolution_system.initialize()
        
        # Создаем тестовую сущность
        entity_id = "test_entity_1"
        result = self.evolution_system.create_evolution_entity(entity_id)
        self.assertTrue(result)
        
        # Проверяем, что сущность создана
        self.assertIn(entity_id, self.evolution_system.evolution_progress)
        self.assertIn(entity_id, self.evolution_system.entity_genes)
        
        # Проверяем прогресс эволюции
        progress = self.evolution_system.evolution_progress[entity_id]
        self.assertEqual(progress.current_stage, EvolutionStage.BASIC)
        self.assertEqual(progress.evolution_points, 0)
        self.assertEqual(progress.required_points, 100)
        
        # Проверяем базовые гены
        genes = self.evolution_system.entity_genes[entity_id]
        self.assertGreater(len(genes), 0)
        
        # Уничтожаем сущность
        result = self.evolution_system.destroy_evolution_entity(entity_id)
        self.assertTrue(result)
        
        # Проверяем, что сущность удалена
        self.assertNotIn(entity_id, self.evolution_system.evolution_progress)
        self.assertNotIn(entity_id, self.evolution_system.entity_genes)
    
    def test_evolution_points_management(self):
        """Тест управления очками эволюции"""
        # Инициализируем систему
        self.evolution_system.initialize()
        
        # Создаем тестовую сущность
        entity_id = "test_entity_2"
        self.evolution_system.create_evolution_entity(entity_id)
        
        # Добавляем очки эволюции
        points_to_add = 50
        result = self.evolution_system.add_evolution_points(entity_id, points_to_add)
        self.assertTrue(result)
        
        # Проверяем, что очки добавлены
        progress = self.evolution_system.evolution_progress[entity_id]
        self.assertEqual(progress.evolution_points, points_to_add)
        
        # Проверяем историю
        self.assertGreater(len(self.evolution_system.evolution_history), 0)
        last_entry = self.evolution_system.evolution_history[-1]
        self.assertEqual(last_entry['action'], 'points_gained')
        self.assertEqual(last_entry['entity_id'], entity_id)
        self.assertEqual(last_entry['points'], points_to_add)
    
    def test_gene_management(self):
        """Тест управления генами"""
        # Инициализируем систему
        self.evolution_system.initialize()
        
        # Создаем тестовую сущность
        entity_id = "test_entity_3"
        self.evolution_system.create_evolution_entity(entity_id)
        
        # Получаем гены сущности
        genes_info = self.evolution_system.get_entity_genes(entity_id)
        self.assertGreater(len(genes_info), 0)
        
        # Проверяем структуру информации о генах
        for gene_info in genes_info:
            self.assertIn('gene_id', gene_info)
            self.assertIn('gene_type', gene_info)
            self.assertIn('rarity', gene_info)
            self.assertIn('strength', gene_info)
            self.assertIn('active', gene_info)
        
        # Тестируем активацию/деактивацию генов
        if genes_info:
            first_gene_id = genes_info[0]['gene_id']
            
            # Деактивируем ген
            result = self.evolution_system.deactivate_gene(entity_id, first_gene_id)
            self.assertTrue(result)
            
            # Проверяем, что ген деактивирован
            updated_genes_info = self.evolution_system.get_entity_genes(entity_id)
            for gene_info in updated_genes_info:
                if gene_info['gene_id'] == first_gene_id:
                    self.assertFalse(gene_info['active'])
                    break
            
            # Активируем ген обратно
            result = self.evolution_system.activate_gene(entity_id, first_gene_id)
            self.assertTrue(result)
    
    def test_evolution_progress_retrieval(self):
        """Тест получения прогресса эволюции"""
        # Инициализируем систему
        self.evolution_system.initialize()
        
        # Создаем тестовую сущность
        entity_id = "test_entity_4"
        self.evolution_system.create_evolution_entity(entity_id)
        
        # Получаем прогресс эволюции
        progress_info = self.evolution_system.get_evolution_progress(entity_id)
        self.assertIsNotNone(progress_info)
        
        # Проверяем структуру информации о прогрессе
        self.assertIn('entity_id', progress_info)
        self.assertIn('current_stage', progress_info)
        self.assertIn('evolution_points', progress_info)
        self.assertIn('required_points', progress_info)
        self.assertIn('evolution_history', progress_info)
        
        # Проверяем значения
        self.assertEqual(progress_info['entity_id'], entity_id)
        self.assertEqual(progress_info['current_stage'], EvolutionStage.BASIC.value)
        self.assertEqual(progress_info['evolution_points'], 0)
        self.assertEqual(progress_info['required_points'], 100)
    
    def test_system_info_retrieval(self):
        """Тест получения информации о системе"""
        # Инициализируем систему
        self.evolution_system.initialize()
        
        # Получаем информацию о системе
        system_info = self.evolution_system.get_system_info()
        
        # Проверяем структуру информации
        self.assertIn('name', system_info)
        self.assertIn('state', system_info)
        self.assertIn('priority', system_info)
        self.assertIn('entities_evolving', system_info)
        self.assertIn('total_genes', system_info)
        self.assertIn('evolution_triggers', system_info)
        self.assertIn('stats', system_info)
        
        # Проверяем значения
        self.assertEqual(system_info['name'], "evolution")
        self.assertEqual(system_info['priority'], Priority.HIGH.value)
        self.assertEqual(system_info['entities_evolving'], 0)
        self.assertEqual(system_info['total_genes'], 0)
        self.assertEqual(system_info['evolution_triggers'], 0)
    
    def test_event_handling(self):
        """Тест обработки событий"""
        # Инициализируем систему
        self.evolution_system.initialize()
        
        # Тестируем обработку события создания сущности
        event_data = {
            'entity_id': 'event_entity_1',
            'initial_genes': []
        }
        result = self.evolution_system.handle_event("entity_created", event_data)
        self.assertTrue(result)
        
        # Проверяем, что сущность создана
        self.assertIn('event_entity_1', self.evolution_system.evolution_progress)
        
        # Тестируем обработку события получения опыта
        event_data = {
            'entity_id': 'event_entity_1',
            'experience_amount': 100
        }
        result = self.evolution_system.handle_event("experience_gained", event_data)
        self.assertTrue(result)
        
        # Проверяем, что очки эволюции добавлены (100 опыта = 10 очков эволюции)
        progress = self.evolution_system.evolution_progress['event_entity_1']
        self.assertEqual(progress.evolution_points, 10)
    
    def test_error_handling(self):
        """Тест обработки ошибок"""
        # Инициализируем систему
        self.evolution_system.initialize()
        
        # Тестируем создание сущности с некорректным ID
        result = self.evolution_system.create_evolution_entity("")
        self.assertFalse(result)
        
        # Тестируем добавление очков несуществующей сущности
        result = self.evolution_system.add_evolution_points("nonexistent", 50)
        self.assertFalse(result)
        
        # Тестируем получение прогресса несуществующей сущности
        progress = self.evolution_system.get_evolution_progress("nonexistent")
        self.assertIsNone(progress)
        
        # Тестируем получение генов несуществующей сущности
        genes = self.evolution_system.get_entity_genes("nonexistent")
        self.assertEqual(genes, [])
    
    def test_reset_stats(self):
        """Тест сброса статистики"""
        # Инициализируем систему
        self.evolution_system.initialize()
        
        # Создаем несколько сущностей для накопления статистики
        for i in range(3):
            self.evolution_system.create_evolution_entity(f"test_entity_{i}")
        
        # Проверяем, что статистика изменилась
        self.assertEqual(self.evolution_system.system_stats['entities_evolving'], 3)
        
        # Сбрасываем статистику
        self.evolution_system.reset_stats()
        
        # Проверяем, что статистика сброшена
        self.assertEqual(self.evolution_system.system_stats['entities_evolving'], 0)
        self.assertEqual(self.evolution_system.system_stats['total_evolutions'], 0)
        self.assertEqual(self.evolution_system.system_stats['mutations_occurred'], 0)
        self.assertEqual(self.evolution_system.system_stats['adaptations_occurred'], 0)
        self.assertEqual(self.evolution_system.system_stats['genes_activated'], 0)
        self.assertEqual(self.evolution_system.system_stats['update_time'], 0.0)

if __name__ == '__main__':
    unittest.main()
