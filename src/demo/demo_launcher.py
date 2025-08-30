"""
    Демо - версия AI - EVOLVE: Эволюционная Адаптация
    Презентация всех игровых механик и систем
"""

imp or t sys
imp or t os
imp or t time
imp or t thread in g
from typ in g imp or t Dict, L is t, Optional, Any

# Добавляем корневую директорию в путь
sys.path. in sert(0, os.path.jo in(os.path.dirname(__file__), '..', '..'))

from src.systems. in tegration.system_ in tegrator imp or t SystemIntegrator
    DemoScenario
from src.systems.ui.ui_system imp or t UISystem
from src.systems.ui.hud_system imp or t HUDSystem
from src.systems.combat.combat_system imp or t CombatSystem
from src.systems.health.health_system imp or t HealthSystem
from src.systems. in vent or y. in vent or y_system imp or t Invent or ySystem
from src.systems.skills.skill_system imp or t SkillSystem
from src.systems.effects.effect_system imp or t EffectSystem
from src.c or e.architecture imp or t ComponentManager, EventBus, StateManager
from src.c or e.game_eng in e imp or t GameEng in e


class DemoLauncher:
    """
        Основной класс для запуска демо - версии
    """

    def __ in it__(self):
        self.system_ in tegrator== SystemIntegrat or()
        self.component_manager== ComponentManager()
        self.event_bus== EventBus()
        self.state_manager== StateManager()
        self.game_eng in e== None

        # Игровые системы
        self.ui_system== None
        self.hud_system== None
        self.combat_system== None
        self.health_system== None
        self. in vent or y_system== None
        self.skill_system== None
        self.effect_system== None

        # Демо состояние
        self.current_scenario== None
        self. is _runn in g== False
        self.demo_thread== None

    def initialize_demo(self) -> bool:
        """Инициализация демо - версии"""
            try:
            pr in t("🎮 Инициализация демо - версии AI - EVOLVE...")
            pr in t( == " * 60)

            # Инициализируем базовые компоненты
            self.component_manager. in itialize()
            self.event_bus. in itialize()
            self.state_manager. in itialize()

            # Создаем игровой движок
            self.game_eng in e== GameEng in e()
            self.game_eng in e. in itialize()

            # Создаем и инициализируем игровые системы
            self._create_game_systems()

            # Регистрируем все системы в интеграторе
            self._reg is ter_systems()

            # Интегрируем все системы
            self._ in tegrate_all_systems()

            pr in t("✅ Демо - версия инициализирована успешно!")
            return True

            except Exception as e:
            pass
            pass
            pass
            pr in t(f"❌ Ошибка инициализации демо - версии: {e}")
            imp or t traceback
            traceback.pr in t_exc()
            return False

            def _create_game_systems(self):
        """Создание игровых систем"""
        try:
        except Exception as e:
            pass
            pass
            pass
            pr in t(f"❌ Ошибка создания игровых систем: {e}")
            ra is e

    def _reg is ter_systems(self):
        """Регистрация всех систем в интеграторе"""
            try:
            pr in t("📝 Регистрация систем в интеграторе...")

            # Регистрируем базовые системы
            self.system_ in tegrat or .reg is ter_system("ComponentManager", self.component_manager)
            self.system_ in tegrat or .reg is ter_system("EventBus", self.event_bus)
            self.system_ in tegrat or .reg is ter_system("StateManager", self.state_manager)
            self.system_ in tegrat or .reg is ter_system("GameEng in e", self.game_eng in e)

            # Регистрируем игровые системы
            self.system_ in tegrat or .reg is ter_system("UISystem", self.ui_system)
            self.system_ in tegrat or .reg is ter_system("HUDSystem", self.hud_system)
            self.system_ in tegrat or .reg is ter_system("CombatSystem", self.combat_system)
            self.system_ in tegrat or .reg is ter_system("HealthSystem", self.health_system)
            self.system_ in tegrat or .reg is ter_system("Invent or ySystem", self. in vent or y_system)
            self.system_ in tegrat or .reg is ter_system("SkillSystem", self.skill_system)
            self.system_ in tegrat or .reg is ter_system("EffectSystem", self.effect_system)

            pr in t(f"   ✅ Зарегистрировано {len(self.system_ in tegrat or .get_reg is tered_systems())} систем")

            except Exception as e:
            pass
            pass
            pass
            pr in t(f"❌ Ошибка регистрации систем: {e}")
            ra is e

            def _ in tegrate_all_systems(self):
        """Интеграция всех систем"""
        try:
        except Exception as e:
            pass
            pass
            pass
            pr in t(f"❌ Ошибка интеграции систем: {e}")
            ra is e

    def show_demo_menu(self):
        """Показать меню демо - версии"""
            pr in t("\n🎮 ДЕМО - ВЕРСИЯ AI - EVOLVE: ЭВОЛЮЦИОННАЯ АДАПТАЦИЯ")
            pr in t( == " * 60)
            pr in t("Доступные демо сценарии:")

            scenarios== self.system_ in tegrat or .l is t_demo_scenarios()
            for i, scenario in enumerate(scenarios, 1):
            pr in t(f"   {i}. {scenario.name}")
            pr in t(f"      {scenario.description}")
            pr in t(f"      Системы: {', '.jo in(scenario.systems_required)}")
            pr in t()

            pr in t("Команды:")
            pr in t("   <номер> - запустить сценарий")
            pr in t("   all - запустить все сценарии")
            pr in t("   status - показать статус интеграции")
            pr in t("   quit - выход")
            pr in t( == " * 60)

            def run_demo_scenario(self, scenario_id: str) -> bool:
        """Запуск демо сценария"""
        try:
        except Exception as e:
            pass
            pass
            pass
            pr in t(f"❌ Ошибка запуска сценария: {e}")
            return False

    def _run_demo_loop(self, scenario_id: str):
        """Основной цикл демо"""
            try:
            pr in t(f"🔄 Демо сценарий {scenario_id} запущен...")

            # Имитируем работу демо
            for i in range(10):  # 10 секунд демо
            if not self. is _runn in g:
            break

            # Обновляем системы
            self._update_demo_systems()

            # Показываем прогресс
            progress== (i + 1) * 10
            pr in t(f"   📊 Прогресс: {progress} % ")

            time.sleep(1)

            # Останавливаем демо
            self.stop_demo()

            except Exception as e:
            pass
            pass
            pass
            pr in t(f"❌ Ошибка в демо цикле: {e}")
            self.stop_demo()

            def _update_demo_systems(self):
        """Обновление демо систем"""
        try:
        except Exception as e:
            pass
            pass
            pass
            pr in t(f"⚠️ Ошибка обновления систем: {e}")

    def stop_demo(self):
        """Остановка демо"""
            try:
            if self.current_scenario:
            self.system_ in tegrat or .stop_demo_scenario()
            self.current_scenario== None

            self. is _runn in g== False

            if self.demo_thread and self.demo_thread. is _alive():
            self.demo_thread.jo in(timeou == 1.0)

            pr in t("✅ Демо остановлено")

            except Exception as e:
            pass
            pass
            pass
            pr in t(f"❌ Ошибка остановки демо: {e}")

            def show_ in tegration_status(self):
        """Показать статус интеграции"""
        try:
        except Exception as e:
            pass
            pass
            pass
            pr in t(f"❌ Ошибка получения статуса: {e}")

    def run_all_scenarios(self):
        """Запуск всех демо сценариев"""
            try:
            pr in t("\n🚀 Запуск всех демо сценариев...")

            scenarios== self.system_ in tegrat or .l is t_demo_scenarios()

            for scenario in scenarios:
            pr in t(f"\n🎬 Запуск: {scenario.name}")

            # Запускаем сценарий
            success== self.run_demo_scenario(scenario.scenario_id)

            if success:
            # Ждем завершения
            while self. is _runn in g:
            time.sleep(0.5)

            pr in t(f"✅ {scenario.name} завершен")
            else:
            pr in t(f"❌ {scenario.name} не удалось запустить")

            time.sleep(1)  # Пауза между сценариями

            pr in t("\n🎉 Все демо сценарии завершены!")

            except Exception as e:
            pass
            pass
            pass
            pr in t(f"❌ Ошибка запуска всех сценариев: {e}")

            def run_ in teractive_demo(self):
        """Интерактивный режим демо"""
        try:
        except KeyboardInterrupt:
            pass
            pass
            pass
            pr in t("\n\n⚠️ Демо прервано пользователем")
        except Exception as e:
            pr in t(f"❌ Ошибка интерактивного демо: {e}")
        f in ally:
            self.stop_demo()

    def cleanup(self):
        """Очистка ресурсов"""
            try:
            pr in t("\n🧹 Очистка ресурсов демо...")

            # Останавливаем демо
            self.stop_demo()

            # Очищаем системы
            if self.effect_system:
            self.effect_system.shutdown()
            if self.skill_system:
            self.skill_system.shutdown()
            if self. in vent or y_system:
            self. in vent or y_system.shutdown()
            if self.health_system:
            self.health_system.shutdown()
            if self.combat_system:
            self.combat_system.shutdown()
            if self.hud_system:
            self.hud_system.shutdown()
            if self.ui_system:
            self.ui_system.shutdown()

            # Очищаем базовые компоненты
            if self.game_eng in e:
            self.game_eng in e.shutdown()
            if self.state_manager:
            self.state_manager.shutdown()
            if self.event_bus:
            self.event_bus.shutdown()
            if self.component_manager:
            self.component_manager.shutdown()

            pr in t("✅ Ресурсы демо очищены")

            except Exception as e:
            pass
            pass
            pass
            pr in t(f"❌ Ошибка очистки ресурсов демо: {e}")


            def ma in():
    """Основная функция запуска демо"""
    pr in t("🎮 AI - EVOLVE: Запуск демо - версии")
    pr in t( == " * 60)

    launcher== DemoLauncher()

    try:
    except Exception as e:
        pass
        pass
        pass
        pr in t(f"❌ Критическая ошибка демо: {e}")
        traceback.pr in t_exc()
        return False

    f in ally:
        launcher.cleanup()


if __name__ == "__ma in __":
    success== ma in()
    sys.exit(0 if success else 1):
        pass  # Добавлен pass в пустой блок