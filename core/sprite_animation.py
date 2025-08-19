#!/usr/bin/env python3
"""
Система анимации спрайтов для персонажей
Обрабатывает анимации из PNG файлов в папке graphics/player
"""

import pygame
import os
from typing import Dict, List, Optional, Tuple
from enum import Enum
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class AnimationState(Enum):
    """Состояния анимации"""
    IDLE = "idle"
    WALKING = "walking"
    ATTACKING = "attacking"
    DEAD = "dead"


class Direction(Enum):
    """Направления движения"""
    DOWN = "down"
    UP = "up"
    LEFT = "left"
    RIGHT = "right"


class SpriteAnimation:
    """Система анимации спрайтов"""
    
    def __init__(self, sprite_path: str = "graphics/player"):
        self.sprite_path = Path(sprite_path)
        self.animations: Dict[str, List[pygame.Surface]] = {}
        self.current_animation = "down_idle"
        self.current_frame = 0
        self.animation_speed = 0.15  # Секунды на кадр
        self.frame_timer = 0
        self.is_playing = True
        self.loop = True
        
        # Загрузка всех анимаций
        self._load_animations()
    
    def _load_animations(self):
        """Загрузка всех анимаций из папки спрайтов"""
        try:
            # Словарь для хранения путей к анимациям
            animation_paths = {
                # Idle анимации
                "down_idle": "down_idle/idle_down.png",
                "up_idle": "up_idle/idle_up.png", 
                "left_idle": "left_idle/idle_left.png",
                "right_idle": "right_idle/idle_right.png",
                
                # Walking анимации
                "down_walk": "down",
                "up_walk": "up",
                "left_walk": "left", 
                "right_walk": "right",
                
                # Attack анимации
                "down_attack": "down_attack/attack_down.png",
                "up_attack": "up_attack/attack_up.png",
                "left_attack": "left_attack/attack_left.png",
                "right_attack": "right_attack/attack_right.png"
            }
            
            # Загружаем idle и attack анимации (один кадр)
            for anim_name, anim_path in animation_paths.items():
                if anim_name.endswith("_idle") or anim_name.endswith("_attack"):
                    full_path = self.sprite_path / anim_path
                    if full_path.exists():
                        try:
                            surface = pygame.image.load(str(full_path)).convert_alpha()
                            self.animations[anim_name] = [surface]
                            logger.info(f"Загружена анимация {anim_name}")
                        except Exception as e:
                            logger.error(f"Ошибка загрузки анимации {anim_name}: {e}")
                            # Создаем заглушку
                            self.animations[anim_name] = [self._create_placeholder_surface()]
            
            # Загружаем walking анимации (несколько кадров)
            for direction in ["down", "up", "left", "right"]:
                anim_name = f"{direction}_walk"
                anim_folder = self.sprite_path / direction
                
                if anim_folder.exists():
                    frames = []
                    # Ищем файлы с номерами кадров
                    for i in range(4):  # Обычно 4 кадра для walking
                        frame_path = anim_folder / f"{direction}_{i}.png"
                        if frame_path.exists():
                            try:
                                surface = pygame.image.load(str(frame_path)).convert_alpha()
                                frames.append(surface)
                            except Exception as e:
                                logger.error(f"Ошибка загрузки кадра {frame_path}: {e}")
                    
                    if frames:
                        self.animations[anim_name] = frames
                        logger.info(f"Загружена анимация {anim_name} с {len(frames)} кадрами")
                    else:
                        # Создаем заглушку
                        self.animations[anim_name] = [self._create_placeholder_surface()]
            
            logger.info(f"Загружено {len(self.animations)} анимаций")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки анимаций: {e}")
            # Создаем базовую заглушку
            self.animations["down_idle"] = [self._create_placeholder_surface()]
    
    def _create_placeholder_surface(self) -> pygame.Surface:
        """Создание заглушки для отсутствующих спрайтов"""
        surface = pygame.Surface((32, 32))
        surface.fill((255, 0, 255))  # Розовый цвет для отладки
        return surface
    
    def set_animation(self, animation_name: str, reset: bool = True):
        """Установка текущей анимации"""
        if animation_name in self.animations:
            if self.current_animation != animation_name or reset:
                self.current_animation = animation_name
                self.current_frame = 0
                self.frame_timer = 0
                logger.debug(f"Установлена анимация: {animation_name}")
        else:
            logger.warning(f"Анимация {animation_name} не найдена")
    
    def set_direction_animation(self, direction: Direction, state: AnimationState):
        """Установка анимации по направлению и состоянию"""
        animation_name = f"{direction.value}_{state.value}"
        self.set_animation(animation_name)
    
    def update(self, delta_time: float):
        """Обновление анимации"""
        if not self.is_playing or self.current_animation not in self.animations:
            return
        
        self.frame_timer += delta_time
        
        if self.frame_timer >= self.animation_speed:
            self.frame_timer = 0
            frames = self.animations[self.current_animation]
            
            if self.current_frame < len(frames) - 1:
                self.current_frame += 1
            elif self.loop:
                self.current_frame = 0
    
    def get_current_frame(self) -> Optional[pygame.Surface]:
        """Получение текущего кадра анимации"""
        if self.current_animation in self.animations:
            frames = self.animations[self.current_animation]
            if 0 <= self.current_frame < len(frames):
                return frames[self.current_frame]
        return None
    
    def get_animation_rect(self) -> Optional[pygame.Rect]:
        """Получение прямоугольника текущего кадра"""
        frame = self.get_current_frame()
        if frame:
            return frame.get_rect()
        return None
    
    def is_animation_finished(self) -> bool:
        """Проверка завершения анимации"""
        if self.current_animation in self.animations:
            frames = self.animations[self.current_animation]
            return self.current_frame >= len(frames) - 1 and not self.loop
        return True
    
    def pause(self):
        """Приостановка анимации"""
        self.is_playing = False
    
    def resume(self):
        """Возобновление анимации"""
        self.is_playing = True
    
    def reset(self):
        """Сброс анимации к началу"""
        self.current_frame = 0
        self.frame_timer = 0


