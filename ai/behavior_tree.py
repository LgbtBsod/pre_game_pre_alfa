from enum import Enum
import random


class NodeStatus(Enum):
    SUCCESS = 1
    FAILURE = 2
    RUNNING = 3


class Node:
    def __init__(self, name="Node"):
        self.name = name

    def execute(self, entity):
        return NodeStatus.SUCCESS

    def __repr__(self):
        return f"{self.name}"


class CompositeNode(Node):
    def __init__(self, name, children=None):
        super().__init__(name)
        self.children = children or []

    def add_child(self, child):
        self.children.append(child)

    def remove_child(self, child):
        if child in self.children:
            self.children.remove(child)


class Selector(CompositeNode):
    def __init__(self, children=None):
        super().__init__("Selector", children)

    def execute(self, entity):
        for child in self.children:
            status = child.execute(entity)
            if status == NodeStatus.SUCCESS:
                return NodeStatus.SUCCESS
            if status == NodeStatus.RUNNING:
                return NodeStatus.RUNNING
        return NodeStatus.FAILURE


class Sequence(CompositeNode):
    def __init__(self, children=None):
        super().__init__("Sequence", children)

    def execute(self, entity):
        for child in self.children:
            status = child.execute(entity)
            if status == NodeStatus.FAILURE:
                return NodeStatus.FAILURE
            if status == NodeStatus.RUNNING:
                return NodeStatus.RUNNING
        return NodeStatus.SUCCESS


class ConditionNode(Node):
    def __init__(self, condition_func, name="Condition"):
        super().__init__(name)
        self.condition = condition_func

    def execute(self, entity):
        if self.condition(entity):
            return NodeStatus.SUCCESS
        return NodeStatus.FAILURE


class ActionNode(Node):
    def __init__(self, action_func, name="Action"):
        super().__init__(name)
        self.action = action_func

    def execute(self, entity):
        self.action(entity)
        return NodeStatus.SUCCESS


class Parallel(CompositeNode):
    def __init__(self, children=None):
        super().__init__("Parallel", children)

    def execute(self, entity):
        any_running = False
        for child in self.children:
            status = child.execute(entity)
            if status == NodeStatus.FAILURE:
                return NodeStatus.FAILURE
            if status == NodeStatus.RUNNING:
                any_running = True
        return NodeStatus.RUNNING if any_running else NodeStatus.SUCCESS


class Inverter(Node):
    def __init__(self, child):
        super().__init__("Inverter")
        self.child = child

    def execute(self, entity):
        status = self.child.execute(entity)
        if status == NodeStatus.SUCCESS:
            return NodeStatus.FAILURE
        if status == NodeStatus.FAILURE:
            return NodeStatus.SUCCESS
        return status


class BehaviorTree:
    def __init__(self, root=None):
        self.root = root
        self.current_node = None
        self.blackboard = Blackboard()
        self.execution_stack = []

    def execute(self, entity):
        if self.root is None:
            return NodeStatus.FAILURE

        if self.current_node is None:
            self.current_node = self.root
            self.execution_stack = [self.root]

        status = self.current_node.execute(entity)

        if status != NodeStatus.RUNNING:
            self.current_node = None
            self.execution_stack = []

        return status

    def set_root(self, new_root):
        self.root = new_root
        self.current_node = None
        self.execution_stack = []

    def get_active_nodes(self):
        return [node for node in self.execution_stack]


# Concrete nodes
class CheckLowHealth(ConditionNode):
    def __init__(self, threshold=0.3):
        super().__init__(
            lambda e: (e.health / max(1.0, getattr(e, "max_health", 1.0))) < threshold,
            f"CheckLowHealth({threshold})",
        )


class UseHealingItem(ActionNode):
    def __init__(self):
        def heal_action(entity):
            # Safe call: use available entity method
            if hasattr(entity, "use_best_healing_item"):
                entity.use_best_healing_item()

        super().__init__(heal_action, "UseHealingItem")


class MoveToPosition(ActionNode):
    def __init__(self, position_getter):
        super().__init__(lambda e: e.move_to(position_getter(e)), "MoveToPosition")


class AttackNearestEnemy(ActionNode):
    def __init__(self):
        super().__init__(
            lambda e: e.attack(e.find_nearest_enemy()), "AttackNearestEnemy"
        )


class UseSpell(ActionNode):
    def __init__(self, spell_name):
        def cast_spell(entity):
            if entity.mana >= entity.spells[spell_name].cost:
                entity.cast_spell(spell_name)

        super().__init__(cast_spell, f"UseSpell({spell_name})")


class CheckMana(ConditionNode):
    def __init__(self, min_mana):
        super().__init__(lambda e: e.mana >= min_mana, f"CheckMana({min_mana})")


# Generates trees based on personality
def generate_tree_for_personality(personality):
    if personality["aggression"] > 0.7:
        return Selector(
            [Sequence([CheckLowHealth(0.3), UseHealingItem()]), AttackNearestEnemy()]
        )
    else:
        return Selector([CheckLowHealth(0.5), UseHealingItem(), AttackNearestEnemy()])


class Blackboard:
    def __init__(self):
        self._data = {}

    def set(self, key, value):
        self._data[key] = value

    def get(self, key, default=None):
        return self._data.get(key, default)


class Repeater(Node):
    def __init__(self, child, count=0):
        super().__init__("Repeater")
        self.child = child
        self.max_count = count
        self.current_count = 0

    def execute(self, entity):
        if self.max_count > 0 and self.current_count >= self.max_count:
            return NodeStatus.SUCCESS

        status = self.child.execute(entity)
        if status == NodeStatus.RUNNING:
            return NodeStatus.RUNNING

        self.current_count += 1
        return NodeStatus.RUNNING
