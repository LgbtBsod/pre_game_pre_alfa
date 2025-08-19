"""
Загрузчик ресурсов для игры
Отвечает только за загрузку и управление ресурсами (спрайты, звуки, данные)
"""

import os
import pygame
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class ResourceLoader:
    """
    Загрузчик ресурсов.
    Отвечает только за загрузку и кэширование ресурсов.
    """
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self._sprite_cache: Dict[str, List[pygame.Surface]] = {}
        self._sound_cache: Dict[str, pygame.mixer.Sound] = {}
        self._music_cache: Dict[str, str] = {}
        self._data_cache: Dict[str, Any] = {}
        
        # Статистика загрузки
        self.loaded_sprites = 0
        self.loaded_sounds = 0
        self.loaded_music = 0
        self.loaded_data = 0
    
    def load_sprite_animations(self, sprite_path: str) -> Dict[str, List[pygame.Surface]]:
        """
        Загрузка анимаций спрайтов из папки
        
        Args:
            sprite_path: Путь к папке со спрайтами
            
        Returns:
            Словарь с анимациями {имя_анимации: [спрайты]}
        """
        animations = {}
        full_path = self.base_path / sprite_path
        
        if not full_path.exists():
            logger.error(f"Путь к спрайтам не найден: {full_path}")
            return animations
        
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
                    full_anim_path = full_path / anim_path
                    if full_anim_path.exists():
                        try:
                            surface = pygame.image.load(str(full_anim_path)).convert_alpha()
                            animations[anim_name] = [surface]
                            self.loaded_sprites += 1
                            logger.debug(f"Загружена анимация {anim_name}")
                        except Exception as e:
                            logger.error(f"Ошибка загрузки анимации {anim_name}: {e}")
                            animations[anim_name] = [self._create_placeholder_surface()]
            
            # Загружаем walking анимации (несколько кадров)
            for direction in ["down", "up", "left", "right"]:
                anim_name = f"{direction}_walk"
                anim_folder = full_path / direction
                
                if anim_folder.exists():
                    frames = []
                    # Ищем файлы с номерами кадров
                    for i in range(4):  # Обычно 4 кадра для walking
                        frame_path = anim_folder / f"{direction}_{i}.png"
                        if frame_path.exists():
                            try:
                                surface = pygame.image.load(str(frame_path)).convert_alpha()
                                frames.append(surface)
                                self.loaded_sprites += 1
                            except Exception as e:
                                logger.error(f"Ошибка загрузки кадра {frame_path}: {e}")
                    
                    if frames:
                        animations[anim_name] = frames
                        logger.debug(f"Загружена анимация {anim_name} с {len(frames)} кадрами")
                    else:
                        animations[anim_name] = [self._create_placeholder_surface()]
            
            # Кэшируем загруженные анимации
            cache_key = str(full_path)
            self._sprite_cache[cache_key] = animations
            
            logger.info(f"Загружено {len(animations)} анимаций, {self.loaded_sprites} спрайтов")
            return animations
            
        except Exception as e:
            logger.error(f"Ошибка загрузки анимаций: {e}")
            return {}
    
    def load_single_sprite(self, sprite_path: str) -> Optional[pygame.Surface]:
        """
        Загрузка одного спрайта
        
        Args:
            sprite_path: Путь к файлу спрайта
            
        Returns:
            Загруженный спрайт или None
        """
        full_path = self.base_path / sprite_path
        
        if not full_path.exists():
            logger.error(f"Файл спрайта не найден: {full_path}")
            return None
        
        try:
            surface = pygame.image.load(str(full_path)).convert_alpha()
            self.loaded_sprites += 1
            logger.debug(f"Загружен спрайт: {sprite_path}")
            return surface
        except Exception as e:
            logger.error(f"Ошибка загрузки спрайта {sprite_path}: {e}")
            return self._create_placeholder_surface()
    
    def load_sound(self, sound_path: str) -> Optional[pygame.mixer.Sound]:
        """
        Загрузка звукового файла
        
        Args:
            sound_path: Путь к звуковому файлу
            
        Returns:
            Загруженный звук или None
        """
        if sound_path in self._sound_cache:
            return self._sound_cache[sound_path]
        
        full_path = self.base_path / sound_path
        
        if not full_path.exists():
            logger.error(f"Звуковой файл не найден: {full_path}")
            return None
        
        try:
            sound = pygame.mixer.Sound(str(full_path))
            self._sound_cache[sound_path] = sound
            self.loaded_sounds += 1
            logger.debug(f"Загружен звук: {sound_path}")
            return sound
        except Exception as e:
            logger.error(f"Ошибка загрузки звука {sound_path}: {e}")
            return None
    
    def load_music(self, music_path: str) -> bool:
        """
        Загрузка музыкального файла
        
        Args:
            music_path: Путь к музыкальному файлу
            
        Returns:
            True если загрузка успешна
        """
        full_path = self.base_path / music_path
        
        if not full_path.exists():
            logger.error(f"Музыкальный файл не найден: {full_path}")
            return False
        
        try:
            self._music_cache[music_path] = str(full_path)
            self.loaded_music += 1
            logger.debug(f"Загружена музыка: {music_path}")
            return True
        except Exception as e:
            logger.error(f"Ошибка загрузки музыки {music_path}: {e}")
            return False
    
    def load_data_file(self, data_path: str) -> Optional[Any]:
        """
        Загрузка файла данных (JSON, TXT и т.д.)
        
        Args:
            data_path: Путь к файлу данных
            
        Returns:
            Загруженные данные или None
        """
        if data_path in self._data_cache:
            return self._data_cache[data_path]
        
        full_path = self.base_path / data_path
        
        if not full_path.exists():
            logger.error(f"Файл данных не найден: {full_path}")
            return None
        
        try:
            import json
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._data_cache[data_path] = data
            self.loaded_data += 1
            logger.debug(f"Загружены данные: {data_path}")
            return data
        except Exception as e:
            logger.error(f"Ошибка загрузки данных {data_path}: {e}")
            return None
    
    def get_cached_animations(self, sprite_path: str) -> Optional[Dict[str, List[pygame.Surface]]]:
        """Получение кэшированных анимаций"""
        cache_key = str(self.base_path / sprite_path)
        return self._sprite_cache.get(cache_key)
    
    def get_cached_sound(self, sound_path: str) -> Optional[pygame.mixer.Sound]:
        """Получение кэшированного звука"""
        return self._sound_cache.get(sound_path)
    
    def get_cached_music(self, music_path: str) -> Optional[str]:
        """Получение кэшированной музыки"""
        return self._music_cache.get(music_path)
    
    def get_cached_data(self, data_path: str) -> Optional[Any]:
        """Получение кэшированных данных"""
        return self._data_cache.get(data_path)
    
    def clear_cache(self, cache_type: str = "all") -> None:
        """
        Очистка кэша
        
        Args:
            cache_type: Тип кэша для очистки ("sprites", "sounds", "music", "data", "all")
        """
        if cache_type in ["sprites", "all"]:
            self._sprite_cache.clear()
            logger.info("Кэш спрайтов очищен")
        
        if cache_type in ["sounds", "all"]:
            self._sound_cache.clear()
            logger.info("Кэш звуков очищен")
        
        if cache_type in ["music", "all"]:
            self._music_cache.clear()
            logger.info("Кэш музыки очищен")
        
        if cache_type in ["data", "all"]:
            self._data_cache.clear()
            logger.info("Кэш данных очищен")
    
    def get_statistics(self) -> Dict[str, int]:
        """Получение статистики загрузки"""
        return {
            'loaded_sprites': self.loaded_sprites,
            'loaded_sounds': self.loaded_sounds,
            'loaded_music': self.loaded_music,
            'loaded_data': self.loaded_data,
            'cached_animations': len(self._sprite_cache),
            'cached_sounds': len(self._sound_cache),
            'cached_music': len(self._music_cache),
            'cached_data': len(self._data_cache)
        }
    
    def _create_placeholder_surface(self) -> pygame.Surface:
        """Создание заглушки для отсутствующих спрайтов"""
        surface = pygame.Surface((32, 32))
        surface.fill((255, 0, 255))  # Розовый цвет для отладки
        return surface
