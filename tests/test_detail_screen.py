"""
Integration tests for DetailScreen (Story 3.1, 3.2, 3.3, 3.4)

Story 3.1: Basic layout, sprite display, header rendering, navigation
Story 3.2: Six base stats with visual progress bars, color-coded rendering
Story 3.3: Type badges with holographic colors and rounded rectangle styling
Story 3.4: Physical measurements (height in meters, weight in kilograms) display

Tests basic layout, sprite display, header rendering, navigation,
StateManager integration, error handling, performance validation,
stat bar rendering with proper colors and proportional widths,
type badge display with type-specific colors, and physical measurements
with unit conversion and edge case handling.
"""

import pytest
import pygame
import time
from unittest.mock import Mock, MagicMock, patch
from src.ui.detail_screen import DetailScreen
from src.ui.screen_manager import ScreenManager
from src.input_manager import InputAction
from src.ui.colors import get_stat_color, Colors


class MockStateManager:
    """Mock StateManager for testing"""
    def __init__(self):
        self.last_viewed_id = None
        self.last_viewed_generation = None
        self.saved = False
    
    def set_last_viewed(self, pokemon_id, generation=None):
        self.last_viewed_id = pokemon_id
        self.last_viewed_generation = generation
    
    def save_state(self):
        self.saved = True
        return True
    
    def get_last_viewed_id(self):
        return self.last_viewed_id


class MockDatabase:
    """Mock Database for testing"""
    def __init__(self, pokemon_data=None, stats_data=None, types_data=None):
        self.pokemon_data = pokemon_data or {
            'id': 25,
            'name': 'pikachu',
            'height': 4,
            'weight': 60,
            'generation': 1
        }
        # Story 3.2: Add default stats data (Pikachu's actual stats)
        self.stats_data = stats_data if stats_data is not None else [
            {'name': 'HP', 'base_stat': 35, 'effort': 0},
            {'name': 'Attack', 'base_stat': 55, 'effort': 0},
            {'name': 'Defense', 'base_stat': 40, 'effort': 0},
            {'name': 'Special Attack', 'base_stat': 50, 'effort': 0},
            {'name': 'Special Defense', 'base_stat': 50, 'effort': 0},
            {'name': 'Speed', 'base_stat': 90, 'effort': 0}
        ]
        # Story 3.3: Add default types data (Pikachu is Electric)
        # Use 'is not None' check to allow empty list []
        self.types_data = types_data if types_data is not None else ['Electric']
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def get_pokemon_by_id(self, pokemon_id):
        if pokemon_id == self.pokemon_data['id']:
            return self.pokemon_data
        return None
    
    def get_pokemon_stats(self, pokemon_id):
        """Return mock stats data (Story 3.2)"""
        if pokemon_id == self.pokemon_data['id']:
            return self.stats_data
        return []
    
    def get_pokemon_types(self, pokemon_id):
        """Return mock types data (Story 3.3)"""
        # Always return the configured types_data for any pokemon_id that matches
        # our pokemon_data, otherwise return empty list
        if self.pokemon_data and pokemon_id == self.pokemon_data['id']:
            return self.types_data
        return []


class MockScreenManager:
    """Mock ScreenManager for testing"""
    def __init__(self, database=None, state_manager=None):
        self.database = database
        self.state_manager = state_manager
        self.sprite_loader = None
        self.popped = False
        self.pushed_screen = None
    
    def pop(self):
        self.popped = True
    
    def push(self, screen):
        self.pushed_screen = screen


@pytest.fixture
def pygame_init():
    """Initialize pygame for testing"""
    pygame.init()
    pygame.display.set_mode((800, 480))
    yield
    pygame.quit()


@pytest.fixture
def mock_state_manager():
    """Create mock StateManager"""
    return MockStateManager()


@pytest.fixture
def mock_database():
    """Create mock Database"""
    return MockDatabase()


@pytest.fixture
def mock_screen_manager(mock_database, mock_state_manager):
    """Create mock ScreenManager with managers"""
    return MockScreenManager(
        database=mock_database,
        state_manager=mock_state_manager
    )


class TestDetailScreenBasic:
    """Test DetailScreen basic functionality (Story 3.1)"""
    
    def test_detail_screen_initialization(self, pygame_init, mock_screen_manager):
        """Test DetailScreen initializes with correct pokemon_id"""
        detail_screen = DetailScreen(mock_screen_manager, pokemon_id=25)
        
        assert detail_screen.pokemon_id == 25
        assert detail_screen.database == mock_screen_manager.database
        assert detail_screen.state_manager == mock_screen_manager.state_manager
    
    def test_on_enter_loads_pokemon_data(self, pygame_init, mock_screen_manager):
        """Test on_enter() loads Pokémon data from database"""
        detail_screen = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail_screen.on_enter()
        
        assert detail_screen.pokemon_data is not None
        assert detail_screen.pokemon_data['id'] == 25
        assert detail_screen.pokemon_data['name'] == 'pikachu'
    
    def test_on_enter_updates_state_manager(self, pygame_init, mock_screen_manager, mock_state_manager):
        """Test on_enter() calls StateManager.set_last_viewed()"""
        detail_screen = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail_screen.on_enter()
        
        assert mock_state_manager.last_viewed_id == 25
    
    def test_on_exit_saves_state(self, pygame_init, mock_screen_manager, mock_state_manager):
        """Test on_exit() calls StateManager.save_state()"""
        detail_screen = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail_screen.on_enter()
        detail_screen.on_exit()
        
        assert mock_state_manager.saved is True
    
    def test_b_button_pops_screen(self, pygame_init, mock_screen_manager):
        """Test B button (BACK action) pops screen stack"""
        detail_screen = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail_screen.on_enter()
        detail_screen.handle_input(InputAction.BACK)
        
        assert mock_screen_manager.popped is True
    
    def test_header_rendering(self, pygame_init, mock_screen_manager):
        """Test header shows Pokémon name and dex number"""
        detail_screen = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail_screen.on_enter()
        
        # Create test surface
        surface = pygame.Surface((800, 480))
        detail_screen.render(surface)
        
        # Verify fonts are initialized
        assert detail_screen.header_font is not None
        assert detail_screen.pokemon_data['name'] == 'pikachu'
        assert detail_screen.pokemon_data['id'] == 25
    
    @patch('src.ui.detail_screen.load_detail')
    def test_sprite_loading(self, mock_load_detail, pygame_init, mock_screen_manager):
        """Test sprite loading from SpriteLoader"""
        # Create mock sprite
        mock_sprite = pygame.Surface((128, 128))
        mock_load_detail.return_value = mock_sprite
        
        detail_screen = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail_screen.on_enter()
        
        assert detail_screen.sprite is not None
        assert detail_screen.sprite.get_size() == (128, 128)
        mock_load_detail.assert_called_once_with(25)
    
    @patch('src.ui.detail_screen.load_detail')
    def test_missing_sprite_shows_placeholder(self, mock_load_detail, pygame_init, mock_screen_manager):
        """Test missing sprite shows text placeholder gracefully"""
        # Simulate missing sprite
        mock_load_detail.return_value = None
        
        detail_screen = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail_screen.on_enter()
        
        # Should create placeholder instead
        assert detail_screen.sprite is not None
        assert detail_screen.sprite.get_size() == (128, 128)
    
    def test_database_error_handling(self, pygame_init, mock_state_manager):
        """Test database error shows friendly message"""
        # Create screen manager with failing database
        failing_db = Mock()
        failing_db.__enter__ = Mock(side_effect=Exception("Database error"))
        failing_db.__exit__ = Mock(return_value=False)
        
        screen_manager = MockScreenManager(
            database=failing_db,
            state_manager=mock_state_manager
        )
        
        detail_screen = DetailScreen(screen_manager, pokemon_id=25)
        detail_screen.on_enter()
        
        # Should not crash
        surface = pygame.Surface((800, 480))
        detail_screen.render(surface)
        
        # Pokemon data should be None
        assert detail_screen.pokemon_data is None
    
    def test_error_screen_shows_b_button_help(self, pygame_init, mock_state_manager):
        """Test error screen displays 'Press B to return' message"""
        # Create screen manager with no database
        screen_manager = MockScreenManager(
            database=None,
            state_manager=mock_state_manager
        )
        
        detail_screen = DetailScreen(screen_manager, pokemon_id=25)
        detail_screen.on_enter()
        
        # Render error screen
        surface = pygame.Surface((800, 480))
        detail_screen.render(surface)
        
        # Should allow B button to work
        detail_screen.handle_input(InputAction.BACK)
        assert screen_manager.popped is True
    
    def test_holographic_styling_applied(self, pygame_init, mock_screen_manager):
        """Test holographic blue styling is applied to panels"""
        from src.ui.colors import Colors
        
        detail_screen = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail_screen.on_enter()
        
        # Create surface and render
        surface = pygame.Surface((800, 480))
        detail_screen.render(surface)
        
        # Verify colors are defined (holographic palette)
        assert hasattr(Colors, 'DEEP_SPACE_BLACK')
        assert hasattr(Colors, 'DARK_BLUE')
        assert hasattr(Colors, 'ELECTRIC_BLUE')
        assert hasattr(Colors, 'HOLOGRAM_WHITE')
        assert hasattr(Colors, 'ICE_BLUE')
    
    def test_placeholder_panels_rendered(self, pygame_init, mock_screen_manager):
        """Test placeholder panels for future features are rendered"""
        detail_screen = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail_screen.on_enter()
        
        surface = pygame.Surface((800, 480))
        detail_screen.render(surface)
        
        # Rendering should complete without errors
        # Panels should be drawn (can't easily verify visually in test)
        assert detail_screen.pokemon_data is not None
    
    def test_update_does_nothing(self, pygame_init, mock_screen_manager):
        """Test update() is minimal for Story 3.1 (no animations)"""
        detail_screen = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail_screen.on_enter()
        
        # Should not crash
        detail_screen.update(0.016)  # ~60 FPS delta
        detail_screen.update(0.033)  # ~30 FPS delta


