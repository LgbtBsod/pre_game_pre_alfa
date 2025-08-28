#!/usr/bin/env python3
"""
Тесты для EmotionSystem - проверка интеграции с новой архитектурой
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
from src.systems.emotion.emotion_system import EmotionSystem, Emotion, EmotionalState, EmotionalTrigger
from src.core.constants import EmotionType, EmotionIntensity

class TestEmotionSystem(unittest.TestCase):
    """Тесты для системы эмоций"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.emotion_system = EmotionSystem()
        
        # Создаем моки для архитектурных компонентов
        self.state_manager = Mock(spec=StateManager)
        self.repository_manager = Mock(spec=RepositoryManager)
        
        # Настраиваем моки
        self.state_manager.update_state = Mock(return_value=True)
        self.repository_manager.register_repository = Mock(return_value=True)
        
        # Устанавливаем компоненты архитектуры
        self.emotion_system.set_architecture_components(
            self.state_manager, 
            self.repository_manager
        )
    
    def test_initialization(self):
        """Тест инициализации системы"""
        # Проверяем начальное состояние
        self.assertEqual(self.emotion_system.system_name, "emotions")
        self.assertEqual(self.emotion_system.system_priority, Priority.NORMAL)
        self.assertEqual(self.emotion_system.system_state, LifecycleState.UNINITIALIZED)
        
        # Проверяем, что компоненты архитектуры установлены
        self.assertIsNotNone(self.emotion_system.state_manager)
        self.assertIsNotNone(self.emotion_system.repository_manager)
    
    def test_register_system_states(self):
        """Тест регистрации состояний системы"""
        # Вызываем регистрацию состояний
        self.emotion_system._register_system_states()
        
        # Проверяем, что состояния зарегистрированы
        self.state_manager.update_state.assert_called()
        
        # Проверяем количество вызовов (должно быть 3: настройки, статистика, состояние)
        self.assertEqual(self.state_manager.update_state.call_count, 3)
    
    def test_register_system_repositories(self):
        """Тест регистрации репозиториев системы"""
        # Вызываем регистрацию репозиториев
        self.emotion_system._register_system_repositories()
        
        # Проверяем, что репозитории зарегистрированы
        self.repository_manager.register_repository.assert_called()
        
        # Проверяем количество вызовов (должно быть 4 репозитория)
        self.assertEqual(self.repository_manager.register_repository.call_count, 4)
    
    def test_lifecycle_management(self):
        """Тест управления жизненным циклом"""
        # Тестируем инициализацию
        result = self.emotion_system.initialize()
        self.assertTrue(result)
        self.assertEqual(self.emotion_system.system_state, LifecycleState.READY)
        
        # Тестируем запуск
        result = self.emotion_system.start()
        self.assertTrue(result)
        self.assertEqual(self.emotion_system.system_state, LifecycleState.RUNNING)
        
        # Тестируем остановку
        result = self.emotion_system.stop()
        self.assertTrue(result)
        self.assertEqual(self.emotion_system.system_state, LifecycleState.STOPPED)
        
        # Тестируем уничтожение
        result = self.emotion_system.destroy()
        self.assertTrue(result)
        self.assertEqual(self.emotion_system.system_state, LifecycleState.DESTROYED)
    
    def test_emotion_creation(self):
        """Тест создания эмоций"""
        # Инициализируем систему
        self.emotion_system.initialize()
        
        # Создаем тестовую эмоцию
        emotion = Emotion(
            emotion_id="test_emotion_1",
            emotion_type=EmotionType.JOY,
            intensity=EmotionIntensity.MEDIUM,
            value=0.5,
            duration=10.0
        )
        
        # Проверяем, что эмоция создана корректно
        self.assertEqual(emotion.emotion_id, "test_emotion_1")
        self.assertEqual(emotion.emotion_type, EmotionType.JOY)
        self.assertEqual(emotion.intensity, EmotionIntensity.MEDIUM)
        self.assertEqual(emotion.value, 0.5)
        self.assertEqual(emotion.duration, 10.0)
        self.assertTrue(emotion.start_time > 0)
    
    def test_emotional_state_creation(self):
        """Тест создания эмоционального состояния"""
        # Инициализируем систему
        self.emotion_system.initialize()
        
        # Создаем тестовое эмоциональное состояние
        emotional_state = EmotionalState(
            entity_id="test_entity_1",
            emotions=[],
            mood=0.0,
            stress_level=0.1,
            emotional_stability=0.7
        )
        
        # Проверяем, что состояние создано корректно
        self.assertEqual(emotional_state.entity_id, "test_entity_1")
        self.assertEqual(emotional_state.mood, 0.0)
        self.assertEqual(emotional_state.stress_level, 0.1)
        self.assertEqual(emotional_state.emotional_stability, 0.7)
        self.assertEqual(len(emotional_state.emotions), 0)
        self.assertTrue(emotional_state.last_update > 0)
    
    def test_emotion_trigger_creation(self):
        """Тест создания триггера эмоций"""
        # Инициализируем систему
        self.emotion_system.initialize()
        
        # Создаем тестовый триггер
        trigger = EmotionalTrigger(
            trigger_id="test_trigger_1",
            trigger_type="combat_victory",
            emotion_type=EmotionType.JOY,
            intensity=EmotionIntensity.HIGH,
            conditions={'min_health': 0.5},
            duration=30.0,
            probability=0.8
        )
        
        # Проверяем, что триггер создан корректно
        self.assertEqual(trigger.trigger_id, "test_trigger_1")
        self.assertEqual(trigger.trigger_type, "combat_victory")
        self.assertEqual(trigger.emotion_type, EmotionType.JOY)
        self.assertEqual(trigger.intensity, EmotionIntensity.HIGH)
        self.assertEqual(trigger.duration, 30.0)
        self.assertEqual(trigger.probability, 0.8)
        self.assertEqual(trigger.conditions['min_health'], 0.5)
    
    def test_system_info_retrieval(self):
        """Тест получения информации о системе"""
        # Инициализируем систему
        self.emotion_system.initialize()
        
        # Получаем информацию о системе
        system_info = self.emotion_system.get_system_info()
        
        # Проверяем структуру информации
        self.assertIn('name', system_info)
        self.assertIn('state', system_info)
        self.assertIn('priority', system_info)
        self.assertIn('entities_with_emotions', system_info)
        self.assertIn('total_emotions', system_info)
        self.assertIn('emotions_triggered', system_info)
        self.assertIn('mood_changes', system_info)
        self.assertIn('stress_events', system_info)
        self.assertIn('update_time', system_info)
        
        # Проверяем значения
        self.assertEqual(system_info['name'], "emotions")
        self.assertEqual(system_info['priority'], Priority.NORMAL.value)
        self.assertEqual(system_info['entities_with_emotions'], 0)
        self.assertEqual(system_info['total_emotions'], 0)
        self.assertEqual(system_info['emotions_triggered'], 0)
        self.assertEqual(system_info['mood_changes'], 0)
        self.assertEqual(system_info['stress_events'], 0)
        self.assertEqual(system_info['update_time'], 0.0)
    
    def test_error_handling(self):
        """Тест обработки ошибок"""
        # Инициализируем систему
        self.emotion_system.initialize()
        
        # Тестируем обработку некорректных данных
        # (здесь можно добавить тесты для различных сценариев ошибок)
        pass
    
    def test_reset_stats(self):
        """Тест сброса статистики"""
        # Инициализируем систему
        self.emotion_system.initialize()
        
        # Изменяем статистику
        self.emotion_system.system_stats['entities_with_emotions'] = 5
        self.emotion_system.system_stats['total_emotions'] = 10
        
        # Сбрасываем статистику
        self.emotion_system.reset_stats()
        
        # Проверяем, что статистика сброшена
        self.assertEqual(self.emotion_system.system_stats['entities_with_emotions'], 0)
        self.assertEqual(self.emotion_system.system_stats['total_emotions'], 0)
        self.assertEqual(self.emotion_system.system_stats['emotions_triggered'], 0)
        self.assertEqual(self.emotion_system.system_stats['mood_changes'], 0)
        self.assertEqual(self.emotion_system.system_stats['stress_events'], 0)
        self.assertEqual(self.emotion_system.system_stats['update_time'], 0.0)
    
    def test_system_settings(self):
        """Тест настроек системы"""
        # Инициализируем систему
        self.emotion_system.initialize()
        
        # Проверяем, что настройки установлены
        self.assertIn('max_emotions_per_entity', self.emotion_system.system_settings)
        self.assertIn('emotion_decay_rate', self.emotion_system.system_settings)
        self.assertIn('mood_update_interval', self.emotion_system.system_settings)
        self.assertIn('stress_decay_rate', self.emotion_system.system_settings)
        self.assertIn('emotional_stability_range', self.emotion_system.system_settings)
        
        # Проверяем типы значений
        self.assertIsInstance(self.emotion_system.system_settings['emotion_decay_rate'], float)
        self.assertIsInstance(self.emotion_system.system_settings['stress_decay_rate'], float)
        self.assertIsInstance(self.emotion_system.system_settings['emotional_stability_range'], tuple)
    
    def test_emotion_constants(self):
        """Тест констант эмоций"""
        # Проверяем, что все типы эмоций доступны
        self.assertIsNotNone(EmotionType.JOY)
        self.assertIsNotNone(EmotionType.SADNESS)
        self.assertIsNotNone(EmotionType.ANGER)
        self.assertIsNotNone(EmotionType.FEAR)
        self.assertIsNotNone(EmotionType.SURPRISE)
        self.assertIsNotNone(EmotionType.DISGUST)
        
        # Проверяем, что все уровни интенсивности доступны
        self.assertIsNotNone(EmotionIntensity.LOW)
        self.assertIsNotNone(EmotionIntensity.MEDIUM)
        self.assertIsNotNone(EmotionIntensity.HIGH)
        self.assertIsNotNone(EmotionIntensity.EXTREME)

if __name__ == '__main__':
    unittest.main()
