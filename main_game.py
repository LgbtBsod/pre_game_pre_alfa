#!/usr/bin/env python3
"""AI-EVOLVE - Главный файл игры с окном"""

import sys
import time
from pathlib import Path

# Добавляем корневую директорию в путь
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.task import Task

class AIGame(ShowBase):
    """Главный класс игры AI-EVOLVE"""
    
    def __init__(self):
        super().__init__()
        
        # Настройки окна
        self.setBackgroundColor(0.1, 0.1, 0.2)  # Темно-синий фон
        
        # Создаем простую сцену
        self.create_scene()
        
        # Запускаем игровой цикл
        self.taskMgr.add(self.game_loop, "game_loop")
        
        print("🎮 AI-EVOLVE запущен! Окно игры открыто.")
        print("🎯 Управление:")
        print("   - WASD: перемещение камеры")
        print("   - Мышь: поворот камеры")
        print("   - ESC: выход")
    
    def create_scene(self):
        """Создание базовой сцены"""
        # Создаем простой куб
        cube = self.loader.loadModel("models/box")
        if not cube:
            # Если модель не найдена, создаем простой куб
            cube = self.create_simple_cube()
        
        cube.setPos(0, 0, 0)
        cube.setScale(1)
        cube.reparentTo(self.render)
        
        # Создаем освещение
        light = PointLight("light")
        light.setColor((1, 1, 1))
        light.setAttenuation((1, 0, 1))
        
        light_np = self.render.attachNewNode(light)
        light_np.setPos(5, 5, 5)
        self.render.setLight(light_np)
        
        # Настройка камеры
        self.camera.setPos(0, -10, 5)
        self.camera.lookAt(0, 0, 0)
        
        # Добавляем текст
        text = TextNode("title")
        text.setText("AI-EVOLVE Enhanced Edition")
        text.setAlign(TextNode.ACenter)
        text.setColor(1, 1, 1, 1)
        
        text_np = self.render.attachNewNode(text)
        text_np.setPos(0, 0, 3)
        text_np.setScale(0.5)
    
    def create_simple_cube(self):
        """Создание простого куба"""
        # Создаем геометрию куба
        format = GeomVertexFormat.getV3n3c4()
        vdata = GeomVertexData("cube", format, Geom.UHStatic)
        
        # Вершины куба
        vertex = GeomVertexWriter(vdata, "vertex")
        normal = GeomVertexWriter(vdata, "normal")
        color = GeomVertexWriter(vdata, "color")
        
        # 8 вершин куба
        vertex.addData3(-1, -1, -1)
        vertex.addData3(1, -1, -1)
        vertex.addData3(1, 1, -1)
        vertex.addData3(-1, 1, -1)
        vertex.addData3(-1, -1, 1)
        vertex.addData3(1, -1, 1)
        vertex.addData3(1, 1, 1)
        vertex.addData3(-1, 1, 1)
        
        # Нормали
        for i in range(8):
            normal.addData3(0, 0, 1)
            color.addData4(0.8, 0.8, 0.8, 1)
        
        # Индексы для граней
        tris = GeomTriangles(Geom.UHStatic)
        
        # Нижняя грань
        tris.addVertices(0, 1, 2)
        tris.addVertices(0, 2, 3)
        # Верхняя грань
        tris.addVertices(4, 7, 6)
        tris.addVertices(4, 6, 5)
        # Передняя грань
        tris.addVertices(0, 4, 5)
        tris.addVertices(0, 5, 1)
        # Задняя грань
        tris.addVertices(2, 6, 7)
        tris.addVertices(2, 7, 3)
        # Левая грань
        tris.addVertices(0, 3, 7)
        tris.addVertices(0, 7, 4)
        # Правая грань
        tris.addVertices(1, 5, 6)
        tris.addVertices(1, 6, 2)
        
        tris.closePrimitive()
        
        # Создаем геометрию
        geom = Geom(vdata)
        geom.addPrimitive(tris)
        
        # Создаем узел
        node = GeomNode("cube")
        node.addGeom(geom)
        
        return node
    
    def game_loop(self, task):
        """Главный игровой цикл"""
        # Вращение куба
        cube = self.render.find("cube")
        if cube:
            cube.setH(cube.getH() + 1)
        
        return Task.cont

def main():
    """Главная функция"""
    try:
        print("🎮 Запуск AI-EVOLVE...")
        print("🚀 Инициализация Panda3D...")
        
        # Создаем игру
        game = AIGame()
        
        print("✅ Игра успешно запущена!")
        print("🎯 Окно игры открыто")
        print("💡 Нажмите ESC для выхода")
        
        # Запускаем главный цикл
        game.run()
        
    except Exception as e:
        print(f"❌ Ошибка запуска игры: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