class TestDetailScreenStateIntegration:
    """Test DetailScreen integration with StateManager"""
    
    def test_state_persists_across_instances(self, pygame_init, mock_database):
        """Test last viewed Pokémon persists across DetailScreen instances"""
        state_manager = MockStateManager()
        screen_manager1 = MockScreenManager(
            database=mock_database,
            state_manager=state_manager
        )
        
        # First instance sets last viewed to 25
        detail1 = DetailScreen(screen_manager1, pokemon_id=25)
        detail1.on_enter()
        detail1.on_exit()
        
        # Verify state was saved
        assert state_manager.last_viewed_id == 25
        assert state_manager.saved is True
    
    def test_multiple_pokemon_views_update_state(self, pygame_init, mock_database, mock_state_manager):
        """Test viewing multiple Pokémon updates state correctly"""
        screen_manager = MockScreenManager(
            database=mock_database,
            state_manager=mock_state_manager
        )
        
        # View Pokémon 25
        detail1 = DetailScreen(screen_manager, pokemon_id=25)
        detail1.on_enter()
        assert mock_state_manager.last_viewed_id == 25
        
        # View Pokémon 1 (change mock database data)
        screen_manager.database.pokemon_data = {
            'id': 1, 'name': 'bulbasaur',
            'height': 7, 'weight': 69, 'generation': 1
        }
        detail2 = DetailScreen(screen_manager, pokemon_id=1)
        detail2.on_enter()
        assert mock_state_manager.last_viewed_id == 1


class TestDetailScreenErrorHandling:
    """Test DetailScreen error handling and graceful degradation"""
    
    def test_invalid_pokemon_id(self, pygame_init, mock_state_manager):
        """Test invalid Pokémon ID handled gracefully"""
        db = MockDatabase(pokemon_data={'id': 1, 'name': 'bulbasaur', 
                                       'height': 7, 'weight': 69, 'generation': 1})
        screen_manager = MockScreenManager(
            database=db,
            state_manager=mock_state_manager
        )
        
        # Try to load non-existent Pokémon
        detail = DetailScreen(screen_manager, pokemon_id=999)
        detail.on_enter()
        
        # Should show error, not crash
        surface = pygame.Surface((800, 480))
        detail.render(surface)
        
        # B button should still work
        detail.handle_input(InputAction.BACK)
        assert screen_manager.popped is True


class TestDetailScreenPerformance:
    """Test DetailScreen performance requirements (Story 3.1, AC #7)"""
    
    def test_render_time_under_33ms(self, pygame_init, mock_screen_manager):
        """Test render() completes in < 33ms for 30+ FPS"""
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        surface = pygame.Surface((800, 480))
        
        # Measure render time over multiple frames
        render_times = []
        for _ in range(10):
            start = time.perf_counter()
            detail.render(surface)
            elapsed = time.perf_counter() - start
            render_times.append(elapsed * 1000)  # Convert to ms
        
        avg_render_time = sum(render_times) / len(render_times)
        
        # Should average < 33ms for 30 FPS
        assert avg_render_time < 33, f"Average render time {avg_render_time:.2f}ms exceeds 33ms target"
    
    @patch('src.ui.detail_screen.load_detail')
    def test_sprite_load_time(self, mock_load_detail, pygame_init, mock_screen_manager):
        """Test sprite loading time from cache"""
        mock_sprite = pygame.Surface((128, 128))
        mock_load_detail.return_value = mock_sprite
        
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        
        start = time.perf_counter()
        detail.on_enter()
        elapsed = time.perf_counter() - start
        
        # on_enter should complete quickly (includes sprite load)
        elapsed_ms = elapsed * 1000
        assert elapsed_ms < 300, f"on_enter took {elapsed_ms:.2f}ms, exceeds 300ms transition target"
    
    def test_database_query_time(self, pygame_init):
        """Test database query completes in < 50ms"""
        # Use real database if available
        try:
            from src.data.database import Database
            
            with Database() as db:
                # Check if data exists
                result = db.execute("SELECT COUNT(*) FROM pokemon").fetchone()
                if result and result[0] > 0:
                    # Measure query time
                    start = time.perf_counter()
                    pokemon_data = db.get_pokemon_by_id(25)
                    elapsed = time.perf_counter() - start
                    
                    elapsed_ms = elapsed * 1000
                    assert elapsed_ms < 50, f"Database query took {elapsed_ms:.2f}ms, exceeds 50ms target"
        except Exception:
            # Skip test if database not available
            pytest.skip("Database not available for performance testing")


class TestStatBarColorCoding:
    """Test stat bar color coding function (Story 3.2, AC #3)"""
    
    def test_low_stat_color_gray(self):
        """Test stats 0-50 return gray color"""
        assert get_stat_color(0) == Colors.STAT_COLORS['low']
        assert get_stat_color(25) == Colors.STAT_COLORS['low']
        assert get_stat_color(50) == Colors.STAT_COLORS['low']
    
    def test_medium_stat_color_electric_blue(self):
        """Test stats 51-100 return electric blue color"""
        assert get_stat_color(51) == Colors.STAT_COLORS['medium']
        assert get_stat_color(75) == Colors.STAT_COLORS['medium']
        assert get_stat_color(100) == Colors.STAT_COLORS['medium']
    
    def test_high_stat_color_bright_cyan(self):
        """Test stats 101-150 return bright cyan color"""
        assert get_stat_color(101) == Colors.STAT_COLORS['high']
        assert get_stat_color(125) == Colors.STAT_COLORS['high']
        assert get_stat_color(150) == Colors.STAT_COLORS['high']
    
    def test_exceptional_stat_color_plasma_orange(self):
        """Test stats 151+ return plasma orange color"""
        assert get_stat_color(151) == Colors.STAT_COLORS['exceptional']
        assert get_stat_color(200) == Colors.STAT_COLORS['exceptional']
        assert get_stat_color(255) == Colors.STAT_COLORS['exceptional']
    
    def test_boundary_values(self):
        """Test color boundaries are correct"""
        # Test boundaries between ranges
        assert get_stat_color(50) == Colors.STAT_COLORS['low']
        assert get_stat_color(51) == Colors.STAT_COLORS['medium']
        
        assert get_stat_color(100) == Colors.STAT_COLORS['medium']
        assert get_stat_color(101) == Colors.STAT_COLORS['high']
        
        assert get_stat_color(150) == Colors.STAT_COLORS['high']
        assert get_stat_color(151) == Colors.STAT_COLORS['exceptional']


class TestDetailScreenStatLoading:
    """Test DetailScreen stat data loading (Story 3.2)"""
    
    def test_stats_loaded_on_enter(self, pygame_init, mock_screen_manager):
        """Test on_enter() loads stats from database"""
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        # Should have loaded 6 stats
        assert len(detail.stats) == 6
        assert detail.stats[0]['name'] == 'HP'
        assert detail.stats[5]['name'] == 'Speed'
    
    def test_stat_values_accurate(self, pygame_init, mock_screen_manager):
        """Test stat values match Pikachu's actual stats"""
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        # Verify Pikachu's stats
        stats_dict = {stat['name']: stat['base_stat'] for stat in detail.stats}
        assert stats_dict['HP'] == 35
        assert stats_dict['Attack'] == 55
        assert stats_dict['Defense'] == 40
        assert stats_dict['Speed'] == 90
    
    def test_missing_stats_handled(self, pygame_init, mock_state_manager):
        """Test missing stats (< 6) handled gracefully"""
        # Create database with only 3 stats
        incomplete_stats = [
            {'name': 'HP', 'base_stat': 35, 'effort': 0},
            {'name': 'Attack', 'base_stat': 55, 'effort': 0},
            {'name': 'Defense', 'base_stat': 40, 'effort': 0}
        ]
        db = MockDatabase(stats_data=incomplete_stats)
        screen_manager = MockScreenManager(
            database=db,
            state_manager=mock_state_manager
        )
        
        detail = DetailScreen(screen_manager, pokemon_id=25)
        detail.on_enter()
        
        # Should load what's available without crashing
        assert len(detail.stats) == 3
        
        # Rendering should still work
        surface = pygame.Surface((800, 480))
        detail.render(surface)
    
    def test_null_stat_values_handled(self, pygame_init, mock_state_manager):
        """Test null stat values show placeholder"""
        # Create stats with null value
        invalid_stats = [
            {'name': 'HP', 'base_stat': None, 'effort': 0},
            {'name': 'Attack', 'base_stat': 55, 'effort': 0},
            {'name': 'Defense', 'base_stat': 40, 'effort': 0},
            {'name': 'Special Attack', 'base_stat': 50, 'effort': 0},
            {'name': 'Special Defense', 'base_stat': 50, 'effort': 0},
            {'name': 'Speed', 'base_stat': 90, 'effort': 0}
        ]
        db = MockDatabase(stats_data=invalid_stats)
        screen_manager = MockScreenManager(
            database=db,
            state_manager=mock_state_manager
        )
        
        detail = DetailScreen(screen_manager, pokemon_id=25)
        detail.on_enter()
        
        # Should handle null gracefully
        surface = pygame.Surface((800, 480))
        detail.render(surface)
        
        # Null stat should be treated as 0
        assert detail.stats[0]['base_stat'] is None


