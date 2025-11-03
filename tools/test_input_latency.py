#!/usr/bin/env python3
"""
Input Latency Testing Tool for ShokeDex

Tests and measures the latency of physical button inputs on Raspberry Pi.
This tool helps verify that button presses are responsive and meet target latency requirements.
"""

import sys
import time
from pathlib import Path
from typing import List, Dict
from statistics import mean, stdev

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.input_manager import InputManager, InputMode, InputAction

try:
    import pygame
except ImportError:
    print("Error: pygame is required for this tool")
    print("Install with: pip install pygame")
    sys.exit(1)


class InputLatencyTester:
    """Tests input latency for button presses."""
    
    def __init__(self, mode: InputMode = InputMode.KEYBOARD):
        """
        Initialize the latency tester.
        
        Args:
            mode: Input mode to test (KEYBOARD or GPIO)
        """
        self.mode = mode
        self.input_manager = InputManager(mode=mode)
        self.latencies: Dict[InputAction, List[float]] = {}
        
        # Initialize pygame for event handling
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480))
        pygame.display.set_caption("Input Latency Tester")
        self.clock = pygame.time.Clock()
    
    def test_action(self, action: InputAction, num_samples: int = 10) -> List[float]:
        """
        Test latency for a specific action.
        
        Args:
            action: The input action to test
            num_samples: Number of samples to collect
            
        Returns:
            List of latency measurements in milliseconds
        """
        latencies = []
        print(f"\nTesting {action.value} - Press the button {num_samples} times")
        print("Press Ctrl+C to skip this action")
        
        for i in range(num_samples):
            try:
                # Wait for button press
                press_detected = False
                start_time = None
                
                while not press_detected:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            return latencies
                        
                        if self.mode == InputMode.KEYBOARD and event.type == pygame.KEYDOWN:
                            # Record the time the event was generated
                            start_time = time.time()
                            detected_action = self.input_manager.get_action(event)
                            
                            if detected_action == action:
                                # Measure processing time
                                end_time = time.time()
                                latency = (end_time - start_time) * 1000  # Convert to ms
                                latencies.append(latency)
                                press_detected = True
                                print(f"  Sample {i+1}/{num_samples}: {latency:.2f}ms")
                                break
                    
                    # For GPIO mode, check button state directly
                    if self.mode == InputMode.GPIO:
                        start_time = time.time()
                        if self.input_manager.is_pressed(action):
                            end_time = time.time()
                            latency = (end_time - start_time) * 1000
                            latencies.append(latency)
                            press_detected = True
                            print(f"  Sample {i+1}/{num_samples}: {latency:.2f}ms")
                            
                            # Wait for button release
                            while self.input_manager.is_pressed(action):
                                time.sleep(0.01)
                    
                    self.clock.tick(60)  # Limit to 60 FPS
                
                # Small delay between samples
                time.sleep(0.2)
                
            except KeyboardInterrupt:
                print("\nSkipping this action...")
                break
        
        return latencies
    
    def test_all_actions(self, num_samples: int = 10):
        """
        Test latency for all input actions.
        
        Args:
            num_samples: Number of samples per action
        """
        actions_to_test = [
            InputAction.UP,
            InputAction.DOWN,
            InputAction.LEFT,
            InputAction.RIGHT,
            InputAction.SELECT,
            InputAction.BACK,
        ]
        
        print("=" * 60)
        print("Input Latency Testing")
        print(f"Mode: {self.mode.value}")
        print(f"Samples per action: {num_samples}")
        print("=" * 60)
        
        for action in actions_to_test:
            latencies = self.test_action(action, num_samples)
            if latencies:
                self.latencies[action] = latencies
    
    def generate_report(self) -> str:
        """
        Generate a report of latency measurements.
        
        Returns:
            Formatted report string
        """
        report = []
        report.append("\n" + "=" * 60)
        report.append("LATENCY TEST REPORT")
        report.append("=" * 60)
        report.append(f"Input Mode: {self.mode.value}")
        report.append("")
        
        if not self.latencies:
            report.append("No data collected.")
            return "\n".join(report)
        
        # Per-action statistics
        report.append("Per-Action Latency Statistics:")
        report.append("-" * 60)
        
        all_latencies = []
        for action, latencies in sorted(self.latencies.items(), key=lambda x: x[0].value):
            if latencies:
                avg = mean(latencies)
                min_lat = min(latencies)
                max_lat = max(latencies)
                std = stdev(latencies) if len(latencies) > 1 else 0.0
                
                report.append(f"{action.value.upper():10s}: "
                            f"avg={avg:6.2f}ms  "
                            f"min={min_lat:6.2f}ms  "
                            f"max={max_lat:6.2f}ms  "
                            f"std={std:6.2f}ms  "
                            f"n={len(latencies)}")
                
                all_latencies.extend(latencies)
        
        # Overall statistics
        if all_latencies:
            report.append("")
            report.append("Overall Statistics:")
            report.append("-" * 60)
            avg = mean(all_latencies)
            min_lat = min(all_latencies)
            max_lat = max(all_latencies)
            std = stdev(all_latencies)
            
            report.append(f"Average Latency: {avg:.2f}ms")
            report.append(f"Min Latency: {min_lat:.2f}ms")
            report.append(f"Max Latency: {max_lat:.2f}ms")
            report.append(f"Std Deviation: {std:.2f}ms")
            report.append(f"Total Samples: {len(all_latencies)}")
            
            # Performance assessment
            report.append("")
            report.append("Performance Assessment:")
            report.append("-" * 60)
            
            if avg < 16.67:  # 60 FPS
                report.append("✓ EXCELLENT: Latency is well below 16.67ms (60 FPS target)")
            elif avg < 33.33:  # 30 FPS
                report.append("✓ GOOD: Latency is below 33.33ms (30 FPS target)")
            elif avg < 50:
                report.append("⚠ ACCEPTABLE: Latency is noticeable but usable")
            else:
                report.append("✗ POOR: Latency is too high, optimization needed")
            
            if max_lat > 50:
                report.append("⚠ WARNING: Some button presses exceeded 50ms latency")
            
            if std > 10:
                report.append("⚠ WARNING: High variance in latency detected")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def cleanup(self):
        """Clean up resources."""
        self.input_manager.cleanup()
        pygame.quit()


def main():
    """Main entry point."""
    print("ShokeDex Input Latency Tester")
    print("=" * 60)
    print()
    print("This tool measures button input latency for optimization.")
    print()
    
    # Determine input mode
    mode = InputMode.KEYBOARD
    if len(sys.argv) > 1 and sys.argv[1].lower() == "gpio":
        mode = InputMode.GPIO
        print("Testing GPIO mode (hardware buttons)")
    else:
        print("Testing KEYBOARD mode (use arrow keys and Enter)")
        print("To test GPIO mode, run: python tools/test_input_latency.py gpio")
    
    print()
    
    # Number of samples
    num_samples = 10
    if len(sys.argv) > 2:
        try:
            num_samples = int(sys.argv[2])
        except ValueError:
            print(f"Invalid sample count: {sys.argv[2]}, using default: {num_samples}")
    
    # Run test
    tester = InputLatencyTester(mode=mode)
    
    try:
        tester.test_all_actions(num_samples=num_samples)
        
        # Generate and print report
        report = tester.generate_report()
        print(report)
        
        # Save report to file
        output_dir = Path(__file__).parent.parent / "data"
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"latency_test_{mode.value}_{int(time.time())}.txt"
        
        with open(output_file, "w") as f:
            f.write(report)
        
        print(f"\nReport saved to: {output_file}")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    finally:
        tester.cleanup()


if __name__ == "__main__":
    main()
