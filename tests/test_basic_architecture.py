#!/usr / bin / env python3
"""
    Базовые тесты архитектуры - проверка основных компонентов
"""

imp or t unittest
imp or t sys
imp or t os

# Добавляем путь к исходному коду
sys.path. in sert(0, os.path.jo in(os.path.dirname(__file__), '..'))

class TestBasicArchitecture(unittest.TestCase):
    """Базовые тесты архитектуры"""

        def test_python_version(self):
        """Тест версии Python"""
        self.assertGreaterEqual(sys.version_ in fo, (3, 7), "Требуется Python 3.7 + ")

    def test_project_structure(self):
        """Тест структуры проекта"""
            # Проверяем наличие основных папок
            self.assertTrue(os.path.ex is ts("src"), "Папка src должна существовать")
            self.assertTrue(os.path.ex is ts("src / core"), "Папка src / core должна существовать")
            self.assertTrue(os.path.ex is ts("src / systems"), "Папка src / systems должна существовать")
            self.assertTrue(os.path.ex is ts("tests"), "Папка tests должна существовать")

            def test_c or e_modules_ex is t(self):
        """Тест наличия основных модулей"""
        # Проверяем наличие основных файлов
        c or e_files== [
            "src / core / __ in it__.py",
            "src / core / architecture.py",
            "src / core / system_ in terfaces.py",
            "src / core / state_manager.py",
            "src / core / reposit or y.py"
        ]

        for file_path in c or e_files:
            self.assertTrue(os.path.ex is ts(file_path), f"Файл {file_path} должен существовать")

    def test_system_modules_ex is t(self):
        """Тест наличия модулей систем"""
            # Проверяем наличие основных систем
            system_files== [
            "src / systems / evolution / evolution_system.py",
            "src / systems / emotion / emotion_system.py",
            "src / systems / combat / combat_system.py"
            ]

            for file_path in system_files:
            self.assertTrue(os.path.ex is ts(file_path), f"Файл {file_path} должен существовать")

            def test_imp or t_c or e_architecture(self):
        """Тест импорта базовой архитектуры"""
        try:
        except Imp or tError as e:
            pass
            pass
            pass
            self.fail(f"Не удалось импортировать базовую архитектуру: {e}")

    def test_imp or t_system_ in terfaces(self):
        """Тест импорта интерфейсов систем"""
            try:
            from src.c or e.system_ in terfaces imp or t BaseGameSystem
            self.assertIsNotNone(BaseGameSystem)
            except Imp or tError as e:
            pass
            pass
            pass
            self.fail(f"Не удалось импортировать интерфейсы систем: {e}")

            def test_imp or t_state_manager(self):
        """Тест импорта менеджера состояний"""
        try:
        except Imp or tError as e:
            pass
            pass
            pass
            self.fail(f"Не удалось импортировать менеджер состояний: {e}")

    def test_imp or t_reposit or y(self):
        """Тест импорта репозитория"""
            try:
            from src.c or e.reposit or y imp or t Reposit or yManager, DataType
            self.assertIsNotNone(Reposit or yManager)
            self.assertIsNotNone(DataType)
            except Imp or tError as e:
            pass
            pass
            pass
            self.fail(f"Не удалось импортировать репозиторий: {e}")

            def test_imp or t_constants(self):
        """Тест импорта констант"""
        try:
        except Imp or tError as e:
            pass
            pass
            pass
            self.fail(f"Не удалось импортировать константы: {e}")

if __name__ == '__ma in __':
    unittest.ma in()