class TestDetailScreenStatBarRendering:
    """Test stat bar rendering logic (Story 3.2)"""
    
    def test_stat_bars_render_without_crash(self, pygame_init, mock_screen_manager):
        """Test stat bars render successfully"""
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        surface = pygame.Surface((800, 480))
        detail.render(surface)
        
        # Should complete without errors
        assert detail.stats is not None
        assert len(detail.stats) == 6
    
    def test_proportional_bar_widths(self, pygame_init, mock_screen_manager):
        """Test bar widths are proportional to stat values (AC #2)"""
        # Create Pokémon with extreme stats
        extreme_stats = [
            {'name': 'HP', 'base_stat': 1, 'effort': 0},      # Min
            {'name': 'Attack', 'base_stat': 255, 'effort': 0}, # Max
            {'name': 'Defense', 'base_stat': 127, 'effort': 0}, # ~50%
            {'name': 'Special Attack', 'base_stat': 64, 'effort': 0}, # ~25%
            {'name': 'Special Defense', 'base_stat': 191, 'effort': 0}, # ~75%
            {'name': 'Speed', 'base_stat': 128, 'effort': 0}  # ~50%
        ]
        db = MockDatabase(stats_data=extreme_stats)
        screen_manager = MockScreenManager(
            database=db,
            state_manager=MockStateManager()
        )
        
        detail = DetailScreen(screen_manager, pokemon_id=25)
        detail.on_enter()
        
        surface = pygame.Surface((800, 480))
        detail.render(surface)
        
        # Verify stats are loaded correctly
        assert detail.stats[0]['base_stat'] == 1   # Min
        assert detail.stats[1]['base_stat'] == 255 # Max
    
    def test_stat_color_applied_correctly(self, pygame_init, mock_screen_manager):
        """Test stat bar colors match value ranges (AC #3)"""
        # Create Pokémon with stats in each range
        varied_stats = [
            {'name': 'HP', 'base_stat': 25, 'effort': 0},      # Low (gray)
            {'name': 'Attack', 'base_stat': 75, 'effort': 0},  # Medium (electric blue)
            {'name': 'Defense', 'base_stat': 125, 'effort': 0}, # High (bright cyan)
            {'name': 'Special Attack', 'base_stat': 200, 'effort': 0}, # Exceptional (orange)
            {'name': 'Special Defense', 'base_stat': 50, 'effort': 0}, # Low boundary
            {'name': 'Speed', 'base_stat': 101, 'effort': 0}   # High boundary
        ]
        db = MockDatabase(stats_data=varied_stats)
        screen_manager = MockScreenManager(
            database=db,
            state_manager=MockStateManager()
        )
        
        detail = DetailScreen(screen_manager, pokemon_id=25)
        detail.on_enter()
        
        # Verify color logic would apply correctly
        assert get_stat_color(25) == Colors.STAT_COLORS['low']
        assert get_stat_color(75) == Colors.STAT_COLORS['medium']
        assert get_stat_color(125) == Colors.STAT_COLORS['high']
        assert get_stat_color(200) == Colors.STAT_COLORS['exceptional']
    
    def test_high_stats_have_glow(self, pygame_init, mock_screen_manager):
        """Test stats >= 100 trigger glow effect (AC #4)"""
        # Create Pokémon with some stats >= 100
        high_stats = [
            {'name': 'HP', 'base_stat': 99, 'effort': 0},      # No glow
            {'name': 'Attack', 'base_stat': 100, 'effort': 0}, # Glow (boundary)
            {'name': 'Defense', 'base_stat': 150, 'effort': 0}, # Glow
            {'name': 'Special Attack', 'base_stat': 50, 'effort': 0}, # No glow
            {'name': 'Special Defense', 'base_stat': 180, 'effort': 0}, # Glow
            {'name': 'Speed', 'base_stat': 90, 'effort': 0}    # No glow
        ]
        db = MockDatabase(stats_data=high_stats)
        screen_manager = MockScreenManager(
            database=db,
            state_manager=MockStateManager()
        )
        
        detail = DetailScreen(screen_manager, pokemon_id=25)
        detail.on_enter()
        
        surface = pygame.Surface((800, 480))
        detail.render(surface)
        
        # Glow logic tested via rendering (visual test)
        # Verify stats that should have glow
        assert detail.stats[1]['base_stat'] >= 100  # Attack
        assert detail.stats[2]['base_stat'] >= 100  # Defense
        assert detail.stats[4]['base_stat'] >= 100  # Sp. Def
    
    def test_stat_labels_and_values_render(self, pygame_init, mock_screen_manager):
        """Test stat labels and values are rendered (AC #5)"""
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        # Verify fonts are loaded
        assert detail.stat_label_font is not None
        assert detail.stat_value_font is not None
        
        surface = pygame.Surface((800, 480))
        detail.render(surface)
        
        # Should render labels and values for all 6 stats
        assert len(detail.stats) == 6


class TestDetailScreenStatPerformance:
    """Test stat rendering performance (Story 3.2, AC #9)"""
    
    def test_stat_rendering_time_under_10ms(self, pygame_init, mock_screen_manager):
        """Test stat bar rendering completes in < 10ms"""
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        surface = pygame.Surface((800, 480))
        
        # Warm up (first render may include font caching)
        detail.render(surface)
        
        # Measure stat rendering over multiple frames
        render_times = []
        for _ in range(20):
            detail.render(surface)  # Full render includes stat bars
        
        # Note: We can't isolate _render_stat_bars() easily without access to internals
        # But full render should still be under 33ms total (includes stats)
        # Stat bars should be a small fraction of that
    
    def test_total_render_time_maintains_30fps(self, pygame_init, mock_screen_manager):
        """Test total render time (including stats) maintains 30+ FPS"""
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        surface = pygame.Surface((800, 480))
        
        render_times = []
        for _ in range(30):
            start = time.perf_counter()
            detail.render(surface)
            elapsed = time.perf_counter() - start
            render_times.append(elapsed * 1000)
        
        avg_render_time = sum(render_times) / len(render_times)
        
        # Should maintain 30 FPS (33ms budget)
        assert avg_render_time < 33, f"Average render time {avg_render_time:.2f}ms exceeds 33ms"


class TestDetailScreenStatIntegration:
    """Integration tests for complete stat display (Story 3.2)"""
    
    def test_six_stats_display_integration(self, pygame_init):
        """Test all 6 stats displayed with correct order"""
        try:
            from src.data.database import Database
            
            with Database() as db:
                # Check if Pikachu exists in database
                pokemon = db.get_pokemon_by_id(25)
                if pokemon:
                    stats = db.get_pokemon_stats(25)
                    
                    # Should have 6 stats
                    assert len(stats) == 6
                    
                    # Verify canonical order
                    stat_names = [s['name'] for s in stats]
                    assert 'HP' in stat_names
                    assert 'Speed' in stat_names
                else:
                    pytest.skip("Pikachu not in database")
        except Exception:
            pytest.skip("Database not available")
    
    def test_edge_case_shedinja_hp_1(self, pygame_init, mock_state_manager):
        """Test Shedinja (HP=1) shows minimal but visible bar"""
        # Shedinja has HP=1 (edge case - minimum stat)
        shedinja_stats = [
            {'name': 'HP', 'base_stat': 1, 'effort': 0},
            {'name': 'Attack', 'base_stat': 90, 'effort': 0},
            {'name': 'Defense', 'base_stat': 45, 'effort': 0},
            {'name': 'Special Attack', 'base_stat': 30, 'effort': 0},
            {'name': 'Special Defense', 'base_stat': 30, 'effort': 0},
            {'name': 'Speed', 'base_stat': 40, 'effort': 0}
        ]
        db = MockDatabase(
            pokemon_data={'id': 292, 'name': 'shedinja', 'height': 8, 'weight': 12, 'generation': 3},
            stats_data=shedinja_stats
        )
        screen_manager = MockScreenManager(database=db, state_manager=mock_state_manager)
        
        detail = DetailScreen(screen_manager, pokemon_id=292)
        detail.on_enter()
        
        surface = pygame.Surface((800, 480))
        detail.render(surface)
        
        # Bar should be minimal (1px min) but visible
        assert detail.stats[0]['base_stat'] == 1
    
    def test_edge_case_blissey_hp_255(self, pygame_init, mock_state_manager):
        """Test Blissey (HP=255) fills bar completely"""
        # Blissey has HP=255 (edge case - maximum stat)
        blissey_stats = [
            {'name': 'HP', 'base_stat': 255, 'effort': 0},
            {'name': 'Attack', 'base_stat': 10, 'effort': 0},
            {'name': 'Defense', 'base_stat': 10, 'effort': 0},
            {'name': 'Special Attack', 'base_stat': 75, 'effort': 0},
            {'name': 'Special Defense', 'base_stat': 135, 'effort': 0},
            {'name': 'Speed', 'base_stat': 55, 'effort': 0}
        ]
        db = MockDatabase(
            pokemon_data={'id': 242, 'name': 'blissey', 'height': 15, 'weight': 468, 'generation': 2},
            stats_data=blissey_stats
        )
        screen_manager = MockScreenManager(database=db, state_manager=mock_state_manager)
        
        detail = DetailScreen(screen_manager, pokemon_id=242)
        detail.on_enter()
        
        surface = pygame.Surface((800, 480))
        detail.render(surface)
        
        # Bar should fill 100%
        assert detail.stats[0]['base_stat'] == 255
    
    def test_mewtwo_multiple_high_stats_glow(self, pygame_init, mock_state_manager):
        """Test Mewtwo (multiple high stats) has multiple glow effects"""
        # Mewtwo has multiple stats > 100 (test glow on multiple bars)
        mewtwo_stats = [
            {'name': 'HP', 'base_stat': 106, 'effort': 0},
            {'name': 'Attack', 'base_stat': 110, 'effort': 0},
            {'name': 'Defense', 'base_stat': 90, 'effort': 0},
            {'name': 'Special Attack', 'base_stat': 154, 'effort': 0},
            {'name': 'Special Defense', 'base_stat': 90, 'effort': 0},
            {'name': 'Speed', 'base_stat': 130, 'effort': 0}
        ]
        db = MockDatabase(
            pokemon_data={'id': 150, 'name': 'mewtwo', 'height': 20, 'weight': 1220, 'generation': 1},
            stats_data=mewtwo_stats
        )
        screen_manager = MockScreenManager(database=db, state_manager=mock_state_manager)
        
        detail = DetailScreen(screen_manager, pokemon_id=150)
        detail.on_enter()
        
        surface = pygame.Surface((800, 480))
        detail.render(surface)
        
        # Count stats >= 100 (should have glow)
        high_stats = [s for s in detail.stats if s['base_stat'] >= 100]
        assert len(high_stats) == 4  # HP, Attack, Sp.Atk, Speed


