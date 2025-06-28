import pygame
import sys
import json
import os
from datetime import datetime

# Импорты классов
from entities.player import Player
from entities.enemy import Enemy
from map.game_map import GameMap
from npcs.trader import Trader
from npcs.quest_giver import QuestGiver
from items.chest import Chest
from ai.player_ai import PlayerAI
from ui.camera import Camera
from ui.buttons import Button

# Инициализация Pygame
pygame.init()

# Константы экрана
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TILE_SIZE = 40
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)

# Настройка экрана
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Isometric RPG Game")
clock = pygame.time.Clock()

# Загрузка данных
def load_game():
    """Загрузка сохраненных данных или создание новых"""
    if os.path.exists("save.json"):
        with open("save.json", "r") as f:
            return json.load(f)
    return {}

def save_game(data):
    """Сохранение игры"""
    data["last_save"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("save.json", "w") as f:
        json.dump(data, f, indent=2)

def init_game(saved_data=None):
    """Инициализация игры"""
    # Создание карты
    game_map = GameMap(20, 15)
    
    # Создание игрока
    player = Player(5, 5)
    
    # Создание врагов
    enemies = []
    for i in range(3):
        enemy = Enemy(10 + i, 5, enemy_type="warrior")
        enemies.append(enemy)
        game_map.add_entity(enemy)
    
    # Создание сундуков
    chests = []
    for i in range(2):
        chest = Chest(15, 5 + i)
        chests.append(chest)
        game_map.add_entity(chest)
    
    # Создание NPC
    trader = Trader(18, 2)
    quest_giver = QuestGiver(18, 3)
    game_map.add_entity(trader)
    game_map.add_entity(quest_giver)
    
    # Создание камеры
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    return game_map, player, enemies, chests, trader, quest_giver, camera

def main():
    # Загрузка сохраненных данных
    saved_data = load_game()
    
    # Инициализация игры
    game_map, player, enemies, chests, trader, quest_giver, camera = init_game(saved_data)
    
    # Меню
    menu_buttons = [
        Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 50, 200, 50, "Новая игра"),
        Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2, 200, 50, "Загрузить"),
        Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 50, 200, 50, "Выход")
    ]
    
    running = True
    in_menu = True
    game_paused = False
    
    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # Обработка нажатий мыши
            if event.type == pygame.MOUSEBUTTONDOWN:
                if in_menu:
                    # Обработка меню
                    for button in menu_buttons:
                        if button.check_hover(pygame.mouse.get_pos()):
                            if button.text == "Выход":
                                running = False
                            elif button.text == "Новая игра":
                                in_menu = False
                            elif button.text == "Загрузить" and os.path.exists("save.json"):
                                in_menu = False
                
                # Пауза
                elif game_paused:
                    pass  # Логика кнопок паузы
                
            # Управление игроком
            if not in_menu and not game_paused:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        # Взаимодействие с NPC
                        nearby_entities = player.get_nearby_entities(game_map.entities)
                        for entity in nearby_entities:
                            if isinstance(entity, (Trader, QuestGiver)):
                                entity.interact(player)
                    elif event.key == pygame.K_p:
                        game_paused = True
                    elif event.key == pygame.K_s:
                        # Сохранение игры
                        save_data = {
                            "player": player.serialize(),
                            "enemies": [e.serialize() for e in enemies],
                            "chests": [c.serialize() for c in chests]
                        }
                        save_game(save_data)
        
        if in_menu:
            # Отрисовка меню
            screen.fill(BLACK)
            for button in menu_buttons:
                button.draw(screen)
        elif game_paused:
            # Отрисовка паузы
            pass
        else:
            # Обновление состояния игры
            keys = pygame.key.get_pressed()
            player.update(keys, game_map)
            
            # Обновление врагов
            for enemy in enemies:
                enemy.update(player, enemies)
            
            # Обновление камеры
            camera.update(player.x, player.y)
            
            # Отрисовка
            screen.fill(GRAY)
            game_map.draw(screen, camera)
            player.draw(screen, camera)
            
            # Отрисовка врагов
            for enemy in enemies:
                enemy.draw(screen, camera)
                
            # Отрисовка сундуков
            for chest in chests:
                chest.draw(screen, camera)
                
            # Отрисовка UI
            camera.draw_ui(screen, player)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()