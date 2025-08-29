#!/usr/bin/env python3
"""
Базовые тесты архитектуры - проверка основных компонентов
"""

import unittest
import sys
import os

# Добавляем путь к исходному коду
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestBasicArchitecture(unittest.TestCase):
    """Базовые тесты архитектуры"""
    
    def test_python_version(self):
        """Тест версии Python"""
        self.assertGreaterEqual(sys.version_info, (3, 7), "Требуется Python 3.7+")
    
    def test_project_structure(self):
        """Тест структуры проекта"""
        # Проверяем наличие основных папок
        self.assertTrue(os.path.exists("src"), "Папка src должна существовать")
        self.assertTrue(os.path.exists("src/core"), "Папка src/core должна существовать")
        self.assertTrue(os.path.exists("src/systems"), "Папка src/systems должна существовать")
        self.assertTrue(os.path.exists("tests"), "Папка tests должна существовать")
    
    def test_core_modules_exist(self):
        """Тест наличия основных модулей"""
        # Проверяем наличие основных файлов
        core_files = [
            "src/core/__init__.py",
            "src/core/architecture.py",
            "src/core/system_interfaces.py",
            "src/core/state_manager.py",
            "src/core/repository.py"
        ]
        
        for file_path in core_files:
            self.assertTrue(os.path.exists(file_path), f"Файл {file_path} должен существовать")
    
    def test_system_modules_exist(self):
        """Тест наличия модулей систем"""
        # Проверяем наличие основных систем
        system_files = [
            "src/systems/evolution/evolution_system.py",
            "src/systems/emotion/emotion_system.py",
            "src/systems/combat/combat_system.py"
        ]
        
        for file_path in system_files:
            self.assertTrue(os.path.exists(file_path), f"Файл {file_path} должен существовать")
    
    def test_import_core_architecture(self):
        """Тест импорта базовой архитектуры"""
        try:
            from src.core.architecture import Priority, LifecycleState
            self.assertIsNotNone(Priority)
            self.assertIsNotNone(LifecycleState)
        except ImportError as e:
            self.fail(f"Не удалось импортировать базовую архитектуру: {e}")
    
    def test_import_system_interfaces(self):
        """Тест импорта интерфейсов систем"""
        try:
            from src.core.system_interfaces import BaseGameSystem
            self.assertIsNotNone(BaseGameSystem)
        except ImportError as e:
            self.fail(f"Не удалось импортировать интерфейсы систем: {e}")
    
    def test_import_state_manager(self):
        """Тест импорта менеджера состояний"""
        try:
            from src.core.state_manager import StateManager, StateType
            self.assertIsNotNone(StateManager)
            self.assertIsNotNone(StateType)
        except ImportError as e:
            self.fail(f"Не удалось импортировать менеджер состояний: {e}")
    
    def test_import_repository(self):
        """Тест импорта репозитория"""
        try:
            from src.core.repository import RepositoryManager, DataType
            self.assertIsNotNone(RepositoryManager)
            self.assertIsNotNone(DataType)
        except ImportError as e:
            self.fail(f"Не удалось импортировать репозиторий: {e}")
    
    def test_import_constants(self):
        """Тест импорта констант"""
        try:
            from src.core.constants import constants_manager, BASE_STATS, PROBABILITY_CONSTANTS
            self.assertIsNotNone(BASE_STATS)
            self.assertIsNotNone(PROBABILITY_CONSTANTS)
        except ImportError as e:
            self.fail(f"Не удалось импортировать константы: {e}")

if __name__ == '__main__':
    unittest.main()