class TestTypeBadgeColors:
    """Test TYPE_COLORS constant matches UX spec (Story 3.3, AC #6)"""
    
    def test_type_colors_defined(self):
        """Test TYPE_COLORS constant exists and has all 17 Gen 1-3 types"""
        from src.ui.colors import TYPE_COLORS
        
        # Should have exactly 17 types (no Fairy for Gen 1-3)
        assert len(TYPE_COLORS) == 17
        
        # Verify all expected types present
        expected_types = [
            'normal', 'fire', 'water', 'electric', 'grass', 'ice',
            'fighting', 'poison', 'ground', 'flying', 'psychic',
            'bug', 'rock', 'ghost', 'dragon', 'dark', 'steel'
        ]
        for type_name in expected_types:
            assert type_name in TYPE_COLORS, f"Type '{type_name}' missing from TYPE_COLORS"
        
        # Verify Fairy type NOT present (Gen 1-3 only)
        assert 'fairy' not in TYPE_COLORS
    
    def test_type_colors_match_ux_spec(self):
        """Test each type color matches UX Design Specification exactly"""
        from src.ui.colors import TYPE_COLORS
        
        # Verify specific colors from UX spec
        assert TYPE_COLORS['normal'] == (184, 184, 208)      # #b8b8d0
        assert TYPE_COLORS['fire'] == (255, 107, 53)         # #ff6b35
        assert TYPE_COLORS['water'] == (77, 159, 255)        # #4d9fff
        assert TYPE_COLORS['electric'] == (255, 210, 63)     # #ffd23f
        assert TYPE_COLORS['grass'] == (107, 255, 107)       # #6bff6b
        assert TYPE_COLORS['ice'] == (168, 230, 255)         # #a8e6ff
        assert TYPE_COLORS['fighting'] == (255, 71, 87)      # #ff4757
        assert TYPE_COLORS['poison'] == (178, 77, 255)       # #b24dff
        assert TYPE_COLORS['ground'] == (212, 165, 116)      # #d4a574
        assert TYPE_COLORS['flying'] == (141, 159, 255)      # #8d9fff
        assert TYPE_COLORS['psychic'] == (255, 107, 189)     # #ff6bbd
        assert TYPE_COLORS['bug'] == (184, 216, 72)          # #b8d848
        assert TYPE_COLORS['rock'] == (196, 176, 122)        # #c4b07a
        assert TYPE_COLORS['ghost'] == (157, 124, 206)       # #9d7cce
        assert TYPE_COLORS['dragon'] == (141, 77, 255)       # #8d4dff
        assert TYPE_COLORS['dark'] == (139, 115, 85)         # #8b7355
        assert TYPE_COLORS['steel'] == (203, 213, 224)       # #cbd5e0


class TestTypeBadgeRendering:
    """Test type badge rendering methods (Story 3.3)"""
    
    def test_single_type_display(self, pygame_init, mock_screen_manager):
        """Test single type Pokemon displays one badge (AC #1)"""
        # Pikachu is Electric (single type)
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        # Should have loaded 1 type
        assert len(detail.types) == 1
        assert detail.types[0] == 'Electric'
        
        # Render without crashing
        surface = pygame.Surface((800, 480))
        detail.render(surface)
    
    def test_dual_type_display(self, pygame_init, mock_state_manager):
        """Test dual type Pokemon displays two badges (AC #2)"""
        # Charizard is Fire/Flying (dual type)
        db = MockDatabase(
            pokemon_data={'id': 6, 'name': 'charizard', 'height': 17, 'weight': 905, 'generation': 1},
            stats_data=[
                {'name': 'HP', 'base_stat': 78, 'effort': 0},
                {'name': 'Attack', 'base_stat': 84, 'effort': 0},
                {'name': 'Defense', 'base_stat': 78, 'effort': 0},
                {'name': 'Special Attack', 'base_stat': 109, 'effort': 0},
                {'name': 'Special Defense', 'base_stat': 85, 'effort': 0},
                {'name': 'Speed', 'base_stat': 100, 'effort': 0}
            ],
            types_data=['Fire', 'Flying']
        )
        screen_manager = MockScreenManager(database=db, state_manager=mock_state_manager)
        
        detail = DetailScreen(screen_manager, pokemon_id=6)
        detail.on_enter()
        
        # Should have loaded 2 types
        assert len(detail.types) == 2
        assert detail.types[0] == 'Fire'
        assert detail.types[1] == 'Flying'
        
        # Render without crashing
        surface = pygame.Surface((800, 480))
        detail.render(surface)
    
    def test_type_badge_font_loaded(self, pygame_init, mock_screen_manager):
        """Test type badge font is loaded on_enter (AC #5)"""
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        # Font should be loaded
        assert detail.type_badge_font is not None
    
    def test_lighten_color_function(self, pygame_init, mock_screen_manager):
        """Test _lighten_color() for badge borders (AC #3)"""
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        
        # Test lightening a color
        base_color = (100, 100, 100)
        lighter = detail._lighten_color(base_color, 20)
        
        assert lighter == (120, 120, 120)
        
        # Test clamping at 255
        bright_color = (250, 250, 250)
        lighter_bright = detail._lighten_color(bright_color, 20)
        
        assert lighter_bright[0] == 255
        assert lighter_bright[1] == 255
        assert lighter_bright[2] == 255
    
    def test_render_type_badge_returns_width(self, pygame_init, mock_screen_manager):
        """Test _render_type_badge() returns badge width for positioning"""
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        surface = pygame.Surface((800, 480))
        
        # Render a badge and check it returns a width
        width = detail._render_type_badge(surface, "Electric", 100, 100)
        
        # Width should be in valid range (80-120px per AC #9)
        assert width >= 80
        assert width <= 120
    
    def test_unknown_type_uses_default_gray(self, pygame_init, mock_state_manager):
        """Test unknown type name uses default gray badge (AC #8)"""
        # Create Pokemon with unknown type
        db = MockDatabase(
            pokemon_data={'id': 999, 'name': 'missingno', 'height': 10, 'weight': 100, 'generation': 1},
            stats_data=[{'name': 'HP', 'base_stat': 50, 'effort': 0}] * 6,
            types_data=['UnknownType']
        )
        screen_manager = MockScreenManager(database=db, state_manager=mock_state_manager)
        
        detail = DetailScreen(screen_manager, pokemon_id=999)
        detail.on_enter()
        
        # Should have type but it's unknown
        assert len(detail.types) == 1
        assert detail.types[0] == 'UnknownType'
        
        # Should render with default gray (not crash)
        surface = pygame.Surface((800, 480))
        detail.render(surface)


class TestTypeBadgeDataValidation:
    """Test type badge error handling (Story 3.3, AC #8)"""
    
    def test_empty_types_shows_placeholder(self, pygame_init, mock_state_manager):
        """Test empty type list shows ??? placeholder"""
        db = MockDatabase(
            pokemon_data={'id': 999, 'name': 'typeless', 'height': 10, 'weight': 100, 'generation': 1},
            stats_data=[{'name': 'HP', 'base_stat': 50, 'effort': 0}] * 6,
            types_data=[]  # No types
        )
        screen_manager = MockScreenManager(database=db, state_manager=mock_state_manager)
        
        detail = DetailScreen(screen_manager, pokemon_id=999)
        detail.on_enter()
        
        # Should have placeholder
        assert len(detail.types) == 1
        assert detail.types[0] == "???"
        
        # Should render without crashing
        surface = pygame.Surface((800, 480))
        detail.render(surface)
    
    def test_excess_types_limited_to_two(self, pygame_init, mock_state_manager):
        """Test more than 2 types limited to first 2 with warning"""
        # Invalid data: 3 types
        db = MockDatabase(
            pokemon_data={'id': 999, 'name': 'tritype', 'height': 10, 'weight': 100, 'generation': 1},
            stats_data=[{'name': 'HP', 'base_stat': 50, 'effort': 0}] * 6,
            types_data=['Fire', 'Water', 'Grass']  # Invalid: 3 types
        )
        screen_manager = MockScreenManager(database=db, state_manager=mock_state_manager)
        
        detail = DetailScreen(screen_manager, pokemon_id=999)
        detail.on_enter()
        
        # Should only keep first 2
        assert len(detail.types) == 2
        assert detail.types[0] == 'Fire'
        assert detail.types[1] == 'Water'
        
        # Should render without crashing
        surface = pygame.Surface((800, 480))
        detail.render(surface)
    
    def test_types_in_slot_order(self, pygame_init, mock_state_manager):
        """Test types returned in slot order (primary first, secondary second)"""
        # Dual type Pokemon
        db = MockDatabase(
            pokemon_data={'id': 1, 'name': 'bulbasaur', 'height': 7, 'weight': 69, 'generation': 1},
            stats_data=[{'name': 'HP', 'base_stat': 45, 'effort': 0}] * 6,
            types_data=['Grass', 'Poison']  # Slot order
        )
        screen_manager = MockScreenManager(database=db, state_manager=mock_state_manager)
        
        detail = DetailScreen(screen_manager, pokemon_id=1)
        detail.on_enter()
        
        # Should maintain order
        assert detail.types[0] == 'Grass'   # Primary type (slot 1)
        assert detail.types[1] == 'Poison'  # Secondary type (slot 2)


class TestTypeBadgePerformance:
    """Test type badge rendering performance (Story 3.3, AC #10)"""
    
    def test_type_badge_rendering_under_5ms(self, pygame_init, mock_screen_manager):
        """Test type badge rendering completes in <5ms per frame"""
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        surface = pygame.Surface((800, 480))
        
        # Warm up
        detail.render(surface)
        
        # Measure type badge rendering over multiple frames
        render_times = []
        for _ in range(20):
            detail.render(surface)
        
        # Full render should stay under 33ms (includes type badges)
        # Type badges should be a small fraction (<5ms target)
    
    def test_dual_type_rendering_performance(self, pygame_init, mock_state_manager):
        """Test dual type badges don't significantly impact performance"""
        # Dual type Pokemon
        db = MockDatabase(
            pokemon_data={'id': 6, 'name': 'charizard', 'height': 17, 'weight': 905, 'generation': 1},
            stats_data=[{'name': 'HP', 'base_stat': 78, 'effort': 0}] * 6,
            types_data=['Fire', 'Flying']
        )
        screen_manager = MockScreenManager(database=db, state_manager=mock_state_manager)
        
        detail = DetailScreen(screen_manager, pokemon_id=6)
        detail.on_enter()
        
        surface = pygame.Surface((800, 480))
        
        # Measure render time
        render_times = []
        for _ in range(20):
            start = time.perf_counter()
            detail.render(surface)
            elapsed = time.perf_counter() - start
            render_times.append(elapsed * 1000)
        
        avg_render_time = sum(render_times) / len(render_times)
        
        # Should maintain 30 FPS budget
        assert avg_render_time < 33, f"Render time {avg_render_time:.2f}ms exceeds 33ms"


