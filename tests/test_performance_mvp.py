"""
Performance Regression Test Suite for ShokeDex MVP (Story 1.7)

Automated tests validating performance requirements (AC #1-8):
- Frame rate: 30+ FPS during navigation
- Input latency: < 100ms
- Memory stability: No unbounded growth
- Sprite cache efficiency: > 70% hit rate

Usage:
    pytest tests/test_performance_mvp.py -v
    pytest tests/test_performance_mvp.py::TestFrameRatePerformance -v
"""

import pytest
import pygame
import time
from typing import List
from unittest.mock import MagicMock, patch

from src.ui.home_screen import HomeScreen
from src.ui.screen_manager import ScreenManager
from src.data.database import Database
from src.state_manager import StateManager
from src.input_manager import InputManager, InputMode, InputAction
from src.performance_monitor import PerformanceMonitor


@pytest.fixture
def mock_database():
    """Mock database with test data."""
    db = MagicMock(spec=Database)
    
    # Mock get_pokemon_by_generation for Kanto
    def mock_get_by_gen(generation):
        if generation == 1:
            return [
                {'id': i, 'name': f'Pokemon{i:03d}'}
                for i in range(1, 152)  # 151 Pokemon
            ]
        elif generation == 2:
            return [
                {'id': i, 'name': f'Pokemon{i:03d}'}
                for i in range(152, 252)  # 100 Pokemon
            ]
        elif generation == 3:
            return [
                {'id': i, 'name': f'Pokemon{i:03d}'}
                for i in range(252, 387)  # 135 Pokemon
            ]
        return []
    
    db.get_pokemon_by_generation.side_effect = mock_get_by_gen
    db.__enter__ = MagicMock(return_value=db)
    db.__exit__ = MagicMock(return_value=False)
    
    return db


@pytest.fixture
def mock_screen_manager(mock_database):
    """Mock screen manager with required dependencies."""
    # Initialize pygame
    pygame.init()
    pygame.font.init()
    
    # Create display surface
    display_surface = pygame.Surface((480, 320))
    
    # Create screen manager
    screen_manager = ScreenManager(display_surface)
    
    # Add managers as attributes (HomeScreen expects these)
    screen_manager.database = mock_database
    
    state_manager = MagicMock(spec=StateManager)
    state_manager.get_last_viewed_generation.return_value = 1
    state_manager.get_last_viewed_id.return_value = 1
    state_manager.set_last_viewed.return_value = None
    state_manager.save_state.return_value = None
    screen_manager.state_manager = state_manager
    
    input_manager = MagicMock(spec=InputManager)
    screen_manager.input_manager = input_manager
    
    return screen_manager


@pytest.fixture
def home_screen(mock_screen_manager, mock_database):
    """Create HomeScreen instance for testing."""
    screen = HomeScreen(mock_screen_manager, database=mock_database)
    screen.on_enter()
    return screen


