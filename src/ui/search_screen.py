"""
Search Screen for ShokeDex - Incremental search functionality
"""

import pygame
from typing import List, Optional
from .screen import Screen
from .colors import Colors
from ..input_manager import InputAction


class SearchScreen(Screen):
    """
    Search screen with incremental search and live results.
    
    Provides text input and displays matching Pokemon in real-time.
    """
    
    def __init__(self, screen_manager, database=None):
        """
        Initialize SearchScreen.
        
        Args:
            screen_manager: ScreenManager instance
            database: Database instance (optional)
        """
        super().__init__(screen_manager)
        self.database = database
        
        # Search state
        self.search_query = ""
        self.results: List[dict] = []
        self.selected_index = 0
        
        # All Pokemon (for searching)
        self.all_pokemon: List[dict] = []
        
        # Fonts
        self.title_font: Optional[pygame.font.Font] = None
        self.text_font: Optional[pygame.font.Font] = None
        self.small_font: Optional[pygame.font.Font] = None
        
        # Layout
        self.results_start_y = 80
        self.item_height = 30
        self.max_visible_results = 7
    
    def on_enter(self):
        """Called when screen becomes active."""
        super().on_enter()
        
        # Initialize fonts
        self.title_font = pygame.font.Font(None, 32)
        self.text_font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 16)
        
        # Load all Pokemon
        self._load_pokemon()
        
        # Enable text input
        pygame.key.start_text_input()
    
    def on_exit(self):
        """Called when screen becomes inactive."""
        super().on_exit()
        pygame.key.stop_text_input()
    
    def _load_pokemon(self):
        """Load all Pokemon from database."""
        if self.database:
            try:
                with self.database as db:
                    cursor = db.execute("""
                        SELECT p.id, p.name, GROUP_CONCAT(t.name) as types
                        FROM pokemon p
                        LEFT JOIN pokemon_types pt ON p.id = pt.pokemon_id
                        LEFT JOIN types t ON pt.type_id = t.id
                        GROUP BY p.id
                        ORDER BY p.id
                    """)
                    self.all_pokemon = [
                        {
                            'id': row[0],
                            'name': row[1],
                            'types': row[2].split(',') if row[2] else []
                        }
                        for row in cursor.fetchall()
                    ]
            except Exception as e:
                print(f"Error loading Pokemon: {e}")
                self.all_pokemon = []
        else:
            # Demo data
            self.all_pokemon = [
                {'id': i, 'name': f"Pokemon {i}", 'types': ['normal']}
                for i in range(1, 151)
            ]
        
        # Initial search (empty = show all)
        self._update_search()
    
    def _update_search(self):
        """Update search results based on current query."""
        if not self.search_query:
            self.results = self.all_pokemon[:50]  # Show first 50
        else:
            query_lower = self.search_query.lower()
            self.results = [
                p for p in self.all_pokemon
                if query_lower in p['name'].lower() or
                   query_lower in str(p['id']) or
                   any(query_lower in t.lower() for t in p.get('types', []))
            ]
        
        # Reset selection
        self.selected_index = 0
    
    def handle_input(self, action: InputAction):
        """Handle input actions."""
        if action == InputAction.UP:
            self.selected_index = max(0, self.selected_index - 1)
        elif action == InputAction.DOWN:
            self.selected_index = min(
                len(self.results) - 1,
                self.selected_index + 1
            )
        elif action == InputAction.SELECT:
            self._select_pokemon()
        elif action == InputAction.BACK:
            self.screen_manager.pop()
    
    def handle_text_input(self, text: str):
        """
        Handle text input event.
        
        Args:
            text: Text that was typed
        """
        self.search_query += text
        self._update_search()
    
    def handle_backspace(self):
        """Handle backspace key."""
        if self.search_query:
            self.search_query = self.search_query[:-1]
            self._update_search()
    
    def _select_pokemon(self):
        """Select and view a Pokemon."""
        if 0 <= self.selected_index < len(self.results):
            pokemon = self.results[self.selected_index]
            
            # Lazy import to avoid circular dependency
            from .detail_screen import DetailScreen
            
            detail_screen = DetailScreen(
                self.screen_manager,
                pokemon_id=pokemon['id'],
                database=self.database
            )
            self.screen_manager.push(detail_screen)
    
    def update(self, delta_time: float):
        """Update screen state."""
        pass
    
    def render(self, surface: pygame.Surface):
        """Render the screen."""
        # Clear background
        surface.fill(Colors.BACKGROUND)
        
        # Draw title
        title_text = self.title_font.render("Search Pokémon", True, Colors.TEXT_PRIMARY)
        title_rect = title_text.get_rect(center=(240, 20))
        surface.blit(title_text, title_rect)
        
        # Draw search box
        self._render_search_box(surface)
        
        # Draw results
        self._render_results(surface)
        
        # Draw help text
        help_text = self.small_font.render(
            "Type to search | SELECT: View | BACK: Cancel",
            True,
            Colors.TEXT_SECONDARY
        )
        help_rect = help_text.get_rect(right=470, bottom=315)
        surface.blit(help_text, help_rect)
    
    def _render_search_box(self, surface: pygame.Surface):
        """Render the search input box."""
        box_rect = pygame.Rect(20, 45, 440, 30)
        pygame.draw.rect(surface, Colors.BLACK, box_rect)
        pygame.draw.rect(surface, Colors.BORDER, box_rect, 2)
        
        # Draw search query with cursor
        query_display = self.search_query + "|"
        query_text = self.text_font.render(
            query_display,
            True,
            Colors.TEXT_PRIMARY
        )
        surface.blit(query_text, (25, 50))
        
        # Draw result count
        count_text = self.small_font.render(
            f"{len(self.results)} results",
            True,
            Colors.TEXT_SECONDARY
        )
        surface.blit(count_text, (25, 78))
    
    def _render_results(self, surface: pygame.Surface):
        """Render search results list."""
        if not self.results:
            no_results = self.text_font.render(
                "No matches found",
                True,
                Colors.TEXT_SECONDARY
            )
            no_results_rect = no_results.get_rect(center=(240, 160))
            surface.blit(no_results, no_results_rect)
            return
        
        # Calculate visible range
        start_idx = max(0, self.selected_index - self.max_visible_results // 2)
        end_idx = min(start_idx + self.max_visible_results, len(self.results))
        
        # Adjust start if we're near the end
        if end_idx - start_idx < self.max_visible_results:
            start_idx = max(0, end_idx - self.max_visible_results)
        
        for i in range(start_idx, end_idx):
            relative_idx = i - start_idx
            y = self.results_start_y + relative_idx * self.item_height
            
            pokemon = self.results[i]
            is_selected = (i == self.selected_index)
            
            self._render_result_item(surface, pokemon, y, is_selected)
    
    def _render_result_item(
        self,
        surface: pygame.Surface,
        pokemon: dict,
        y: int,
        is_selected: bool
    ):
        """Render a single result item."""
        # Draw selection background
        if is_selected:
            rect = pygame.Rect(20, y, 440, self.item_height - 2)
            pygame.draw.rect(surface, Colors.SELECTION_BG, rect)
            pygame.draw.rect(surface, Colors.BORDER, rect, 2)
        
        text_color = Colors.SELECTION_TEXT if is_selected else Colors.TEXT_PRIMARY
        
        # Draw Pokemon ID
        id_text = self.text_font.render(
            f"#{pokemon['id']:03d}",
            True,
            text_color
        )
        surface.blit(id_text, (25, y + 5))
        
        # Draw Pokemon name
        name_text = self.text_font.render(
            pokemon['name'].capitalize(),
            True,
            text_color
        )
        surface.blit(name_text, (80, y + 5))
        
        # Draw types if available
        if 'types' in pokemon and pokemon['types']:
            types_text = ' '.join([t.capitalize() for t in pokemon['types']])
            types_render = self.small_font.render(
                types_text,
                True,
                text_color
            )
            types_rect = types_render.get_rect(right=450, centery=y + self.item_height // 2)
            surface.blit(types_render, types_rect)
        
        # Return empty list = full screen update
        return []