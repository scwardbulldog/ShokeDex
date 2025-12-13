"""
Demo script to capture screenshots of Story 3.5: Pokédex Description Text Display

Shows description panel with text wrapping, truncation, and holographic styling.
"""

import pygame
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ui.detail_screen import DetailScreen
from src.ui.screen_manager import ScreenManager
from src.data.database import Database
from src.state_manager import StateManager

# Initialize pygame
pygame.init()

# Create display
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 360
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("ShokeDex - Story 3.5: Description Display Demo")

# Initialize components
database = Database()
state_manager = StateManager()

# Create a mock screen manager (simplified for demo)
class MockScreenManager:
    def __init__(self, database, state_manager):
        self.database = database
        self.state_manager = state_manager
        self.sprite_loader = None

screen_manager = MockScreenManager(database, state_manager)

# Create screenshots directory
screenshots_dir = Path(__file__).parent / "screenshots"
screenshots_dir.mkdir(exist_ok=True)

# Test Pokemon with different description lengths
test_pokemon = [
    (25, "pikachu", "Medium-length description (2-3 lines)"),
    (1, "bulbasaur", "Short description (1-2 lines)"),
    (150, "mewtwo", "Long description (truncates at 4 lines with ellipsis)")
]

print("🎬 Generating Story 3.5 Description Display Screenshots...")
print("=" * 60)

for pokemon_id, name, description_type in test_pokemon:
    print(f"\n📸 Capturing #{pokemon_id:03d} - {name.upper()}")
    print(f"   Description type: {description_type}")
    
    # Create DetailScreen for this Pokemon
    detail_screen = DetailScreen(screen_manager, pokemon_id=pokemon_id)
    detail_screen.on_enter()
    
    # Render to screen
    detail_screen.render(screen)
    
    # Save screenshot
    screenshot_path = screenshots_dir / f"story-3-5-description-{name}.png"
    pygame.image.save(screen, str(screenshot_path))
    print(f"   ✅ Saved: {screenshot_path.name}")
    
    # Print description info
    print(f"   Description: \"{detail_screen.description[:60]}...\"")
    print(f"   Lines rendered: {len(detail_screen.description_lines)}")

print("\n" + "=" * 60)
print("✅ Screenshots saved to: screenshots/")
print("\nScreenshots generated:")
print("  1. story-3-5-description-pikachu.png    - Medium-length text")
print("  2. story-3-5-description-bulbasaur.png  - Short text")
print("  3. story-3-5-description-mewtwo.png     - Long text with ellipsis")
print("\n🎉 Story 3.5 Description Display Demo Complete!")

pygame.quit()