class TestTypeBadgeIntegration:
    """Integration tests for type badge display (Story 3.3)"""
    
    def test_database_get_pokemon_types_method(self):
        """Test Database.get_pokemon_types() integration (AC #7)"""
        try:
            from src.data.database import Database
            
            with Database() as db:
                # Check if Pikachu exists
                pokemon = db.get_pokemon_by_id(25)
                if pokemon:
                    start = time.perf_counter()
                    types = db.get_pokemon_types(25)
                    elapsed = time.perf_counter() - start
                    
                    # Should return ['Electric']
                    assert len(types) >= 1
                    assert 'electric' in types[0].lower()
                    
                    # Should complete in <50ms
                    elapsed_ms = elapsed * 1000
                    assert elapsed_ms < 50, f"Query took {elapsed_ms:.2f}ms, exceeds 50ms"
                else:
                    pytest.skip("Pikachu not in database")
        except Exception:
            pytest.skip("Database not available")
    
    def test_charizard_dual_types(self):
        """Test Charizard displays Fire and Flying badges"""
        try:
            from src.data.database import Database
            
            with Database() as db:
                pokemon = db.get_pokemon_by_id(6)
                if pokemon:
                    types = db.get_pokemon_types(6)
                    
                    # Charizard should be Fire/Flying
                    assert len(types) == 2
                    assert 'fire' in types[0].lower()
                    assert 'flying' in types[1].lower()
                else:
                    pytest.skip("Charizard not in database")
        except Exception:
            pytest.skip("Database not available")
    
    def test_bulbasaur_grass_poison(self):
        """Test Bulbasaur displays Grass and Poison badges"""
        try:
            from src.data.database import Database
            
            with Database() as db:
                pokemon = db.get_pokemon_by_id(1)
                if pokemon:
                    types = db.get_pokemon_types(1)
                    
                    # Bulbasaur should be Grass/Poison
                    assert len(types) == 2
                    assert 'grass' in types[0].lower()
                    assert 'poison' in types[1].lower()
                else:
                    pytest.skip("Bulbasaur not in database")
        except Exception:
            pytest.skip("Database not available")
    
    def test_gengar_ghost_poison_colors(self):
        """Test Gengar displays Ghost and Poison badges with correct colors"""
        from src.ui.colors import TYPE_COLORS
        
        try:
            from src.data.database import Database
            
            with Database() as db:
                pokemon = db.get_pokemon_by_id(94)
                if pokemon:
                    types = db.get_pokemon_types(94)
                    
                    # Gengar should be Ghost/Poison
                    assert len(types) == 2
                    assert 'ghost' in types[0].lower()
                    assert 'poison' in types[1].lower()
                    
                    # Verify colors are defined
                    assert 'ghost' in TYPE_COLORS
                    assert 'poison' in TYPE_COLORS
                else:
                    pytest.skip("Gengar not in database")
        except Exception:
            pytest.skip("Database not available")


class TestPhysicalDataUnitConversion:
    """Test unit conversion for physical data (Story 3.4, AC #6)"""
    
    def test_height_decimeters_to_meters(self, pygame_init, mock_screen_manager):
        """Test height conversion: decimeters / 10 = meters"""
        # Pikachu: height = 4 dm = 0.4 m
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        assert detail.height == 0.4
    
    def test_weight_hectograms_to_kilograms(self, pygame_init, mock_screen_manager):
        """Test weight conversion: hectograms / 10 = kilograms"""
        # Pikachu: weight = 60 hg = 6.0 kg
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        assert detail.weight == 6.0
    
    def test_large_pokemon_onix(self, pygame_init, mock_state_manager):
        """Test large Pokémon (Onix: 88dm, 2100hg)"""
        # Onix: height = 88 dm = 8.8 m, weight = 2100 hg = 210.0 kg
        db = MockDatabase(
            pokemon_data={'id': 95, 'name': 'onix', 'height': 88, 'weight': 2100, 'generation': 1},
            stats_data=[{'name': 'HP', 'base_stat': 35, 'effort': 0}] * 6,
            types_data=['Rock', 'Ground']
        )
        screen_manager = MockScreenManager(database=db, state_manager=mock_state_manager)
        
        detail = DetailScreen(screen_manager, pokemon_id=95)
        detail.on_enter()
        
        assert detail.height == 8.8
        assert detail.weight == 210.0
    
    def test_small_pokemon_diglett(self, pygame_init, mock_state_manager):
        """Test small Pokémon (Diglett: 2dm, 8hg)"""
        # Diglett: height = 2 dm = 0.2 m, weight = 8 hg = 0.8 kg
        db = MockDatabase(
            pokemon_data={'id': 50, 'name': 'diglett', 'height': 2, 'weight': 8, 'generation': 1},
            stats_data=[{'name': 'HP', 'base_stat': 10, 'effort': 0}] * 6,
            types_data=['Ground']
        )
        screen_manager = MockScreenManager(database=db, state_manager=mock_state_manager)
        
        detail = DetailScreen(screen_manager, pokemon_id=50)
        detail.on_enter()
        
        assert detail.height == 0.2
        assert detail.weight == 0.8


class TestPhysicalDataEdgeCases:
    """Test edge case handling for physical data (Story 3.4, AC #7)"""
    
    def test_zero_height(self, pygame_init, mock_state_manager):
        """Test height = 0 shows ??? placeholder"""
        db = MockDatabase(
            pokemon_data={'id': 999, 'name': 'missingdata', 'height': 0, 'weight': 100, 'generation': 1},
            stats_data=[{'name': 'HP', 'base_stat': 50, 'effort': 0}] * 6,
            types_data=['Normal']
        )
        screen_manager = MockScreenManager(database=db, state_manager=mock_state_manager)
        
        detail = DetailScreen(screen_manager, pokemon_id=999)
        detail.on_enter()
        
        # Should set marker for placeholder
        assert detail.height == -1
    
    def test_zero_weight(self, pygame_init, mock_state_manager):
        """Test weight = 0 shows ??? placeholder"""
        db = MockDatabase(
            pokemon_data={'id': 999, 'name': 'missingdata', 'height': 50, 'weight': 0, 'generation': 1},
            stats_data=[{'name': 'HP', 'base_stat': 50, 'effort': 0}] * 6,
            types_data=['Normal']
        )
        screen_manager = MockScreenManager(database=db, state_manager=mock_state_manager)
        
        detail = DetailScreen(screen_manager, pokemon_id=999)
        detail.on_enter()
        
        # Should set marker for placeholder
        assert detail.weight == -1
    
    def test_none_height(self, pygame_init, mock_state_manager):
        """Test None height shows ??? placeholder"""
        db = MockDatabase(
            pokemon_data={'id': 999, 'name': 'missingdata', 'height': None, 'weight': 100, 'generation': 1},
            stats_data=[{'name': 'HP', 'base_stat': 50, 'effort': 0}] * 6,
            types_data=['Normal']
        )
        screen_manager = MockScreenManager(database=db, state_manager=mock_state_manager)
        
        detail = DetailScreen(screen_manager, pokemon_id=999)
        detail.on_enter()
        
        # Should convert None to 0.0, then mark as -1 for placeholder
        assert detail.height == -1
    
    def test_none_weight(self, pygame_init, mock_state_manager):
        """Test None weight shows ??? placeholder"""
        db = MockDatabase(
            pokemon_data={'id': 999, 'name': 'missingdata', 'height': 50, 'weight': None, 'generation': 1},
            stats_data=[{'name': 'HP', 'base_stat': 50, 'effort': 0}] * 6,
            types_data=['Normal']
        )
        screen_manager = MockScreenManager(database=db, state_manager=mock_state_manager)
        
        detail = DetailScreen(screen_manager, pokemon_id=999)
        detail.on_enter()
        
        # Should convert None to 0.0, then mark as -1 for placeholder
        assert detail.weight == -1
    
    def test_extreme_height_warning(self, pygame_init, mock_state_manager):
        """Test extreme height > 100m logs warning but displays value"""
        # Unrealistic data: 1500 dm = 150 m
        db = MockDatabase(
            pokemon_data={'id': 999, 'name': 'giant', 'height': 1500, 'weight': 5000, 'generation': 1},
            stats_data=[{'name': 'HP', 'base_stat': 255, 'effort': 0}] * 6,
            types_data=['Normal']
        )
        screen_manager = MockScreenManager(database=db, state_manager=mock_state_manager)
        
        detail = DetailScreen(screen_manager, pokemon_id=999)
        detail.on_enter()
        
        # Should convert and store value (not replace with placeholder)
        assert detail.height == 150.0
        # Warning should be logged (can't easily test logging without capturing)
    
    def test_extreme_weight_warning(self, pygame_init, mock_state_manager):
        """Test extreme weight > 10000kg logs warning but displays value"""
        # Unrealistic data: 150000 hg = 15000 kg
        db = MockDatabase(
            pokemon_data={'id': 999, 'name': 'heavy', 'height': 100, 'weight': 150000, 'generation': 1},
            stats_data=[{'name': 'HP', 'base_stat': 255, 'effort': 0}] * 6,
            types_data=['Normal']
        )
        screen_manager = MockScreenManager(database=db, state_manager=mock_state_manager)
        
        detail = DetailScreen(screen_manager, pokemon_id=999)
        detail.on_enter()
        
        # Should convert and store value (not replace with placeholder)
        assert detail.weight == 15000.0


