#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ГЛАВНЫЙ ФАЙЛ ИГРЫ
Использует новые унифицированные системы
"""

import sys
import os
from direct.showbase.ShowBase import ShowBase

# Импорты систем состояний (совместимых с экранами)
from game_states import GameStateManager
from core.config_manager import ConfigManager, ConfigCategory
from core.save_system import SaveSystem, SaveType
from core.audio_system import AudioSystem, AudioType
from core.achievement_system import AchievementSystem, AchievementType
from core.event_system import EventSystem, EventPriority, EventType
from core.resource_manager import ResourceManager, ResourceType
from core.roguelike_content_generator import RoguelikeContentGenerator
from core.enhanced_ai_memory import EnhancedAIMemorySystem
from core.enhanced_item_system import EnhancedItemSystem
from core.lighthouse_system import LighthouseSystem
from core.enemy_behavior_system import EnemyBehaviorSystem
from entities.character_manager import CharacterManager

# Импорты экранов
from screens.start_screen import StartScreen
from screens.pause_screen import PauseScreen
from screens.settings_screen import SettingsScreen
from screens.death_screen import DeathScreen
from game_scene_new import GameScene

# Утилиты
from utils.logging_system import initialize_logging, get_logger, log_system_event

class Game(ShowBase):
    """Главный класс игры с унифицированными системами"""
    
    def __init__(self):
        ShowBase.__init__(self)
        
        # Инициализация системы логирования
        self.logger = initialize_logging("logs", "INFO")
        log_system_event("main", "game_started")
        
        # Инициализация менеджеров
        self.config_manager = ConfigManager()
        self.state_manager = GameStateManager()
        self.character_manager = CharacterManager(self)
        
        # Инициализация систем сохранения и контента
        self.save_system = SaveSystem()
        self.audio_system = AudioSystem()
        self.achievement_system = AchievementSystem()
        self.event_system = EventSystem()
        self.resource_manager = ResourceManager()
        
        # Инициализация роглайк систем
        self.content_generator = RoguelikeContentGenerator()
        self.ai_memory_system = EnhancedAIMemorySystem()
        self.item_system = EnhancedItemSystem()
        self.lighthouse_system = LighthouseSystem()
        self.enemy_behavior_system = EnemyBehaviorSystem()
        
        # Текущая сессия
        self.current_session_id = None
        self.current_session_content = None
        
        # Настройка окна из конфигурации
        self._setup_window()
        
        # Создание экранов
        self.start_screen = StartScreen(self)
        self.pause_screen = PauseScreen(self)
        self.settings_screen = SettingsScreen(self)
        self.death_screen = DeathScreen(self)
        self.game_scene = GameScene(self)
        
        # Регистрация состояний
        self.state_manager.add_state("start", self.start_screen)
        self.state_manager.add_state("game", self.game_scene)
        self.state_manager.add_state("pause", self.pause_screen)
        self.state_manager.add_state("settings", self.settings_screen)
        self.state_manager.add_state("death", self.death_screen)
        
        # Установка начального состояния
        self.state_manager.change_state("start")
        
        # Настройка клавиатуры
        self.accept("escape", self.toggle_pause)
        self.accept("f1", self.toggle_settings)
        
        # Регистрация callbacks для состояний (не используется в legacy менеджере)
        # Оставлено для будущей интеграции расширенных состояний
    
    def _setup_window(self):
        """Настройка окна из конфигурации"""
        width = self.config_manager.get("window_width", 1920)
        height = self.config_manager.get("window_height", 1080)
        fullscreen = self.config_manager.get("fullscreen", False)
        vsync = self.config_manager.get("vsync", True)
        
        # Настройка окна
        self.setFrameRateMeter(self.config_manager.get("show_fps", False))
        self.setBackgroundColor(0.1, 0.1, 0.1, 1)
        
        # Настройка размеров окна
        if fullscreen:
            # Для Panda3D создаем новые свойства окна
            from panda3d.core import WindowProperties
            props = WindowProperties()
            props.setFullscreen(True)
            self.win.requestProperties(props)
        else:
            from panda3d.core import WindowProperties
            props = WindowProperties()
            props.setFullscreen(False)
            props.setSize(width, height)
            self.win.requestProperties(props)
        
        # Настройка VSync
        # В некоторых версиях Panda3D VSync управляется через конфиг-переменную
        # 'sync-video' и не поддерживается через WindowProperties.
        try:
            if vsync:
                from panda3d.core import ConfigVariableBool
                ConfigVariableBool('sync-video').set_value(True)
            else:
                from panda3d.core import ConfigVariableBool
                ConfigVariableBool('sync-video').set_value(False)
        except Exception:
            # Безопасно игнорируем, если платформа/версия не поддерживает динамическое изменение
            pass
    
    # Зарезервировано под расширенные callbacks при переходе на core.game_state_manager
    
    def toggle_pause(self):
        """Переключение паузы"""
        if self.state_manager.current_state == "game":
            self.state_manager.change_state("pause")
        elif self.state_manager.current_state == "pause":
            self.state_manager.change_state("game")
    
    def toggle_settings(self):
        """Переключение настроек"""
        if self.state_manager.current_state == "settings":
            # Возвращаемся к предыдущему состоянию
            if self.state_manager.previous_state:
                self.state_manager.change_state(self.state_manager.previous_state)
            else:
                self.state_manager.change_state("start")
        else:
            self.state_manager.change_state("settings")
    
    def start_new_roguelike_session(self, difficulty_level: int = 1) -> str:
        """Начало новой роглайк сессии"""
        import uuid
        import time
        
        # Генерируем ID сессии
        session_id = f"session_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        # Генерируем контент для сессии
        self.current_session_content = self.content_generator.generate_session_content(
            session_id, difficulty_level
        )
        
        self.current_session_id = session_id
        
        # Инициализируем память ИИ для сессии
        from core.enhanced_ai_memory import EntityType
        self.ai_memory_system.initialize_entity_memory("player", EntityType.PLAYER)
        
        # Генерируем маяк для сессии
        self.lighthouse_system.generate_lighthouse_for_session(session_id, difficulty_level)
        
        log_system_event("main", "roguelike_session_started", {
            "session_id": session_id,
            "difficulty_level": difficulty_level
        })
        
        return session_id
    
    def save_roguelike_session(self) -> bool:
        """Сохранение текущей роглайк сессии"""
        if not self.current_session_id or not self.current_session_content:
            return False
        
        try:
            # Получаем данные игрока
            player_data = self._get_player_data()
            
            # Получаем состояние игры
            game_state = self._get_game_state()
            
            # Получаем данные мира
            world_data = self._get_world_data()
            
            # Получаем данные памяти ИИ
            ai_memory_data = self.ai_memory_system.save_memory_data(self.current_session_id)
            
            # Получаем данные сгенерированного контента
            generated_content = self._get_generated_content_data()
            
            # Получаем данные памяти врагов
            enemy_memory_bank = self._get_enemy_memory_data()
            
            # Получаем данные памяти игрока
            player_memory = self._get_player_memory_data()
            
            # Создаем сохранение
            save_id = self.save_system.create_roguelike_save(
                session_id=self.current_session_id,
                player_data=player_data,
                game_state=game_state,
                world_data=world_data,
                ai_memory_data=ai_memory_data,
                generated_content=generated_content,
                enemy_memory_bank=enemy_memory_bank,
                player_memory=player_memory
            )
            
            # Сохраняем данные предметов и маяков отдельно
            if save_id:
                self.item_system.save_item_data(self.current_session_id)
                self.lighthouse_system.save_lighthouse_data(self.current_session_id)
            
            if save_id:
                log_system_event("main", "roguelike_session_saved", {
                    "session_id": self.current_session_id,
                    "save_id": save_id
                })
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error saving roguelike session: {e}")
            return False
    
    def _get_player_data(self) -> dict:
        """Получение данных игрока для сохранения"""
        if hasattr(self, 'game_scene') and hasattr(self.game_scene, 'player'):
            player = self.game_scene.player
            return {
                "name": getattr(player, 'name', 'Player'),
                "level": getattr(player, 'level', 1),
                "health": getattr(player, 'health', 100),
                "max_health": getattr(player, 'max_health', 100),
                "mana": getattr(player, 'mana', 50),
                "max_mana": getattr(player, 'max_mana', 50),
                "position": getattr(player, 'position', [0, 0, 0]),
                "inventory": getattr(player, 'inventory', {}),
                "skills": getattr(player, 'skills', {}),
                "experience": getattr(player, 'experience', 0)
            }
        return {}
    
    def _get_game_state(self) -> dict:
        """Получение состояния игры для сохранения"""
        import time
        return {
            "current_time": time.time(),
            "game_mode": "roguelike",
            "difficulty_level": getattr(self, 'difficulty_level', 1),
            "session_id": self.current_session_id
        }
    
    def _get_world_data(self) -> dict:
        """Получение данных мира для сохранения"""
        if hasattr(self, 'game_scene'):
            return {
                "current_location": getattr(self.game_scene, 'current_location', 'unknown'),
                "lighthouse_found": getattr(self.game_scene, 'lighthouse_found', False),
                "lighthouse_location": getattr(self.current_session_content, 'lighthouse_location', [0, 0, 0])
            }
        return {}
    
    def _get_generated_content_data(self) -> dict:
        """Получение данных сгенерированного контента"""
        if self.current_session_content:
            return {
                "items": {item_id: {
                    "item_id": item.item_id,
                    "name": item.name,
                    "item_type": item.item_type,
                    "rarity": item.rarity.value,
                    "base_stats": item.base_stats,
                    "special_effects": item.special_effects,
                    "active_skills": item.active_skills,
                    "trigger_skills": item.trigger_skills,
                    "basic_attack_skill": item.basic_attack_skill,
                    "requirements": item.requirements,
                    "description": item.description
                } for item_id, item in self.current_session_content.items.items()},
                "enemies": {enemy_id: {
                    "enemy_id": enemy.enemy_id,
                    "name": enemy.name,
                    "enemy_type": enemy.enemy_type.value,
                    "base_stats": enemy.base_stats,
                    "resistances": enemy.resistances,
                    "weaknesses": enemy.weaknesses,
                    "skill_set": enemy.skill_set,
                    "ai_behavior": enemy.ai_behavior,
                    "learning_rate": enemy.learning_rate,
                    "phases": enemy.phases,
                    "loot_table": enemy.loot_table
                } for enemy_id, enemy in self.current_session_content.enemies.items()},
                "skills": {skill_id: {
                    "skill_id": skill.skill_id,
                    "name": skill.name,
                    "skill_type": skill.skill_type,
                    "description": skill.description,
                    "effects": skill.effects,
                    "cooldown": skill.cooldown,
                    "mana_cost": skill.mana_cost,
                    "requirements": skill.requirements
                } for skill_id, skill in self.current_session_content.skills.items()},
                "lighthouse_location": self.current_session_content.lighthouse_location
            }
        return {}
    
    def _get_enemy_memory_data(self) -> dict:
        """Получение данных памяти врагов"""
        return {
            "shared_memories": [
                {
                    "memory_id": m.memory_id,
                    "memory_type": m.memory_type.value,
                    "data": m.data,
                    "importance": m.importance,
                    "timestamp": m.timestamp
                }
                for m in self.ai_memory_system.shared_enemy_memory.shared_memories
            ],
            "total_learning_experience": self.ai_memory_system.shared_enemy_memory.total_learning_experience,
            "evolution_level": self.ai_memory_system.shared_enemy_memory.evolution_level
        }
    
    def _get_player_memory_data(self) -> dict:
        """Получение данных памяти игрока"""
        if "player" in self.ai_memory_system.entity_memories:
            player_memory = self.ai_memory_system.entity_memories["player"]
            return {
                "short_term_memories": [
                    {
                        "memory_id": m.memory_id,
                        "memory_type": m.memory_type.value,
                        "data": m.data,
                        "importance": m.importance,
                        "timestamp": m.timestamp
                    }
                    for m in player_memory.short_term_memories
                ],
                "long_term_memories": [
                    {
                        "memory_id": m.memory_id,
                        "memory_type": m.memory_type.value,
                        "data": m.data,
                        "importance": m.importance,
                        "timestamp": m.timestamp
                    }
                    for m in player_memory.long_term_memories
                ],
                "total_experience": player_memory.total_experience,
                "evolution_stage": player_memory.evolution_stage
            }
        return {}

    def cleanup(self):
        """Очистка ресурсов"""
        log_system_event("main", "cleanup_started")
        
        # Сохраняем текущую сессию если она активна
        if hasattr(self, 'current_session_id') and self.current_session_id:
            self.save_roguelike_session()
        
        # Очистка менеджеров
        self.character_manager.cleanup()
        self.state_manager.cleanup()
        self.config_manager.cleanup()
        
        log_system_event("main", "cleanup_completed")

    def quit(self):
        """Корректное завершение игры"""
        try:
            self.cleanup()
        finally:
            # Завершение приложения Panda3D
            self.userExit()

if __name__ == "__main__":
    app = Game()
    app.run()
