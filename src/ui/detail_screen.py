"""
Detail Screen for ShokeDex - Detailed Pokémon view
"""

import pygame
from typing import Optional, Dict, List
from .screen import Screen
from .colors import Colors
from ..input_manager import InputAction
from .sprite_loader import load_detail


class DetailScreen(Screen):
    """
    Detail screen showing comprehensive information about a single Pokémon.
    
    Displays sprite, stats, types, abilities, and other information.
    """
    
    def __init__(self, screen_manager, pokemon_id: int, database=None):
        """
        Initialize DetailScreen.
        
        Args:
            screen_manager: ScreenManager instance
            pokemon_id: ID of the Pokemon to display
            database: Database instance (optional)
        """
        super().__init__(screen_manager)
        self.pokemon_id = pokemon_id
        self.database = database
        
        # Pokemon data
        self.pokemon_data: Optional[Dict] = None
        self.stats: List[Dict] = []
        self.types: List[str] = []
        self.evolutions: List[Dict] = []
        self.abilities: List[Dict] = []
        
        # View mode (stats, evolutions, abilities)
        self.view_tab = "stats"  # Can be "stats", "evolutions", "abilities"
        
        # Fonts
        self.title_font: Optional[pygame.font.Font] = None
        self.heading_font: Optional[pygame.font.Font] = None
        self.text_font: Optional[pygame.font.Font] = None
        self.small_font: Optional[pygame.font.Font] = None
    
    def on_enter(self):
        """Called when screen becomes active."""
        super().on_enter()
        
        # Initialize fonts
        self.title_font = pygame.font.Font(None, 36)
        self.heading_font = pygame.font.Font(None, 24)
        self.text_font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 16)
        
        # Load Pokemon data
        self._load_pokemon_data()
    
    def _load_pokemon_data(self):
        """Load Pokemon data from database."""
        if self.database:
            try:
                with self.database as db:
                    # Get basic Pokemon info
                    self.pokemon_data = db.get_pokemon_by_id(self.pokemon_id)
                    
                    if self.pokemon_data:
                        # Get stats
                        self.stats = db.get_pokemon_stats(self.pokemon_id)
                        
                        # Get types
                        cursor = db.execute("""
                            SELECT t.name
                            FROM pokemon_types pt
                            JOIN types t ON pt.type_id = t.id
                            WHERE pt.pokemon_id = ?
                            ORDER BY pt.slot
                        """, (self.pokemon_id,))
                        self.types = [row[0] for row in cursor.fetchall()]
                        
                        # Get evolutions
                        self.evolutions = db.get_evolutions(self.pokemon_id)
                        
                        # Get abilities
                        cursor = db.execute("""
                            SELECT a.name, pa.is_hidden
                            FROM pokemon_abilities pa
                            JOIN abilities a ON pa.ability_id = a.id
                            WHERE pa.pokemon_id = ?
                            ORDER BY pa.slot
                        """, (self.pokemon_id,))
                        self.abilities = [
                            {'name': row[0], 'is_hidden': row[1]}
                            for row in cursor.fetchall()
                        ]
            except Exception as e:
                print(f"Error loading Pokemon data: {e}")
                self.pokemon_data = None
        
        # Create demo data if no database
        if not self.pokemon_data:
            self.pokemon_data = {
                'id': self.pokemon_id,
                'name': f'pokemon_{self.pokemon_id}',
                'height': 10,
                'weight': 100,
                'generation': 1,
            }
            self.stats = [
                {'name': 'HP', 'base_stat': 45},
                {'name': 'Attack', 'base_stat': 49},
                {'name': 'Defense', 'base_stat': 49},
                {'name': 'Special Attack', 'base_stat': 65},
                {'name': 'Special Defense', 'base_stat': 65},
                {'name': 'Speed', 'base_stat': 45},
            ]
            self.types = ['normal']
            self.evolutions = []
            self.abilities = []
    
    def handle_input(self, action: InputAction):
        """Handle input actions."""
        if action == InputAction.BACK:
            self.screen_manager.pop()
        elif action == InputAction.LEFT:
            self._navigate_pokemon(-1)
        elif action == InputAction.RIGHT:
            self._navigate_pokemon(1)
        elif action == InputAction.UP:
            self._cycle_tab(-1)
        elif action == InputAction.DOWN:
            self._cycle_tab(1)
    
    def _cycle_tab(self, delta: int):
        """Cycle through view tabs."""
        tabs = ["stats", "evolutions", "abilities"]
        current_idx = tabs.index(self.view_tab)
        new_idx = (current_idx + delta) % len(tabs)
        self.view_tab = tabs[new_idx]
    
    def _navigate_pokemon(self, delta: int):
        """Navigate to adjacent Pokemon."""
        new_id = self.pokemon_id + delta
        
        # Check if Pokemon exists
        # TODO: Query database for max Pokemon ID instead of hardcoding
        max_id = 386  # Gen 1-3 for now
        if self.database:
            try:
                with self.database as db:
                    cursor = db.execute("SELECT MAX(id) FROM pokemon")
                    result = cursor.fetchone()
                    if result and result[0]:
                        max_id = result[0]
            except Exception:
                pass  # Use default
        
        if new_id >= 1 and new_id <= max_id:
            self.pokemon_id = new_id
            self._load_pokemon_data()
    
    def update(self, delta_time: float):
        """Update screen state."""
        pass
    
    def render(self, surface: pygame.Surface):
        """Render the screen."""
        if not self.pokemon_data:
            surface.fill(Colors.BACKGROUND)
            error_text = self.text_font.render(
                "Pokemon not found",
                True,
                Colors.ERROR
            )
            error_rect = error_text.get_rect(center=(240, 160))
            surface.blit(error_text, error_rect)
            return
        
        # Clear background
        surface.fill(Colors.BACKGROUND)
        
        # Draw Pokemon name and ID
        name = self.pokemon_data['name'].capitalize()
        name_text = self.title_font.render(name, True, Colors.TEXT_PRIMARY)
        name_rect = name_text.get_rect(centerx=240, top=10)
        surface.blit(name_text, name_rect)
        
        id_text = self.text_font.render(
            f"#{self.pokemon_data['id']:03d}",
            True,
            Colors.TEXT_SECONDARY
        )
        id_rect = id_text.get_rect(centerx=240, top=45)
        surface.blit(id_text, id_rect)
        
        # Draw sprite placeholder
        sprite_rect = pygame.Rect(180, 75, 120, 120)
        # Attempt to load and draw the detail sprite; fall back to placeholder
        try:
            sprite_surf = load_detail(self.pokemon_id)
            if sprite_surf:
                # Scale to sprite_rect size if necessary
                try:
                    if sprite_surf.get_size() != (sprite_rect.width, sprite_rect.height):
                        sprite_surf = pygame.transform.smoothscale(sprite_surf, (sprite_rect.width, sprite_rect.height))
                except Exception:
                    pass

                surface.blit(sprite_surf, sprite_rect.topleft)
            else:
                pygame.draw.rect(surface, Colors.BORDER, sprite_rect, 2)
                # Draw "Sprite" text in center
                sprite_text = self.small_font.render("Sprite", True, Colors.TEXT_SECONDARY)
                sprite_text_rect = sprite_text.get_rect(center=sprite_rect.center)
                surface.blit(sprite_text, sprite_text_rect)
        except Exception:
            # If pygame unavailable or load fails, show placeholder
            pygame.draw.rect(surface, Colors.BORDER, sprite_rect, 2)
            sprite_text = self.small_font.render("Sprite", True, Colors.TEXT_SECONDARY)
            sprite_text_rect = sprite_text.get_rect(center=sprite_rect.center)
            surface.blit(sprite_text, sprite_text_rect)
        
        # Draw types
        if self.types:
            types_y = 205
            types_label = self.heading_font.render("Type:", True, Colors.TEXT_PRIMARY)
            surface.blit(types_label, (20, types_y))
            
            types_x = 80
            for type_name in self.types:
                type_color = Colors.TYPE_COLORS.get(type_name.lower(), Colors.GRAY)
                type_rect = pygame.Rect(types_x, types_y, 70, 25)
                pygame.draw.rect(surface, type_color, type_rect)
                pygame.draw.rect(surface, Colors.BLACK, type_rect, 1)
                
                type_text = self.small_font.render(
                    type_name.capitalize(),
                    True,
                    Colors.BLACK
                )
                type_text_rect = type_text.get_rect(center=type_rect.center)
                surface.blit(type_text, type_text_rect)
                
                types_x += 75
        
        # Draw tabs
        self._render_tabs(surface)
        
        # Draw content based on selected tab
        if self.view_tab == "stats":
            self._render_stats_tab(surface)
        elif self.view_tab == "evolutions":
            self._render_evolutions_tab(surface)
        elif self.view_tab == "abilities":
            self._render_abilities_tab(surface)
        
        # Draw help text
        help_text = self.small_font.render(
            "←/→: Navigate | ↑/↓: Tabs | BACK: Return",
            True,
            Colors.TEXT_SECONDARY
        )
        help_rect = help_text.get_rect(right=470, bottom=315)
        surface.blit(help_text, help_rect)
    
    def _render_tabs(self, surface: pygame.Surface):
        """Render tab buttons."""
        tabs = [
            ("Stats", "stats"),
            ("Evolutions", "evolutions"),
            ("Abilities", "abilities")
        ]
        
        tab_y = 235
        tab_width = 150
        tab_x = 10
        
        for label, tab_id in tabs:
            is_active = self.view_tab == tab_id
            
            # Draw tab button
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width, 20)
            if is_active:
                pygame.draw.rect(surface, Colors.SELECTION_BG, tab_rect)
            pygame.draw.rect(surface, Colors.BORDER, tab_rect, 1)
            
            # Draw tab label
            color = Colors.BLACK if is_active else Colors.TEXT_SECONDARY
            tab_text = self.small_font.render(label, True, color)
            tab_text_rect = tab_text.get_rect(center=tab_rect.center)
            surface.blit(tab_text, tab_text_rect)
            
            tab_x += tab_width + 5
    
    def _render_stats_tab(self, surface: pygame.Surface):
        """Render stats tab content."""
        if not self.stats:
            return
        
        stats_y = 260
        
        for stat in self.stats[:6]:  # Show first 6 stats
            # Stat name
            stat_name = self.small_font.render(
                f"{stat['name']}:",
                True,
                Colors.TEXT_SECONDARY
            )
            surface.blit(stat_name, (20, stats_y))
            
            # Stat value
            stat_value = self.text_font.render(
                str(stat['base_stat']),
                True,
                Colors.TEXT_PRIMARY
            )
            surface.blit(stat_value, (120, stats_y - 2))
            
            # Stat bar
            bar_width = int(stat['base_stat'] * 1.2)  # Scale to fit
            max_bar_width = 200
            bar_width = min(bar_width, max_bar_width)
            bar_rect = pygame.Rect(170, stats_y + 2, bar_width, 10)
            pygame.draw.rect(surface, Colors.LIGHT_GREEN, bar_rect)
            pygame.draw.rect(surface, Colors.BORDER, bar_rect, 1)
            
            stats_y += 18
        
        # Draw physical stats
        phys_y = 260
        phys_x = 380
        
        height_m = self.pokemon_data.get('height', 0) / 10.0
        weight_kg = self.pokemon_data.get('weight', 0) / 10.0
        
        height_text = self.small_font.render(
            f"Height:",
            True,
            Colors.TEXT_SECONDARY
        )
        surface.blit(height_text, (phys_x, phys_y))
        
        height_value = self.text_font.render(
            f"{height_m:.1f}m",
            True,
            Colors.TEXT_PRIMARY
        )
        surface.blit(height_value, (phys_x, phys_y + 15))
        
        weight_text = self.small_font.render(
            f"Weight:",
            True,
            Colors.TEXT_SECONDARY
        )
        surface.blit(weight_text, (phys_x, phys_y + 40))
        
        weight_value = self.text_font.render(
            f"{weight_kg:.1f}kg",
            True,
            Colors.TEXT_PRIMARY
        )
        surface.blit(weight_value, (phys_x, phys_y + 55))
    
    def _render_evolutions_tab(self, surface: pygame.Surface):
        """Render evolutions tab content."""
        content_y = 260
        
        if not self.evolutions:
            no_evo = self.text_font.render(
                "No evolution data",
                True,
                Colors.TEXT_SECONDARY
            )
            surface.blit(no_evo, (20, content_y + 20))
            return
        
        # Draw evolution chain
        for evo in self.evolutions[:5]:  # Show up to 5 evolutions
            from_name = evo.get('from_name', '???')
            to_name = evo.get('to_name', '???')
            
            # Draw "from" Pokemon
            if from_name and from_name != 'None':
                from_text = self.text_font.render(
                    from_name.capitalize(),
                    True,
                    Colors.TEXT_PRIMARY
                )
                surface.blit(from_text, (20, content_y))
                
                # Draw arrow
                arrow = self.text_font.render("→", True, Colors.LIGHT_GREEN)
                surface.blit(arrow, (140, content_y))
            
            # Draw "to" Pokemon
            to_text = self.text_font.render(
                to_name.capitalize(),
                True,
                Colors.TEXT_PRIMARY
            )
            surface.blit(to_text, (170, content_y))
            
            # Draw evolution requirements
            requirements = []
            if evo.get('min_level'):
                requirements.append(f"Lv.{evo['min_level']}")
            if evo.get('item'):
                requirements.append(evo['item'])
            if evo.get('trigger') and evo['trigger'] not in ['level-up', 'use-item']:
                requirements.append(evo['trigger'].replace('-', ' '))
            
            if requirements:
                req_text = self.small_font.render(
                    ' / '.join(requirements),
                    True,
                    Colors.TEXT_SECONDARY
                )
                surface.blit(req_text, (300, content_y + 3))
            
            content_y += 25
    
    def _render_abilities_tab(self, surface: pygame.Surface):
        """Render abilities tab content."""
        content_y = 260
        
        if not self.abilities:
            no_abilities = self.text_font.render(
                "No ability data",
                True,
                Colors.TEXT_SECONDARY
            )
            surface.blit(no_abilities, (20, content_y + 20))
            return
        
        for ability in self.abilities:
            # Draw ability name
            ability_name = ability['name'].replace('-', ' ').title()
            ability_text = self.text_font.render(
                ability_name,
                True,
                Colors.TEXT_PRIMARY
            )
            surface.blit(ability_text, (20, content_y))
            
            # Draw hidden indicator
            if ability.get('is_hidden'):
                hidden_text = self.small_font.render(
                    "(Hidden)",
                    True,
                    Colors.YELLOW
                )
                surface.blit(hidden_text, (220, content_y + 3))
            
            content_y += 25
