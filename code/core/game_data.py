from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
import json
from .constants import WEAPON_DATA, MAGIC_DATA, ENEMY_DATA

class WeaponType(Enum):
    """Weapon type enumeration"""
    SWORD = "sword"
    LANCE = "lance"
    AXE = "axe"
    RAPIER = "rapier"
    SAI = "sai"

class MagicType(Enum):
    """Magic type enumeration"""
    FLAME = "flame"
    HEAL = "heal"

class EnemyType(Enum):
    """Enemy type enumeration"""
    SQUID = "squid"
    RACCOON = "raccoon"
    SPIRIT = "spirit"
    BAMBOO = "bamboo"

@dataclass
class WeaponData:
    """Weapon data structure"""
    name: str
    cooldown: int
    damage: int
    graphic: str
    weapon_type: WeaponType
    description: str = ""
    special_effects: List[str] = field(default_factory=list)

@dataclass
class MagicData:
    """Magic data structure"""
    name: str
    strength: int
    cost: int
    graphic: str
    magic_type: MagicType
    description: str = ""
    special_effects: List[str] = field(default_factory=list)

@dataclass
class EnemyData:
    """Enemy data structure"""
    name: str
    health: int
    exp: int
    damage: int
    attack_type: str
    attack_sound: str
    speed: int
    resistance: int
    attack_radius: int
    notice_radius: int
    description: str = ""
    weaknesses: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)

