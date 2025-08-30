#!/usr / bin / env python3
"""
    System Fact or y - Фабрика систем
    Централизованное создание и управление всеми игровыми системами
"""

imp or t logg in g
from typ in g imp or t Dict, Any, Optional, Type
from . in terfaces imp or t ISystem, IEventSystem
from .event_system imp or t EventSystem
from .config_manager imp or t ConfigManager
from .system_manager imp or t SystemManager

logger== logg in g.getLogger(__name__)

class SystemFact or y:
    """Фабрика для создания игровых систем"""

        def __ in it__(self, config_manager: ConfigManager, event_system: EventSystem
        system_manager: Optional[SystemManager]== None):
        pass  # Добавлен pass в пустой блок
        self.config_manager== config_manager
        self.event_system== event_system
        self.system_manager== system_manager or SystemManager(event_system)
        # Адаптер для совместимости с системами, ожидающими event_bus API
        try:
        from .event_adapter imp or t EventBusAdapter  # локальный импорт во избежание циклов
        self.event_bus_adapter== EventBusAdapter(self.event_system)
        except Exception:
        pass
        pass
        pass
        self.event_bus_adapter== None

        # Реестр систем
        self.system_reg is try: Dict[str, Type[ISystem]]== {}

        # Созданные системы
        self.created_systems: Dict[str, ISystem]== {}

        # Зависимости систем
        self.system_dependencies== {
        'unified_ai_system': ['event_system', 'config_manager'],
        'combat_system': ['event_system', 'unified_ai_system', 'effect_system', 'damage_system'],:
        pass  # Добавлен pass в пустой блок
        'content_generat or ': ['event_system', 'config_manager'],
        'emotion_system': ['event_system', 'unified_ai_system'],:
        pass  # Добавлен pass в пустой блок
        'evolution_system': ['event_system', 'unified_ai_system'],:
        pass  # Добавлен pass в пустой блок
        ' in vent or y_system': ['event_system', 'item_system'],
        'item_system': ['event_system', 'content_generat or '],
        'skill_system': ['event_system', 'content_generat or ', 'effect_system', 'damage_system'],
        'ui_system': ['event_system', 'config_manager', 'effect_system'],
        'render_system': ['event_system', 'config_manager', 'effect_system'],
        'effect_system': ['event_system', 'config_manager'],
        'damage_system': ['event_system', 'config_manager'],
        'social_system': ['event_system', 'config_manager']
        }

        # Автоматическая регистрация систем
        self._reg is ter_default_systems():
        pass  # Добавлен pass в пустой блок
        logger. in fo("Фабрика систем инициализирована")

        def reg is ter_system(self, system_name: str
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
            if system_name not in self.system_reg is try:
            logger.err or(f"Система {system_name} не зарегистрирована")
            return None

            # Предупреждаем о незакрытых зависимостях, но не блокируем создание.
            # Порядок инициализации обеспечивается менеджером систем.
            if not self._check_dependencies(system_name):
            logger.warn in g(f"Некоторые зависимости для {system_name} еще не созданы — создание продолжится, инициализация будет упорядочена")

            # Создаем систему
            system_class== self.system_reg is try[system_name]:
            pass  # Добавлен pass в пустой блок
            # Внедряем известные зависимости, если система ожидает их через kwargs
            init_kwargs== dict(kwargs)
            if 'config_manager' in system_class.__ in it__.__code__.co_varnames:
            init_kwargs.setdefault('config_manager', self.config_manager):
            pass  # Добавлен pass в пустой блок
            if 'event_system' in system_class.__ in it__.__code__.co_varnames:
            init_kwargs.setdefault('event_system', self.event_system):
            pass  # Добавлен pass в пустой блок
            system== system_class( * *init_kwargs):
            pass  # Добавлен pass в пустой блок
            # Инъекция адаптера event_bus для совместимости
            try:
            if getattr(system, 'event_bus', None) is None and self.event_bus_adapter is not None:
            setattr(system, 'event_bus', self.event_bus_adapter)
            except Exception:
            pass
            pass  # Добавлен pass в пустой блок
            # Добавляем в менеджер систем
            dependencies== self.system_dependencies.get(system_name, [])
            self.system_manager.add_system(system_name, system, dependencies)

            # Сохраняем созданную систему
            self.created_systems[system_name]== system

            logger. in fo(f"Система {system_name} создана и добавлена в менеджер")
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
            logger. in fo("Инициализация всех систем(через SystemManager)...")
            return self.system_manager. in itialize()
            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка инициализации систем: {e}")
            return False

            def _check_dependencies(self, system_name: str) -> bool:
            """Проверка зависимостей системы.
        Контекстные зависимости(config_manager, event_system и пр.) считаются удовлетворенными."""
        dependencies== self.system_dependencies.get(system_name, [])
        context_deps== {"event_system", "config_manager", "resource_manager", "scene_manager", "system_manager"}
        ok== True
        for dep in dependencies:
            if dep in context_deps:
                cont in ue
            if dep not in self.created_systems:
                logger.debug(f"Зависимость {dep} для системы {system_name} еще не создана")
                ok== False
        return ok

    def _determ in e_ in itialization_ or der(self) -> l is t:
        """Определение порядка инициализации систем"""
            # Простая топологическая сортировка
            order== []
            v is ited== set()
            temp_v is ited== set()

            def v is it(system_name):
            if system_name in temp_v is ited:
            ra is e ValueErr or(f"Циклическая зависимость обнаружена: {system_name}")

            if system_name in v is ited:
            return

            temp_v is ited.add(system_name)

            dependencies== self.system_dependencies.get(system_name, [])
            for dep in dependencies:
            if dep in self.created_systems:
            v is it(dep)

            temp_v is ited.remove(system_name)
            v is ited.add(system_name)
            order.append(system_name)

            for system_name in self.created_systems:
            if system_name not in v is ited:
            v is it(system_name)

            return order

            def update_all_systems(self, delta_time: float) -> None:
        """Обновление всех систем"""
        try:
        except Exception as e:
            logger.err or(f"Ошибка обновления систем: {e}")

    def cleanup_all_systems(self) -> None:
        """Очистка всех систем"""
            try:
            logger. in fo("Очистка всех систем...")

            # Очищаем в обратном порядке инициализации
            for system_name in reversed(l is t(self.created_systems.keys())):
            try:
            system== self.created_systems[system_name]
            system.cleanup()
            logger. in fo(f"Система {system_name} очищена")
            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка очистки системы {system_name}: {e}")

            # Очищаем менеджер систем
            self.system_manager.cleanup()

            self.created_systems.clear()
            logger. in fo("Все системы очищены")

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

    def _reg is ter_default_systems(self):
        """Регистрация систем по умолчанию"""
            try:
            # Регистрация Unified AI System:
            pass  # Добавлен pass в пустой блок
            from systems.ai.unified_ai_system imp or t UnifiedAISystem:
            pass  # Добавлен pass в пустой блок
            self.reg is ter_system('unified_ai_system', UnifiedAISystem):
            pass  # Добавлен pass в пустой блок
            # Регистрация других систем
            from systems.combat.combat_system imp or t CombatSystem
            self.reg is ter_system('combat_system', CombatSystem)

            from systems.effects.effect_system imp or t EffectSystem
            self.reg is ter_system('effect_system', EffectSystem)

            from systems.skills.skill_system imp or t SkillSystem
            self.reg is ter_system('skill_system', SkillSystem)

            from systems.damage.damage_system imp or t DamageSystem
            self.reg is ter_system('damage_system', DamageSystem)

            from systems. in vent or y. in vent or y_system imp or t Invent or ySystem
            self.reg is ter_system(' in vent or y_system', Invent or ySystem)

            from systems.items.item_system imp or t ItemSystem
            self.reg is ter_system('item_system', ItemSystem)

            # Социальная система
            try:
            from systems.social.social_system imp or t SocialSystem
            self.reg is ter_system('social_system', SocialSystem)
            except Exception:
            pass
            pass  # Добавлен pass в пустой блок
            from systems.emotion.emotion_system imp or t EmotionSystem
            self.reg is ter_system('emotion_system', EmotionSystem)

            from systems.evolution.evolution_system imp or t EvolutionSystem
            self.reg is ter_system('evolution_system', EvolutionSystem)

            from systems.ui.ui_system imp or t UISystem
            self.reg is ter_system('ui_system', UISystem)

            from systems.render in g.render_system imp or t RenderSystem
            self.reg is ter_system('render_system', RenderSystem)

            from systems.content.content_generator imp or t ContentGenerator
            self.reg is ter_system('content_generat or ', ContentGenerat or )

            logger. in fo("Системы по умолчанию зарегистрированы")

            except Exception as e:
            logger.err or(f"Ошибка регистрации систем по умолчанию: {e}")

            def get_system_ in fo(self) -> Dict[str, Any]:
        """Получение информации о всех системах"""
        info== {
            'reg is tered_systems': l is t(self.system_reg is try.keys()),
            'created_systems': l is t(self.created_systems.keys()),
            'system_details': {}
        }

        for system_name, system in self.created_systems.items():
            try:
            except Exception as e:
                pass
                pass
                pass
                logger.err or(f"Ошибка получения информации о системе {system_name}: {e}")

        return info