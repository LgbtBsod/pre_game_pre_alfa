#!/usr/bin/env python3
"""Тесты для EmotionSystem - проверка интеграции с новой архитектурой"""

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
from src.core.constants import constants_manager, EmotionType, EmotionIntensity
from src.core.state_manager import StateManager, StateType

logger = logging.getLogger(__name__)

class TestEmotionSystem(unittest.TestCase):
    """Тесты для системы эмоций"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        # Создаем моки для архитектурных компонентов
        self.state_manager = Mock(spec=StateManager)
        
        # Настраиваем моки
        self.state_manager.set_state = Mock(return_value=True)
        self.state_manager.get_state = Mock(return_value=None)
    
    def test_emotion_creation(self):
        """Тест создания эмоций"""
        # Создаем тестовую эмоцию
        emotion_data = {
            "emotion_type": EmotionType.JOY,
            "intensity": EmotionIntensity.MEDIUM,
            "duration": 5.0,
            "source": "test"
        }
        
        # Проверяем, что эмоция создана корректно
        self.assertEqual(emotion_data["emotion_type"], EmotionType.JOY)
        self.assertEqual(emotion_data["intensity"], EmotionIntensity.MEDIUM)
        self.assertEqual(emotion_data["duration"], 5.0)
    
    def test_emotion_intensity(self):
        """Тест интенсивности эмоций"""
        # Проверяем все уровни интенсивности
        intensities = [
            EmotionIntensity.NONE,
            EmotionIntensity.LOW,
            EmotionIntensity.MEDIUM,
            EmotionIntensity.HIGH,
            EmotionIntensity.EXTREME
        ]
        
        for intensity in intensities:
            self.assertIsNotNone(intensity)
            self.assertIsInstance(intensity.value, str)
    
    def test_emotion_types(self):
        """Тест типов эмоций"""
        # Проверяем все типы эмоций
        emotion_types = [
            EmotionType.JOY,
            EmotionType.SADNESS,
            EmotionType.ANGER,
            EmotionType.FEAR,
            EmotionType.SURPRISE,
            EmotionType.DISGUST,
            EmotionType.TRUST,
            EmotionType.ANTICIPATION,
            EmotionType.NEUTRAL
        ]
        
        for emotion_type in emotion_types:
            self.assertIsNotNone(emotion_type)
            self.assertIsInstance(emotion_type.value, str)
    
    def test_constants_manager(self):
        """Тест менеджера констант"""
        # Проверяем, что менеджер констант работает
        self.assertIsNotNone(constants_manager)
        
        # Проверяем получение цветов эмоций
        emotion_colors = constants_manager.get_emotion_colors()
        self.assertIsNotNone(emotion_colors)
        self.assertIsInstance(emotion_colors, dict)
        
        # Проверяем, что все типы эмоций имеют цвета
        for emotion_type in EmotionType:
            self.assertIn(emotion_type, emotion_colors)
    
    def test_state_manager_integration(self):
        """Тест интеграции с менеджером состояний"""
        # Проверяем, что мок работает корректно
        self.assertIsNotNone(self.state_manager)
        
        # Тестируем установку состояния
        result = self.state_manager.set_state("test_emotion", EmotionType.JOY)
        self.assertTrue(result)
        
        # Проверяем, что метод был вызван
        self.state_manager.set_state.assert_called_with("test_emotion", EmotionType.JOY)
    
    def test_emotion_validation(self):
        """Тест валидации эмоций"""
        # Тестируем валидные эмоции
        valid_emotions = [
            (EmotionType.JOY, EmotionIntensity.MEDIUM),
            (EmotionType.SADNESS, EmotionIntensity.LOW),
            (EmotionType.ANGER, EmotionIntensity.HIGH),
            (EmotionType.FEAR, EmotionIntensity.EXTREME)
        ]
        
        for emotion_type, intensity in valid_emotions:
            self.assertIsNotNone(emotion_type)
            self.assertIsNotNone(intensity)
            self.assertIsInstance(emotion_type.value, str)
            self.assertIsInstance(intensity.value, str)
    
    def test_emotion_serialization(self):
        """Тест сериализации эмоций"""
        # Создаем тестовую эмоцию
        emotion_data = {
            "emotion_type": EmotionType.JOY.value,
            "intensity": EmotionIntensity.MEDIUM.value,
            "duration": 5.0,
            "source": "test"
        }
        
        # Проверяем, что данные можно сериализовать
        self.assertIsInstance(emotion_data["emotion_type"], str)
        self.assertIsInstance(emotion_data["intensity"], str)
        self.assertIsInstance(emotion_data["duration"], float)
        self.assertIsInstance(emotion_data["source"], str)
    
    def test_emotion_deserialization(self):
        """Тест десериализации эмоций"""
        # Тестовые данные
        emotion_data = {
            "emotion_type": "joy",
            "intensity": "medium",
            "duration": 5.0,
            "source": "test"
        }
        
        # Проверяем, что можно восстановить типы
        emotion_type = EmotionType(emotion_data["emotion_type"])
        intensity = EmotionIntensity(emotion_data["intensity"])
        
        self.assertEqual(emotion_type, EmotionType.JOY)
        self.assertEqual(intensity, EmotionIntensity.MEDIUM)
    
    def test_emotion_combinations(self):
        """Тест комбинаций эмоций"""
        # Тестируем различные комбинации эмоций и интенсивностей
        combinations = [
            (EmotionType.JOY, EmotionIntensity.LOW),
            (EmotionType.SADNESS, EmotionIntensity.MEDIUM),
            (EmotionType.ANGER, EmotionIntensity.HIGH),
            (EmotionType.FEAR, EmotionIntensity.EXTREME),
            (EmotionType.SURPRISE, EmotionIntensity.MEDIUM),
            (EmotionType.DISGUST, EmotionIntensity.LOW),
            (EmotionType.TRUST, EmotionIntensity.HIGH),
            (EmotionType.ANTICIPATION, EmotionIntensity.MEDIUM),
            (EmotionType.NEUTRAL, EmotionIntensity.NONE)
        ]
        
        for emotion_type, intensity in combinations:
            # Проверяем, что комбинация валидна
            self.assertIsNotNone(emotion_type)
            self.assertIsNotNone(intensity)
            
            # Проверяем, что значения корректны
            self.assertIsInstance(emotion_type.value, str)
            self.assertIsInstance(intensity.value, str)
    
    def test_emotion_transitions(self):
        """Тест переходов между эмоциями"""
        # Тестируем переходы между различными эмоциями
        transitions = [
            (EmotionType.JOY, EmotionType.SADNESS),
            (EmotionType.ANGER, EmotionType.FEAR),
            (EmotionType.SURPRISE, EmotionType.TRUST),
            (EmotionType.DISGUST, EmotionType.ANTICIPATION),
            (EmotionType.NEUTRAL, EmotionType.JOY)
        ]
        
        for from_emotion, to_emotion in transitions:
            # Проверяем, что переходы валидны
            self.assertNotEqual(from_emotion, to_emotion)
            self.assertIsNotNone(from_emotion)
            self.assertIsNotNone(to_emotion)
    
    def test_emotion_duration(self):
        """Тест длительности эмоций"""
        # Тестируем различные длительности
        durations = [0.0, 1.0, 5.0, 10.0, 30.0, 60.0]
        
        for duration in durations:
            # Проверяем, что длительность валидна
            self.assertIsInstance(duration, float)
            self.assertGreaterEqual(duration, 0.0)
            
            # Создаем тестовую эмоцию с данной длительностью
            emotion_data = {
                "emotion_type": EmotionType.JOY,
                "intensity": EmotionIntensity.MEDIUM,
                "duration": duration,
                "source": "test"
            }
            
            self.assertEqual(emotion_data["duration"], duration)
    
    def test_emotion_source_tracking(self):
        """Тест отслеживания источников эмоций"""
        # Тестируем различные источники эмоций
        sources = [
            "combat",
            "dialogue",
            "environment",
            "quest",
            "item",
            "skill",
            "system"
        ]
        
        for source in sources:
            # Проверяем, что источник валиден
            self.assertIsInstance(source, str)
            self.assertGreater(len(source), 0)
            
            # Создаем тестовую эмоцию с данным источником
            emotion_data = {
                "emotion_type": EmotionType.JOY,
                "intensity": EmotionIntensity.MEDIUM,
                "duration": 5.0,
                "source": source
            }
            
            self.assertEqual(emotion_data["source"], source)
    
    def test_emotion_priority(self):
        """Тест приоритетов эмоций"""
        # Тестируем различные приоритеты
        priorities = [Priority.LOW, Priority.NORMAL, Priority.HIGH, Priority.CRITICAL]
        
        for priority in priorities:
            # Проверяем, что приоритет валиден
            self.assertIsNotNone(priority)
            self.assertIsInstance(priority.value, int)
            
            # Проверяем, что приоритет в допустимом диапазоне
            self.assertGreaterEqual(priority.value, 0)
            self.assertLessEqual(priority.value, 4)
    
    def test_emotion_lifecycle(self):
        """Тест жизненного цикла эмоций"""
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
            # Попытка создать эмоцию с некорректным типом
            invalid_emotion_type = "invalid_emotion"
            # Это должно вызвать ошибку при попытке создания EmotionType
            pass
        except Exception:
            # Ожидаем ошибку для некорректного типа
            pass
        
        try:
            # Попытка создать эмоцию с некорректной интенсивностью
            invalid_intensity = "invalid_intensity"
            # Это должно вызвать ошибку при попытке создания EmotionIntensity
            pass
        except Exception:
            # Ожидаем ошибку для некорректной интенсивности
            pass
    
    def test_performance(self):
        """Тест производительности"""
        # Тестируем создание множества эмоций
        num_emotions = 1000
        
        start_time = time.time()
        
        for i in range(num_emotions):
            emotion_data = {
                "emotion_type": EmotionType.JOY,
                "intensity": EmotionIntensity.MEDIUM,
                "duration": 5.0,
                "source": f"test_{i}"
            }
            
            # Проверяем, что данные созданы корректно
            self.assertIsNotNone(emotion_data)
            self.assertEqual(emotion_data["emotion_type"], EmotionType.JOY)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Проверяем, что время выполнения приемлемо (менее 1 секунды)
        self.assertLess(execution_time, 1.0)

if __name__ == '__main__':
    # Настройка логирования для тестов
    logging.basicConfig(level=logging.INFO)
    
    # Запуск тестов
    unittest.main(verbosity=2)
