#!/usr/bin/env python3
"""
UI Demo for ShokeDex

Demonstrates the UI system with mock data (no database required).
"""

import pygame
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.input_manager import InputManager, InputMode, InputAction
from src.ui import ScreenManager, HomeScreen


# Display configuration
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320
FPS = 30


def main():
    """Run the UI demo."""
    print("Starting ShokeDex UI Demo...")
    print("This demo runs without a database, using mock data.")
    print()
    print("Controls:")
    print("  Arrow Keys / WASD: Navigate")
    print("  Enter / Space: Select")
    print("  Escape / Backspace: Back")
    print("  Tab: Settings")
    print("  ESC on home screen: Quit")
    print()
    
    # Initialize Pygame
    pygame.init()
    
    # Set up display
    screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    pygame.display.set_caption("ShokeDex - UI Demo")
    
    # Set up clock
    clock = pygame.time.Clock()
    
    # Initialize input manager
    input_manager = InputManager(mode=InputMode.KEYBOARD)
    
    # Initialize screen manager
    screen_manager = ScreenManager(screen)
    
    # Create home screen (without database - will use demo data)
    home_screen = HomeScreen(screen_manager, database=None)
    screen_manager.push(home_screen)
    
    # Main loop
    running = True
    while running:
        # Calculate delta time
        delta_time = clock.tick(FPS) / 1000.0
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Process input
                action = input_manager.process_event(event)
                
                # Pass to screen manager
                if action != InputAction.NONE:
                    screen_manager.handle_input(action)
                
                # Quit with ESC on home screen
                if event.key == pygame.K_ESCAPE:
                    if screen_manager.get_stack_depth() <= 1:
                        running = False
        
        # Update
        screen_manager.update(delta_time)
        
        # Render
        screen.fill((0, 0, 0))
        screen_manager.render()
        pygame.display.flip()
    
    # Cleanup
    input_manager.cleanup()
    pygame.quit()
    print("Demo finished!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
