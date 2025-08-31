#!/usr/bin/env python3
"""Тесты для EvolutionSystem - проверка интеграции с новой архитектурой"""

# Добавляем путь к исходному коду
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import logging
import time
import unittest
from typing import *
from unittest.mock import Mock, MagicMock

from src.core.architecture import Priority, LifecycleState
from src.core.state_manager import StateManager, StateType
from src.systems.evolution.evolution_system import EvolutionSystem

logger = logging.getLogger(__name__)

class TestEvolutionSystem(unittest.TestCase):
    """Тесты для системы эволюции"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.evolution_system = EvolutionSystem()
        
        # Создаем моки для архитектурных компонентов
        self.state_manager = Mock(spec=StateManager)
        
        # Настраиваем моки
        self.state_manager.set_state = Mock(return_value=True)
        self.state_manager.get_state = Mock(return_value=None)
        
        # Устанавливаем компоненты архитектуры
        self.evolution_system.state_manager = self.state_manager
    
    def test_initialization(self):
        """Тест инициализации системы"""
        # Проверяем начальное состояние
        self.assertEqual(self.evolution_system.component_id, "evolution_system")
        self.assertEqual(self.evolution_system.priority, Priority.HIGH)
        self.assertEqual(self.evolution_system.state, LifecycleState.UNINITIALIZED)
        
        # Проверяем, что компоненты архитектуры установлены
        self.assertIsNotNone(self.evolution_system.state_manager)
    
    def test_lifecycle_management(self):
        """Тест управления жизненным циклом"""
        # Тестируем инициализацию
        self.assertTrue(self.evolution_system.initialize())
        self.assertEqual(self.evolution_system.state, LifecycleState.READY)
        
        # Тестируем запуск
        self.assertTrue(self.evolution_system.start())
        self.assertEqual(self.evolution_system.state, LifecycleState.RUNNING)
        
        # Тестируем приостановку
        self.assertTrue(self.evolution_system.pause())
        self.assertEqual(self.evolution_system.state, LifecycleState.PAUSED)
        
        # Тестируем возобновление
        self.assertTrue(self.evolution_system.resume())
        self.assertEqual(self.evolution_system.state, LifecycleState.RUNNING)
        
        # Тестируем остановку
        self.assertTrue(self.evolution_system.stop())
        self.assertEqual(self.evolution_system.state, LifecycleState.READY)
    
    def test_gene_creation(self):
        """Тест создания генов"""
        # Создаем тестовый ген
        gene_data = {
            "gene_id": "test_gene",
            "gene_type": "PHYSICAL",
            "name": "Test Gene",
            "description": "Test gene for testing",
            "base_value": 10.0,
            "max_value": 100.0,
            "mutation_chance": 0.1
        }
        
        gene = self.evolution_system.create_gene(**gene_data)
        
        # Проверяем создание гена
        self.assertIsNotNone(gene)
        self.assertEqual(gene.gene_id, "test_gene")
        self.assertEqual(gene.gene_type.value, "PHYSICAL")
        self.assertEqual(gene.base_value, 10.0)
    
    def test_mutation_creation(self):
        """Тест создания мутаций"""
        # Создаем тестовую мутацию
        mutation_data = {
            "mutation_id": "test_mutation",
            "gene_id": "test_gene",
            "name": "Test Mutation",
            "description": "Test mutation for testing",
            "mutation_type": "SPONTANEOUS",
            "level": "MINOR",
            "value_change": 5.0
        }
        
        mutation = self.evolution_system.create_mutation(**mutation_data)
        
        # Проверяем создание мутации
        self.assertIsNotNone(mutation)
        self.assertEqual(mutation.mutation_id, "test_mutation")
        self.assertEqual(mutation.gene_id, "test_gene")
        self.assertEqual(mutation.value_change, 5.0)
    
    def test_evolution_tree_creation(self):
        """Тест создания дерева эволюции"""
        # Создаем тестовое дерево эволюции
        tree_data = {
            "tree_id": "test_tree",
            "name": "Test Evolution Tree",
            "description": "Test evolution tree for testing",
            "max_level": 5,
            "requirements": []
        }
        
        tree = self.evolution_system.create_evolution_tree(**tree_data)
        
        # Проверяем создание дерева
        self.assertIsNotNone(tree)
        self.assertEqual(tree.tree_id, "test_tree")
        self.assertEqual(tree.max_level, 5)
    
    def test_entity_evolution(self):
        """Тест эволюции сущности"""
        # Создаем тестовую сущность
        entity_id = "test_entity"
        
        # Инициализируем эволюцию для сущности
        self.evolution_system.initialize_entity_evolution(entity_id)
        
        # Проверяем, что эволюция инициализирована
        self.assertTrue(self.evolution_system.has_entity_evolution(entity_id))
        
        # Получаем прогресс эволюции
        progress = self.evolution_system.get_entity_evolution_progress(entity_id)
        self.assertIsNotNone(progress)
        self.assertEqual(progress.entity_id, entity_id)
    
    def test_gene_mutation(self):
        """Тест мутации генов"""
        # Создаем тестовый ген
        gene_data = {
            "gene_id": "test_gene",
            "gene_type": "PHYSICAL",
            "name": "Test Gene",
            "description": "Test gene for testing",
            "base_value": 10.0,
            "max_value": 100.0,
            "mutation_chance": 0.5  # Высокая вероятность мутации для теста
        }
        
        gene = self.evolution_system.create_gene(**gene_data)
        
        # Применяем мутацию
        mutation_result = self.evolution_system.apply_gene_mutation(gene, "test_source")
        
        # Проверяем результат мутации
        self.assertIsNotNone(mutation_result)
        self.assertGreaterEqual(mutation_result.value_change, 0)
    
    def test_evolution_trigger(self):
        """Тест триггеров эволюции"""
        # Создаем тестовый триггер
        trigger_data = {
            "trigger_id": "test_trigger",
            "name": "Test Trigger",
            "description": "Test trigger for testing",
            "trigger_type": "LEVEL_UP",
            "conditions": {"level": 5},
            "effects": {"evolution_points": 10}
        }
        
        trigger = self.evolution_system.create_evolution_trigger(**trigger_data)
        
        # Проверяем создание триггера
        self.assertIsNotNone(trigger)
        self.assertEqual(trigger.trigger_id, "test_trigger")
        self.assertEqual(trigger.trigger_type.value, "LEVEL_UP")
    
    def test_evolution_calculation(self):
        """Тест расчета эволюции"""
        # Создаем тестовую сущность с генами
        entity_id = "test_entity"
        
        # Создаем несколько генов
        genes = []
        for i in range(3):
            gene_data = {
                "gene_id": f"gene_{i}",
                "gene_type": "PHYSICAL",
                "name": f"Gene {i}",
                "description": f"Test gene {i}",
                "base_value": 10.0 + i * 5,
                "max_value": 100.0,
                "mutation_chance": 0.1
            }
            gene = self.evolution_system.create_gene(**gene_data)
            genes.append(gene)
        
        # Инициализируем эволюцию
        self.evolution_system.initialize_entity_evolution(entity_id)
        
        # Добавляем гены к сущности
        for gene in genes:
            self.evolution_system.add_gene_to_entity(entity_id, gene)
        
        # Рассчитываем эволюцию
        evolution_result = self.evolution_system.calculate_entity_evolution(entity_id)
        
        # Проверяем результат расчета
        self.assertIsNotNone(evolution_result)
        self.assertGreaterEqual(evolution_result.total_evolution_points, 0)
    
    def test_evolution_history(self):
        """Тест истории эволюции"""
        # Создаем тестовую сущность
        entity_id = "test_entity"
        
        # Инициализируем эволюцию
        self.evolution_system.initialize_entity_evolution(entity_id)
        
        # Создаем несколько событий эволюции
        for i in range(3):
            event_data = {
                "event_id": f"event_{i}",
                "entity_id": entity_id,
                "event_type": "GENE_MUTATION",
                "description": f"Test evolution event {i}",
                "timestamp": time.time() + i
            }
            self.evolution_system.record_evolution_event(**event_data)
        
        # Получаем историю эволюции
        history = self.evolution_system.get_entity_evolution_history(entity_id)
        
        # Проверяем историю
        self.assertIsNotNone(history)
        self.assertEqual(len(history), 3)
    
    def test_cleanup(self):
        """Тест очистки системы"""
        # Создаем тестовые данные
        entity_id = "test_entity"
        self.evolution_system.initialize_entity_evolution(entity_id)
        
        # Проверяем, что данные созданы
        self.assertTrue(self.evolution_system.has_entity_evolution(entity_id))
        
        # Очищаем систему
        self.evolution_system.cleanup()
        
        # Проверяем, что система очищена
        self.assertEqual(self.evolution_system.state, LifecycleState.DESTROYED)
    
    def test_error_handling(self):
        """Тест обработки ошибок"""
        # Тестируем обработку несуществующей сущности
        non_existent_entity = "non_existent_entity"
        
        # Попытка получить эволюцию несуществующей сущности
        progress = self.evolution_system.get_entity_evolution_progress(non_existent_entity)
        self.assertIsNone(progress)
        
        # Попытка добавить ген к несуществующей сущности
        gene_data = {
            "gene_id": "test_gene",
            "gene_type": "PHYSICAL",
            "name": "Test Gene",
            "description": "Test gene",
            "base_value": 10.0,
            "max_value": 100.0,
            "mutation_chance": 0.1
        }
        gene = self.evolution_system.create_gene(**gene_data)
        
        result = self.evolution_system.add_gene_to_entity(non_existent_entity, gene)
        self.assertFalse(result)
    
    def test_performance(self):
        """Тест производительности"""
        # Создаем множество сущностей для тестирования производительности
        num_entities = 100
        
        start_time = time.time()
        
        for i in range(num_entities):
            entity_id = f"entity_{i}"
            self.evolution_system.initialize_entity_evolution(entity_id)
            
            # Добавляем несколько генов к каждой сущности
            for j in range(5):
                gene_data = {
                    "gene_id": f"gene_{i}_{j}",
                    "gene_type": "PHYSICAL",
                    "name": f"Gene {i}_{j}",
                    "description": f"Test gene {i}_{j}",
                    "base_value": 10.0 + j,
                    "max_value": 100.0,
                    "mutation_chance": 0.1
                }
                gene = self.evolution_system.create_gene(**gene_data)
                self.evolution_system.add_gene_to_entity(entity_id, gene)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Проверяем, что время выполнения приемлемо (менее 1 секунды)
        self.assertLess(execution_time, 1.0)
        
        # Проверяем, что все сущности созданы
        for i in range(num_entities):
            entity_id = f"entity_{i}"
            self.assertTrue(self.evolution_system.has_entity_evolution(entity_id))

if __name__ == '__main__':
    # Настройка логирования для тестов
    logging.basicConfig(level=logging.INFO)
    
    # Запуск тестов
    unittest.main(verbosity=2)
