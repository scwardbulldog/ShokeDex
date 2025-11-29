"""
Home Screen for ShokeDex - Grid view of Pokémon
"""

import logging
import os
from typing import List, Optional, Tuple

import pygame

from .screen import Screen
from .colors import Colors
from ..input_manager import InputAction
from .sprite_loader import load_thumb
from ..performance_monitor import PerformanceMonitor

# Module logger
logger = logging.getLogger(__name__)

# Generation constants
GENERATION_NAMES = {
    1: "KANTO",
    2: "JOHTO",
    3: "HOENN"
}

GENERATION_RANGES = {
    1: (1, 151),    # Kanto: Bulbasaur to Mew
    2: (152, 251),  # Johto: Chikorita to Celebi
    3: (252, 386)   # Hoenn: Treecko to Deoxys
}

GENERATION_TOTALS = {
    1: 151,
    2: 100,
    3: 135
}


class GenerationBadge:
    """
    Visual component displaying current generation with logo and position counter.
    
    Shows region name (KANTO/JOHTO/HOENN) with optional logo icon and
    position counter in format #XXX/YYY.
    """
    
    def __init__(self, generation: int, pokemon_id: int):
        """
        Initialize generation badge.
        
        Args:
            generation: 1 (Kanto), 2 (Johto), or 3 (Hoenn)
            pokemon_id: Current Pokemon National Dex number
        """
        self.generation = generation
        self.pokemon_id = pokemon_id
        self.logo_surface: Optional[pygame.Surface] = None
        
        # Glow effect state (Story 1.4)
        self.active_glow = False
        self.glow_timer = 0.0  # milliseconds remaining
        
        # Try to load generation logo
        self._load_logo()
        
        # Initialize fonts (will be set by parent screen)
        self.name_font: Optional[pygame.font.Font] = None
        self.counter_font: Optional[pygame.font.Font] = None
    
    def _load_logo(self):
        """Load generation logo asset with fallback to text-only."""
        logo_paths = {
            1: "assets/icons/badge_kanto.png",
            2: "assets/icons/badge_johto.png",
            3: "assets/icons/badge_hoenn.png"
        }
        
        if self.generation not in logo_paths:
            return
        
        logo_path = logo_paths[self.generation]
        
        try:
            if os.path.exists(logo_path):
                self.logo_surface = pygame.image.load(logo_path).convert_alpha()
                # Scale to 40x40px
                self.logo_surface = pygame.transform.smoothscale(self.logo_surface, (40, 40))
        except Exception as e:
            print(f"Warning: Generation badge asset not found: {logo_path} - {e}")
            self.logo_surface = None
    
    def update(self, pokemon_id: int):
        """Update position counter when Pokemon changes."""
        self.pokemon_id = pokemon_id
    
    def update_glow(self, delta_time: float):
        """
        Update glow animation timer.
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        if self.glow_timer > 0:
            self.glow_timer -= delta_time * 1000  # Convert to milliseconds
            self.active_glow = True
        else:
            self.active_glow = False
            self.glow_timer = 0
    
    def trigger_glow(self, duration_ms: float = 300):
        """
        Trigger badge glow effect for specified duration.
        
        Args:
            duration_ms: Duration in milliseconds (default 300ms)
        """
        self.glow_timer = duration_ms
        self.active_glow = True
    
    def set_generation(self, generation: int, pokemon_id: int):
        """Update generation and reload logo if needed."""
        if generation != self.generation:
            self.generation = generation
            self.pokemon_id = pokemon_id
            self._load_logo()
    
    def render(self, surface: pygame.Surface, x: int, y: int):
        """
        Render badge to surface at specified position.
        
        Args:
            surface: pygame Surface to render on
            x: X coordinate (top-left corner)
            y: Y coordinate (top-left corner)
        """
        # Badge dimensions
        badge_width = 220
        badge_height = 50
        
        # Create badge background with transparency
        badge_surface = pygame.Surface((badge_width, badge_height), pygame.SRCALPHA)
        
        # Draw background (dark blue with transparency)
        bg_color = (*Colors.DARK_BLUE, 230)  # rgba(26, 47, 74, 0.9)
        pygame.draw.rect(badge_surface, bg_color, (0, 0, badge_width, badge_height))
        
        # Draw glow effect if active (Story 1.4)
        if self.active_glow:
            # Bright cyan glow color
            glow_color = Colors.BRIGHT_CYAN  # #4df7ff
            
            # Draw outer glow border (3px wide)
            pygame.draw.rect(badge_surface, glow_color, (0, 0, badge_width, badge_height), 3)
            
            # Draw semi-transparent glow aura layers for depth
            for offset, alpha in [(8, 60), (5, 100), (3, 140)]:
                glow_rect = pygame.Rect(-offset, -offset, 
                                       badge_width + offset*2, badge_height + offset*2)
                glow_layer = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                glow_layer.fill((*glow_color, alpha))
                badge_surface.blit(glow_layer, (glow_rect.x, glow_rect.y), special_flags=pygame.BLEND_ADD)
        else:
            # Draw 2px electric blue border (normal state)
            pygame.draw.rect(badge_surface, Colors.ELECTRIC_BLUE, (0, 0, badge_width, badge_height), 2)
        
        # Draw corner accent lines (45° cuts)
        accent_length = 10
        border_color = Colors.BRIGHT_CYAN if self.active_glow else Colors.ELECTRIC_BLUE
        # Top-left corner
        pygame.draw.line(badge_surface, border_color, (2, accent_length), (accent_length, 2), 2)
        # Top-right corner
        pygame.draw.line(badge_surface, border_color, 
                        (badge_width - accent_length, 2), (badge_width - 2, accent_length), 2)
        # Bottom-left corner
        pygame.draw.line(badge_surface, border_color,
                        (2, badge_height - accent_length), (accent_length, badge_height - 2), 2)
        # Bottom-right corner
        pygame.draw.line(badge_surface, border_color,
                        (badge_width - accent_length, badge_height - 2), 
                        (badge_width - 2, badge_height - accent_length), 2)
        
        # Calculate content positioning
        content_x = 10
        
        # Draw logo if available
        if self.logo_surface:
            badge_surface.blit(self.logo_surface, (content_x, 5))
            content_x += 45  # Logo width + spacing
        
        # Draw generation name
        if self.name_font:
            try:
                gen_name = GENERATION_NAMES[self.generation]
                color = Colors.HOLOGRAM_WHITE
                # Recreate font fresh to avoid NULL pointer issues
                temp_font = pygame.font.Font(None, 24)
                name_text = temp_font.render(
                    gen_name,
                    True,
                    color
                )
                badge_surface.blit(name_text, (content_x, 8))
            except Exception as e:
                logger.warning("Could not render generation name: %s", e)
        
        # Draw position counter
        if self.counter_font:
            try:
                total = GENERATION_TOTALS[self.generation]
                # Recreate font fresh to avoid NULL pointer issues
                temp_font = pygame.font.Font(None, 18)
                counter_text = temp_font.render(
                    f"#{self.pokemon_id:03d}/{total:03d}",
                    True,
                    Colors.ICE_BLUE
                )
                badge_surface.blit(counter_text, (content_x, 28))
            except Exception as e:
                logger.warning("Could not render position counter: %s", e)
        
        # Blit badge to main surface
        surface.blit(badge_surface, (x, y))


class HomeScreen(Screen):
    """
    Home screen showing a grid of Pokémon thumbnails.
    
    Displays Pokémon in a grid layout with sprite thumbnails and names.
    """
    
    def __init__(self, screen_manager, database=None):
        """
        Initialize HomeScreen.
        
        Args:
            screen_manager: ScreenManager instance
            database: Database instance (optional, for loading Pokemon data)
        """
        super().__init__(screen_manager)
        self.database = database
        
        # Grid configuration
        self.grid_cols = 4
        self.grid_rows = 3
        self.items_per_page = self.grid_cols * self.grid_rows
        
        # Selection state
        self.selected_index = 0
        self.page = 0
        
        # Pokemon data
        self.pokemon_list: List[dict] = []
        self.filtered_list: List[dict] = []
        self.total_pokemon = 0
        
        # Search state
        self.search_active = False
        self.search_query = ""
        
        # Favorites (stub - will be loaded from settings/database later)
        self.favorites: set = set()
        self.recent_views: List[int] = []  # Pokemon IDs
        
        # View mode (all, favorites, recent)
        self.view_mode = "all"  # Can be "all", "favorites", "recent"
        
        # Generation navigation
        self.current_generation = 1  # Default to Kanto
        self.generation_badge: Optional[GenerationBadge] = None
        
        # Transition state (Story 1.4)
        self.is_transitioning = False
        self.transition_timer = 0.0
        self.transition_alpha = 255
        self.pending_generation = None
        
        # Hold-to-scroll state (Story 1.6)
        self.button_hold_time = {
            InputAction.UP: 0.0,
            InputAction.DOWN: 0.0
        }
        self.active_button = None
        self.scroll_speed = 1  # Pokemon per frame during hold
        
        # Sprite transition state (Story 1.6)
        self.sprite_transition_state = None  # None, "fade-out", "loading", "fade-in"
        self.sprite_transition_timer = 0.0
        self.sprite_alpha = 255
        self.target_pokemon_index = None
        
        # Fonts (will be initialized in on_enter)
        self.title_font: Optional[pygame.font.Font] = None
        self.text_font: Optional[pygame.font.Font] = None
        self.small_font: Optional[pygame.font.Font] = None
        self.badge_name_font: Optional[pygame.font.Font] = None
        self.badge_counter_font: Optional[pygame.font.Font] = None
        
        # Layout dimensions (for 480x320 display)
        self.cell_width = 120
        self.cell_height = 75  # Reduced from 90 to prevent overlap with bottom status bar
        self.grid_start_y = 70  # Buffer below badge/search bar (was 60)
        
        # Performance monitoring (Story 1.7)
        self.performance_monitor = PerformanceMonitor(history_size=100)
        self.fps_warning_count = 0  # Track consecutive low FPS frames
        
    def on_enter(self):
        """Called when screen becomes active."""
        super().on_enter()
        
        # Ensure pygame font is initialized
        if not pygame.font.get_init():
            pygame.font.init()
        
        # Initialize fonts with custom typefaces
        # Try to load Orbitron Bold for generation name
        try:
            self.badge_name_font = pygame.font.Font("assets/fonts/Orbitron-Bold.ttf", 24)
        except Exception:
            self.badge_name_font = pygame.font.Font(None, 24)
        
        # Try to load Share Tech Mono for counter
        try:
            self.badge_counter_font = pygame.font.Font("assets/fonts/ShareTechMono-Regular.ttf", 18)
        except Exception:
            self.badge_counter_font = pygame.font.Font(None, 18)
        
        # Use None for all other fonts (pygame default - most reliable)
        self.title_font = pygame.font.Font(None, 32)
        self.text_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 16)
        
        # Load state from StateManager (Story 1.5: State Persistence)
        if hasattr(self.screen_manager, 'state_manager') and self.screen_manager.state_manager:
            self.current_generation = self.screen_manager.state_manager.get_last_viewed_generation()
            last_pokemon_id = self.screen_manager.state_manager.get_last_viewed_id()
        else:
            # No state manager available (test environment) - use defaults
            last_pokemon_id = 1
        
        # Load Pokemon data for current generation
        self._load_pokemon_by_generation(self.current_generation)
        
        # Find the last viewed Pokemon in the loaded list and set selected_index
        if self.pokemon_list:
            found_index = None
            for i, pokemon in enumerate(self.pokemon_list):
                if pokemon['id'] == last_pokemon_id:
                    found_index = i
                    break
            
            if found_index is not None:
                self.selected_index = found_index
                # Calculate correct page for this selection
                self.page = found_index // self.items_per_page
            else:
                # Pokemon not in current generation - default to first
                self.selected_index = 0
                self.page = 0
            
            first_pokemon_id = self.pokemon_list[self.selected_index]['id']
        else:
            first_pokemon_id = 1
        
        # Initialize generation badge with correct Pokemon ID
        self.generation_badge = GenerationBadge(self.current_generation, first_pokemon_id)
        
        # Assign fonts to badge - verify they're valid first
        if self.badge_name_font:
            self.generation_badge.name_font = self.badge_name_font
            
        if self.badge_counter_font:
            self.generation_badge.counter_font = self.badge_counter_font
    
    def on_exit(self):
        """Called when screen becomes inactive - save state."""
        super().on_exit()
        
        # Save current state to StateManager (Story 1.5: State Persistence)
        if hasattr(self.screen_manager, 'state_manager') and self.screen_manager.state_manager:
            # Get current Pokemon ID from selected index
            if self.pokemon_list and 0 <= self.selected_index < len(self.pokemon_list):
                current_pokemon_id = self.pokemon_list[self.selected_index]['id']
                
                try:
                    # Save last viewed Pokemon and generation
                    self.screen_manager.state_manager.set_last_viewed(
                        current_pokemon_id,
                        self.current_generation
                    )
                    self.screen_manager.state_manager.save_state()
                except Exception as e:
                    # Don't crash on save failure - just log it
                    print(f"Warning: Failed to save state: {e}")
    
    def _load_pokemon_by_generation(self, generation: int):
        """
        Load Pokemon for specified generation from database.
        
        Args:
            generation: Generation number (1, 2, or 3)
        """
        if self.database:
            try:
                with self.database as db:
                    # Get Pokemon filtered by generation using ID ranges
                    pokemon_data = db.get_pokemon_by_generation(generation)
                    self.pokemon_list = [
                        {'id': p['id'], 'name': p['name']}
                        for p in pokemon_data
                    ]
                    self.total_pokemon = len(self.pokemon_list)
            except ValueError as e:
                # Invalid generation parameter
                print(f"Error: {e}")
                self.pokemon_list = []
                self.total_pokemon = 0
            except Exception as e:
                print(f"Error loading Pokemon for generation {generation}: {e}")
                self.pokemon_list = []
                self.total_pokemon = 0
        else:
            # Demo data if no database - use generation ranges
            if generation not in GENERATION_RANGES:
                # Invalid generation even for demo mode
                print(f"Error: Invalid generation {generation}")
                self.pokemon_list = []
                self.total_pokemon = 0
            else:
                start_id, end_id = GENERATION_RANGES[generation]
                self.pokemon_list = [
                    {'id': i, 'name': f"Pokemon {i}"}
                    for i in range(start_id, end_id + 1)
                ]
                self.total_pokemon = len(self.pokemon_list)
        
        # Initialize filtered list
        self._apply_filters()
    
    def _load_pokemon(self):
        """
        DEPRECATED: Use _load_pokemon_by_generation() instead.
        
        Load Pokemon data from database.
        This method loads all Pokemon and is kept for backwards compatibility.
        """
        if self.database:
            try:
                with self.database as db:
                    # Get all Pokemon, ordered by ID
                    cursor = db.execute(
                        "SELECT id, name FROM pokemon ORDER BY id"
                    )
                    self.pokemon_list = [
                        {'id': row[0], 'name': row[1]}
                        for row in cursor.fetchall()
                    ]
                    self.total_pokemon = len(self.pokemon_list)
            except Exception as e:
                print(f"Error loading Pokemon: {e}")
                self.pokemon_list = []
                self.total_pokemon = 0
        else:
            # Demo data if no database
            self.pokemon_list = [
                {'id': i, 'name': f"Pokemon {i}"}
                for i in range(1, 151)
            ]
            self.total_pokemon = len(self.pokemon_list)
        
        # Initialize filtered list
        self._apply_filters()
    
    def _apply_filters(self):
        """Apply current search and view filters to Pokemon list."""
        # Start with full list
        result = self.pokemon_list
        
        # Apply view mode filter
        if self.view_mode == "favorites" and self.favorites:
            result = [p for p in result if p['id'] in self.favorites]
        elif self.view_mode == "recent" and self.recent_views:
            # Show recent views in order
            result = [p for p in result if p['id'] in self.recent_views]
            result.sort(key=lambda p: self.recent_views.index(p['id']))
        
        # Apply search filter
        if self.search_query:
            query_lower = self.search_query.lower()
            result = [
                p for p in result
                if query_lower in p['name'].lower() or
                   query_lower in str(p['id'])
            ]
        
        self.filtered_list = result
        self.total_pokemon = len(result)
        
        # Reset selection if out of bounds
        if self.selected_index >= self.total_pokemon and self.total_pokemon > 0:
            self.selected_index = 0
            self.page = 0
    
    def _switch_generation(self, direction: int):
        """
        Switch to next or previous generation with circular wrapping and fade transitions.
        
        Implements visual fade-out → load → fade-in transition as specified in Story 1.4.
        
        Args:
            direction: 1 for next generation (R button), -1 for previous (L button)
        """
        # Start fade-out transition
        self.is_transitioning = True
        self.transition_timer = 0.0
        self.transition_alpha = 255
        
        # Calculate new generation with wrapping (1 -> 2 -> 3 -> 1)
        new_generation = ((self.current_generation + direction - 1) % 3) + 1
        self.pending_generation = new_generation
        
        # Note: Actual generation switch happens in update() during transition
        # This allows smooth fade animation without blocking
    
    def handle_input(self, action: InputAction):
        """Handle input actions."""
        # If search is active, handle search-specific input
        if self.search_active:
            if action == InputAction.BACK:
                # Clear search or deactivate
                if self.search_query:
                    self.search_query = ""
                    self._apply_filters()
                else:
                    self.search_active = False
                return
            # For actual typing, we'd need text input events
            # This is handled in the render loop for now
            return
        
        # Story 1.6: Single-Pokemon scrolling with Up/Down
        if action == InputAction.UP:
            self.active_button = InputAction.UP
            self.button_hold_time[InputAction.UP] = 0.0  # Reset on new press
            self._handle_selection_change(-1)
        elif action == InputAction.DOWN:
            self.active_button = InputAction.DOWN
            self.button_hold_time[InputAction.DOWN] = 0.0  # Reset on new press
            self._handle_selection_change(1)
        elif action == InputAction.LEFT:
            # L button: Previous generation (Story 1.4)
            self._switch_generation(-1)
        elif action == InputAction.RIGHT:
            # R button: Next generation (Story 1.4)
            self._switch_generation(1)
        elif action == InputAction.SELECT:
            self._select_pokemon()
        elif action == InputAction.START:
            self._open_settings()
    
    def handle_input_release(self, action: InputAction):
        """Handle input release events (key up).
        
        Args:
            action: The input action that was released
        """
        # Reset hold state when button is released
        if action in [InputAction.UP, InputAction.DOWN]:
            if self.active_button == action:
                self.active_button = None
                self.scroll_speed = 1
    
    def _handle_selection_change(self, delta: int):
        """Handle single-Pokemon navigation with boundary wrapping (Story 1.6).
        
        Args:
            delta: +1 for down/next, -1 for up/previous
        """
        if not self.pokemon_list:
            return
        
        # Apply delta with modulo wrapping (stays within current generation)
        self.selected_index = (self.selected_index + delta) % len(self.pokemon_list)
        
        # Update page to match new selection
        self.page = self.selected_index // self.items_per_page
        
        # Get current Pokemon ID
        if 0 <= self.selected_index < len(self.pokemon_list):
            current_pokemon = self.pokemon_list[self.selected_index]
            pokemon_id = current_pokemon['id']
            
            # Update generation badge position counter
            if self.generation_badge:
                self.generation_badge.update(pokemon_id)
            
            # Save to StateManager
            if hasattr(self.screen_manager, 'state_manager') and self.screen_manager.state_manager:
                try:
                    self.screen_manager.state_manager.set_last_viewed(
                        pokemon_id=pokemon_id,
                        generation=self.current_generation
                    )
                except Exception as e:
                    # Don't crash on state save failure
                    print(f"Warning: Failed to update last viewed state: {e}")
            
            # Start sprite transition if not in fast scroll mode
            if self.scroll_speed == 1:
                self._start_sprite_transition(self.selected_index)
    
    def _start_sprite_transition(self, target_index: int):
        """Start smooth sprite fade transition (Story 1.6).
        
        Args:
            target_index: Index of Pokemon to transition to
        """
        self.sprite_transition_state = "fade-out"
        self.sprite_transition_timer = 0.0
        self.sprite_alpha = 255
        self.target_pokemon_index = target_index
    
    def _move_selection(self, delta: int):
        """DEPRECATED: Use _handle_selection_change() instead.
        
        Move selection by delta positions (old grid-based navigation).
        Kept for backwards compatibility with existing code.
        """
        new_index = self.selected_index + delta
        
        # Clamp to valid range
        max_index = min(self.total_pokemon - 1, (self.page + 1) * self.items_per_page - 1)
        min_index = self.page * self.items_per_page
        
        if new_index < min_index:
            # Move to previous page
            if self.page > 0:
                self.page -= 1
                self.selected_index = new_index + self.items_per_page
        elif new_index > max_index:
            # Move to next page
            if (self.page + 1) * self.items_per_page < self.total_pokemon:
                self.page += 1
                self.selected_index = new_index - self.items_per_page
        else:
            self.selected_index = new_index
        
        # Final clamp
        self.selected_index = max(0, min(self.selected_index, self.total_pokemon - 1))
        
        # Update generation badge with current Pokemon ID
        if 0 <= self.selected_index < self.total_pokemon:
            current_pokemon = self.filtered_list[self.selected_index]
            if self.generation_badge:
                self.generation_badge.update(current_pokemon['id'])
    
    def _select_pokemon(self):
        """Handle Pokemon selection."""
        if 0 <= self.selected_index < self.total_pokemon:
            pokemon = self.filtered_list[self.selected_index]
            
            # Add to recent views
            if pokemon['id'] not in self.recent_views:
                self.recent_views.insert(0, pokemon['id'])
                # Keep only last 12 recent views
                self.recent_views = self.recent_views[:12]
            elif pokemon['id'] in self.recent_views:
                # Move to front if already in list
                self.recent_views.remove(pokemon['id'])
                self.recent_views.insert(0, pokemon['id'])
            
            # Lazy import to avoid circular dependency
            # DetailScreen -> ScreenManager -> HomeScreen cycle
            from .detail_screen import DetailScreen
            
            detail_screen = DetailScreen(
                self.screen_manager,
                pokemon_id=pokemon['id']
            )
            self.screen_manager.push(detail_screen)
    
    def _open_settings(self):
        """Open settings screen."""
        from .settings_screen import SettingsScreen
        
        settings_screen = SettingsScreen(self.screen_manager)
        self.screen_manager.push(settings_screen)
    
    def update(self, delta_time: float):
        """Update screen state."""
        # Record frame for performance monitoring (Story 1.7: AC #1, #5)
        self.performance_monitor.record_frame()
        self.performance_monitor.record_cpu_memory()
        
        # Check FPS and log warnings if performance degrades (Story 1.7: AC #1)
        stats = self.performance_monitor.get_stats()
        if stats['fps_avg'] < 30.0 and len(self.performance_monitor.fps_history) >= 90:  # 3 seconds at 30 FPS
            self.fps_warning_count += 1
            if self.fps_warning_count == 1:  # Log only on first detection
                print(f"⚠️ Performance Warning: FPS dropped to {stats['fps_avg']:.1f} (target: 30+ FPS)")
        else:
            self.fps_warning_count = 0  # Reset when FPS recovers
        
        # Update generation badge glow timer
        if self.generation_badge:
            self.generation_badge.update_glow(delta_time)
        
        # Handle hold-to-scroll acceleration (Story 1.6)
        if self.active_button in [InputAction.UP, InputAction.DOWN]:
            self.button_hold_time[self.active_button] += delta_time
            
            # Check for acceleration threshold
            hold_duration = self.button_hold_time[self.active_button]
            
            if hold_duration >= 1.0:
                # Turbo mode: 5 Pokemon per frame
                self.scroll_speed = 5
            elif hold_duration >= 0.5:
                # Fast mode: 3 Pokemon per frame
                self.scroll_speed = 3
            else:
                # Normal mode: 1 Pokemon per press
                self.scroll_speed = 1
            
            # Apply accelerated scrolling during hold
            if self.scroll_speed > 1 and self.pokemon_list:
                delta = 1 if self.active_button == InputAction.DOWN else -1
                
                # Scroll multiple Pokemon per frame
                for _ in range(self.scroll_speed - 1):  # -1 because initial press already moved once
                    self.selected_index = (self.selected_index + delta) % len(self.pokemon_list)
                
                # Update display after fast scroll
                self.page = self.selected_index // self.items_per_page
                
                if 0 <= self.selected_index < len(self.pokemon_list):
                    current_pokemon = self.pokemon_list[self.selected_index]
                    if self.generation_badge:
                        self.generation_badge.update(current_pokemon['id'])
                    
                    # Save state during fast scroll
                    if hasattr(self.screen_manager, 'state_manager') and self.screen_manager.state_manager:
                        try:
                            self.screen_manager.state_manager.set_last_viewed(
                                pokemon_id=current_pokemon['id'],
                                generation=self.current_generation
                            )
                        except Exception:
                            pass
        else:
            # Button released - reset scroll speed
            self.scroll_speed = 1
        
        # Handle sprite transition animation (Story 1.6)
        if self.sprite_transition_state is not None:
            self.sprite_transition_timer += delta_time
            
            if self.sprite_transition_state == "fade-out":
                # Fade out over 100ms
                if self.sprite_transition_timer < 0.1:
                    self.sprite_alpha = int(255 * (1 - self.sprite_transition_timer / 0.1))
                else:
                    # Transition to loading state
                    self.sprite_transition_state = "loading"
                    self.sprite_transition_timer = 0.0
                    self.sprite_alpha = 0
            
            elif self.sprite_transition_state == "loading":
                # Instant transition to fade-in (sprite loading happens in render)
                self.sprite_transition_state = "fade-in"
                self.sprite_transition_timer = 0.0
            
            elif self.sprite_transition_state == "fade-in":
                # Fade in over 100ms
                if self.sprite_transition_timer < 0.1:
                    self.sprite_alpha = int(255 * (self.sprite_transition_timer / 0.1))
                else:
                    # Transition complete
                    self.sprite_transition_state = None
                    self.sprite_alpha = 255
                    self.target_pokemon_index = None
        
        # Handle generation switch transition (Story 1.4)
        if self.is_transitioning:
            self.transition_timer += delta_time
            
            # Phase 1: Fade out (0-0.1s)
            if self.transition_timer < 0.1:
                # Linear fade from 255 to 0
                self.transition_alpha = int(255 * (1 - self.transition_timer / 0.1))
            
            # Phase 2: Switch generation at 0.1s mark (execute only once)
            elif self.transition_timer >= 0.1 and self.pending_generation is not None:
                # Perform the actual generation switch
                self.current_generation = self.pending_generation
                self.pending_generation = None  # Clear to prevent re-execution
                
                # Update generation badge
                if self.generation_badge:
                    start_id, _ = GENERATION_RANGES[self.current_generation]
                    self.generation_badge.set_generation(self.current_generation, start_id)
                    # Trigger badge glow effect
                    self.generation_badge.trigger_glow(300)
                
                # Reset scroll position and hold state
                self.selected_index = 0
                self.page = 0
                self.active_button = None
                self.scroll_speed = 1
                self.button_hold_time = {InputAction.UP: 0.0, InputAction.DOWN: 0.0}
                
                # Reload Pokemon list for new generation
                self._load_pokemon_by_generation(self.current_generation)
                
                # Save to state manager
                if hasattr(self.screen_manager, 'state_manager') and self.screen_manager.state_manager and self.pokemon_list:
                    first_pokemon_id = self.pokemon_list[0]['id']
                    self.screen_manager.state_manager.set_last_viewed(
                        pokemon_id=first_pokemon_id,
                        generation=self.current_generation
                    )
            
            # Phase 3: Fade in (0.1-0.2s) - happens after switch
            if self.transition_timer >= 0.1 and self.transition_timer < 0.2:
                # Linear fade from 0 to 255
                fade_progress = (self.transition_timer - 0.1) / 0.1
                self.transition_alpha = int(255 * fade_progress)
            
            # Phase 4: Complete transition (>= 0.2s)
            elif self.transition_timer >= 0.2:
                self.is_transitioning = False
                self.transition_alpha = 255
                self.transition_timer = 0.0
    
    def render(self, surface: pygame.Surface):
        """Render the screen."""
        # Clear background (holographic theme - AC #1)
        surface.fill(Colors.DEEP_SPACE_BLACK)
        
        # Draw generation badge (top-left position)
        if self.generation_badge:
            self.generation_badge.render(surface, 10, 10)
        
        # Draw search/filter bar
        self._render_search_bar(surface)
        
        # Apply transition alpha if transitioning
        if self.is_transitioning and self.transition_alpha < 255:
            # Create a copy surface for alpha blending
            content_surface = pygame.Surface((480, 320), pygame.SRCALPHA)
            content_surface.fill((0, 0, 0, 0))  # Transparent
            
            # Render grid to content surface
            self._render_grid(content_surface)
            
            # Apply alpha to content surface
            content_surface.set_alpha(self.transition_alpha)
            surface.blit(content_surface, (0, 0))
        else:
            # Normal rendering without alpha
            self._render_grid(surface)
        
        # Draw page indicator and view mode (holographic ice blue - AC #5)
        # Status bar at bottom of screen (y=305 leaves room below 285px grid)
        status_y = 305
        total_pages = max(1, (self.total_pokemon + self.items_per_page - 1) // self.items_per_page)
        page_text = self.small_font.render(
            f"Page {self.page + 1}/{total_pages}",
            True,
            Colors.ICE_BLUE
        )
        surface.blit(page_text, (10, status_y))
        
        # Draw view mode indicator (holographic ice blue - AC #5)
        view_mode_text = f"View: {self.view_mode.capitalize()}"
        if self.search_query:
            view_mode_text += f" (Search: {self.search_query})"
        mode_render = self.small_font.render(
            view_mode_text,
            True,
            Colors.ICE_BLUE
        )
        surface.blit(mode_render, (140, status_y))
        
        # Draw help text (holographic ice blue - AC #5)
        help_text = self.small_font.render(
            "SELECT: View | START: Settings",
            True,
            Colors.ICE_BLUE
        )
        help_rect = help_text.get_rect(right=470, top=status_y)
        surface.blit(help_text, help_rect)
    
    def _render_search_bar(self, surface: pygame.Surface):
        """Render search/filter bar."""
        bar_y = 35
        bar_height = 18
        
        # Draw search indicator
        # Search icon with holographic styling (AC #6)
        search_icon = "🔍" if self.search_query or self.search_active else "⊡"
        search_text = self.small_font.render(
            f"{search_icon} {self.search_query}",
            True,
            Colors.HOLOGRAM_WHITE if self.search_active else Colors.ICE_BLUE
        )
        surface.blit(search_text, (10, bar_y))
        
        # Draw view mode buttons with holographic styling (AC #6)
        button_x = 280
        button_width = 60
        for mode in ["all", "recent", "fav"]:
            is_active = (self.view_mode == mode or 
                        (mode == "fav" and self.view_mode == "favorites"))
            
            btn_rect = pygame.Rect(button_x, bar_y - 2, button_width, bar_height)
            
            # Draw button background (holographic - AC #6)
            if is_active:
                pygame.draw.rect(surface, Colors.DARK_BLUE, btn_rect)
            pygame.draw.rect(surface, Colors.ELECTRIC_BLUE, btn_rect, 2)
            
            # Draw button text (holographic - white active, ice blue inactive)
            btn_color = Colors.HOLOGRAM_WHITE if is_active else Colors.ICE_BLUE
            mode_name = "Fav" if mode == "fav" else mode.capitalize()
            btn_text = self.small_font.render(mode_name, True, btn_color)
            btn_text_rect = btn_text.get_rect(center=btn_rect.center)
            surface.blit(btn_text, btn_text_rect)
            
            button_x += button_width + 5
    
    def _render_grid(self, surface: pygame.Surface):
        """Render the Pokemon grid."""
        if self.total_pokemon == 0:
            # Show "no results" message (holographic ice blue)
            no_results = self.text_font.render(
                "No Pokémon found",
                True,
                Colors.ICE_BLUE
            )
            no_results_rect = no_results.get_rect(center=(240, 160))
            surface.blit(no_results, no_results_rect)
            return
        
        start_idx = self.page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, self.total_pokemon)
        
        for i in range(start_idx, end_idx):
            relative_idx = i - start_idx
            row = relative_idx // self.grid_cols
            col = relative_idx % self.grid_cols
            
            # Calculate cell position
            x = col * self.cell_width
            y = self.grid_start_y + row * self.cell_height
            
            # Get Pokemon data
            pokemon = self.filtered_list[i]
            
            # Check if favorited or recently viewed
            is_favorite = pokemon['id'] in self.favorites
            is_recent = pokemon['id'] in self.recent_views
            
            # Determine if this cell is selected
            is_selected = (i == self.selected_index)
            
            # Draw cell
            self._render_cell(surface, pokemon, x, y, is_selected, is_favorite, is_recent)
    
    def _render_cell(
        self,
        surface: pygame.Surface,
        pokemon: dict,
        x: int,
        y: int,
        is_selected: bool,
        is_favorite: bool = False,
        is_recent: bool = False
    ):
        """Render a single grid cell with holographic styling."""
        rect = pygame.Rect(x + 2, y + 2, self.cell_width - 4, self.cell_height - 4)
        
        # Draw cell border (AC #2) - ELECTRIC_BLUE for all cells
        pygame.draw.rect(surface, Colors.ELECTRIC_BLUE, rect, 2)
        
        # Draw selection background and highlight border (AC #3)
        if is_selected:
            # Fill with DARK_BLUE background for selection
            inner_rect = pygame.Rect(x + 4, y + 4, self.cell_width - 8, self.cell_height - 8)
            pygame.draw.rect(surface, Colors.DARK_BLUE, inner_rect)
            # Bright cyan border for selected cell
            pygame.draw.rect(surface, Colors.BRIGHT_CYAN, rect, 2)
        
        # Draw favorite/recent indicator
        if is_favorite:
            fav_text = self.small_font.render("★", True, Colors.YELLOW)
            surface.blit(fav_text, (x + 5, y + 3))
        elif is_recent:
            recent_text = self.small_font.render("•", True, Colors.LIGHT_BLUE)
            surface.blit(recent_text, (x + 5, y + 3))
        
        # Draw sprite placeholder (centered in cell)
        sprite_size = 48
        sprite_x = x + (self.cell_width - sprite_size) // 2
        sprite_y = y + 10
        sprite_rect = pygame.Rect(sprite_x, sprite_y, sprite_size, sprite_size)
        
        # Draw sprite border (holographic styling)
        border_color = Colors.BRIGHT_CYAN if is_selected else Colors.ELECTRIC_BLUE
        pygame.draw.rect(surface, border_color, sprite_rect, 1)

        # Attempt to load and draw thumbnail
        try:
            thumb_surf = load_thumb(pokemon['id'])
            if thumb_surf:
                try:
                    if thumb_surf.get_size() != (sprite_size, sprite_size):
                        thumb_surf = pygame.transform.smoothscale(thumb_surf, (sprite_size, sprite_size))
                except Exception:
                    pass

                surface.blit(thumb_surf, (sprite_x, sprite_y))
            else:
                # Draw Pokemon ID (in sprite area as fallback)
                id_text = self.small_font.render(
                    f"#{pokemon['id']:03d}",
                    True,
                    Colors.ICE_BLUE
                )
                id_rect = id_text.get_rect(center=sprite_rect.center)
                surface.blit(id_text, id_rect)
        except Exception:
            # On any error (pygame missing, load fail), draw ID placeholder
            id_text = self.small_font.render(
                f"#{pokemon['id']:03d}",
                True,
                Colors.ICE_BLUE
            )
            id_rect = id_text.get_rect(center=sprite_rect.center)
            surface.blit(id_text, id_rect)
        
        # Draw Pokemon name (holographic white for all - readable against DARK_BLUE selection)
        name_text = self.small_font.render(
            pokemon['name'].capitalize(),
            True,
            Colors.HOLOGRAM_WHITE
        )
        name_rect = name_text.get_rect(centerx=x + self.cell_width // 2, top=y + 58)
        surface.blit(name_text, name_rect)