class CharacterSprite:
    """Спрайт персонажа с анимацией"""
    
    def __init__(self, sprite_path: str = "graphics/player"):
        self.animation = SpriteAnimation(sprite_path)
        self.direction = Direction.DOWN
        self.state = AnimationState.IDLE
        self.position = pygame.Vector2(0, 0)
        self.scale = 1.0
        
    def update(self, delta_time: float):
        """Обновление спрайта"""
        self.animation.update(delta_time)
        
        # Автоматическое определение анимации по состоянию и направлению
        animation_name = f"{self.direction.value}_{self.state.value}"
        self.animation.set_animation(animation_name, reset=False)
    
    def set_direction(self, direction: Direction):
        """Установка направления"""
        self.direction = direction
    
    def set_state(self, state: AnimationState):
        """Установка состояния"""
        self.state = state
    
    def set_position(self, x: float, y: float):
        """Установка позиции"""
        self.position.x = x
        self.position.y = y
    
    def get_surface(self) -> Optional[pygame.Surface]:
        """Получение поверхности для отрисовки"""
        return self.animation.get_current_frame()
    
    def get_rect(self) -> Optional[pygame.Rect]:
        """Получение прямоугольника спрайта"""
        frame = self.get_surface()
        if frame:
            rect = frame.get_rect()
            rect.center = self.position
            return rect
        return None
    
    def render(self, surface: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)):
        """Отрисовка спрайта"""
        frame = self.get_surface()
        if frame:
            rect = frame.get_rect()
            rect.center = (self.position.x - camera_offset[0], self.position.y - camera_offset[1])
            surface.blit(frame, rect)
