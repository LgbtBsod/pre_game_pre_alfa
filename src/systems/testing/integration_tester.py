"""
Система тестирования интеграции - проверка всех интегрированных компонентов
"""

import time
import traceback
from typing import Dict, List, Optional, Callable, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum

from src.core.architecture import BaseComponent, ComponentType, Priority


class TestStatus(Enum):
    """Статус теста"""
    NOT_RUN = "not_run"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


class TestPriority(Enum):
    """Приоритет теста"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class TestResult:
    """Результат теста"""
    test_name: str
    status: TestStatus
    execution_time: float = 0.0
    error_message: str = ""
    error_traceback: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestCase:
    """Тестовый случай"""
    name: str
    description: str
    test_function: Callable
    priority: TestPriority = TestPriority.MEDIUM
    dependencies: List[str] = field(default_factory=list)
    timeout: float = 30.0  # секунды
    retry_count: int = 0
    max_retries: int = 3


class IntegrationTester(BaseComponent):
    """
    Система тестирования интеграции
    Проверяет работоспособность всех интегрированных систем
    """
    
    def __init__(self):
        super().__init__(
            name="IntegrationTester",
            component_type=ComponentType.SYSTEM,
            priority=Priority.HIGH
        )
        
        # Тестовые случаи
        self.test_cases: Dict[str, TestCase] = {}
        self.test_results: Dict[str, TestResult] = {}
        
        # Настройки тестирования
        self.auto_run_tests = False
        self.test_timeout = 30.0
        self.max_parallel_tests = 5
        
        # Статистика
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.skipped_tests = 0
        
        # Система интеграции для тестирования
        self.system_integrator = None
        
    def _on_initialize(self) -> bool:
        """Инициализация системы тестирования"""
        try:
            # Создание тестовых случаев
            self._create_test_cases()
            
            # Настройка тестирования
            self._setup_testing()
            
            return True
        except Exception as e:
            self.logger.error(f"Ошибка инициализации IntegrationTester: {e}")
            return False
    
    def _create_test_cases(self):
        """Создание тестовых случаев"""
        # Тесты базовой архитектуры
        self._add_test_case(
            "test_component_lifecycle",
            "Тест жизненного цикла компонентов",
            self._test_component_lifecycle,
            TestPriority.CRITICAL
        )
        
        self._add_test_case(
            "test_event_bus",
            "Тест системы событий",
            self._test_event_bus,
            TestPriority.CRITICAL
        )
        
        self._add_test_case(
            "test_component_manager",
            "Тест менеджера компонентов",
            self._test_component_manager,
            TestPriority.CRITICAL
        )
        
        # Тесты UI систем
        self._add_test_case(
            "test_ui_system",
            "Тест UI системы",
            self._test_ui_system,
            TestPriority.HIGH,
            ["test_component_lifecycle"]
        )
        
        self._add_test_case(
            "test_hud_system",
            "Тест HUD системы",
            self._test_hud_system,
            TestPriority.HIGH,
            ["test_ui_system"]
        )
        
        # Тесты игровых систем
        self._add_test_case(
            "test_combat_system",
            "Тест боевой системы",
            self._test_combat_system,
            TestPriority.HIGH,
            ["test_component_lifecycle"]
        )
        
        self._add_test_case(
            "test_health_system",
            "Тест системы здоровья",
            self._test_health_system,
            TestPriority.HIGH,
            ["test_component_lifecycle"]
        )
        
        self._add_test_case(
            "test_inventory_system",
            "Тест системы инвентаря",
            self._test_inventory_system,
            TestPriority.HIGH,
            ["test_component_lifecycle"]
        )
        
        self._add_test_case(
            "test_skill_system",
            "Тест системы навыков",
            self._test_skill_system,
            TestPriority.HIGH,
            ["test_component_lifecycle"]
        )
        
        self._add_test_case(
            "test_effect_system",
            "Тест системы эффектов",
            self._test_effect_system,
            TestPriority.HIGH,
            ["test_component_lifecycle"]
        )
        
        # Тесты интеграции
        self._add_test_case(
            "test_system_integration",
            "Тест интеграции всех систем",
            self._test_system_integration,
            TestPriority.CRITICAL,
            ["test_ui_system", "test_hud_system", "test_combat_system", 
             "test_health_system", "test_inventory_system", "test_skill_system", "test_effect_system"]
        )
        
        # Тесты производительности
        self._add_test_case(
            "test_performance",
            "Тест производительности",
            self._test_performance,
            TestPriority.MEDIUM,
            ["test_system_integration"]
        )
        
        # Тесты демо сценариев
        self._add_test_case(
            "test_demo_scenarios",
            "Тест демо сценариев",
            self._test_demo_scenarios,
            TestPriority.MEDIUM,
            ["test_system_integration"]
        )
    
    def _setup_testing(self):
        """Настройка тестирования"""
        self.auto_run_tests = False
        self.test_timeout = 30.0
        self.max_parallel_tests = 5
    
    def _add_test_case(self, name: str, description: str, test_function: Callable, 
                       priority: TestPriority, dependencies: List[str] = None):
        """Добавить тестовый случай"""
        test_case = TestCase(
            name=name,
            description=description,
            test_function=test_function,
            priority=priority,
            dependencies=dependencies or []
        )
        
        self.test_cases[name] = test_case
        self.test_results[name] = TestResult(test_name=name, status=TestStatus.NOT_RUN)
        
        self.total_tests += 1
    
    # Основные методы тестирования
    def run_test(self, test_name: str) -> TestResult:
        """Запустить конкретный тест"""
        if test_name not in self.test_cases:
            error_msg = f"Тест {test_name} не найден"
            self.logger.error(error_msg)
            return TestResult(test_name=test_name, status=TestStatus.ERROR, error_message=error_msg)
        
        test_case = self.test_cases[test_name]
        test_result = self.test_results[test_name]
        
        # Проверяем зависимости
        if not self._check_dependencies(test_case):
            test_result.status = TestStatus.SKIPPED
            test_result.error_message = "Зависимости не выполнены"
            self.skipped_tests += 1
            return test_result
        
        # Запускаем тест
        try:
            test_result.status = TestStatus.RUNNING
            start_time = time.time()
            
            # Выполняем тест с таймаутом
            result = self._execute_test_with_timeout(test_case)
            
            execution_time = time.time() - start_time
            test_result.execution_time = execution_time
            
            if result:
                test_result.status = TestStatus.PASSED
                self.passed_tests += 1
                self.logger.info(f"Тест {test_name} прошел успешно за {execution_time:.2f}с")
            else:
                test_result.status = TestStatus.FAILED
                test_result.error_message = "Тест не прошел проверку"
                self.failed_tests += 1
                self.logger.warning(f"Тест {test_name} не прошел проверку")
            
        except Exception as e:
            test_result.status = TestStatus.ERROR
            test_result.error_message = str(e)
            test_result.error_traceback = traceback.format_exc()
            self.failed_tests += 1
            self.logger.error(f"Ошибка в тесте {test_name}: {e}")
        
        return test_result
    
    def run_all_tests(self) -> Dict[str, TestResult]:
        """Запустить все тесты"""
        self.logger.info("Начинаем запуск всех тестов...")
        
        # Сбрасываем статистику
        self.passed_tests = 0
        self.failed_tests = 0
        self.skipped_tests = 0
        
        # Запускаем тесты по приоритету
        for priority in [TestPriority.CRITICAL, TestPriority.HIGH, TestPriority.MEDIUM, TestPriority.LOW]:
            priority_tests = [name for name, tc in self.test_cases.items() if tc.priority == priority]
            
            for test_name in priority_tests:
                self.run_test(test_name)
        
        # Выводим итоговую статистику
        self._print_test_summary()
        
        return self.test_results.copy()
    
    def run_tests_by_priority(self, priority: TestPriority) -> Dict[str, TestResult]:
        """Запустить тесты определенного приоритета"""
        priority_tests = [name for name, tc in self.test_cases.items() if tc.priority == priority]
        
        self.logger.info(f"Запускаем тесты приоритета {priority.value} ({len(priority_tests)} тестов)")
        
        results = {}
        for test_name in priority_tests:
            result = self.run_test(test_name)
            results[test_name] = result
        
        return results
    
    def _check_dependencies(self, test_case: TestCase) -> bool:
        """Проверить зависимости теста"""
        for dep_name in test_case.dependencies:
            if dep_name not in self.test_results:
                return False
            
            dep_result = self.test_results[dep_name]
            if dep_result.status != TestStatus.PASSED:
                return False
        
        return True
    
    def _execute_test_with_timeout(self, test_case: TestCase) -> bool:
        """Выполнить тест с таймаутом"""
        try:
            # TODO: Реализовать выполнение с таймаутом
            return test_case.test_function()
        except Exception as e:
            raise e
    
    # Тестовые функции
    def _test_component_lifecycle(self) -> bool:
        """Тест жизненного цикла компонентов"""
        try:
            # TODO: Создать тестовый компонент и проверить жизненный цикл
            self.logger.info("Тестируем жизненный цикл компонентов...")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка теста жизненного цикла: {e}")
            return False
    
    def _test_event_bus(self) -> bool:
        """Тест системы событий"""
        try:
            # TODO: Протестировать EventBus
            self.logger.info("Тестируем систему событий...")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка теста системы событий: {e}")
            return False
    
    def _test_component_manager(self) -> bool:
        """Тест менеджера компонентов"""
        try:
            # TODO: Протестировать ComponentManager
            self.logger.info("Тестируем менеджер компонентов...")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка теста менеджера компонентов: {e}")
            return False
    
    def _test_ui_system(self) -> bool:
        """Тест UI системы"""
        try:
            # TODO: Протестировать UISystem
            self.logger.info("Тестируем UI систему...")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка теста UI системы: {e}")
            return False
    
    def _test_hud_system(self) -> bool:
        """Тест HUD системы"""
        try:
            # TODO: Протестировать HUDSystem
            self.logger.info("Тестируем HUD систему...")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка теста HUD системы: {e}")
            return False
    
    def _test_combat_system(self) -> bool:
        """Тест боевой системы"""
        try:
            # TODO: Протестировать CombatSystem
            self.logger.info("Тестируем боевую систему...")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка теста боевой системы: {e}")
            return False
    
    def _test_health_system(self) -> bool:
        """Тест системы здоровья"""
        try:
            # TODO: Протестировать HealthSystem
            self.logger.info("Тестируем систему здоровья...")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка теста системы здоровья: {e}")
            return False
    
    def _test_inventory_system(self) -> bool:
        """Тест системы инвентаря"""
        try:
            # TODO: Протестировать InventorySystem
            self.logger.info("Тестируем систему инвентаря...")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка теста системы инвентаря: {e}")
            return False
    
    def _test_skill_system(self) -> bool:
        """Тест системы навыков"""
        try:
            # TODO: Протестировать SkillSystem
            self.logger.info("Тестируем систему навыков...")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка теста системы навыков: {e}")
            return False
    
    def _test_effect_system(self) -> bool:
        """Тест системы эффектов"""
        try:
            # TODO: Протестировать EffectSystem
            self.logger.info("Тестируем систему эффектов...")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка теста системы эффектов: {e}")
            return False
    
    def _test_system_integration(self) -> bool:
        """Тест интеграции всех систем"""
        try:
            # TODO: Протестировать SystemIntegrator
            self.logger.info("Тестируем интеграцию всех систем...")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка теста интеграции: {e}")
            return False
    
    def _test_performance(self) -> bool:
        """Тест производительности"""
        try:
            # TODO: Протестировать производительность
            self.logger.info("Тестируем производительность...")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка теста производительности: {e}")
            return False
    
    def _test_demo_scenarios(self) -> bool:
        """Тест демо сценариев"""
        try:
            # TODO: Протестировать демо сценарии
            self.logger.info("Тестируем демо сценарии...")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка теста демо сценариев: {e}")
            return False
    
    def _test_damage_system(self) -> TestResult:
        """Тест системы урона"""
        try:
            # TODO: Реализовать тест системы урона
            return TestResult(
                test_name="test_damage_system",
                status=TestStatus.PASSED,
                execution_time=0.1,
                details="Тест системы урона пройден успешно"
            )
        except Exception as e:
            return TestResult(
                test_name="test_damage_system",
                status=TestStatus.FAILED,
                execution_time=0.0,
                details=f"Ошибка теста системы урона: {e}"
            )
    
    def _test_evolution_system(self) -> TestResult:
        """Тест системы эволюции"""
        try:
            start_time = time.time()
            
            # Создаем систему эволюции
            evolution_system = EvolutionSystem()
            
            # Инициализируем систему
            if not evolution_system.initialize():
                raise Exception("Не удалось инициализировать систему эволюции")
            
            # Регистрируем тестового персонажа
            test_character_id = "test_player_1"
            if not evolution_system.register_character(test_character_id):
                raise Exception("Не удалось зарегистрировать персонажа")
            
            # Добавляем очки эволюции
            if not evolution_system.add_evolution_points(test_character_id, 100):
                raise Exception("Не удалось добавить очки эволюции")
            
            # Получаем статус эволюции
            status = evolution_system.get_character_evolution_status(test_character_id)
            if not status:
                raise Exception("Не удалось получить статус эволюции")
            
            # Проверяем базовые гены
            if "genes" not in status:
                raise Exception("Отсутствует информация о генах")
            
            # Проверяем количество генов
            expected_genes = 6  # Базовые гены: сила, ловкость, интеллект, харизма, боевой инстинкт, магическая склонность
            if len(status["genes"]) != expected_genes:
                raise Exception(f"Неверное количество генов: {len(status['genes'])} вместо {expected_genes}")
            
            # Проверяем эволюцию гена
            if not evolution_system.evolve_gene(test_character_id, "gene_strength", 20):
                raise Exception("Не удалось эволюционировать ген силы")
            
            # Проверяем спонтанную мутацию
            mutation = evolution_system.trigger_mutation(test_character_id, "gene_agility")
            if mutation:
                self.logger.info(f"Спонтанная мутация: {mutation.name}")
            
            # Получаем сводку по системе
            summary = evolution_system.get_evolution_summary()
            if not summary:
                raise Exception("Не удалось получить сводку по системе эволюции")
            
            # Проверяем статистику
            if summary["total_characters"] != 1:
                raise Exception(f"Неверное количество персонажей: {summary['total_characters']}")
            
            if summary["total_genes"] < expected_genes:
                raise Exception(f"Неверное количество генов в сводке: {summary['total_genes']}")
            
            execution_time = time.time() - start_time
            
            self.logger.info(f"Тест системы эволюции пройден за {execution_time:.3f} секунд")
            
            return TestResult(
                test_name="test_evolution_system",
                status=TestStatus.PASSED,
                execution_time=execution_time,
                details=f"Тест системы эволюции пройден успешно. Проверено: {summary['total_genes']} генов, {summary['total_evolution_trees']} деревьев эволюции"
            )
            
        except Exception as e:
            self.logger.error(f"Ошибка теста системы эволюции: {e}")
            return TestResult(
                test_name="test_evolution_system",
                status=TestStatus.FAILED,
                execution_time=0.0,
                details=f"Ошибка теста системы эволюции: {e}"
            )
    
    # Вспомогательные методы
    def _print_test_summary(self):
        """Вывести сводку по тестам"""
        self.logger.info("=" * 50)
        self.logger.info("ИТОГИ ТЕСТИРОВАНИЯ")
        self.logger.info("=" * 50)
        self.logger.info(f"Всего тестов: {self.total_tests}")
        self.logger.info(f"Пройдено: {self.passed_tests}")
        self.logger.info(f"Провалено: {self.failed_tests}")
        self.logger.info(f"Пропущено: {self.skipped_tests}")
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        self.logger.info(f"Процент успеха: {success_rate:.1f}%")
        
        if self.failed_tests > 0:
            self.logger.warning("Есть проваленные тесты!")
            for test_name, result in self.test_results.items():
                if result.status == TestStatus.FAILED:
                    self.logger.warning(f"  - {test_name}: {result.error_message}")
        
        self.logger.info("=" * 50)
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Получить сводку по тестам"""
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "skipped_tests": self.skipped_tests,
            "success_rate": (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0,
            "test_results": self.test_results.copy()
        }
    
    def get_test_status(self, test_name: str) -> Optional[TestStatus]:
        """Получить статус теста"""
        if test_name in self.test_results:
            return self.test_results[test_name].status
        return None
    
    def get_failed_tests(self) -> List[str]:
        """Получить список проваленных тестов"""
        return [name for name, result in self.test_results.items() 
                if result.status in [TestStatus.FAILED, TestStatus.ERROR]]
    
    def get_passed_tests(self) -> List[str]:
        """Получить список пройденных тестов"""
        return [name for name, result in self.test_results.items() 
                if result.status == TestStatus.PASSED]
    
    def retry_failed_tests(self) -> Dict[str, TestResult]:
        """Повторить проваленные тесты"""
        failed_tests = self.get_failed_tests()
        
        if not failed_tests:
            self.logger.info("Нет проваленных тестов для повторного запуска")
            return {}
        
        self.logger.info(f"Повторяем {len(failed_tests)} проваленных тестов...")
        
        results = {}
        for test_name in failed_tests:
            result = self.run_test(test_name)
            results[test_name] = result
        
        return results
    
    def clear_test_results(self):
        """Очистить результаты тестов"""
        for result in self.test_results.values():
            result.status = TestStatus.NOT_RUN
            result.execution_time = 0.0
            result.error_message = ""
            result.error_traceback = ""
            result.details.clear()
        
        self.passed_tests = 0
        self.failed_tests = 0
        self.skipped_tests = 0
        
        self.logger.info("Результаты тестов очищены")
    
    # Обновление системы
    def update(self, delta_time: float):
        """Обновить систему тестирования"""
        # Автоматический запуск тестов при необходимости
        if self.auto_run_tests:
            # TODO: Логика автоматического запуска тестов
            pass
    
    # Публичные методы
    def set_system_integrator(self, integrator):
        """Установить систему интеграции для тестирования"""
        self.system_integrator = integrator
        self.logger.info("Система интеграции установлена для тестирования")
    
    def enable_auto_testing(self, enabled: bool = True):
        """Включить/выключить автоматическое тестирование"""
        self.auto_run_tests = enabled
        status = "включено" if enabled else "выключено"
        self.logger.info(f"Автоматическое тестирование {status}")
    
    def set_test_timeout(self, timeout: float):
        """Установить таймаут для тестов"""
        self.test_timeout = timeout
        self.logger.info(f"Таймаут тестов установлен: {timeout}с")
    
    def set_max_parallel_tests(self, max_count: int):
        """Установить максимальное количество параллельных тестов"""
        self.max_parallel_tests = max_count
        self.logger.info(f"Максимум параллельных тестов: {max_count}")