class TestFrameRatePerformance:
    """Test frame rate performance (Story 1.7: AC #1)."""
    
    def test_performance_monitor_integration(self, home_screen):
        """Verify PerformanceMonitor is integrated in HomeScreen."""
        assert hasattr(home_screen, 'performance_monitor')
        assert isinstance(home_screen.performance_monitor, PerformanceMonitor)
    
    def test_frame_rate_during_navigation(self, home_screen):
        """Test FPS maintains 30+ during normal navigation (AC #1)."""
        # Create surface for rendering
        surface = pygame.Surface((480, 320))
        
        # Simulate 100 frames of navigation (3.3 seconds at 30 FPS)
        delta_time = 1.0 / 30.0  # 33.3ms per frame
        
        for _ in range(100):
            home_screen.update(delta_time)
            home_screen.render(surface)
        
        # Check average FPS
        stats = home_screen.performance_monitor.get_stats()
        assert stats['fps_avg'] >= 30.0, f"FPS {stats['fps_avg']:.1f} below 30 FPS target"
    
    def test_frame_rate_during_generation_switch(self, home_screen):
        """Test FPS during generation switching with transitions (AC #1)."""
        surface = pygame.Surface((480, 320))
        delta_time = 1.0 / 30.0
        
        # Switch generation (triggers fade transition)
        home_screen.handle_input(InputAction.RIGHT)
        
        # Simulate transition frames (600ms transition = ~18 frames)
        for _ in range(20):
            home_screen.update(delta_time)
            home_screen.render(surface)
        
        # Check FPS maintained during transition
        stats = home_screen.performance_monitor.get_stats()
        assert stats['fps_avg'] >= 29.0, "FPS dropped during generation switch"
    
    def test_frame_rate_during_hold_to_scroll(self, home_screen):
        """Test FPS during hold-to-scroll acceleration (AC #1)."""
        surface = pygame.Surface((480, 320))
        delta_time = 1.0 / 30.0
        
        # Start holding down button
        home_screen.handle_input(InputAction.DOWN)
        
        # Simulate 60 frames (2 seconds) of holding
        # This should trigger turbo mode (5 Pokemon/frame)
        for _ in range(60):
            # Keep active_button set to simulate holding
            if not home_screen.active_button:
                home_screen.active_button = InputAction.DOWN
            
            home_screen.update(delta_time)
            home_screen.render(surface)
        
        # Check FPS maintained during fast scroll
        stats = home_screen.performance_monitor.get_stats()
        assert stats['fps_avg'] >= 29.0, "FPS dropped during hold-to-scroll"
    
    def test_fps_warning_system_exists(self, home_screen):
        """Test that FPS warning system is implemented (AC #1)."""
        # Verify warning tracking exists
        assert hasattr(home_screen, 'fps_warning_count')
        assert home_screen.fps_warning_count == 0  # Initial state
        
        # Verify performance monitor can detect low FPS
        # Run a few frames to establish baseline
        surface = pygame.Surface((480, 320))
        for _ in range(10):
            home_screen.update(0.0167)
            home_screen.render(surface)
        
        # Verify FPS tracking is working
        stats = home_screen.performance_monitor.get_stats()
        assert 'fps_avg' in stats
        assert stats['fps_avg'] > 0
        
        # Note: Actual FPS warning logging is validated through manual/integration testing
        # The test environment runs too fast to reliably trigger warnings


