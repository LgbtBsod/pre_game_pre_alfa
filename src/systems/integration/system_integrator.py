"""
Система интеграции - связывание всех игровых систем для демонстрации
"""

import time
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from enum import Enum

from src.core.architecture import BaseComponent, ComponentType, Priority


class IntegrationType(Enum):
    """Типы интеграции"""
    UI_INTEGRATION = "ui_integration"           # Интеграция с UI
    HUD_INTEGRATION = "hud_integration"         # Интеграция с HUD
    COMBAT_INTEGRATION = "combat_integration"   # Интеграция с боевой системой
    HEALTH_INTEGRATION = "health_integration"   # Интеграция с системой здоровья
    INVENTORY_INTEGRATION = "inventory_integration"  # Интеграция с инвентарем
    SKILLS_INTEGRATION = "skills_integration"   # Интеграция с навыками
    EFFECTS_INTEGRATION = "effects_integration" # Интеграция с эффектами


class IntegrationStatus(Enum):
    """Статус интеграции"""
    NOT_INTEGRATED = "not_integrated"
    PARTIALLY_INTEGRATED = "partially_integrated"
    FULLY_INTEGRATED = "fully_integrated"
    ERROR = "error"


@dataclass
class IntegrationInfo:
    """Информация об интеграции"""
    system_name: str
    integration_type: IntegrationType
    status: IntegrationStatus
    last_update: float = 0.0
    error_message: str = ""
    integration_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DemoScenario:
    """Сценарий для демонстрации"""
    scenario_id: str
    name: str
    description: str
    systems_required: List[str]
    setup_function: Optional[Callable] = None
    cleanup_function: Optional[Callable] = None
    is_active: bool = False


