#!/usr/bin/env python3
"""
Обработчик событий Enhanced Edition для GameInterface.
Выделен в отдельный файл для лучшей организации кода.
"""

import logging

logger = logging.getLogger(__name__)


class EnhancedEventHandler:
    """Обработчик событий Enhanced Edition"""
    
    def __init__(self, game_interface):
        self.game_interface = game_interface
    
    def handle_enhanced_event(self, event: dict):
        """Обработка событий от Enhanced Game Master"""
        event_type = event.get("type")
        
        if event_type == "emotion_trigger":
            self._handle_emotion_trigger(event)
        elif event_type == "risk_factor_added":
            self._handle_risk_factor_added(event)
        elif event_type == "skill_learned":
            self._handle_skill_learned(event)
        elif event_type == "curse_applied":
            self._handle_curse_applied(event)
        elif event_type == "blessing_applied":
            self._handle_blessing_applied(event)
        elif event_type == "evolution_event":
            self._handle_evolution_event(event)
        else:
            logger.debug(f"Неизвестное Enhanced событие: {event_type}")
    
    def _handle_emotion_trigger(self, event: dict):
        """Обработка события активации эмоции"""
        if hasattr(self.game_interface, 'emotion_system') and self.game_interface.emotion_system:
            self.game_interface.emotion_system.trigger_emotion(
                event["emotion_code"],
                event.get("intensity", 1.0),
                event.get("source", "enhanced_system")
            )
            logger.info(f"😊 Эмоция активирована: {event['emotion_code']}")
    
    def _handle_risk_factor_added(self, event: dict):
        """Обработка события добавления фактора риска"""
        logger.info(f"🎯 Фактор риска добавлен: {event['factor_name']}")
        # Здесь можно добавить визуальное уведомление игроку
    
    def _handle_skill_learned(self, event: dict):
        """Обработка события изучения навыка"""
        logger.info(f"📚 Навык изучен: {event['skill_id']}")
        # Здесь можно обновить UI навыков
    
    def _handle_curse_applied(self, event: dict):
        """Обработка события применения проклятия"""
        curse_type = event.get("curse_type", "unknown")
        logger.info(f"🎭 Проклятие применено: {curse_type}")
        # Здесь можно показать уведомление о проклятии
    
    def _handle_blessing_applied(self, event: dict):
        """Обработка события применения благословения"""
        blessing_type = event.get("blessing_type", "unknown")
        logger.info(f"✨ Благословение применено: {blessing_type}")
        # Здесь можно показать уведомление о благословении
    
    def _handle_evolution_event(self, event: dict):
        """Обработка события эволюции"""
        if (hasattr(self.game_interface, 'enhanced_game_master') and 
            self.game_interface.enhanced_game_master and 
            self.game_interface.player):
            
            evolution_result = self.game_interface.enhanced_game_master.trigger_evolution_event(
                "player", 
                {
                    "required_experience": 100,
                    "current_experience": getattr(self.game_interface.player, 'experience', 150),
                    "combat_experience": 50,
                    "learning_points": 30,
                    "survival_time": getattr(self.game_interface, "elapsed_time", 1800)
                }
            )
            
            if evolution_result.get("success"):
                evolution_name = evolution_result.get("evolution_name", "Unknown")
                logger.info(f"🧬 Эволюция успешна: {evolution_name}")
                # Здесь можно показать анимацию эволюции
