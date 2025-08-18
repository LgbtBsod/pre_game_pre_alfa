#!/usr/bin/env python3
"""
Simple test script to check if the game can start
"""

import sys
import os
from pathlib import Path

# Add the code directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'code'))

def test_game_startup():
    """Test if the game can start without crashing"""
    try:
        print("Testing game startup...")
        
        # Import and initialize the game manager
        from core.game_manager import get_game_manager, cleanup_game_manager
        
        print("✓ Game manager imported successfully")
        
        # Get the game manager instance
        game_manager = get_game_manager()
        print("✓ Game manager instance created successfully")
        
        # Check if display is initialized
        if hasattr(game_manager, 'screen') and game_manager.screen:
            print("✓ Display initialized successfully")
        else:
            print("✗ Display not initialized")
            return False
        
        # Check if scenes are initialized
        if hasattr(game_manager, 'scene_manager') and game_manager.scene_manager:
            current_scene = game_manager.scene_manager.get_current_scene()
            if current_scene:
                print("✓ Scene manager initialized successfully")
                print(f"  Current scene: {current_scene.__class__.__name__}")
            else:
                print("✗ No current scene")
                return False
        else:
            print("✗ Scene manager not initialized")
            return False
        
        print("✓ Game startup test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Game startup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Ensure cleanup happens
        try:
            cleanup_game_manager()
            print("✓ Game manager cleaned up successfully")
        except Exception as e:
            print(f"✗ Error during cleanup: {e}")

if __name__ == '__main__':
    success = test_game_startup()
    if success:
        print("\n🎮 Game startup test PASSED! The game should work.")
    else:
        print("\n❌ Game startup test FAILED! There are issues to fix.")
    
    input("\nPress Enter to exit...")
