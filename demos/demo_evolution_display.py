#!/usr/bin/env python3
"""
Visual demonstration of evolution chain display.

Story 5.1: Three-Stage Evolution Chain Display
Story 5.2: Branching Evolution Display
Story 5.3: Single-Stage Pokémon Handling ("No evolutions" message)
Story 5.4: Evolution Requirement Display (Level/Stone/Trade)

This demo showcases all evolution requirement types:
- Level-based (Charmander, Bulbasaur, Squirtle)
- Stone-based (Pikachu → Raichu with Thunder Stone)
- Trade-based (Kadabra → Alakazam)
- Trade with item (Onix → Steelix with Metal Coat)
- Happiness-based (Golbat → Crobat)
- Conditional stats (Tyrogue branches based on Attack vs Defense)
- Happiness with time-of-day (Eevee → Espeon/Umbreon)
"""

import pygame
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

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
    print("Evolution Panel Demo - Stories 5.1, 5.2, 5.3, 5.4")
    print("=" * 60)
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
    pygame.display.set_caption("Evolution Panel Demo - All Requirement Types")
    
    # Pokemon to display - organized by requirement type (Story 5.4)
    test_pokemon = [
        # Level-based requirements (Story 5.1)
        (4, "Charmander (Level 16 → Charmeleon, Level 36 → Charizard)"),
        (1, "Bulbasaur (Level 16 → Ivysaur, Level 32 → Venusaur)"),
        (7, "Squirtle (Level 16 → Wartortle, Level 36 → Blastoise)"),
        
        # Stone-based requirements (Story 5.4 AC #2)
        (25, "Pikachu (Thunder Stone → Raichu)"),
        
        # Trade requirements (Story 5.4 AC #3)
        (64, "Kadabra (Trade → Alakazam)"),
        (95, "Onix (Trade holding Metal Coat → Steelix)"),
        
        # Happiness requirements (Story 5.4 AC #7)
        (42, "Golbat (High Friendship → Crobat)"),
        
        # Branching with mixed requirements (Story 5.2 + 5.4)
        (133, "Eevee (5 branches: Stones + Happiness with Day/Night)"),
        (236, "Tyrogue (3 branches based on Attack vs Defense stats)"),
        (265, "Wurmple (2 branches: Silcoon/Cascoon)"),
        
        # Single-stage (no evolutions) (Story 5.3)
        (132, "Ditto (Gen 1 single-stage, no evolutions)"),
        (83, "Farfetch'd (Gen 1 single-stage, no evolutions)"),
        (201, "Unown (Gen 2 single-stage, no evolutions)"),
        (359, "Absol (Gen 3 single-stage, no evolutions)"),
        
        # Additional examples
        (134, "Vaporeon (view from Eevee branch)"),
    ]
    
    print()
    print("Test Pokemon (grouped by requirement type):")
    print()
    for i, (pid, desc) in enumerate(test_pokemon, 1):
        print(f"{i:2d}. {desc}")
    
    choice = input(f"\nEnter choice (1-{len(test_pokemon)}): ").strip()
    try:
        idx = int(choice) - 1
        pokemon_id, description = test_pokemon[idx]
    except (ValueError, IndexError):
        print("Invalid choice, using Eevee (#133)")
        pokemon_id = 133
        description = "Eevee"
    
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
