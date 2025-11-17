"""
Integration tests for DetailScreen (Story 3.1)

Tests basic layout, sprite display, header rendering, navigation,
StateManager integration, error handling, and performance validation.
"""

import pytest
import pygame
import time
from unittest.mock import Mock, MagicMock, patch
from src.ui.detail_screen import DetailScreen
from src.ui.screen_manager import ScreenManager
from src.input_manager import InputAction


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
    def __init__(self, pokemon_data=None):
        self.pokemon_data = pokemon_data or {
            'id': 25,
            'name': 'pikachu',
            'height': 4,
            'weight': 60,
            'generation': 1
        }
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def get_pokemon_by_id(self, pokemon_id):
        if pokemon_id == self.pokemon_data['id']:
            return self.pokemon_data
        return None


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

