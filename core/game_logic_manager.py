"""
Менеджер игровой логики - управляет столкновениями, движением и взаимодействиями
"""
import random
import math
from typing import List, Optional, Tuple, Any, TYPE_CHECKING
from combat.damage_system import DamageSystem

from core.game_state_manager import GameStateManager

# Убираем циклический импорт
if TYPE_CHECKING:
    from entities.entity_refactored import Entity


class GameLogicManager:
    """Управляет игровой логикой: столкновения, движение, взаимодействия"""
    
    def __init__(self, game_state: GameStateManager):
        self.game_state = game_state
        
    def update(self, delta_time: float) -> None:
        """Обновление игровой логики"""
        self._update_player_ai(delta_time)
        self._update_entity_movement(delta_time)
        self._check_collisions()
        self._process_chest_interactions()
        
    def _update_player_ai(self, delta_time: float) -> None:
        """Обновление AI игрока"""
        if not self.game_state.player or not self.game_state.player.alive:
            return
            
        target_pos = self._get_player_target()
        if target_pos is None:
            return
            
        speed = float(self.game_state.player.movement_speed)
        self._move_entity_toward(self.game_state.player, target_pos, speed, delta_time)
        
    def _get_player_target(self) -> Optional[Tuple[float, float]]:
        """Определение цели для игрока"""
        # Приоритет: сундуки (если здоровье низкое) -> босс -> враги
        if self.game_state.chests and self.game_state.player.health < self.game_state.player.max_health * 0.7:
            return self._get_nearest_chest_world_pos(self.game_state.player.position)
            
        if self.game_state.boss and self.game_state.boss.alive:
            return self.game_state.boss.position
            
        alive_enemies = [e for e in self.game_state.enemies if e.alive]
        if alive_enemies:
            target = min(alive_enemies, key=lambda e: self._dist2(self.game_state.player.position, e.position))
            return target.position
            
        return None
        
    def _update_entity_movement(self, delta_time: float) -> None:
        """Обновление движения сущностей"""
        # Движение врагов к игроку
        for enemy in self.game_state.enemies:
            if enemy.alive and self.game_state.player:
                speed = enemy.movement_speed
                self._move_entity_toward(enemy, self.game_state.player.position, speed, delta_time)
                
        # Движение босса к игроку
        if self.game_state.boss and self.game_state.boss.alive and self.game_state.player:
            speed = self.game_state.boss.movement_speed
            self._move_entity_toward(self.game_state.boss, self.game_state.player.position, speed, delta_time)
            
    def _move_entity_toward(self, entity: 'Entity', target_pos: Tuple[float, float], speed: float, delta_time: float) -> None:
        """Движение сущности к цели с учетом препятствий"""
        ex, ey = entity.position
        tx, ty = target_pos
        
        dx = tx - ex
        dy = ty - ey
        dist = max(1e-6, math.sqrt(dx * dx + dy * dy))
        
        nx, ny = dx / dist, dy / dist
        step_x = ex + nx * speed * delta_time
        step_y = ey + ny * speed * delta_time
        
        # Проверка препятствий
        if self._is_blocked_pixel(step_x, step_y):
            # Попытка обхода препятствия
            ax, ay = ny, -nx  # Перпендикулярное направление
            step1_x = ex + ax * speed * delta_time
            step1_y = ey + ay * speed * delta_time
            
            if not self._is_blocked_pixel(step1_x, step1_y):
                entity.position[0], entity.position[1] = step1_x, step1_y
                return
                
            # Вторая попытка обхода
            bx, by = -ny, nx
            step2_x = ex + bx * speed * delta_time
            step2_y = ey + by * speed * delta_time
            
            if not self._is_blocked_pixel(step2_x, step2_y):
                entity.position[0], entity.position[1] = step2_x, step2_y
                return
                
            return  # Не удалось обойти препятствие
            
        # Обычное движение
        entity.position[0], entity.position[1] = step_x, step_y
        
    def _is_blocked_pixel(self, x: float, y: float) -> bool:
        """Проверка, заблокирована ли позиция"""
        if not hasattr(self.game_state, 'tiled_map') or not self.game_state.tiled_map:
            return False
            
        tw, th = self.game_state.tiled_map.tilewidth, self.game_state.tiled_map.tileheight
        tx, ty = int(x // tw), int(y // th)
        return (tx, ty) in self.game_state.user_obstacles
        
    def _check_collisions(self) -> None:
        """Проверка столкновений"""
        if not self.game_state.player or not self.game_state.player.alive:
            return
            
        px, py = self.game_state.player.position
        
        # Столкновения с врагами
        for enemy in self.game_state.enemies:
            if not enemy.alive:
                continue
                
            ex, ey = enemy.position
            dx = px - ex
            dy = py - ey
            collision_distance = 20 + 15  # Радиус игрока + радиус врага
            
            if (dx * dx + dy * dy) <= collision_distance * collision_distance:
                damage = enemy.damage_output * random.uniform(0.8, 1.2)
                self.game_state.player.take_damage({
                    "total": damage,
                    "physical": damage,
                    "source": enemy,
                })
                
        # Столкновения с боссом
        if self.game_state.boss and self.game_state.boss.alive:
            bx, by = self.game_state.boss.position
            dx = px - bx
            dy = py - by
            collision_distance = 20 + 30  # Радиус игрока + радиус босса
            
            if (dx * dx + dy * dy) <= collision_distance * collision_distance:
                damage = self.game_state.boss.damage_output * random.uniform(0.9, 1.5)
                self.game_state.player.take_damage({
                    "total": damage,
                    "boss": damage,
                    "source": self.game_state.boss,
                })
                
    def _process_chest_interactions(self) -> None:
        """Обработка взаимодействий с сундуками"""
        if not self.game_state.chests or not hasattr(self.game_state, 'tiled_map') or not self.game_state.tiled_map:
            return
            
        tw, th = self.game_state.tiled_map.tilewidth, self.game_state.tiled_map.tileheight
        
        # Проверка для игрока
        if self.game_state.player:
            self._check_entity_chest_interaction(self.game_state.player, tw, th)
            
        # Проверка для врагов
        for enemy in self.game_state.enemies:
            if enemy.alive:
                self._check_entity_chest_interaction(enemy, tw, th)
                
        # Проверка для босса
        if self.game_state.boss and self.game_state.boss.alive:
            self._check_entity_chest_interaction(self.game_state.boss, tw, th)
            
    def _check_entity_chest_interaction(self, entity: 'Entity', tile_width: int, tile_height: int) -> None:
        """Проверка взаимодействия сущности с сундуком"""
        ex, ey = entity.position
        etx, ety = int(ex // tile_width), int(ey // tile_height)
        
        for chest in list(self.game_state.chests):
            if chest.get("opened"):
                continue
                
            if chest["tx"] == etx and chest["ty"] == ety:
                # Восстановление здоровья
                entity.health = min(entity.max_health, entity.health + 20)
                chest["opened"] = True
                
    def _get_nearest_chest_world_pos(self, from_pos: Tuple[float, float]) -> Optional[Tuple[float, float]]:
        """Получение позиции ближайшего сундука в мировых координатах"""
        if not self.game_state.chests:
            return None
            
        fx, fy = from_pos
        best, best_d2 = None, None
        
        if hasattr(self.game_state, 'tiled_map') and self.game_state.tiled_map:
            tw = self.game_state.tiled_map.tilewidth
            th = self.game_state.tiled_map.tileheight
        else:
            tw, th = 40, 40
            
        for chest in self.game_state.chests:
            cx = chest["tx"] * tw + tw / 2
            cy = chest["ty"] * th + th / 2
            d2 = (cx - fx) ** 2 + (cy - fy) ** 2
            
            if best is None or d2 < best_d2:
                best, best_d2 = (cx, cy), d2
                
        return best
        
    def _dist2(self, a: Tuple[float, float], b: Tuple[float, float]) -> float:
        """Квадрат расстояния между двумя точками"""
        ax, ay = a
        bx, by = b
        return (ax - bx) ** 2 + (ay - by) ** 2
        
    def add_obstacle(self, tile_x: int, tile_y: int) -> None:
        """Добавление препятствия"""
        if (tile_x, tile_y) in self.game_state.user_obstacles:
            # Убираем препятствие при повторном клике
            self.game_state.user_obstacles.remove((tile_x, tile_y))
        else:
            # Добавляем препятствие
            self.game_state.user_obstacles.add((tile_x, tile_y))
            
    def add_chest(self, tile_x: int, tile_y: int) -> None:
        """Добавление сундука"""
        # Проверяем, есть ли уже сундук в этой точке
        existing_chest = None
        for chest in self.game_state.chests:
            if chest["tx"] == tile_x and chest["ty"] == tile_y:
                existing_chest = chest
                break
                
        if existing_chest:
            # Убираем сундук при повторном клике
            self.game_state.chests.remove(existing_chest)
        else:
            # Добавляем сундук
            self.game_state.chests.append({"tx": tile_x, "ty": tile_y, "opened": False})
            
    def process_effects(self, delta_time: float) -> None:
        """Обработка эффектов для всех сущностей"""
        # Обработка эффектов игрока
        if self.game_state.player:
            DamageSystem.process_entity_effects(self.game_state.player, delta_time)
            
        # Обработка эффектов врагов
        for enemy in self.game_state.enemies:
            if enemy.alive:
                DamageSystem.process_entity_effects(enemy, delta_time)
                
        # Обработка эффектов босса
        if self.game_state.boss and self.game_state.boss.alive:
            DamageSystem.process_entity_effects(self.game_state.boss, delta_time)
            
    def use_skill(self, skill_id: str) -> bool:
        """Использование навыка"""
        if not self.game_state.skill_system or not self.game_state.player:
            return False
            
        success = self.game_state.skill_system.use_skill(skill_id, self.game_state.player)
        return success
