#!/usr/bin/env python3
"""
System Factory - Фабрика систем
Централизованное создание и управление всеми игровыми системами
"""

import logging
from typing import Dict, Any, Optional, Type
from .interfaces import ISystem, IEventSystem
from .event_system import EventSystem
from .config_manager import ConfigManager
from .system_manager import SystemManager

logger = logging.getLogger(__name__)

class SystemFactory:
    """Фабрика для создания игровых систем"""
    
    def __init__(self, config_manager: ConfigManager, event_system: EventSystem, system_manager: Optional[SystemManager] = None):
        self.config_manager = config_manager
        self.event_system = event_system
        self.system_manager = system_manager or SystemManager(event_system)
        # Адаптер для совместимости с системами, ожидающими event_bus API
        try:
            from .event_adapter import EventBusAdapter  # локальный импорт во избежание циклов
            self.event_bus_adapter = EventBusAdapter(self.event_system)
        except Exception:
            self.event_bus_adapter = None
        
        # Реестр систем
        self.system_registry: Dict[str, Type[ISystem]] = {}
        
        # Созданные системы
        self.created_systems: Dict[str, ISystem] = {}
        
        # Зависимости систем
        self.system_dependencies = {
            'unified_ai_system': ['event_system', 'config_manager'],
            'combat_system': ['event_system', 'unified_ai_system', 'effect_system', 'damage_system'],
            'content_generator': ['event_system', 'config_manager'],
            'emotion_system': ['event_system', 'unified_ai_system'],
            'evolution_system': ['event_system', 'unified_ai_system'],
            'inventory_system': ['event_system', 'item_system'],
            'item_system': ['event_system', 'content_generator'],
            'skill_system': ['event_system', 'content_generator', 'effect_system', 'damage_system'],
            'ui_system': ['event_system', 'config_manager', 'effect_system'],
            'render_system': ['event_system', 'config_manager', 'effect_system'],
            'effect_system': ['event_system', 'config_manager'],
            'damage_system': ['event_system', 'config_manager'],
            'social_system': ['event_system', 'config_manager']
        }
        
        # Автоматическая регистрация систем
        self._register_default_systems()
        
        logger.info("Фабрика систем инициализирована")
    
    def register_system(self, system_name: str, system_class: Type[ISystem]) -> bool:
        """Регистрация системы в фабрике"""
        try:
            self.system_registry[system_name] = system_class
            logger.debug(f"Система {system_name} зарегистрирована в фабрике")
            return True
        except Exception as e:
            logger.error(f"Ошибка регистрации системы {system_name}: {e}")
            return False
    
    def create_system(self, system_name: str, **kwargs) -> Optional[ISystem]:
        """Создание системы"""
        try:
            if system_name not in self.system_registry:
                logger.error(f"Система {system_name} не зарегистрирована")
                return None
            
            # Предупреждаем о незакрытых зависимостях, но не блокируем создание.
            # Порядок инициализации обеспечивается менеджером систем.
            if not self._check_dependencies(system_name):
                logger.warning(f"Некоторые зависимости для {system_name} еще не созданы — создание продолжится, инициализация будет упорядочена")
            
            # Создаем систему
            system_class = self.system_registry[system_name]
            # Внедряем известные зависимости, если система ожидает их через kwargs
            init_kwargs = dict(kwargs)
            if 'config_manager' in system_class.__init__.__code__.co_varnames:
                init_kwargs.setdefault('config_manager', self.config_manager)
            if 'event_system' in system_class.__init__.__code__.co_varnames:
                init_kwargs.setdefault('event_system', self.event_system)
            system = system_class(**init_kwargs)

            # Инъекция адаптера event_bus для совместимости
            try:
                if getattr(system, 'event_bus', None) is None and self.event_bus_adapter is not None:
                    setattr(system, 'event_bus', self.event_bus_adapter)
            except Exception:
                pass
            
            # Добавляем в менеджер систем
            dependencies = self.system_dependencies.get(system_name, [])
            self.system_manager.add_system(system_name, system, dependencies)
            
            # Сохраняем созданную систему
            self.created_systems[system_name] = system
            
            logger.info(f"Система {system_name} создана и добавлена в менеджер")
            return system
            
        except Exception as e:
            logger.error(f"Ошибка создания системы {system_name}: {e}")
            return None
    
    def get_system(self, system_name: str) -> Optional[ISystem]:
        """Получение созданной системы"""
        return self.created_systems.get(system_name)
    
    def initialize_all_systems(self) -> bool:
        """Инициализация всех систем через менеджер систем (без двойной инициализации)."""
        try:
            logger.info("Инициализация всех систем (через SystemManager)...")
            return self.system_manager.initialize()
        except Exception as e:
            logger.error(f"Ошибка инициализации систем: {e}")
            return False
    
    def _check_dependencies(self, system_name: str) -> bool:
        """Проверка зависимостей системы.
        Контекстные зависимости (config_manager, event_system и пр.) считаются удовлетворенными."""
        dependencies = self.system_dependencies.get(system_name, [])
        context_deps = {"event_system", "config_manager", "resource_manager", "scene_manager", "system_manager"}
        ok = True
        for dep in dependencies:
            if dep in context_deps:
                continue
            if dep not in self.created_systems:
                logger.debug(f"Зависимость {dep} для системы {system_name} еще не создана")
                ok = False
        return ok
    
    def _determine_initialization_order(self) -> list:
        """Определение порядка инициализации систем"""
        # Простая топологическая сортировка
        order = []
        visited = set()
        temp_visited = set()
        
        def visit(system_name):
            if system_name in temp_visited:
                raise ValueError(f"Циклическая зависимость обнаружена: {system_name}")
            
            if system_name in visited:
                return
            
            temp_visited.add(system_name)
            
            dependencies = self.system_dependencies.get(system_name, [])
            for dep in dependencies:
                if dep in self.created_systems:
                    visit(dep)
            
            temp_visited.remove(system_name)
            visited.add(system_name)
            order.append(system_name)
        
        for system_name in self.created_systems:
            if system_name not in visited:
                visit(system_name)
        
        return order
    
    def update_all_systems(self, delta_time: float) -> None:
        """Обновление всех систем"""
        try:
            # Делегируем обновление менеджеру систем, чтобы избежать двойных апдейтов
            if self.system_manager:
                self.system_manager.update_all_systems(delta_time)
            else:
                # Fallback на прямое обновление при отсутствии менеджера
                for system_name, system in self.created_systems.items():
                    try:
                        system.update(delta_time)
                    except Exception as e:
                        logger.error(f"Ошибка обновления системы {system_name}: {e}")
        except Exception as e:
            logger.error(f"Ошибка обновления систем: {e}")
    
    def cleanup_all_systems(self) -> None:
        """Очистка всех систем"""
        try:
            logger.info("Очистка всех систем...")
            
            # Очищаем в обратном порядке инициализации
            for system_name in reversed(list(self.created_systems.keys())):
                try:
                    system = self.created_systems[system_name]
                    system.cleanup()
                    logger.info(f"Система {system_name} очищена")
                except Exception as e:
                    logger.error(f"Ошибка очистки системы {system_name}: {e}")
            
            # Очищаем менеджер систем
            self.system_manager.cleanup()
            
            self.created_systems.clear()
            logger.info("Все системы очищены")
            
        except Exception as e:
            logger.error(f"Ошибка очистки систем: {e}")
    
    def _register_default_systems(self):
        """Регистрация систем по умолчанию"""
        try:
            # Регистрация Unified AI System
            from ..systems.ai.unified_ai_system import UnifiedAISystem
            self.register_system('unified_ai_system', UnifiedAISystem)
            
            # Регистрация других систем
            from ..systems.combat.combat_system import CombatSystem
            self.register_system('combat_system', CombatSystem)
            
            from ..systems.effects.effect_system import EffectSystem
            self.register_system('effect_system', EffectSystem)
            
            from ..systems.skills.skill_system import SkillSystem
            self.register_system('skill_system', SkillSystem)
            
            from ..systems.damage.damage_system import DamageSystem
            self.register_system('damage_system', DamageSystem)
            
            from ..systems.inventory.inventory_system import InventorySystem
            self.register_system('inventory_system', InventorySystem)
            
            from ..systems.items.item_system import ItemSystem
            self.register_system('item_system', ItemSystem)
            
            # Социальная система
            try:
                from ..systems.social.social_system import SocialSystem
                self.register_system('social_system', SocialSystem)
            except Exception:
                pass
            
            from ..systems.emotion.emotion_system import EmotionSystem
            self.register_system('emotion_system', EmotionSystem)
            
            from ..systems.evolution.evolution_system import EvolutionSystem
            self.register_system('evolution_system', EvolutionSystem)
            
            from ..systems.ui.ui_system import UISystem
            self.register_system('ui_system', UISystem)
            
            from ..systems.rendering.render_system import RenderSystem
            self.register_system('render_system', RenderSystem)
            
            from ..systems.content.content_generator import ContentGenerator
            self.register_system('content_generator', ContentGenerator)
            
            logger.info("Системы по умолчанию зарегистрированы")
            
        except Exception as e:
            logger.error(f"Ошибка регистрации систем по умолчанию: {e}")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о всех системах"""
        info = {
            'registered_systems': list(self.system_registry.keys()),
            'created_systems': list(self.created_systems.keys()),
            'system_details': {}
        }
        
        for system_name, system in self.created_systems.items():
            try:
                info['system_details'][system_name] = system.get_system_info()
            except Exception as e:
                logger.error(f"Ошибка получения информации о системе {system_name}: {e}")
        
        return info
