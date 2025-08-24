#!/usr/bin/env python3
"""
Фабрика систем - создание и управление игровыми системами
"""

import importlib
import logging
from typing import Dict, List, Optional, Type, Any
from .interfaces import ISystem, SystemPriority, SystemState

logger = logging.getLogger(__name__)

class SystemFactory:
    """Фабрика для создания и управления игровыми системами"""
    
    def __init__(self):
        self.registered_systems: Dict[str, Type[ISystem]] = {}
        self.system_instances: Dict[str, ISystem] = {}
        self.system_configs: Dict[str, Dict[str, Any]] = {}
        
        # Стандартные пути к системам
        self.system_paths = {
            'render': 'src.systems.rendering.render_system.RenderSystem',
            'ui': 'src.systems.ui.ui_system.UISystem',
            'ai': 'src.systems.ai.ai_system.AISystem',
            'pytorch_ai': 'src.systems.ai.pytorch_ai_system.PyTorchAISystem',
            'combat': 'src.systems.combat.combat_system.CombatSystem',
            'content_database': 'src.systems.content.content_database.ContentDatabase',
            'content_generator': 'src.systems.content.content_generator.ContentGenerator',
            'ai_integration': 'src.systems.ai.ai_integration_system.AIIntegrationSystem',
            'entity_stats': 'src.systems.entity.entity_stats_system.EntityStatsSystem',
            'evolution': 'src.systems.evolution.evolution_system.EvolutionSystem',
            'genome': 'src.systems.genome.genome_system.GenomeSystem',
            'emotion': 'src.systems.emotion.emotion_system.EmotionSystem',
            'skills': 'src.systems.skills.skill_system.SkillSystem',
            'effects': 'src.systems.effects.effect_system.EffectSystem',
            'items': 'src.systems.items.item_system.ItemSystem',
            'inventory': 'src.systems.inventory.inventory_system.InventorySystem',
            'crafting': 'src.systems.crafting.crafting_system.CraftingSystem'
        }
        
        logger.info("Фабрика систем инициализирована")
    
    def register_system(self, system_name: str, system_class: Type[ISystem]) -> bool:
        """Регистрация системы в фабрике"""
        try:
            if not issubclass(system_class, ISystem):
                logger.warning(f"⚠️ Класс {system_class.__name__} не является системой ISystem")
                return False
            
            self.registered_systems[system_name] = system_class
            logger.info(f"✅ Система {system_name} зарегистрирована: {system_class.__name__}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка регистрации системы {system_name}: {e}")
            return False
    
    def auto_discover_systems(self) -> bool:
        """Автоматическое обнаружение и регистрация систем"""
        logger.info("🔍 Автоматическое обнаружение систем...")
        
        discovered_count = 0
        
        for system_name, system_path in self.system_paths.items():
            try:
                # Разбиваем путь на модуль и класс
                module_path, class_name = system_path.rsplit('.', 1)
                
                # Импортируем модуль
                module = importlib.import_module(module_path)
                
                # Получаем класс системы
                system_class = getattr(module, class_name, None)
                
                if system_class is None:
                    logger.warning(f"📁 Класс {class_name} не найден в {module_path}")
                    continue
                
                # Регистрируем систему
                if self.register_system(system_name, system_class):
                    discovered_count += 1
                
            except ImportError as e:
                logger.warning(f"📁 Модуль {module_path} не найден: {e}")
            except Exception as e:
                logger.error(f"❌ Ошибка обнаружения системы {system_name}: {e}")
        
        logger.info(f"📊 Обнаружено и зарегистрировано {discovered_count} систем")
        return discovered_count > 0
    
    def create_system(self, system_name: str, **kwargs) -> Optional[ISystem]:
        """Создание экземпляра системы"""
        try:
            if system_name not in self.registered_systems:
                logger.error(f"❌ Система {system_name} не зарегистрирована")
                return None
            
            system_class = self.registered_systems[system_name]
            system_instance = system_class(**kwargs)
            
            # Устанавливаем базовые свойства
            if hasattr(system_instance, '_system_state'):
                system_instance._system_state = SystemState.INITIALIZING
            
            self.system_instances[system_name] = system_instance
            logger.info(f"✅ Создан экземпляр системы {system_name}")
            return system_instance
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания системы {system_name}: {e}")
            return None
    
    def get_system(self, system_name: str) -> Optional[ISystem]:
        """Получение системы по имени"""
        return self.system_instances.get(system_name)
    
    def get_registered_systems(self) -> List[str]:
        """Получение списка зарегистрированных систем"""
        return list(self.registered_systems.keys())
    
    def get_system_info(self, system_name: str) -> Optional[Dict[str, Any]]:
        """Получение информации о системе"""
        if system_name not in self.registered_systems:
            return None
        
        system_class = self.registered_systems[system_name]
        system_instance = self.system_instances.get(system_name)
        
        info = {
            'name': system_name,
            'class': system_class.__name__,
            'module': system_class.__module__,
            'registered': True,
            'instantiated': system_instance is not None
        }
        
        if system_instance:
            info.update({
                'state': getattr(system_instance, 'system_state', SystemState.UNINITIALIZED),
                'priority': getattr(system_instance, 'system_priority', SystemPriority.NORMAL),
                'dependencies': getattr(system_instance, 'dependencies', [])
            })
        
        return info
    
    def create_standard_systems(self) -> Dict[str, ISystem]:
        """Создание стандартного набора систем"""
        logger.info("Создание стандартного набора систем...")
        
        created_systems = {}
        
        # Создаем системы в порядке приоритета
        priority_order = [
            SystemPriority.CRITICAL,
            SystemPriority.HIGH,
            SystemPriority.NORMAL,
            SystemPriority.LOW,
            SystemPriority.BACKGROUND
        ]
        
        for priority in priority_order:
            for system_name in self.registered_systems:
                try:
                    system_class = self.registered_systems[system_name]
                    
                    # Проверяем приоритет системы
                    if hasattr(system_class, 'system_priority'):
                        if system_class.system_priority != priority:
                            continue
                    
                    # Создаем систему
                    system_instance = self.create_system(system_name)
                    if system_instance:
                        created_systems[system_name] = system_instance
                        logger.info(f"✅ Система {system_name} создана")
                    else:
                        logger.error(f"❌ Система {system_name} не создана")
                        
                except Exception as e:
                    logger.error(f"❌ Ошибка создания системы {system_name}: {e}")
        
        logger.info(f"Создано {len(created_systems)} систем")
        return created_systems
    
    def initialize_all_systems(self) -> bool:
        """Инициализация всех созданных систем"""
        logger.info("Инициализация всех систем...")
        
        success_count = 0
        total_count = len(self.system_instances)
        
        for system_name, system_instance in self.system_instances.items():
            try:
                if system_instance.initialize():
                    success_count += 1
                    logger.info(f"✅ Система {system_name} инициализирована")
                else:
                    logger.error(f"❌ Система {system_name} не инициализирована")
                    
            except Exception as e:
                logger.error(f"❌ Ошибка инициализации системы {system_name}: {e}")
        
        logger.info(f"Инициализировано {success_count}/{total_count} систем")
        return success_count == total_count
    
    def update_all_systems(self, delta_time: float) -> bool:
        """Обновление всех систем"""
        success_count = 0
        total_count = len(self.system_instances)
        
        for system_name, system_instance in self.system_instances.items():
            try:
                if system_instance.update(delta_time):
                    success_count += 1
                else:
                    logger.warning(f"⚠️ Система {system_name} не обновилась")
                    
            except Exception as e:
                logger.error(f"❌ Ошибка обновления системы {system_name}: {e}")
        
        return success_count == total_count
    
    def cleanup_all_systems(self) -> bool:
        """Очистка всех систем"""
        logger.info("Очистка всех систем...")
        
        success_count = 0
        total_count = len(self.system_instances)
        
        for system_name, system_instance in self.system_instances.items():
            try:
                if system_instance.cleanup():
                    success_count += 1
                    logger.info(f"✅ Система {system_name} очищена")
                else:
                    logger.warning(f"⚠️ Система {system_name} не очищена")
                    
            except Exception as e:
                logger.error(f"❌ Ошибка очистки системы {system_name}: {e}")
        
        # Очищаем словари
        self.system_instances.clear()
        
        logger.info(f"Очищено {success_count}/{total_count} систем")
        return success_count == total_count
    
    def destroy_all_systems(self) -> None:
        """Уничтожение всех систем"""
        logger.info("Уничтожение всех систем...")
        
        for system_name in list(self.system_instances.keys()):
            try:
                system_instance = self.system_instances[system_name]
                system_instance.cleanup()
                del self.system_instances[system_name]
                logger.debug(f"Система {system_name} уничтожена")
                
            except Exception as e:
                logger.error(f"❌ Ошибка уничтожения системы {system_name}: {e}")
        
        logger.info("Все системы уничтожены")
    
    def cleanup(self) -> None:
        """Очистка фабрики систем"""
        logger.info("Очистка фабрики систем...")
        
        self.destroy_all_systems()
        self.registered_systems.clear()
        self.system_configs.clear()
        
        logger.info("Фабрика систем очищена")
    
    def __del__(self):
        """Деструктор"""
        self.cleanup()
