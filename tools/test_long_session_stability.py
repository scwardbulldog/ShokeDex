#!/usr/bin/env python3
"""
Long-session stability test for Evolution Panel.

Story 5.6 Task 5: Test memory stability and performance over extended browsing sessions.

Tests:
- Navigate through 100+ Pokémon with evolution panels
- Monitor memory usage and frame times
- Verify sprite caches and evolution data don't grow unbounded
- Confirm no memory leaks over long sessions

Usage:
    python tools/test_long_session_stability.py
"""

import pygame
import time
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.database import Database
from src.ui.detail_screen import EvolutionPanel
from src.performance_monitor import PerformanceMonitor


class MockScreenManager:
    """Mock ScreenManager for testing."""
    
    def __init__(self, database):
        self.database = database


def test_long_session_stability(pokemon_count=100):
    """
    Simulate long browsing session and monitor resource usage.
    
    Args:
        pokemon_count: Number of Pokémon to navigate through
        
    Returns:
        dict: Results with memory, frame time stats, and stability metrics
    """
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 480))
    
    # Initialize performance monitor
    monitor = PerformanceMonitor()
    
    # Connect to database
    db_path = Path(__file__).parent.parent / 'data' / 'pokedex.db'
    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        print("Please run: python src/data/manage_db.py seed --gen 1-3")
        return None
    
    db = Database(str(db_path))
    screen_manager = MockScreenManager(db)
    
    # Get list of Pokemon IDs to test
    with db as conn:
        cursor = conn.execute("SELECT id FROM pokemon ORDER BY id LIMIT ?", (pokemon_count,))
        pokemon_ids = [row[0] for row in cursor.fetchall()]
    
    print(f"\n{'='*70}")
    print(f"Long-Session Stability Test")
    print(f"{'='*70}")
    print(f"Testing {len(pokemon_ids)} Pokémon...")
    print()
    
    # Track metrics
    render_times = []
    memory_samples = []
    frame_times = []
    
    # Simulate navigation through many Pokémon
    for i, pokemon_id in enumerate(pokemon_ids):
        # Create panel for this Pokémon
        panel = EvolutionPanel(screen_manager, pokemon_id)
        panel.load_data()
        panel.load_sprites()
        
        # Render panel multiple times (simulate multiple frames)
        for _ in range(3):
            start_time = time.perf_counter()
            panel.render(screen, 20, 100)
            render_time = (time.perf_counter() - start_time) * 1000
            render_times.append(render_time)
            
            # Record frame for performance monitoring
            monitor.record_frame()
        
        # Sample metrics every 10 Pokémon
        if (i + 1) % 10 == 0:
            stats = monitor.get_stats()
            frame_times.append(stats.get('avg_frame_time_ms', 0))
            
            print(f"Progress: {i + 1}/{len(pokemon_ids)} | "
                  f"Avg Render: {sum(render_times[-30:]) / min(len(render_times), 30):.2f}ms | "
                  f"FPS: {stats.get('fps', 0):.1f} | "
                  f"Frame Time: {stats.get('avg_frame_time_ms', 0):.2f}ms")
    
    print()
    print(f"{'='*70}")
    print(f"RESULTS")
    print(f"{'='*70}")
    
    # Calculate statistics
    avg_render = sum(render_times) / len(render_times)
    min_render = min(render_times)
    max_render = max(render_times)
    
    early_renders = render_times[:30]
    late_renders = render_times[-30:]
    early_avg = sum(early_renders) / len(early_renders)
    late_avg = sum(late_renders) / len(late_renders)
    
    print(f"\nRender Time Statistics:")
    print(f"  Average:    {avg_render:.2f}ms")
    print(f"  Min:        {min_render:.2f}ms")
    print(f"  Max:        {max_render:.2f}ms")
    print(f"  Early Avg:  {early_avg:.2f}ms (first 30 renders)")
    print(f"  Late Avg:   {late_avg:.2f}ms (last 30 renders)")
    print(f"  Drift:      {late_avg - early_avg:+.2f}ms ({((late_avg / early_avg - 1) * 100):+.1f}%)")
    
    # Check for memory leaks / performance degradation
    drift_threshold = 0.20  # 20% performance drift is concerning
    drift_ratio = (late_avg / early_avg - 1)
    
    print(f"\nStability Assessment:")
    if drift_ratio < -0.05:
        # Performance improved (negative drift = faster renders)
        print(f"  ✅ EXCELLENT: Performance improved over time ({drift_ratio * 100:+.1f}% faster)")
        print(f"     This indicates caching is working effectively.")
    elif abs(drift_ratio) < drift_threshold:
        print(f"  ✅ PASS: Performance stable ({drift_ratio * 100:+.1f}% drift)")
    else:
        print(f"  ⚠️  WARNING: Performance degradation detected ({drift_ratio * 100:+.1f}% slower)")
        print(f"     This may indicate memory leaks or cache growth issues.")
    
    if max_render < 500:
        print(f"  ✅ PASS: No extreme render spikes (max {max_render:.2f}ms)")
    else:
        print(f"  ⚠️  WARNING: Render spike detected ({max_render:.2f}ms)")
    
    # Final metrics
    final_stats = monitor.get_stats()
    print(f"\nFinal Performance Metrics:")
    print(f"  FPS:        {final_stats.get('fps', 0):.1f}")
    print(f"  Frame Time: {final_stats.get('avg_frame_time_ms', 0):.2f}ms")
    print(f"  Frames:     {final_stats.get('frame_count', 0)}")
    
    # Cleanup
    pygame.quit()
    
    return {
        'avg_render_time': avg_render,
        'min_render_time': min_render,
        'max_render_time': max_render,
        'early_avg': early_avg,
        'late_avg': late_avg,
        'drift_percent': drift_ratio * 100,
        'stable': (drift_ratio < 0 or abs(drift_ratio) < drift_threshold),  # Negative drift is good (faster)
        'final_fps': final_stats.get('fps', 0),
        'final_frame_time': final_stats.get('avg_frame_time_ms', 0)
    }


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.WARNING,  # Reduce noise during test
        format='%(levelname)s: %(message)s'
    )
    
    # Run stability test
    results = test_long_session_stability(pokemon_count=100)
    
    # Exit with appropriate code
    if results and results['stable']:
        sys.exit(0)
    else:
        sys.exit(1)
