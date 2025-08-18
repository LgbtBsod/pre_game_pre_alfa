import pygame 
from typing import List, Optional, Dict, Any, Tuple
from .ui import UI
from .particles import AnimationPlayer
from .magic import MagicPlayer
from .upgrade import Upgrade
from .core.resource_manager import ResourceManager
from .core.game_data import GameDataManager
from .core.audio_manager import AudioManager
from .core.logger import get_logger
from .core.config import ConfigManager
from .core.game_state import GameState, GameStateManager
from .core.map_manager import MapManager
from .core.entity_manager import EntityManager
from .core.camera_manager import CameraManager
from .core.entity_factory import EntityFactory

class Level:
	"""
	Класс уровня, отвечающий за координацию различных менеджеров.
	Теперь следует принципу единой ответственности, делегируя задачи специализированным менеджерам.
	"""
	
	def __init__(self, 
				 resource_manager: Optional[ResourceManager] = None,
				 game_data_manager: Optional[GameDataManager] = None,
				 audio_manager: Optional[AudioManager] = None,
				 config_manager: Optional[ConfigManager] = None,
				 state_manager: Optional[GameStateManager] = None):
		
		self.logger = get_logger()
		
		# Основные системы
		self.resource_manager = resource_manager
		self.game_data_manager = game_data_manager
		self.audio_manager = audio_manager
		self.config_manager = config_manager
		self.state_manager = state_manager

		# Поверхность отображения
		self.display_surface = pygame.display.get_surface()

		# Инициализация менеджеров
		self._initialize_managers()

		# Создание карты
		self.create_map()

		# Пользовательский интерфейс
		self.ui = UI()
		self.upgrade: Optional[Upgrade] = None

		# Частицы и магия
		self.animation_player = AnimationPlayer()
		self.magic_player = MagicPlayer(self.animation_player)

	def _initialize_managers(self) -> None:
		"""Инициализирует все менеджеры согласно принципу единой ответственности"""
		try:
			# Map Manager - отвечает за загрузку и управление картами
			self.map_manager = MapManager(self.resource_manager)
			
			# Entity Factory - отвечает за создание сущностей
			self.entity_factory = EntityFactory(
				self.resource_manager,
				self.game_data_manager,
				self.audio_manager,
				self.config_manager
			)
			
			# Entity Manager - отвечает за управление жизненным циклом сущностей
			self.entity_manager = EntityManager(self.entity_factory)
			
			# Camera Manager - отвечает за управление камерой
			screen_size = self.display_surface.get_size()
			self.camera_manager = CameraManager(screen_size)
			
			# Настройка callbacks для Entity Manager
			self._setup_entity_callbacks()
			
			self.logger.info("All managers initialized successfully")
			
		except Exception as e:
			self.logger.error(f"Failed to initialize managers: {e}")

	def _setup_entity_callbacks(self) -> None:
		"""Настраивает callbacks для Entity Manager"""
		callbacks = {
			'create_attack': self.create_attack,
			'destroy_attack': self.destroy_attack,
			'create_magic': self.create_magic,
			'damage_player': self.damage_player,
			'trigger_death_particles': self.trigger_death_particles,
			'add_exp': self.add_exp
		}
		self.entity_manager.set_callbacks(callbacks)

	def create_map(self) -> None:
		"""Создает карту уровня, используя Map Manager"""
		try:
			# Загружаем данные карты через Map Manager
			layouts, graphics = self.map_manager.load_map_data()
			
			if not layouts or not graphics:
				self.logger.warning("Failed to load map data, creating fallback map")
				layouts, graphics = self.map_manager.create_fallback_map()
			
			# Создаем тайлы и сущности через Entity Manager
			self._create_tiles_and_entities(layouts, graphics)
			
			# Валидируем созданную карту
			if not self.entity_manager.validate_entities():
				self.logger.error("Entity validation failed")
			
			self.logger.info("Map created successfully")
			
		except Exception as e:
			self.logger.error(f"Error creating map: {e}")

	def _create_tiles_and_entities(self, layouts: Dict[str, List[List[str]]], 
								 graphics: Dict[str, List[pygame.Surface]]) -> None:
		"""Создает тайлы и сущности на основе данных карты"""
		try:
			for style, layout in layouts.items():
				for row_index, row in enumerate(layout):
					for col_index, col in enumerate(row):
						x = col_index * self.map_manager.tile_size
						y = row_index * self.map_manager.tile_size
						
						if col != '-1':  # Пропускаем пустые ячейки
							self._create_tile_or_entity(style, col, (x, y), graphics)
							
		except Exception as e:
			self.logger.error(f"Error creating tiles and entities: {e}")

	def _create_tile_or_entity(self, style: str, col: str, position: Tuple[int, int], 
							  graphics: Dict[str, List[pygame.Surface]]) -> None:
		"""Создает тайл или сущность в зависимости от стиля"""
		try:
			# Безопасное преобразование col в строку
			col_str = str(int(float(col))) if isinstance(col, (int, float)) else str(col)
			
			if style == 'boundary':
				self.entity_manager.create_tile(position, 'invisible')
				
			elif style == 'grass':
				grass_surface = self._get_random_grass(graphics.get('grass', []))
				self.entity_manager.create_tile(position, 'grass', grass_surface)

			elif style == 'object':
				if graphics.get('objects') and col_str.isdigit():
					try:
						obj_index = int(col_str)
						if 0 <= obj_index < len(graphics['objects']):
							surf = graphics['objects'][obj_index]
							self.entity_manager.create_tile(position, 'object', surf)
					except (ValueError, IndexError) as e:
						self.logger.warning(f"Invalid object index {col_str}: {e}")

			elif style == 'entities':
				self._create_entity(col_str, position)
				
		except Exception as e:
			self.logger.error(f"Error creating tile/entity at {position}: {e}")

	def _get_random_grass(self, grass_images: List[pygame.Surface]) -> Optional[pygame.Surface]:
		"""Возвращает случайное изображение травы"""
		import random
		return random.choice(grass_images) if grass_images else None

	def _create_entity(self, entity_id: str, pos: Tuple[int, int]) -> None:
		"""Создает сущность на основе ID через Entity Manager"""
		try:
			entity_type = self.map_manager.entity_mapping.get(entity_id)
			
			if entity_type == 'player':
				player = self.entity_manager.create_player(pos)
				if player:
					# Создаем Upgrade после создания игрока
					self.upgrade = Upgrade(player)
					self.logger.info(f"Created player at position {pos}")
				else:
					self.logger.error("Failed to create player")
					
			elif entity_type in ['bamboo', 'spirit', 'raccoon', 'squid']:
				enemy = self.entity_manager.create_enemy(entity_type, pos)
				if enemy:
					self.logger.info(f"Created {entity_type} enemy at position {pos}")
				else:
					self.logger.error(f"Failed to create {entity_type} enemy")
			else:
				self.logger.debug(f"Unknown entity ID: {entity_id}")
				
		except Exception as e:
			self.logger.error(f"Failed to create entity {entity_id}: {e}")

	def create_attack(self) -> None:
		"""Создает атаку игрока"""
		player = self.entity_manager.get_player()
		if player:
			weapon = self.entity_manager.create_weapon('sword', player.rect.center)
			if weapon:
				self.current_attack = weapon

	def create_magic(self, style: str, strength: int, cost: int) -> None:
		"""Создает магический эффект"""
		player = self.entity_manager.get_player()
		if player and style == 'heal':
			self.magic_player.heal(player, strength, cost, [self.entity_manager.get_sprite_group('visible')])
		elif player and style == 'flame':
			self.magic_player.flame(player, cost, [self.entity_manager.get_sprite_group('visible')])

	def destroy_attack(self) -> None:
		"""Уничтожает текущую атаку"""
		if hasattr(self, 'current_attack') and self.current_attack:
			self.current_attack = None

	def damage_player(self, amount: int, attack_type: str) -> None:
		"""Наносит урон игроку"""
		player = self.entity_manager.get_player()
		if player:
			player.get_damage(amount, attack_type)

	def trigger_death_particles(self, pos: Tuple[int, int], monster_name: str) -> None:
		"""Запускает частицы смерти"""
		self.animation_player.create_particles(monster_name, pos, [self.entity_manager.get_sprite_group('visible')])

	def add_exp(self, amount: int) -> None:
		"""Добавляет опыт игроку"""
		player = self.entity_manager.get_player()
		if player:
			player.exp += amount

	def player_attack_logic(self) -> None:
		"""Логика атаки игрока"""
		from random import randint
		
		if self.entity_manager.get_sprite_group('attack') and self.entity_manager.get_sprite_group('attackable'):
			for attack_sprite in self.entity_manager.get_sprite_group('attack'):
				for attackable_sprite in self.entity_manager.get_sprite_group('attackable'):
					if attack_sprite.rect.colliderect(attackable_sprite.rect):
						if attackable_sprite.sprite_type == 'grass':
							pos = attackable_sprite.rect.center
							offset = pygame.math.Vector2(0, 75)
							for leaf in range(randint(3, 6)):
								self.animation_player.create_grass_particles(pos - offset, [self.entity_manager.get_sprite_group('visible')])
							attackable_sprite.kill()
						else:
							attackable_sprite.get_damage(self.entity_manager.get_player(), attack_sprite.sprite_type)

	def run(self) -> None:
		"""Основной цикл обновления уровня"""
		# Проверяем, что игрок существует
		player = self.entity_manager.get_player()
		if not player:
			# Создаем игрока по умолчанию, если он не найден
			self.logger.warning("Player not found in level, creating default player")
			player = self.entity_manager.create_player((400, 400))  # Центр экрана
			if not player:
				self.logger.error("Failed to create default player")
				return
			
		# Обновляем камеру
		self.camera_manager.set_target(player)
		self.camera_manager.update(1/60)  # TODO: Use actual delta time
		
		# Отрисовка
		self._render_level()
		self.ui.display(player)
		
		# Проверяем состояние игры
		if self.state_manager and self.state_manager.is_state(GameState.PAUSED):
			if self.upgrade:
				self.upgrade.display()
		else:
			# Обновление игровой логики
			self.entity_manager.update_entities(1/60)  # TODO: Use actual delta time
			self.player_attack_logic()

	def _render_level(self) -> None:
		"""Отрисовывает уровень через Camera Manager"""
		# Отрисовка пола
		self.camera_manager.render_floor(self.display_surface)
		
		# Отрисовка сущностей
		visible_sprites = self.entity_manager.get_sprite_group('visible').sprites()
		self.camera_manager.render_sprites(self.display_surface, visible_sprites)

	def get_level_info(self) -> Dict[str, Any]:
		"""Получает информацию об уровне"""
		info = {
			'map_info': self.map_manager.get_map_info(),
			'entity_stats': self.entity_manager.get_entity_statistics(),
			'camera_info': self.camera_manager.get_camera_info(),
			'player_exists': self.entity_manager.get_player() is not None
		}
		return info

	def cleanup(self) -> None:
		"""Очищает ресурсы уровня"""
		try:
			self.map_manager.cleanup()
			self.entity_manager.cleanup()
			self.camera_manager.cleanup()
			self.logger.info("Level cleanup completed")
		except Exception as e:
			self.logger.error(f"Error during level cleanup: {e}")