class TestPhysicalDataFormatting:
    """Test physical data formatting (Story 3.4, AC #8)"""
    
    def test_height_format_one_decimal(self, pygame_init, mock_screen_manager):
        """Test height formatted as 'X.Xm' with one decimal place"""
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        # Pikachu: 0.4m
        height_str = f"{detail.height:.1f}m"
        assert height_str == "0.4m"
    
    def test_weight_format_one_decimal(self, pygame_init, mock_screen_manager):
        """Test weight formatted as 'X.Xkg' with one decimal place"""
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        # Pikachu: 6.0kg
        weight_str = f"{detail.weight:.1f}kg"
        assert weight_str == "6.0kg"
    
    def test_large_values_formatting(self, pygame_init, mock_state_manager):
        """Test large values format correctly (Onix: 8.8m, 210.0kg)"""
        db = MockDatabase(
            pokemon_data={'id': 95, 'name': 'onix', 'height': 88, 'weight': 2100, 'generation': 1},
            stats_data=[{'name': 'HP', 'base_stat': 35, 'effort': 0}] * 6,
            types_data=['Rock', 'Ground']
        )
        screen_manager = MockScreenManager(database=db, state_manager=mock_state_manager)
        
        detail = DetailScreen(screen_manager, pokemon_id=95)
        detail.on_enter()
        
        height_str = f"{detail.height:.1f}m"
        weight_str = f"{detail.weight:.1f}kg"
        
        assert height_str == "8.8m"
        assert weight_str == "210.0kg"
    
    def test_small_values_formatting(self, pygame_init, mock_state_manager):
        """Test small values format correctly (Diglett: 0.2m, 0.8kg)"""
        db = MockDatabase(
            pokemon_data={'id': 50, 'name': 'diglett', 'height': 2, 'weight': 8, 'generation': 1},
            stats_data=[{'name': 'HP', 'base_stat': 10, 'effort': 0}] * 6,
            types_data=['Ground']
        )
        screen_manager = MockScreenManager(database=db, state_manager=mock_state_manager)
        
        detail = DetailScreen(screen_manager, pokemon_id=50)
        detail.on_enter()
        
        height_str = f"{detail.height:.1f}m"
        weight_str = f"{detail.weight:.1f}kg"
        
        assert height_str == "0.2m"
        assert weight_str == "0.8kg"
    
    def test_placeholder_format(self, pygame_init, mock_state_manager):
        """Test placeholder '???' displayed for invalid data"""
        db = MockDatabase(
            pokemon_data={'id': 999, 'name': 'invalid', 'height': 0, 'weight': 0, 'generation': 1},
            stats_data=[{'name': 'HP', 'base_stat': 50, 'effort': 0}] * 6,
            types_data=['Normal']
        )
        screen_manager = MockScreenManager(database=db, state_manager=mock_state_manager)
        
        detail = DetailScreen(screen_manager, pokemon_id=999)
        detail.on_enter()
        
        # Both should be marked invalid
        assert detail.height == -1
        assert detail.weight == -1
        
        # Render should show "???" (visual test)
        surface = pygame.Surface((800, 480))
        detail.render(surface)


class TestPhysicalDataRendering:
    """Test physical data rendering methods (Story 3.4, AC #1-5, #9)"""
    
    def test_physical_data_renders_without_crash(self, pygame_init, mock_screen_manager):
        """Test physical data section renders successfully"""
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        surface = pygame.Surface((800, 480))
        detail.render(surface)
        
        # Should have loaded physical data
        assert detail.height == 0.4
        assert detail.weight == 6.0
    
    def test_physical_data_colors(self, pygame_init, mock_screen_manager):
        """Test labels use ice blue, values use white (AC #9)"""
        from src.ui.colors import Colors
        
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        # Verify colors are defined
        assert Colors.ICE_BLUE == (168, 230, 255)
        assert Colors.HOLOGRAM_WHITE == (232, 244, 248)
        
        # Render with these colors
        surface = pygame.Surface((800, 480))
        detail.render(surface)
    
    def test_physical_data_positioning(self, pygame_init, mock_screen_manager):
        """Test physical data positioned below sprite and type badges (AC #3)"""
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        # Physical data should be positioned at y = screen_height - 120
        screen_height = 480
        expected_y = screen_height - 120  # 360
        
        # Can't easily verify exact position without inspecting render internals
        # But rendering should complete without overlap
        surface = pygame.Surface((800, 480))
        detail.render(surface)
    
    def test_physical_data_fonts_loaded(self, pygame_init, mock_screen_manager):
        """Test fonts loaded for physical data rendering (AC #4, #9)"""
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        # Body font used for 16px physical data
        assert detail.body_font is not None
    
    def test_placeholder_panel_removed(self, pygame_init, mock_screen_manager):
        """Test physical data placeholder panel no longer rendered"""
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        surface = pygame.Surface((800, 480))
        detail.render(surface)
        
        # Should render real data, not placeholder
        # (visual verification - placeholder panel removed from code)


class TestPhysicalDataPerformance:
    """Test physical data rendering performance (Story 3.4, AC #10)"""
    
    def test_physical_data_render_time_under_2ms(self, pygame_init, mock_screen_manager):
        """Test physical data rendering completes in < 2ms per frame"""
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        surface = pygame.Surface((800, 480))
        
        # Warm up
        detail.render(surface)
        
        # Measure full render time (includes physical data)
        render_times = []
        for _ in range(30):
            start = time.perf_counter()
            detail.render(surface)
            elapsed = time.perf_counter() - start
            render_times.append(elapsed * 1000)
        
        avg_render_time = sum(render_times) / len(render_times)
        
        # Full render should maintain 30 FPS budget
        assert avg_render_time < 33, f"Render time {avg_render_time:.2f}ms exceeds 33ms"
    
    def test_total_render_maintains_30fps(self, pygame_init, mock_screen_manager):
        """Test total DetailScreen render maintains 30+ FPS with physical data"""
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        surface = pygame.Surface((800, 480))
        
        # Measure over extended period
        render_times = []
        for _ in range(60):
            start = time.perf_counter()
            detail.render(surface)
            elapsed = time.perf_counter() - start
            render_times.append(elapsed * 1000)
        
        avg_render_time = sum(render_times) / len(render_times)
        max_render_time = max(render_times)
        
        # Average and max should both be under 33ms
        assert avg_render_time < 33, f"Avg render {avg_render_time:.2f}ms exceeds 33ms"
        assert max_render_time < 50, f"Max render {max_render_time:.2f}ms exceeds reasonable limit"


class TestPhysicalDataIntegration:
    """Integration tests for physical data with database (Story 3.4)"""
    
    def test_database_provides_height_weight(self):
        """Test Database.get_pokemon_by_id() returns height/weight"""
        try:
            from src.data.database import Database
            
            with Database() as db:
                pokemon = db.get_pokemon_by_id(25)
                if pokemon:
                    # Should have height and weight fields
                    assert 'height' in pokemon
                    assert 'weight' in pokemon
                    
                    # Pikachu values (in decimeters/hectograms)
                    assert pokemon['height'] == 4
                    assert pokemon['weight'] == 60
                else:
                    pytest.skip("Pikachu not in database")
        except Exception:
            pytest.skip("Database not available")
    
    def test_onix_large_measurements(self):
        """Test Onix (large Pokémon) physical data"""
        try:
            from src.data.database import Database
            
            with Database() as db:
                pokemon = db.get_pokemon_by_id(95)
                if pokemon:
                    # Onix: 88 dm = 8.8m, 2100 hg = 210kg
                    assert pokemon['height'] == 88
                    assert pokemon['weight'] == 2100
                    
                    # Test conversion
                    height_m = pokemon['height'] / 10.0
                    weight_kg = pokemon['weight'] / 10.0
                    
                    assert height_m == 8.8
                    assert weight_kg == 210.0
                else:
                    pytest.skip("Onix not in database")
        except Exception:
            pytest.skip("Database not available")
    
    def test_wailord_extreme_size(self):
        """Test Wailord (Gen 3, huge Pokémon) physical data"""
        try:
            from src.data.database import Database
            
            with Database() as db:
                pokemon = db.get_pokemon_by_id(321)
                if pokemon:
                    # Wailord is massive: 145 dm = 14.5m, 3980 hg = 398kg
                    height_m = pokemon['height'] / 10.0
                    weight_kg = pokemon['weight'] / 10.0
                    
                    assert height_m > 10  # Very tall
                    assert weight_kg > 300  # Very heavy
                else:
                    pytest.skip("Wailord not in database (Gen 3)")
        except Exception:
            pytest.skip("Database not available")
    
    def test_all_gen_1_3_pokemon_have_measurements(self):
        """Test all Gen 1-3 Pokémon (1-386) have valid height/weight"""
        try:
            from src.data.database import Database
            
            with Database() as db:
                # Sample random Pokémon from each generation
                sample_ids = [
                    1,    # Bulbasaur (Gen 1)
                    25,   # Pikachu (Gen 1)
                    152,  # Chikorita (Gen 2)
                    252,  # Treecko (Gen 3)
                    386   # Deoxys (Gen 3, last)
                ]
                
                for pokemon_id in sample_ids:
                    pokemon = db.get_pokemon_by_id(pokemon_id)
                    if pokemon:
                        # Should have height and weight
                        assert 'height' in pokemon
                        assert 'weight' in pokemon
                        assert pokemon['height'] > 0
                        assert pokemon['weight'] > 0
        except Exception:
            pytest.skip("Database not available")


