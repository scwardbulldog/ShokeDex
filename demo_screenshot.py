#!/usr/bin/env python3
"""
Generate screenshots of ShokeDex UI for demo purposes

Story 5.7: Added tab-based DetailScreen screenshots (Info/Stats/Evolution)
"""

import pygame
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.input_manager import InputManager, InputMode, InputAction
from src.ui import ScreenManager, HomeScreen, DetailScreen
from src.ui.detail_screen import DetailTab
from src.data.database import Database
from src.state_manager import StateManager

# Display configuration
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320

def main():
    """Generate UI screenshots."""
    print("Generating ShokeDex screenshots...")
    print("Story 5.7: Testing tab-based DetailScreen layout\n")
    
    # Initialize Pygame
    pygame.init()
    
    # Set up display (headless for screenshot generation)
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    
    # Initialize database
    db_path = Path(__file__).parent / "data" / "pokedex.db"
    
    with Database(str(db_path)) as database:
        # Initialize managers
        state_manager = StateManager()
        input_manager = InputManager(mode=InputMode.KEYBOARD)
        
        # Initialize screen manager
        screen_manager = ScreenManager(screen)
        screen_manager.database = database
        screen_manager.state_manager = state_manager
        screen_manager.input_manager = input_manager
        
        # Create screenshots directory
        screenshots_dir = Path(__file__).parent / "screenshots"
        screenshots_dir.mkdir(exist_ok=True)
        
        # 1. Home Screen
        print("Capturing Home Screen...")
        home_screen = HomeScreen(screen_manager, database)
        home_screen.on_enter()
        screen.fill((10, 14, 26))  # Deep space black
        home_screen.render(screen)
        pygame.image.save(screen, str(screenshots_dir / "01_home_screen.png"))
        
        # 2. Home Screen with selection
        print("Capturing Home Screen with selection...")
        home_screen.selected_index = 24  # Pikachu
        screen.fill((10, 14, 26))
        home_screen.render(screen)
        pygame.image.save(screen, str(screenshots_dir / "02_home_selected.png"))
        
        # Story 5.7: Capture all three tabs for multiple Pokémon
        test_pokemon = [
            (25, "Pikachu", "Has evolution chain (Pichu → Pikachu → Raichu)"),
            (133, "Eevee", "Branching evolution (5 evolutions in Gen 1-3)"),
            (132, "Ditto", "No evolutions (single-stage Pokémon)")
        ]
        
        screenshot_num = 3
        
        for pokemon_id, name, description in test_pokemon:
            print(f"\nCapturing {name} (#{pokemon_id:03d}) - {description}")
            
            # Create detail screen
            detail_screen = DetailScreen(screen_manager, pokemon_id=pokemon_id)
            detail_screen.on_enter()
            
            # Capture all three tabs
            tabs = [
                (DetailTab.INFO, "info", "Description and Pokédex entry"),
                (DetailTab.STATS, "stats", "Stats, types, physical measurements"),
                (DetailTab.EVOLUTION, "evolution", "Evolution chain display")
            ]
            
            for tab, tab_name, tab_desc in tabs:
                detail_screen.current_tab = tab
                screen.fill((10, 14, 26))
                detail_screen.render(screen)
                
                filename = f"{screenshot_num:02d}_{name.lower()}_{tab_name}_tab.png"
                filepath = screenshots_dir / filename
                pygame.image.save(screen, str(filepath))
                print(f"  ✓ {tab_name.capitalize()} tab: {filepath.name}")
                screenshot_num += 1
            
            detail_screen.on_exit()
    
    pygame.quit()
    
    print(f"\n{'='*50}")
    print(f"Screenshots saved to: {screenshots_dir}")
    print(f"{'='*50}")
    print("\nGenerated files:")
    for file in sorted(screenshots_dir.glob("*.png")):
        print(f"  - {file.name}")
    
    print("\nStory 5.7 Visual Testing Complete!")
    print("Verify:")
    print("  1. All three tabs visible with correct content")
    print("  2. Tab indicator shows current tab highlighted")
    print("  3. No content overflow or cutoff")
    print("  4. Holographic styling consistent across tabs")
    print("  5. Evolution panel shows correctly for branching/no-evolution cases")

if __name__ == "__main__":
    main()
