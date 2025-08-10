import random
from entities.effect import Effect
import json
import os
import time


class DamageSystem:
    @staticmethod
    def calculate_damage(attacker, target, weapon, skill=None):
        total_damage = 0.0
        damage_report = {"total": 0.0}

        # Базовый урон от характеристик (атрибуты представлены числами)
        base_damage = 0.0
        weapon_type_value = getattr(weapon.weapon_type, "value", weapon.weapon_type)
        if isinstance(weapon_type_value, str):
            wtype = weapon_type_value.lower()
        else:
            wtype = str(weapon_type_value).lower()

        if any(k in wtype for k in ["sword", "axe", "hammer"]):
            base_damage = float(attacker.attributes.get("strength", 10)) * 0.7
        elif any(k in wtype for k in ["bow", "crossbow", "musket"]):
            base_damage = float(attacker.attributes.get("dexterity", 10)) * 0.8
        elif "staff" in wtype:
            base_damage = float(attacker.attributes.get("intelligence", 10)) * 0.9

        # Учет урона от оружия
        for dmg_type in weapon.damage_types:
            dmg_value = float(dmg_type.get("value", 0))

            # Имя типа урона может быть Enum или строкой
            dtype = dmg_type.get("type")
            if hasattr(dtype, "value"):
                dtype_key = str(dtype.value)
            else:
                dtype_key = str(dtype)
            dtype_key = dtype_key.lower()

            resist_stat = f"{dtype_key}_resist"
            resistance = float(target.combat_stats.get(resist_stat, 0.0))

            # Пробивание сопротивлений (универсальная/элементная)
            penetration = float(attacker.combat_stats.get("elemental_penetration", 0.0))
            effective_resistance = max(0.0, resistance - penetration)

            # Финальный урон по типу
            final_damage = max(0.0, (base_damage + dmg_value) * (1 - effective_resistance))
            total_damage += final_damage
            damage_report[dtype_key] = final_damage

        # Учет критического удара
        critical_chance = float(attacker.combat_stats.get("critical_chance", 0.05)) + float(
            getattr(weapon, "critical_chance", 0.0)
        )
        if random.random() < critical_chance:
            total_damage *= 2.0
            damage_report["critical"] = True

        # Учет навыков (если есть)
        if skill:
            dmg_mult = float(getattr(skill, "damage_multiplier", 1.0))
            total_damage *= dmg_mult

        damage_report["total"] = total_damage
        
        # Применение эффектов от оружия и навыков
        DamageSystem._apply_weapon_effects(attacker, target, weapon, skill)
        
        return damage_report
    
    @staticmethod
    def _apply_weapon_effects(attacker, target, weapon, skill):
        """Применить эффекты от оружия и навыков"""
        effects_to_apply = []
        
        # Эффекты от оружия
        if hasattr(weapon, 'effects') and weapon.effects:
            effects_to_apply.extend(weapon.effects)
        
        # Эффекты от навыка
        if skill and hasattr(skill, 'effects') and skill.effects:
            effects_to_apply.extend(skill.effects)
        
        # Применение эффектов
        for effect_id in effects_to_apply:
            DamageSystem._apply_effect_to_target(target, effect_id)
    
    @staticmethod
    def _apply_effect_to_target(target, effect_id):
        """Применить эффект к цели"""
        try:
            # Загрузка данных эффектов
            effects_file = "data/effects.json"
            if os.path.exists(effects_file):
                with open(effects_file, 'r', encoding='utf-8') as f:
                    effects_data = json.load(f)
                
                if effect_id in effects_data:
                    effect_data = effects_data[effect_id]
                    
                    # Создание и применение эффекта
                    effect = Effect(
                        effect_id=effect_id,
                        tags=effect_data.get("tags", []),
                        modifiers=effect_data.get("modifiers", [])
                    )
                    
                    # Применение эффекта к цели
                    effect.apply(target, True)
                    
                    # Добавление эффекта в список активных эффектов цели
                    if not hasattr(target, 'active_effects'):
                        target.active_effects = []
                    target.active_effects.append(effect)
                    
        except Exception as e:
            print(f"Ошибка применения эффекта {effect_id}: {e}")
    
    @staticmethod
    def process_entity_effects(entity, delta_time):
        """Обработать все активные эффекты сущности"""
        if not hasattr(entity, 'active_effects'):
            return
        
        # Обработка эффектов
        for effect in entity.active_effects[:]:  # Копия списка для безопасного удаления
            if effect.active:
                effect.process_tick(entity, delta_time)
                
                # Проверка истечения эффекта
                if hasattr(effect, 'duration') and effect.duration:
                    if time.time() - effect.start_time >= effect.duration:
                        effect.active = False
                        effect.apply(entity, False)  # Отмена эффекта
                        entity.active_effects.remove(effect)
            else:
                entity.active_effects.remove(effect)