class GameDataManager:
    """Centralized game data management system"""
    
    def __init__(self):
        self._weapons: Dict[str, WeaponData] = {}
        self._magic: Dict[str, MagicData] = {}
        self._enemies: Dict[str, EnemyData] = {}
        self._load_default_data()
    
    def _load_default_data(self) -> None:
        """Load default game data"""
        # Weapon data
        weapon_data = {
            'sword': WeaponData(
                name="Sword",
                cooldown=100,
                damage=15,
                graphic='graphics/weapons/sword/full.png',
                weapon_type=WeaponType.SWORD,
                description="A reliable steel sword",
                special_effects=["balanced", "versatile"]
            ),
            'lance': WeaponData(
                name="Lance",
                cooldown=400,
                damage=30,
                graphic='graphics/weapons/lance/full.png',
                weapon_type=WeaponType.LANCE,
                description="A powerful piercing weapon",
                special_effects=["piercing", "high_damage"]
            ),
            'axe': WeaponData(
                name="Axe",
                cooldown=300,
                damage=20,
                graphic='graphics/weapons/axe/full.png',
                weapon_type=WeaponType.AXE,
                description="A heavy crushing weapon",
                special_effects=["crushing", "armor_penetration"]
            ),
            'rapier': WeaponData(
                name="Rapier",
                cooldown=50,
                damage=8,
                graphic='graphics/weapons/rapier/full.png',
                weapon_type=WeaponType.RAPIER,
                description="A fast fencing weapon",
                special_effects=["fast", "critical_hit"]
            ),
            'sai': WeaponData(
                name="Sai",
                cooldown=80,
                damage=10,
                graphic='graphics/weapons/sai/full.png',
                weapon_type=WeaponType.SAI,
                description="A defensive weapon",
                special_effects=["defensive", "disarm"]
            )
        }
        
        # Magic data
        magic_data = {
            'flame': MagicData(
                name="Flame",
                strength=5,
                cost=20,
                graphic='graphics/particles/flame/fire.png',
                magic_type=MagicType.FLAME,
                description="Burns enemies with fire",
                special_effects=["burning", "area_damage"]
            ),
            'heal': MagicData(
                name="Heal",
                strength=20,
                cost=10,
                graphic='graphics/particles/heal/heal.png',
                magic_type=MagicType.HEAL,
                description="Restores health",
                special_effects=["healing", "overheal"]
            )
        }
        
        # Enemy data
        enemy_data = {
            'squid': EnemyData(
                name="Squid",
                health=100,
                exp=100,
                damage=20,
                attack_type='slash',
                attack_sound='audio/attack/slash.wav',
                speed=3,
                resistance=3,
                attack_radius=80,
                notice_radius=360,
                description="A tentacled sea creature",
                weaknesses=["fire", "lightning"],
                strengths=["water", "ice"]
            ),
            'raccoon': EnemyData(
                name="Raccoon",
                health=300,
                exp=250,
                damage=40,
                attack_type='claw',
                attack_sound='audio/attack/claw.wav',
                speed=2,
                resistance=3,
                attack_radius=120,
                notice_radius=400,
                description="A cunning forest dweller",
                weaknesses=["fire"],
                strengths=["stealth", "night_vision"]
            ),
            'spirit': EnemyData(
                name="Spirit",
                health=100,
                exp=110,
                damage=8,
                attack_type='thunder',
                attack_sound='audio/attack/fireball.wav',
                speed=4,
                resistance=3,
                attack_radius=60,
                notice_radius=350,
                description="An ethereal being",
                weaknesses=["holy", "light"],
                strengths=["magic", "invisibility"]
            ),
            'bamboo': EnemyData(
                name="Bamboo",
                health=70,
                exp=120,
                damage=6,
                attack_type='leaf_attack',
                attack_sound='audio/attack/slash.wav',
                speed=3,
                resistance=3,
                attack_radius=50,
                notice_radius=300,
                description="A living bamboo plant",
                weaknesses=["fire", "cutting"],
                strengths=["nature", "regeneration"]
            )
        }
        
        self._weapons.update(weapon_data)
        self._magic.update(magic_data)
        self._enemies.update(enemy_data)
    
    def get_weapon(self, name: str) -> Optional[WeaponData]:
        """Get weapon data by name"""
        return self._weapons.get(name)
    
    def get_magic(self, name: str) -> Optional[MagicData]:
        """Get magic data by name"""
        return self._magic.get(name)
    
    def get_enemy(self, name: str) -> Optional[EnemyData]:
        """Get enemy data by name"""
        return self._enemies.get(name)
    
    def get_all_weapons(self) -> List[WeaponData]:
        """Get all weapon data"""
        return list(self._weapons.values())
    
    def get_all_magic(self) -> List[MagicData]:
        """Get all magic data"""
        return list(self._magic.values())
    
    def get_all_enemies(self) -> List[EnemyData]:
        """Get all enemy data"""
        return list(self._enemies.values())
    
    def get_weapon_by_type(self, weapon_type: WeaponType) -> List[WeaponData]:
        """Get weapons by type"""
        return [weapon for weapon in self._weapons.values() if weapon.weapon_type == weapon_type]
    
    def get_magic_by_type(self, magic_type: MagicType) -> List[MagicData]:
        """Get magic by type"""
        return [magic for magic in self._magic.values() if magic.magic_type == magic_type]
    
    def get_enemy_by_attack_type(self, attack_type: str) -> List[EnemyData]:
        """Get enemies by attack type"""
        return [enemy for enemy in self._enemies.values() if enemy.attack_type == attack_type]
    
    def add_weapon(self, weapon: WeaponData) -> None:
        """Add a new weapon"""
        self._weapons[weapon.name.lower()] = weapon
    
    def add_magic(self, magic: MagicData) -> None:
        """Add new magic"""
        self._magic[magic.name.lower()] = magic
    
    def add_enemy(self, enemy: EnemyData) -> None:
        """Add a new enemy"""
        self._enemies[enemy.name.lower()] = enemy
    
    def remove_weapon(self, name: str) -> bool:
        """Remove a weapon"""
        if name in self._weapons:
            del self._weapons[name]
            return True
        return False
    
    def remove_magic(self, name: str) -> bool:
        """Remove magic"""
        if name in self._magic:
            del self._magic[name]
            return True
        return False
    
    def remove_enemy(self, name: str) -> bool:
        """Remove an enemy"""
        if name in self._enemies:
            del self._enemies[name]
            return True
        return False
    
    def get_weapon_stats(self, name: str) -> Dict[str, Any]:
        """Get weapon statistics"""
        weapon = self.get_weapon(name)
        if weapon:
            return {
                'name': weapon.name,
                'cooldown': weapon.cooldown,
                'damage': weapon.damage,
                'type': weapon.weapon_type.value,
                'description': weapon.description,
                'special_effects': weapon.special_effects
            }
        return {}
    
    def get_magic_stats(self, name: str) -> Dict[str, Any]:
        """Get magic statistics"""
        magic = self.get_magic(name)
        if magic:
            return {
                'name': magic.name,
                'strength': magic.strength,
                'cost': magic.cost,
                'type': magic.magic_type.value,
                'description': magic.description,
                'special_effects': magic.special_effects
            }
        return {}
    
    def get_enemy_stats(self, name: str) -> Dict[str, Any]:
        """Get enemy statistics"""
        enemy = self.get_enemy(name)
        if enemy:
            return {
                'name': enemy.name,
                'health': enemy.health,
                'exp': enemy.exp,
                'damage': enemy.damage,
                'attack_type': enemy.attack_type,
                'speed': enemy.speed,
                'resistance': enemy.resistance,
                'description': enemy.description,
                'weaknesses': enemy.weaknesses,
                'strengths': enemy.strengths
            }
        return {}
    
    def export_data(self, filename: str) -> bool:
        """Export game data to JSON file"""
        try:
            data = {
                'weapons': {name: weapon.__dict__ for name, weapon in self._weapons.items()},
                'magic': {name: magic.__dict__ for name, magic in self._magic.items()},
                'enemies': {name: enemy.__dict__ for name, enemy in self._enemies.items()}
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error exporting game data: {e}")
            return False
    
    def import_data(self, filename: str) -> bool:
        """Import game data from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Clear existing data
            self._weapons.clear()
            self._magic.clear()
            self._enemies.clear()
            
            # Import weapons
            for name, weapon_data in data.get('weapons', {}).items():
                weapon = WeaponData(**weapon_data)
                self._weapons[name] = weapon
            
            # Import magic
            for name, magic_data in data.get('magic', {}).items():
                magic = MagicData(**magic_data)
                self._magic[name] = magic
            
            # Import enemies
            for name, enemy_data in data.get('enemies', {}).items():
                enemy = EnemyData(**enemy_data)
                self._enemies[name] = enemy
            
            return True
        except Exception as e:
            print(f"Error importing game data: {e}")
            return False
    
    def reset_to_defaults(self) -> None:
        """Reset to default game data"""
        self._load_default_data()

# Global game data manager instance
_game_data_manager: Optional[GameDataManager] = None

def get_game_data_manager() -> GameDataManager:
    """Get the global game data manager instance"""
    global _game_data_manager
    if _game_data_manager is None:
        _game_data_manager = GameDataManager()
    return _game_data_manager