class SystemIntegrator(BaseComponent):
    """
    Система интеграции
    Связывает все игровые системы для демонстрации и тестирования
    """
    
    def __init__(self):
        super().__init__(
            name="SystemIntegrator",
            component_type=ComponentType.SYSTEM,
            priority=Priority.HIGH
        )
        
        # Информация об интеграции
        self.integration_status: Dict[str, IntegrationInfo] = {}
        
        # Демо сценарии
        self.demo_scenarios: Dict[str, DemoScenario] = {}
        self.active_scenario: Optional[str] = None
        
        # Системы для интеграции
        self.target_systems: Dict[str, Any] = {}
        
        # Настройки
        self.auto_integration = True
        self.integration_interval = 1.0  # секунды
        self.last_integration_time = 0.0
        
    def _on_initialize(self) -> bool:
        """Инициализация системы интеграции"""
        try:
            # Создание демо сценариев
            self._create_demo_scenarios()
            
            # Настройка интеграции
            self._setup_integration()
            
            return True
        except Exception as e:
            self.logger.error(f"Ошибка инициализации SystemIntegrator: {e}")
            return False
    
    def _create_demo_scenarios(self):
        """Создание демо сценариев"""
        # Сценарий 1: Демонстрация боевой системы
        combat_scenario = DemoScenario(
            scenario_id="combat_demo",
            name="Демонстрация боевой системы",
            description="Показывает работу боевой системы с инициативой, позиционированием и типами атак",
            systems_required=["CombatSystem", "HealthSystem", "DamageSystem", "UISystem", "HUDSystem"],
            setup_function=self._setup_combat_demo,
            cleanup_function=self._cleanup_combat_demo
        )
        self.demo_scenarios["combat_demo"] = combat_scenario
        
        # Сценарий 2: Демонстрация системы здоровья
        health_scenario = DemoScenario(
            scenario_id="health_demo",
            name="Демонстрация системы здоровья",
            description="Показывает работу системы здоровья с ресурсами, состояниями и регенерацией",
            systems_required=["HealthSystem", "UISystem", "HUDSystem"],
            setup_function=self._setup_health_demo,
            cleanup_function=self._cleanup_health_demo
        )
        self.demo_scenarios["health_demo"] = health_scenario
        
        # Сценарий 3: Демонстрация инвентаря
        inventory_scenario = DemoScenario(
            scenario_id="inventory_demo",
            name="Демонстрация системы инвентаря",
            description="Показывает работу системы инвентаря с предметами, экипировкой и крафтингом",
            systems_required=["InventorySystem", "UISystem", "HUDSystem"],
            setup_function=self._setup_inventory_demo,
            cleanup_function=self._cleanup_inventory_demo
        )
        self.demo_scenarios["inventory_demo"] = inventory_scenario
        
        # Сценарий 4: Демонстрация навыков
        skills_scenario = DemoScenario(
            scenario_id="skills_demo",
            name="Демонстрация системы навыков",
            description="Показывает работу системы навыков с типами, категориями и деревьями",
            systems_required=["SkillSystem", "UISystem", "HUDSystem"],
            setup_function=self._setup_skills_demo,
            cleanup_function=self._cleanup_skills_demo
        )
        self.demo_scenarios["skills_demo"] = skills_scenario
        
        # Сценарий 5: Демонстрация эффектов
        effects_scenario = DemoScenario(
            scenario_id="effects_demo",
            name="Демонстрация системы эффектов",
            description="Показывает работу системы эффектов с типами, комбинациями и цепочками",
            systems_required=["EffectSystem", "UISystem", "HUDSystem"],
            setup_function=self._setup_effects_demo,
            cleanup_function=self._cleanup_effects_demo
        )
        self.demo_scenarios["effects_demo"] = effects_scenario
        
        # Сценарий 6: Полная интеграция
        full_scenario = DemoScenario(
            scenario_id="full_integration",
            name="Полная интеграция всех систем",
            description="Демонстрирует работу всех систем вместе",
            systems_required=["CombatSystem", "HealthSystem", "InventorySystem", "SkillSystem", "EffectSystem", "UISystem", "HUDSystem"],
            setup_function=self._setup_full_integration,
            cleanup_function=self._cleanup_full_integration
        )
        self.demo_scenarios["full_integration"] = full_scenario
    
    def _setup_integration(self):
        """Настройка интеграции"""
        self.auto_integration = True
        self.integration_interval = 1.0
    
    # Регистрация систем
    def register_system(self, system_name: str, system_instance: Any):
        """Зарегистрировать систему для интеграции"""
        self.target_systems[system_name] = system_instance
        
        # Создаем информацию об интеграции
        integration_info = IntegrationInfo(
            system_name=system_name,
            integration_type=IntegrationType.UI_INTEGRATION,  # По умолчанию
            status=IntegrationStatus.NOT_INTEGRATED
        )
        self.integration_status[system_name] = integration_info
        
        self.logger.info(f"Зарегистрирована система: {system_name}")
    
    def unregister_system(self, system_name: str):
        """Отменить регистрацию системы"""
        if system_name in self.target_systems:
            del self.target_systems[system_name]
        
        if system_name in self.integration_status:
            del self.integration_status[system_name]
        
        self.logger.info(f"Отменена регистрация системы: {system_name}")
    
    # Управление интеграцией
    def integrate_system(self, system_name: str, integration_type: IntegrationType):
        """Интегрировать систему"""
        if system_name not in self.target_systems:
            self.logger.error(f"Система {system_name} не зарегистрирована")
            return False
        
        try:
            system_instance = self.target_systems[system_name]
            integration_info = self.integration_status[system_name]
            
            # Выполняем интеграцию в зависимости от типа
            if integration_type == IntegrationType.UI_INTEGRATION:
                success = self._integrate_with_ui(system_name, system_instance)
            elif integration_type == IntegrationType.HUD_INTEGRATION:
                success = self._integrate_with_hud(system_name, system_instance)
            elif integration_type == IntegrationType.COMBAT_INTEGRATION:
                success = self._integrate_with_combat(system_name, system_instance)
            elif integration_type == IntegrationType.HEALTH_INTEGRATION:
                success = self._integrate_with_health(system_name, system_instance)
            elif integration_type == IntegrationType.INVENTORY_INTEGRATION:
                success = self._integrate_with_inventory(system_name, system_instance)
            elif integration_type == IntegrationType.SKILLS_INTEGRATION:
                success = self._integrate_with_skills(system_name, system_instance)
            elif integration_type == IntegrationType.EFFECTS_INTEGRATION:
                success = self._integrate_with_effects(system_name, system_instance)
            else:
                success = False
            
            # Обновляем статус
            if success:
                integration_info.status = IntegrationStatus.FULLY_INTEGRATED
                integration_info.integration_type = integration_type
                integration_info.last_update = time.time()
                self.logger.info(f"Система {system_name} успешно интегрирована")
            else:
                integration_info.status = IntegrationStatus.ERROR
                integration_info.error_message = "Ошибка интеграции"
                self.logger.error(f"Ошибка интеграции системы {system_name}")
            
            return success
            
        except Exception as e:
            integration_info = self.integration_status[system_name]
            integration_info.status = IntegrationStatus.ERROR
            integration_info.error_message = str(e)
            self.logger.error(f"Исключение при интеграции {system_name}: {e}")
            return False
    
    def integrate_all_systems(self):
        """Интегрировать все системы"""
        self.logger.info("Начинаем интеграцию всех систем...")
        
        success_count = 0
        total_count = len(self.target_systems)
        
        for system_name in self.target_systems:
            # Определяем тип интеграции по имени системы
            if "UI" in system_name:
                integration_type = IntegrationType.UI_INTEGRATION
            elif "HUD" in system_name:
                integration_type = IntegrationType.HUD_INTEGRATION
            elif "Combat" in system_name:
                integration_type = IntegrationType.COMBAT_INTEGRATION
            elif "Health" in system_name:
                integration_type = IntegrationType.HEALTH_INTEGRATION
            elif "Inventory" in system_name:
                integration_type = IntegrationType.INVENTORY_INTEGRATION
            elif "Skill" in system_name:
                integration_type = IntegrationType.SKILLS_INTEGRATION
            elif "Effect" in system_name:
                integration_type = IntegrationType.EFFECTS_INTEGRATION
            else:
                integration_type = IntegrationType.UI_INTEGRATION
            
            if self.integrate_system(system_name, integration_type):
                success_count += 1
        
        self.logger.info(f"Интеграция завершена: {success_count}/{total_count} систем успешно интегрированы")
        return success_count == total_count
    
    # Методы интеграции по типам
    def _integrate_with_ui(self, system_name: str, system_instance: Any) -> bool:
        """Интегрировать с UI системой"""
        try:
            # Проверяем, есть ли UI система
            if "UISystem" not in self.target_systems:
                return False
            
            ui_system = self.target_systems["UISystem"]
            
            # Регистрируем UI элементы для системы
            if hasattr(system_instance, 'create_ui_elements'):
                system_instance.create_ui_elements(ui_system)
            
            # Регистрируем обработчики событий
            if hasattr(system_instance, 'register_ui_handlers'):
                system_instance.register_ui_handlers(ui_system)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка интеграции {system_name} с UI: {e}")
            return False
    
    def _integrate_with_hud(self, system_name: str, system_instance: Any) -> bool:
        """Интегрировать с HUD системой"""
        try:
            # Проверяем, есть ли HUD система
            if "HUDSystem" not in self.target_systems:
                return False
            
            hud_system = self.target_systems["HUDSystem"]
            
            # Регистрируем HUD элементы для системы
            if hasattr(system_instance, 'create_hud_elements'):
                system_instance.create_hud_elements(hud_system)
            
            # Регистрируем обновления HUD
            if hasattr(system_instance, 'register_hud_updates'):
                system_instance.register_hud_updates(hud_system)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка интеграции {system_name} с HUD: {e}")
            return False
    
    def _integrate_with_combat(self, system_name: str, system_instance: Any) -> bool:
        """Интегрировать с боевой системой"""
        try:
            # Проверяем, есть ли боевая система
            if "CombatSystem" not in self.target_systems:
                return False
            
            combat_system = self.target_systems["CombatSystem"]
            
            # Регистрируем обработчики боевых событий
            if hasattr(system_instance, 'register_combat_handlers'):
                system_instance.register_combat_handlers(combat_system)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка интеграции {system_name} с боевой системой: {e}")
            return False
    
    def _integrate_with_health(self, system_name: str, system_instance: Any) -> bool:
        """Интегрировать с системой здоровья"""
        try:
            # Проверяем, есть ли система здоровья
            if "HealthSystem" not in self.target_systems:
                return False
            
            health_system = self.target_systems["HealthSystem"]
            
            # Регистрируем обработчики здоровья
            if hasattr(system_instance, 'register_health_handlers'):
                system_instance.register_health_handlers(health_system)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка интеграции {system_name} с системой здоровья: {e}")
            return False
    
    def _integrate_with_inventory(self, system_name: str, system_instance: Any) -> bool:
        """Интегрировать с системой инвентаря"""
        try:
            # Проверяем, есть ли система инвентаря
            if "InventorySystem" not in self.target_systems:
                return False
            
            inventory_system = self.target_systems["InventorySystem"]
            
            # Регистрируем обработчики инвентаря
            if hasattr(system_instance, 'register_inventory_handlers'):
                system_instance.register_inventory_handlers(inventory_system)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка интеграции {system_name} с системой инвентаря: {e}")
            return False
    
    def _integrate_with_skills(self, system_name: str, system_instance: Any) -> bool:
        """Интегрировать с системой навыков"""
        try:
            # Проверяем, есть ли система навыков
            if "SkillSystem" not in self.target_systems:
                return False
            
            skill_system = self.target_systems["SkillSystem"]
            
            # Регистрируем обработчики навыков
            if hasattr(system_instance, 'register_skill_handlers'):
                system_instance.register_skill_handlers(skill_system)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка интеграции {system_name} с системой навыков: {e}")
            return False
    
    def _integrate_with_effects(self, system_name: str, system_instance: Any) -> bool:
        """Интегрировать с системой эффектов"""
        try:
            # Проверяем, есть ли система эффектов
            if "EffectSystem" not in self.target_systems:
                return False
            
            effect_system = self.target_systems["EffectSystem"]
            
            # Регистрируем обработчики эффектов
            if hasattr(system_instance, 'register_effect_handlers'):
                system_instance.register_effect_handlers(effect_system)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка интеграции {system_name} с системой эффектов: {e}")
            return False
    
    # Управление демо сценариями
    def start_demo_scenario(self, scenario_id: str) -> bool:
        """Запустить демо сценарий"""
        if scenario_id not in self.demo_scenarios:
            self.logger.error(f"Сценарий {scenario_id} не найден")
            return False
        
        # Останавливаем текущий сценарий
        if self.active_scenario:
            self.stop_demo_scenario()
        
        scenario = self.demo_scenarios[scenario_id]
        
        # Проверяем доступность систем
        missing_systems = []
        for system_name in scenario.systems_required:
            if system_name not in self.target_systems:
                missing_systems.append(system_name)
        
        if missing_systems:
            self.logger.error(f"Недоступны системы для сценария {scenario_id}: {missing_systems}")
            return False
        
        # Запускаем сценарий
        try:
            if scenario.setup_function:
                scenario.setup_function()
            
            scenario.is_active = True
            self.active_scenario = scenario_id
            
            self.logger.info(f"Запущен демо сценарий: {scenario.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка запуска сценария {scenario_id}: {e}")
            return False
    
    def stop_demo_scenario(self):
        """Остановить текущий демо сценарий"""
        if not self.active_scenario:
            return
        
        scenario = self.demo_scenarios[self.active_scenario]
        
        try:
            if scenario.cleanup_function:
                scenario.cleanup_function()
            
            scenario.is_active = False
            self.active_scenario = None
            
            self.logger.info(f"Остановлен демо сценарий: {scenario.name}")
            
        except Exception as e:
            self.logger.error(f"Ошибка остановки сценария {self.active_scenario}: {e}")
    
    def get_active_scenario(self) -> Optional[DemoScenario]:
        """Получить активный сценарий"""
        if self.active_scenario:
            return self.demo_scenarios[self.active_scenario]
        return None
    
    def list_demo_scenarios(self) -> List[DemoScenario]:
        """Получить список всех демо сценариев"""
        return list(self.demo_scenarios.values())
    
    # Настройка демо сценариев
    def _setup_combat_demo(self):
        """Настройка демо боевой системы"""
        try:
            # Создаем тестовые сущности
            combat_system = self.target_systems.get("CombatSystem")
            if combat_system:
                # TODO: Создание тестовых сущностей для демо
                pass
            
            self.logger.info("Настроен демо сценарий боевой системы")
            
        except Exception as e:
            self.logger.error(f"Ошибка настройки демо боевой системы: {e}")
    
    def _cleanup_combat_demo(self):
        """Очистка демо боевой системы"""
        try:
            # TODO: Очистка тестовых данных
            self.logger.info("Очищен демо сценарий боевой системы")
            
        except Exception as e:
            self.logger.error(f"Ошибка очистки демо боевой системы: {e}")
    
    def _setup_health_demo(self):
        """Настройка демо системы здоровья"""
        try:
            # TODO: Настройка демо системы здоровья
            self.logger.info("Настроен демо сценарий системы здоровья")
            
        except Exception as e:
            self.logger.error(f"Ошибка настройки демо системы здоровья: {e}")
    
    def _cleanup_health_demo(self):
        """Очистка демо системы здоровья"""
        try:
            # TODO: Очистка демо системы здоровья
            self.logger.info("Очищен демо сценарий системы здоровья")
            
        except Exception as e:
            self.logger.error(f"Ошибка очистки демо системы здоровья: {e}")
    
    def _setup_inventory_demo(self):
        """Настройка демо системы инвентаря"""
        try:
            # TODO: Настройка демо системы инвентаря
            self.logger.info("Настроен демо сценарий системы инвентаря")
            
        except Exception as e:
            self.logger.error(f"Ошибка настройки демо системы инвентаря: {e}")
    
    def _cleanup_inventory_demo(self):
        """Очистка демо системы инвентаря"""
        try:
            # TODO: Очистка демо системы инвентаря
            self.logger.info("Очищен демо сценарий системы инвентаря")
            
        except Exception as e:
            self.logger.error(f"Ошибка очистки демо системы инвентаря: {e}")
    
    def _setup_skills_demo(self):
        """Настройка демо системы навыков"""
        try:
            # TODO: Настройка демо системы навыков
            self.logger.info("Настроен демо сценарий системы навыков")
            
        except Exception as e:
            self.logger.error(f"Ошибка настройки демо системы навыков: {e}")
    
    def _cleanup_skills_demo(self):
        """Очистка демо системы навыков"""
        try:
            # TODO: Очистка демо системы навыков
            self.logger.info("Очищен демо сценарий системы навыков")
            
        except Exception as e:
            self.logger.error(f"Ошибка очистки демо системы навыков: {e}")
    
    def _setup_effects_demo(self):
        """Настройка демо системы эффектов"""
        try:
            # TODO: Настройка демо системы эффектов
            self.logger.info("Настроен демо сценарий системы эффектов")
            
        except Exception as e:
            self.logger.error(f"Ошибка настройки демо системы эффектов: {e}")
    
    def _cleanup_effects_demo(self):
        """Очистка демо системы эффектов"""
        try:
            # TODO: Очистка демо системы эффектов
            self.logger.info("Очищен демо сценарий системы эффектов")
            
        except Exception as e:
            self.logger.error(f"Ошибка очистки демо системы эффектов: {e}")
    
    def _setup_full_integration(self):
        """Настройка полной интеграции"""
        try:
            # TODO: Настройка полной интеграции всех систем
            self.logger.info("Настроен демо сценарий полной интеграции")
            
        except Exception as e:
            self.logger.error(f"Ошибка настройки полной интеграции: {e}")
    
    def _cleanup_full_integration(self):
        """Очистка полной интеграции"""
        try:
            # TODO: Очистка полной интеграции
            self.logger.info("Очищен демо сценарий полной интеграции")
            
        except Exception as e:
            self.logger.error(f"Ошибка очистки полной интеграции: {e}")
    
    # Обновление системы
    def update(self, delta_time: float):
        """Обновить систему интеграции"""
        current_time = time.time()
        
        # Проверяем, нужно ли выполнять автоматическую интеграцию
        if self.auto_integration and (current_time - self.last_integration_time >= self.integration_interval):
            self.integrate_all_systems()
            self.last_integration_time = current_time
    
    # Публичные методы
    def get_integration_status(self) -> Dict[str, IntegrationInfo]:
        """Получить статус интеграции всех систем"""
        return self.integration_status.copy()
    
    def get_system_integration_status(self, system_name: str) -> Optional[IntegrationInfo]:
        """Получить статус интеграции конкретной системы"""
        return self.integration_status.get(system_name)
    
    def get_registered_systems(self) -> List[str]:
        """Получить список зарегистрированных систем"""
        return list(self.target_systems.keys())
    
    def is_system_integrated(self, system_name: str) -> bool:
        """Проверить, интегрирована ли система"""
        if system_name not in self.integration_status:
            return False
        
        status = self.integration_status[system_name]
        return status.status == IntegrationStatus.FULLY_INTEGRATED
    
    def get_integration_summary(self) -> Dict[str, Any]:
        """Получить сводку по интеграции"""
        total_systems = len(self.integration_status)
        integrated_systems = sum(1 for info in self.integration_status.values() 
                               if info.status == IntegrationStatus.FULLY_INTEGRATED)
        error_systems = sum(1 for info in self.integration_status.values() 
                           if info.status == IntegrationStatus.ERROR)
        
        return {
            "total_systems": total_systems,
            "integrated_systems": integrated_systems,
            "error_systems": error_systems,
            "integration_percentage": (integrated_systems / total_systems * 100) if total_systems > 0 else 0,
            "active_scenario": self.active_scenario,
            "available_scenarios": len(self.demo_scenarios)
        }
