#!/usr/bin/env python3
"""
Main entry point for ShokeDex application

Initializes Pygame, sets up the display, and runs the main game loop.
"""

import logging
import pygame
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.input_manager import InputManager, InputMode, InputAction
from src.ui import ScreenManager, HomeScreen
from src.data.database import Database
from src.state_manager import StateManager
from src.audio_manager import AudioManager

# Module logger
logger = logging.getLogger(__name__)


# Display configuration (optimized for 480x320 LCD, can be overridden by env vars)
DISPLAY_WIDTH = int(os.environ.get('SHOKEDEX_WIDTH', '480'))
DISPLAY_HEIGHT = int(os.environ.get('SHOKEDEX_HEIGHT', '320'))
FPS = int(os.environ.get('SHOKEDEX_FPS', '30'))

# Application configuration
APP_NAME = "ShokeDex"
DATABASE_PATH = "data/pokedex.db"
ASSETS_PATH = "assets"


class ShokeDexApp:
    """Main application class for ShokeDex."""
    
    def __init__(self):
        """Initialize the application."""
        # Validate and create required directories
        self._validate_directories()
        
        # Log configuration
        self._log_configuration()
        
        # Initialize Pygame
        pygame.init()
        
        # Set up display
        self.screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        pygame.display.set_caption(APP_NAME)
        
        # Set up clock for FPS control
        self.clock = pygame.time.Clock()
        
        # Initialize state manager
        self.state_manager = StateManager()
        self.state_manager.increment_session()
        
        # Initialize audio manager
        volume = self.state_manager.get_volume()
        self.audio_manager = AudioManager(volume=volume)
        
        # Log audio status
        if self.audio_manager.is_enabled():
            print(f"Audio system ready (volume: {volume:.0%})")
            missing = self.audio_manager.get_missing_cries()
            if missing:
                print(f"Warning: Missing {len(missing)} cry audio files")
        else:
            print("Audio system disabled")
        
        # Initialize input manager (use saved preference)
        input_mode_str = self.state_manager.get_input_mode()
        input_mode = InputMode.GPIO if input_mode_str == 'gpio' else InputMode.KEYBOARD
        self.input_manager = InputManager(mode=input_mode)
        
        # Initialize screen manager
        self.screen_manager = ScreenManager(self.screen)
        
        # Attach state_manager to screen_manager for screen access (Story 1.5)
        self.screen_manager.state_manager = self.state_manager
        self.screen_manager.audio_manager = self.audio_manager
        self.screen_manager.input_manager = self.input_manager
        
        # Initialize database
        self.database = self._init_database()
        self.screen_manager.database = self.database
        
        # Set up initial screen - ALWAYS HomeScreen (Story 4.3: AC #1, #6)
        # Get last viewed state for boot logging
        last_pokemon_id = self.state_manager.get_last_viewed_id()
        last_generation = self.state_manager.get_last_viewed_generation()
        logger.info(
            f"Booting to HomeScreen with Pokémon #{last_pokemon_id} (Generation {last_generation})"
        )
        
        home_screen = HomeScreen(self.screen_manager, self.database)
        self.screen_manager.push(home_screen)
        
        # Verify boot state (Story 4.3: AC #6)
        assert self.screen_manager.get_stack_depth() == 1, "Screen stack should have exactly 1 screen on boot"
        logger.debug(f"Boot complete: screen stack depth = {self.screen_manager.get_stack_depth()}")
        
        # Application state
        self.running = True
    
    def _validate_directories(self):
        """Validate and create required directories."""
        project_root = Path(__file__).parent.parent
        
        # Create data directory if missing
        data_dir = project_root / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create assets directories if missing
        assets_dir = project_root / ASSETS_PATH
        sprites_dir = assets_dir / "sprites"
        thumb_dir = sprites_dir / "thumb"
        detail_dir = sprites_dir / "detail"
        
        for directory in [assets_dir, sprites_dir, thumb_dir, detail_dir]:
            if not directory.exists():
                print(f"Warning: Directory missing: {directory}")
                directory.mkdir(parents=True, exist_ok=True)
        
        # Validate sprite assets are accessible
        if not thumb_dir.exists() or not list(thumb_dir.glob('*.png')):
            print(f"Warning: No sprite assets found in {thumb_dir}")
        
        if not detail_dir.exists() or not list(detail_dir.glob('*.png')):
            print(f"Warning: No detail sprites found in {detail_dir}")
    
    def _log_configuration(self):
        """Log loaded configuration for debugging."""
        print(f"Configuration:")
        print(f"  Display: {DISPLAY_WIDTH}x{DISPLAY_HEIGHT}")
        print(f"  Target FPS: {FPS}")
        print(f"  Database: {DATABASE_PATH}")
        print(f"  Assets: {ASSETS_PATH}")
        
        # Validate configuration values
        if DISPLAY_WIDTH <= 0 or DISPLAY_HEIGHT <= 0:
            raise ValueError(f"Invalid display resolution: {DISPLAY_WIDTH}x{DISPLAY_HEIGHT}")
        if FPS <= 0:
            raise ValueError(f"Invalid FPS target: {FPS}")
    
    def _init_database(self):
        """Initialize database connection and validate schema."""
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
        else:
            print(f"Database found at {db_path}")
        
        # Validate database schema
        db = Database(str(db_path))
        try:
            with db as connection:
                # Check if pokemon table exists
                cursor = connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='pokemon'"
                )
                if not cursor.fetchone():
                    print("Warning: Pokemon table not found, creating schema...")
                    connection.create_schema()
                else:
                    print("Database schema validated.")
        except Exception as e:
            print(f"Error validating database: {e}")
            return None
        
        return db
    
    def handle_events(self):
        """Handle Pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.TEXTINPUT:
                # Pass text input to current screen if it has the method
                current_screen = self.screen_manager.get_current()
                if current_screen and hasattr(current_screen, 'handle_text_input'):
                    current_screen.handle_text_input(event.text)
            elif event.type == pygame.KEYDOWN:
                # Handle backspace specially for text input
                current_screen = self.screen_manager.get_current()
                if event.key == pygame.K_BACKSPACE:
                    if current_screen and hasattr(current_screen, 'handle_backspace'):
                        current_screen.handle_backspace()
                        continue
                
                # Process input through input manager
                action = self.input_manager.process_event(event)
                
                # Handle quit with BACK action on home screen
                if action == InputAction.BACK:
                    if self.screen_manager.get_stack_depth() <= 1:
                        self.running = False
                        continue
                
                # Pass action to screen manager
                if action != InputAction.NONE:
                    self.screen_manager.handle_input(action)
            elif event.type == pygame.KEYUP:
                # Handle key release to stop hold-to-scroll
                action = self.input_manager.get_action_from_keyup(event)
                if action != InputAction.NONE:
                    self.screen_manager.handle_input_release(action)
    
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
        
        try:
            while self.running:
                # Calculate delta time
                delta_time = self.clock.tick(FPS) / 1000.0
                
                # Handle events
                self.handle_events()
                
                # Update
                self.update(delta_time)
                
                # Render
                self.render()
        finally:
            # Ensure cleanup happens even on unexpected exit (Story 1.5: State Persistence)
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources before exit."""
        print("Shutting down...")
        
        # Save state
        if self.state_manager.save_state():
            print("State saved successfully")
        
        # Clean up audio
        self.audio_manager.cleanup()
        
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
