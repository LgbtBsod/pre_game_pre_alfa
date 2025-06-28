import pygame
import asyncio
import random
import sys
from entities.player import Player
from entities.enemy import Enemy
from entities.boss import Boss
from items.weapon import WeaponGenerator

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 800))
        pygame.display.set_caption("Автономный ИИ-выживач")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont(None, 24)
        
        # Создание игрока
        self.player = Player("player_ai", (600, 400))
        self.player.learning_rate = 1.0
        
        # Создание врагов
        self.enemies = []
        enemy_types = ["warrior", "archer", "mage"]
        for i in range(10):
            enemy = Enemy(random.choice(enemy_types), level=random.randint(1, 5))
            enemy.position = [random.randint(100, 1100), random.randint(100, 700)]
            self.enemies.append(enemy)
        
        # Создание босса с исправлением параметров
        self.boss = Boss(boss_type="dragon", level=15, position=(900, 300))
        self.boss.learning_rate = 0.005
        
        # Генерация стартового оружия
        starter_weapon = WeaponGenerator.generate_weapon(1)
        self.player.equip_item(starter_weapon)
        
        # Инициализация координатора ИИ
        from ai.cooperation import AICoordinator
        self.coordinator = AICoordinator()
        
        # Регистрация врагов в координаторе
        for enemy in self.enemies:
            self.coordinator.register_entity(enemy, "enemy_group")
        
        # Регистрация босса
        self.coordinator.register_entity(self.boss, "boss_group")
    
    async def run(self):
        while self.running:
            delta_time = self.clock.tick(60) / 1000.0
            
            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            # Обновление игрока
            self.player.update(delta_time)
            
            # Обновление врагов
            for enemy in self.enemies:
                if enemy.alive:
                    enemy.update(delta_time)
            
            # Обновление босса
            if self.boss.alive:
                self.boss.update(delta_time)
            
            # Обновление координатора ИИ
            self.coordinator.update_group_behavior("enemy_group")
            self.coordinator.update_group_behavior("boss_group")
            
            # Проверка столкновений
            self.check_collisions()
            
            # Удаление мертвых врагов
            self.enemies = [e for e in self.enemies if e.alive]
            
            # Отрисовка
            self.screen.fill((20, 30, 40))
            self.draw_entities()
            self.draw_ui()
            pygame.display.flip()
            
            # Проверка условий победы/поражения
            if not self.player.alive:
                self.game_over("Поражение! Игрок погиб.")
            elif not self.boss.alive:
                self.game_over("Победа! Босс повержен!")
    
    def check_collisions(self):
        # Проверка столкновений между игроком и врагами
        player_rect = pygame.Rect(self.player.position[0]-20, self.player.position[1]-20, 40, 40)
        
        for enemy in self.enemies:
            if enemy.alive:
                enemy_rect = pygame.Rect(enemy.position[0]-15, enemy.position[1]-15, 30, 30)
                if player_rect.colliderect(enemy_rect):
                    # Игрок получает урон от врага
                    damage = enemy.damage_output * random.uniform(0.8, 1.2)
                    self.player.take_damage({
                        "amount": damage,
                        "type": "physical",
                        "source": enemy
                    })
        
        # Проверка столкновений между игроком и боссом
        if self.boss.alive:
            boss_rect = pygame.Rect(self.boss.position[0]-30, self.boss.position[1]-30, 60, 60)
            if player_rect.colliderect(boss_rect):
                # Игрок получает урон от босса
                damage = self.boss.damage_output * random.uniform(0.9, 1.5)
                self.player.take_damage({
                    "amount": damage,
                    "type": "boss",
                    "source": self.boss
                })
    
    def draw_entities(self):
        # Отрисовка игрока
        color = (0, 100, 255) if self.player.alive else (50, 50, 50)
        pygame.draw.circle(self.screen, color, self.player.position, 20)
        
        # Отрисовка врагов
        for enemy in self.enemies:
            if enemy.alive:
                color = (255, 50, 50) if enemy.enemy_type == "warrior" else \
                        (200, 50, 150) if enemy.enemy_type == "archer" else \
                        (50, 150, 255)
                pygame.draw.circle(self.screen, color, enemy.position, 15)
        
        # Отрисовка босса
        if self.boss.alive:
            pygame.draw.circle(self.screen, (255, 165, 0), self.boss.position, 30)
            # Отображение фазы босса
            phase_text = self.font.render(f"Фаза: {self.boss.phase}", True, (255, 255, 0))
            self.screen.blit(phase_text, (self.boss.position[0]-20, self.boss.position[1]-40))
    
    def draw_ui(self):
        # Отображение уровня игрока
        level_text = self.font.render(f"Уровень: {self.player.level}", True, (255, 255, 255))
        self.screen.blit(level_text, (10, 10))
        
        # Отображение здоровья
        health_text = self.font.render(f"Здоровье: {int(self.player.health)}/{int(self.player.max_health)}", True, (255, 255, 255))
        self.screen.blit(health_text, (10, 40))
        
        # Отображение знаний
        knowledge_text = self.font.render(f"Известных слабостей: {len(self.player.known_weaknesses)}", True, (255, 255, 255))
        self.screen.blit(knowledge_text, (10, 70))
        
        # Отображение скорости обучения
        learn_text = self.font.render(f"Скорость обучения: {self.player.learning_rate:.2f}", True, (255, 255, 255))
        self.screen.blit(learn_text, (10, 100))
        
        # Отображение состояния босса
        if self.boss.alive:
            boss_health = self.font.render(f"Босс: {int(self.boss.health)}/{int(self.boss.max_health)}", True, (255, 100, 100))
            self.screen.blit(boss_health, (1000, 10))
    
    def game_over(self, message):
        """Обработка окончания игры"""
        game_over_font = pygame.font.SysFont(None, 72)
        game_over_text = game_over_font.render(message, True, (255, 50, 50))
        text_rect = game_over_text.get_rect(center=(600, 400))
        
        self.screen.blit(game_over_text, text_rect)
        pygame.display.flip()
        
        # Ожидание нажатия клавиши
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Перезапуск игры
                        self.__init__()
                        waiting = False
                    elif event.key == pygame.K_ESCAPE:
                        waiting = False
                        self.running = False
        
        if not self.running:
            pygame.quit()
            sys.exit()

def main():
    game = Game()
    asyncio.run(game.run())

if __name__ == "__main__":
    main()