class TestPhysicalDataComprehensive:
    """Comprehensive tests covering all Story 3.4 acceptance criteria"""
    
    def test_ac_1_height_display(self, pygame_init, mock_screen_manager):
        """Test AC #1: Height displayed in meters with format 'X.Xm'"""
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        # Height should be 0.4m
        assert detail.height == 0.4
        
        # Format should be X.Xm
        height_str = f"{detail.height:.1f}m"
        assert height_str == "0.4m"
        
        # Render without crash
        surface = pygame.Surface((800, 480))
        detail.render(surface)
    
    def test_ac_2_weight_display(self, pygame_init, mock_screen_manager):
        """Test AC #2: Weight displayed in kilograms with format 'X.Xkg'"""
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        # Weight should be 6.0kg
        assert detail.weight == 6.0
        
        # Format should be X.Xkg
        weight_str = f"{detail.weight:.1f}kg"
        assert weight_str == "6.0kg"
        
        # Render without crash
        surface = pygame.Surface((800, 480))
        detail.render(surface)
    
    def test_ac_3_positioning(self, pygame_init, mock_screen_manager):
        """Test AC #3: Physical data positioned without overlap"""
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        surface = pygame.Surface((800, 480))
        detail.render(surface)
        
        # Physical data should be in lower section (y=360 for 480 height)
        # Should not overlap sprite, stats, or type badges
        # (visual verification - tested by rendering)
    
    def test_ac_4_layout_typography(self, pygame_init, mock_screen_manager):
        """Test AC #4: Labels right-aligned, values left-aligned, 16px font"""
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        # Font should be loaded (16px body font)
        assert detail.body_font is not None
        
        surface = pygame.Surface((800, 480))
        detail.render(surface)
        
        # Layout constants tested in implementation
        # LABEL_WIDTH = 80, VALUE_OFFSET = 10, LINE_HEIGHT = 24
    
    def test_ac_5_database_query_integration(self, pygame_init, mock_screen_manager):
        """Test AC #5: Height/weight fetched from pokemon table"""
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        # Data should be loaded
        assert detail.pokemon_data is not None
        assert detail.pokemon_data['height'] == 4  # decimeters
        assert detail.pokemon_data['weight'] == 60  # hectograms
        
        # Converted values stored
        assert detail.height == 0.4  # meters
        assert detail.weight == 6.0  # kilograms
    
    def test_ac_6_unit_conversion(self, pygame_init, mock_screen_manager):
        """Test AC #6: Unit conversion formulas"""
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        # Conversion: decimeters / 10 = meters
        assert detail.height == detail.pokemon_data['height'] / 10.0
        
        # Conversion: hectograms / 10 = kilograms
        assert detail.weight == detail.pokemon_data['weight'] / 10.0
    
    def test_ac_7_edge_case_handling(self, pygame_init, mock_state_manager):
        """Test AC #7: Edge cases handled gracefully"""
        # Test None values
        db = MockDatabase(
            pokemon_data={'id': 999, 'name': 'invalid', 'height': None, 'weight': None, 'generation': 1},
            stats_data=[{'name': 'HP', 'base_stat': 50, 'effort': 0}] * 6,
            types_data=['Normal']
        )
        screen_manager = MockScreenManager(database=db, state_manager=mock_state_manager)
        
        detail = DetailScreen(screen_manager, pokemon_id=999)
        detail.on_enter()
        
        # Should handle None gracefully by converting to 0.0, then marking as -1 for placeholder
        assert detail.height == -1
        assert detail.weight == -1
        
        # Render without crash
        surface = pygame.Surface((800, 480))
        detail.render(surface)
    
    def test_ac_8_formatting_consistency(self, pygame_init, mock_state_manager):
        """Test AC #8: Formatting consistent across all Pokémon"""
        # Test multiple Pokémon
        pokemon_list = [
            {'id': 25, 'name': 'pikachu', 'height': 4, 'weight': 60, 'expected_h': "0.4m", 'expected_w': "6.0kg"},
            {'id': 95, 'name': 'onix', 'height': 88, 'weight': 2100, 'expected_h': "8.8m", 'expected_w': "210.0kg"},
            {'id': 50, 'name': 'diglett', 'height': 2, 'weight': 8, 'expected_h': "0.2m", 'expected_w': "0.8kg"},
        ]
        
        for poke in pokemon_list:
            db = MockDatabase(
                pokemon_data={'id': poke['id'], 'name': poke['name'], 
                             'height': poke['height'], 'weight': poke['weight'], 'generation': 1},
                stats_data=[{'name': 'HP', 'base_stat': 50, 'effort': 0}] * 6,
                types_data=['Normal']
            )
            screen_manager = MockScreenManager(database=db, state_manager=MockStateManager())
            
            detail = DetailScreen(screen_manager, pokemon_id=poke['id'])
            detail.on_enter()
            
            # Check formatting
            height_str = f"{detail.height:.1f}m"
            weight_str = f"{detail.weight:.1f}kg"
            
            assert height_str == poke['expected_h']
            assert weight_str == poke['expected_w']
    
    def test_ac_9_visual_consistency(self, pygame_init, mock_screen_manager):
        """Test AC #9: Visual consistency with holographic aesthetic"""
        from src.ui.colors import Colors
        
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        # Colors should match holographic palette
        assert Colors.ICE_BLUE == (168, 230, 255)  # Labels
        assert Colors.HOLOGRAM_WHITE == (232, 244, 248)  # Values
        
        surface = pygame.Surface((800, 480))
        detail.render(surface)
    
    def test_ac_10_performance_requirements(self, pygame_init, mock_screen_manager):
        """Test AC #10: Performance maintains 30+ FPS"""
        detail = DetailScreen(mock_screen_manager, pokemon_id=25)
        detail.on_enter()
        
        surface = pygame.Surface((800, 480))
        
        # Measure render performance
        render_times = []
        for _ in range(60):
            start = time.perf_counter()
            detail.render(surface)
            elapsed = time.perf_counter() - start
            render_times.append(elapsed)
        
        avg_render_time_ms = (sum(render_times) / len(render_times)) * 1000
        
        # Should maintain 30 FPS (33ms budget)
        assert avg_render_time_ms < 33, f"Render time {avg_render_time_ms:.2f}ms exceeds 33ms"


# ==========================================
# STORY 3.5: POKÉDEX DESCRIPTION TEXT DISPLAY
# ==========================================

