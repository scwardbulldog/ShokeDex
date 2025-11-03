#!/usr/bin/env python3
"""
Performance Profiling Tool for ShokeDex

Runs the application with performance monitoring enabled and generates
detailed performance reports for optimization on Raspberry Pi.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pygame
from src.performance_monitor import PerformanceMonitor, PerformanceProfiler
from src.input_manager import InputManager, InputMode, InputAction
from src.ui import ScreenManager, HomeScreen
from src.data.database import Database


# Display configuration
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320
FPS = 30

# Profiling configuration
PROFILE_DURATION = 60  # seconds
SAMPLE_INTERVAL = 1.0  # seconds


class ProfiledApp:
    """ShokeDex application with performance profiling."""
    
    def __init__(self):
        """Initialize profiled application."""
        # Initialize Pygame
        pygame.init()
        
        # Set up display
        self.screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        pygame.display.set_caption("ShokeDex - Performance Profiling")
        
        # Set up clock
        self.clock = pygame.time.Clock()
        
        # Initialize performance monitoring
        self.monitor = PerformanceMonitor(history_size=100)
        self.profiler = PerformanceProfiler()
        
        # Initialize input manager
        self.input_manager = InputManager(mode=InputMode.KEYBOARD)
        
        # Initialize screen manager
        self.screen_manager = ScreenManager(self.screen)
        
        # Initialize database
        db_path = Path(__file__).parent.parent / "data" / "pokedex.db"
        self.database = Database(str(db_path)) if db_path.exists() else None
        
        if self.database:
            home_screen = HomeScreen(self.screen_manager, self.database)
            self.screen_manager.push(home_screen)
        else:
            print("Warning: Database not found. Running without data.")
        
        # Application state
        self.running = True
        self.last_sample_time = time.time()
    
    def handle_events(self):
        """Handle Pygame events."""
        start = self.profiler.start_section("event_handling")
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.TEXTINPUT:
                current_screen = self.screen_manager.get_current()
                if current_screen and hasattr(current_screen, 'handle_text_input'):
                    current_screen.handle_text_input(event.text)
            elif event.type == pygame.KEYDOWN:
                current_screen = self.screen_manager.get_current()
                if event.key == pygame.K_BACKSPACE:
                    if current_screen and hasattr(current_screen, 'handle_backspace'):
                        current_screen.handle_backspace()
                        continue
                
                action = self.input_manager.process_event(event)
                
                if action == InputAction.BACK:
                    if self.screen_manager.get_stack_depth() <= 1:
                        self.running = False
                        continue
                
                if action != InputAction.NONE:
                    self.screen_manager.handle_input(action)
        
        self.profiler.end_section("event_handling", start)
    
    def update(self, delta_time: float):
        """Update application state."""
        start = self.profiler.start_section("update")
        self.screen_manager.update(delta_time)
        self.profiler.end_section("update", start)
    
    def render(self):
        """Render the current frame."""
        start = self.profiler.start_section("render")
        
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Render current screen
        self.screen_manager.render()
        
        # Draw performance overlay
        self.draw_performance_overlay()
        
        # Update display
        pygame.display.flip()
        
        self.profiler.end_section("render", start)
    
    def draw_performance_overlay(self):
        """Draw performance statistics on screen."""
        stats = self.monitor.get_stats()
        
        # Create font
        try:
            font = pygame.font.Font(None, 20)
        except:
            return
        
        # Prepare text
        texts = [
            f"FPS: {stats['fps_current']:.1f} (avg: {stats['fps_avg']:.1f})",
            f"CPU: {stats['cpu_percent']:.1f}% (avg: {stats['cpu_avg']:.1f}%)",
            f"MEM: {stats['memory_mb']:.1f}MB",
        ]
        
        # Draw background
        overlay_height = len(texts) * 22 + 10
        overlay_surface = pygame.Surface((200, overlay_height))
        overlay_surface.set_alpha(180)
        overlay_surface.fill((0, 0, 0))
        self.screen.blit(overlay_surface, (10, 10))
        
        # Draw text
        y = 15
        for text in texts:
            surface = font.render(text, True, (0, 255, 0))
            self.screen.blit(surface, (15, y))
            y += 22
    
    def run(self, duration: float = PROFILE_DURATION):
        """
        Run the profiled application.
        
        Args:
            duration: How long to run the profiling (in seconds)
        """
        print("=" * 60)
        print("ShokeDex Performance Profiling")
        print("=" * 60)
        print(f"Display: {DISPLAY_WIDTH}x{DISPLAY_HEIGHT}")
        print(f"Target FPS: {FPS}")
        print(f"Profile Duration: {duration}s")
        print()
        print("The application will run with performance monitoring enabled.")
        print("Navigate through screens normally to generate realistic data.")
        print("Press ESC to exit early.")
        print("=" * 60)
        print()
        
        start_time = time.time()
        
        while self.running:
            # Check if duration exceeded
            elapsed = time.time() - start_time
            if elapsed >= duration:
                print("\nProfile duration reached. Shutting down...")
                break
            
            # Calculate delta time
            delta_time = self.clock.tick(FPS) / 1000.0
            
            # Record frame
            self.monitor.record_frame()
            
            # Sample CPU/memory periodically
            if time.time() - self.last_sample_time >= SAMPLE_INTERVAL:
                self.monitor.record_cpu_memory()
                self.last_sample_time = time.time()
            
            # Handle events
            self.handle_events()
            
            # Update
            self.update(delta_time)
            
            # Render
            self.render()
        
        # Generate reports
        self.generate_reports()
        
        # Cleanup
        self.cleanup()
    
    def generate_reports(self):
        """Generate and save performance reports."""
        print("\n" + "=" * 60)
        print("Generating Performance Reports")
        print("=" * 60)
        
        # Performance monitor report
        monitor_report = self.monitor.get_report()
        print(monitor_report)
        
        # Profiler report
        print("\n")
        profiler_report = self.profiler.get_report()
        print(profiler_report)
        
        # Save reports to file
        output_dir = Path(__file__).parent.parent / "data"
        output_dir.mkdir(exist_ok=True)
        timestamp = int(time.time())
        
        # Save combined report
        output_file = output_dir / f"performance_profile_{timestamp}.txt"
        with open(output_file, "w") as f:
            f.write("ShokeDex Performance Profile Report\n")
            f.write(f"Generated: {time.ctime()}\n")
            f.write("=" * 60 + "\n\n")
            f.write(monitor_report)
            f.write("\n\n")
            f.write(profiler_report)
        
        print(f"\nReport saved to: {output_file}")
        
        # Performance assessment
        print("\n" + "=" * 60)
        print("Performance Assessment")
        print("=" * 60)
        
        if self.monitor.is_performance_adequate(target_fps=FPS, max_cpu=80.0):
            print("✓ Performance meets targets for Raspberry Pi 3B+")
        else:
            print("✗ Performance needs optimization")
            
            stats = self.monitor.get_stats()
            if stats['fps_avg'] < FPS * 0.9:
                print(f"  - FPS is below target: {stats['fps_avg']:.1f} < {FPS}")
            if stats['cpu_avg'] > 80.0:
                print(f"  - CPU usage is high: {stats['cpu_avg']:.1f}% > 80%")
        
        print("=" * 60)
    
    def cleanup(self):
        """Clean up resources."""
        self.input_manager.cleanup()
        pygame.quit()


def main():
    """Main entry point."""
    # Parse arguments
    duration = PROFILE_DURATION
    if len(sys.argv) > 1:
        try:
            duration = float(sys.argv[1])
        except ValueError:
            print(f"Invalid duration: {sys.argv[1]}, using default: {duration}s")
    
    # Run profiling
    app = ProfiledApp()
    
    try:
        app.run(duration=duration)
    except KeyboardInterrupt:
        print("\n\nProfiling interrupted by user")
        app.generate_reports()
        app.cleanup()
    except Exception as e:
        print(f"\nError during profiling: {e}")
        import traceback
        traceback.print_exc()
        app.cleanup()


if __name__ == "__main__":
    main()
