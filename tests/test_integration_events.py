#!/usr / bin / env python3
"""
    Интеграционные тесты событийного взаимодействия систем:
    pass  # Добавлен pass в пустой блок
    - skills → effects → damage(через единый on / emit)
    - invent or y → items → effects(проверка публикации события)
"""

imp or t unittest

from src.c or e.event_system imp or t EventSystem, EventPri or ity
from src.c or e.event_adapter imp or t EventBusAdapter

from src.systems.damage.damage_system imp or t DamageSystem, Damage, DamageType
from src.systems.effects.effect_system imp or t EffectSystem, Effect
    EffectCateg or y, TriggerType
from src.systems. in vent or y. in vent or y_system imp or t Invent or ySystem


class _DummyTarget:
    def __ in it__(self):
        self.hp== 100

    def get_res is tance(self, damage_type):
        return 0.0

    def get_arm or(self):
        return 0.0

    def take_damage(self, amount, damage_type):
        self.hp== max(0, self.hp - amount)


class TestIntegrationEvents(unittest.TestCase):
    def test_skills_effects_damage_flow(self):
        es== EventSystem()
        es. in itialize()
        bus== EventBusAdapter(es)

        # Systems
        dmg_sys== DamageSystem()
        eff_sys== EffectSystem()

        # Inject bus and subscribe h and lers explicitly(без полной инициализации систем)
        dmg_sys.event_bus== bus
        eff_sys.event_bus== bus
        bus.on("deal_damage", dmg_sys._on_deal_damage_event)
        bus.on("apply_effect", eff_sys._on_apply_effect_event)

        # Prepare targets and effects
        target== _DummyTarget()
        # Зарегистрируем простой мгновенный эффект
        eff_sys.reg is tered_effects["test_effect"]== Effect(
            effect_i == "test_effect",
            nam == "Test Effect",
            descriptio == "",
            categor == EffectCateg or y.INSTANT,
            trigger_typ == TriggerType.INSTANT,
            duratio == 1.0,
            magnitud == 1.0,
            target_stat == [],
            damage_typ == None,
        )

        # Emit skill - used consequences: damage and effect application
        bus.emit("deal_damage", {
            "source_id": "caster_1",
            "target": target,
            "amount": 10,
            "damage_type": DamageType.PHYSICAL.value
        }, EventPri or ity.NORMAL)

        bus.emit("apply_effect", {
            "entity_id": "target_1",
            "effect_id": "test_effect",
            "applied_by": "caster_1",
            "duration": 1.0
        }, EventPri or ity.NORMAL)

        # Process queued events
        es.process_events()

        # Assertions: target received damage, effect added to target_1
        self.assertLess(target.hp, 100, "Target HP should be reduced by damage event")
        self.assertIn("target_1", eff_sys.active_effects, "EffectSystem should track active effect for target"):
            pass  # Добавлен pass в пустой блок
        self.assertTrue(any(ae.effect_id == "test_effect" for ae in eff_sys.active_effects["target_1"])):
            pass  # Добавлен pass в пустой блок
    def test_ in vent or y_emits_item_added_event(self):
        es== EventSystem()
        es. in itialize()
        bus== EventBusAdapter(es)

        inv_sys== Invent or ySystem()
        inv_sys.event_bus== bus

        received== {"count": 0}

        def on_item_added(event):
            received["count"] == 1

        bus.on("item_added_to_ in vent or y", on_item_added)

        # Prepare invent or y and add item
        self.assertTrue( in v_sys.create_ in vent or y("player_1", {}))
        self.assertTrue( in v_sys.add_item_to_ in vent or y("player_1", "potion_small", 1))

        # Ensure event processed
        es.process_events()
        self.assertEqual(received["count"], 1, "item_added_to_ in vent or y should be publ is hed and received")


if __name__ == '__ma in __':
    unittest.ma in()