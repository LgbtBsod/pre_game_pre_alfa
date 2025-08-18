"""
Основной игровой цикл с интеграцией всех систем.
Объединяет эволюционные циклы, процедурную генерацию и косвенное управление.
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from .effect_system import EffectDatabase
from .genetic_system import AdvancedGeneticSystem
from .emotion_system import AdvancedEmotionSystem
from .ai_system import AdaptiveAISystem
from .content_generator import ContentGenerator
from .evolution_system import EvolutionCycleSystem
from .advanced_entity import AdvancedGameEntity

logger = logging.getLogger(__name__)


class GameWorld:
    """Игровой мир"""
    
    def __init__(self, seed: int = None):
        self.seed = seed or random.randint(1, 999999)
        self.name = f"World_{self.seed}"
        self.entities: List[AdvancedGameEntity] = []
        self.player = None
        self.explored_areas = 0
        self.total_areas = 100
        self.explored_percent = 0.0
        self.weather = "clear"
        self.time_of_day = 0.0
        self.day_cycle = 0
        
        # Экосистема
        self.ecosystem = {
            "predators": 0,
            "prey": 0,
            "neutral": 0,
            "balance": 1.0
        }
        
        # Глобальные события
        self.active_events = []
        self.event_history = []
        
        logger.info(f"Создан игровой мир: {self.name} (seed: {self.seed})")
    
    def add_entity(self, entity: AdvancedGameEntity):
        """Добавление сущности в мир"""
        self.entities.append(entity)
        
        # Обновление экосистемы
        if entity.type == "enemy":
            self.ecosystem["predators"] += 1
        elif entity.type == "creature":
            self.ecosystem["prey"] += 1
        elif entity.type == "npc":
            self.ecosystem["neutral"] += 1
        
        # Обновление баланса экосистемы
        self._update_ecosystem_balance()
        
        logger.info(f"Добавлена сущность {entity.id} в мир")
    
    def remove_entity(self, entity: AdvancedGameEntity):
        """Удаление сущности из мира"""
        if entity in self.entities:
            self.entities.remove(entity)
            
            # Обновление экосистемы
            if entity.type == "enemy":
                self.ecosystem["predators"] = max(0, self.ecosystem["predators"] - 1)
            elif entity.type == "creature":
                self.ecosystem["prey"] = max(0, self.ecosystem["prey"] - 1)
            elif entity.type == "npc":
                self.ecosystem["neutral"] = max(0, self.ecosystem["neutral"] - 1)
            
            # Обновление баланса экосистемы
            self._update_ecosystem_balance()
            
            logger.info(f"Удалена сущность {entity.id} из мира")
    
    def _update_ecosystem_balance(self):
        """Обновление баланса экосистемы"""
        total_entities = sum(self.ecosystem.values()) - self.ecosystem["balance"]
        
        if total_entities > 0:
            predator_ratio = self.ecosystem["predators"] / total_entities
            prey_ratio = self.ecosystem["prey"] / total_entities
            
            # Идеальный баланс: 1 хищник на 3 жертвы
            ideal_ratio = 0.25
            self.ecosystem["balance"] = 1.0 - abs(predator_ratio - ideal_ratio)
        else:
            self.ecosystem["balance"] = 1.0
    
    def update_exploration(self, new_areas: int):
        """Обновление прогресса исследования"""
        self.explored_areas = min(self.total_areas, self.explored_areas + new_areas)
        self.explored_percent = self.explored_areas / self.total_areas
        
        logger.info(f"Прогресс исследования: {self.explored_percent:.1%}")
    
    def update_time(self, delta_time: float):
        """Обновление времени в мире"""
        self.time_of_day += delta_time
        
        # Цикл дня (24 игровых часа = 24 реальных минуты)
        day_length = 24 * 60  # секунды
        if self.time_of_day >= day_length:
            self.time_of_day = 0
            self.day_cycle += 1
            
            # Смена погоды
            self._change_weather()
            
            logger.info(f"Наступил день {self.day_cycle}")
    
    def _change_weather(self):
        """Смена погоды"""
        weather_options = ["clear", "cloudy", "rainy", "stormy", "foggy"]
        weights = [0.4, 0.3, 0.15, 0.1, 0.05]  # Вероятности погоды
        
        self.weather = random.choices(weather_options, weights=weights)[0]
        logger.info(f"Погода изменилась на: {self.weather}")
    
    def get_entities_in_radius(self, position, radius: float) -> List[AdvancedGameEntity]:
        """Получение сущностей в радиусе от позиции"""
        nearby_entities = []
        
        for entity in self.entities:
            if entity.is_active:
                distance = position.distance_to(entity.position)
                if distance <= radius:
                    nearby_entities.append(entity)
        
        return nearby_entities
    
    def get_world_info(self) -> Dict[str, Any]:
        """Получение информации о мире"""
        return {
            "name": self.name,
            "seed": self.seed,
            "total_entities": len(self.entities),
            "explored_percent": self.explored_percent,
            "weather": self.weather,
            "time_of_day": self.time_of_day,
            "day_cycle": self.day_cycle,
            "ecosystem": self.ecosystem.copy(),
            "active_events": len(self.active_events)
        }


class GameLoop:
    """Основной игровой цикл"""
    
    def __init__(self):
        # Инициализация систем
        self.effect_db = EffectDatabase()
        self.content_generator = ContentGenerator()
        self.evolution_system = EvolutionCycleSystem(self.effect_db)
        
        # Игровое состояние
        self.current_world = None
        self.current_player = None
        self.game_time = 0.0
        self.is_running = False
        self.is_paused = False
        
        # Настройки
        self.target_fps = 60
        self.frame_time = 1.0 / self.target_fps
        
        # Статистика
        self.frames_rendered = 0
        self.fps_counter = 0
        self.last_fps_update = 0.0
        
        logger.info("Игровой цикл инициализирован")
    
    def start_new_game(self, seed: int = None) -> bool:
        """Начало новой игры"""
        try:
            # Создание нового мира
            self.content_generator.set_seed(seed or random.randint(1, 999999))
            world_data = self.content_generator.generate_world()
            
            self.current_world = GameWorld(world_data.seed)
            self.current_world.name = world_data.name
            
            # Создание игрока
            self.current_player = AdvancedGameEntity("PLAYER_01", "player", self.effect_db)
            self.current_world.player = self.current_player
            self.current_world.add_entity(self.current_player)
            
            # Генерация начального контента
            self._generate_initial_content()
            
            # Сброс времени
            self.game_time = 0.0
            self.frames_rendered = 0
            
            self.is_running = True
            self.is_paused = False
            
            logger.info(f"Начата новая игра в мире {self.current_world.name}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка начала новой игры: {e}")
            return False
    
    def _generate_initial_content(self):
        """Генерация начального контента"""
        try:
            # Генерация врагов
            num_enemies = random.randint(5, 15)
            for i in range(num_enemies):
                enemy = AdvancedGameEntity(f"ENEMY_{i:03d}", "enemy", self.effect_db)
                enemy.position.x = random.uniform(10, 90)
                enemy.position.y = random.uniform(10, 90)
                self.current_world.add_entity(enemy)
            
            # Генерация NPC
            num_npcs = random.randint(2, 5)
            for i in range(num_npcs):
                npc = AdvancedGameEntity(f"NPC_{i:03d}", "npc", self.effect_db)
                npc.position.x = random.uniform(20, 80)
                npc.position.y = random.uniform(20, 80)
                self.current_world.add_entity(npc)
            
            # Генерация существ
            num_creatures = random.randint(8, 20)
            for i in range(num_creatures):
                creature = AdvancedGameEntity(f"CREATURE_{i:03d}", "creature", self.effect_db)
                creature.position.x = random.uniform(5, 95)
                creature.position.y = random.uniform(5, 95)
                self.current_world.add_entity(creature)
            
            logger.info(f"Сгенерирован начальный контент: {num_enemies} врагов, {num_npcs} NPC, {num_creatures} существ")
            
        except Exception as e:
            logger.error(f"Ошибка генерации начального контента: {e}")
    
    def run(self):
        """Запуск игрового цикла"""
        if not self.is_running:
            logger.error("Игра не инициализирована")
            return
        
        logger.info("Запуск игрового цикла")
        
        last_time = time.time()
        
        try:
            while self.is_running:
                current_time = time.time()
                delta_time = current_time - last_time
                
                # Ограничение FPS
                if delta_time < self.frame_time:
                    time.sleep(self.frame_time - delta_time)
                    delta_time = self.frame_time
                
                # Обновление игрового времени
                self.game_time += delta_time
                
                # Обновление FPS
                self._update_fps(delta_time)
                
                # Обработка ввода
                self._handle_input()
                
                # Обновление игры
                if not self.is_paused:
                    self._update_game(delta_time)
                
                # Рендеринг
                self._render()
                
                # Проверка завершения цикла
                self._check_cycle_completion()
                
                last_time = current_time
                
        except KeyboardInterrupt:
            logger.info("Игровой цикл прерван пользователем")
        except Exception as e:
            logger.error(f"Критическая ошибка в игровом цикле: {e}")
        finally:
            self._cleanup()
    
    def _update_fps(self, delta_time: float):
        """Обновление счётчика FPS"""
        self.fps_counter += 1
        self.last_fps_update += delta_time
        
        if self.last_fps_update >= 1.0:
            current_fps = self.fps_counter / self.last_fps_update
            logger.debug(f"FPS: {current_fps:.1f}")
            
            self.fps_counter = 0
            self.last_fps_update = 0.0
    
    def _handle_input(self):
        """Обработка ввода"""
        # Здесь будет логика обработки ввода
        # Пока что просто заглушка
        pass
    
    def _update_game(self, delta_time: float):
        """Обновление игровой логики"""
        try:
            # Обновление мира
            if self.current_world:
                self.current_world.update_time(delta_time)
            
            # Обновление сущностей
            if self.current_world:
                for entity in self.current_world.entities[:]:  # Копия списка для безопасного удаления
                    if entity.is_active:
                        entity.update(delta_time, self.current_world)
                    else:
                        # Удаление неактивных сущностей
                        self.current_world.remove_entity(entity)
            
            # Генерация нового контента
            self._generate_dynamic_content(delta_time)
            
            # Обновление глобальных событий
            self._update_global_events(delta_time)
            
        except Exception as e:
            logger.error(f"Ошибка обновления игры: {e}")
    
    def _generate_dynamic_content(self, delta_time: float):
        """Динамическая генерация контента"""
        try:
            if not self.current_world:
                return
            
            # Генерация новых врагов каждые 30 секунд
            if int(self.game_time) % 30 == 0 and len([e for e in self.current_world.entities if e.type == "enemy"]) < 20:
                num_new_enemies = random.randint(1, 3)
                for i in range(num_new_enemies):
                    enemy = AdvancedGameEntity(f"ENEMY_{random.randint(100, 999)}", "enemy", self.effect_db)
                    enemy.position.x = random.uniform(0, 100)
                    enemy.position.y = random.uniform(0, 100)
                    self.current_world.add_entity(enemy)
                
                logger.info(f"Сгенерировано {num_new_enemies} новых врагов")
            
            # Генерация ресурсов каждые 60 секунд
            if int(self.game_time) % 60 == 0:
                # Здесь будет генерация ресурсов
                pass
                
        except Exception as e:
            logger.error(f"Ошибка динамической генерации контента: {e}")
    
    def _update_global_events(self, delta_time: float):
        """Обновление глобальных событий"""
        try:
            if not self.current_world:
                return
            
            # События каждые 2 минуты
            if int(self.game_time) % 120 == 0:
                event_type = random.choice([
                    "genetic_surge",
                    "emotional_storm",
                    "ai_awakening",
                    "cosmic_disturbance"
                ])
                
                self._trigger_global_event(event_type)
                
        except Exception as e:
            logger.error(f"Ошибка обновления глобальных событий: {e}")
    
    def _trigger_global_event(self, event_type: str):
        """Триггер глобального события"""
        try:
            event_data = {
                "type": event_type,
                "timestamp": self.game_time,
                "duration": random.uniform(30, 120),
                "effects": []
            }
            
            if event_type == "genetic_surge":
                event_data["effects"] = ["mutation_rate_increased", "gene_combinations_enhanced"]
                # Применение эффектов ко всем сущностям
                for entity in self.current_world.entities:
                    if hasattr(entity, 'genetic_system'):
                        entity.genetic_system.mutation_resistance *= 0.8
            
            elif event_type == "emotional_storm":
                event_data["effects"] = ["emotions_intensified", "emotional_resonance_boosted"]
                # Применение эффектов ко всем сущностям
                for entity in self.current_world.entities:
                    if hasattr(entity, 'emotion_system'):
                        entity.emotion_system.trigger_emotion("EMO_109", 0.5, "global_event")  # Удивление
            
            elif event_type == "ai_awakening":
                event_data["effects"] = ["ai_learning_accelerated", "ai_adaptation_enhanced"]
                # Применение эффектов ко всем сущностям
                for entity in self.current_world.entities:
                    if hasattr(entity, 'ai_system'):
                        entity.ai_system.q_agent.adaptive_learning_rate *= 1.5
            
            elif event_type == "cosmic_disturbance":
                event_data["effects"] = ["reality_shifted", "dimensions_merged"]
                # Случайные эффекты для всех сущностей
                for entity in self.current_world.entities:
                    random_effect = random.choice([
                        "teleport", "transform", "enhance", "weaken"
                    ])
                    if random_effect == "teleport":
                        entity.position.x = random.uniform(0, 100)
                        entity.position.y = random.uniform(0, 100)
            
            self.current_world.active_events.append(event_data)
            self.current_world.event_history.append(event_data)
            
            logger.info(f"Триггер глобального события: {event_type}")
            
        except Exception as e:
            logger.error(f"Ошибка триггера глобального события: {e}")
    
    def _render(self):
        """Рендеринг игры"""
        # Здесь будет логика рендеринга
        # Пока что просто увеличение счётчика кадров
        self.frames_rendered += 1
    
    def _check_cycle_completion(self):
        """Проверка завершения эволюционного цикла"""
        try:
            if not self.current_world or not self.current_player:
                return
            
            # Условия завершения цикла
            cycle_completed = False
            completion_reason = ""
            
            # Завершение по исследованию мира
            if self.current_world.explored_percent >= 0.8:
                cycle_completed = True
                completion_reason = "exploration_complete"
            
            # Завершение по достижению маяка
            if hasattr(self.current_player, 'reached_beacon') and self.current_player.reached_beacon:
                cycle_completed = True
                completion_reason = "beacon_reached"
            
            # Завершение по времени (максимум 1 час реального времени)
            if self.game_time >= 3600:
                cycle_completed = True
                completion_reason = "time_limit"
            
            if cycle_completed:
                self._complete_evolution_cycle(completion_reason)
                
        except Exception as e:
            logger.error(f"Ошибка проверки завершения цикла: {e}")
    
    def _complete_evolution_cycle(self, reason: str):
        """Завершение эволюционного цикла"""
        try:
            logger.info(f"Завершение эволюционного цикла по причине: {reason}")
            
            # Завершение цикла через систему эволюции
            cycle_result = self.evolution_system.complete_cycle(self.current_player, self.current_world)
            
            if cycle_result.get("cycle_completed"):
                # Начало нового цикла
                new_cycle_data = self.evolution_system.start_new_cycle(self.current_player, cycle_result)
                
                # Обновление игрового состояния
                self.current_world = new_cycle_data["world"]
                self.current_player = new_cycle_data["player"]
                self.current_world.player = self.current_player
                
                # Генерация нового контента
                self._generate_initial_content()
                
                # Сброс времени
                self.game_time = 0.0
                
                logger.info(f"Начат новый эволюционный цикл {new_cycle_data['cycle_number']}")
            else:
                logger.error("Ошибка завершения эволюционного цикла")
                
        except Exception as e:
            logger.error(f"Ошибка завершения эволюционного цикла: {e}")
    
    def pause_game(self):
        """Пауза игры"""
        self.is_paused = True
        logger.info("Игра поставлена на паузу")
    
    def resume_game(self):
        """Возобновление игры"""
        self.is_paused = False
        logger.info("Игра возобновлена")
    
    def stop_game(self):
        """Остановка игры"""
        self.is_running = False
        logger.info("Игра остановлена")
    
    def _cleanup(self):
        """Очистка ресурсов"""
        try:
            # Сохранение состояния
            if self.current_player:
                self.current_player.save_entity_state("save/player_state.json")
            
            if self.evolution_system:
                self.evolution_system.save_evolution_state("save/evolution_state.json")
            
            logger.info("Очистка ресурсов завершена")
            
        except Exception as e:
            logger.error(f"Ошибка очистки ресурсов: {e}")
    
    def get_game_stats(self) -> Dict[str, Any]:
        """Получение статистики игры"""
        try:
            stats = {
                "game_time": self.game_time,
                "frames_rendered": self.frames_rendered,
                "current_fps": self.fps_counter / max(self.last_fps_update, 0.001),
                "is_running": self.is_running,
                "is_paused": self.is_paused,
                "target_fps": self.target_fps
            }
            
            if self.current_world:
                stats.update(self.current_world.get_world_info())
            
            if self.current_player:
                stats["player_info"] = self.current_player.get_entity_info()
            
            if self.evolution_system:
                stats["evolution_summary"] = self.evolution_system.get_evolution_summary()
            
            return stats
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики игры: {e}")
            return {"error": str(e)}
    
    def save_game(self, filepath: str) -> bool:
        """Сохранение игры"""
        try:
            import json
            
            save_data = {
                "game_time": self.game_time,
                "frames_rendered": self.frames_rendered,
                "world_info": self.current_world.get_world_info() if self.current_world else {},
                "player_state": self.current_player.get_entity_info() if self.current_player else {},
                "evolution_state": self.evolution_system.get_evolution_summary()
            }
            
            # Создание директории для сохранений
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            logger.info(f"Игра сохранена в {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения игры: {e}")
            return False
    
    def load_game(self, filepath: str) -> bool:
        """Загрузка игры"""
        try:
            import json
            
            with open(filepath, 'r') as f:
                save_data = json.load(f)
            
            # Восстановление игрового времени
            self.game_time = save_data.get("game_time", 0.0)
            self.frames_rendered = save_data.get("frames_rendered", 0)
            
            # Восстановление мира
            world_info = save_data.get("world_info", {})
            if world_info:
                self.current_world = GameWorld(world_info.get("seed", random.randint(1, 999999)))
                self.current_world.name = world_info.get("name", f"World_{world_info.get('seed')}")
                self.current_world.explored_percent = world_info.get("explored_percent", 0.0)
                self.current_world.day_cycle = world_info.get("day_cycle", 0)
            
            # Восстановление игрока
            player_info = save_data.get("player_state", {})
            if player_info:
                self.current_player = AdvancedGameEntity("PLAYER_01", "player", self.effect_db)
                self.current_world.player = self.current_player
                self.current_world.add_entity(self.current_player)
            
            # Восстановление эволюционного состояния
            evolution_info = save_data.get("evolution_state", {})
            if evolution_info:
                # Здесь будет восстановление состояния эволюции
                pass
            
            self.is_running = True
            self.is_paused = False
            
            logger.info(f"Игра загружена из {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка загрузки игры: {e}")
            return False


def main_game_loop():
    """Основная функция игрового цикла"""
    try:
        # Создание и инициализация игрового цикла
        game_loop = GameLoop()
        
        # Начало новой игры
        if game_loop.start_new_game():
            # Запуск игрового цикла
            game_loop.run()
        else:
            logger.error("Не удалось начать новую игру")
            
    except Exception as e:
        logger.error(f"Критическая ошибка в главном игровом цикле: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Запуск игры
    main_game_loop()
