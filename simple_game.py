"""
Упрощенная версия игры с базовой функциональностью.
"""

import sys
import logging
import time
import random
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Импорт основных систем
from config.settings_manager import settings_manager
from entities.player import Player
from entities.enemy import Enemy
from entities.entity_factory import EntityFactory

class SimpleGame:
    """Упрощенная версия игры"""
    
    def __init__(self):
        self.running = False
        self.player = None
        self.enemies = []
        self.game_time = 0
        self.delta_time = 0
        self.last_frame_time = 0
        
        # Создаем фабрику
        self.factory = EntityFactory()
        
        logger.info("Простая игра инициализирована")
    
    def start_new_game(self, player_name: str = "Герой"):
        """Начинает новую игру"""
        try:
            logger.info(f"Создание новой игры: {player_name}")
            
            # Создаем игрока
            self.player = self.factory.create_player("player", (0, 0))
            self.player.name = player_name
            
            # Создаем врагов
            self.spawn_enemies()
            
            # Запускаем игровой цикл
            self.running = True
            self.game_time = 0
            self.last_frame_time = time.time()
            
            logger.info("Новая игра запущена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания новой игры: {e}")
            return False
    
    def spawn_enemies(self):
        """Создает врагов"""
        enemy_types = ["warrior", "archer", "mage"]
        
        for i in range(3):
            enemy_type = random.choice(enemy_types)
            enemy = self.factory.create_enemy(
                enemy_type=enemy_type,
                level=random.randint(1, 3),
                position=(random.randint(100, 300), random.randint(100, 300))
            )
            self.enemies.append(enemy)
        
        logger.info(f"Создано {len(self.enemies)} врагов")
    
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
                self.update()
                
                # Рендерим
                self.render()
                
                # Ограничиваем FPS
                time.sleep(max(0, 1/30 - self.delta_time))
            
            logger.info("Игровой цикл завершен")
            
        except Exception as e:
            logger.error(f"Ошибка в игровом цикле: {e}")
    
    def handle_input(self):
        """Обрабатывает ввод"""
        try:
            # Простая обработка ввода через консоль
            # В реальной игре здесь была бы обработка событий pygame
            
            # Автоматические действия
            if self.player and self.player.health < self.player.max_health * 0.5:
                self.player.use_item_intelligently()
            
        except Exception as e:
            logger.error(f"Ошибка обработки ввода: {e}")
    
    def update(self):
        """Обновляет игровую логику"""
        try:
            # Обновляем игрока
            if self.player:
                self.player.update(self.delta_time)
            
            # Обновляем врагов
            for enemy in self.enemies[:]:  # Копируем список для безопасного удаления
                enemy.update(self.delta_time)
                
                # Удаляем мертвых врагов
                if not enemy.alive:
                    self.enemies.remove(enemy)
                    logger.info(f"Враг {enemy.enemy_type} побежден!")
            
            # Проверяем коллизии
            self.check_collisions()
            
            # Проверяем победу/поражение
            self.check_game_state()
            
        except Exception as e:
            logger.error(f"Ошибка обновления: {e}")
    
    def check_collisions(self):
        """Проверяет коллизии"""
        try:
            if not self.player or not self.player.alive:
                return
            
            # Проверяем коллизии игрока с врагами
            for enemy in self.enemies:
                if enemy.alive:
                    distance = self.player.distance_to(enemy)
                    if distance < 50:  # Радиус коллизии
                        # Игрок атакует врага
                        if self.player.can_attack():
                            damage_report = self.player.attack(enemy)
                            if damage_report:
                                logger.info(f"Игрок нанес {damage_report.get('damage', 0)} урона врагу {enemy.enemy_type}")
                        
                        # Враг атакует игрока
                        if enemy.can_attack():
                            damage_report = enemy.attack(self.player)
                            if damage_report:
                                logger.info(f"Враг {enemy.enemy_type} нанес {damage_report.get('damage', 0)} урона игроку")
            
        except Exception as e:
            logger.error(f"Ошибка проверки коллизий: {e}")
    
    def check_game_state(self):
        """Проверяет состояние игры"""
        try:
            # Проверяем победу
            if not self.enemies:
                logger.info("🎉 Победа! Все враги побеждены!")
                self.running = False
                return
            
            # Проверяем поражение
            if self.player and not self.player.alive:
                logger.info("💀 Поражение! Игрок погиб!")
                self.running = False
                return
            
        except Exception as e:
            logger.error(f"Ошибка проверки состояния игры: {e}")
    
    def render(self):
        """Рендерит игру"""
        try:
            # Очищаем экран (в консольной версии просто выводим информацию)
            self.print_game_state()
            
        except Exception as e:
            logger.error(f"Ошибка рендеринга: {e}")
    
    def print_game_state(self):
        """Выводит состояние игры в консоль"""
        if not self.player:
            return
        
        # Очищаем экран (простой способ)
        print("\n" * 50)
        
        print("=" * 60)
        print(f"🎮 ИГРА ВРЕМЯ: {self.game_time//1000}с")
        print("=" * 60)
        
        # Информация об игроке
        print(f"👤 ИГРОК: {self.player.name}")
        print(f"   ❤️  Здоровье: {self.player.health:.1f}/{self.player.max_health:.1f} ({self.player.get_health_percentage()*100:.1f}%)")
        print(f"   🔮 Мана: {self.player.mana:.1f}/{self.player.max_mana:.1f} ({self.player.get_mana_percentage()*100:.1f}%)")
        print(f"   ⚡ Выносливость: {self.player.stamina:.1f}/{self.player.max_stamina:.1f} ({self.player.get_stamina_percentage()*100:.1f}%)")
        print(f"   📊 Уровень: {self.player.level} | Опыт: {self.player.experience}/{self.player.experience_to_next}")
        print(f"   🗡️  Урон: {self.player.damage_output:.1f} | 🛡️ Защита: {self.player.defense:.1f}")
        
        # Информация о врагах
        print(f"\n👹 ВРАГИ ({len(self.enemies)}):")
        for i, enemy in enumerate(self.enemies, 1):
            if enemy.alive:
                health_percent = enemy.get_health_percentage() * 100
                print(f"   {i}. {enemy.enemy_type.title()} (Ур.{enemy.level}) - ❤️ {enemy.health:.1f}/{enemy.max_health:.1f} ({health_percent:.1f}%)")
            else:
                print(f"   {i}. {enemy.enemy_type.title()} - 💀 МЕРТВ")
        
        # AI информация
        print(f"\n🤖 AI СИСТЕМЫ:")
        print(f"   🧠 Память: {len(self.player.ai_memory.memory)} событий")
        print(f"   📈 Мастерство оружия: {self.player.weapon_mastery}")
        print(f"   🎯 Предпочтения предметов: {self.player.item_preferences}")
        
        print("\n" + "=" * 60)
        print("💡 Управление: Автоматический режим (AI управляет игроком)")
        print("=" * 60)
        
    def cleanup(self):
        """Очистка ресурсов"""
        try:
            logger.info("Начинается очистка ресурсов...")
            
            # Здесь можно добавить сохранение игры
            
            logger.info("Очистка ресурсов завершена")
            
        except Exception as e:
            logger.error(f"Ошибка очистки ресурсов: {e}")


def main():
    """Главная функция"""
    game = SimpleGame()
    
    try:
        logger.info("🚀 Запуск упрощенной версии игры...")
        
        # Загружаем настройки
        settings_manager.reload_settings()
        logger.info("Настройки загружены")
        
        # Начинаем новую игру
        if game.start_new_game("Герой"):
            # Запускаем игровой цикл
            game.run()
        
    except KeyboardInterrupt:
        logger.info("Игра прервана пользователем")
    
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Очистка ресурсов
        game.cleanup()
        logger.info("Игра завершена")


if __name__ == "__main__":
    main()
