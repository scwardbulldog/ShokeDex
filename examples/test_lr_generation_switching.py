#!/usr/bin/env python3
"""
Visual test for L/R button generation switching (Story 1.4)

Tests:
- LEFT key (L button): Previous generation
- RIGHT key (R button): Next generation  
- Visual fade transitions
- Badge glow effect
- State persistence

Keys:
- LEFT/A: Previous generation (L button)
- RIGHT/D: Next generation (R button)
- ESC: Quit
"""

import pygame
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ui.home_screen import HomeScreen
from src.data.database import Database
from src.input_manager import InputManager, InputAction


def main():
    """Run visual test for L/R generation switching"""
    
    # Initialize pygame
    pygame.init()
    
    # Create display
    screen = pygame.display.set_mode((480, 320))
    pygame.display.set_caption("Story 1.4: L/R Button Generation Switching Test")
    
    # Initialize database
    db_path = "data/pokedex.db"
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        print("Please run: python src/data/manage_db.py init && python src/data/manage_db.py seed --gen 1-3")
        return
    
    db = Database(db_path)
    
    # Create mock screen manager
    class MockScreenManager:
        def __init__(self):
            self.width = 480
            self.height = 320
            self.database = db
            self.state_manager = None
            self.input_manager = None
    
    screen_manager = MockScreenManager()
    
    # Create HomeScreen
    home_screen = HomeScreen(screen_manager, database=db)
    home_screen.on_enter()
    
    # Create input manager
    input_manager = InputManager()
    
    # Game loop
    clock = pygame.time.Clock()
    running = True
    
    print("\n=== Story 1.4: L/R Generation Switching Test ===")
    print("Controls:")
    print("  LEFT/A  - Previous generation (L button)")
    print("  RIGHT/D - Next generation (R button)")
    print("  ESC     - Quit")
    print("\nWatch for:")
    print("  - Fade-out → Fade-in transitions")
    print("  - Badge glow effect (bright cyan)")
    print("  - Generation cycling: Kanto ↔ Johto ↔ Hoenn")
    print("  - Position counter updates")
    print("  - Transition completes in <300ms")
    print("=" * 50)
    print(f"Starting generation: {home_screen.current_generation}")
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    action = input_manager.handle_event(event)
                    if action:
                        print(f"\nAction: {action}")
                        
                        # Track generation before switch
                        old_gen = home_screen.current_generation
                        
                        # Handle input
                        home_screen.handle_input(action)
                        
                        # Log generation switch
                        if action in [InputAction.LEFT, InputAction.RIGHT]:
                            direction = "previous" if action == InputAction.LEFT else "next"
                            print(f"  Switching to {direction} generation...")
                            print(f"  From: Generation {old_gen}")
                            print(f"  Transition started: is_transitioning={home_screen.is_transitioning}")
        
        # Update
        delta_time = clock.tick(60) / 1000.0  # 60 FPS
        home_screen.update(delta_time)
        
        # Check if transition just completed
        if not home_screen.is_transitioning and home_screen.transition_timer == 0.0:
            current_gen = home_screen.current_generation
            if 'last_logged_gen' not in locals() or last_logged_gen != current_gen:
                print(f"  To: Generation {current_gen} ({len(home_screen.pokemon_list)} Pokemon)")
                if home_screen.generation_badge:
                    print(f"  Badge glow: {home_screen.generation_badge.active_glow}")
                last_logged_gen = current_gen
        
        # Render
        home_screen.render(screen)
        
        # Draw FPS counter
        fps = int(clock.get_fps())
        font = pygame.font.Font(None, 20)
        fps_text = font.render(f"FPS: {fps}", True, (0, 255, 0))
        screen.blit(fps_text, (400, 5))
        
        # Draw transition status
        if home_screen.is_transitioning:
            status_text = font.render("TRANSITIONING", True, (255, 255, 0))
            screen.blit(status_text, (5, 295))
        
        pygame.display.flip()
    
    # Cleanup
    pygame.quit()
    print("\nTest complete!")


if __name__ == "__main__":
    main()
