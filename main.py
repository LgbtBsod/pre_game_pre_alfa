#!/usr/bin/env python3
"""
Zelda Game - Enhanced Edition
Main entry point with refactored architecture
"""

import sys
import os
from pathlib import Path

# Add the code directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'code'))

def main():
    """Main entry point for the game"""
    try:
        # Import and initialize the game manager
        from core.game_manager import get_game_manager, cleanup_game_manager
        
        # Get the game manager instance
        game_manager = get_game_manager()
        
        # Run the game
        game_manager.run()
        
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Ensure cleanup happens
        try:
            cleanup_game_manager()
        except:
            pass

if __name__ == '__main__':
    main()