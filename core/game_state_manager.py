"""Менеджер состояния игры."""

import json
import os
import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
from enum import Enum

from .component import Component, ComponentManager
from .attributes import AttributesComponent
from .combat_stats import CombatStatsComponent
from .inventory import InventoryComponent
from .transform import TransformComponent
from .skill_system import SkillSystem
from .leveling_system import LevelingSystem
from config.game_constants import (
    PLAYER_START_HEALTH, PLAYER_START_MANA, PLAYER_START_STAMINA,
    ENEMY_BASE_HEALTH, ENEMY_BASE_MANA, ENEMY_BASE_STAMINA,
    BOSS_HEALTH_MULTIPLIER, BOSS_DAMAGE_MULTIPLIER,
    XP_BASE, XP_MULTIPLIER, LEVEL_CAP
)

logger = logging.getLogger(__name__)


@dataclass
class GameSettings:
    """Настройки игры"""
    difficulty: str = "normal"
    learning_rate: float = 1.0
    window_size: List[int] = field(default_factory=lambda: [1200, 800])


@dataclass
class GameStatistics:
    """Статистика игры"""
    reincarnation_count: int = 0
    generation_count: int = 0
    session_start_time: float = 0.0
    enemies_defeated: int = 0
    boss_defeated: bool = False


