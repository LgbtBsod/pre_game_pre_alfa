"""
Демо-версия AI-EVOLVE: Эволюционная Адаптация
Презентация всех игровых механик и систем
"""

import sys
import os
import time
import threading
from typing import Dict, List, Optional, Any

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.systems.integration.system_integrator import SystemIntegrator, DemoScenario
from src.systems.ui.ui_system import UISystem
from src.systems.ui.hud_system import HUDSystem
from src.systems.combat.combat_system import CombatSystem
from src.systems.health.health_system import HealthSystem
from src.systems.inventory.inventory_system import InventorySystem
from src.systems.skills.skill_system import SkillSystem
from src.systems.effects.effect_system import EffectSystem
from src.core.architecture import ComponentManager, EventBus, StateManager
from src.core.game_engine import GameEngine


class DemoLauncher:
    """
    Основной класс для запуска демо-версии
    """
    
    def __init__(self):
        self.system_integrator = SystemIntegrator()
        self.component_manager = ComponentManager()
        self.event_bus = EventBus()
        self.state_manager = StateManager()
        self.game_engine = None
        
        # Игровые системы
        self.ui_system = None
        self.hud_system = None
        self.combat_system = None
        self.health_system = None
        self.inventory_system = None
        self.skill_system = None
        self.effect_system = None
        
        # Демо состояние
        self.current_scenario = None
        self.is_running = False
        self.demo_thread = None
        
    def initialize_demo(self) -> bool:
        """Инициализация демо-версии"""
        try:
            print("🎮 Инициализация демо-версии AI-EVOLVE...")
            print("=" * 60)
            
            # Инициализируем базовые компоненты
            self.component_manager.initialize()
            self.event_bus.initialize()
            self.state_manager.initialize()
            
            # Создаем игровой движок
            self.game_engine = GameEngine()
            self.game_engine.initialize()
            
            # Создаем и инициализируем игровые системы
            self._create_game_systems()
            
            # Регистрируем все системы в интеграторе
            self._register_systems()
            
            # Интегрируем все системы
            self._integrate_all_systems()
            
            print("✅ Демо-версия инициализирована успешно!")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка инициализации демо-версии: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _create_game_systems(self):
        """Создание игровых систем"""
        try:
            print("🔧 Создание игровых систем...")
            
            # UI система
            self.ui_system = UISystem()
            self.ui_system.initialize()
            print("   ✅ UISystem создана")
            
            # HUD система
            self.hud_system = HUDSystem()
            self.hud_system.initialize()
            print("   ✅ HUDSystem создана")
            
            # Боевая система
            self.combat_system = CombatSystem()
            self.combat_system.initialize()
            print("   ✅ CombatSystem создана")
            
            # Система здоровья
            self.health_system = HealthSystem()
            self.health_system.initialize()
            print("   ✅ HealthSystem создана")
            
            # Система инвентаря
            self.inventory_system = InventorySystem()
            self.inventory_system.initialize()
            print("   ✅ InventorySystem создана")
            
            # Система навыков
            self.skill_system = SkillSystem()
            self.skill_system.initialize()
            print("   ✅ SkillSystem создана")
            
            # Система эффектов
            self.effect_system = EffectSystem()
            self.effect_system.initialize()
            print("   ✅ EffectSystem создана")
            
        except Exception as e:
            print(f"❌ Ошибка создания игровых систем: {e}")
            raise
    
    def _register_systems(self):
        """Регистрация всех систем в интеграторе"""
        try:
            print("📝 Регистрация систем в интеграторе...")
            
            # Регистрируем базовые системы
            self.system_integrator.register_system("ComponentManager", self.component_manager)
            self.system_integrator.register_system("EventBus", self.event_bus)
            self.system_integrator.register_system("StateManager", self.state_manager)
            self.system_integrator.register_system("GameEngine", self.game_engine)
            
            # Регистрируем игровые системы
            self.system_integrator.register_system("UISystem", self.ui_system)
            self.system_integrator.register_system("HUDSystem", self.hud_system)
            self.system_integrator.register_system("CombatSystem", self.combat_system)
            self.system_integrator.register_system("HealthSystem", self.health_system)
            self.system_integrator.register_system("InventorySystem", self.inventory_system)
            self.system_integrator.register_system("SkillSystem", self.skill_system)
            self.system_integrator.register_system("EffectSystem", self.effect_system)
            
            print(f"   ✅ Зарегистрировано {len(self.system_integrator.get_registered_systems())} систем")
            
        except Exception as e:
            print(f"❌ Ошибка регистрации систем: {e}")
            raise
    
    def _integrate_all_systems(self):
        """Интеграция всех систем"""
        try:
            print("🔗 Интеграция всех систем...")
            
            # Интегрируем все системы
            success = self.system_integrator.integrate_all_systems()
            
            if success:
                print("   ✅ Все системы успешно интегрированы")
            else:
                print("   ⚠️ Некоторые системы не удалось интегрировать")
            
            # Получаем статус интеграции
            status = self.system_integrator.get_integration_summary()
            print(f"   📊 Статус интеграции: {status['integrated_systems']}/{status['total_systems']} систем")
            
        except Exception as e:
            print(f"❌ Ошибка интеграции систем: {e}")
            raise
    
    def show_demo_menu(self):
        """Показать меню демо-версии"""
        print("\n🎮 ДЕМО-ВЕРСИЯ AI-EVOLVE: ЭВОЛЮЦИОННАЯ АДАПТАЦИЯ")
        print("=" * 60)
        print("Доступные демо сценарии:")
        
        scenarios = self.system_integrator.list_demo_scenarios()
        for i, scenario in enumerate(scenarios, 1):
            print(f"   {i}. {scenario.name}")
            print(f"      {scenario.description}")
            print(f"      Системы: {', '.join(scenario.systems_required)}")
            print()
        
        print("Команды:")
        print("   <номер> - запустить сценарий")
        print("   all - запустить все сценарии")
        print("   status - показать статус интеграции")
        print("   quit - выход")
        print("=" * 60)
    
    def run_demo_scenario(self, scenario_id: str) -> bool:
        """Запуск демо сценария"""
        try:
            if not self.system_integrator.is_system_integrated("UISystem"):
                print("❌ UI система не интегрирована")
                return False
            
            print(f"\n🎬 Запуск демо сценария: {scenario_id}")
            
            # Запускаем сценарий
            success = self.system_integrator.start_demo_scenario(scenario_id)
            
            if success:
                self.current_scenario = scenario_id
                print("✅ Сценарий запущен успешно!")
                
                # Запускаем демо в отдельном потоке
                self.is_running = True
                self.demo_thread = threading.Thread(target=self._run_demo_loop, args=(scenario_id,))
                self.demo_thread.daemon = True
                self.demo_thread.start()
                
                return True
            else:
                print("❌ Не удалось запустить сценарий")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка запуска сценария: {e}")
            return False
    
    def _run_demo_loop(self, scenario_id: str):
        """Основной цикл демо"""
        try:
            print(f"🔄 Демо сценарий {scenario_id} запущен...")
            
            # Имитируем работу демо
            for i in range(10):  # 10 секунд демо
                if not self.is_running:
                    break
                
                # Обновляем системы
                self._update_demo_systems()
                
                # Показываем прогресс
                progress = (i + 1) * 10
                print(f"   📊 Прогресс: {progress}%")
                
                time.sleep(1)
            
            # Останавливаем демо
            self.stop_demo()
            
        except Exception as e:
            print(f"❌ Ошибка в демо цикле: {e}")
            self.stop_demo()
    
    def _update_demo_systems(self):
        """Обновление демо систем"""
        try:
            # Обновляем UI
            if self.ui_system:
                self.ui_system.update(1.0)
            
            # Обновляем HUD
            if self.hud_system:
                self.hud_system.update(1.0)
            
            # Обновляем другие системы
            if self.combat_system:
                self.combat_system.update(1.0)
            
            if self.health_system:
                self.health_system.update(1.0)
            
            if self.inventory_system:
                self.inventory_system.update(1.0)
            
            if self.skill_system:
                self.skill_system.update(1.0)
            
            if self.effect_system:
                self.effect_system.update(1.0)
                
        except Exception as e:
            print(f"⚠️ Ошибка обновления систем: {e}")
    
    def stop_demo(self):
        """Остановка демо"""
        try:
            if self.current_scenario:
                self.system_integrator.stop_demo_scenario()
                self.current_scenario = None
            
            self.is_running = False
            
            if self.demo_thread and self.demo_thread.is_alive():
                self.demo_thread.join(timeout=1.0)
            
            print("✅ Демо остановлено")
            
        except Exception as e:
            print(f"❌ Ошибка остановки демо: {e}")
    
    def show_integration_status(self):
        """Показать статус интеграции"""
        try:
            print("\n📊 СТАТУС ИНТЕГРАЦИИ СИСТЕМ")
            print("=" * 60)
            
            status = self.system_integrator.get_integration_summary()
            
            print(f"Всего систем: {status['total_systems']}")
            print(f"Интегрировано: {status['integrated_systems']}")
            print(f"Ошибок: {status['error_systems']}")
            print(f"Процент интеграции: {status['integration_percentage']:.1f}%")
            
            if status['active_scenario']:
                print(f"Активный сценарий: {status['active_scenario']}")
            
            print(f"Доступно сценариев: {status['available_scenarios']}")
            
            # Детальный статус каждой системы
            print("\nДетальный статус:")
            system_status = self.system_integrator.get_integration_status()
            
            for system_name, info in system_status.items():
                status_icon = "✅" if info.status.value == "fully_integrated" else "❌" if info.status.value == "error" else "⚠️"
                print(f"   {status_icon} {system_name}: {info.status.value}")
                if info.error_message:
                    print(f"      Ошибка: {info.error_message}")
            
        except Exception as e:
            print(f"❌ Ошибка получения статуса: {e}")
    
    def run_all_scenarios(self):
        """Запуск всех демо сценариев"""
        try:
            print("\n🚀 Запуск всех демо сценариев...")
            
            scenarios = self.system_integrator.list_demo_scenarios()
            
            for scenario in scenarios:
                print(f"\n🎬 Запуск: {scenario.name}")
                
                # Запускаем сценарий
                success = self.run_demo_scenario(scenario.scenario_id)
                
                if success:
                    # Ждем завершения
                    while self.is_running:
                        time.sleep(0.5)
                    
                    print(f"✅ {scenario.name} завершен")
                else:
                    print(f"❌ {scenario.name} не удалось запустить")
                
                time.sleep(1)  # Пауза между сценариями
            
            print("\n🎉 Все демо сценарии завершены!")
            
        except Exception as e:
            print(f"❌ Ошибка запуска всех сценариев: {e}")
    
    def run_interactive_demo(self):
        """Интерактивный режим демо"""
        try:
            print("🎮 Запуск интерактивного демо...")
            
            while True:
                self.show_demo_menu()
                
                command = input("\nВведите команду: ").strip().lower()
                
                if command == "quit":
                    break
                elif command == "status":
                    self.show_integration_status()
                elif command == "all":
                    self.run_all_scenarios()
                elif command.isdigit():
                    # Запуск конкретного сценария
                    scenarios = self.system_integrator.list_demo_scenarios()
                    index = int(command) - 1
                    
                    if 0 <= index < len(scenarios):
                        scenario = scenarios[index]
                        self.run_demo_scenario(scenario.scenario_id)
                        
                        # Ждем завершения
                        while self.is_running:
                            time.sleep(0.5)
                    else:
                        print("❌ Неверный номер сценария")
                else:
                    print("❌ Неизвестная команда")
                
                print()
            
        except KeyboardInterrupt:
            print("\n\n⚠️ Демо прервано пользователем")
        except Exception as e:
            print(f"❌ Ошибка интерактивного демо: {e}")
        finally:
            self.stop_demo()
    
    def cleanup(self):
        """Очистка ресурсов"""
        try:
            print("\n🧹 Очистка ресурсов демо...")
            
            # Останавливаем демо
            self.stop_demo()
            
            # Очищаем системы
            if self.effect_system:
                self.effect_system.shutdown()
            if self.skill_system:
                self.skill_system.shutdown()
            if self.inventory_system:
                self.inventory_system.shutdown()
            if self.health_system:
                self.health_system.shutdown()
            if self.combat_system:
                self.combat_system.shutdown()
            if self.hud_system:
                self.hud_system.shutdown()
            if self.ui_system:
                self.ui_system.shutdown()
            
            # Очищаем базовые компоненты
            if self.game_engine:
                self.game_engine.shutdown()
            if self.state_manager:
                self.state_manager.shutdown()
            if self.event_bus:
                self.event_bus.shutdown()
            if self.component_manager:
                self.component_manager.shutdown()
            
            print("✅ Ресурсы демо очищены")
            
        except Exception as e:
            print(f"❌ Ошибка очистки ресурсов демо: {e}")


def main():
    """Основная функция запуска демо"""
    print("🎮 AI-EVOLVE: Запуск демо-версии")
    print("=" * 60)
    
    launcher = DemoLauncher()
    
    try:
        # Инициализация демо
        if not launcher.initialize_demo():
            print("❌ Не удалось инициализировать демо-версию")
            return False
        
        # Запуск интерактивного демо
        launcher.run_interactive_demo()
        
        return True
        
    except Exception as e:
        print(f"❌ Критическая ошибка демо: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        launcher.cleanup()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
