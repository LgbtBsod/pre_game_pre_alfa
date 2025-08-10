"""
Главный файл игры.
Инициализирует все системы и запускает игровой цикл.
"""

import sys
import logging
import time
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('game.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Импорт основных систем
from config.settings_manager import settings_manager
from core.data_manager import data_manager
from core.game_state_manager import game_state_manager
from entities.entity_factory import entity_factory
from items.item_manager import item_manager

# Импорт игровых систем
from core.game_logic_manager import GameLogicManager
from core.resource_manager import resource_manager
from ui.game_menu import GameMenu
from ui.render_manager import RenderManager

# Импорт AI системы
from ai.ai_manager import ai_manager


class Game:
    """Основной класс игры"""
    
    def __init__(self):
        self.running = False
        self.paused = False
        
        # Инициализация систем
        self.game_logic = GameLogicManager(game_state_manager)
        self.render_manager = None
        self.game_menu = None
        
        # Игровые объекты
        self.player = None
        self.entities = []
        self.current_area = None
        
        # Время
        self.game_time = 0
        self.delta_time = 0
        self.last_frame_time = 0
        
        logger.info("Игра инициализирована")
    
    def initialize(self):
        """Инициализация игры"""
        try:
            logger.info("Начинается инициализация игры...")
            
            # Загружаем настройки
            settings_manager.reload_settings()
            logger.info("Настройки загружены")
            
            # Загружаем данные
            data_manager.reload_data()
            logger.info("Данные загружены")
            
            logger.info("Инициализация завершена успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации: {e}")
            return False
    
    def start_new_game(self, player_name: str, difficulty: str = "normal"):
        """Начинает новую игру"""
        try:
            logger.info(f"Создание новой игры: {player_name}, сложность: {difficulty}")
            
            # Создаем новое состояние игры
            game_id = game_state_manager.create_new_game(
                save_name=f"Save_{player_name}_{int(time.time())}",
                player_name=player_name,
                difficulty=difficulty
            )
            
            if not game_id:
                logger.error("Не удалось создать новую игру")
                return False
            
            # Создаем игрока
            self.player = entity_factory.create_player("player", (0, 0))
            
            # Загружаем начальную область
            self.load_area("starting_area")
            
            # Запускаем игровой цикл
            self.running = True
            self.game_time = 0
            self.last_frame_time = time.time()
            
            logger.info("Новая игра запущена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания новой игры: {e}")
            return False
    
    def load_game(self, game_id: str):
        """Загружает игру"""
        try:
            logger.info(f"Загрузка игры: {game_id}")
            
            # Загружаем состояние игры
            if not game_state_manager.load_game(game_id):
                logger.error("Не удалось загрузить игру")
                return False
            
            # Получаем состояние
            game_state = game_state_manager.get_current_state()
            if not game_state:
                logger.error("Состояние игры не найдено")
                return False
            
            # Восстанавливаем игрока
            player_state = game_state.player_state
            self.player = entity_factory.create_player(player_state.player_id, player_state.position)
            
            # Восстанавливаем характеристики игрока
            self.restore_player_state(player_state)
            
            # Загружаем область
            self.load_area(game_state.current_area)
            
            # Восстанавливаем время игры
            self.game_time = game_state.game_time
            
            # Запускаем игровой цикл
            self.running = True
            self.last_frame_time = time.time()
            
            logger.info("Игра загружена успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка загрузки игры: {e}")
            return False
    
    def save_game(self):
        """Сохраняет игру"""
        try:
            if not self.player:
                logger.warning("Нет игрока для сохранения")
                return False
            
            # Обновляем состояние игрока
            player_state = self.create_player_state()
            game_state_manager.update_player_state(player_state)
            
            # Сохраняем игру
            success = game_state_manager.save_game()
            
            if success:
                logger.info("Игра сохранена")
            
            return success
            
        except Exception as e:
            logger.error(f"Ошибка сохранения игры: {e}")
            return False
    
    def load_area(self, area_name: str):
        """Загружает игровую область"""
        try:
            logger.info(f"Загрузка области: {area_name}")
            
            # Очищаем текущие сущности
            self.entities.clear()
            
            # Загружаем область из менеджера карт
            # Здесь должна быть логика загрузки карты
            self.current_area = area_name
            
            # Создаем сущности для области
            self.spawn_area_entities(area_name)
            
            logger.info(f"Область {area_name} загружена")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки области: {e}")
    
    def spawn_area_entities(self, area_name: str):
        """Создает сущности для области"""
        try:
            # Создаем врагов в зависимости от области
            if area_name == "starting_area":
                # Создаем несколько слабых врагов
                for i in range(3):
                    enemy = entity_factory.create_enemy(
                        enemy_type="warrior",
                        level=1,
                        position=(100 + i * 50, 100 + i * 50)
                    )
                    self.entities.append(enemy)
                    # Регистрируем в AI системе
                    if hasattr(enemy, 'ai_core'):
                        ai_manager.register_entity(enemy, enemy.ai_core)
            
            elif area_name == "forest":
                # Создаем лесных врагов
                for i in range(5):
                    enemy = entity_factory.create_enemy(
                        enemy_type="archer",
                        level=3,
                        position=(200 + i * 80, 200 + i * 80)
                    )
                    self.entities.append(enemy)
                    # Регистрируем в AI системе
                    if hasattr(enemy, 'ai_core'):
                        ai_manager.register_entity(enemy, enemy.ai_core)
            
            elif area_name == "dungeon":
                # Создаем подземных врагов
                for i in range(8):
                    enemy = entity_factory.create_enemy(
                        enemy_type="mage",
                        level=5,
                        position=(300 + i * 60, 300 + i * 60)
                    )
                    self.entities.append(enemy)
                    # Регистрируем в AI системе
                    if hasattr(enemy, 'ai_core'):
                        ai_manager.register_entity(enemy, enemy.ai_core)
            
            logger.info(f"Создано {len(self.entities)} сущностей для области {area_name}")
            
        except Exception as e:
            logger.error(f"Ошибка создания сущностей: {e}")
    
    def run(self):
        """Основной игровой цикл"""
        try:
            logger.info("Запуск игрового цикла")
            
            while self.running:
                # Вычисляем delta time
                current_time = time.time()
                self.delta_time = current_time - self.last_frame_time
                self.last_frame_time = current_time
                
                # Обновляем время игры
                self.game_time += int(self.delta_time * 1000)
                
                # Обрабатываем ввод
                self.handle_input()
                
                # Обновляем игровую логику
                if not self.paused:
                    self.update()
                
                # Рендерим
                self.render()
                
                # Автосохранение
                game_state_manager.auto_save(self.game_time)
                
                # Ограничиваем FPS
                time.sleep(max(0, 1/60 - self.delta_time))
            
            logger.info("Игровой цикл завершен")
            
        except Exception as e:
            logger.error(f"Ошибка в игровом цикле: {e}")
    
    def handle_input(self):
        """Обрабатывает ввод"""
        try:
            # Обработка ввода через меню
            input_result = self.game_menu.handle_input()
            
            if input_result == "quit":
                self.running = False
            elif input_result == "pause":
                self.paused = not self.paused
            elif input_result == "save":
                self.save_game()
            
            # Обработка игрового ввода
            if not self.paused and self.player:
                self.game_logic.handle_player_input(self.player)
                
        except Exception as e:
            logger.error(f"Ошибка обработки ввода: {e}")
    
    def update(self):
        """Обновляет игровую логику"""
        try:
            # Обновляем игровую логику
            self.game_logic.update(self.delta_time)
            
            # Обновляем AI систему
            ai_manager.update(self.delta_time)
            
            # Обновляем игрока
            if self.player:
                self.player.update(self.delta_time)
            
            # Обновляем сущности
            for entity in self.entities[:]:  # Копируем список для безопасного удаления
                entity.update(self.delta_time)
                
                # Удаляем мертвых сущностей
                if not entity.alive:
                    self.entities.remove(entity)
                    # Удаляем из AI системы
                    ai_manager.unregister_entity(entity)
            
            # Проверяем коллизии
            self.check_collisions()
            
            # Обновляем время игры игрока
            if self.player:
                self.player.playtime = self.game_time
            
        except Exception as e:
            logger.error(f"Ошибка обновления: {e}")
    
    def render(self):
        """Рендерит игру"""
        try:
            # Очищаем экран
            self.render_manager.clear()
            
            # Рендерим игровую область
            if self.current_area:
                self.render_manager.render_area(self.current_area)
            
            # Рендерим сущности
            for entity in self.entities:
                self.render_manager.render_entity(entity)
            
            # Рендерим игрока
            if self.player:
                self.render_manager.render_entity(self.player)
            
            # Рендерим UI
            self.game_menu.render(self.render_manager)
            
            # Обновляем экран
            self.render_manager.update()
            
        except Exception as e:
            logger.error(f"Ошибка рендеринга: {e}")
    
    def check_collisions(self):
        """Проверяет коллизии"""
        try:
            if not self.player:
                return
            
            # Проверяем коллизии игрока с врагами
            for entity in self.entities:
                if entity.alive and self.player.alive:
                    distance = self.player.distance_to(entity)
                    if distance < 50:  # Радиус коллизии
                        # Игрок атакует врага
                        if self.player.can_attack():
                            self.player.attack(entity)
                        
                        # Враг атакует игрока
                        if entity.can_attack():
                            entity.attack(self.player)
            
        except Exception as e:
            logger.error(f"Ошибка проверки коллизий: {e}")
    
    def create_player_state(self) -> dict:
        """Создает состояние игрока для сохранения"""
        if not self.player:
            return {}
        
        return {
            "position": self.player.position,
            "level": self.player.level,
            "experience": self.player.experience,
            "attributes": {name: self.player.get_attribute_value(name) 
                          for name in self.player.attributes.keys()},
            "combat_stats": self.player.combat_stats.copy(),
            "equipment": self.player.equipment.copy(),
            "inventory": [item.item_id if hasattr(item, 'item_id') else str(item) 
                         for item in self.player.inventory],
            "skills": list(self.player.skill_cooldowns.keys()),
            "effects": list(self.player.active_effects.keys()),
            "playtime": self.player.playtime
        }
    
    def restore_player_state(self, player_state):
        """Восстанавливает состояние игрока"""
        if not self.player or not player_state:
            return
        
        try:
            # Восстанавливаем позицию
            self.player.position = list(player_state.position)
            
            # Восстанавливаем уровень и опыт
            self.player.level = player_state.level
            self.player.experience = player_state.experience
            
            # Восстанавливаем атрибуты
            for attr_name, attr_value in player_state.attributes.items():
                self.player.set_attribute_base(attr_name, attr_value)
            
            # Восстанавливаем боевые характеристики
            self.player.combat_stats.update(player_state.combat_stats)
            
            # Восстанавливаем экипировку
            self.player.equipment.update(player_state.equipment)
            
            # Восстанавливаем инвентарь
            self.player.inventory = []
            for item_id in player_state.inventory:
                item = item_manager.create_item(item_id)
                if item:
                    self.player.inventory.append(item)
            
            # Восстанавливаем время игры
            self.player.playtime = player_state.playtime
            
            logger.info("Состояние игрока восстановлено")
            
        except Exception as e:
            logger.error(f"Ошибка восстановления состояния игрока: {e}")
    
    def cleanup(self):
        """Очистка ресурсов"""
        try:
            logger.info("Начинается очистка ресурсов...")
            
            # Сохраняем игру
            if self.running:
                self.save_game()
            
            # Очищаем рендер
            if self.render_manager:
                self.render_manager.cleanup()
            
            # Очищаем меню
            if self.game_menu:
                self.game_menu.cleanup()
            
            logger.info("Очистка ресурсов завершена")
            
        except Exception as e:
            logger.error(f"Ошибка очистки ресурсов: {e}")


def main():
    """Главная функция"""
    game = Game()
    
    try:
        # Инициализация
        if not game.initialize():
            logger.error("Не удалось инициализировать игру")
            return
        
        # Простое тестовое сообщение
        logger.info("Игра успешно инициализирована!")
        logger.info("Все системы загружены и готовы к работе.")
        
        # Здесь можно добавить простой тестовый интерфейс или запустить игру
        input("Нажмите Enter для выхода...")
    
    except KeyboardInterrupt:
        logger.info("Игра прервана пользователем")
    
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    
    finally:
        # Очистка ресурсов
        game.cleanup()
        logger.info("Игра завершена")


if __name__ == "__main__":
    main()
