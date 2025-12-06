#!/usr/bin/env python3
"""
Generate screenshots of ShokeDex UI for demo purposes
"""

import pygame
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.input_manager import InputManager, InputMode, InputAction
from src.ui import ScreenManager, HomeScreen, DetailScreen, SettingsScreen
from src.data.database import Database

# Display configuration
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320

def main():
    """Generate UI screenshots."""
    print("Generating ShokeDex screenshots...")
    
    # Initialize Pygame
    pygame.init()
    
    # Set up display
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    
    # Initialize database
    db_path = Path(__file__).parent / "data" / "pokedex.db"
    database = Database(str(db_path)) if db_path.exists() else None
    
    # Initialize screen manager
    screen_manager = ScreenManager(screen)
    
    # Inject database into screen_manager (following main.py pattern)
    screen_manager.database = database
    
    # Create screenshots directory
    screenshots_dir = Path(__file__).parent / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)
    
    # 1. Home Screen
    print("Capturing Home Screen...")
    home_screen = HomeScreen(screen_manager, database)
    home_screen.on_enter()
    screen.fill((0, 0, 0))
    home_screen.render(screen)
    pygame.image.save(screen, str(screenshots_dir / "01_home_screen.png"))
    
    # 2. Home Screen with search indicator
    print("Capturing Home Screen with selection...")
    home_screen.selected_index = 24  # Pikachu
    screen.fill((0, 0, 0))
    home_screen.render(screen)
    pygame.image.save(screen, str(screenshots_dir / "02_home_selected.png"))
    
    # 3. Detail Screen
    print("Capturing Detail Screen...")
    detail_screen = DetailScreen(screen_manager, pokemon_id=25)
    detail_screen.on_enter()
    screen.fill((0, 0, 0))
    detail_screen.render(screen)
    pygame.image.save(screen, str(screenshots_dir / "03_detail_stats.png"))
    
    # 4. Detail Screen - Evolutions Tab
    print("Capturing Detail Screen - Evolutions...")
    detail_screen.view_tab = "evolutions"
    screen.fill((0, 0, 0))
    detail_screen.render(screen)
    pygame.image.save(screen, str(screenshots_dir / "04_detail_evolutions.png"))
    
    # 5. Detail Screen - Abilities Tab
    print("Capturing Detail Screen - Abilities...")
    detail_screen.view_tab = "abilities"
    screen.fill((0, 0, 0))
    detail_screen.render(screen)
    pygame.image.save(screen, str(screenshots_dir / "05_detail_abilities.png"))
    
    # 6. Settings Screen
    print("Capturing Settings Screen...")
    settings_screen = SettingsScreen(screen_manager)
    settings_screen.on_enter()
    screen.fill((0, 0, 0))
    settings_screen.render(screen)
    pygame.image.save(screen, str(screenshots_dir / "06_settings.png"))
    
    # 7. Different Pokemon
    print("Capturing Detail Screen - Different Pokemon...")
    detail_screen2 = DetailScreen(screen_manager, pokemon_id=1)
    detail_screen2.on_enter()
    screen.fill((0, 0, 0))
    detail_screen2.render(screen)
    pygame.image.save(screen, str(screenshots_dir / "07_detail_bulbasaur.png"))
    
    pygame.quit()
    
    print(f"\nScreenshots saved to: {screenshots_dir}")
    print("Generated files:")
    for file in sorted(screenshots_dir.glob("*.png")):
        print(f"  - {file.name}")

if __name__ == "__main__":
    main()
