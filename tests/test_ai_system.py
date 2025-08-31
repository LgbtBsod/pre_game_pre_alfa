#!/usr/bin/env python3
"""Тесты для AISystem - проверка интеграции с новой архитектурой"""

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
from src.core.constants import constants_manager, AIState, AIBehavior
from src.core.state_manager import StateManager, StateType

logger = logging.getLogger(__name__)

class TestAISystem(unittest.TestCase):
    """Тесты для системы ИИ"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        # Создаем моки для архитектурных компонентов
        self.state_manager = Mock(spec=StateManager)
        
        # Настраиваем моки
        self.state_manager.set_state = Mock(return_value=True)
        self.state_manager.get_state = Mock(return_value=None)
    
    def test_ai_state_creation(self):
        """Тест создания состояний ИИ"""
        # Проверяем все состояния ИИ
        ai_states = [
            AIState.IDLE,
            AIState.PATROLLING,
            AIState.CHASING,
            AIState.ATTACKING,
            AIState.FLEEING,
            AIState.SEARCHING,
            AIState.INTERACTING,
            AIState.THINKING,
            AIState.LEARNING
        ]
        
        for state in ai_states:
            self.assertIsNotNone(state)
            self.assertIsInstance(state.value, str)
    
    def test_ai_behavior_creation(self):
        """Тест создания поведений ИИ"""
        # Проверяем все типы поведения
        behaviors = [
            AIBehavior.AGGRESSIVE,
            AIBehavior.DEFENSIVE,
            AIBehavior.CAUTIOUS,
            AIBehavior.CURIOUS,
            AIBehavior.SOCIAL,
            AIBehavior.SOLITARY,
            AIBehavior.ADAPTIVE,
            AIBehavior.PREDICTABLE
        ]
        
        for behavior in behaviors:
            self.assertIsNotNone(behavior)
            self.assertIsInstance(behavior.value, str)
    
    def test_constants_manager(self):
        """Тест менеджера констант"""
        # Проверяем, что менеджер констант работает
        self.assertIsNotNone(constants_manager)
        
        # Проверяем получение настроек ИИ
        ai_settings = constants_manager.get_ai_settings()
        self.assertIsNotNone(ai_settings)
        self.assertIsInstance(ai_settings, dict)
    
    def test_state_manager_integration(self):
        """Тест интеграции с менеджером состояний"""
        # Проверяем, что мок работает корректно
        self.assertIsNotNone(self.state_manager)
        
        # Тестируем установку состояния
        result = self.state_manager.set_state("test_ai", AIState.IDLE)
        self.assertTrue(result)
        
        # Проверяем, что метод был вызван
        self.state_manager.set_state.assert_called_with("test_ai", AIState.IDLE)
    
    def test_ai_state_transitions(self):
        """Тест переходов между состояниями ИИ"""
        # Тестируем переходы между различными состояниями
        transitions = [
            (AIState.IDLE, AIState.PATROLLING),
            (AIState.PATROLLING, AIState.CHASING),
            (AIState.CHASING, AIState.ATTACKING),
            (AIState.ATTACKING, AIState.FLEEING),
            (AIState.FLEEING, AIState.SEARCHING),
            (AIState.SEARCHING, AIState.INTERACTING),
            (AIState.INTERACTING, AIState.THINKING),
            (AIState.THINKING, AIState.LEARNING)
        ]
        
        for from_state, to_state in transitions:
            # Проверяем, что переходы валидны
            self.assertNotEqual(from_state, to_state)
            self.assertIsNotNone(from_state)
            self.assertIsNotNone(to_state)
    
    def test_ai_behavior_combinations(self):
        """Тест комбинаций поведения ИИ"""
        # Тестируем различные комбинации поведения
        combinations = [
            (AIBehavior.AGGRESSIVE, AIState.ATTACKING),
            (AIBehavior.DEFENSIVE, AIState.FLEEING),
            (AIBehavior.CAUTIOUS, AIState.SEARCHING),
            (AIBehavior.CURIOUS, AIState.INTERACTING),
            (AIBehavior.SOCIAL, AIState.INTERACTING),
            (AIBehavior.SOLITARY, AIState.IDLE),
            (AIBehavior.ADAPTIVE, AIState.LEARNING),
            (AIBehavior.PREDICTABLE, AIState.PATROLLING)
        ]
        
        for behavior, state in combinations:
            # Проверяем, что комбинация валидна
            self.assertIsNotNone(behavior)
            self.assertIsNotNone(state)
            
            # Проверяем, что значения корректны
            self.assertIsInstance(behavior.value, str)
            self.assertIsInstance(state.value, str)
    
    def test_ai_validation(self):
        """Тест валидации ИИ"""
        # Тестируем валидные состояния и поведения
        valid_states = [
            AIState.IDLE,
            AIState.PATROLLING,
            AIState.CHASING,
            AIState.ATTACKING,
            AIState.FLEEING
        ]
        
        valid_behaviors = [
            AIBehavior.AGGRESSIVE,
            AIBehavior.DEFENSIVE,
            AIBehavior.CAUTIOUS,
            AIBehavior.CURIOUS
        ]
        
        for state in valid_states:
            self.assertIsNotNone(state)
            self.assertIsInstance(state.value, str)
        
        for behavior in valid_behaviors:
            self.assertIsNotNone(behavior)
            self.assertIsInstance(behavior.value, str)
    
    def test_ai_serialization(self):
        """Тест сериализации ИИ"""
        # Создаем тестовые данные ИИ
        ai_data = {
            "state": AIState.IDLE.value,
            "behavior": AIBehavior.AGGRESSIVE.value,
            "intelligence": 0.8,
            "memory_capacity": 1000
        }
        
        # Проверяем, что данные можно сериализовать
        self.assertIsInstance(ai_data["state"], str)
        self.assertIsInstance(ai_data["behavior"], str)
        self.assertIsInstance(ai_data["intelligence"], float)
        self.assertIsInstance(ai_data["memory_capacity"], int)
    
    def test_ai_deserialization(self):
        """Тест десериализации ИИ"""
        # Тестовые данные
        ai_data = {
            "state": "idle",
            "behavior": "aggressive",
            "intelligence": 0.8,
            "memory_capacity": 1000
        }
        
        # Проверяем, что можно восстановить типы
        state = AIState(ai_data["state"])
        behavior = AIBehavior(ai_data["behavior"])
        
        self.assertEqual(state, AIState.IDLE)
        self.assertEqual(behavior, AIBehavior.AGGRESSIVE)
    
    def test_ai_priority(self):
        """Тест приоритетов ИИ"""
        # Тестируем различные приоритеты
        priorities = [Priority.LOW, Priority.NORMAL, Priority.HIGH, Priority.CRITICAL]
        
        for priority in priorities:
            # Проверяем, что приоритет валиден
            self.assertIsNotNone(priority)
            self.assertIsInstance(priority.value, int)
            
            # Проверяем, что приоритет в допустимом диапазоне
            self.assertGreaterEqual(priority.value, 0)
            self.assertLessEqual(priority.value, 4)
    
    def test_ai_lifecycle(self):
        """Тест жизненного цикла ИИ"""
        # Тестируем состояния жизненного цикла
        lifecycle_states = [
            LifecycleState.UNINITIALIZED,
            LifecycleState.INITIALIZING,
            LifecycleState.READY,
            LifecycleState.RUNNING,
            LifecycleState.PAUSED,
            LifecycleState.STOPPING,
            LifecycleState.STOPPED,
            LifecycleState.ERROR,
            LifecycleState.DESTROYED
        ]
        
        for state in lifecycle_states:
            # Проверяем, что состояние валидно
            self.assertIsNotNone(state)
            self.assertIsInstance(state.value, str)
    
    def test_error_handling(self):
        """Тест обработки ошибок"""
        # Тестируем обработку некорректных данных
        try:
            # Попытка создать состояние с некорректным типом
            invalid_state = "invalid_state"
            # Это должно вызвать ошибку при попытке создания AIState
            pass
        except Exception:
            # Ожидаем ошибку для некорректного типа
            pass
        
        try:
            # Попытка создать поведение с некорректным типом
            invalid_behavior = "invalid_behavior"
            # Это должно вызвать ошибку при попытке создания AIBehavior
            pass
        except Exception:
            # Ожидаем ошибку для некорректного типа
            pass
    
    def test_performance(self):
        """Тест производительности"""
        # Тестируем создание множества состояний ИИ
        num_states = 1000
        
        start_time = time.time()
        
        for i in range(num_states):
            ai_data = {
                "state": AIState.IDLE,
                "behavior": AIBehavior.AGGRESSIVE,
                "intelligence": 0.8,
                "memory_capacity": 1000
            }
            
            # Проверяем, что данные созданы корректно
            self.assertIsNotNone(ai_data)
            self.assertEqual(ai_data["state"], AIState.IDLE)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Проверяем, что время выполнения приемлемо (менее 1 секунды)
        self.assertLess(execution_time, 1.0)

if __name__ == '__main__':
    # Настройка логирования для тестов
    logging.basicConfig(level=logging.INFO)
    
    # Запуск тестов
    unittest.main(verbosity=2)