class GameStateManager:
    """Управляет состоянием игры и всеми игровыми системами"""
    
    def __init__(self, settings: GameSettings):
        self.settings = settings
        self.statistics = GameStatistics()
        self.statistics.session_start_time = time.time()
        
        # Игровые сущности
        self.player: Optional[Component] = None
        self.enemies: List[Component] = []
        self.boss: Optional[Component] = None
        
        # Системы
        self.coordinator: Optional[ComponentManager] = None
        self.ai_scheduler: Optional[ComponentManager] = None
        self.skill_system: Optional[SkillSystem] = None
        self.leveling_system: Optional[LevelingSystem] = None
        
        # AI компоненты
        self.player_ai_memory: Optional[Component] = None
        self.player_learning: Optional[Component] = None
        self.player_decision_maker: Optional[Component] = None
        self.emotion_synthesizer: Optional[Component] = None
        self.pattern_recognizer: Optional[Component] = None
        
        # Пользовательские объекты
        self.user_obstacles: set = set()
        self.chests: List[Dict[str, Any]] = []
        
        # Состояние
        self.victory_shown: bool = False
        self.paused: bool = False
        self.running: bool = True
        
    def initialize_game(self, map_width: int, map_height: int) -> None:
        """Инициализация всех игровых систем"""
        self._create_entities(map_width, map_height)
        self._setup_ai_systems()
        self._setup_coordination()
        self._setup_skills_and_leveling()
        
    def _create_entities(self, map_width: int, map_height: int) -> None:
        """Создание игровых сущностей"""
        from entities.player import Player
        from items.weapon import WeaponGenerator
        
        # Игрок
        start_x = map_width // 2 if map_width > 0 else 600
        start_y = map_height // 2 if map_height > 0 else 400
        self.player = Player("player_ai", (start_x, start_y))
        self.player.learning_rate = self.settings.learning_rate
        
        # Враги
        self.enemies = self._create_enemies(map_width, map_height)
        
        # Босс
        self.boss = self._create_boss(map_width, map_height)
        
        # Стартовое оружие
        if not self.player.equipment.get("weapon"):
            starter_weapon = WeaponGenerator.generate_weapon(1)
            self.player.equip_item(starter_weapon)
            
    def _create_enemies(self, map_width: int, map_height: int) -> List['Enemy']:
        """Создание врагов в зависимости от сложности"""
        import random
        from entities.enemy import Enemy
        
        enemy_list = []
        enemy_types = ["warrior", "archer", "mage"]
        
        # Настройки сложности
        difficulty = self.settings.difficulty
        if difficulty == "easy":
            num_enemies, lvl_min, lvl_max = 6, 1, 3
        elif difficulty == "hard":
            num_enemies, lvl_min, lvl_max = 14, 3, 7
        else:
            num_enemies, lvl_min, lvl_max = 10, 1, 5
            
        for _ in range(num_enemies):
            enemy = Enemy(random.choice(enemy_types), level=random.randint(lvl_min, lvl_max))
            x = random.randint(100, max(200, map_width - 100)) if map_width > 0 else random.randint(100, 1100)
            y = random.randint(100, max(200, map_height - 100)) if map_height > 0 else random.randint(100, 700)
            enemy.position = [x, y]
            enemy.player_ref = self.player
            enemy_list.append(enemy)
            
        return enemy_list
        
    def _create_boss(self, map_width: int, map_height: int) -> 'Boss':
        """Создание босса"""
        import random
        from entities.boss import Boss
        
        if map_width > 0:
            bx = map_width - 300
        else:
            bx = 900
            
        by = 300
        
        difficulty = self.settings.difficulty
        boss_level = 12 if difficulty == "easy" else (20 if difficulty == "hard" else 15)
        
        boss = Boss(boss_type="dragon", level=boss_level, position=(bx, by))
        boss.learning_rate = 0.005
        boss.player_ref = self.player
        
        return boss
        
    def _setup_ai_systems(self) -> None:
        """Настройка AI систем"""
        from ai.cooperation import AICoordinator
        from ai.ai_update_scheduler import AIUpdateScheduler
        from ai.memory import AIMemory
        from ai.learning import PlayerLearning
        from ai.decision_maker import PlayerDecisionMaker
        from ai.emotion_genetics import EmotionGeneticSynthesizer
        from ai.pattern_recognizer import PatternRecognizer
        
        # AI координатор
        self.coordinator = AICoordinator()
        for enemy in self.enemies:
            self.coordinator.register_entity(enemy, "enemy_group")
        if self.boss:
            self.coordinator.register_entity(self.boss, "boss_group")
            
        # AI планировщик
        self.ai_scheduler = AIUpdateScheduler()
        
        # AI для игрока
        self.player_ai_memory = AIMemory()
        self.player_learning = PlayerLearning(self.player, self.player_ai_memory)
        self.player_decision_maker = PlayerDecisionMaker(self.player, self.player_ai_memory)
        
        # Эмоции и паттерны
        self.emotion_synthesizer = EmotionGeneticSynthesizer(self.player, {}, {}, {})
        self.pattern_recognizer = PatternRecognizer()
        
        # Регистрация AI обновлений
        self.ai_scheduler.register_entity(self.player, self.player_learning.update)
        self.ai_scheduler.register_entity(self.player, self.player_decision_maker.update)
        
    def _setup_coordination(self) -> None:
        """Настройка координации между сущностями"""
        pass  # Уже настроено в _setup_ai_systems
        
    def _setup_skills_and_leveling(self) -> None:
        """Настройка системы навыков и уровней"""
        from core.skill_system import SkillSystem
        from core.leveling_system import LevelingSystem
        
        self.skill_system = SkillSystem()
        self.leveling_system = LevelingSystem(self.player)
        
        # Добавление базовых навыков
        self.skill_system.add_skill_to_entity(self.player, "whirlwind_attack")
        self.skill_system.add_skill_to_entity(self.player, "healing_light")
        
    def update(self, delta_time: float) -> None:
        """Обновление всех игровых систем"""
        if self.paused or not self.running:
            return
            
        # Обновление AI
        self._update_ai_systems(delta_time)
        
        # Обновление сущностей
        self._update_entities(delta_time)
        
        # Обновление систем
        self._update_systems(delta_time)
        
        # Проверка состояния
        self._check_game_state()
        
    def _update_ai_systems(self, delta_time: float) -> None:
        """Обновление AI систем"""
        # Обновление AI планировщика
        if self.ai_scheduler:
            self.ai_scheduler.update_all(delta_time)
            
        # Обновление координации
        if self.coordinator:
            self.coordinator.update_group_behavior("enemy_group")
            self.coordinator.update_group_behavior("boss_group")
            
        # Анализ паттернов и эмоций
        if self.pattern_recognizer:
            entities = [self.player] + self.enemies + ([self.boss] if self.boss else [])
            self.pattern_recognizer.analyze_combat_patterns(entities)
            
        if self.emotion_synthesizer:
            self.emotion_synthesizer.update_emotions(delta_time)
            
    def _update_entities(self, delta_time: float) -> None:
        """Обновление игровых сущностей"""
        # Обновление игрока
        if self.player and self.player.alive:
            self.player.update(delta_time)
            
        # Обновление врагов
        for enemy in self.enemies:
            if enemy.alive:
                enemy.update(delta_time)
                
        # Обновление босса
        if self.boss and self.boss.alive:
            self.boss.update(delta_time)
            
    def _update_systems(self, delta_time: float) -> None:
        """Обновление игровых систем"""
        # Обновление навыков
        if self.skill_system:
            self.skill_system.update(delta_time)
            
        # Обновление уровней
        if self.leveling_system:
            self.leveling_system.update(delta_time)
            
    def _check_game_state(self) -> None:
        """Проверка состояния игры"""
        # Проверка победы над врагами
        for enemy in self.enemies[:]:
            if not enemy.alive:
                self._handle_enemy_defeat(enemy)
                
        # Проверка победы над боссом
        if self.boss and not self.boss.alive and not hasattr(self.boss, 'exp_given'):
            self._handle_boss_defeat()
            
        # Проверка смерти игрока
        if self.player and not self.player.alive:
            self._handle_player_death()
            
    def _handle_enemy_defeat(self, enemy: 'Enemy') -> None:
        """Обработка победы над врагом"""
        import random
        
        # Удаление врага из списка
        self.enemies.remove(enemy)
        
        # Награждение опытом
        if self.leveling_system:
            enemy_level = getattr(enemy, 'level', 1)
            exp_gain = enemy_level * 10 + random.randint(5, 15)
            self.leveling_system.gain_experience(exp_gain)
            
        # Запись в память AI
        if self.player_ai_memory:
            enemy_level = getattr(enemy, 'level', 1)
            exp_gain = enemy_level * 10 + random.randint(5, 15)
            self.player_ai_memory.record_event("ENEMY_DEFEATED", {
                "enemy_type": getattr(enemy, 'enemy_type', 'unknown'),
                "enemy_level": enemy_level,
                "exp_gained": exp_gain,
                "player_health": self.player.health if self.player else 0,
                "player_level": self.leveling_system.level if self.leveling_system else 1
            })
            
        # Обновление статистики
        self.statistics.enemies_defeated += 1
        
    def _handle_boss_defeat(self) -> None:
        """Обработка победы над боссом"""
        import random
        
        if not self.boss:
            return
            
        # Награждение опытом
        if self.leveling_system:
            boss_level = getattr(self.boss, 'level', 15)
            exp_gain = boss_level * 50 + random.randint(100, 200)
            self.leveling_system.gain_experience(exp_gain)
            
        # Запись в память AI
        if self.player_ai_memory:
            boss_level = getattr(self.boss, 'level', 15)
            exp_gain = boss_level * 50 + random.randint(100, 200)
            self.player_ai_memory.record_event("BOSS_DEFEATED", {
                "boss_type": getattr(self.boss, 'boss_type', 'unknown'),
                "boss_level": boss_level,
                "exp_gained": exp_gain,
                "player_health": self.player.health if self.player else 0,
                "player_level": self.leveling_system.level if self.leveling_system else 1
            })
            
        # Обновление статистики
        self.statistics.boss_defeated = True
        self.boss.exp_given = True
        
    def _handle_player_death(self) -> None:
        """Обработка смерти игрока"""
        self.statistics.reincarnation_count += 1
        
    def soft_restart(self) -> None:
        """Перезапуск мира без потери знаний"""
        self.victory_shown = False
        self.statistics.generation_count += 1
        
        # Возрождение игрока
        if self.player:
            self._respawn_player()
            
        # Возрождение врагов
        for enemy in self.enemies:
            self._respawn_entity(enemy)
            self._reposition_enemy(enemy)
            
        # Возрождение босса
        if self.boss:
            self._respawn_entity(self.boss)
            self._reposition_boss()
            
    def _respawn_player(self) -> None:
        """Возрождение игрока"""
        if not self.player:
            return
            
        self.player.alive = True
        self.player.health = self.player.max_health
        self.player.learning_rate = min(2.0, self.player.learning_rate * 1.01)
        
        # Перемещение к центру
        if hasattr(self, 'tiled_map') and self.tiled_map:
            map_px_w = self.tiled_map.width * self.tiled_map.tilewidth
            map_px_h = self.tiled_map.height * self.tiled_map.tileheight
            self.player.position = [map_px_w // 2, map_px_h // 2]
        else:
            self.player.position = [600, 400]
            
    def _respawn_entity(self, entity) -> None:
        """Возрождение сущности"""
        entity.alive = True
        entity.health = entity.max_health
        
    def _reposition_enemy(self, enemy: 'Enemy') -> None:
        """Перемещение врага в случайную позицию"""
        import random
        
        if not self.player:
            return
            
        # Получаем размеры карты из позиции игрока
        player_x, player_y = self.player.position
        map_width = max(800, player_x * 2)
        map_height = max(600, player_y * 2)
        
        # Размещаем врага в случайной позиции
        x = random.randint(-map_width//2, map_width//2)
        y = random.randint(-map_height//2, map_height//2)
        enemy.position = [x, y]
        
        # Возрождаем врага
        enemy.alive = True
        enemy.health = enemy.max_health
        
    def _reposition_boss(self) -> None:
        """Перемещение босса в случайную позицию"""
        import random
        
        if not self.boss or not self.player:
            return
            
        # Получаем размеры карты из позиции игрока
        player_x, player_y = self.player.position
        map_width = max(800, player_x * 2)
        
        # Размещаем босса справа от игрока
        x = map_width//2 - 300
        y = 300
        self.boss.position = [x, y]
        
        # Возрождаем босса
        self.boss.alive = True
        self.boss.health = self.boss.max_health
        self.boss.exp_given = False
            
    def save_game(self, save_file: str) -> bool:
        """Сохранение игры"""
        try:
            save_data = {
                "reincarnation_count": self.statistics.reincarnation_count,
                "generation_count": self.statistics.generation_count,
                "session_start_time": self.statistics.session_start_time,
                "player": {
                    "health": self.player.health if self.player else 100,
                    "level": self.player.level if self.player else 1,
                    "learning_rate": self.player.learning_rate if self.player else 1.0,
                    "position": self.player.position if self.player else [600, 400]
                },
                "obstacles": list(self.user_obstacles),
                "chests": self.chests
            }
            
            with open(save_file, "w", encoding="utf-8") as f:
                json.dump(save_data, f, indent=2)
                
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения: {e}")
            return False
            
    def load_game(self, save_file: str) -> bool:
        """Загрузка игры"""
        if not os.path.exists(save_file):
            return False
            
        try:
            with open(save_file, "r", encoding="utf-8") as f:
                save_data = json.load(f)
                
            # Восстановление статистики
            self.statistics.reincarnation_count = save_data.get("reincarnation_count", 0)
            self.statistics.generation_count = save_data.get("generation_count", 0)
            self.statistics.session_start_time = save_data.get("session_start_time", time.time())
            
            # Восстановление игрока
            if "player" in save_data and self.player:
                player_data = save_data["player"]
                self.player.health = player_data.get("health", self.player.max_health)
                self.player.level = player_data.get("level", 1)
                self.player.learning_rate = player_data.get("learning_rate", 1.0)
                self.player.position = player_data.get("position", [600, 400])
                
            # Восстановление препятствий и сундуков
            self.user_obstacles = set(tuple(obs) for obs in save_data.get("obstacles", []))
            self.chests = save_data.get("chests", [])
            
            return True
        except Exception as e:
            logger.error(f"Ошибка загрузки: {e}")
            return False
            
    def get_game_info(self) -> Dict[str, Any]:
        """Получение информации об игре для отображения"""
        info = {
            "player_level": self.leveling_system.level if self.leveling_system else 1,
            "player_health": self.player.health if self.player else 0,
            "player_max_health": self.player.max_health if self.player else 100,
            "enemies_remaining": len([e for e in self.enemies if e.alive]),
            "boss_alive": self.boss.alive if self.boss else False,
            "reincarnation_count": self.statistics.reincarnation_count,
            "generation_count": self.statistics.generation_count,
            "session_time": time.time() - self.statistics.session_start_time,
            "learning_rate": self.player.learning_rate if self.player else 1.0
        }
        
        # Информация об опыте
        if self.leveling_system:
            exp_progress = self.leveling_system.get_leveling_progress()
            info.update({
                "current_exp": exp_progress.get('current_exp', 0),
                "exp_to_next": exp_progress.get('exp_to_next', 100),
                "attribute_points": exp_progress.get('attribute_points', 0)
            })
            
        return info
