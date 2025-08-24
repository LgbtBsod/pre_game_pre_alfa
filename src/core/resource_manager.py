#!/usr/bin/env python3
"""
Resource Manager - Менеджер ресурсов для Panda3D
Отвечает только за загрузку, кэширование и управление игровыми ресурсами
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
from panda3d.core import Texture, TextureStage, NodePath, PandaNode
from panda3d.core import GeomNode, Geom, GeomVertexData, GeomVertexFormat
from panda3d.core import GeomVertexWriter, GeomTriangles
from panda3d.core import AudioSound, AudioManager
from direct.showbase.Loader import Loader
from .interfaces import IResourceManager

logger = logging.getLogger(__name__)

class ResourceManager(IResourceManager):
    """Менеджер ресурсов для Panda3D"""
    
    def __init__(self):
        self.base_path = Path("assets")
        self.cache: Dict[str, Any] = {}
        self.textures: Dict[str, Texture] = {}
        self.models: Dict[str, NodePath] = {}
        self.sounds: Dict[str, AudioSound] = {}
        self.audio_manager: Optional[AudioManager] = None
        self.loader: Optional[Loader] = None
        
        logger.info("Менеджер ресурсов Panda3D инициализирован")
    
    def initialize(self) -> bool:
        """Инициализация менеджера ресурсов"""
        try:
            logger.info("Инициализация менеджера ресурсов Panda3D...")
            
            # Создание директорий ресурсов
            self._create_resource_directories()
            
            # Инициализация загрузчика Panda3D
            self._initialize_loader()
            
            # Инициализация аудио менеджера
            self._initialize_audio()
            
            # Предзагрузка базовых ресурсов
            self._preload_basic_resources()
            
            logger.info("Менеджер ресурсов Panda3D успешно инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации менеджера ресурсов: {e}")
            return False
    
    def _create_resource_directories(self):
        """Создание директорий ресурсов"""
        directories = [
            "textures",
            "models", 
            "audio",
            "shaders",
            "data"
        ]
        
        for directory in directories:
            dir_path = self.base_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Создана директория ресурсов: {directory}")
    
    def _initialize_loader(self):
        """Инициализация загрузчика Panda3D"""
        try:
            self.loader = Loader(None)
            logger.debug("Загрузчик Panda3D инициализирован")
        except Exception as e:
            logger.warning(f"Не удалось инициализировать загрузчик: {e}")
    
    def _initialize_audio(self):
        """Инициализация аудио менеджера"""
        try:
            self.audio_manager = AudioManager()
            logger.debug("Аудио менеджер инициализирован")
        except Exception as e:
            logger.warning(f"Не удалось инициализировать аудио менеджер: {e}")
    
    def _preload_basic_resources(self):
        """Предзагрузка базовых ресурсов"""
        try:
            # Создаем базовые текстуры
            self._create_basic_textures()
            
            # Создаем базовые модели
            self._create_basic_models()
            
            logger.debug("Базовые ресурсы предзагружены")
            
        except Exception as e:
            logger.warning(f"Ошибка предзагрузки базовых ресурсов: {e}")
    
    # Реализация интерфейса IResourceManager
    def load_resource(self, resource_path: str, resource_type: str) -> Any:
        """Загрузка ресурса"""
        try:
            if resource_type == "texture":
                return self.load_texture(resource_path)
            elif resource_type == "model":
                return self.load_model(resource_path)
            elif resource_type == "sound":
                return self.load_sound(resource_path)
            else:
                logger.warning(f"Неизвестный тип ресурса: {resource_type}")
                return None
        except Exception as e:
            logger.error(f"Ошибка загрузки ресурса {resource_path}: {e}")
            return None
    
    def unload_resource(self, resource_path: str) -> bool:
        """Выгрузка ресурса"""
        try:
            if resource_path in self.cache:
                del self.cache[resource_path]
                logger.debug(f"Ресурс {resource_path} выгружен")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка выгрузки ресурса {resource_path}: {e}")
            return False
    
    def get_resource(self, resource_path: str) -> Optional[Any]:
        """Получение ресурса"""
        return self.cache.get(resource_path)
    
    def is_resource_loaded(self, resource_path: str) -> bool:
        """Проверка загрузки ресурса"""
        return resource_path in self.cache
    
    def _create_basic_textures(self):
        """Создание базовых текстур"""
        # Создаем простую текстуру для тестирования
        texture = Texture("basic_texture")
        texture.setup2dTexture(64, 64, Texture.TUnsignedByte, Texture.FRgba)
        
        # Заполняем текстуру данными
        data = texture.modifyRamImage()
        for i in range(64 * 64 * 4):
            data.setElement(i, 128)  # Серый цвет
        
        self.textures["basic"] = texture
        logger.debug("Создана базовая текстура")
    
    def _create_basic_models(self):
        """Создание базовых моделей"""
        # Создаем простой куб
        cube = self._create_cube_model()
        self.models["cube"] = cube
        logger.debug("Создана базовая модель куба")
    
    def _create_cube_model(self) -> NodePath:
        """Создание модели куба"""
        # Создаем геометрию куба
        format = GeomVertexFormat.getV3c4()
        vdata = GeomVertexData('cube', format, Geom.UHStatic)
        
        vertex = GeomVertexWriter(vdata, 'vertex')
        color = GeomVertexWriter(vdata, 'color')
        
        # Вершины куба
        vertices = [
            (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
            (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)
        ]
        
        # Добавляем вершины
        for v in vertices:
            vertex.addData3(*v)
            color.addData4(1, 1, 1, 1)  # Белый цвет
        
        # Создаем треугольники
        prim = GeomTriangles(Geom.UHStatic)
        
        # Грани куба
        faces = [
            (0, 1, 2), (2, 3, 0),  # Передняя грань
            (1, 5, 6), (6, 2, 1),  # Правая грань
            (5, 4, 7), (7, 6, 5),  # Задняя грань
            (4, 0, 3), (3, 7, 4),  # Левая грань
            (3, 2, 6), (6, 7, 3),  # Верхняя грань
            (4, 5, 1), (1, 0, 4)   # Нижняя грань
        ]
        
        for face in faces:
            prim.addVertices(*face)
            prim.closePrimitive()
        
        # Создаем геометрию
        geom = Geom(vdata)
        geom.addPrimitive(prim)
        
        # Создаем узел
        node = GeomNode('cube')
        node.addGeom(geom)
        
        return NodePath(node)
    
    def load_texture(self, texture_path: str) -> Optional[Texture]:
        """Загрузка текстуры"""
        if texture_path in self.textures:
            return self.textures[texture_path]
        
        try:
            full_path = self.base_path / "textures" / texture_path
            
            if not full_path.exists():
                logger.warning(f"Текстура не найдена: {texture_path}")
                return self.textures.get("basic")
            
            # Загружаем текстуру через Panda3D
            texture = Texture()
            texture.read(str(full_path))
            
            self.textures[texture_path] = texture
            logger.debug(f"Текстура загружена: {texture_path}")
            return texture
            
        except Exception as e:
            logger.error(f"Ошибка загрузки текстуры {texture_path}: {e}")
            return self.textures.get("basic")
    
    def load_model(self, model_path: str) -> Optional[NodePath]:
        """Загрузка модели"""
        if model_path in self.models:
            return self.models[model_path].copy()
        
        try:
            full_path = self.base_path / "models" / model_path
            
            if not full_path.exists():
                logger.warning(f"Модель не найдена: {model_path}")
                return self.models.get("cube")
            
            # Загружаем модель через Panda3D загрузчик
            if self.loader:
                model = self.loader.loadModel(str(full_path))
                if model:
                    self.models[model_path] = model
                    logger.debug(f"Модель загружена: {model_path}")
                    return model.copy()
            
            logger.warning(f"Не удалось загрузить модель: {model_path}")
            return self.models.get("cube")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки модели {model_path}: {e}")
            return self.models.get("cube")
    
    def load_sound(self, sound_path: str) -> Optional[AudioSound]:
        """Загрузка звука"""
        if sound_path in self.sounds:
            return self.sounds[sound_path]
        
        try:
            full_path = self.base_path / "audio" / sound_path
            
            if not full_path.exists():
                logger.warning(f"Звук не найден: {sound_path}")
                return None
            
            # Загружаем звук через Panda3D аудио менеджер
            if self.audio_manager:
                sound = self.audio_manager.getSound(str(full_path))
                if sound:
                    self.sounds[sound_path] = sound
                    logger.debug(f"Звук загружен: {sound_path}")
                    return sound
            
            logger.warning(f"Не удалось загрузить звук: {sound_path}")
            return None
            
        except Exception as e:
            logger.error(f"Ошибка загрузки звука {sound_path}: {e}")
            return None
    
    def get_texture(self, texture_name: str) -> Optional[Texture]:
        """Получение текстуры по имени"""
        return self.textures.get(texture_name)
    
    def get_model(self, model_name: str) -> Optional[NodePath]:
        """Получение модели по имени"""
        model = self.models.get(model_name)
        return model.copy() if model else None
    
    def get_sound(self, sound_name: str) -> Optional[AudioSound]:
        """Получение звука по имени"""
        return self.sounds.get(sound_name)
    
    def create_simple_texture(self, name: str, width: int, height: int, color: tuple) -> Texture:
        """Создание простой текстуры"""
        texture = Texture(name)
        texture.setup2dTexture(width, height, Texture.TUnsignedByte, Texture.FRgba)
        
        # Заполняем текстуру цветом
        data = texture.modifyRamImage()
        for i in range(0, width * height * 4, 4):
            data.setElement(i, color[0])     # R
            data.setElement(i + 1, color[1]) # G
            data.setElement(i + 2, color[2]) # B
            data.setElement(i + 3, color[3]) # A
        
        self.textures[name] = texture
        logger.debug(f"Создана простая текстура: {name}")
        return texture
    
    def create_simple_model(self, name: str, vertices: list, faces: list, color: tuple = (1, 1, 1, 1)) -> NodePath:
        """Создание простой модели"""
        format = GeomVertexFormat.getV3c4()
        vdata = GeomVertexData(name, format, Geom.UHStatic)
        
        vertex = GeomVertexWriter(vdata, 'vertex')
        color_writer = GeomVertexWriter(vdata, 'color')
        
        # Добавляем вершины
        for v in vertices:
            vertex.addData3(*v)
            color_writer.addData4(*color)
        
        # Создаем треугольники
        prim = GeomTriangles(Geom.UHStatic)
        
        for face in faces:
            prim.addVertices(*face)
            prim.closePrimitive()
        
        # Создаем геометрию
        geom = Geom(vdata)
        geom.addPrimitive(prim)
        
        # Создаем узел
        node = GeomNode(name)
        node.addGeom(geom)
        
        model = NodePath(node)
        self.models[name] = model
        logger.debug(f"Создана простая модель: {name}")
        return model
    
    def clear_cache(self):
        """Очистка кэша ресурсов"""
        self.cache.clear()
        logger.info("Кэш ресурсов очищен")
    
    def get_resource_info(self) -> Dict[str, Any]:
        """Получение информации о ресурсах"""
        return {
            'textures_count': len(self.textures),
            'models_count': len(self.models),
            'sounds_count': len(self.sounds),
            'cache_size': len(self.cache),
            'textures': list(self.textures.keys()),
            'models': list(self.models.keys()),
            'sounds': list(self.sounds.keys())
        }
    
    def cleanup(self):
        """Очистка менеджера ресурсов"""
        logger.info("Очистка менеджера ресурсов Panda3D...")
        
        # Очищаем ресурсы
        self.textures.clear()
        self.models.clear()
        self.sounds.clear()
        self.cache.clear()
        
        # Очищаем менеджеры
        self.audio_manager = None
        self.loader = None
        
        logger.info("Менеджер ресурсов Panda3D очищен")
