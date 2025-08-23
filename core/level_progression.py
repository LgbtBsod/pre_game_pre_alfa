#!/usr/bin/env python3
"""
Система прогрессии уровней
Обрабатывает завершение уровня, отображение статистики и генерацию следующего уровня
"""

import pygame
import json
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from pathlib import Path

from core.content_generator import ContentGenerator
from core.advanced_entity import AdvancedGameEntity
from core.genetic_system import AdvancedGeneticSystem
from core.emotion_system import AdvancedEmotionSystem
from core.ai_system import AdaptiveAISystem
from core.effect_system import EffectDatabase

logger = logging.getLogger(__name__)


class LevelState(Enum):
    """Состояния уровня"""
    PLAYING = "playing"
    COMPLETED = "completed"
    STATISTICS = "statistics"
    NEXT_LEVEL = "next_level"


@dataclass
class LevelStatistics:
    """Статистика уровня"""
    level_number: int
    completion_time: float
    enemies_defeated: int
    items_collected: int
    beacons_found: int
    genetic_mutations: int
    emotional_changes: int
    ai_learning_progress: float
    total_damage_dealt: float
    total_damage_taken: float
    distance_traveled: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для сохранения"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LevelStatistics':
        """Создание из словаря"""
        return cls(**data)


class LevelProgressionSystem:
    """Система прогрессии уровней"""
    
    def __init__(self, content_generator: ContentGenerator, effect_db: EffectDatabase):
        self.content_generator = content_generator
        self.effect_db = effect_db
        self.current_level = 1
        self.level_state = LevelState.PLAYING
        self.level_start_time = time.time()
        self.level_statistics = LevelStatistics(
            level_number=1,
            completion_time=0.0,
            enemies_defeated=0,
            items_collected=0,
            beacons_found=0,
            genetic_mutations=0,
            emotional_changes=0,
            ai_learning_progress=0.0,
            total_damage_dealt=0.0,
            total_damage_taken=0.0,
            distance_traveled=0.0
        )
        self.level_state = LevelState.PLAYING
        self.statistics_display_time = 0
        self.statistics_display_duration = 5.0  # Секунды показа статистики
        
    def start_level(self, level_number: int):
        """Начало нового уровня"""
        self.current_level = level_number
        self.level_start_time = time.time()
        self.level_state = LevelState.PLAYING
        
        # Сброс статистики
        self.level_statistics = LevelStatistics(
            level_number=level_number,
            completion_time=0.0,
            enemies_defeated=0,
            items_collected=0,
            beacons_found=0,
            genetic_mutations=0,
            emotional_changes=0,
            ai_learning_progress=0.0,
            total_damage_dealt=0.0,
            total_damage_taken=0.0,
            distance_traveled=0.0
        )
        
        logger.info(f"Начат уровень {level_number}")
    
    def on_beacon_found(self, player: AdvancedGameEntity):
        """Обработка обнаружения маяка"""
        if self.level_state == LevelState.PLAYING:
            self.level_statistics.beacons_found += 1
            self.complete_level(player)
    
    def complete_level(self, player: AdvancedGameEntity):
        """Завершение уровня"""
        if self.level_state != LevelState.PLAYING:
            return
        
        # Обновляем статистику
        self.level_statistics.completion_time = time.time() - self.level_start_time
        
        # Получаем статистику игрока
        if hasattr(player, 'ai_system') and player.ai_system:
            self.level_statistics.ai_learning_progress = getattr(player.ai_system, 'learning_level', 1)
        
        if hasattr(player, 'genetic_system') and player.genetic_system:
            self.level_statistics.genetic_mutations = getattr(player.genetic_system, 'mutation_count', 0)
        
        if hasattr(player, 'emotion_system') and player.emotion_system:
            emotions = player.emotion_system.get_all_emotions()
            self.level_statistics.emotional_changes = len(emotions)
        
        # Переходим к показу статистики
        self.level_state = LevelState.STATISTICS
        self.statistics_display_time = time.time()
        
        logger.info(f"Уровень {self.current_level} завершен за {self.level_statistics.completion_time:.2f} секунд")
    
    def update(self, delta_time: float):
        """Обновление системы прогрессии"""
        if self.level_state == LevelState.STATISTICS:
            if time.time() - self.statistics_display_time >= self.statistics_display_duration:
                self.level_state = LevelState.NEXT_LEVEL
    
    def generate_next_level(self, player: AdvancedGameEntity) -> Dict[str, Any]:
        """Генерация следующего уровня"""
        next_level_number = self.current_level + 1
        
        # Сохраняем прогресс игрока
        player_data = self._save_player_progress(player)
        
        # Генерируем новый уровень с повышенной сложностью
        level_config = {
            "level_number": next_level_number,
            "difficulty_multiplier": 1.0 + (next_level_number - 1) * 0.2,  # Увеличиваем сложность
            "world_size": 1000 + (next_level_number - 1) * 50,  # Увеличиваем размер мира
            "enemy_count": 5 + (next_level_number - 1) * 2,  # Больше врагов
            "item_count": 10 + (next_level_number - 1) * 3,  # Больше предметов
            "obstacle_count": 3 + (next_level_number - 1),  # Больше препятствий
            "player_data": player_data
        }
        
        # Генерируем контент для нового уровня
        generated_content = self.content_generator.generate_level_content(level_config)
        
        logger.info(f"Сгенерирован уровень {next_level_number}")
        return generated_content
    
    def _save_player_progress(self, player: AdvancedGameEntity) -> Dict[str, Any]:
        """Сохранение прогресса игрока"""
        player_data = {
            "position": {
                "x": player.position.x,
                "y": player.position.y,
                "z": player.position.z
            },
            "stats": {
                "health": player.stats.health,
                "max_health": player.stats.max_health,
                "mana": player.stats.mana,
                "max_mana": player.stats.max_mana,
                "stamina": player.stats.stamina,
                "max_stamina": player.stats.max_stamina,
                "speed": player.stats.speed,
                "strength": player.stats.strength,
                "intelligence": player.stats.intelligence,
                "agility": player.stats.agility
            },
            "inventory": player.inventory.get_all_items() if hasattr(player, 'inventory') else [],
            "genes": player.genetic_system.get_active_genes() if hasattr(player, 'genetic_system') else [],
            "emotions": player.emotion_system.get_all_emotions() if hasattr(player, 'emotion_system') else {},
            "ai_learning": {
                "level": getattr(player.ai_system, 'learning_level', 1) if hasattr(player, 'ai_system') else 1,
                "experience": getattr(player.ai_system, 'experience_points', 0) if hasattr(player, 'ai_system') else 0
            }
        }
        
        return player_data
    
    def get_statistics(self) -> LevelStatistics:
        """Получение статистики текущего уровня"""
        return self.level_statistics
    
    def get_level_state(self) -> LevelState:
        """Получение состояния уровня"""
        return self.level_state


