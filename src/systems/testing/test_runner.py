"""
Основной скрипт для запуска всех тестов интеграции
"""

import sys
import os
import time
import traceback
from typing import Dict, List, Optional, Any

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.systems.testing.integration_tester import IntegrationTester, TestStatus, TestPriority
from src.systems.integration.system_integrator import SystemIntegrator
from src.core.architecture import ComponentManager, EventBus, StateManager
from src.core.game_engine import GameEngine


class TestRunner:
    """
    Основной класс для запуска всех тестов
    """
    
    def __init__(self):
        self.tester = IntegrationTester()
        self.system_integrator = SystemIntegrator()
        self.component_manager = ComponentManager()
        self.event_bus = EventBus()
        self.state_manager = StateManager()
        self.game_engine = None
        
        # Результаты тестирования
        self.test_results = {}
        self.overall_success = False
        
    def setup_test_environment(self) -> bool:
        """Настройка тестовой среды"""
        try:
            print("🔧 Настройка тестовой среды...")
            
            # Инициализируем базовые компоненты
            self.component_manager.initialize()
            self.event_bus.initialize()
            self.state_manager.initialize()
            
            # Создаем игровой движок
            self.game_engine = GameEngine()
            self.game_engine.initialize()
            
            # Устанавливаем систему интеграции для тестирования
            self.tester.set_system_integrator(self.system_integrator)
            
            # Регистрируем все системы в интеграторе
            self._register_all_systems()
            
            print("✅ Тестовая среда настроена успешно")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка настройки тестовой среды: {e}")
            traceback.print_exc()
            return False
    
    def _register_all_systems(self):
        """Регистрация всех систем в интеграторе"""
        try:
            # Регистрируем базовые системы
            self.system_integrator.register_system("ComponentManager", self.component_manager)
            self.system_integrator.register_system("EventBus", self.event_bus)
            self.system_integrator.register_system("StateManager", self.state_manager)
            self.system_integrator.register_system("GameEngine", self.game_engine)
            
            # Регистрируем игровые системы (если доступны)
            try:
                from src.systems.ui.ui_system import UISystem
                ui_system = UISystem()
                self.system_integrator.register_system("UISystem", ui_system)
            except ImportError:
                print("⚠️ UISystem недоступна для тестирования")
            
            try:
                from src.systems.ui.hud_system import HUDSystem
                hud_system = HUDSystem()
                self.system_integrator.register_system("HUDSystem", hud_system)
            except ImportError:
                print("⚠️ HUDSystem недоступна для тестирования")
            
            try:
                from src.systems.combat.combat_system import CombatSystem
                combat_system = CombatSystem()
                self.system_integrator.register_system("CombatSystem", combat_system)
            except ImportError:
                print("⚠️ CombatSystem недоступна для тестирования")
            
            try:
                from src.systems.health.health_system import HealthSystem
                health_system = HealthSystem()
                self.system_integrator.register_system("HealthSystem", health_system)
            except ImportError:
                print("⚠️ HealthSystem недоступна для тестирования")
            
            try:
                from src.systems.inventory.inventory_system import InventorySystem
                inventory_system = InventorySystem()
                self.system_integrator.register_system("InventorySystem", inventory_system)
            except ImportError:
                print("⚠️ InventorySystem недоступна для тестирования")
            
            try:
                from src.systems.skills.skill_system import SkillSystem
                skill_system = SkillSystem()
                self.system_integrator.register_system("SkillSystem", skill_system)
            except ImportError:
                print("⚠️ SkillSystem недоступна для тестирования")
            
            try:
                from src.systems.effects.effect_system import EffectSystem
                effect_system = EffectSystem()
                self.system_integrator.register_system("EffectSystem", effect_system)
            except ImportError:
                print("⚠️ EffectSystem недоступна для тестирования")
            
            print(f"✅ Зарегистрировано {len(self.system_integrator.get_registered_systems())} систем")
            
        except Exception as e:
            print(f"❌ Ошибка регистрации систем: {e}")
            traceback.print_exc()
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Запуск всех тестов"""
        try:
            print("\n🚀 Запуск всех тестов интеграции...")
            print("=" * 60)
            
            # Запускаем тесты по приоритету
            results = self.tester.run_all_tests()
            
            # Анализируем результаты
            self._analyze_test_results(results)
            
            return results
            
        except Exception as e:
            print(f"❌ Ошибка запуска тестов: {e}")
            traceback.print_exc()
            return {}
    
    def _analyze_test_results(self, results: Dict[str, Any]):
        """Анализ результатов тестирования"""
        try:
            print("\n📊 АНАЛИЗ РЕЗУЛЬТАТОВ ТЕСТИРОВАНИЯ")
            print("=" * 60)
            
            total_tests = len(results)
            passed_tests = sum(1 for r in results.values() if r.status == TestStatus.PASSED)
            failed_tests = sum(1 for r in results.values() if r.status in [TestStatus.FAILED, TestStatus.ERROR])
            skipped_tests = sum(1 for r in results.values() if r.status == TestStatus.SKIPPED)
            
            success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
            
            print(f"📈 Общая статистика:")
            print(f"   Всего тестов: {total_tests}")
            print(f"   Пройдено: {passed_tests}")
            print(f"   Провалено: {failed_tests}")
            print(f"   Пропущено: {skipped_tests}")
            print(f"   Процент успеха: {success_rate:.1f}%")
            
            # Анализ по приоритетам
            self._analyze_by_priority(results)
            
            # Анализ проваленных тестов
            if failed_tests > 0:
                self._analyze_failed_tests(results)
            
            # Определяем общий успех
            self.overall_success = failed_tests == 0 and passed_tests > 0
            
            if self.overall_success:
                print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
            else:
                print(f"\n⚠️ Есть проблемы: {failed_tests} тестов не прошли")
            
        except Exception as e:
            print(f"❌ Ошибка анализа результатов: {e}")
            traceback.print_exc()
    
    def _analyze_by_priority(self, results: Dict[str, Any]):
        """Анализ результатов по приоритетам"""
        try:
            print(f"\n🎯 Анализ по приоритетам:")
            
            for priority in [TestPriority.CRITICAL, TestPriority.HIGH, TestPriority.MEDIUM, TestPriority.LOW]:
                priority_tests = [name for name, result in results.items() 
                                if hasattr(result, 'priority') and result.priority == priority]
                
                if priority_tests:
                    passed = sum(1 for name in priority_tests 
                               if results[name].status == TestStatus.PASSED)
                    total = len(priority_tests)
                    rate = (passed / total * 100) if total > 0 else 0
                    
                    print(f"   {priority.value.upper()}: {passed}/{total} ({rate:.1f}%)")
                    
        except Exception as e:
            print(f"❌ Ошибка анализа по приоритетам: {e}")
    
    def _analyze_failed_tests(self, results: Dict[str, Any]):
        """Анализ проваленных тестов"""
        try:
            print(f"\n❌ Детализация проваленных тестов:")
            
            for test_name, result in results.items():
                if result.status in [TestStatus.FAILED, TestStatus.ERROR]:
                    print(f"   🔴 {test_name}:")
                    print(f"      Статус: {result.status.value}")
                    if result.error_message:
                        print(f"      Ошибка: {result.error_message}")
                    if result.execution_time > 0:
                        print(f"      Время: {result.execution_time:.2f}с")
                    
        except Exception as e:
            print(f"❌ Ошибка анализа проваленных тестов: {e}")
    
    def run_demo_scenarios(self) -> bool:
        """Запуск демо сценариев"""
        try:
            if not self.overall_success:
                print("⚠️ Демо сценарии не могут быть запущены - есть проваленные тесты")
                return False
            
            print("\n🎮 Запуск демо сценариев...")
            print("=" * 60)
            
            # Получаем список доступных сценариев
            scenarios = self.system_integrator.list_demo_scenarios()
            
            if not scenarios:
                print("❌ Нет доступных демо сценариев")
                return False
            
            print(f"📋 Доступно сценариев: {len(scenarios)}")
            
            # Запускаем каждый сценарий
            for scenario in scenarios:
                print(f"\n🎬 Запуск сценария: {scenario.name}")
                print(f"   Описание: {scenario.description}")
                print(f"   Требуемые системы: {', '.join(scenario.systems_required)}")
                
                try:
                    success = self.system_integrator.start_demo_scenario(scenario.scenario_id)
                    if success:
                        print("   ✅ Сценарий запущен успешно")
                        
                        # Имитируем работу сценария
                        time.sleep(2)
                        
                        # Останавливаем сценарий
                        self.system_integrator.stop_demo_scenario()
                        print("   ✅ Сценарий остановлен")
                    else:
                        print("   ❌ Ошибка запуска сценария")
                        
                except Exception as e:
                    print(f"   ❌ Исключение при запуске сценария: {e}")
            
            print("\n🎉 Все демо сценарии протестированы!")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка запуска демо сценариев: {e}")
            traceback.print_exc()
            return False
    
    def cleanup(self):
        """Очистка ресурсов"""
        try:
            print("\n🧹 Очистка ресурсов...")
            
            if self.game_engine:
                self.game_engine.shutdown()
            
            if self.component_manager:
                self.component_manager.shutdown()
            
            if self.event_bus:
                self.event_bus.shutdown()
            
            if self.state_manager:
                self.state_manager.shutdown()
            
            print("✅ Ресурсы очищены")
            
        except Exception as e:
            print(f"❌ Ошибка очистки ресурсов: {e}")
    
    def generate_report(self) -> str:
        """Генерация отчета о тестировании"""
        try:
            report = []
            report.append("📋 ОТЧЕТ О ТЕСТИРОВАНИИ ИНТЕГРАЦИИ")
            report.append("=" * 50)
            report.append(f"Дата: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            report.append(f"Версия: 2.4.0")
            report.append("")
            
            # Общая статистика
            summary = self.tester.get_test_summary()
            report.append("📊 ОБЩАЯ СТАТИСТИКА:")
            report.append(f"   Всего тестов: {summary['total_tests']}")
            report.append(f"   Пройдено: {summary['passed_tests']}")
            report.append(f"   Провалено: {summary['failed_tests']}")
            report.append(f"   Пропущено: {summary['skipped_tests']}")
            report.append(f"   Процент успеха: {summary['success_rate']:.1f}%")
            report.append("")
            
            # Детальные результаты
            report.append("🔍 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
            for test_name, result in summary['test_results'].items():
                status_icon = "✅" if result.status == TestStatus.PASSED else "❌" if result.status in [TestStatus.FAILED, TestStatus.ERROR] else "⚠️"
                report.append(f"   {status_icon} {test_name}: {result.status.value}")
                if result.execution_time > 0:
                    report.append(f"      Время: {result.execution_time:.2f}с")
                if result.error_message:
                    report.append(f"      Ошибка: {result.error_message}")
            
            report.append("")
            report.append("🎯 ЗАКЛЮЧЕНИЕ:")
            if self.overall_success:
                report.append("   Все тесты пройдены успешно!")
                report.append("   Проект готов к демонстрации.")
            else:
                report.append("   Есть проблемы, требующие исправления.")
                report.append("   Демо-версия не может быть запущена.")
            
            return "\n".join(report)
            
        except Exception as e:
            return f"❌ Ошибка генерации отчета: {e}"


def main():
    """Основная функция запуска тестирования"""
    print("🎮 AI-EVOLVE: Запуск тестирования интеграции")
    print("=" * 60)
    
    runner = TestRunner()
    
    try:
        # Настройка тестовой среды
        if not runner.setup_test_environment():
            print("❌ Не удалось настроить тестовую среду")
            return False
        
        # Запуск всех тестов
        results = runner.run_all_tests()
        
        if not results:
            print("❌ Не удалось запустить тесты")
            return False
        
        # Запуск демо сценариев (если все тесты прошли)
        if runner.overall_success:
            runner.run_demo_scenarios()
        
        # Генерация отчета
        report = runner.generate_report()
        print("\n" + report)
        
        # Сохранение отчета в файл
        try:
            with open("test_report.txt", "w", encoding="utf-8") as f:
                f.write(report)
            print("\n💾 Отчет сохранен в файл test_report.txt")
        except Exception as e:
            print(f"⚠️ Не удалось сохранить отчет: {e}")
        
        return runner.overall_success
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        traceback.print_exc()
        return False
        
    finally:
        runner.cleanup()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
