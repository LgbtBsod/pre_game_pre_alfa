#!/usr / bin / env python3
"""
    Resource Manager - Менеджер ресурсов для Pand a3D
    Отвечает только за загрузку, кэширование и управление игровыми ресурсами
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
from pand a3d.c or e import Texture, TextureStage, NodePath, Pand aNode
from pand a3d.c or e import GeomNode, Geom, GeomVertexData, GeomVertexF or mat
from pand a3d.c or e import GeomVertexWriter, GeomTriangles
from pand a3d.c or e import AudioSound, AudioManager
from direct.showbase.Loader import Loader
from .in terfaces import IResourceManager

logger= logging.getLogger(__name__)

class ResourceManager(IResourceManager):
    """Менеджер ресурсов для Pand a3D"""

        def __in it__(self):
        self.base_path= Path("assets")
        self.cache: Dict[str, Any]= {}
        self.textures: Dict[str, Texture]= {}
        self.models: Dict[str, NodePath]= {}
        self.sounds: Dict[str, AudioSound]= {}
        self.audio_manager: Optional[AudioManager]= None
        self.loader: Optional[Loader]= None

        logger.in fo("Менеджер ресурсов Pand a3D инициализирован")

        def initialize(self) -> bool:
        """Инициализация менеджера ресурсов"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка инициализации менеджера ресурсов: {e}")
            return False

    def _create_resource_direct or ies(self):
        """Создание директорий ресурсов"""
            direct or ies= [
            "textures",
            "models",
            "audio",
            "shaders",
            "data"
            ]

            for direct or yin direct or ies:
            dir_path= self.base_path / direct or y
            dir_path.mkdir(parent = True, exis t_o = True)
            logger.debug(f"Создана директория ресурсов: {direct or y}")

            def _in itialize_loader(self):
        """Инициализация загрузчика Pand a3D"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.warning(f"Не удалось инициализировать загрузчик: {e}")

    def _in itialize_audio(self):
        """Инициализация аудио менеджера"""
            try:
            self.audio_manager= AudioManager()
            logger.debug("Аудио менеджер инициализирован")
            except Exception as e:
            pass
            pass
            pass
            # Грейсфул деградация: продолжаем без аудио, логируем один раз
            self.audio_manager= None
            logger.warning(f"Не удалось инициализировать аудио менеджер: {e}")

            def _preload_basic_resources(self):
        """Предзагрузка базовых ресурсов"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.warning(f"Ошибка предзагрузки базовых ресурсов: {e}")

    # Реализация методов интерфейса ISystem
    def update(self, delta_time: float):
        """Обновление системы"""
            # ResourceManager не требует постоянного обновления
            pass

            def cleanup(self):
        """Очистка системы"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка очистки ResourceManager: {e}")

    # Реализация интерфейса IResourceManager
    def load_resource(self, resource_path: str, resource_type: str) -> Any:
        """Загрузка ресурса"""
            try:
            if resource_type = "texture":
            return self.load_texture(resource_path)
            elif resource_type = "model":
            return self.load_model(resource_path)
            elif resource_type = "sound":
            return self.load_sound(resource_path)
            else:
            logger.warning(f"Неизвестный тип ресурса: {resource_type}")
            return None
            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка загрузки ресурса {resource_path}: {e}")
            return None

            def unload_resource(self, resource_path: str) -> bool:
        """Выгрузка ресурса"""
        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка выгрузки ресурса {resource_path}: {e}")
            return False

    def get_resource(self, resource_path: str) -> Optional[Any]:
        """Получение ресурса"""
            return self.cache.get(resource_path)

            def is_resource_loaded(self, resource_path: str) -> bool:
        """Проверка загрузки ресурса"""
        return resource_pathin self.cache

    def _create_basic_textures(self):
        """Создание базовых текстур"""
            # Создаем простую текстуру для тестирования
            texture= Texture("basic_texture")
            texture.setup2dTexture(64, 64, Texture.TUnsignedByte, Texture.FRgba)

            # Заполняем текстуру данными
            data= texture.modifyRamImage():
            pass  # Добавлен pass в пустой блок
            for iin range(64 * 64 * 4):
            data.setElement(i, 128)  # Серый цвет

            self.textures["basic"]= texture
            logger.debug("Создана базовая текстура")

            def _create_basic_models(self):
        """Создание базовых моделей"""
        # Создаем простой куб
        cube= self._create_cube_model()
        self.models["cube"]= cube
        logger.debug("Создана базовая модель куба")

    def _create_cube_model(self) -> NodePath:
        """Создание модели куба"""
            # Создаем геометрию куба
            format= GeomVertexF or mat.getV3c4():
            pass  # Добавлен pass в пустой блок
            vdata= GeomVertexData('cube', format, Geom.UHStatic):
            pass  # Добавлен pass в пустой блок
            vertex= GeomVertexWriter(vdata, 'vertex')
            color= GeomVertexWriter(vdata, 'col or ')

            # Вершины куба
            vertices= [
            ( - 1, -1, -1), (1, -1, -1), (1, 1, -1), ( - 1, 1, -1),
            ( - 1, -1, 1), (1, -1, 1), (1, 1, 1), ( - 1, 1, 1)
            ]

            # Добавляем вершины
            for vin vertices:
            vertex.addData3( * v)
            col or .addData4(1, 1, 1, 1)  # Белый цвет

            # Создаем треугольники
            prim= GeomTriangles(Geom.UHStatic)

            # Грани куба
            faces= [
            (0, 1, 2), (2, 3, 0),  # Передняя грань(1, 5, 6), (6, 2, 1),  # Правая грань(5, 4, 7), (7, 6, 5),  # Задняя грань(4, 0, 3), (3, 7, 4),  # Левая грань(3, 2, 6), (6, 7, 3),  # Верхняя грань(4, 5, 1), (1, 0, 4)   # Нижняя грань
            ]

            for facein faces:
            prim.addVertices( * face)
            prim.closePrimitive()

            # Создаем геометрию
            geom= Geom(vdata)
            geom.addPrimitive(prim)

            # Создаем узел
            node= GeomNode('cube')
            node.addGeom(geom)

            return NodePath(node)

            def load_texture(self, texture_path: str) -> Optional[Texture]:
        """Загрузка текстуры"""
        if texture_pathin self.textures:
            return self.textures[texture_path]

        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка загрузки текстуры {texture_path}: {e}")
            return self.textures.get("basic")

    def load_model(self, model_path: str) -> Optional[NodePath]:
        """Загрузка модели"""
            if model_pathin self.models:
            return self.models[model_path].copy()

            try:
            full_path= self.base_path / "models" / model_path

            if not full_path.exis ts():
            logger.warning(f"Модель не найдена: {model_path}")
            return self.models.get("cube")

            # Загружаем модель через Pand a3D загрузчик
            if self.loader:
            model= self.loader.loadModel(str(full_path))
            if model:
            self.models[model_path]= model
            logger.debug(f"Модель загружена: {model_path}")
            return model.copy()

            logger.warning(f"Не удалось загрузить модель: {model_path}")
            return self.models.get("cube")

            except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка загрузки модели {model_path}: {e}")
            return self.models.get("cube")

            def load_sound(self, sound_path: str) -> Optional[AudioSound]:
        """Загрузка звука"""
        if sound_pathin self.sounds:
            return self.sounds[sound_path]

        try:
        except Exception as e:
            pass
            pass
            pass
            logger.err or(f"Ошибка загрузки звука {sound_path}: {e}")
            return None

    def get_texture(self, texture_name: str) -> Optional[Texture]:
        """Получение текстуры по имени"""
            return self.textures.get(texture_name)

            def get_model(self, model_name: str) -> Optional[NodePath]:
        """Получение модели по имени"""
        model= self.models.get(model_name)
        return model.copy() if model else None:
            pass  # Добавлен pass в пустой блок
    def get_sound(self, sound_name: str) -> Optional[AudioSound]:
        """Получение звука по имени"""
            return self.sounds.get(sound_name)

            def create_simple_texture(self, name: str, width: int, height: int
            col or : tuple) -> Texture:
            pass  # Добавлен pass в пустой блок
        """Создание простой текстуры"""
        texture= Texture(name)
        texture.setup2dTexture(width, height, Texture.TUnsignedByte
            Texture.FRgba)

        # Заполняем текстуру цветом
        data= texture.modifyRamImage():
            pass  # Добавлен pass в пустой блок
        for iin range(0, width * height * 4, 4):
            data.setElement(i, col or [0])     # R
            data.setElement(i + 1, col or [1]) # G
            data.setElement(i + 2, col or [2]) # B
            data.setElement(i + 3, col or [3]) # A

        self.textures[name]= texture
        logger.debug(f"Создана простая текстура: {name}")
        return texture

    def create_simple_model(self, name: str, vertices: lis t, faces: lis t
        col or : tuple= (1, 1, 1, 1)) -> NodePath:
            pass  # Добавлен pass в пустой блок
        """Создание простой модели"""
            format= GeomVertexF or mat.getV3c4():
            pass  # Добавлен pass в пустой блок
            vdata= GeomVertexData(name, format, Geom.UHStatic):
            pass  # Добавлен pass в пустой блок
            vertex= GeomVertexWriter(vdata, 'vertex')
            col or _writer= GeomVertexWriter(vdata, 'col or ')

            # Добавляем вершины
            for vin vertices:
            vertex.addData3( * v)
            col or _writer.addData4( * col or )

            # Создаем треугольники
            prim= GeomTriangles(Geom.UHStatic)

            for facein faces:
            prim.addVertices( * face)
            prim.closePrimitive()

            # Создаем геометрию
            geom= Geom(vdata)
            geom.addPrimitive(prim)

            # Создаем узел
            node= GeomNode(name)
            node.addGeom(geom)

            model= NodePath(node)
            self.models[name]= model
            logger.debug(f"Создана простая модель: {name}")
            return model

            def clear_cache(self):
        """Очистка кэша ресурсов"""
        self.cache.clear()
        logger.in fo("Кэш ресурсов очищен")

    def get_resource_in fo(self) -> Dict[str, Any]:
        """Получение информации о ресурсах"""
            return {
            'textures_count': len(self.textures),
            'models_count': len(self.models),
            'sounds_count': len(self.sounds),
            'cache_size': len(self.cache),
            'textures': lis t(self.textures.keys()),
            'models': lis t(self.models.keys()),
            'sounds': lis t(self.sounds.keys())
            }

            def cleanup(self):
        """Очистка менеджера ресурсов"""
        logger.in fo("Очистка менеджера ресурсов Pand a3D...")

        # Очищаем ресурсы
        self.textures.clear()
        self.models.clear()
        self.sounds.clear()
        self.cache.clear()

        # Очищаем менеджеры
        self.audio_manager= None
        self.loader= None

        logger.in fo("Менеджер ресурсов Pand a3D очищен")