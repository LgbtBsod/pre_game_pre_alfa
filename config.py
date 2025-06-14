import pygame

# Настройки окна
WIDTH, HEIGHT = 1200, 800
TILE_SIZE = 40  # Размер одного тайла в пикселях

# Цвета
BACKGROUND = (30, 35, 45)       # Фон
GRID_COLOR = (60, 70, 90)        # Сетка карты
PLAYER_COLOR = (80, 180, 255)    # Игрок
ENEMY_COLOR = (220, 80, 80)      # Враги
TRAP_COLOR = (220, 180, 60)      # Ловушки
ITEM_COLOR = (50, 200, 150)      # Предметы
CHEST_COLOR = (200, 160, 60)     # Сундуки
GOAL_COLOR = (255, 215, 70)      # Цель
UI_BG = (40, 45, 60, 200)        # Фон UI
TEXT_COLOR = (220, 220, 220)     # Текст
PATH_COLOR = (180, 100, 220, 100)  # Путь игрока
ATTACK_COLOR = (255, 200, 0, 180) # Атака
DAMAGE_COLOR = (255, 50, 50, 220) # Получение урона
XP_COLOR = (100, 200, 255)       # Опыт
LEVEL_UP_COLOR = (255, 215, 0)   # Уровень вырос
POISON_COLOR = (100, 200, 100, 150)  # Отравление
BUTTON_COLOR = (70, 90, 120)     # Кнопки
BUTTON_HOVER = (90, 110, 150)    # Наведение на кнопку
BUTTON_TEXT = (240, 240, 240)    # Текст на кнопках

# Инициализация Pygame
pygame.init()

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Изометрический Автономный Платформер")
clock = pygame.time.Clock()