#!/usr/bin/env python3
"""
Main entry point for ShokeDex application

Initializes Pygame, sets up the display, and runs the main game loop.
"""

import pygame
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.input_manager import InputManager, InputMode, InputAction
from src.ui import ScreenManager, HomeScreen
from src.data.database import Database


# Display configuration (optimized for 480x320 LCD)
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320
FPS = 30

# Application configuration
APP_NAME = "ShokeDex"
DATABASE_PATH = "data/pokedex.db"


class ShokeDexApp:
    """Main application class for ShokeDex."""
    
    def __init__(self):
        """Initialize the application."""
        # Initialize Pygame
        pygame.init()
        
        # Set up display
        self.screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        pygame.display.set_caption(APP_NAME)
        
        # Set up clock for FPS control
        self.clock = pygame.time.Clock()
        
        # Initialize input manager (start with keyboard mode)
        self.input_manager = InputManager(mode=InputMode.KEYBOARD)
        
        # Initialize screen manager
        self.screen_manager = ScreenManager(self.screen)
        
        # Initialize database
        self.database = self._init_database()
        
        # Set up initial screen
        home_screen = HomeScreen(self.screen_manager, self.database)
        self.screen_manager.push(home_screen)
        
        # Application state
        self.running = True
    
    def _init_database(self):
        """Initialize database connection."""
        db_path = Path(__file__).parent.parent / DATABASE_PATH
        
        # Check if database exists
        if not db_path.exists():
            print(f"Database not found at {db_path}")
            print("Creating empty database...")
            db_path.parent.mkdir(parents=True, exist_ok=True)
            db = Database(str(db_path))
            try:
                with db as connection:
                    connection.create_schema()
                print("Database created successfully.")
            except Exception as e:
                print(f"Error creating database: {e}")
                return None
        
        return Database(str(db_path))
    
    def handle_events(self):
        """Handle Pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                # Process input through input manager
                action = self.input_manager.process_event(event)
                
                # Pass action to screen manager
                if action != InputAction.NONE:
                    self.screen_manager.handle_input(action)
                
                # Handle quit with ESC (if on home screen)
                if event.key == pygame.K_ESCAPE:
                    if self.screen_manager.get_stack_depth() <= 1:
                        self.running = False
    
    def update(self, delta_time: float):
        """
        Update application state.
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        self.screen_manager.update(delta_time)
    
    def render(self):
        """Render the current frame."""
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Render current screen
        self.screen_manager.render()
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        """Run the main application loop."""
        print(f"Starting {APP_NAME}...")
        print(f"Display: {DISPLAY_WIDTH}x{DISPLAY_HEIGHT}")
        print(f"Input mode: {self.input_manager.get_mode_name()}")
        print("Press ESC to quit.")
        
        while self.running:
            # Calculate delta time
            delta_time = self.clock.tick(FPS) / 1000.0
            
            # Handle events
            self.handle_events()
            
            # Update
            self.update(delta_time)
            
            # Render
            self.render()
        
        # Cleanup
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources before exit."""
        print("Shutting down...")
        
        # Clean up input manager
        self.input_manager.cleanup()
        
        # Quit Pygame
        pygame.quit()
        
        print("Goodbye!")


def main():
    """Main entry point."""
    try:
        app = ShokeDexApp()
        app.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
