import random


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
        return damage_report