"""
Quick demo of tab-based DetailScreen (Story 5.7)

Demonstrates:
- L/R buttons to switch tabs
- UP/DOWN buttons to navigate Pokémon
- Tab indicator at bottom
- Tab state preservation
"""

import pygame
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.detail_screen import DetailScreen, DetailTab
from src.ui.screen_manager import ScreenManager
from src.data.database import Database
from src.input_manager import InputManager, InputAction
from src.state_manager import StateManager

def main():
    # Initialize pygame
    pygame.init()
    
    # Create display (480x320 for small screen testing)
    screen = pygame.display.set_mode((480, 320))
    pygame.display.set_caption("ShokeDex - Tab System Demo")
    
    # Initialize managers
    database = Database()
    state_manager = StateManager()
    input_manager = InputManager()
    screen_manager = ScreenManager(database, state_manager, input_manager)
    
    # Create DetailScreen for Pikachu
    detail = DetailScreen(screen_manager, pokemon_id=25)
    detail.on_enter()
    
    # Game loop
    clock = pygame.time.Clock()
    running = True
    
    print("\n" + "="*50)
    print("TAB SYSTEM DEMO - Story 5.7")
    print("="*50)
    print("Controls:")
    print("  LEFT/RIGHT: Switch tabs")
    print("  UP/DOWN: Navigate Pokémon")
    print("  ESC: Quit demo")
    print("\nCurrent: Pikachu #25 | Tab: INFO")
    print("="*50 + "\n")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                action = None
                
                if event.key == pygame.K_LEFT:
                    action = InputAction.LEFT
                    print("← Previous tab")
                elif event.key == pygame.K_RIGHT:
                    action = InputAction.RIGHT
                    print("→ Next tab")
                elif event.key == pygame.K_UP:
                    action = InputAction.UP
                    print("↑ Next Pokémon")
                elif event.key == pygame.K_DOWN:
                    action = InputAction.DOWN
                    print("↓ Previous Pokémon")
                elif event.key == pygame.K_ESCAPE:
                    running = False
                
                if action:
                    detail.handle_input(action)
                    tab_name = detail.current_tab.name
                    print(f"  Current: Pokémon #{detail.pokemon_id} | Tab: {tab_name}")
        
        # Update and render
        detail.update(clock.get_time() / 1000.0)
        detail.render(screen)
        
        pygame.display.flip()
        clock.tick(30)  # 30 FPS
    
    # Cleanup
    detail.on_exit()
    pygame.quit()
    print("\nDemo complete!")

if __name__ == "__main__":
    main()
