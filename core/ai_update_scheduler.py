import asyncio


class AIUpdateScheduler:
    def __init__(self):
        self.high_priority = []  # Player, bosses, important NPCs
        self.medium_priority = []  # Enemies in view
        self.low_priority = []  # All others
        self.last_update_time = 0

    def add_entity(self, entity):
        if entity.is_player or entity.is_boss:
            self.high_priority.append(entity)
        elif (
            hasattr(entity, "distance_to_player") and entity.distance_to_player < 1000
        ):  # In view
            self.medium_priority.append(entity)
        else:
            self.low_priority.append(entity)

    def remove_entity(self, entity):
        if entity in self.high_priority:
            self.high_priority.remove(entity)
        elif entity in self.medium_priority:
            self.medium_priority.remove(entity)
        elif entity in self.low_priority:
            self.low_priority.remove(entity)

    def update(self, delta_time):
        current_time = self.last_update_time + delta_time

        # High priority: full update
        for entity in self.high_priority:
            if hasattr(entity, "ai_controller"):
                entity.ai_controller.update(delta_time)

        # Medium priority: simplified update
        for entity in self.medium_priority:
            if hasattr(entity, "ai_controller"):
                entity.ai_controller.light_update(delta_time)

        # Low priority: update every 0.5 seconds
        if current_time - self.last_update_time > 0.5:
            for entity in self.low_priority:
                if hasattr(entity, "ai_controller"):
                    entity.ai_controller.minimal_update(delta_time)
            self.last_update_time = current_time

    async def update_async(self, delta_time):
        """Asynchronous update version"""
        tasks = []

        # High priority
        for entity in self.high_priority:
            if hasattr(entity, "ai_controller"):
                tasks.append(
                    asyncio.create_task(self._update_entity(entity, delta_time, "full"))
                )

        # Medium priority
        for entity in self.medium_priority:
            if hasattr(entity, "ai_controller"):
                tasks.append(
                    asyncio.create_task(
                        self._update_entity(entity, delta_time, "light")
                    )
                )

        # Low priority (batch update)
        if self.last_update_time + delta_time > 0.5:
            for entity in self.low_priority:
                if hasattr(entity, "ai_controller"):
                    tasks.append(
                        asyncio.create_task(
                            self._update_entity(entity, delta_time, "minimal")
                        )
                    )
            self.last_update_time = 0
        else:
            self.last_update_time += delta_time

        await asyncio.gather(*tasks)

    async def _update_entity(self, entity, delta_time, mode):
        if mode == "full":
            entity.ai_controller.update(delta_time)
        elif mode == "light":
            entity.ai_controller.light_update(delta_time)
        elif mode == "minimal":
            entity.ai_controller.minimal_update(delta_time)

    def register_system(self, name, update_func, interval):
        """Register an AI system with update function and interval"""
        if not hasattr(self, "systems"):
            self.systems = {}
        self.systems[name] = {
            "func": update_func,
            "interval": interval,
            "last_update": 0,
        }

    def register_entity(self, entity, update_func):
        """Register an entity with its update function"""
        if not hasattr(self, "entities"):
            self.entities = []
        self.entities.append({"entity": entity, "update_func": update_func})

    def update_all(self, delta_time):
        """Update all registered systems and entities"""
        current_time = self.last_update_time + delta_time

        # Update systems
        if hasattr(self, "systems"):
            for name, system in self.systems.items():
                if current_time - system["last_update"] >= system["interval"]:
                    system["func"](delta_time)
                    system["last_update"] = current_time

        # Update entities
        if hasattr(self, "entities"):
            for entity_data in self.entities:
                entity_data["update_func"](delta_time)

        self.last_update_time = current_time
