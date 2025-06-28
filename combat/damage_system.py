class DamageSystem:
    @staticmethod
    def calculate_damage(attacker, target, weapon, skill=None):
        total_damage = 0
        damage_report = {"total": 0}
        
        # Базовый урон от характеристик
        base_damage = 0
        if weapon.weapon_type in ["sword", "axe", "hammer"]:
            base_damage = attacker.attributes["strength"].value * 0.7
        elif weapon.weapon_type in ["bow", "crossbow"]:
            base_damage = attacker.attributes["dexterity"].value * 0.8
        elif weapon.weapon_type == "staff":
            base_damage = attacker.attributes["intelligence"].value * 0.9
        
        # Учет урона от оружия
        for dmg_type in weapon.damage_types:
            dmg_value = dmg_type["value"]
            resist_stat = f"{dmg_type['type']}_resist"
            resistance = target.combat_stats.get(resist_stat, 0.0)
            
            # Пробивание сопротивлений
            penetration = attacker.combat_stats.get("elemental_penetration", 0.0)
            effective_resistance = max(0, resistance - penetration)
            
            # Финальный урон по типу
            final_damage = (base_damage + dmg_value) * (1 - effective_resistance)
            total_damage += final_damage
            damage_report[dmg_type['type']] = final_damage
        
        # Учет критического удара
        critical_chance = attacker.combat_stats["critical_chance"] + weapon.critical_chance
        if random.random() < critical_chance:
            total_damage *= 2.0
            damage_report["critical"] = True
        
        # Учет навыков
        if skill:
            total_damage *= skill.damage_multiplier
            if skill.elemental_effect:
                # Применение стихийного эффекта
                pass
        
        damage_report["total"] = total_damage
        return damage_report