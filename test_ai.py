#!/usr/bin/env python3
"""Test AI features"""

import sys
sys.path.insert(0, '/home/mobotronst/Codes/Goalin/src')

from goalin.ai_assistant import AIAssistant
from goalin.config import get_category

print("="*60)
print("Testing AI Assistant")
print("="*60)

# Test 1: Initialize AI
print("\n1. Initializing AI Assistant...")
ai = AIAssistant()
print(f"   API Key loaded: {'Yes' if ai.api_key else 'No'}")
print(f"   Model initialized: {'Yes' if ai.model else 'No'}")
print(f"   Is configured: {ai.is_configured()}")

# Test 2: Test categorization
if ai.is_configured():
    print("\n2. Testing app categorization...")
    test_apps = ["Firefox", "VSCode", "Spotify", "Discord", "LibreOffice"]
    
    print(f"   Testing with apps: {test_apps}")
    
    for app in test_apps:
        category = ai.get_app_category(app)
        print(f"   {app:20} -> {category}")
    
    # Test 3: Check cached categories
    print(f"\n3. Total cached categories: {len(ai.app_categories)}")
    
    # Show sample of categories
    print("\n4. Sample of 10 categorizations:")
    for app, cat in list(ai.app_categories.items())[:10]:
        print(f"   {app:30} -> {cat}")
else:
    print("\n❌ AI is not configured!")
    print("   Reason: API key or model not initialized")

# Test 4: Test get_category from config
print("\n5. Testing config.get_category()...")
test_apps2 = ["firefox", "code", "spotify"]
for app in test_apps2:
    cat = get_category(app)
    print(f"   {app:20} -> {cat}")

print("\n" + "="*60)
