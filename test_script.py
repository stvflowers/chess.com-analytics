#!/usr/bin/env python3
"""
Test script for the updated advanced_game_analysis.py
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, '/workspaces/chess.com-analytics')

try:
    # Test import
    import advanced_game_analysis as aga
    print("✅ Successfully imported advanced_game_analysis")
    
    # Test basic functionality
    print("🔧 Testing configuration function...")
    aga.configure_database("test-server", "test-db", "test-user", "test-pass")
    
    print("✅ All tests passed!")
    
except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()
