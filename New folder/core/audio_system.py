#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЗВУКОВАЯ СИСТЕМА
Централизованное управление аудио в игре
Соблюдает принцип единой ответственности
"""

import time
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import math

from utils.logging_system import get_logger, log_system_event

class AudioType(Enum):
    """Типы аудио"""
    MUSIC = "music"
    SFX = "sfx"
    VOICE = "voice"
    AMBIENT = "ambient"
    UI = "ui"

class AudioState(Enum):
    """Состояния аудио"""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    LOADING = "loading"
    ERROR = "error"

@dataclass
class AudioClip:
    """Аудио клип"""
    clip_id: str
    file_path: str
    audio_type: AudioType
    volume: float = 1.0
    pitch: float = 1.0
    loop: bool = False
    fade_in: float = 0.0
    fade_out: float = 0.0
    duration: float = 0.0
    loaded: bool = False

@dataclass
class AudioInstance:
    """Экземпляр воспроизведения аудио"""
    instance_id: str
    clip: AudioClip
    volume: float
    pitch: float
    position: float = 0.0
    state: AudioState = AudioState.STOPPED
    start_time: float = 0.0
    fade_start: float = 0.0
    fade_duration: float = 0.0

class AudioSystem:
    """Звуковая система"""
    
    def __init__(self, audio_directory: str = "assets/audio"):
        self.audio_directory = Path(audio_directory)
        self.audio_directory.mkdir(parents=True, exist_ok=True)
        
        # Словари для хранения аудио
        self.clips: Dict[str, AudioClip] = {}
        self.instances: Dict[str, AudioInstance] = {}
        
        # Настройки громкости
        self.master_volume = 1.0
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        self.voice_volume = 0.9
        self.ambient_volume = 0.5
        self.ui_volume = 0.6
        
        # Состояние системы
        self.enabled = True
        self.muted = False
        self.current_music: Optional[str] = None
        
        # Поток для обновления аудио
        self.update_thread: Optional[threading.Thread] = None
        self.running = False
        
        self.logger = get_logger("audio_system")
        
        # Настройки
        self.max_instances = 32
        self.fade_time = 1.0
        self.audio_3d_enabled = True
        self.doppler_enabled = True
        
        # Инициализация
        self._initialize_audio()
        
        log_system_event("audio_system", "initialized")
    
    def _initialize_audio(self):
        """Инициализация аудио системы"""
        try:
            # Здесь должна быть инициализация конкретной аудио библиотеки
            # Для демонстрации используем заглушки
            
            # Загружаем базовые звуки
            self._load_default_sounds()
            
            # Запускаем поток обновления
            self.running = True
            self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
            self.update_thread.start()
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации аудио системы: {e}")
            self.enabled = False
    
    def _load_default_sounds(self):
        """Загрузка базовых звуков"""
        default_sounds = {
            "ui_click": ("ui/click.wav", AudioType.UI),
            "ui_hover": ("ui/hover.wav", AudioType.UI),
            "ui_error": ("ui/error.wav", AudioType.UI),
            "combat_hit": ("sfx/hit.wav", AudioType.SFX),
            "combat_miss": ("sfx/miss.wav", AudioType.SFX),
            "combat_critical": ("sfx/critical.wav", AudioType.SFX),
            "player_levelup": ("sfx/levelup.wav", AudioType.SFX),
            "player_death": ("sfx/death.wav", AudioType.SFX),
            "ambient_forest": ("ambient/forest.wav", AudioType.AMBIENT),
            "ambient_cave": ("ambient/cave.wav", AudioType.AMBIENT),
            "music_main": ("music/main_theme.wav", AudioType.MUSIC),
            "music_combat": ("music/combat.wav", AudioType.MUSIC),
            "voice_npc": ("voice/npc.wav", AudioType.VOICE)
        }
        
        for sound_id, (file_path, audio_type) in default_sounds.items():
            self.load_audio(sound_id, file_path, audio_type)
    
    def load_audio(self, clip_id: str, file_path: str, audio_type: AudioType, 
                  volume: float = 1.0, loop: bool = False) -> bool:
        """Загрузка аудио файла"""
        try:
            full_path = self.audio_directory / file_path
            
            # Проверяем существование файла
            if not full_path.exists():
                self.logger.warning(f"Аудио файл не найден: {full_path}")
                return False
            
            # Создаем аудио клип
            clip = AudioClip(
                clip_id=clip_id,
                file_path=str(full_path),
                audio_type=audio_type,
                volume=volume,
                loop=loop,
                loaded=True
            )
            
            # Здесь должна быть реальная загрузка аудио файла
            # Для демонстрации просто добавляем в словарь
            self.clips[clip_id] = clip
            
            log_system_event("audio_system", "audio_loaded", {
                "clip_id": clip_id,
                "file_path": file_path,
                "audio_type": audio_type.value
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки аудио {clip_id}: {e}")
            return False
    
    def play_audio(self, clip_id: str, volume: Optional[float] = None, 
                  pitch: float = 1.0, loop: bool = False, 
                  fade_in: float = 0.0, position: tuple = None) -> Optional[str]:
        """Воспроизведение аудио"""
        try:
            if not self.enabled or self.muted:
                return None
            
            if clip_id not in self.clips:
                self.logger.warning(f"Аудио клип не найден: {clip_id}")
                return None
            
            clip = self.clips[clip_id]
            
            # Проверяем лимит экземпляров
            if len(self.instances) >= self.max_instances:
                self._stop_oldest_instance()
            
            # Генерируем ID экземпляра
            instance_id = f"{clip_id}_{int(time.time() * 1000)}"
            
            # Устанавливаем громкость
            if volume is None:
                volume = clip.volume * self._get_type_volume(clip.audio_type)
            
            # Создаем экземпляр
            instance = AudioInstance(
                instance_id=instance_id,
                clip=clip,
                volume=volume * self.master_volume,
                pitch=pitch,
                state=AudioState.PLAYING,
                start_time=time.time(),
                fade_duration=fade_in
            )
            
            self.instances[instance_id] = instance
            
            # Специальная обработка для музыки
            if clip.audio_type == AudioType.MUSIC:
                self._handle_music_playback(clip_id, instance_id)
            
            # Здесь должна быть реальная команда воспроизведения
            self._start_audio_playback(instance)
            
            log_system_event("audio_system", "audio_played", {
                "clip_id": clip_id,
                "instance_id": instance_id,
                "volume": volume,
                "loop": loop
            })
            
            return instance_id
            
        except Exception as e:
            self.logger.error(f"Ошибка воспроизведения аудио {clip_id}: {e}")
            return None
    
    def stop_audio(self, instance_id: str, fade_out: float = 0.0) -> bool:
        """Остановка аудио"""
        try:
            if instance_id not in self.instances:
                return False
            
            instance = self.instances[instance_id]
            
            if fade_out > 0:
                instance.fade_start = time.time()
                instance.fade_duration = fade_out
                instance.state = AudioState.PLAYING  # Продолжаем для фейда
            else:
                instance.state = AudioState.STOPPED
                self._stop_audio_playback(instance)
                del self.instances[instance_id]
            
            log_system_event("audio_system", "audio_stopped", {
                "instance_id": instance_id,
                "fade_out": fade_out
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка остановки аудио {instance_id}: {e}")
            return False
    
    def pause_audio(self, instance_id: str) -> bool:
        """Пауза аудио"""
        try:
            if instance_id not in self.instances:
                return False
            
            instance = self.instances[instance_id]
            if instance.state == AudioState.PLAYING:
                instance.state = AudioState.PAUSED
                self._pause_audio_playback(instance)
                
                log_system_event("audio_system", "audio_paused", {
                    "instance_id": instance_id
                })
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Ошибка паузы аудио {instance_id}: {e}")
            return False
    
    def resume_audio(self, instance_id: str) -> bool:
        """Возобновление аудио"""
        try:
            if instance_id not in self.instances:
                return False
            
            instance = self.instances[instance_id]
            if instance.state == AudioState.PAUSED:
                instance.state = AudioState.PLAYING
                self._resume_audio_playback(instance)
                
                log_system_event("audio_system", "audio_resumed", {
                    "instance_id": instance_id
                })
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Ошибка возобновления аудио {instance_id}: {e}")
            return False
    
    def set_volume(self, volume_type: str, volume: float) -> bool:
        """Установка громкости"""
        try:
            volume = max(0.0, min(1.0, volume))
            
            if volume_type == "master":
                self.master_volume = volume
            elif volume_type == "music":
                self.music_volume = volume
            elif volume_type == "sfx":
                self.sfx_volume = volume
            elif volume_type == "voice":
                self.voice_volume = volume
            elif volume_type == "ambient":
                self.ambient_volume = volume
            elif volume_type == "ui":
                self.ui_volume = volume
            else:
                return False
            
            # Обновляем громкость всех активных экземпляров
            self._update_all_volumes()
            
            log_system_event("audio_system", "volume_changed", {
                "volume_type": volume_type,
                "volume": volume
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка установки громкости: {e}")
            return False
    
    def mute_all(self, muted: bool = True):
        """Отключение/включение всех звуков"""
        self.muted = muted
        
        if muted:
            # Останавливаем все звуки
            for instance_id in list(self.instances.keys()):
                self.stop_audio(instance_id)
        else:
            # Обновляем громкость
            self._update_all_volumes()
        
        log_system_event("audio_system", "mute_toggled", {
            "muted": muted
        })
    
    def play_music(self, clip_id: str, fade_in: float = 2.0, loop: bool = True) -> bool:
        """Воспроизведение музыки"""
        try:
            # Останавливаем текущую музыку
            if self.current_music:
                self.stop_audio(self.current_music, fade_out=1.0)
            
            # Воспроизводим новую музыку
            instance_id = self.play_audio(clip_id, volume=self.music_volume, 
                                        loop=loop, fade_in=fade_in)
            
            if instance_id:
                self.current_music = instance_id
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Ошибка воспроизведения музыки {clip_id}: {e}")
            return False
    
    def play_sfx(self, clip_id: str, volume: Optional[float] = None) -> bool:
        """Воспроизведение звукового эффекта"""
        instance_id = self.play_audio(clip_id, volume=volume or self.sfx_volume)
        return instance_id is not None
    
    def play_ui_sound(self, clip_id: str) -> bool:
        """Воспроизведение звука интерфейса"""
        instance_id = self.play_audio(clip_id, volume=self.ui_volume)
        return instance_id is not None
    
    def play_3d_audio(self, clip_id: str, position: tuple, 
                     volume: Optional[float] = None) -> Optional[str]:
        """Воспроизведение 3D аудио"""
        if not self.audio_3d_enabled:
            return self.play_audio(clip_id, volume)
        
        # Здесь должна быть реализация 3D позиционирования
        # Для демонстрации просто воспроизводим обычный звук
        return self.play_audio(clip_id, volume)
    
    def _get_type_volume(self, audio_type: AudioType) -> float:
        """Получение громкости по типу"""
        if audio_type == AudioType.MUSIC:
            return self.music_volume
        elif audio_type == AudioType.SFX:
            return self.sfx_volume
        elif audio_type == AudioType.VOICE:
            return self.voice_volume
        elif audio_type == AudioType.AMBIENT:
            return self.ambient_volume
        elif audio_type == AudioType.UI:
            return self.ui_volume
        else:
            return 1.0
    
    def _handle_music_playback(self, clip_id: str, instance_id: str):
        """Обработка воспроизведения музыки"""
        # Останавливаем предыдущую музыку
        if self.current_music and self.current_music != instance_id:
            self.stop_audio(self.current_music, fade_out=1.0)
        
        self.current_music = instance_id
    
    def _start_audio_playback(self, instance: AudioInstance):
        """Запуск воспроизведения аудио"""
        # Здесь должна быть реальная команда воспроизведения
        # Для демонстрации просто логируем
        self.logger.debug(f"Воспроизведение: {instance.clip.clip_id}")
    
    def _stop_audio_playback(self, instance: AudioInstance):
        """Остановка воспроизведения аудио"""
        # Здесь должна быть реальная команда остановки
        self.logger.debug(f"Остановка: {instance.clip.clip_id}")
    
    def _pause_audio_playback(self, instance: AudioInstance):
        """Пауза воспроизведения аудио"""
        # Здесь должна быть реальная команда паузы
        self.logger.debug(f"Пауза: {instance.clip.clip_id}")
    
    def _resume_audio_playback(self, instance: AudioInstance):
        """Возобновление воспроизведения аудио"""
        # Здесь должна быть реальная команда возобновления
        self.logger.debug(f"Возобновление: {instance.clip.clip_id}")
    
    def _update_all_volumes(self):
        """Обновление громкости всех экземпляров"""
        for instance in self.instances.values():
            type_volume = self._get_type_volume(instance.clip.audio_type)
            instance.volume = instance.clip.volume * type_volume * self.master_volume
    
    def _stop_oldest_instance(self):
        """Остановка самого старого экземпляра"""
        if not self.instances:
            return
        
        oldest_id = min(self.instances.keys(), 
                       key=lambda x: self.instances[x].start_time)
        self.stop_audio(oldest_id)
    
    def _update_loop(self):
        """Основной цикл обновления аудио"""
        while self.running:
            try:
                current_time = time.time()
                
                # Обновляем все экземпляры
                to_remove = []
                for instance_id, instance in self.instances.items():
                    if instance.state == AudioState.PLAYING:
                        # Обработка фейда
                        if instance.fade_duration > 0:
                            elapsed = current_time - instance.start_time
                            if elapsed < instance.fade_duration:
                                # Фейд ин
                                fade_progress = elapsed / instance.fade_duration
                                instance.volume *= fade_progress
                            else:
                                instance.fade_duration = 0
                        
                        # Обработка фейда аут
                        if instance.fade_start > 0:
                            fade_elapsed = current_time - instance.fade_start
                            if fade_elapsed < instance.fade_duration:
                                # Фейд аут
                                fade_progress = 1.0 - (fade_elapsed / instance.fade_duration)
                                instance.volume *= fade_progress
                            else:
                                # Завершение фейда
                                instance.state = AudioState.STOPPED
                                to_remove.append(instance_id)
                
                # Удаляем завершенные экземпляры
                for instance_id in to_remove:
                    if instance_id in self.instances:
                        del self.instances[instance_id]
                
                time.sleep(0.016)  # 60 FPS
                
            except Exception as e:
                self.logger.error(f"Ошибка в цикле обновления аудио: {e}")
                time.sleep(0.1)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики аудио системы"""
        return {
            "enabled": self.enabled,
            "muted": self.muted,
            "total_clips": len(self.clips),
            "active_instances": len(self.instances),
            "current_music": self.current_music,
            "volumes": {
                "master": self.master_volume,
                "music": self.music_volume,
                "sfx": self.sfx_volume,
                "voice": self.voice_volume,
                "ambient": self.ambient_volume,
                "ui": self.ui_volume
            },
            "settings": {
                "audio_3d_enabled": self.audio_3d_enabled,
                "doppler_enabled": self.doppler_enabled,
                "max_instances": self.max_instances
            }
        }
    
    def cleanup(self):
        """Очистка ресурсов"""
        self.running = False
        
        # Останавливаем все звуки
        for instance_id in list(self.instances.keys()):
            self.stop_audio(instance_id)
        
        # Ждем завершения потока
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1.0)
        
        self.clips.clear()
        self.instances.clear()
        self.current_music = None
        
        log_system_event("audio_system", "cleanup_completed")
