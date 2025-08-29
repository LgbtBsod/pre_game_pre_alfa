#!/usr/bin/env python3
"""
Интеграционные тесты событийного взаимодействия систем:
- skills → effects → damage (через единый on/emit)
- inventory → items → effects (проверка публикации события)
"""

import unittest

from src.core.event_system import EventSystem, EventPriority
from src.core.event_adapter import EventBusAdapter

from src.systems.damage.damage_system import DamageSystem, Damage, DamageType
from src.systems.effects.effect_system import EffectSystem, Effect, EffectCategory, TriggerType
from src.systems.inventory.inventory_system import InventorySystem


class _DummyTarget:
    def __init__(self):
        self.hp = 100

    def get_resistance(self, damage_type):
        return 0.0

    def get_armor(self):
        return 0.0

    def take_damage(self, amount, damage_type):
        self.hp = max(0, self.hp - amount)


class TestIntegrationEvents(unittest.TestCase):
    def test_skills_effects_damage_flow(self):
        es = EventSystem()
        es.initialize()
        bus = EventBusAdapter(es)

        # Systems
        dmg_sys = DamageSystem()
        eff_sys = EffectSystem()

        # Inject bus and subscribe handlers explicitly (без полной инициализации систем)
        dmg_sys.event_bus = bus
        eff_sys.event_bus = bus
        bus.on("deal_damage", dmg_sys._on_deal_damage_event)
        bus.on("apply_effect", eff_sys._on_apply_effect_event)

        # Prepare targets and effects
        target = _DummyTarget()
        # Зарегистрируем простой мгновенный эффект
        eff_sys.registered_effects["test_effect"] = Effect(
            effect_id="test_effect",
            name="Test Effect",
            description="",
            category=EffectCategory.INSTANT,
            trigger_type=TriggerType.INSTANT,
            duration=1.0,
            magnitude=1.0,
            target_stats=[],
            damage_type=None,
        )

        # Emit skill-used consequences: damage and effect application
        bus.emit("deal_damage", {
            "source_id": "caster_1",
            "target": target,
            "amount": 10,
            "damage_type": DamageType.PHYSICAL.value,
        }, EventPriority.NORMAL)

        bus.emit("apply_effect", {
            "entity_id": "target_1",
            "effect_id": "test_effect",
            "applied_by": "caster_1",
            "duration": 1.0,
        }, EventPriority.NORMAL)

        # Process queued events
        es.process_events()

        # Assertions: target received damage, effect added to target_1
        self.assertLess(target.hp, 100, "Target HP should be reduced by damage event")
        self.assertIn("target_1", eff_sys.active_effects, "EffectSystem should track active effect for target")
        self.assertTrue(any(ae.effect_id == "test_effect" for ae in eff_sys.active_effects["target_1"]))

    def test_inventory_emits_item_added_event(self):
        es = EventSystem()
        es.initialize()
        bus = EventBusAdapter(es)

        inv_sys = InventorySystem()
        inv_sys.event_bus = bus

        received = {"count": 0}

        def on_item_added(event):
            received["count"] += 1

        bus.on("item_added_to_inventory", on_item_added)

        # Prepare inventory and add item
        self.assertTrue(inv_sys.create_inventory("player_1", {}))
        self.assertTrue(inv_sys.add_item_to_inventory("player_1", "potion_small", 1))

        # Ensure event processed
        es.process_events()
        self.assertEqual(received["count"], 1, "item_added_to_inventory should be published and received")


if __name__ == '__main__':
    unittest.main()


