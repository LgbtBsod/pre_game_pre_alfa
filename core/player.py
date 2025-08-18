import pygame
from typing import List, Optional, Dict, Any, Tuple
from entity import Entity
from core.input_manager import InputManager, InputAction
from core.audio_manager import AudioManager
from core.game_data import GameDataManager, WeaponData, MagicData
from core.resource_manager import ResourceManager
from core.logger import get_logger
from core.config import ConfigManager

class Player(Entity):
	"""
	Класс игрока, отвечающий за управление персонажем, бой и статистику.
	Интегрирован с новыми основными системами.
	"""
	
	def __init__(self, 
				 pos: Tuple[int, int], 
				 groups: List[pygame.sprite.Group], 
				 obstacle_sprites: pygame.sprite.Group,
				 create_attack: callable,
				 destroy_attack: callable,
				 create_magic: callable,
				 input_manager: Optional[InputManager] = None,
				 audio_manager: Optional[AudioManager] = None,
				 resource_manager: Optional[ResourceManager] = None,
				 game_data_manager: Optional[GameDataManager] = None,
				 config_manager: Optional[ConfigManager] = None):
		
		super().__init__(groups)
		self.logger = get_logger()
		
		# Основные системы
		self.input_manager = input_manager
		self.audio_manager = audio_manager
		self.game_data_manager = game_data_manager
		self.config_manager = config_manager
		
		# Позиция и размеры
		self.image = pygame.Surface((64, 64))  # Используем константу вместо TILESIZE
		self.image.fill('yellow')
		self.rect = self.image.get_rect(topleft=pos)
		
		# Устанавливаем хитбокс и спрайты коллизий
		hitbox_offset = 6  # Константа вместо HITBOX_OFFSET['player']
		self.hitbox = self.rect.inflate(-hitbox_offset, -hitbox_offset)
		self.set_obstacle_sprites(obstacle_sprites)
		
		# Анимация
		self.import_player_assets()
		self.status = 'down'

		# Бой
		self.attacking = False
		self.attack_cooldown = 400
		self.attack_time: Optional[int] = None

		# Оружие
		self.create_attack = create_attack
		self.destroy_attack = destroy_attack
		self.weapon_index = 0
		self.weapon = self._get_default_weapon()
		self.can_switch_weapon = True
		self.weapon_switch_time: Optional[int] = None
		self.switch_duration_cooldown = 200

		# Магия
		self.create_magic = create_magic
		self.magic_index = 0
		self.magic = self._get_default_magic()
		self.can_switch_magic = True
		self.magic_switch_time: Optional[int] = None

		# Статистика
		self.stats = {'health': 100, 'energy': 60, 'attack': 10, 'magic': 4, 'speed': 5}
		self.max_stats = {'health': 300, 'energy': 140, 'attack': 20, 'magic': 10, 'speed': 10}
		self.upgrade_cost = {'health': 100, 'energy': 100, 'attack': 100, 'magic': 100, 'speed': 100}
		self.health = self.stats['health'] + 20
		self.energy = self.stats['energy']
		self.exp = 5000
		self.speed = self.stats['speed']

		# Таймер урона
		self.vulnerable = True
		self.hurt_time: Optional[int] = None
		self.invincibility_duration = 500

	def _get_default_weapon(self) -> str:
		"""Возвращает оружие по умолчанию."""
		if self.game_data_manager:
			weapons = list(self.game_data_manager.get_all_weapons().keys())
			return weapons[0] if weapons else 'sword'
		return 'sword'

	def _get_default_magic(self) -> str:
		"""Возвращает магию по умолчанию."""
		if self.game_data_manager:
			magic_spells = list(self.game_data_manager.get_all_magic().keys())
			return magic_spells[0] if magic_spells else 'heal'
		return 'heal'

	def import_player_assets(self) -> None:
		"""Загружает анимации игрока."""
		character_path = 'graphics/player/'
		self.animations = {
			'up': [], 'down': [], 'left': [], 'right': [],
			'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
			'right_attack': [], 'left_attack': [], 'up_attack': [], 'down_attack': []
		}

		for animation in self.animations.keys():
			full_path = character_path + animation
			animation_frames = self.load_animation_frames(full_path)
			self.animations[animation] = animation_frames

	def input(self) -> None:
		"""Обрабатывает ввод игрока."""
		if self.attacking:
			return

		if self.input_manager:
			# Движение через InputManager
			movement_vector = self.input_manager.get_movement_vector()
			self.direction.x = movement_vector[0]
			self.direction.y = movement_vector[1]
			
			# Обновляем статус на основе движения
			if self.direction.y < 0:
				self.status = 'up'
			elif self.direction.y > 0:
				self.status = 'down'
			elif self.direction.x > 0:
				self.status = 'right'
			elif self.direction.x < 0:
				self.status = 'left'

			# Атака
			if self.input_manager.is_action_just_pressed(InputAction.ATTACK):
				self._handle_attack()

			# Магия
			if self.input_manager.is_action_just_pressed(InputAction.MAGIC):
				self._handle_magic()

			# Переключение оружия
			if self.input_manager.is_action_just_pressed(InputAction.SWITCH_WEAPON):
				self._switch_weapon()

			# Переключение магии
			if self.input_manager.is_action_just_pressed(InputAction.SWITCH_MAGIC):
				self._switch_magic()
		else:
			# Fallback на прямое управление клавишами
			self._fallback_input()

	def _handle_attack(self) -> None:
		"""Обрабатывает атаку игрока."""
		self.attacking = True
		self.attack_time = pygame.time.get_ticks()
		self.create_attack()
		
		if self.audio_manager:
			self.audio_manager.play_sound('sword')

	def _handle_magic(self) -> None:
		"""Обрабатывает использование магии."""
		self.attacking = True
		self.attack_time = pygame.time.get_ticks()
		
		if self.game_data_manager:
			magic_data = self.game_data_manager.get_magic(self.magic)
			if magic_data:
				style = magic_data.name
				strength = magic_data.strength + self.stats['magic']
				cost = magic_data.cost
				self.create_magic(style, strength, cost)

	def _switch_weapon(self) -> None:
		"""Переключает оружие."""
		if not self.can_switch_weapon:
			return
			
		self.can_switch_weapon = False
		self.weapon_switch_time = pygame.time.get_ticks()
		
		if self.game_data_manager:
			weapons = list(self.game_data_manager.get_all_weapons().keys())
			if self.weapon_index < len(weapons) - 1:
				self.weapon_index += 1
			else:
				self.weapon_index = 0
			self.weapon = weapons[self.weapon_index]

	def _switch_magic(self) -> None:
		"""Переключает магию."""
		if not self.can_switch_magic:
			return
			
		self.can_switch_magic = False
		self.magic_switch_time = pygame.time.get_ticks()
		
		if self.game_data_manager:
			magic_spells = list(self.game_data_manager.get_all_magic().keys())
			if self.magic_index < len(magic_spells) - 1:
				self.magic_index += 1
			else:
				self.magic_index = 0
			self.magic = magic_spells[self.magic_index]

	def _fallback_input(self) -> None:
		"""Fallback обработка ввода без InputManager."""
		keys = pygame.key.get_pressed()

		# Движение
		if keys[pygame.K_UP]:
			self.direction.y = -1
			self.status = 'up'
		elif keys[pygame.K_DOWN]:
			self.direction.y = 1
			self.status = 'down'
		else:
			self.direction.y = 0

		if keys[pygame.K_RIGHT]:
			self.direction.x = 1
			self.status = 'right'
		elif keys[pygame.K_LEFT]:
			self.direction.x = -1
			self.status = 'left'
		else:
			self.direction.x = 0

		# Атака
		if keys[pygame.K_SPACE]:
			self._handle_attack()

		# Магия
		if keys[pygame.K_LCTRL]:
			self._handle_magic()

		# Переключение оружия
		if keys[pygame.K_q] and self.can_switch_weapon:
			self._switch_weapon()

		# Переключение магии
		if keys[pygame.K_e] and self.can_switch_magic:
			self._switch_magic()

	def get_status(self) -> None:
		"""Обновляет статус игрока на основе действий."""
		# Статус покоя
		if not self.is_moving():
			if not 'idle' in self.status and not 'attack' in self.status:
				self.status = self.status + '_idle'

		# Статус атаки
		if self.attacking:
			self.direction.x = 0
			self.direction.y = 0
			if not 'attack' in self.status:
				if 'idle' in self.status:
					self.status = self.status.replace('_idle', '_attack')
				else:
					self.status = self.status + '_attack'
		else:
			if 'attack' in self.status:
				self.status = self.status.replace('_attack', '')

	def cooldowns(self) -> None:
		"""Обрабатывает все кулдауны игрока."""
		current_time = pygame.time.get_ticks()

		# Кулдаун атаки
		if self.attacking and self.attack_time:
			weapon_cooldown = 0
			if self.game_data_manager:
				weapon_data = self.game_data_manager.get_weapon(self.weapon)
				if weapon_data:
					weapon_cooldown = weapon_data.cooldown
					
			if current_time - self.attack_time >= self.attack_cooldown + weapon_cooldown:
				self.attacking = False
				self.destroy_attack()

		# Кулдаун переключения оружия
		if not self.can_switch_weapon and self.weapon_switch_time:
			if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
				self.can_switch_weapon = True

		# Кулдаун переключения магии
		if not self.can_switch_magic and self.magic_switch_time:
			if current_time - self.magic_switch_time >= self.switch_duration_cooldown:
				self.can_switch_magic = True

		# Кулдаун неуязвимости
		if not self.vulnerable and self.hurt_time:
			if current_time - self.hurt_time >= self.invincibility_duration:
				self.vulnerable = True

	def animate(self) -> None:
		"""Обновляет анимацию игрока."""
		if self.status not in self.animations:
			self.logger.warning(f"Animation not found for status: {self.status}")
			return
			
		animation = self.animations[self.status]
		self.update_animation(animation)
		
		# Обновляем rect на основе hitbox
		if self.hitbox:
			self.rect = self.image.get_rect(center=self.hitbox.center)

		# Эффект мерцания при неуязвимости
		if not self.vulnerable:
			alpha = self.wave_value()
			self.image.set_alpha(alpha)
		else:
			self.image.set_alpha(255)

	def get_full_weapon_damage(self) -> int:
		"""Возвращает полный урон оружия."""
		base_damage = self.stats['attack']
		weapon_damage = 0
		
		if self.game_data_manager:
			weapon_data = self.game_data_manager.get_weapon(self.weapon)
			if weapon_data:
				weapon_damage = weapon_data.damage
				
		return base_damage + weapon_damage

	def get_full_magic_damage(self) -> int:
		"""Возвращает полный урон магии."""
		base_damage = self.stats['magic']
		spell_damage = 0
		
		if self.game_data_manager:
			magic_data = self.game_data_manager.get_magic(self.magic)
			if magic_data:
				spell_damage = magic_data.strength
				
		return base_damage + spell_damage

	def get_value_by_index(self, index: int) -> int:
		"""Возвращает значение статистики по индексу."""
		values = list(self.stats.values())
		return values[index] if 0 <= index < len(values) else 0

	def get_cost_by_index(self, index: int) -> int:
		"""Возвращает стоимость улучшения по индексу."""
		costs = list(self.upgrade_cost.values())
		return costs[index] if 0 <= index < len(costs) else 0

	def energy_recovery(self) -> None:
		"""Восстанавливает энергию игрока."""
		if self.energy < self.stats['energy']:
			self.energy += 0.01 * self.stats['magic']
		else:
			self.energy = self.stats['energy']

	def take_damage(self, amount: int, attack_type: str) -> None:
		"""
		Принимает урон от врага.
		
		Args:
			amount: Количество урона
			attack_type: Тип атаки
		"""
		if self.vulnerable:
			self.health -= amount
			self.vulnerable = False
			self.hurt_time = pygame.time.get_ticks()
			
			if self.audio_manager:
				self.audio_manager.play_sound('hit')

	def add_experience(self, amount: int) -> None:
		"""
		Добавляет опыт игроку.
		
		Args:
			amount: Количество опыта
		"""
		self.exp += amount

	def upgrade_stat(self, stat_name: str) -> bool:
		"""
		Улучшает статистику игрока.
		
		Args:
			stat_name: Название статистики для улучшения
			
		Returns:
			True, если улучшение успешно
		"""
		if stat_name not in self.stats:
			return False
			
		cost = self.upgrade_cost.get(stat_name, 0)
		if self.exp >= cost and self.stats[stat_name] < self.max_stats[stat_name]:
			self.exp -= cost
			self.stats[stat_name] += 1
			
			# Обновляем текущие значения
			if stat_name == 'health':
				self.health = self.stats['health'] + 20
			elif stat_name == 'energy':
				self.energy = self.stats['energy']
			elif stat_name == 'speed':
				self.speed = self.stats['speed']
				
			return True
		return False

	def update(self) -> None:
		"""Обновляет состояние игрока."""
		self.input()
		self.cooldowns()
		self.get_status()
		self.animate()
		self.move(self.speed)
		self.energy_recovery()