#!/usr/bin/env python3
"""Test AI categorization with a small set of apps"""

import sys
sys.path.insert(0, '/home/mobotronst/Codes/Goalin/src')

from goalin.ai_assistant import AIAssistant

print("Testing AI Categorization with Real API Calls")
print("="*60)

ai = AIAssistant()

if not ai.is_configured():
    print("❌ AI not configured!")
    sys.exit(1)

print(f"✅ AI configured with API key: {ai.api_key[:20]}...")

# Test with a small set of common apps
test_apps = [
    "firefox",
    "code",
    "spotify", 
    "discord",
    "libreoffice",
    "gimp",
    "vlc",
    "thunderbird",
    "steam",
    "kitty"
]

print(f"\n📦 Categorizing {len(test_apps)} apps...")
print("This will make actual API calls to Gemini\n")

def progress(current, total, app):
    print(f"   [{current}/{total}] {app}")

result = ai.categorize_apps(test_apps, progress_callback=progress)

print("\n✅ Categorization complete!")
print("\nResults:")
print("-"*60)
for app in test_apps:
    category = result.get(app, "Unknown")
    print(f"   {app:20} -> {category}")

print("\n" + "="*60)
print("Check your Gemini API usage at:")
print("https://aistudio.google.com/app/apikey")
