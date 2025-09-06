#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
СИСТЕМА СОХРАНЕНИЙ
Централизованное управление сохранениями игры
Соблюдает принцип единой ответственности
"""

import json
import time
import os
import shutil
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field
from pathlib import Path
from enum import Enum
import hashlib
import gzip
import pickle

from utils.logging_system import get_logger, log_system_event

class SaveType(Enum):
    """Типы сохранений"""
    AUTO = "auto"
    MANUAL = "manual"
    QUICK = "quick"
    BACKUP = "backup"

class SaveStatus(Enum):
    """Статусы сохранений"""
    SUCCESS = "success"
    FAILED = "failed"
    CORRUPTED = "corrupted"
    INCOMPLETE = "incomplete"

@dataclass
class SaveMetadata:
    """Метаданные сохранения"""
    save_id: str
    save_type: SaveType
    timestamp: float
    game_version: str
    player_name: str
    level: int
    playtime: float
    location: str
    file_size: int
    checksum: str
    status: SaveStatus = SaveStatus.SUCCESS
    description: str = ""

@dataclass
class SaveData:
    """Данные сохранения"""
    metadata: SaveMetadata
    game_state: Dict[str, Any]
    player_data: Dict[str, Any]
    world_data: Dict[str, Any]
    settings: Dict[str, Any]
    # Новые поля для роглайк механик
    ai_memory_data: Dict[str, Any] = field(default_factory=dict)
    generated_content: Dict[str, Any] = field(default_factory=dict)
    session_data: Dict[str, Any] = field(default_factory=dict)
    enemy_memory_bank: Dict[str, Any] = field(default_factory=dict)
    player_memory: Dict[str, Any] = field(default_factory=dict)

class SaveSystem:
    """Система сохранений"""
    
    def __init__(self, save_directory: str = "saves", max_saves: int = 50):
        self.save_directory = Path(save_directory)
        self.save_directory.mkdir(parents=True, exist_ok=True)
        
        # Поддиректории
        self.auto_saves_dir = self.save_directory / "auto"
        self.manual_saves_dir = self.save_directory / "manual"
        self.quick_saves_dir = self.save_directory / "quick"
        self.backup_dir = self.save_directory / "backup"
        
        # Создаем поддиректории
        for dir_path in [self.auto_saves_dir, self.manual_saves_dir, 
                        self.quick_saves_dir, self.backup_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.max_saves = max_saves
        self.current_save_id: Optional[str] = None
        self.game_version = "1.0.0"
        
        self.logger = get_logger("save_system")
        
        # Настройки
        self.auto_save_interval = 300.0  # 5 минут
        self.last_auto_save = time.time()
        self.compression_enabled = True
        self.encryption_enabled = False
        
        log_system_event("save_system", "initialized")
    
    def create_save(self, save_type: SaveType, player_data: Dict[str, Any], 
                   game_state: Dict[str, Any], world_data: Dict[str, Any],
                   settings: Dict[str, Any], description: str = "",
                   ai_memory_data: Dict[str, Any] = None,
                   generated_content: Dict[str, Any] = None,
                   session_data: Dict[str, Any] = None,
                   enemy_memory_bank: Dict[str, Any] = None,
                   player_memory: Dict[str, Any] = None) -> Optional[str]:
        """Создание сохранения"""
        try:
            # Генерируем ID сохранения
            save_id = self._generate_save_id(save_type)
            
            # Создаем метаданные
            metadata = SaveMetadata(
                save_id=save_id,
                save_type=save_type,
                timestamp=time.time(),
                game_version=self.game_version,
                player_name=player_data.get("name", "Unknown"),
                level=player_data.get("level", 1),
                playtime=player_data.get("playtime", 0.0),
                location=world_data.get("current_location", "Unknown"),
                file_size=0,  # Будет установлен после сохранения
                checksum="",  # Будет установлен после сохранения
                description=description
            )
            
            # Создаем данные сохранения
            save_data = SaveData(
                metadata=metadata,
                game_state=game_state,
                player_data=player_data,
                world_data=world_data,
                settings=settings,
                ai_memory_data=ai_memory_data or {},
                generated_content=generated_content or {},
                session_data=session_data or {},
                enemy_memory_bank=enemy_memory_bank or {},
                player_memory=player_memory or {}
            )
            
            # Сохраняем файл
            if self._save_to_file(save_data):
                self.current_save_id = save_id
                
                # Очистка старых сохранений
                self._cleanup_old_saves(save_type)
                
                log_system_event("save_system", "save_created", {
                    "save_id": save_id,
                    "save_type": save_type.value,
                    "player_name": metadata.player_name,
                    "level": metadata.level
                })
                
                return save_id
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Ошибка создания сохранения: {e}")
            return None
    
    def create_roguelike_save(self, session_id: str, player_data: Dict[str, Any],
                            game_state: Dict[str, Any], world_data: Dict[str, Any],
                            ai_memory_data: Dict[str, Any],
                            generated_content: Dict[str, Any],
                            enemy_memory_bank: Dict[str, Any],
                            player_memory: Dict[str, Any]) -> Optional[str]:
        """Создание сохранения для роглайк сессии"""
        try:
            # Создаем данные сессии
            session_data = {
                "session_id": session_id,
                "session_start_time": time.time(),
                "is_roguelike": True,
                "content_generated": True,
                "lighthouse_found": False,
                "enemies_encountered": [],
                "items_generated": [],
                "bosses_defeated": []
            }
            
            # Создаем сохранение с роглайк данными
            save_id = self.create_save(
                save_type=SaveType.MANUAL,
                player_data=player_data,
                game_state=game_state,
                world_data=world_data,
                settings={},
                description=f"Roguelike Session {session_id}",
                ai_memory_data=ai_memory_data,
                generated_content=generated_content,
                session_data=session_data,
                enemy_memory_bank=enemy_memory_bank,
                player_memory=player_memory
            )
            
            if save_id:
                log_system_event("save_system", "roguelike_save_created", {
                    "session_id": session_id,
                    "save_id": save_id
                })
            
            return save_id
            
        except Exception as e:
            self.logger.error(f"Ошибка создания роглайк сохранения: {e}")
            return None
    
    def load_roguelike_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Загрузка роглайк сессии"""
        try:
            # Ищем сохранение по session_id
            for save_file in self.save_directory.glob("*.json"):
                try:
                    with open(save_file, 'r', encoding='utf-8') as f:
                        save_data = json.load(f)
                    
                    if (save_data.get("session_data", {}).get("session_id") == session_id and
                        save_data.get("session_data", {}).get("is_roguelike", False)):
                        return save_data
                        
                except Exception:
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки роглайк сессии: {e}")
            return None
    
    def update_ai_memory_in_save(self, save_id: str, entity_id: str, 
                                memory_data: Dict[str, Any]) -> bool:
        """Обновление памяти ИИ в сохранении"""
        try:
            save_file = self.save_directory / f"{save_id}.json"
            if not save_file.exists():
                return False
            
            with open(save_file, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Обновляем память ИИ
            if "ai_memory_data" not in save_data:
                save_data["ai_memory_data"] = {}
            
            save_data["ai_memory_data"][entity_id] = memory_data
            
            # Сохраняем обратно
            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления памяти ИИ: {e}")
            return False
    
    def get_all_roguelike_sessions(self) -> List[Dict[str, Any]]:
        """Получение всех роглайк сессий"""
        sessions = []
        
        try:
            for save_file in self.save_directory.glob("*.json"):
                try:
                    with open(save_file, 'r', encoding='utf-8') as f:
                        save_data = json.load(f)
                    
                    if save_data.get("session_data", {}).get("is_roguelike", False):
                        sessions.append({
                            "save_id": save_file.stem,
                            "session_id": save_data.get("session_data", {}).get("session_id"),
                            "timestamp": save_data.get("metadata", {}).get("timestamp", 0),
                            "player_name": save_data.get("metadata", {}).get("player_name", "Unknown"),
                            "level": save_data.get("metadata", {}).get("level", 1),
                            "lighthouse_found": save_data.get("session_data", {}).get("lighthouse_found", False)
                        })
                        
                except Exception:
                    continue
            
            # Сортируем по времени
            sessions.sort(key=lambda x: x["timestamp"], reverse=True)
            return sessions
            
        except Exception as e:
            self.logger.error(f"Ошибка получения роглайк сессий: {e}")
            return []
    
    def load_save(self, save_id: str) -> Optional[SaveData]:
        """Загрузка сохранения"""
        try:
            # Ищем файл сохранения
            save_file = self._find_save_file(save_id)
            if not save_file or not save_file.exists():
                self.logger.error(f"Файл сохранения не найден: {save_id}")
                return None
            
            # Загружаем данные
            save_data = self._load_from_file(save_file)
            if not save_data:
                return None
            
            # Проверяем целостность
            if not self._verify_save_integrity(save_data):
                self.logger.error(f"Сохранение повреждено: {save_id}")
                save_data.metadata.status = SaveStatus.CORRUPTED
                return None
            
            self.current_save_id = save_id
            
            log_system_event("save_system", "save_loaded", {
                "save_id": save_id,
                "player_name": save_data.metadata.player_name,
                "level": save_data.metadata.level
            })
            
            return save_data
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки сохранения {save_id}: {e}")
            return None
    
    def delete_save(self, save_id: str) -> bool:
        """Удаление сохранения"""
        try:
            save_file = self._find_save_file(save_id)
            if not save_file or not save_file.exists():
                return False
            
            # Создаем резервную копию
            backup_file = self.backup_dir / f"{save_id}_deleted_{int(time.time())}.save"
            shutil.copy2(save_file, backup_file)
            
            # Удаляем файл
            save_file.unlink()
            
            if save_id == self.current_save_id:
                self.current_save_id = None
            
            log_system_event("save_system", "save_deleted", {
                "save_id": save_id
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка удаления сохранения {save_id}: {e}")
            return False
    
    def list_saves(self, save_type: Optional[SaveType] = None) -> List[SaveMetadata]:
        """Получение списка сохранений"""
        saves = []
        
        try:
            # Определяем директории для поиска
            if save_type:
                dirs = [self._get_save_directory(save_type)]
            else:
                dirs = [self.auto_saves_dir, self.manual_saves_dir, 
                       self.quick_saves_dir]
            
            for save_dir in dirs:
                if not save_dir.exists():
                    continue
                
                for save_file in save_dir.glob("*.save"):
                    try:
                        # Загружаем только метаданные
                        metadata = self._load_metadata(save_file)
                        if metadata:
                            saves.append(metadata)
                    except Exception as e:
                        self.logger.warning(f"Ошибка загрузки метаданных {save_file}: {e}")
            
            # Сортируем по времени создания
            saves.sort(key=lambda x: x.timestamp, reverse=True)
            
        except Exception as e:
            self.logger.error(f"Ошибка получения списка сохранений: {e}")
        
        return saves
    
    def auto_save(self, player_data: Dict[str, Any], game_state: Dict[str, Any], 
                 world_data: Dict[str, Any], settings: Dict[str, Any]) -> bool:
        """Автоматическое сохранение"""
        current_time = time.time()
        
        if current_time - self.last_auto_save < self.auto_save_interval:
            return False
        
        save_id = self.create_save(
            SaveType.AUTO,
            player_data,
            game_state,
            world_data,
            settings,
            "Автоматическое сохранение"
        )
        
        if save_id:
            self.last_auto_save = current_time
            return True
        
        return False
    
    def quick_save(self, player_data: Dict[str, Any], game_state: Dict[str, Any], 
                  world_data: Dict[str, Any], settings: Dict[str, Any]) -> bool:
        """Быстрое сохранение"""
        save_id = self.create_save(
            SaveType.QUICK,
            player_data,
            game_state,
            world_data,
            settings,
            "Быстрое сохранение"
        )
        
        return save_id is not None
    
    def _generate_save_id(self, save_type: SaveType) -> str:
        """Генерация ID сохранения"""
        timestamp = int(time.time())
        return f"{save_type.value}_{timestamp}"
    
    def _get_save_directory(self, save_type: SaveType) -> Path:
        """Получение директории для типа сохранения"""
        if save_type == SaveType.AUTO:
            return self.auto_saves_dir
        elif save_type == SaveType.MANUAL:
            return self.manual_saves_dir
        elif save_type == SaveType.QUICK:
            return self.quick_saves_dir
        else:
            return self.save_directory
    
    def _find_save_file(self, save_id: str) -> Optional[Path]:
        """Поиск файла сохранения"""
        for save_dir in [self.auto_saves_dir, self.manual_saves_dir, 
                        self.quick_saves_dir]:
            save_file = save_dir / f"{save_id}.save"
            if save_file.exists():
                return save_file
        return None
    
    def _save_to_file(self, save_data: SaveData) -> bool:
        """Сохранение в файл"""
        try:
            save_dir = self._get_save_directory(save_data.metadata.save_type)
            save_file = save_dir / f"{save_data.metadata.save_id}.save"
            
            # Сериализуем данные
            data_bytes = pickle.dumps(save_data)
            
            # Сжимаем если включено
            if self.compression_enabled:
                data_bytes = gzip.compress(data_bytes)
            
            # Шифруем если включено
            if self.encryption_enabled:
                data_bytes = self._encrypt_data(data_bytes)
            
            # Записываем в файл
            with open(save_file, 'wb') as f:
                f.write(data_bytes)
            
            # Обновляем метаданные
            save_data.metadata.file_size = len(data_bytes)
            save_data.metadata.checksum = self._calculate_checksum(data_bytes)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка сохранения в файл: {e}")
            return False
    
    def _load_from_file(self, save_file: Path) -> Optional[SaveData]:
        """Загрузка из файла"""
        try:
            with open(save_file, 'rb') as f:
                data_bytes = f.read()
            
            # Расшифровываем если включено
            if self.encryption_enabled:
                data_bytes = self._decrypt_data(data_bytes)
            
            # Распаковываем если сжато
            if self.compression_enabled:
                try:
                    data_bytes = gzip.decompress(data_bytes)
                except:
                    # Возможно, файл не сжат
                    pass
            
            # Десериализуем данные
            save_data = pickle.loads(data_bytes)
            
            return save_data
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки из файла {save_file}: {e}")
            return None
    
    def _load_metadata(self, save_file: Path) -> Optional[SaveMetadata]:
        """Загрузка только метаданных"""
        try:
            save_data = self._load_from_file(save_file)
            if save_data:
                return save_data.metadata
        except Exception as e:
            self.logger.warning(f"Ошибка загрузки метаданных {save_file}: {e}")
        return None
    
    def _verify_save_integrity(self, save_data: SaveData) -> bool:
        """Проверка целостности сохранения"""
        try:
            # Проверяем версию игры
            if save_data.metadata.game_version != self.game_version:
                self.logger.warning(f"Несовместимая версия сохранения: {save_data.metadata.game_version}")
            
            # Проверяем обязательные поля
            required_fields = ['player_data', 'game_state', 'world_data', 'settings']
            for field in required_fields:
                if not hasattr(save_data, field) or not getattr(save_data, field):
                    self.logger.error(f"Отсутствует обязательное поле: {field}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка проверки целостности: {e}")
            return False
    
    def _calculate_checksum(self, data: bytes) -> str:
        """Вычисление контрольной суммы"""
        return hashlib.md5(data).hexdigest()
    
    def _encrypt_data(self, data: bytes) -> bytes:
        """Шифрование данных"""
        # Простое XOR шифрование (для демонстрации)
        key = b"game_save_key_2025"
        encrypted = bytearray()
        for i, byte in enumerate(data):
            encrypted.append(byte ^ key[i % len(key)])
        return bytes(encrypted)
    
    def _decrypt_data(self, data: bytes) -> bytes:
        """Расшифровка данных"""
        # XOR расшифровка (симметричное шифрование)
        return self._encrypt_data(data)
    
    def _cleanup_old_saves(self, save_type: SaveType):
        """Очистка старых сохранений"""
        try:
            save_dir = self._get_save_directory(save_type)
            if not save_dir.exists():
                return
            
            # Получаем все сохранения данного типа
            saves = []
            for save_file in save_dir.glob("*.save"):
                metadata = self._load_metadata(save_file)
                if metadata:
                    saves.append((save_file, metadata))
            
            # Сортируем по времени
            saves.sort(key=lambda x: x[1].timestamp, reverse=True)
            
            # Удаляем лишние сохранения
            if len(saves) > self.max_saves:
                for save_file, _ in saves[self.max_saves:]:
                    try:
                        save_file.unlink()
                        self.logger.info(f"Удалено старое сохранение: {save_file.name}")
                    except Exception as e:
                        self.logger.error(f"Ошибка удаления старого сохранения {save_file}: {e}")
                        
        except Exception as e:
            self.logger.error(f"Ошибка очистки старых сохранений: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики системы сохранений"""
        stats = {
            "total_saves": 0,
            "saves_by_type": {},
            "total_size": 0,
            "current_save_id": self.current_save_id,
            "auto_save_enabled": True,
            "compression_enabled": self.compression_enabled,
            "encryption_enabled": self.encryption_enabled
        }
        
        try:
            for save_type in SaveType:
                saves = self.list_saves(save_type)
                stats["saves_by_type"][save_type.value] = len(saves)
                stats["total_saves"] += len(saves)
                
                # Подсчитываем размер
                for save in saves:
                    stats["total_size"] += save.file_size
                    
        except Exception as e:
            self.logger.error(f"Ошибка получения статистики: {e}")
        
        return stats
    
    def cleanup(self):
        """Очистка ресурсов"""
        # Создаем финальное сохранение если есть текущее
        if self.current_save_id:
            log_system_event("save_system", "final_save_created", {
                "save_id": self.current_save_id
            })
        
        self.current_save_id = None
        log_system_event("save_system", "cleanup_completed")
