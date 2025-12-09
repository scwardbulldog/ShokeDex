#!/usr/bin/env python3
"""
Demo: Story 5.7 Tab Layout Fixes
Demonstrates the three layout fixes after user feedback:
1. Info tab - description panel no longer overlaps tab indicator
2. Evolution tab - removed redundant sprite display
3. Stats tab - type badges don't overlap height/weight
"""

import pygame
import sys
import os
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data.database import Database
from src.ui.detail_screen import DetailScreen, DetailTab
from src.ui.colors import Colors
from src.input_manager import InputManager, InputAction

# Test Pokemon IDs to showcase different tab layouts
TEST_POKEMON = [
    25,   # Pikachu - 3-stage evolution (Info, Stats, Evolution)
    133,  # Eevee - branching evolution (multiple evolutions)
    132,  # Ditto - no evolution (single stage)
]

class MockScreenManager:
    """Mock ScreenManager for standalone demo"""
    
    def __init__(self, database):
        self.database = database
        self.state_manager = None
        self.sprite_loader = None
        self.screen_stack = []
    
    def pop(self):
        """Mock pop - just exit demo"""
        print("Back button pressed - exiting demo")
        pygame.quit()
        sys.exit(0)


def main():
    """Run tab layout fixes demo"""
    
    # Initialize pygame
    pygame.init()
    
    # Create display (480x320 for small screen testing)
    SCREEN_WIDTH = 480
    SCREEN_HEIGHT = 320
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("ShokeDex - Tab Layout Fixes Demo")
    
    # Initialize database
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'pokedex.db')
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        print("Run: python src/data/manage_db.py init && python src/data/manage_db.py seed --gen 1-3")
        return
    
    database = Database(db_path)
    
    # Create mock screen manager
    screen_manager = MockScreenManager(database)
    
    # Input manager
    input_manager = InputManager()
    
    # Initialize with first Pokemon
    current_pokemon_index = 0
    detail_screen = DetailScreen(screen_manager, TEST_POKEMON[current_pokemon_index])
    detail_screen.on_enter()
    
    # Track current tab for display
    tab_names = ["Info", "Stats", "Evolution"]
    
    # Demo instructions
    print("\n" + "="*60)
    print("TAB LAYOUT FIXES DEMO")
    print("="*60)
    print("\nFixed Issues:")
    print("1. Info tab: Description panel raised 45px to avoid tab indicator overlap")
    print("2. Evolution tab: Removed redundant sprite (evolution panel shows all)")
    print("3. Stats tab: Increased margins between type badges and height/weight")
    print("\nControls:")
    print("  LEFT/RIGHT (A/D) - Switch tabs")
    print("  UP/DOWN (W/S)    - Switch Pokemon")
    print("  SPACE            - Next test Pokemon")
    print("  ESC              - Quit")
    print("\nTest Pokemon:")
    for i, pid in enumerate(TEST_POKEMON):
        with database as db:
            pkmn = db.get_pokemon_by_id(pid)
            name = pkmn['name'].capitalize() if pkmn else f"#{pid}"
            marker = " <-- Current" if i == current_pokemon_index else ""
            print(f"  {i+1}. {name} (#{pid:03d}){marker}")
    print("\n" + "="*60 + "\n")
    
    # Main loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        delta_time = clock.tick(60) / 1000.0  # 60 FPS
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Map keys to actions
                action = input_manager.map_key_to_action(event.key)
                
                if action == InputAction.CONFIRM:
                    # SPACE - cycle to next test Pokemon
                    current_pokemon_index = (current_pokemon_index + 1) % len(TEST_POKEMON)
                    detail_screen = DetailScreen(screen_manager, TEST_POKEMON[current_pokemon_index])
                    detail_screen.on_enter()
                    
                    print(f"\nSwitched to Pokemon #{TEST_POKEMON[current_pokemon_index]:03d}")
                    print(f"Current tab: {tab_names[detail_screen.current_tab.value]}")
                
                elif action == InputAction.BACK:
                    # ESC - quit
                    running = False
                
                elif action in [InputAction.LEFT, InputAction.RIGHT, InputAction.UP, InputAction.DOWN]:
                    # Let detail screen handle tab/Pokemon navigation
                    detail_screen.handle_input(action)
                    print(f"Current tab: {tab_names[detail_screen.current_tab.value]}")
        
        # Update
        detail_screen.update(delta_time)
        
        # Render
        screen.fill(Colors.DEEP_SPACE_BLACK)
        detail_screen.render(screen)
        
        # Render demo overlay
        font = pygame.font.Font(None, 14)
        
        # Current Pokemon name in top-left corner
        with database as db:
            pkmn = db.get_pokemon_by_id(detail_screen.pokemon_id)
            name = pkmn['name'].capitalize() if pkmn else f"#{detail_screen.pokemon_id}"
        
        overlay_text = f"{name} | Tab: {tab_names[detail_screen.current_tab.value]} | SPACE=Next Pokemon"
        overlay_surface = font.render(overlay_text, True, Colors.BRIGHT_CYAN)
        overlay_bg = pygame.Surface((overlay_surface.get_width() + 8, overlay_surface.get_height() + 4), pygame.SRCALPHA)
        overlay_bg.fill((0, 0, 0, 180))
        screen.blit(overlay_bg, (4, 2))
        screen.blit(overlay_surface, (8, 4))
        
        pygame.display.flip()
    
    # Cleanup
    detail_screen.on_exit()
    pygame.quit()
    print("\nDemo complete!")


if __name__ == "__main__":
    main()
