#!/usr/bin/env python3
"""
Performance test for dirty rectangle rendering optimization.

Demonstrates and measures the performance improvement from dirty rect updates
versus full screen flips.
"""

import os
import sys
import time
import pygame

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ui.dirty_rect_manager import DirtyRectManager


def test_full_screen_update(screen_size=(480, 320), iterations=100):
    """Test performance with full screen flip."""
    pygame.init()
    screen = pygame.display.set_mode(screen_size)
    
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        
        # Simulated rendering
        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, (255, 0, 0), (100, 100, 50, 50))
        
        # Full flip
        pygame.display.flip()
        
        times.append((time.perf_counter() - start) * 1000)
    
    pygame.quit()
    return times


def test_dirty_rect_update(screen_size=(480, 320), iterations=100):
    """Test performance with dirty rectangle updates."""
    pygame.init()
    screen = pygame.display.set_mode(screen_size)
    dirty_manager = DirtyRectManager()
    
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        
        # Simulated rendering - only update small region
        rect = pygame.Rect(100, 100, 50, 50)
        pygame.draw.rect(screen, (255, 0, 0), rect)
        
        # Dirty rect update
        dirty_manager.mark_dirty(rect)
        dirty_manager.update_display()
        
        times.append((time.perf_counter() - start) * 1000)
    
    pygame.quit()
    return times


def calculate_stats(times):
    """Calculate statistics from timing data."""
    avg = sum(times) / len(times)
    sorted_times = sorted(times)
    p50 = sorted_times[len(times) // 2]
    p95 = sorted_times[int(len(times) * 0.95)]
    p99 = sorted_times[int(len(times) * 0.99)]
    
    return {
        'avg': avg,
        'p50': p50,
        'p95': p95,
        'p99': p99,
        'min': min(times),
        'max': max(times)
    }


def main():
    """Run performance comparison."""
    print("=" * 70)
    print("Dirty Rectangle Rendering Performance Test")
    print("=" * 70)
    print()
    
    # Set headless mode for CI
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    
    iterations = 100
    
    # Test full screen updates
    print(f"Testing full screen flip ({iterations} iterations)...")
    full_times = test_full_screen_update(iterations=iterations)
    full_stats = calculate_stats(full_times)
    
    print(f"  Average:  {full_stats['avg']:.3f} ms")
    print(f"  Median:   {full_stats['p50']:.3f} ms")
    print(f"  P95:      {full_stats['p95']:.3f} ms")
    print(f"  P99:      {full_stats['p99']:.3f} ms")
    print(f"  Min:      {full_stats['min']:.3f} ms")
    print(f"  Max:      {full_stats['max']:.3f} ms")
    print()
    
    # Test dirty rect updates
    print(f"Testing dirty rectangle update ({iterations} iterations)...")
    dirty_times = test_dirty_rect_update(iterations=iterations)
    dirty_stats = calculate_stats(dirty_times)
    
    print(f"  Average:  {dirty_stats['avg']:.3f} ms")
    print(f"  Median:   {dirty_stats['p50']:.3f} ms")
    print(f"  P95:      {dirty_stats['p95']:.3f} ms")
    print(f"  P99:      {dirty_stats['p99']:.3f} ms")
    print(f"  Min:      {dirty_stats['min']:.3f} ms")
    print(f"  Max:      {dirty_stats['max']:.3f} ms")
    print()
    
    # Calculate improvement
    improvement_avg = ((full_stats['avg'] - dirty_stats['avg']) / full_stats['avg']) * 100
    improvement_p95 = ((full_stats['p95'] - dirty_stats['p95']) / full_stats['p95']) * 100
    
    print("=" * 70)
    print("Performance Improvement")
    print("=" * 70)
    print(f"Average:  {improvement_avg:+.1f}%")
    print(f"P95:      {improvement_p95:+.1f}%")
    print()
    
    if improvement_avg > 0:
        print(f"✅ Dirty rect optimization is {improvement_avg:.1f}% faster on average")
    else:
        print(f"⚠️  No performance improvement detected")
    
    print()
    print("Note: In dummy video mode, improvements may be minimal.")
    print("Real hardware would show greater benefits, especially at higher resolutions.")
    print()


if __name__ == '__main__':
    main()
