#!/usr/bin/env python3
"""
Input Latency Testing Tool for ShokeDex (Story 1.7)

Measures end-to-end button press response time from pygame event to screen
render completion. Validates NFR-P2 requirement (<100ms latency).

This tool measures the COMPLETE input pipeline:
1. pygame.event.get() - Event detection
2. InputManager.handle_event() - Event processing  
3. HomeScreen.handle_input() - Input handling
4. HomeScreen.update() - State update
5. HomeScreen.render() - Screen rendering

Usage:
    python tools/test_input_latency.py [--iterations N] [--buttons BUTTONS]

Examples:
    python tools/test_input_latency.py --iterations 100
    python tools/test_input_latency.py --buttons LEFT,RIGHT,UP,DOWN
"""

import sys
import time
import argparse
from pathlib import Path
from typing import List, Dict
from statistics import mean, stdev

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.input_manager import InputManager, InputMode, InputAction
from src.ui.screen_manager import ScreenManager
from src.ui.home_screen import HomeScreen
from src.data.database import Database
from src.state_manager import StateManager

try:
    import pygame
except ImportError:
    print("Error: pygame is required for this tool")
    print("Install with: pip install pygame")
    sys.exit(1)


class InputLatencyTester:
    """
    Tests end-to-end input latency for button presses (Story 1.7: AC #2).
    
    Measures complete pipeline from pygame event to render completion.
    """
    
    def __init__(self, database_path: str = "data/pokedex.db"):
        """
        Initialize the latency tester.
        
        Args:
            database_path: Path to SQLite database
        """
        # Initialize pygame
        pygame.init()
        pygame.font.init()
        
        # Create display surface (headless for profiling)
        self.surface = pygame.Surface((480, 320))
        
        # Initialize database
        self.database = Database(database_path)
        
        # Initialize managers
        self.state_manager = StateManager()
        self.input_manager = InputManager(mode=InputMode.KEYBOARD)
        
        # Initialize screen manager with home screen
        self.screen_manager = ScreenManager(
            database=self.database,
            state_manager=self.state_manager,
            audio_manager=None,  # Not needed for latency tests
            input_manager=self.input_manager
        )
        
        # Create and enter home screen
        self.home_screen = HomeScreen(self.screen_manager, database=self.database)
        self.screen_manager.push(self.home_screen)
        self.home_screen.on_enter()
        
        # Input action to pygame key mapping
        self.action_to_key = {
            InputAction.LEFT: pygame.K_LEFT,
            InputAction.RIGHT: pygame.K_RIGHT,
            InputAction.UP: pygame.K_UP,
            InputAction.DOWN: pygame.K_DOWN,
            InputAction.SELECT: pygame.K_RETURN,
            InputAction.BACK: pygame.K_ESCAPE,
        }
        
        self.latencies: Dict[InputAction, List[float]] = {}
    
    def measure_single_latency(self, action: InputAction) -> float:
        """
        Measure end-to-end latency for a single button press.
        
        Measures from pygame event post to render completion.
        
        Args:
            action: Input action to test
            
        Returns:
            Latency in milliseconds
        """
        if action not in self.action_to_key:
            return 0.0
        
        key = self.action_to_key[action]
        
        # Clear event queue
        pygame.event.clear()
        
        # Start timing (Story 1.7: NFR-P2 requirement)
        start_time = time.perf_counter()
        
        # 1. Post pygame event
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))
        
        # 2. Process events through input manager
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                input_action = self.input_manager.handle_event(event)
                if input_action != InputAction.NONE:
                    # 3. Handle input on home screen
                    self.home_screen.handle_input(input_action)
        
        # 4. Update screen state (delta_time = 16.7ms for 60 FPS)
        self.home_screen.update(0.0167)
        
        # 5. Render screen (completes input→display pipeline)
        self.home_screen.render(self.surface)
        
        # End timing
        end_time = time.perf_counter()
        
        # Calculate latency in milliseconds
        latency_ms = (end_time - start_time) * 1000.0
        
        return latency_ms
    
    def test_action(self, action: InputAction, num_samples: int = 100) -> List[float]:
        """
        Test latency for a specific action over multiple iterations.
        
        Args:
            action: The input action to test
            num_samples: Number of samples to collect
            
        Returns:
            List of latency measurements in milliseconds
        """
        latencies = []
        
        print(f"\nProfiling {action.name} button ({num_samples} iterations)...")
        
        for i in range(num_samples):
            # Measure latency
            latency = self.measure_single_latency(action)
            latencies.append(latency)
            
            # Progress indicator every 20 iterations
            if (i + 1) % 20 == 0:
                print(f"  Progress: {i + 1}/{num_samples}")
        
        return latencies
    
    def test_all_actions(self, num_samples: int = 100, buttons: List[InputAction] = None):
        """
        Test latency for all (or specified) input actions.
        
        Args:
            num_samples: Number of samples per action
            buttons: List of buttons to test (None = test default set)
        """
        if buttons is None:
            buttons = [
                InputAction.LEFT,
                InputAction.RIGHT,
                InputAction.UP,
                InputAction.DOWN,
                InputAction.SELECT,
            ]
        
        print("=" * 60)
        print("ShokeDex Input Latency Profiling (Story 1.7: AC #2)")
        print("=" * 60)
        print(f"Target: < 100ms per NFR-P2")
        print(f"Iterations per button: {num_samples}")
        print("=" * 60)
        
        for action in buttons:
            latencies = self.test_action(action, num_samples)
            if latencies:
                self.latencies[action] = latencies
    
    def generate_report(self) -> str:
        """
        Generate a detailed latency report (Story 1.7: AC #2).
        
        Returns:
            Formatted report string
        """
        report = []
        report.append("\n" + "=" * 60)
        report.append("LATENCY TEST REPORT (Story 1.7)")
        report.append("=" * 60)
        report.append("Target: < 100ms per NFR-P2 (Button press → screen update)")
        report.append("")
        
        if not self.latencies:
            report.append("No data collected.")
            return "\n".join(report)
        
        # Per-action statistics
        report.append("Per-Action Latency Statistics:")
        report.append("-" * 60)
        
        all_latencies = []
        for action in sorted(self.latencies.keys(), key=lambda x: x.name):
            latencies = self.latencies[action]
            if latencies:
                latencies_sorted = sorted(latencies)
                avg = mean(latencies)
                min_lat = min(latencies)
                max_lat = max(latencies)
                std = stdev(latencies) if len(latencies) > 1 else 0.0
                p50 = latencies_sorted[len(latencies) // 2]
                p95 = latencies_sorted[int(len(latencies) * 0.95)]
                p99 = latencies_sorted[int(len(latencies) * 0.99)]
                
                report.append(f"\n{action.name}:")
                report.append(f"  Average:    {avg:6.2f}ms")
                report.append(f"  Std Dev:    {std:6.2f}ms")
                report.append(f"  Min/Max:    {min_lat:6.2f}ms / {max_lat:6.2f}ms")
                report.append(f"  Percentiles:")
                report.append(f"    P50:      {p50:6.2f}ms")
                report.append(f"    P95:      {p95:6.2f}ms")
                report.append(f"    P99:      {p99:6.2f}ms")
                
                # Pass/fail indicator (Story 1.7: Task 2 criteria)
                if avg < 80 and p95 < 100:
                    report.append(f"  Status:     ✅ PASS (avg < 80ms, p95 < 100ms)")
                elif p95 < 100:
                    report.append(f"  Status:     ⚠️  WARN (avg >= 80ms, but p95 < 100ms)")
                else:
                    report.append(f"  Status:     ❌ FAIL (p95 >= 100ms)")
                
                all_latencies.extend(latencies)
        
        # Overall statistics
        if all_latencies:
            report.append("")
            report.append("=" * 60)
            report.append("OVERALL SUMMARY")
            report.append("=" * 60)
            
            all_latencies_sorted = sorted(all_latencies)
            avg = mean(all_latencies)
            min_lat = min(all_latencies)
            max_lat = max(all_latencies)
            std = stdev(all_latencies)
            p50 = all_latencies_sorted[len(all_latencies) // 2]
            p95 = all_latencies_sorted[int(len(all_latencies) * 0.95)]
            p99 = all_latencies_sorted[int(len(all_latencies) * 0.99)]
            
            report.append(f"Average Latency: {avg:.2f}ms")
            report.append(f"Min/Max Latency: {min_lat:.2f}ms / {max_lat:.2f}ms")
            report.append(f"Std Deviation: {std:.2f}ms")
            report.append(f"P50/P95/P99: {p50:.2f}ms / {p95:.2f}ms / {p99:.2f}ms")
            report.append(f"Total Samples: {len(all_latencies)}")
            report.append(f"Target (NFR-P2): < 100ms")
            
            # Performance assessment
            report.append("")
            report.append("Performance Assessment:")
            report.append("-" * 60)
            
            if avg < 80 and p95 < 100:
                report.append("✅ PASS: Input latency meets NFR-P2 requirements")
                report.append("   Average < 80ms and P95 < 100ms")
            elif p95 < 100:
                report.append("⚠️  WARN: Input latency marginally acceptable")
                report.append("   P95 < 100ms but average >= 80ms")
            else:
                report.append("❌ FAIL: Input latency exceeds NFR-P2 requirement")
                report.append(f"   P95 ({p95:.2f}ms) >= 100ms target")
            
            if max_lat > 150:
                report.append("⚠️  WARNING: Some inputs exceeded 150ms latency")
            
            if std > 20:
                report.append("⚠️  WARNING: High variance in latency detected")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def cleanup(self):
        """Clean up resources."""
        self.input_manager.cleanup()
        pygame.quit()


def main():
    """Main entry point for input latency profiling tool (Story 1.7: Task 2)."""
    parser = argparse.ArgumentParser(
        description="Profile ShokeDex end-to-end input latency"
    )
    parser.add_argument(
        '--iterations', '-i',
        type=int,
        default=100,
        help="Number of test iterations per button (default: 100)"
    )
    parser.add_argument(
        '--buttons', '-b',
        type=str,
        default=None,
        help="Comma-separated list of buttons to test (e.g., LEFT,RIGHT,UP,DOWN)"
    )
    parser.add_argument(
        '--database', '-d',
        type=str,
        default="data/pokedex.db",
        help="Path to database file (default: data/pokedex.db)"
    )
    
    args = parser.parse_args()
    
    # Parse button list if provided
    buttons = None
    if args.buttons:
        button_names = [name.strip().upper() for name in args.buttons.split(',')]
        buttons = []
        for name in button_names:
            try:
                action = InputAction[name]
                buttons.append(action)
            except KeyError:
                print(f"Warning: Unknown button '{name}', skipping")
    
    # Create tester
    tester = InputLatencyTester(database_path=args.database)
    
    try:
        # Run profiling
        tester.test_all_actions(num_samples=args.iterations, buttons=buttons)
        
        # Generate and print report
        report = tester.generate_report()
        print(report)
        
        # Save report to file
        output_dir = Path(__file__).parent.parent / "data"
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"latency_test_{int(time.time())}.txt"
        
        with open(output_file, "w") as f:
            f.write(report)
        
        print(f"\nReport saved to: {output_file}")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    finally:
        tester.cleanup()


if __name__ == "__main__":
    main()
