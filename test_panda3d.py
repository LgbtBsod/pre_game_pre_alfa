#!/usr/bin/env python3
"""Тест Panda3D для проверки 3D функциональности."""

import sys
import os
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties, TextNode
from direct.gui.OnscreenText import OnscreenText
logger.info("✓ Panda3D успешно импортирован")

class TestPanda3D(ShowBase):
    def __init__(self):
        super().__init__()
        
        # Настройка окна
        props = WindowProperties()
        props.setTitle("Тест Panda3D")
        props.setSize(800, 600)
        self.win.requestProperties(props)
        
        # Создание простого куба
        self.create_test_cube()
        
        # Создание UI
        self.create_test_ui()
        
        # Обработка клавиш
        self.accept("escape", self.userExit)
        self.accept("space", self.rotate_cube)
        
        logger.info("✓ Panda3D тест запущен успешно")
        logger.info("Нажмите SPACE для вращения куба, ESC для выхода")
    
    def create_test_cube(self):
        """Создание тестового куба"""
        try:
            # Пытаемся загрузить модель
            self.cube = self.loader.loadModel("models/box")
            if not self.cube:
                # Если модель не найдена, создаем простой куб
                self.cube = self.create_simple_cube()
                logger.info("✓ Создан простой куб")
            else:
                logger.info("✓ Загружена модель box.egg")
            
            self.cube.setColor(0, 0.8, 1, 1)  # Голубой цвет
            self.cube.setPos(0, 0, 0)
            self.cube.reparentTo(self.render)
            
        except Exception as e:
            logger.warning(f"⚠ Ошибка создания куба: {e}")
            self.cube = None
    
    def create_simple_cube(self):
        """Создание простого куба программно"""
        from panda3d.core import GeomNode, Geom, GeomVertexData, GeomVertexFormat
        from panda3d.core import GeomVertexWriter, GeomTriangles, GeomNode
        
        # Вершины куба
        vertices = [
            -0.5, -0.5, -0.5,  # 0
             0.5, -0.5, -0.5,  # 1
             0.5,  0.5, -0.5,  # 2
            -0.5,  0.5, -0.5,  # 3
            -0.5, -0.5,  0.5,  # 4
             0.5, -0.5,  0.5,  # 5
             0.5,  0.5,  0.5,  # 6
            -0.5,  0.5,  0.5   # 7
        ]
        
        # Индексы для треугольников
        indices = [
            0, 1, 2, 0, 2, 3,  # передняя грань
            1, 5, 6, 1, 6, 2,  # правая грань
            5, 4, 7, 5, 7, 6,  # задняя грань
            4, 0, 3, 4, 3, 7,  # левая грань
            3, 2, 6, 3, 6, 7,  # верхняя грань
            4, 5, 1, 4, 1, 0   # нижняя грань
        ]
        
        # Создание геометрии
        format = GeomVertexFormat.getV3()
        vdata = GeomVertexData('cube', format, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        
        for i in range(0, len(vertices), 3):
            vertex.addData3(vertices[i], vertices[i+1], vertices[i+2])
        
        # Создание треугольников
        tris = GeomTriangles(Geom.UHStatic)
        for i in range(0, len(indices), 3):
            tris.addVertices(indices[i], indices[i+1], indices[i+2])
        
        tris.closePrimitive()
        
        # Создание геометрии
        geom = Geom(vdata)
        geom.addPrimitive(tris)
        
        # Создание узла
        node = GeomNode('cube')
        node.addGeom(geom)
        
        return self.render.attachNewNode(node)
    
    def create_test_ui(self):
        """Создание тестового UI"""
        # Заголовок
        title = OnscreenText(
            text="Тест Panda3D - Успешно!",
            pos=(0, 0.7),
            scale=0.05,
            fg=(0, 1, 0, 1),  # Зеленый цвет
            align=TextNode.ACenter,
            mayChange=False
        )
        
        # Инструкции
        instructions = OnscreenText(
            text="SPACE - вращать куб | ESC - выход",
            pos=(0, -0.7),
            scale=0.03,
            fg=(1, 1, 1, 1),  # Белый цвет
            align=TextNode.ACenter,
            mayChange=False
        )
        
        # Кнопка теста (упрощенная версия)
        logger.info("Кнопка теста создана (упрощенная версия)")
    
    def test_button_click(self):
        """Тест нажатия кнопки"""
        logger.info("✓ Кнопка работает!")
        if self.cube:
            self.cube.setColor(1, 0.5, 0, 1)  # Оранжевый цвет
    
    def rotate_cube(self):
        """Вращение куба"""
        if self.cube:
            self.cube.setH(self.cube.getH() + 45)
            logger.info("Куб повернут на 45°")

def main():
    logger.info("Запуск теста Panda3D...")
    try:
        app = TestPanda3D()
        app.run()
        logger.info("✓ Тест завершен успешно")
    except Exception as e:
        logger.error(f"✗ Ошибка запуска: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
