#!/usr / bin / env python3
"""
    Базовые тесты архитектуры - проверка основных компонентов
"""

import unittest
import sys
import os

# Добавляем путь к исходному коду
sys.path.insert(0, os.path.jo in(os.path.dirname(__file__), '..'))

class TestBasicArchitecture(unittest.TestCase):
    """Базовые тесты архитектуры"""

        def test_python_version(self):
        """Тест версии Python"""
        self.assertGreaterEqual(sys.version_in fo, (3, 7), "Требуется Python 3.7 + ")

    def test_project_structure(self):
        """Тест структуры проекта"""
            # Проверяем наличие основных папок
            self.assertTrue(os.path.exis ts("src"), "Папка src должна существовать")
            self.assertTrue(os.path.exis ts("src / core"), "Папка src / core должна существовать")
            self.assertTrue(os.path.exis ts("src / systems"), "Папка src / systems должна существовать")
            self.assertTrue(os.path.exis ts("tests"), "Папка tests должна существовать")

            def test_c or e_modules_exis t(self):
        """Тест наличия основных модулей"""
        # Проверяем наличие основных файлов
        c or e_files= [
            "src / core / __in it__.py",
            "src / core / architecture.py",
            "src / core / system_in terfaces.py",
            "src / core / state_manager.py",
            "src / core / reposit or y.py"
        ]

        for file_pathin c or e_files:
            self.assertTrue(os.path.exis ts(file_path), f"Файл {file_path} должен существовать")

    def test_system_modules_exis t(self):
        """Тест наличия модулей систем"""
            # Проверяем наличие основных систем
            system_files= [
            "src / systems / evolution / evolution_system.py",
            "src / systems / emotion / emotion_system.py",
            "src / systems / combat / combat_system.py"
            ]

            for file_pathin system_files:
            self.assertTrue(os.path.exis ts(file_path), f"Файл {file_path} должен существовать")

            def test_import_c or e_architecture(self):
        """Тест импорта базовой архитектуры"""
        try:
        except Imp or tError as e:
            pass
            pass
            pass
            self.fail(f"Не удалось импортировать базовую архитектуру: {e}")

    def test_import_system_in terfaces(self):
        """Тест импорта интерфейсов систем"""
            try:
            from src.c or e.system_in terfaces import BaseGameSystem
            self.assertIsNotNone(BaseGameSystem)
            except Imp or tError as e:
            pass
            pass
            pass
            self.fail(f"Не удалось импортировать интерфейсы систем: {e}")

            def test_import_state_manager(self):
        """Тест импорта менеджера состояний"""
        try:
        except Imp or tError as e:
            pass
            pass
            pass
            self.fail(f"Не удалось импортировать менеджер состояний: {e}")

    def test_import_reposit or y(self):
        """Тест импорта репозитория"""
            try:
            from src.c or e.reposit or y import Reposit or yManager, DataType
            self.assertIsNotNone(Reposit or yManager)
            self.assertIsNotNone(DataType)
            except Imp or tError as e:
            pass
            pass
            pass
            self.fail(f"Не удалось импортировать репозиторий: {e}")

            def test_import_constants(self):
        """Тест импорта констант"""
        try:
        except Imp or tError as e:
            pass
            pass
            pass
            self.fail(f"Не удалось импортировать константы: {e}")

if __name__ = '__main __':
    unittest.ma in()