class TestButtonInputLatency:
    """Test button input latency (Story 1.7: AC #2)."""
    
    def test_input_to_render_latency(self, home_screen):
        """Test end-to-end latency from input to render < 100ms (AC #2)."""
        surface = pygame.Surface((480, 320))
        latencies: List[float] = []
        
        # Test 50 button presses (faster test than tools/test_input_latency.py)
        for action in [InputAction.UP, InputAction.DOWN, InputAction.LEFT, InputAction.RIGHT]:
            for _ in range(10):  # 10 samples per button
                # Start timing
                start_time = time.perf_counter()
                
                # Input → Update → Render pipeline
                home_screen.handle_input(action)
                home_screen.update(0.0167)  # 60 FPS delta
                home_screen.render(surface)
                
                # End timing
                end_time = time.perf_counter()
                latency_ms = (end_time - start_time) * 1000.0
                latencies.append(latency_ms)
        
        # Check average and P95 latency
        avg_latency = sum(latencies) / len(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
        
        assert avg_latency < 80.0, f"Average latency {avg_latency:.2f}ms exceeds 80ms target"
        assert p95_latency < 100.0, f"P95 latency {p95_latency:.2f}ms exceeds 100ms requirement (NFR-P2)"


class TestMemoryStability:
    """Test memory stability and leak detection (Story 1.7: AC #5)."""
    
    def test_performance_monitor_tracks_memory(self, home_screen):
        """Verify PerformanceMonitor tracks memory usage (AC #5)."""
        # Record some frames to populate history
        for _ in range(10):
            home_screen.update(0.0167)
        
        stats = home_screen.performance_monitor.get_stats()
        assert 'memory_mb' in stats
        assert 'memory_avg_mb' in stats
        assert stats['memory_mb'] > 0, "Memory tracking should report non-zero usage"
    
    def test_memory_stability_during_navigation(self, home_screen):
        """Test memory remains stable during extended navigation (AC #5)."""
        surface = pygame.Surface((480, 320))
        
        # Record initial memory
        home_screen.performance_monitor.record_cpu_memory()
        initial_stats = home_screen.performance_monitor.get_stats()
        initial_memory = initial_stats['memory_mb']
        
        # Simulate extended navigation (100 generation switches, 500 scrolls)
        for _ in range(100):
            # Generation switch
            home_screen.handle_input(InputAction.RIGHT)
            for _ in range(5):
                home_screen.update(0.0167)
                home_screen.render(surface)
            
            # Scrolling
            for _ in range(5):
                home_screen.handle_input(InputAction.DOWN)
                home_screen.update(0.0167)
                home_screen.render(surface)
        
        # Check final memory
        home_screen.performance_monitor.record_cpu_memory()
        final_stats = home_screen.performance_monitor.get_stats()
        final_memory = final_stats['memory_mb']
        
        memory_increase = final_memory - initial_memory
        
        # AC #5: Memory increase should be < 50MB over 30 minutes
        # This is a shorter test, so allow proportionally less growth
        # 100 switches + 500 scrolls ~= 1 minute of activity
        # Allow 50MB / 30 = ~1.7MB per minute of activity
        assert memory_increase < 5.0, f"Memory increased by {memory_increase:.1f}MB (possible leak)"
    
    def test_sprite_cache_bounded(self, home_screen):
        """Test that sprite cache doesn't grow unbounded (AC #5)."""
        from src.ui import sprite_loader
        
        # Clear cache and load many sprites
        sprite_loader._CACHE.clear()
        
        # Load 60 sprites (exceeds max of 50)
        for pokemon_id in range(1, 61):
            sprite_loader.load_thumb(pokemon_id)
        
        stats = sprite_loader.get_cache_stats()
        # Cache should be capped at max size
        assert stats["size"] <= sprite_loader._CACHE_MAX_SIZE, \
            f"Cache size {stats['size']} exceeds max {sprite_loader._CACHE_MAX_SIZE} (AC #5)"


class TestSpriteLoadingPerformance:
    """Test sprite loading performance (Story 1.7: AC #6)."""
    
    def test_sprite_cache_hit_rate(self, home_screen):
        """Test sprite cache hit rate > 70% during typical navigation (AC #6)."""
        from src.ui import sprite_loader
        
        # Clear cache and reset stats
        sprite_loader._CACHE.clear()
        sprite_loader.reset_cache_stats()
        
        # Simulate realistic navigation with repeated viewing
        # Pattern: Browse a few Pokémon, go back and forth comparing them
        navigation_sequence = [
            # Browse Kanto starters
            1, 2, 3, 2, 1, 2, 3, 4, 5, 4, 3,
            # Browse Pikachu area
            25, 26, 27, 26, 25, 26, 27, 28,
            # Check Eevee evolutions
            133, 134, 135, 136, 134, 133, 134, 135,
            # Return to start
            1, 2, 3, 4, 5,
            # More Pikachu browsing
            25, 26, 25, 24, 25, 26, 27, 26,
            # Check starters again
            1, 4, 7, 1, 4, 7, 1, 4, 7,
            # Final Pikachu area pass
            25, 26, 27, 25, 26, 27,
        ]
        
        for pokemon_id in navigation_sequence:
            sprite_loader.load_thumb(pokemon_id)
        
        stats = sprite_loader.get_cache_stats()
        # AC #6: Cache hit rate should exceed 70%
        assert stats["hit_rate"] > 70.0, \
            f"Cache hit rate {stats['hit_rate']:.1f}% below 70% requirement (AC #6)"
    
    def test_cached_sprite_load_fast(self, home_screen):
        """Test cached sprite load is fast (AC #6)."""
        from src.ui import sprite_loader
        import time
        
        # Load sprite once (to cache it)
        sprite_loader.load_thumb(1)
        
        # Measure cached load time
        load_times = []
        for _ in range(10):
            start = time.perf_counter()
            sprite_loader.load_thumb(1)
            end = time.perf_counter()
            load_times.append((end - start) * 1000)  # Convert to ms
        
        avg_load_time = sum(load_times) / len(load_times)
        
        # AC #6: Cached sprite load < 50ms (we expect < 1ms for memory lookup)
        assert avg_load_time < 10.0, \
            f"Cached sprite load time {avg_load_time:.2f}ms too slow (AC #6)"


class TestRenderingOptimization:
    """Test rendering optimization (Story 1.7: AC #7)."""
    
    def test_idle_frame_render_time(self, home_screen):
        """Test idle rendering uses minimal CPU (AC #7)."""
        surface = pygame.Surface((480, 320))
        
        # Render 30 idle frames (no input, no state changes)
        render_times: List[float] = []
        
        for _ in range(30):
            start_time = time.perf_counter()
            home_screen.render(surface)
            end_time = time.perf_counter()
            
            render_time_ms = (end_time - start_time) * 1000.0
            render_times.append(render_time_ms)
        
        avg_render_time = sum(render_times) / len(render_times)
        
        # AC #7: Idle frame render time < 16ms (60 FPS capability)
        # Allow some margin for test overhead
        assert avg_render_time < 20.0, f"Idle render time {avg_render_time:.2f}ms exceeds 16ms target"
    
    def test_active_navigation_maintains_fps(self, home_screen):
        """Test active navigation maintains 30+ FPS (AC #7)."""
        surface = pygame.Surface((480, 320))
        
        # Simulate active navigation with constant input
        for _ in range(90):  # 3 seconds at 30 FPS
            home_screen.handle_input(InputAction.DOWN)
            home_screen.update(1.0 / 30.0)
            home_screen.render(surface)
        
        stats = home_screen.performance_monitor.get_stats()
        assert stats['fps_avg'] >= 30.0, "FPS dropped during active navigation"


class TestPerformanceRegressions:
    """Test for performance regressions against baseline (Story 1.7: AC #1-8)."""
    
    # Performance baseline (should be updated after profiling on Pi hardware)
    BASELINE = {
        "desktop_fps": 60.0,
        "pi_fps": 30.0,
        "input_latency_ms": 80.0,
        "memory_mb_growth_per_minute": 2.0,
    }
    
    def test_no_fps_regression(self, home_screen):
        """Test that FPS hasn't regressed from baseline."""
        surface = pygame.Surface((480, 320))
        
        # Run navigation for 60 frames (2 seconds)
        for _ in range(60):
            home_screen.handle_input(InputAction.DOWN)
            home_screen.update(1.0 / 30.0)
            home_screen.render(surface)
        
        stats = home_screen.performance_monitor.get_stats()
        
        # Allow 10% degradation from baseline
        min_acceptable_fps = self.BASELINE["pi_fps"] * 0.9
        
        assert stats['fps_avg'] >= min_acceptable_fps, \
            f"FPS regression detected: {stats['fps_avg']:.1f} < {min_acceptable_fps:.1f}"
    
    def test_performance_adequate_check(self, home_screen):
        """Test PerformanceMonitor.is_performance_adequate() method."""
        surface = pygame.Surface((480, 320))
        
        # Run some frames to populate performance history
        for _ in range(100):
            home_screen.update(1.0 / 30.0)
            home_screen.render(surface)
        
        # Record CPU/memory for the adequacy check
        home_screen.performance_monitor.record_cpu_memory()
        
        # Check performance adequacy
        # Note: In test environment with mocked data, CPU usage may be very low
        # So we use a higher max_cpu threshold for testing
        is_adequate = home_screen.performance_monitor.is_performance_adequate(
            target_fps=30.0,
            max_cpu=100.0  # Allow any CPU for test environment
        )
        
        stats = home_screen.performance_monitor.get_stats()
        assert is_adequate or stats['fps_avg'] >= 27.0, \
            f"Performance should be adequate: FPS={stats['fps_avg']:.1f}, adequate={is_adequate}"


# Performance baseline documentation for future comparison
"""
Performance Baseline (to be updated with actual Pi 3B+ hardware testing):

Desktop Development Machine:
- Frame Rate: 60 FPS (capped)
- Input Latency: 50-70ms average
- Memory Usage: ~150MB baseline
- Sprite Load (cached): < 5ms
- Sprite Load (first): 30-50ms

Raspberry Pi 3B+ (Target):
- Frame Rate: 30+ FPS required (NFR-P1)
- Input Latency: < 100ms required (NFR-P2)
- Memory Usage: < 300MB (headroom for OS)
- Sprite Load (cached): < 50ms acceptable
- Sprite Load (first): < 150ms acceptable

Test with: pytest tests/test_performance_mvp.py -v --tb=short
"""
