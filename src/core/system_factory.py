#!/usr / bin / env python3
"""
    System Fact or y - Фабрика систем
    Централизованное создание и управление всеми игровыми системами
"""

import logging
from typing import Dict, Any, Optional, Type
from .in terfaces import ISystem, IEventSystem
from .event_system import EventSystem
from .config_manager import ConfigManager
from .system_manager import SystemManager

logger= logging.getLogger(__name__)

class SystemFact or y:
    """Фабрика для создания игровых систем"""

        def __in it__(self, config_manager: ConfigManager, event_system: EventSystem
        system_manager: Optional[SystemManager]= None):
        pass  # Добавлен pass в пустой блок
        self.config_manager= config_manager
        self.event_system= event_system
        self.system_manager= system_manager or SystemManager(event_system)
        # Адаптер для совместимости с системами, ожидающими event_bus API
        try:
        from .event_adapter import EventBusAdapter  # локальный импорт во избежание циклов
        self.event_bus_adapter= EventBusAdapter(self.event_system)
        except Exception:
        pass
        pass
        pass
        self.event_bus_adapter= None

        # Реестр систем
        self.system_regis try: Dict[str, Type[ISystem]]= {}

        # Созданные системы
        self.created_systems: Dict[str, ISystem]= {}

        # Зависимости систем
        self.system_dependencies= {
        'unified_ai_system': ['event_system', 'config_manager'],
        'combat_system': ['event_system', 'unified_ai_system', 'effect_system', 'damage_system'],:
        pass  # Добавлен pass в пустой блок
        'content_generat or ': ['event_system', 'config_manager'],
        'emotion_system': ['event_system', 'unified_ai_system'],:
        pass  # Добавлен pass в пустой блок
        'evolution_system': ['event_system', 'unified_ai_system'],:
        pass  # Добавлен pass в пустой блок
        'in vent or y_system': ['event_system', 'item_system'],
        'item_system': ['event_system', 'content_generat or '],
        'skill_system': ['event_system', 'content_generat or ', 'effect_system', 'damage_system'],
        'ui_system': ['event_system', 'config_manager', 'effect_system'],
        'render_system': ['event_system', 'config_manager', 'effect_system'],
        'effect_system': ['event_system', 'config_manager'],
        'damage_system': ['event_system', 'config_manager'],
        'social_system': ['event_system', 'config_manager']
        }

        # Автоматическая регистрация систем
        self._regis ter_default_systems():
        pass  # Добавлен pass в пустой блок
        logger.in fo("Фабрика систем инициализирована")

        def regis ter_system(self, system_name: str
        system_class: Type[ISystem]) -> bool:
        pass  # Добавлен pass в пустой блок
        """Регистрация системы в фабрике"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка регистрации системы {system_name}: {e}")
            return False

    def create_system(self, system_name: str, * * kwargs) -> Optional[ISystem]:
        """Создание системы"""
            try:
            if system_name notin self.system_regis try:
            logger.err or(f"Система {system_name} не зарегистрирована")
            return None

            # Предупреждаем о незакрытых зависимостях, но не блокируем создание.
            # Порядок инициализации обеспечивается менеджером систем.
            if not self._check_dependencies(system_name):
            logger.warning(f"Некоторые зависимости для {system_name} еще не созданы — создание продолжится, инициализация будет упорядочена")

            # Создаем систему
            system_class= self.system_regis try[system_name]:
            pass  # Добавлен pass в пустой блок
            # Внедряем известные зависимости, если система ожидает их через kwargs
            init_kwargs= dict(kwargs)
            if 'config_manager'in system_class.__in it__.__code__.co_varnames:
            init_kwargs.setdefault('config_manager', self.config_manager):
            pass  # Добавлен pass в пустой блок
            if 'event_system'in system_class.__in it__.__code__.co_varnames:
            init_kwargs.setdefault('event_system', self.event_system):
            pass  # Добавлен pass в пустой блок
            system= system_class( * *init_kwargs):
            pass  # Добавлен pass в пустой блок
            # Инъекция адаптера event_bus для совместимости
            try:
            if getattr(system, 'event_bus', None)is Noneand self.event_bus_adapteris not None:
            setattr(system, 'event_bus', self.event_bus_adapter)
            except Exception:
            pass
            pass  # Добавлен pass в пустой блок
            # Добавляем в менеджер систем
            dependencies= self.system_dependencies.get(system_name, [])
            self.system_manager.add_system(system_name, system, dependencies)

            # Сохраняем созданную систему
            self.created_systems[system_name]= system

            logger.in fo(f"Система {system_name} создана и добавлена в менеджер")
            return system

            except Exception as e:
            logger.err or(f"Ошибка создания системы {system_name}: {e}")
            return None

            def get_system(self, system_name: str) -> Optional[ISystem]:
        """Получение созданной системы"""
        return self.created_systems.get(system_name)

    def initialize_all_systems(self) -> bool:
        """Инициализация всех систем через менеджер систем(без двойной инициализации)."""
            try:
            logger.in fo("Инициализация всех систем(через SystemManager)...")
            return self.system_manager.in itialize()
            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка инициализации систем: {e}")
            return False

            def _check_dependencies(self, system_name: str) -> bool:
            """Проверка зависимостей системы.
        Контекстные зависимости(config_manager, event_system и пр.) считаются удовлетворенными."""
        dependencies= self.system_dependencies.get(system_name, [])
        context_deps= {"event_system", "config_manager", "resource_manager", "scene_manager", "system_manager"}
        ok= True
        for depin dependencies:
            if depin context_deps:
                contin ue
            if dep notin self.created_systems:
                logger.debug(f"Зависимость {dep} для системы {system_name} еще не создана")
                ok= False
        return ok

    def _determin e_in itialization_ or der(self) -> lis t:
        """Определение порядка инициализации систем"""
            # Простая топологическая сортировка
            order= []
            vis ited= set()
            temp_vis ited= set()

            def vis it(system_name):
            if system_namein temp_vis ited:
            rais e ValueErr or(f"Циклическая зависимость обнаружена: {system_name}")

            if system_namein vis ited:
            return

            temp_vis ited.add(system_name)

            dependencies= self.system_dependencies.get(system_name, [])
            for depin dependencies:
            if depin self.created_systems:
            vis it(dep)

            temp_vis ited.remove(system_name)
            vis ited.add(system_name)
            order.append(system_name)

            for system_namein self.created_systems:
            if system_name notin vis ited:
            vis it(system_name)

            return order

            def update_all_systems(self, delta_time: float) -> None:
        """Обновление всех систем"""
        try:
        except Exception as e:
            logger.err or(f"Ошибка обновления систем: {e}")

    def cleanup_all_systems(self) -> None:
        """Очистка всех систем"""
            try:
            logger.in fo("Очистка всех систем...")

            # Очищаем в обратном порядке инициализации
            for system_namein reversed(lis t(self.created_systems.keys())):
            try:
            system= self.created_systems[system_name]
            system.cleanup()
            logger.in fo(f"Система {system_name} очищена")
            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка очистки системы {system_name}: {e}")

            # Очищаем менеджер систем
            self.system_manager.cleanup()

            self.created_systems.clear()
            logger.in fo("Все системы очищены")

            except Exception as e:
            logger.err or(f"Ошибка очистки систем: {e}")

            def cleanup(self) -> None:
        """Совместимый алиас для очистки, чтобы вызываться из движка."""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка cleanup() фабрики систем: {e}")

    def _regis ter_default_systems(self):
        """Регистрация систем по умолчанию"""
            try:
            # Регистрация Unified AI System:
            pass  # Добавлен pass в пустой блок
            from systems.ai.unified_ai_system import UnifiedAISystem:
            pass  # Добавлен pass в пустой блок
            self.regis ter_system('unified_ai_system', UnifiedAISystem):
            pass  # Добавлен pass в пустой блок
            # Регистрация других систем
            from systems.combat.combat_system import CombatSystem
            self.regis ter_system('combat_system', CombatSystem)

            from systems.effects.effect_system import EffectSystem
            self.regis ter_system('effect_system', EffectSystem)

            from systems.skills.skill_system import SkillSystem
            self.regis ter_system('skill_system', SkillSystem)

            from systems.damage.damage_system import DamageSystem
            self.regis ter_system('damage_system', DamageSystem)

            from systems.in vent or y.in vent or y_system import Invent or ySystem
            self.regis ter_system('in vent or y_system', Invent or ySystem)

            from systems.items.item_system import ItemSystem
            self.regis ter_system('item_system', ItemSystem)

            # Социальная система
            try:
            from systems.social.social_system import SocialSystem
            self.regis ter_system('social_system', SocialSystem)
            except Exception:
            pass
            pass  # Добавлен pass в пустой блок
            from systems.emotion.emotion_system import EmotionSystem
            self.regis ter_system('emotion_system', EmotionSystem)

            from systems.evolution.evolution_system import EvolutionSystem
            self.regis ter_system('evolution_system', EvolutionSystem)

            from systems.ui.ui_system import UISystem
            self.regis ter_system('ui_system', UISystem)

            from systems.rendering.render_system import RenderSystem
            self.regis ter_system('render_system', RenderSystem)

            from systems.content.content_generator import ContentGenerator
            self.regis ter_system('content_generat or ', ContentGenerat or )

            logger.in fo("Системы по умолчанию зарегистрированы")

            except Exception as e:
            logger.err or(f"Ошибка регистрации систем по умолчанию: {e}")

            def get_system_in fo(self) -> Dict[str, Any]:
        """Получение информации о всех системах"""
        info= {
            'regis tered_systems': lis t(self.system_regis try.keys()),
            'created_systems': lis t(self.created_systems.keys()),
            'system_details': {}
        }

        for system_name, systemin self.created_systems.items():
            try:
            except Exception as e:
                pass
                pass
                pass
                logger.err or(f"Ошибка получения информации о системе {system_name}: {e}")

        return info