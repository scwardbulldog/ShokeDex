#!/usr/bin/env python3
"""
Visual demonstration of evolution chain display.

Story 5.1: Three-Stage Evolution Chain Display
This demo shows the evolution panel integrated into the DetailScreen.
"""

import pygame
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.data.database import Database
from src.ui.detail_screen import DetailScreen
from src.ui.screen_manager import ScreenManager
from src.state_manager import StateManager
from src.ui.colors import Colors


class DemoScreenManager:
    """Minimal ScreenManager for demo purposes."""
    
    def __init__(self):
        self.database = Database()
        self.state_manager = StateManager()
        self.sprite_loader = None
        self.screen_stack = []
        
    def pop(self):
        """Pop screen from stack."""
        if self.screen_stack:
            self.screen_stack.pop()
    
    def push(self, screen):
        """Push screen to stack."""
        self.screen_stack.append(screen)


def main():
    """Run evolution panel demo."""
    print("Evolution Panel Demo - Story 5.1")
    print("=" * 50)
    print()
    
    # Initialize pygame
    pygame.init()
    
    # Screen size options
    SMALL_SCREEN = (480, 320)
    LARGE_SCREEN = (800, 480)
    
    # Choose screen size
    print("Choose screen size:")
    print("1. Small (480x320)")
    print("2. Large (800x480)")
    choice = input("Enter choice (1 or 2): ").strip()
    
    screen_size = SMALL_SCREEN if choice == "1" else LARGE_SCREEN
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Evolution Panel Demo")
    
    # Pokemon to display (with different evolution chains)
    test_pokemon = [
        (4, "Charmander (3-stage chain: Charmander → Charmeleon → Charizard)"),
        (1, "Bulbasaur (3-stage chain: Bulbasaur → Ivysaur → Venusaur)"),
        (7, "Squirtle (3-stage chain: Squirtle → Wartortle → Blastoise)"),
        (25, "Pikachu (2-stage chain: Pikachu → Raichu)"),
        (132, "Ditto (single stage, no evolutions)"),
    ]
    
    print()
    print("Test Pokemon:")
    for i, (pid, desc) in enumerate(test_pokemon, 1):
        print(f"{i}. {desc}")
    
    choice = input(f"\nEnter choice (1-{len(test_pokemon)}): ").strip()
    try:
        idx = int(choice) - 1
        pokemon_id, description = test_pokemon[idx]
    except (ValueError, IndexError):
        print("Invalid choice, using Charmander (#4)")
        pokemon_id = 4
        description = test_pokemon[0][1]
    
    print(f"\nDisplaying: {description}")
    print("Press Q to quit, or click X to close window")
    print()
    
    # Create screen manager and detail screen
    screen_manager = DemoScreenManager()
    detail_screen = DetailScreen(screen_manager, pokemon_id=pokemon_id)
    detail_screen.on_enter()
    
    # Main loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
        
        # Clear screen
        screen.fill(Colors.DARK_BLUE)
        
        # Render detail screen
        detail_screen.render(screen)
        
        # Update display
        pygame.display.flip()
        clock.tick(30)  # 30 FPS
    
    pygame.quit()
    print("\nDemo complete!")


if __name__ == "__main__":
    main()