class StatisticsRenderer:
    """Отрисовщик статистики уровня"""
    
    def __init__(self, screen: pygame.Surface, font: pygame.font.Font):
        self.screen = screen
        self.font = font
        self.title_font = pygame.font.Font(None, 48)
        self.subtitle_font = pygame.font.Font(None, 32)
        
    def render_statistics(self, statistics: LevelStatistics):
        """Отрисовка статистики уровня"""
        screen_width, screen_height = self.screen.get_size()
        
        # Фон
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Заголовок
        title_text = f"Уровень {statistics.level_number} Завершен!"
        title_surface = self.title_font.render(title_text, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(screen_width // 2, 100))
        self.screen.blit(title_surface, title_rect)
        
        # Статистика
        stats_y = 200
        line_height = 40
        
        stats_items = [
            ("Время прохождения", f"{statistics.completion_time:.1f} сек"),
            ("Побеждено врагов", str(statistics.enemies_defeated)),
            ("Собрано предметов", str(statistics.items_collected)),
            ("Найдено маяков", str(statistics.beacons_found)),
            ("Генетических мутаций", str(statistics.genetic_mutations)),
            ("Эмоциональных изменений", str(statistics.emotional_changes)),
            ("Уровень обучения ИИ", f"{statistics.ai_learning_progress:.1f}"),
            ("Нанесено урона", f"{statistics.total_damage_dealt:.0f}"),
            ("Получено урона", f"{statistics.total_damage_taken:.0f}"),
            ("Пройдено расстояния", f"{statistics.distance_traveled:.0f}")
        ]
        
        for label, value in stats_items:
            # Метка
            label_surface = self.font.render(label, True, (200, 200, 200))
            label_rect = label_surface.get_rect(x=screen_width // 2 - 200, y=stats_y)
            self.screen.blit(label_surface, label_rect)
            
            # Значение
            value_surface = self.font.render(value, True, (255, 255, 255))
            value_rect = value_surface.get_rect(x=screen_width // 2 + 50, y=stats_y)
            self.screen.blit(value_surface, value_rect)
            
            stats_y += line_height
        
        # Инструкции
        instruction_text = "Нажмите ПРОБЕЛ для перехода на следующий уровень или S для сохранения"
        instruction_surface = self.font.render(instruction_text, True, (150, 255, 150))
        instruction_rect = instruction_surface.get_rect(center=(screen_width // 2, screen_height - 100))
        self.screen.blit(instruction_surface, instruction_rect)


class LevelTransitionManager:
    """Менеджер переходов между уровнями"""
    
    def __init__(self, progression_system: LevelProgressionSystem, statistics_renderer: StatisticsRenderer):
        self.progression_system = progression_system
        self.statistics_renderer = statistics_renderer
        self.transition_alpha = 0
        self.transition_speed = 2.0  # Скорость перехода
        
    def update(self, delta_time: float):
        """Обновление переходов"""
        if self.progression_system.level_state == LevelState.STATISTICS:
            self.transition_alpha = min(255, self.transition_alpha + self.transition_speed * delta_time * 255)
        elif self.progression_system.level_state == LevelState.NEXT_LEVEL:
            self.transition_alpha = max(0, self.transition_alpha - self.transition_speed * delta_time * 255)
    
    def render_transition(self):
        """Отрисовка перехода"""
        if self.progression_system.level_state == LevelState.STATISTICS:
            self.statistics_renderer.render_statistics(self.progression_system.get_statistics())
        elif self.progression_system.level_state == LevelState.NEXT_LEVEL:
            # Отрисовка экрана загрузки
            self._render_loading_screen()
    
    def _render_loading_screen(self):
        """Отрисовка экрана загрузки"""
        screen_width, screen_height = self.statistics_renderer.screen.get_size()
        
        # Фон
        self.statistics_renderer.screen.fill((0, 0, 0))
        
        # Текст загрузки
        loading_text = "Генерация следующего уровня..."
        loading_surface = self.statistics_renderer.font.render(loading_text, True, (255, 255, 255))
        loading_rect = loading_surface.get_rect(center=(screen_width // 2, screen_height // 2))
        self.statistics_renderer.screen.blit(loading_surface, loading_rect)
        
        # Индикатор прогресса
        progress_text = "Пожалуйста, подождите..."
        progress_surface = self.statistics_renderer.font.render(progress_text, True, (150, 150, 150))
        progress_rect = progress_surface.get_rect(center=(screen_width // 2, screen_height // 2 + 50))
        self.statistics_renderer.screen.blit(progress_surface, progress_rect)
