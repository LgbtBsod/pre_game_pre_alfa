#!/usr/bin/env python3
"""
Simple test for AI-EVOLVE system
"""

import sys
import os

# Add root directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """Test basic imports"""
    try:
        from src.core.constants import EntityType, DamageType, ItemType
        print("SUCCESS: Basic constants imported")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_entities():
    """Test entity imports"""
    try:
        from src.entities import BaseEntity, Player, NPC, Enemy
        print("SUCCESS: Entities imported")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    print("Testing AI-EVOLVE system...")
    
    test1 = test_basic_imports()
    test2 = test_entities()
    
    if test1 and test2:
        print("ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("SOME TESTS FAILED")
        sys.exit(1)
