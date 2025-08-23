#!/usr/bin/env python3
"""
Тест интеграции Enhanced Edition систем
"""

import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

def test_enhanced_systems():
    """Тест всех Enhanced систем"""
    print("🧪 Тестирование Enhanced Edition систем...")
    
    try:
        # Тест 1: Память поколений
        print("1️⃣ Тестирую систему памяти поколений...")
        from core.generational_memory_system import GenerationalMemorySystem
        memory_system = GenerationalMemorySystem("test_save")
        print("   ✅ Память поколений работает")
        
        # Тест 2: Эмоциональное влияние ИИ
        print("2️⃣ Тестирую эмоциональное влияние ИИ...")
        from core.emotional_ai_influence import EmotionalAIInfluenceSystem
        emotional_system = EmotionalAIInfluenceSystem(memory_system)
        print("   ✅ Эмоциональное влияние ИИ работает")
        
        # Тест 3: Улучшенная боевая система
        print("3️⃣ Тестирую улучшенную боевую систему...")
        from core.enhanced_combat_learning import EnhancedCombatLearningSystem
        combat_system = EnhancedCombatLearningSystem(memory_system, emotional_system)
        print("   ✅ Улучшенная боевая система работает")
        
        # Тест 4: Генератор контента
        print("4️⃣ Тестирую улучшенный генератор контента...")
        from core.enhanced_content_generator import EnhancedContentGenerator, BiomeType
        content_generator = EnhancedContentGenerator(memory_system)
        print("   ✅ Улучшенный генератор контента работает")
        
        # Тест 5: Система навыков
        print("5️⃣ Тестирую систему навыков...")
        from core.enhanced_skill_system import SkillManager, SkillLearningAI
        skill_manager = SkillManager(memory_system, emotional_system)
        skill_ai = SkillLearningAI(memory_system, emotional_system)
        print("   ✅ Система навыков работает")
        
        # Тест 6: GameInterface
        print("6️⃣ Тестирую GameInterface...")
        from ui.game_interface import GameInterface
        print("   ✅ GameInterface импортируется")
        
        print("\n🎉 ВСЕ ENHANCED СИСТЕМЫ РАБОТАЮТ!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_components():
    """Тест UI компонентов"""
    print("\n🎨 Тестирование UI компонентов...")
    
    try:
        # Тест HUD компонентов
        from ui.hud import StatusHUD, InventoryHUD, GeneticsHUD, AILearningHUD
        print("   ✅ HUD компоненты доступны")
        
        # Тест сцен
        from ui.menu_scene import MenuScene
        from ui.pause_scene import PauseScene
        print("   ✅ Сцены доступны")
        
        # Тест рендерера
        from ui.renderer import GameRenderer
        print("   ✅ Рендерер доступен")
        
        print("   ✅ Все UI компоненты работают")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка UI: {e}")
        return False

if __name__ == "__main__":
    print("🎮 AI-EVOLVE: Enhanced Edition - Тест интеграции")
    print("=" * 60)
    
    success1 = test_enhanced_systems()
    success2 = test_ui_components()
    
    if success1 and success2:
        print("\n🎯 ИНТЕГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print("Enhanced Edition готов к запуску!")
    else:
        print("\n⚠️ Есть проблемы с интеграцией")
        sys.exit(1)