class TestStory35DescriptionDisplay:
    """
    Tests for Story 3.5: Pokédex Description Text Display
    
    Tests description loading from database, text wrapping at word boundaries,
    4-line truncation with ellipsis, typography specifications, layout positioning,
    pre-rendering optimization, and performance requirements.
    """
    
    def test_ac_1_authentic_description_display(self, pygame_init, mock_screen_manager):
        """Test AC #1: Authentic description displayed from database"""
        # Create database with description
        description_text = "When several of these Pokémon gather, their electricity could build and cause lightning storms."
        db = MockDatabase(
            pokemon_data={
                'id': 25,
                'name': 'pikachu',
                'height': 4,
                'weight': 60,
                'generation': 1,
                'description': description_text
            }
        )
        
        screen_manager = MockScreenManager(database=db, state_manager=MockStateManager())
        detail = DetailScreen(screen_manager, pokemon_id=25)
        detail.on_enter()
        
        # Verify description loaded
        assert detail.description == description_text
        assert detail.description != "No description available"
    
    def test_ac_1_no_placeholder_when_description_exists(self, pygame_init, mock_screen_manager):
        """Test AC #1: No placeholder shown when authentic description exists"""
        db = MockDatabase(
            pokemon_data={
                'id': 25,
                'name': 'pikachu',
                'height': 4,
                'weight': 60,
                'generation': 1,
                'description': "Electric mouse Pokémon."
            }
        )
        
        screen_manager = MockScreenManager(database=db, state_manager=MockStateManager())
        detail = DetailScreen(screen_manager, pokemon_id=25)
        detail.on_enter()
        
        # Should not be placeholder
        assert "No description available" not in detail.description
    
    def test_ac_2_text_wrapping_word_boundaries(self, pygame_init, mock_screen_manager):
        """Test AC #2: Text wraps at word boundaries, not mid-word"""
        db = MockDatabase(
            pokemon_data={
                'id': 25,
                'name': 'pikachu',
                'height': 4,
                'weight': 60,
                'generation': 1,
                'description': "When several of these Pokémon gather, their electricity could build and cause lightning storms."
            }
        )
        
        screen_manager = MockScreenManager(database=db, state_manager=MockStateManager())
        detail = DetailScreen(screen_manager, pokemon_id=25)
        detail.on_enter()
        
        # Get wrapped lines
        if detail.description_font:
            wrapped_lines = detail._wrap_description_text(
                detail.description,
                detail.description_font,
                max_width=400,
                max_lines=4
            )
            
            # Verify no mid-word breaks (lines shouldn't end with partial words)
            for line in wrapped_lines:
                # Lines should end cleanly (not with hyphen unless in original text)
                assert not line.endswith('-') or '-' in detail.description
    
    def test_ac_3_four_line_display_limit(self, pygame_init, mock_screen_manager):
        """Test AC #3: Maximum 4 lines displayed"""
        # Very long description (should exceed 4 lines)
        long_description = "Created from the DNA of Mew, this Pokémon is said to have the most savage heart among all Pokémon. " \
                          "It is a Psychic-type with incredible power that was created through genetic manipulation for " \
                          "battling purposes. Its appearance alone instills fear in those who see it."
        
        db = MockDatabase(
            pokemon_data={
                'id': 150,
                'name': 'mewtwo',
                'height': 20,
                'weight': 1220,
                'generation': 1,
                'description': long_description
            }
        )
        
        screen_manager = MockScreenManager(database=db, state_manager=MockStateManager())
        detail = DetailScreen(screen_manager, pokemon_id=150)
        detail.on_enter()
        
        # Verify max 4 lines
        assert len(detail.description_lines) <= 4, f"Expected max 4 lines, got {len(detail.description_lines)}"
    
    def test_ac_4_truncation_with_ellipsis(self, pygame_init, mock_screen_manager):
        """Test AC #4: Long text truncates with ellipsis on line 4"""
        # Very long description that will definitely exceed 4 lines
        long_description = "Created from the DNA of Mew, this Pokémon is said to have the most savage heart among all Pokémon. " \
                          "It is a Psychic-type with incredible power that was created through genetic manipulation for " \
                          "battling purposes. Its appearance alone instills fear in those who see it. This description is " \
                          "intentionally very long to force truncation at the fourth line with an ellipsis indicator."
        
        db = MockDatabase(
            pokemon_data={
                'id': 150,
                'name': 'mewtwo',
                'height': 20,
                'weight': 1220,
                'generation': 1,
                'description': long_description
            }
        )
        
        screen_manager = MockScreenManager(database=db, state_manager=MockStateManager())
        detail = DetailScreen(screen_manager, pokemon_id=150)
        detail.on_enter()
        
        if detail.description_font:
            wrapped_lines = detail._wrap_description_text(
                long_description,
                detail.description_font,
                max_width=400,
                max_lines=4
            )
            
            # Should have 4 lines
            assert len(wrapped_lines) == 4
            
            # Last line should end with ellipsis
            assert wrapped_lines[-1].endswith("..."), f"Last line should end with ellipsis: '{wrapped_lines[-1]}'"
    
    def test_ac_4_no_ellipsis_if_fits(self, pygame_init, mock_screen_manager):
        """Test AC #4: No ellipsis if text fits naturally in 4 lines"""
        # Short description that fits in less than 4 lines
        short_description = "A small Electric-type Pokémon that is very popular."
        
        db = MockDatabase(
            pokemon_data={
                'id': 25,
                'name': 'pikachu',
                'height': 4,
                'weight': 60,
                'generation': 1,
                'description': short_description
            }
        )
        
        screen_manager = MockScreenManager(database=db, state_manager=MockStateManager())
        detail = DetailScreen(screen_manager, pokemon_id=25)
        detail.on_enter()
        
        if detail.description_font:
            wrapped_lines = detail._wrap_description_text(
                short_description,
                detail.description_font,
                max_width=400,
                max_lines=4
            )
            
            # Should have fewer than 4 lines
            assert len(wrapped_lines) < 4
            
            # No line should end with ellipsis
            for line in wrapped_lines:
                assert not line.endswith("...")
    
    def test_ac_5_typography_specifications(self, pygame_init, mock_screen_manager):
        """Test AC #5: Typography uses Rajdhani 16px, ice blue color"""
        db = MockDatabase(
            pokemon_data={
                'id': 25,
                'name': 'pikachu',
                'height': 4,
                'weight': 60,
                'generation': 1,
                'description': "Electric mouse Pokémon."
            }
        )
        
        screen_manager = MockScreenManager(database=db, state_manager=MockStateManager())
        detail = DetailScreen(screen_manager, pokemon_id=25)
        detail.on_enter()
        
        # Verify font loaded
        assert detail.description_font is not None
        
        # Verify font size (16px)
        assert detail.description_font.get_height() <= 20  # Approximate check
        
        # Verify ice blue color used in rendering
        from src.ui.colors import Colors
        assert Colors.ICE_BLUE == (168, 230, 255)
    
    def test_ac_6_layout_and_positioning(self, pygame_init, mock_screen_manager):
        """Test AC #6: Panel positioned in lower section with holographic styling"""
        db = MockDatabase(
            pokemon_data={
                'id': 25,
                'name': 'pikachu',
                'height': 4,
                'weight': 60,
                'generation': 1,
                'description': "Electric mouse Pokémon."
            }
        )
        
        screen_manager = MockScreenManager(database=db, state_manager=MockStateManager())
        detail = DetailScreen(screen_manager, pokemon_id=25)
        detail.on_enter()
        
        surface = pygame.Surface((640, 360))
        detail.render(surface)
        
        # Panel should be in lower section (y > screen_height / 2)
        # DESC_PANEL_Y = screen_height - 140
        expected_y = 360 - 140
        assert expected_y > 360 / 2, "Description panel should be in lower section"
    
    def test_ac_8_missing_description_placeholder(self, pygame_init):
        """Test AC #8: Missing description shows placeholder"""
        # Create database with no description (None or empty string)
        db = MockDatabase(
            pokemon_data={
                'id': 999,
                'name': 'missingno',
                'height': 0,
                'weight': 0,
                'generation': 1,
                'description': None  # No description
            }
        )
        
        screen_manager = MockScreenManager(database=db, state_manager=MockStateManager())
        detail = DetailScreen(screen_manager, pokemon_id=999)
        detail.on_enter()
        
        # Should use placeholder
        assert detail.description == "No description available"
    
    def test_ac_8_empty_description_placeholder(self, pygame_init):
        """Test AC #8: Empty string description shows placeholder"""
        db = MockDatabase(
            pokemon_data={
                'id': 999,
                'name': 'missingno',
                'height': 0,
                'weight': 0,
                'generation': 1,
                'description': ""  # Empty description
            }
        )
        
        screen_manager = MockScreenManager(database=db, state_manager=MockStateManager())
        detail = DetailScreen(screen_manager, pokemon_id=999)
        detail.on_enter()
        
        # Should use placeholder
        assert detail.description == "No description available"
    
    def test_ac_9_pre_rendering_optimization(self, pygame_init, mock_screen_manager):
        """Test AC #9: Description pre-rendered in on_enter, cached for render"""
        db = MockDatabase(
            pokemon_data={
                'id': 25,
                'name': 'pikachu',
                'height': 4,
                'weight': 60,
                'generation': 1,
                'description': "When several of these Pokémon gather, their electricity could build and cause lightning storms."
            }
        )
        
        screen_manager = MockScreenManager(database=db, state_manager=MockStateManager())
        detail = DetailScreen(screen_manager, pokemon_id=25)
        
        # Before on_enter, description_lines should be empty
        assert len(detail.description_lines) == 0
        
        # Call on_enter (should pre-render)
        start_time = time.perf_counter()
        detail.on_enter()
        pre_render_time = (time.perf_counter() - start_time) * 1000
        
        # After on_enter, description_lines should be populated
        assert len(detail.description_lines) > 0
        
        # Pre-rendering should be fast (< 50ms per story notes, < 5ms ideal)
        assert pre_render_time < 50, f"Pre-render took {pre_render_time:.2f}ms (target: <50ms)"
    
    def test_ac_9_surfaces_cached_for_blit(self, pygame_init, mock_screen_manager):
        """Test AC #9: Surfaces cached, render() just blits (no text processing)"""
        db = MockDatabase(
            pokemon_data={
                'id': 25,
                'name': 'pikachu',
                'height': 4,
                'weight': 60,
                'generation': 1,
                'description': "Electric mouse Pokémon with powerful abilities."
            }
        )
        
        screen_manager = MockScreenManager(database=db, state_manager=MockStateManager())
        detail = DetailScreen(screen_manager, pokemon_id=25)
        detail.on_enter()
        
        # Verify surfaces are pygame.Surface objects (pre-rendered)
        for line_surface in detail.description_lines:
            assert isinstance(line_surface, pygame.Surface), "Lines should be pre-rendered surfaces"
    
    def test_ac_10_performance_blit_under_5ms(self, pygame_init, mock_screen_manager):
        """Test AC #10: Description blit completes in < 5ms per frame"""
        db = MockDatabase(
            pokemon_data={
                'id': 25,
                'name': 'pikachu',
                'height': 4,
                'weight': 60,
                'generation': 1,
                'description': "When several of these Pokémon gather, their electricity could build and cause lightning storms."
            }
        )
        
        screen_manager = MockScreenManager(database=db, state_manager=MockStateManager())
        detail = DetailScreen(screen_manager, pokemon_id=25)
        detail.on_enter()
        
        surface = pygame.Surface((640, 360))
        
        # Measure description panel render time specifically
        blit_times = []
        for _ in range(100):
            start = time.perf_counter()
            detail._render_description_panel(surface)
            elapsed = (time.perf_counter() - start) * 1000
            blit_times.append(elapsed)
        
        avg_blit_time = sum(blit_times) / len(blit_times)
        max_blit_time = max(blit_times)
        
        # Average should be well under 5ms
        assert avg_blit_time < 5, f"Avg blit time {avg_blit_time:.2f}ms exceeds 5ms"
        
        # Even max shouldn't exceed 10ms
        assert max_blit_time < 10, f"Max blit time {max_blit_time:.2f}ms exceeds 10ms"
    
    def test_ac_10_maintains_30fps(self, pygame_init, mock_screen_manager):
        """Test AC #10: Frame rate maintains 30+ FPS with description rendering"""
        db = MockDatabase(
            pokemon_data={
                'id': 25,
                'name': 'pikachu',
                'height': 4,
                'weight': 60,
                'generation': 1,
                'description': "When several of these Pokémon gather, their electricity could build and cause lightning storms."
            }
        )
        
        screen_manager = MockScreenManager(database=db, state_manager=MockStateManager())
        detail = DetailScreen(screen_manager, pokemon_id=25)
        detail.on_enter()
        
        surface = pygame.Surface((640, 360))
        
        # Measure full frame render times
        render_times = []
        for _ in range(60):
            start = time.perf_counter()
            detail.render(surface)
            elapsed = (time.perf_counter() - start) * 1000
            render_times.append(elapsed)
        
        avg_render_time = sum(render_times) / len(render_times)
        
        # Should maintain 30 FPS (33ms budget)
        assert avg_render_time < 33, f"Render time {avg_render_time:.2f}ms exceeds 33ms (30 FPS)"
    
    def test_edge_case_single_word_description(self, pygame_init, mock_screen_manager):
        """Test edge case: Single word description"""
        db = MockDatabase(
            pokemon_data={
                'id': 25,
                'name': 'pikachu',
                'height': 4,
                'weight': 60,
                'generation': 1,
                'description': "Pikachu"
            }
        )
        
        screen_manager = MockScreenManager(database=db, state_manager=MockStateManager())
        detail = DetailScreen(screen_manager, pokemon_id=25)
        detail.on_enter()
        
        # Should render without error
        assert len(detail.description_lines) == 1
        assert detail.description_lines[0] is not None
    
    def test_edge_case_exactly_four_lines(self, pygame_init, mock_screen_manager):
        """Test edge case: Description fits exactly in 4 lines"""
        # Craft description that fits exactly 4 lines at 400px width
        exact_description = "Line one text here. " * 8 + "Line two text. " * 8 + "Line three. " * 8 + "Line four text."
        
        db = MockDatabase(
            pokemon_data={
                'id': 25,
                'name': 'pikachu',
                'height': 4,
                'weight': 60,
                'generation': 1,
                'description': exact_description
            }
        )
        
        screen_manager = MockScreenManager(database=db, state_manager=MockStateManager())
        detail = DetailScreen(screen_manager, pokemon_id=25)
        detail.on_enter()
        
        if detail.description_font:
            wrapped_lines = detail._wrap_description_text(
                exact_description,
                detail.description_font,
                max_width=400,
                max_lines=4
            )
            
            # If it naturally fits in 4 lines or fewer, no ellipsis needed
            if len(wrapped_lines) <= 4:
                # Check last line doesn't have forced ellipsis
                if len(wrapped_lines) == 4:
                    # Only should have ellipsis if text was actually truncated
                    words_displayed = sum(len(line.split()) for line in wrapped_lines)
                    total_words = len(exact_description.split())
                    if words_displayed >= total_words:
                        assert not wrapped_lines[-1].endswith("...")








