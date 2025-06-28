import asyncio

class AIUpdateScheduler:
    def __init__(self):
        self.high_priority = []    # Игрок, боссы, важные NPC
        self.medium_priority = []  # Враги в поле зрения
        self.low_priority = []     # Все остальные
        self.last_update_time = 0
    
    def add_entity(self, entity):
        if entity.is_player or entity.is_boss:
            self.high_priority.append(entity)
        elif entity.distance_to_player < 1000:  # В поле зрения
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
        
        # High priority: полное обновление
        for entity in self.high_priority:
            entity.ai_controller.update(delta_time)
        
        # Medium priority: упрощенное обновление
        for entity in self.medium_priority:
            entity.ai_controller.light_update(delta_time)
        
        # Low priority: обновление раз в 0.5 секунды
        if current_time - self.last_update_time > 0.5:
            for entity in self.low_priority:
                entity.ai_controller.minimal_update(delta_time)
            self.last_update_time = current_time
    
    async def update_async(self, delta_time):
        """Асинхронная версия обновления"""
        tasks = []
        
        # High priority
        for entity in self.high_priority:
            tasks.append(asyncio.create_task(
                self._update_entity(entity, delta_time, "full")
            ))
        
        # Medium priority
        for entity in self.medium_priority:
            tasks.append(asyncio.create_task(
                self._update_entity(entity, delta_time, "light")
            ))
        
        # Low priority (batch update)
        if self.last_update_time + delta_time > 0.5:
            for entity in self.low_priority:
                tasks.append(asyncio.create_task(
                    self._update_entity(entity, delta_time, "minimal")
                ))
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