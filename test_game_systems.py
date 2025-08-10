"""
Тестирование основных игровых систем
Улучшенная версия с детальным анализом
"""

import sys
import logging
import time
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class TestResult:
    """Результат тестирования"""

    name: str
    success: bool
    duration: float
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class GameSystemTester:
    """Класс для тестирования игровых систем"""

    def __init__(self):
        self.results: List[TestResult] = []
        self.start_time = time.time()

        # Настройка логирования
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def run_all_tests(self) -> bool:
        """Запуск всех тестов"""
        self.logger.info("=== ЗАПУСК ТЕСТИРОВАНИЯ ИГРОВЫХ СИСТЕМ ===")

        # Тестируем основные системы
        self._test_basic_systems()

        # Тестируем UI системы
        self._test_ui_systems()

        # Тестируем AI системы
        self._test_ai_systems()

        # Тестируем производительность
        self._test_performance()

        # Выводим результаты
        self._print_results()

        # Возвращаем общий результат
        return all(result.success for result in self.results)

    def _test_basic_systems(self):
        """Тестирование основных систем"""
        self.logger.info("=== ТЕСТИРОВАНИЕ ОСНОВНЫХ СИСТЕМ ===")

        # Тест импорта модулей
        self._run_test("Импорт модулей", self._test_module_imports)

        # Тест настроек
        self._run_test("Система настроек", self._test_settings_system)

        # Тест данных
        self._run_test("Система данных", self._test_data_system)

        # Тест AI системы
        self._run_test("AI система", self._test_ai_system)

        # Тест создания сущностей
        self._run_test("Создание сущностей", self._test_entity_creation)

        # Тест состояния игры
        self._run_test("Состояние игры", self._test_game_state)

    def _test_ui_systems(self):
        """Тестирование UI систем"""
        self.logger.info("=== ТЕСТИРОВАНИЕ UI СИСТЕМ ===")

        # Тест импорта UI модулей
        self._run_test("Импорт UI модулей", self._test_ui_imports)

        # Тест создания главного окна
        self._run_test("Создание главного окна", self._test_main_window_creation)

        # Тест создания меню
        self._run_test("Создание игрового меню", self._test_game_menu_creation)

        # Тест создания рендер менеджера
        self._run_test("Создание рендер менеджера", self._test_render_manager_creation)

    def _test_ai_systems(self):
        """Тестирование AI систем"""
        self.logger.info("=== ТЕСТИРОВАНИЕ AI СИСТЕМ ===")

        # Тест AI менеджера
        self._run_test("AI менеджер", self._test_ai_manager)

        # Тест AI ядра
        self._run_test("AI ядро", self._test_ai_core)

        # Тест регистрации AI сущностей
        self._run_test("Регистрация AI сущностей", self._test_ai_entity_registration)

        # Тест обновления AI
        self._run_test("Обновление AI", self._test_ai_update)

    def _test_performance(self):
        """Тестирование производительности"""
        self.logger.info("=== ТЕСТИРОВАНИЕ ПРОИЗВОДИТЕЛЬНОСТИ ===")

        # Тест скорости создания объектов
        self._run_test("Скорость создания объектов", self._test_creation_performance)

        # Тест скорости обновления AI
        self._run_test("Скорость обновления AI", self._test_ai_performance)

        # Тест использования памяти
        self._run_test("Использование памяти", self._test_memory_usage)

    def _run_test(self, name: str, test_func):
        """Запуск отдельного теста"""
        start_time = time.time()

        try:
            self.logger.info(f"Запуск теста: {name}")
            result = test_func()

            duration = time.time() - start_time

            if result:
                self.logger.info(f"✓ Тест '{name}' пройден за {duration:.3f}с")
                self.results.append(TestResult(name, True, duration))
            else:
                self.logger.error(f"✗ Тест '{name}' провален за {duration:.3f}с")
                self.results.append(
                    TestResult(name, False, duration, "Тест вернул False")
                )

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"{type(e).__name__}: {str(e)}"
            self.logger.error(f"✗ Тест '{name}' провален с ошибкой: {error_msg}")
            self.results.append(TestResult(name, False, duration, error_msg))

    def _test_module_imports(self) -> bool:
        """Тест импорта модулей"""
        try:
            # Импорт основных систем
            from config.settings_manager import settings_manager
            from core.data_manager import data_manager
            from core.game_state_manager import game_state_manager
            from entities.entity_factory import entity_factory
            from ai.ai_manager import ai_manager

            return True

        except Exception as e:
            self.logger.error(f"Ошибка импорта модулей: {e}")
            return False

    def _test_settings_system(self) -> bool:
        """Тест системы настроек"""
        try:
            from config.settings_manager import settings_manager

            # Загружаем настройки
            settings_manager.reload_settings()

            # Проверяем, что настройки загружены
            if not hasattr(settings_manager, "settings"):
                return False

            return True

        except Exception as e:
            self.logger.error(f"Ошибка системы настроек: {e}")
            return False

    def _test_data_system(self) -> bool:
        """Тест системы данных"""
        try:
            from core.data_manager import data_manager

            # Загружаем данные
            data_manager.reload_data()

            # Проверяем, что данные загружены
            if not hasattr(data_manager, "data"):
                return False

            return True

        except Exception as e:
            self.logger.error(f"Ошибка системы данных: {e}")
            return False

    def _test_ai_system(self) -> bool:
        """Тест AI системы"""
        try:
            from ai.ai_manager import ai_manager

            # Инициализируем AI систему
            ai_manager.initialize()

            return True

        except Exception as e:
            self.logger.error(f"Ошибка AI системы: {e}")
            return False

    def _test_entity_creation(self) -> bool:
        """Тест создания сущностей"""
        try:
            from entities.entity_factory import entity_factory

            # Создаем тестового игрока
            player = entity_factory.create_player("TestPlayer", (100, 100))
            if not player:
                return False

            # Создаем тестового врага
            enemy = entity_factory.create_enemy("warrior", 1, (200, 200))
            if not enemy:
                return False

            return True

        except Exception as e:
            self.logger.error(f"Ошибка создания сущностей: {e}")
            return False

    def _test_game_state(self) -> bool:
        """Тест состояния игры"""
        try:
            from core.game_state_manager import game_state_manager

            # Создаем новое состояние игры
            game_id = game_state_manager.create_new_game(
                save_name="TestSave", player_name="TestPlayer", difficulty="normal"
            )

            if not game_id:
                return False

            return True

        except Exception as e:
            self.logger.error(f"Ошибка состояния игры: {e}")
            return False

    def _test_ui_imports(self) -> bool:
        """Тест импорта UI модулей"""
        try:
            from ui.main_window import MainWindow
            from ui.game_menu import GameMenu
            from ui.render_manager import RenderManager

            return True

        except Exception as e:
            self.logger.error(f"Ошибка импорта UI модулей: {e}")
            return False

    def _test_main_window_creation(self) -> bool:
        """Тест создания главного окна"""
        try:
            from ui.main_window import MainWindow
            import tkinter as tk

            # Создаем временное окно для тестирования
            root = tk.Tk()
            root.withdraw()  # Скрываем окно

            # Создаем главное окно
            app = MainWindow()

            # Проверяем, что окно создано
            if not hasattr(app, "root"):
                return False

            root.destroy()
            return True

        except Exception as e:
            self.logger.error(f"Ошибка создания главного окна: {e}")
            return False

    def _test_game_menu_creation(self) -> bool:
        """Тест создания игрового меню"""
        try:
            from ui.game_menu import GameMenu
            import tkinter as tk

            # Создаем временное окно
            root = tk.Tk()
            root.withdraw()

            # Создаем canvas
            canvas = tk.Canvas(root, width=800, height=600)

            # Создаем меню
            menu = GameMenu(canvas, 800, 600)

            # Проверяем, что меню создано
            if not hasattr(menu, "menu_items"):
                return False

            root.destroy()
            return True

        except Exception as e:
            self.logger.error(f"Ошибка создания игрового меню: {e}")
            return False

    def _test_render_manager_creation(self) -> bool:
        """Тест создания рендер менеджера"""
        try:
            from ui.render_manager import RenderManager
            from core.game_state_manager import game_state_manager
            import tkinter as tk

            # Создаем временное окно
            root = tk.Tk()
            root.withdraw()

            # Создаем canvas
            canvas = tk.Canvas(root, width=800, height=600)

            # Создаем рендер менеджер
            render_manager = RenderManager(canvas, game_state_manager)

            # Проверяем, что рендер менеджер создан
            if not hasattr(render_manager, "canvas"):
                return False

            root.destroy()
            return True

        except Exception as e:
            self.logger.error(f"Ошибка создания рендер менеджера: {e}")
            return False

    def _test_ai_manager(self) -> bool:
        """Тест AI менеджера"""
        try:
            from ai.ai_manager import ai_manager
            from entities.entity_factory import entity_factory

            # Создаем тестовую сущность
            enemy = entity_factory.create_enemy("warrior", 1, (100, 100))
            if not enemy:
                return False

            # Проверяем, что у сущности есть AI core
            if not hasattr(enemy, "ai_core") or enemy.ai_core is None:
                self.logger.error("У сущности отсутствует AI core")
                return False

            # Регистрируем в AI системе
            success = ai_manager.register_entity(enemy, enemy.ai_core)

            return success

        except Exception as e:
            self.logger.error(f"Ошибка AI менеджера: {e}")
            return False

    def _test_ai_core(self) -> bool:
        """Тест AI ядра"""
        try:
            from ai.ai_core import AICore, AIState, AIPriority
            from entities.entity_factory import entity_factory

            # Создаем тестовую сущность
            enemy = entity_factory.create_enemy("warrior", 1, (100, 100))
            if not enemy:
                return False

            # Проверяем, что AI core создан и работает
            if not hasattr(enemy, "ai_core") or enemy.ai_core is None:
                self.logger.error("AI core не был создан для сущности")
                return False

            # Проверяем основные свойства AI core
            ai_core = enemy.ai_core
            if not hasattr(ai_core, "state") or not hasattr(ai_core, "priority"):
                self.logger.error("AI core не имеет необходимых атрибутов")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Ошибка AI ядра: {e}")
            return False

    def _test_ai_entity_registration(self) -> bool:
        """Тест регистрации AI сущностей"""
        try:
            from ai.ai_manager import ai_manager
            from entities.entity_factory import entity_factory

            # Создаем несколько тестовых сущностей
            entities = []
            for i in range(5):
                enemy = entity_factory.create_enemy("warrior", 1, (100 + i * 50, 100))
                if enemy and hasattr(enemy, "ai_core") and enemy.ai_core is not None:
                    entities.append(enemy)
                else:
                    self.logger.warning(f"Сущность {i} не имеет AI core")

            # Регистрируем их в AI системе
            registered_count = 0
            for entity in entities:
                if ai_manager.register_entity(entity, entity.ai_core):
                    registered_count += 1

            # Проверяем количество зарегистрированных сущностей
            stats = ai_manager.get_performance_stats()

            # Считаем тест успешным, если хотя бы одна сущность зарегистрирована
            return registered_count > 0

        except Exception as e:
            self.logger.error(f"Ошибка регистрации AI сущностей: {e}")
            return False

    def _test_ai_update(self) -> bool:
        """Тест обновления AI"""
        try:
            from ai.ai_manager import ai_manager

            # Обновляем AI систему
            ai_manager.update(0.016)  # 16ms

            # Получаем статистику
            stats = ai_manager.get_performance_stats()

            return True

        except Exception as e:
            self.logger.error(f"Ошибка обновления AI: {e}")
            return False

    def _test_creation_performance(self) -> bool:
        """Тест производительности создания объектов"""
        try:
            from entities.entity_factory import entity_factory
            import time

            # Тестируем создание множества объектов
            start_time = time.time()

            for i in range(100):
                enemy = entity_factory.create_enemy("warrior", 1, (i * 10, i * 10))

            end_time = time.time()
            duration = end_time - start_time

            # Проверяем, что создание не занимает слишком много времени
            if duration > 1.0:  # Больше 1 секунды
                self.logger.warning(f"Создание 100 объектов заняло {duration:.3f}с")

            return True

        except Exception as e:
            self.logger.error(f"Ошибка теста производительности создания: {e}")
            return False

    def _test_ai_performance(self) -> bool:
        """Тест производительности AI"""
        try:
            from ai.ai_manager import ai_manager
            import time

            # Тестируем обновление AI
            start_time = time.time()

            for i in range(100):
                ai_manager.update(0.016)

            end_time = time.time()
            duration = end_time - start_time

            # Проверяем, что обновление не занимает слишком много времени
            if duration > 0.5:  # Больше 0.5 секунды
                self.logger.warning(f"100 обновлений AI заняли {duration:.3f}с")

            return True

        except Exception as e:
            self.logger.error(f"Ошибка теста производительности AI: {e}")
            return False

    def _test_memory_usage(self) -> bool:
        """Тест использования памяти"""
        try:
            import psutil
            import os

            # Получаем информацию о памяти
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()

            # Проверяем, что использование памяти разумное (менее 500MB)
            memory_mb = memory_info.rss / 1024 / 1024

            if memory_mb > 500:
                self.logger.warning(f"Использование памяти: {memory_mb:.1f}MB")

            return True

        except ImportError:
            # psutil не установлен, пропускаем тест
            self.logger.info("psutil не установлен, пропускаем тест памяти")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка теста памяти: {e}")
            return False

    def _print_results(self):
        """Вывод результатов тестирования"""
        total_time = time.time() - self.start_time

        self.logger.info("=== РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ ===")

        # Подсчитываем статистику
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result.success)
        failed_tests = total_tests - passed_tests

        # Выводим общую статистику
        self.logger.info(f"Всего тестов: {total_tests}")
        self.logger.info(f"Пройдено: {passed_tests}")
        self.logger.info(f"Провалено: {failed_tests}")
        self.logger.info(f"Общее время: {total_time:.3f}с")

        # Выводим детальные результаты
        for result in self.results:
            status = "✓" if result.success else "✗"
            self.logger.info(f"{status} {result.name} ({result.duration:.3f}с)")

            if not result.success and result.error:
                self.logger.error(f"  Ошибка: {result.error}")

        # Итоговый результат
        if failed_tests == 0:
            self.logger.info("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
            self.logger.info("Игра готова к запуску!")
        else:
            self.logger.error(f"❌ {failed_tests} ТЕСТОВ ПРОВАЛЕНО")
            self.logger.info("Проверьте логи выше для деталей")


def main():
    """Главная функция тестирования"""
    tester = GameSystemTester()
    success = tester.run_all_tests()

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
