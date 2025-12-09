"""
Detail Screen for ShokeDex - Detailed Pokémon view

Story 3.1: Basic layout with large sprite, header, and placeholder panels.
Story 3.2: Six base stats with visual progress bars, color-coded by value.
Story 3.3: Type badges with holographic colors and rounded rectangle styling.
Story 3.4: Physical measurements (height in meters, weight in kilograms) display.
Story 3.6: L/R button navigation to adjacent Pokémon with fade transitions.
Story 5.1: Three-stage evolution chain display with sprites and requirements.
Story 5.7: Tab-based navigation (Info/Stats/Evolution) using L/R buttons.
"""

import pygame
import logging
import time
import math
from enum import Enum
from typing import Optional, Dict, List
from .screen import Screen
from .colors import Colors, get_stat_color, TYPE_COLORS
from ..input_manager import InputAction
from .sprite_loader import load_detail, load_thumb


# Story 3.7: Stat label formatting map (AC #4)
# Database stores lowercase hyphenated names, display uses proper game conventions
STAT_LABEL_MAP = {
    'hp': 'HP',
    'attack': 'Attack',
    'defense': 'Defense',
    'special-attack': 'Sp.Atk',
    'special-defense': 'Sp.Def',
    'speed': 'Speed'
}


# Story 5.7: Tab enum for DetailScreen navigation (AC #1)
class DetailTab(Enum):
    """
    Tabs available on DetailScreen for organizing information.
    
    INFO = Description and Pokédex entry (default tab)
    STATS = Base stats, type badges, physical measurements
    EVOLUTION = Evolution chain display
    
    Story 5.7 AC #1: Three tabs available - Info (default), Stats, Evolution
    Numeric values determine tab cycling order for L/R button navigation
    """
    INFO = 0
    STATS = 1
    EVOLUTION = 2


def format_stat_label(db_stat_name: str) -> str:
    """Convert database stat name to display label.
    
    Args:
        db_stat_name: Stat name from database (e.g., 'special-attack')
        
    Returns:
        Formatted display label (e.g., 'Sp.Atk')
        
    Story 3.7 AC #4: Labels use proper formatting like game conventions
    """
    return STAT_LABEL_MAP.get(db_stat_name.lower(), db_stat_name.title())


class EvolutionPanel:
    """
    Component for displaying evolution chains on DetailScreen.
    
    Story 5.1 Implementation:
    - Loads evolution chain data from Database.get_evolution_chain()
    - Loads thumbnail sprites (64x64) for all chain members
    - Renders horizontal evolution chain with sprites, names, dex numbers
    - Shows evolution arrows with requirements (level, stone, etc.)
    - Highlights current Pokémon with cyan glow
    - Uses holographic blue styling consistent with DetailScreen
    
    AC #1: Three stages displayed horizontally with sprites, names, dex numbers
    AC #2: Electric blue arrows between stages pointing evolution direction
    AC #3: Requirements displayed below arrows (Level 16, Thunder Stone, etc.)
    AC #4: Current Pokémon highlighted with bright cyan glow
    AC #5: Holographic blue panel styling, electric blue border, dark blue background
    AC #6: Database integration via get_evolution_chain()
    AC #7: Sprite loading via SpriteLoader.load_thumb()
    AC #8: Rendering performance < 200ms first load, < 50ms cached
    """
    
    def __init__(self, screen_manager, pokemon_id: int):
        """
        Initialize EvolutionPanel for a Pokémon.
        
        Args:
            screen_manager: ScreenManager instance providing database access
            pokemon_id: National Dex number (1-386)
        """
        self.screen_manager = screen_manager
        self.pokemon_id = pokemon_id
        self.database = screen_manager.database if hasattr(screen_manager, 'database') else None
        
        # Evolution data
        self.evolution_data: Optional[Dict] = None
        self.sprites: Dict[int, pygame.Surface] = {}  # pokemon_id -> Surface
        
        # Fonts (initialized in load_data after pygame is guaranteed ready)
        self.name_font: Optional[pygame.font.Font] = None
        self.dex_font: Optional[pygame.font.Font] = None
        self.requirement_font: Optional[pygame.font.Font] = None
        self.label_font: Optional[pygame.font.Font] = None
    
    def load_data(self):
        """
        Load evolution chain data from database.
        
        AC #6: Calls Database.get_evolution_chain(pokemon_id)
        Uses parameterized SQL, completes in < 50ms
        """
        if not self.database:
            logging.warning("EvolutionPanel: No database available")
            self.evolution_data = None
            return
        
        try:
            start_time = time.perf_counter()
            
            with self.database as db:
                self.evolution_data = db.get_evolution_chain(self.pokemon_id)
            
            load_time = (time.perf_counter() - start_time) * 1000
            logging.debug(f"Evolution data loaded in {load_time:.2f}ms")
        except Exception as e:
            logging.error(f"EvolutionPanel: Failed to load evolution data: {e}")
            self.evolution_data = None
            return
        
        # Initialize fonts now that pygame is ready
        self.name_font = pygame.font.Font(None, 14)  # Rajdhani Bold 14px for names
        self.dex_font = pygame.font.Font(None, 12)   # Share Tech Mono 12px for dex numbers
        self.requirement_font = pygame.font.Font(None, 14)  # Rajdhani 14px for requirements
        self.label_font = pygame.font.Font(None, 12)  # Small font for "Current" label
    
    def load_sprites(self):
        """
        Load thumbnail sprites for all Pokémon in evolution chain.
        
        AC #7: Calls SpriteLoader.load_thumb(pokemon_id) for each stage
        Thumbnails are 64x64 pixels, loaded from LRU cache when available
        Missing sprites handled gracefully with placeholder
        """
        if not self.evolution_data or not self.evolution_data['stages']:
            return
        
        start_time = time.perf_counter()
        
        for stage in self.evolution_data['stages']:
            pokemon_id = stage['pokemon_id']
            sprite = load_thumb(pokemon_id)
            
            if sprite:
                # Scale to 64x64 if not already (load_thumb returns 32x32)
                # Story 5.1 AC #1: Thumbnails must be 64x64
                if sprite.get_width() != 64:
                    sprite = pygame.transform.scale(sprite, (64, 64))
                self.sprites[pokemon_id] = sprite
            else:
                # Create placeholder surface for missing sprites
                placeholder = pygame.Surface((64, 64))
                placeholder.fill(Colors.DARK_BLUE)
                pygame.draw.rect(placeholder, Colors.ELECTRIC_BLUE, 
                               pygame.Rect(0, 0, 64, 64), 2)
                self.sprites[pokemon_id] = placeholder
        
        load_time = (time.perf_counter() - start_time) * 1000
        logging.debug(f"Evolution sprites loaded in {load_time:.2f}ms")
    
    def render(self, surface: pygame.Surface, x: int, y: int):
        """
        Render evolution panel at specified position.
        
        Args:
            surface: pygame.Surface to draw on
            x: X position (panel left edge)
            y: Y position (panel top edge)
            
        AC #1: All three stages displayed horizontally with sprites, names, dex numbers
        AC #2: Arrows shown between stages with electric blue color
        AC #3: Requirements displayed below arrows (ice blue text)
        AC #4: Current Pokémon highlighted with bright cyan glow (#4df7ff)
        AC #5: Panel styling: dark blue background, electric blue border, 16px padding
        AC #8: Rendering performance < 200ms first load, < 50ms cached
        """
        if not self.evolution_data or not self.evolution_data['stages']:
            # No evolution data - render "No evolutions" message
            self._render_no_evolutions(surface, x, y)
            return
        
        start_time = time.perf_counter()
        
        stages = self.evolution_data['stages']
        evolutions = self.evolution_data['evolutions']
        current_stage = self.evolution_data['current_stage']
        is_branching = self.evolution_data.get('is_branching', False)  # Story 5.2
        
        # Panel dimensions (AC #5: holographic styling)
        panel_width = surface.get_width() - (x * 2)  # Full width minus margins
        panel_height = 120  # Height for sprites + text + arrows (linear layout)
        
        # Story 5.2 AC #6: Conditional layout based on branching
        if is_branching:
            # Use vertical branching layout (Story 5.2 Tasks 2-6)
            self._render_branching_layout(surface, x, y, stages, evolutions, current_stage)
        else:
            # Use existing horizontal layout (Story 5.1)
            self._render_linear_layout(surface, x, y, panel_width, panel_height, 
                                      stages, evolutions, current_stage)
        
        # Performance logging (AC #8)
        render_time = (time.perf_counter() - start_time) * 1000
        if render_time > 200:
            logging.warning(f"Evolution panel render took {render_time:.2f}ms (target: <200ms first load)")
        else:
            logging.debug(f"Evolution panel rendered in {render_time:.2f}ms")
    
    def _render_linear_layout(self, surface: pygame.Surface, x: int, y: int,
                              panel_width: int, panel_height: int,
                              stages: list, evolutions: list, current_stage: int):
        """
        Render linear (horizontal) evolution chain layout.
        
        Story 5.1: Three-stage horizontal layout with arrows between stages
        """
        # Draw panel background (AC #5: dark blue rgba(26, 47, 74, 0.9))
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((*Colors.DARK_BLUE, 230))
        
        # Draw panel border (AC #5: electric blue 2px border)
        pygame.draw.rect(panel_surface, Colors.ELECTRIC_BLUE,
                        pygame.Rect(0, 0, panel_width, panel_height), 2)
        
        surface.blit(panel_surface, (x, y))
        
        # Calculate sprite positions (AC #1: horizontal layout with even spacing)
        num_stages = len(stages)
        sprite_spacing = panel_width // (num_stages + 1)  # Distribute evenly
        sprite_y = y + 20  # Vertical position for sprites within panel
        
        # Render each evolution stage
        for i, stage in enumerate(stages):
            pokemon_id = stage['pokemon_id']
            pokemon_name = stage['name'].capitalize()
            stage_num = stage['stage']
            is_current = (stage_num == current_stage)
            
            # Calculate X position for this stage
            sprite_x = x + (i + 1) * sprite_spacing - 32  # Center 64px sprite
            
            # AC #4: Highlight current Pokémon with bright cyan glow
            if is_current:
                glow_rect = pygame.Rect(sprite_x - 4, sprite_y - 4, 72, 72)
                pygame.draw.rect(surface, Colors.BRIGHT_CYAN, glow_rect, 3)
            
            # Render sprite (AC #1: 64x64 thumbnail size)
            if pokemon_id in self.sprites:
                surface.blit(self.sprites[pokemon_id], (sprite_x, sprite_y))
            
            # Render Pokémon name below sprite (AC #1: Rajdhani Bold 14px, white)
            if self.name_font:
                name_text = self.name_font.render(pokemon_name, True, Colors.HOLOGRAM_WHITE)
                name_rect = name_text.get_rect(centerx=sprite_x + 32, top=sprite_y + 68)
                surface.blit(name_text, name_rect)
            
            # Render Dex number below name (AC #1: "#NNN" format, Share Tech Mono 12px, ice blue)
            if self.dex_font:
                dex_text = self.dex_font.render(f"#{pokemon_id:03d}", True, Colors.ICE_BLUE)
                dex_rect = dex_text.get_rect(centerx=sprite_x + 32, top=sprite_y + 84)
                surface.blit(dex_text, dex_rect)
            
            # AC #4: "Current" label below current Pokémon (ice blue)
            if is_current and self.label_font:
                current_label = self.label_font.render("Current", True, Colors.ICE_BLUE)
                current_rect = current_label.get_rect(centerx=sprite_x + 32, top=sprite_y + 98)
                surface.blit(current_label, current_rect)
        
        # Render evolution arrows and requirements (AC #2, AC #3)
        for i in range(len(stages) - 1):
            from_stage = stages[i]
            to_stage = stages[i + 1]
            
            # Find matching evolution relationship
            evo_data = None
            for evo in evolutions:
                if evo['from_id'] == from_stage['pokemon_id'] and evo['to_id'] == to_stage['pokemon_id']:
                    evo_data = evo
                    break
            
            if not evo_data:
                continue  # No evolution relationship (shouldn't happen but defensive)
            
            # Calculate arrow position (between sprites)
            from_x = x + (i + 1) * sprite_spacing + 32  # Right edge of from sprite
            to_x = x + (i + 2) * sprite_spacing - 32    # Left edge of to sprite
            arrow_y = sprite_y + 32  # Middle of sprite height
            
            # Draw arrow (AC #2: electric blue color, clear direction indicator)
            pygame.draw.line(surface, Colors.ELECTRIC_BLUE, 
                           (from_x, arrow_y), (to_x, arrow_y), 3)
            # Arrow head (simple triangle)
            pygame.draw.polygon(surface, Colors.ELECTRIC_BLUE, [
                (to_x, arrow_y),
                (to_x - 8, arrow_y - 5),
                (to_x - 8, arrow_y + 5)
            ])
            
            # Format requirement text (AC #3)
            requirement_text = self._format_requirement(evo_data)
            
            # Render requirement below arrow (AC #3: Rajdhani 14px, ice blue)
            if requirement_text and self.requirement_font:
                req_surface = self.requirement_font.render(requirement_text, True, Colors.ICE_BLUE)
                req_rect = req_surface.get_rect(centerx=(from_x + to_x) // 2, top=arrow_y + 10)
                surface.blit(req_surface, req_rect)
    
    def _render_branching_layout(self, surface: pygame.Surface, x: int, y: int,
                                 stages: list, evolutions: list, current_stage: int):
        """
        Render branching evolution layout with vertical branch distribution.
        
        Story 5.2: Branching evolution display (Eevee, Tyrogue, Wurmple, etc.)
        AC #2: Root on left, branches spread vertically on right
        AC #3: Visual separation with tree-like arrows
        AC #4: Requirements displayed per branch
        AC #5: Current highlighting maintained
        AC #8: Consistent holographic blue styling
        """
        # Build branching structure: find root and branches
        # Root = stage 1 Pokemon, Branches = stage 2+ Pokemon
        root_pokemon = [s for s in stages if s['stage'] == 1]
        branch_pokemon = [s for s in stages if s['stage'] > 1]
        
        if not root_pokemon:
            # Fallback: shouldn't happen but defensive
            self._render_linear_layout(surface, x, y, surface.get_width() - (x * 2), 
                                      120, stages, evolutions, current_stage)
            return
        
        root = root_pokemon[0]  # Only one root for branching chains
        num_branches = len(branch_pokemon)
        
        # Panel dimensions (Story 5.2 AC #2: accommodate vertical branches)
        panel_width = surface.get_width() - (x * 2)
        panel_height = max(150, 40 + num_branches * 30)  # Dynamic height based on branches
        
        # Draw panel background (AC #8: same styling as Story 5.1)
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((*Colors.DARK_BLUE, 230))
        
        # Draw panel border (AC #8: electric blue 2px border)
        pygame.draw.rect(panel_surface, Colors.ELECTRIC_BLUE,
                        pygame.Rect(0, 0, panel_width, panel_height), 2)
        
        surface.blit(panel_surface, (x, y))
        
        # Story 5.2 Task 2.3: Vertical spacing formula
        vertical_spacing = (panel_height - 40) / (num_branches + 1) if num_branches > 0 else 0
        
        # Root Pokemon position (Story 5.2 AC #2: left side, vertically centered)
        root_x = x + 50
        root_y = y + (panel_height // 2) - 32  # Center vertically within panel
        root_id = root['pokemon_id']
        root_is_current = (root['stage'] == current_stage)
        
        # Render root Pokemon (Story 5.2 Task 3.1)
        if root_is_current:
            glow_rect = pygame.Rect(root_x - 4, root_y - 4, 72, 72)
            pygame.draw.rect(surface, Colors.BRIGHT_CYAN, glow_rect, 3)
        
        if root_id in self.sprites:
            surface.blit(self.sprites[root_id], (root_x, root_y))
        
        # Root name and dex number (Story 5.2 Task 3.4, 3.5)
        if self.name_font:
            name_text = self.name_font.render(root['name'].capitalize(), True, Colors.HOLOGRAM_WHITE)
            name_rect = name_text.get_rect(centerx=root_x + 32, top=root_y + 68)
            surface.blit(name_text, name_rect)
        
        if self.dex_font:
            dex_text = self.dex_font.render(f"#{root_id:03d}", True, Colors.ICE_BLUE)
            dex_rect = dex_text.get_rect(centerx=root_x + 32, top=root_y + 84)
            surface.blit(dex_text, dex_rect)
        
        if root_is_current and self.label_font:
            current_label = self.label_font.render("Current", True, Colors.ICE_BLUE)
            current_rect = current_label.get_rect(centerx=root_x + 32, top=root_y + 98)
            surface.blit(current_label, current_rect)
        
        # Branch Pokemon positions (Story 5.2 AC #2: right side, vertically distributed)
        branch_x = x + panel_width - 114  # Right side with margin (64px sprite + 50px margin)
        
        for i, branch in enumerate(branch_pokemon):
            # Story 5.2 Task 2.2: Calculate vertical position using spacing formula
            branch_y = y + 20 + int((i + 1) * vertical_spacing) - 32  # Center sprite on position
            branch_id = branch['pokemon_id']
            branch_is_current = (branch['stage'] == current_stage)
            
            # Story 5.2 Task 5: Highlight current branch (AC #5)
            if branch_is_current:
                glow_rect = pygame.Rect(branch_x - 4, branch_y - 4, 72, 72)
                pygame.draw.rect(surface, Colors.BRIGHT_CYAN, glow_rect, 3)
            
            # Render branch sprite (Story 5.2 Task 3.2)
            if branch_id in self.sprites:
                surface.blit(self.sprites[branch_id], (branch_x, branch_y))
            
            # Render branch name and dex number (Story 5.2 Task 3.4, 3.5)
            if self.name_font:
                name_text = self.name_font.render(branch['name'].capitalize(), True, Colors.HOLOGRAM_WHITE)
                name_rect = name_text.get_rect(centerx=branch_x + 32, top=branch_y + 68)
                surface.blit(name_text, name_rect)
            
            if self.dex_font:
                dex_text = self.dex_font.render(f"#{branch_id:03d}", True, Colors.ICE_BLUE)
                dex_rect = dex_text.get_rect(centerx=branch_x + 32, top=branch_y + 84)
                surface.blit(dex_text, dex_rect)
            
            if branch_is_current and self.label_font:
                current_label = self.label_font.render("Current", True, Colors.ICE_BLUE)
                current_rect = current_label.get_rect(centerx=branch_x + 32, top=branch_y + 98)
                surface.blit(current_label, current_rect)
            
            # Story 5.2 Task 4: Draw arrow from root to this branch (AC #3)
            # Find evolution data for this branch
            evo_data = None
            for evo in evolutions:
                if evo['from_id'] == root_id and evo['to_id'] == branch_id:
                    evo_data = evo
                    break
            
            if evo_data:
                # Arrow start: right edge of root sprite, vertically centered
                arrow_start_x = root_x + 64
                arrow_start_y = root_y + 32
                
                # Arrow end: left edge of branch sprite, vertically centered
                arrow_end_x = branch_x
                arrow_end_y = branch_y + 32
                
                # Story 5.2 Task 4.2: Electric blue arrow (AC #3)
                pygame.draw.line(surface, Colors.ELECTRIC_BLUE,
                               (arrow_start_x, arrow_start_y), 
                               (arrow_end_x, arrow_end_y), 3)
                
                # Arrow head pointing to branch
                angle = math.atan2(arrow_end_y - arrow_start_y, arrow_end_x - arrow_start_x)
                arrow_len = 8
                pygame.draw.polygon(surface, Colors.ELECTRIC_BLUE, [
                    (arrow_end_x, arrow_end_y),
                    (arrow_end_x - arrow_len * math.cos(angle - math.pi/6),
                     arrow_end_y - arrow_len * math.sin(angle - math.pi/6)),
                    (arrow_end_x - arrow_len * math.cos(angle + math.pi/6),
                     arrow_end_y - arrow_len * math.sin(angle + math.pi/6))
                ])
                
                # Story 5.2 Task 4.4, 4.5, 4.6: Requirement text along arrow (AC #4)
                requirement_text = self._format_requirement(evo_data)
                if requirement_text and self.requirement_font:
                    # Position text at midpoint of arrow
                    mid_x = (arrow_start_x + arrow_end_x) // 2
                    mid_y = (arrow_start_y + arrow_end_y) // 2
                    
                    req_surface = self.requirement_font.render(requirement_text, True, Colors.ICE_BLUE)
                    req_rect = req_surface.get_rect(center=(mid_x, mid_y - 10))
                    
                    # Draw small background for readability
                    bg_rect = req_rect.inflate(8, 4)
                    bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
                    bg_surface.fill((*Colors.DARK_BLUE, 200))
                    surface.blit(bg_surface, bg_rect.topleft)
                    
                    surface.blit(req_surface, req_rect)
    
    def _format_requirement(self, evo_data: Dict) -> str:
        """
        Format evolution requirement text for display.
        
        Args:
            evo_data: Evolution relationship dict with method, level, item, trigger
            
        Returns:
            Formatted requirement string (e.g., "Level 16", "Thunder Stone", "Trade")
            
        AC #3: Requirements displayed with proper formatting
        """
        method = evo_data.get('method', 'level-up')
        level = evo_data.get('level')
        item = evo_data.get('item')
        trigger = evo_data.get('trigger')
        
        # Format based on evolution method
        if method == 'level-up' and level:
            return f"Level {level}"
        elif method == 'use-item' and item:
            # Format item name (e.g., "thunder-stone" → "Thunder Stone")
            return item.replace('-', ' ').title()
        elif method == 'trade':
            if item:
                return f"Trade + {item.replace('-', ' ').title()}"
            return "Trade"
        elif trigger == 'high-friendship':
            return "High Friendship"
        elif trigger in ('daytime', 'nighttime'):
            return trigger.capitalize()
        else:
            return "Unknown"
    
    def _render_no_evolutions(self, surface: pygame.Surface, x: int, y: int):
        """
        Render "No evolutions" message for single-stage Pokémon.
        
        Args:
            surface: pygame.Surface to draw on
            x: X position
            y: Y position
        """
        panel_width = surface.get_width() - (x * 2)
        panel_height = 60
        
        # Draw panel background
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((*Colors.DARK_BLUE, 230))
        pygame.draw.rect(panel_surface, Colors.ELECTRIC_BLUE,
                        pygame.Rect(0, 0, panel_width, panel_height), 2)
        surface.blit(panel_surface, (x, y))
        
        # Render message
        if self.name_font:
            message = self.name_font.render("No evolutions", True, Colors.ICE_BLUE)
            message_rect = message.get_rect(center=(x + panel_width // 2, y + panel_height // 2))
            surface.blit(message, message_rect)


class DetailScreen(Screen):
    """
    Detail screen showing comprehensive information about a single Pokémon.
    
    Story 3.1 Implementation:
    - Large sprite display (128x128, center-left positioning)
    - Header with Pokémon name and National Dex number
    - Holographic blue styling (panels, borders, text colors)
    - Placeholder panels for future features (stats, types, measurements, description)
    - B button navigation back to HomeScreen
    - StateManager integration for last viewed persistence
    
    Story 3.2 Implementation:
    - Six base stats displayed with labels, bars, and values
    - Stat bars proportional to value (base_stat / 255) * max_bar_width
    - Color-coded bars: 0-50 gray, 51-100 electric blue, 101-150 cyan, 151+ orange
    - Glow effect for high stats (>= 100)
    - Share Tech Mono font for stat labels/values (with fallback)
    - Holographic blue panel styling for stats
    
    Story 3.3 Implementation:
    - Type badges with rounded rectangles (8px border radius)
    - Type-specific colors from UX holographic palette (17 Gen 1-3 types)
    - Single and dual type display with 8px spacing
    - Rajdhani Bold 14px typography, white text, uppercase
    - 2px border with lighter shade of type color
    - Positioned near sprite without overlapping sprite or stats
    
    Story 3.4 Implementation:
    - Height displayed in meters (e.g., "0.4m") with one decimal place
    - Weight displayed in kilograms (e.g., "6.0kg") with one decimal place
    - Unit conversion: decimeters → meters (/10), hectograms → kilograms (/10)
    - Labels (ice blue) right-aligned, values (white) left-aligned
    - 8px vertical spacing between height and weight lines
    - Positioned below sprite and type badges without overlap
    
    Story 3.6 Implementation:
    - L button (LEFT) navigates to previous Pokémon (#25 → #24)
    - R button (RIGHT) navigates to next Pokémon (#25 → #26)
    - Wrap-around navigation: #1 ↔ #386 circular browsing
    - Smooth sprite fade transition (100ms out + 100ms in)
    - StateManager updated on each navigation for persistence
    - All UI components refresh: name, sprite, stats, types, measurements, description
    - Performance target: total navigation < 300ms
    """
    
    # Story 5.7: Class-level tab state cache (AC #8)
    # Shared across all DetailScreen instances to persist tab state per Pokémon
    # Key: pokemon_id (1-386), Value: DetailTab enum
    _tab_state_cache: Dict[int, 'DetailTab'] = {}
    
    def __init__(self, screen_manager, pokemon_id: int):
        """
        Initialize DetailScreen for a specific Pokémon.
        
        Args:
            screen_manager: ScreenManager instance providing manager access
            pokemon_id: National Dex number to display (1-386)
        """
        super().__init__(screen_manager)
        self.pokemon_id = pokemon_id
        
        # Manager references (via screen_manager injection pattern)
        self.database = screen_manager.database if hasattr(screen_manager, 'database') else None
        self.state_manager = screen_manager.state_manager if hasattr(screen_manager, 'state_manager') else None
        self.sprite_loader = screen_manager.sprite_loader if hasattr(screen_manager, 'sprite_loader') else None
        
        # Story 5.7: Tab state management (AC #1, #5)
        # current_tab is instance-level, defaults to INFO
        # _tab_state_cache is class-level (shared across instances) for AC #8
        self.current_tab: DetailTab = DetailTab.INFO  # Default to Info tab
        
        # Pokémon data
        self.pokemon_data: Optional[Dict] = None
        self.sprite: Optional[pygame.Surface] = None
        self.stats: List[Dict] = []  # Story 3.2: List of stat dicts with 'name', 'base_stat'
        self.types: List[str] = []  # Story 3.3: List of 1-2 type names (e.g., ['Fire', 'Flying'])
        self.height: float = 0.0  # Story 3.4: Height in meters (converted from decimeters)
        self.weight: float = 0.0  # Story 3.4: Weight in kilograms (converted from hectograms)
        self.description: str = ""  # Story 3.5: Pokédex description text
        self.description_lines: List[pygame.Surface] = []  # Story 3.5: Pre-rendered text surfaces
        self.evolution_panel: Optional[EvolutionPanel] = None  # Story 5.1: Evolution chain display
        
        # Fonts
        self.header_font: Optional[pygame.font.Font] = None
        self.body_font: Optional[pygame.font.Font] = None
        self.small_font: Optional[pygame.font.Font] = None
        self.stat_label_font: Optional[pygame.font.Font] = None  # Story 3.2: 14px for labels
        self.stat_value_font: Optional[pygame.font.Font] = None  # Story 3.2: 16px for values
        self.type_badge_font: Optional[pygame.font.Font] = None  # Story 3.3: Rajdhani Bold 14px
        self.description_font: Optional[pygame.font.Font] = None  # Story 3.5: Rajdhani 16px for description
    
    def on_enter(self):
        """
        Called when screen becomes active - load data, initialize resources.
        
        Lifecycle hook from Screen base class. Loads Pokémon data, sprite,
        and updates StateManager with last viewed Pokémon.
        
        Story 5.7 AC #8: Restore last viewed tab for this Pokémon from class-level cache
        """
        super().on_enter()
        
        # Story 5.7: Restore tab state from class-level cache (AC #8)
        self.current_tab = DetailScreen._tab_state_cache.get(self.pokemon_id, DetailTab.INFO)
        logging.debug(f"DetailScreen.on_enter(): restored tab={self.current_tab.name} for Pokemon #{self.pokemon_id}")
        
        # Initialize fonts (Orbitron Bold 24px for headers per UX spec, fallback to system)
        try:
            # Try to load custom fonts if available
            self.header_font = pygame.font.Font(None, 24)  # Orbitron Bold equivalent
        except Exception:
            self.header_font = pygame.font.Font(None, 24)
        
        self.body_font = pygame.font.Font(None, 16)  # Rajdhani equivalent for body
        self.small_font = pygame.font.Font(None, 14)
        
        # Story 3.2: Load fonts for stat labels and values
        # Share Tech Mono preferred (monospace for number alignment), fallback to None
        self.stat_label_font = pygame.font.Font(None, 14)  # 14px for stat labels (ice blue)
        self.stat_value_font = pygame.font.Font(None, 16)  # 16px for stat values (white)
        
        # Story 3.3: Load font for type badges (Rajdhani Bold 14px preferred)
        try:
            # Try to load Rajdhani Bold (custom font if available)
            self.type_badge_font = pygame.font.Font(None, 14)
            self.type_badge_font.set_bold(True)
        except Exception as e:
            logging.warning(f"Failed to load custom type badge font, using fallback: {e}")
            self.type_badge_font = pygame.font.Font(None, 14)
        
        # Story 3.5: Load font for description (Rajdhani Regular 16px preferred)
        try:
            # Try to load Rajdhani Regular (custom font if available)
            self.description_font = pygame.font.Font(None, 16)
        except Exception as e:
            logging.warning(f"Failed to load description font, using fallback: {e}")
            self.description_font = pygame.font.Font(None, 16)
        
        # Load Pokémon data from database
        self._load_pokemon_data()
        
        # Story 3.5: Pre-render description lines after loading data
        self._render_description_lines()
        
        # Load detail sprite (128x128 variant)
        if self.pokemon_data:
            try:
                self.sprite = load_detail(self.pokemon_id)
                if self.sprite is None:
                    logging.warning(f"Missing sprite for Pokemon #{self.pokemon_id}")
                    # Create text placeholder
                    self.sprite = self._create_text_placeholder(self.pokemon_data['name'])
            except Exception as e:
                logging.error(f"Error loading sprite for Pokemon #{self.pokemon_id}: {e}")
                self.sprite = self._create_text_placeholder(self.pokemon_data.get('name', f'Pokemon #{self.pokemon_id}'))
        
        # Story 5.1: Initialize and load evolution panel (AC #6, #7)
        self.evolution_panel = EvolutionPanel(self.screen_manager, self.pokemon_id)
        self.evolution_panel.load_data()
        self.evolution_panel.load_sprites()
        
        # Update StateManager with last viewed Pokémon (Story 4.2: AC #2)
        if self.state_manager:
            try:
                self.state_manager.set_last_viewed(self.pokemon_id)
                logging.debug(f"DetailScreen.on_enter(): set_last_viewed({self.pokemon_id})")
            except Exception as e:
                logging.warning(f"Failed to update last viewed: {e}")
    
    def on_exit(self):
        """
        Called when screen becomes inactive - save state.
        
        Lifecycle hook from Screen base class. Persists last viewed Pokémon
        to state file via StateManager using atomic write pattern.
        
        Story 5.7 AC #8, #9: Save current tab to class-level cache AND reset to INFO for next viewing
        """
        # Story 5.7: Save current tab to class-level cache for this Pokémon (AC #8)
        DetailScreen._tab_state_cache[self.pokemon_id] = self.current_tab
        logging.debug(f"DetailScreen.on_exit(): saved tab={self.current_tab.name} for Pokemon #{self.pokemon_id}")
        
        # Story 5.7: Reset to INFO tab for next viewing (AC #9)
        self.current_tab = DetailTab.INFO
        
        if self.state_manager:
            try:
                # Ensure current pokemon_id is saved before persisting (Story 4.2: AC #2)
                self.state_manager.set_last_viewed(self.pokemon_id)
                self.state_manager.save_state()
                logging.debug(f"DetailScreen.on_exit(): saved pokemon_id={self.pokemon_id}")
            except Exception as e:
                logging.warning(f"Failed to save state on exit: {e}")
        super().on_exit()
    
    def _load_pokemon_data(self):
        """
        Load Pokémon data from database.
        
        Queries database for basic Pokémon information and stats needed for DetailScreen.
        Handles errors gracefully with fallback data.
        
        Story 3.1 AC #7: Database query must complete in < 50ms
        Story 3.2 AC #7: Load stats data with get_pokemon_stats()
        Story 3.2 AC #8: Validate stat count and values
        """
        if not self.database:
            logging.error("No database available for DetailScreen")
            self._show_error_screen("Database not available")
            return
        
        try:
            with self.database as db:
                # Get basic Pokémon info (AC #3: name and ID for header)
                self.pokemon_data = db.get_pokemon_by_id(self.pokemon_id)
                
                if not self.pokemon_data:
                    logging.error(f"Pokemon #{self.pokemon_id} not found in database")
                    self._show_error_screen("Could not load Pokémon data")
                    return
                
                # Story 3.2: Load stat data (AC #7)
                start_time = time.perf_counter()
                self.stats = db.get_pokemon_stats(self.pokemon_id)
                query_time = (time.perf_counter() - start_time) * 1000  # ms
                
                # Story 3.2 AC #8: Validate stat count
                if len(self.stats) != 6:
                    logging.warning(f"Stats query returned {len(self.stats)}, expected 6 for Pokemon #{self.pokemon_id}")
                
                # Log performance (AC #7: < 50ms target)
                if query_time > 50:
                    logging.warning(f"Stats query took {query_time:.2f}ms (target: <50ms)")
                else:
                    logging.debug(f"Stats loaded in {query_time:.2f}ms")
                
                # Story 3.3: Load type data (AC #7)
                start_time = time.perf_counter()
                self.types = db.get_pokemon_types(self.pokemon_id)
                query_time = (time.perf_counter() - start_time) * 1000  # ms
                
                # Story 3.3 AC #8: Validate type count
                if len(self.types) == 0:
                    logging.warning(f"No types found for Pokemon #{self.pokemon_id}, using placeholder")
                    self.types = ["???"]
                elif len(self.types) > 2:
                    logging.warning(f"Types query returned {len(self.types)}, expected 1-2 for Pokemon #{self.pokemon_id}, using first 2")
                    self.types = self.types[:2]
                
                # Log performance (AC #7: < 50ms target)
                if query_time > 50:
                    logging.warning(f"Types query took {query_time:.2f}ms (target: <50ms)")
                else:
                    logging.debug(f"Types loaded in {query_time:.2f}ms")
                
                # Story 3.4: Load physical data (height, weight) from pokemon_data
                # Database stores: height in decimeters (dm), weight in hectograms (hg)
                # Convert to: meters (m), kilograms (kg)
                # Formula: meters = decimeters / 10, kilograms = hectograms / 10
                height_dm = self.pokemon_data.get('height', 0)
                weight_hg = self.pokemon_data.get('weight', 0)
                
                # Convert units (AC #6: unit conversion)
                self.height = height_dm / 10.0 if height_dm else 0.0
                self.weight = weight_hg / 10.0 if weight_hg else 0.0
                
                # Story 3.4 AC #7: Edge case validation and logging
                if self.height <= 0:
                    logging.warning(f"Invalid height for Pokemon #{self.pokemon_id}: {height_dm} dm, using placeholder")
                    self.height = -1  # Marker for "???" placeholder
                elif self.height > 100:
                    logging.warning(f"Unusually large height for Pokemon #{self.pokemon_id}: {self.height}m")
                
                if self.weight <= 0:
                    logging.warning(f"Invalid weight for Pokemon #{self.pokemon_id}: {weight_hg} hg, using placeholder")
                    self.weight = -1  # Marker for "???" placeholder
                if self.weight > 10000:
                    logging.warning(f"Unusually heavy weight for Pokemon #{self.pokemon_id}: {self.weight}kg")
                
                # Story 3.5: Load description text (AC #7)
                start_time = time.perf_counter()
                self.description = self.pokemon_data.get('description') or ""
                
                # Story 3.5 AC #8: Handle missing description with placeholder
                if not self.description:
                    self.description = "No description available"
                    logging.warning(f"No description found for Pokemon #{self.pokemon_id}")
                
                query_time = (time.perf_counter() - start_time) * 1000  # ms
                if query_time > 50:
                    logging.warning(f"Description load took {query_time:.2f}ms (target: <50ms)")
                else:
                    logging.debug(f"Description loaded in {query_time:.2f}ms")
                
        except Exception as e:
            logging.error(f"Database error loading Pokemon #{self.pokemon_id}: {e}")
            self._show_error_screen("Could not load Pokémon data")
    
    def _create_text_placeholder(self, name: str) -> pygame.Surface:
        """
        Create text-based placeholder for missing sprites.
        
        Args:
            name: Pokémon name to display
            
        Returns:
            pygame.Surface with Pokémon name text on gray background
            
        AC #8: Missing sprites show text placeholder gracefully
        """
        surface = pygame.Surface((128, 128))
        surface.fill((64, 64, 64))  # Gray background
        
        try:
            font = pygame.font.Font(None, 36)
            text = font.render(name, True, (255, 255, 255))
            text_rect = text.get_rect(center=(64, 64))
            surface.blit(text, text_rect)
        except Exception:
            pass  # Silent failure, return gray surface
        
        return surface
    
    def _show_error_screen(self, message: str):
        """
        Display error message when data loading fails.
        
        Args:
            message: User-friendly error message
            
        AC #8: Database errors show friendly message, allow B button exit
        """
        self.pokemon_data = None
        self.sprite = None
        logging.error(f"DetailScreen error: {message}")
    
    def handle_input(self, action: InputAction):
        """
        Handle button press actions.
        
        Args:
            action: InputAction enum value (BACK, LEFT, RIGHT, UP, DOWN, etc.)
            
        Story 3.1 AC #1: B button returns to HomeScreen (pop navigation stack)
        Story 5.7 AC #5: L button (LEFT) switches to previous tab
        Story 5.7 AC #5: R button (RIGHT) switches to next tab
        Story 5.7 AC #6: UP button navigates to next Pokémon (preserves tab)
        Story 5.7 AC #6: DOWN button navigates to previous Pokémon (preserves tab)
        """
        if action == InputAction.BACK:
            # Pop screen stack to return to HomeScreen
            self.screen_manager.pop()
        elif action == InputAction.LEFT:
            # Story 5.7: Switch to previous tab (AC #5)
            self._switch_tab(-1)
        elif action == InputAction.RIGHT:
            # Story 5.7: Switch to next tab (AC #5)
            self._switch_tab(1)
        elif action == InputAction.UP:
            # Story 5.7: Navigate to next Pokémon, preserve tab (AC #6)
            self._navigate_adjacent(1)
        elif action == InputAction.DOWN:
            # Story 5.7: Navigate to previous Pokémon, preserve tab (AC #6)
            self._navigate_adjacent(-1)
    
    def _switch_tab(self, direction: int):
        """
        Switch to next/previous tab with wrapping.
        
        Args:
            direction: 1 for next tab (R button), -1 for previous tab (L button)
            
        Story 5.7 AC #5: Tab switching with wrapping
        - direction=1: INFO → STATS → EVOLUTION → INFO (wrap forward)
        - direction=-1: INFO → EVOLUTION → STATS → INFO (wrap backward)
        - Transition completes in < 100ms (just updates current_tab, no data reload)
        """
        tab_order = [DetailTab.INFO, DetailTab.STATS, DetailTab.EVOLUTION]
        current_index = tab_order.index(self.current_tab)
        new_index = (current_index + direction) % len(tab_order)
        self.current_tab = tab_order[new_index]
        
        logging.debug(f"Tab switched to {self.current_tab.name} (direction={direction})")
    
    def _calculate_adjacent_id(self, current_id: int, direction: int) -> int:
        """
        Calculate adjacent Pokémon ID with wrap-around.
        
        Args:
            current_id: Current Pokémon ID (1-386)
            direction: 1 for next (R button), -1 for previous (L button)
            
        Returns:
            New Pokémon ID (1-386) with wrap-around at boundaries
            
        Story 3.6 AC #3: #1 + LEFT → #386 (wrap to end)
        Story 3.6 AC #4: #386 + RIGHT → #1 (wrap to beginning)
        """
        if direction == 1:  # Next (R button)
            return (current_id % 386) + 1
        else:  # Previous (L button)
            return ((current_id - 2) % 386) + 1
    
    def _navigate_adjacent(self, direction: int):
        """
        Navigate to adjacent Pokémon with state persistence and visual transition.
        
        Args:
            direction: 1 for next (R button), -1 for previous (L button)
            
        Story 3.6 Implementation:
        AC #1, #2: Navigate to prev/next Pokémon, update all data and sprite
        AC #3, #4: Wrap around at boundaries (#1 ↔ #386)
        AC #5: Update StateManager for persistence
        AC #6: Smooth fade transition effect
        AC #7: Data integrity - all UI components update correctly
        AC #8: Performance - total navigation < 300ms
        """
        start_time = time.perf_counter()
        
        # Calculate new pokemon_id with wrap-around (AC #3, #4)
        new_id = self._calculate_adjacent_id(self.pokemon_id, direction)
        
        logging.debug(f"Navigating from Pokemon #{self.pokemon_id} to #{new_id} (direction={direction})")
        
        try:
            # Perform fade transition with data loading (AC #6)
            self._fade_sprite_transition(new_id)
            
            # Update state for persistence (AC #5)
            if self.state_manager:
                self.state_manager.set_last_viewed(self.pokemon_id)
            
        except Exception as e:
            # AC #7 Error handling: stay on current Pokémon if navigation fails
            logging.error(f"Navigation failed: {e}, staying on Pokemon #{self.pokemon_id}")
            return
        
        # Performance logging (AC #8: total < 300ms)
        total_time = (time.perf_counter() - start_time) * 1000
        if total_time > 300:
            logging.warning(f"Slow navigation: {total_time:.2f}ms (target: <300ms)")
        else:
            logging.debug(f"Navigation completed in {total_time:.2f}ms")
    
    def _fade_sprite_transition(self, new_pokemon_id: int):
        """
        Smooth sprite transition with fade effect during Pokémon change.
        
        Args:
            new_pokemon_id: Target Pokémon ID to navigate to
            
        Story 3.6 AC #6:
        - Sprite fades out (100ms) → load new data → fades in (100ms)
        - Total fade transition < 300ms
        - Smooth alpha blending (not jarring cuts)
        - Fade applies to sprite only, not entire screen
        """
        import pygame
        
        # Get current screen surface for rendering during transition
        screen = pygame.display.get_surface()
        if screen is None:
            # No display available (testing mode), skip fade and just load data
            self.pokemon_id = new_pokemon_id
            self._load_pokemon_data()
            self._refresh_pre_rendered_elements()
            self._reload_sprite()
            return
        
        start_time = time.perf_counter()
        clock = pygame.time.Clock()
        
        # Phase 1: Fade out current sprite (100ms)
        if self.sprite:
            fade_duration_ms = 100
            fade_steps = 10
            step_time = fade_duration_ms / fade_steps
            
            for step in range(fade_steps):
                alpha = int(255 * (1.0 - (step + 1) / fade_steps))
                self.sprite.set_alpha(alpha)
                self.render(screen)
                pygame.display.flip()
                clock.tick(100)  # Cap at 100 FPS during transition
        
        # Phase 2: Load new Pokémon data while faded out
        load_start = time.perf_counter()
        self.pokemon_id = new_pokemon_id
        self._load_pokemon_data()
        self._refresh_pre_rendered_elements()
        self._reload_sprite()
        load_time = (time.perf_counter() - load_start) * 1000
        logging.debug(f"Data load during transition: {load_time:.2f}ms")
        
        # Phase 3: Fade in new sprite (100ms)
        if self.sprite:
            fade_duration_ms = 100
            fade_steps = 10
            
            for step in range(fade_steps):
                alpha = int(255 * ((step + 1) / fade_steps))
                self.sprite.set_alpha(alpha)
                self.render(screen)
                pygame.display.flip()
                clock.tick(100)
            
            # Ensure full opacity restored
            self.sprite.set_alpha(255)
        
        total_time = (time.perf_counter() - start_time) * 1000
        logging.debug(f"Fade transition completed: {total_time:.2f}ms")
    
    def _refresh_pre_rendered_elements(self):
        """
        Refresh cached rendered surfaces after Pokémon change.
        
        Called after _load_pokemon_data() to regenerate pre-rendered
        elements that depend on pokemon_id (description lines, stat bars, etc.)
        
        Story 3.6 AC #7: Clear stale data, regenerate cached surfaces
        Story 5.1: Reload evolution panel for new Pokemon
        """
        # Clear description line cache and re-render (Story 3.5)
        self.description_lines = []
        self._render_description_lines()
        
        # Story 5.1: Reload evolution panel for new Pokemon
        if self.evolution_panel:
            self.evolution_panel = EvolutionPanel(self.screen_manager, self.pokemon_id)
            self.evolution_panel.load_data()
            self.evolution_panel.load_sprites()
    
    def _reload_sprite(self):
        """
        Reload sprite for current pokemon_id from SpriteLoader.
        
        Uses cached sprites when available for performance (AC #9).
        Falls back to text placeholder if sprite missing (AC #7).
        """
        if self.pokemon_data:
            try:
                self.sprite = load_detail(self.pokemon_id)
                if self.sprite is None:
                    logging.warning(f"Missing sprite for Pokemon #{self.pokemon_id}")
                    self.sprite = self._create_text_placeholder(self.pokemon_data['name'])
            except Exception as e:
                logging.error(f"Error loading sprite for Pokemon #{self.pokemon_id}: {e}")
                self.sprite = self._create_text_placeholder(
                    self.pokemon_data.get('name', f'Pokemon #{self.pokemon_id}')
                )
    
    def update(self, delta_time: float):
        """
        Update screen state logic each frame.
        
        Args:
            delta_time: Time elapsed since last frame (seconds)
            
        Story 3.1: Minimal implementation - no animations or timers needed
        """
        pass  # No dynamic updates needed for basic layout
    
    def render(self, surface: pygame.Surface):
        """
        Draw screen content to pygame surface.
        
        Args:
            surface: pygame.Surface to render to
            
        Story 5.7 Implementation:
        AC #1: Conditionally render current tab content (Info/Stats/Evolution)
        AC #2-#4: Each tab has specific content layout
        AC #7: Tab indicator always visible at bottom
        AC #10: Render must complete in < 100ms for smooth tab switching
        """
        # Handle error state
        if not self.pokemon_data:
            surface.fill(Colors.DEEP_SPACE_BLACK)
            if self.body_font:
                error_text = self.body_font.render(
                    "Could not load Pokémon data",
                    True,
                    Colors.ICE_BLUE
                )
                error_rect = error_text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
                surface.blit(error_text, error_rect)
                
                help_text = self.small_font.render(
                    "Press B to return",
                    True,
                    Colors.ICE_BLUE
                )
                help_rect = help_text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 + 30))
                surface.blit(help_text, help_rect)
            return
        
        # Fill background with deep space black
        surface.fill(Colors.DEEP_SPACE_BLACK)
        
        # Render header with name and dex number (always visible)
        self._render_header(surface)
        
        # Story 5.7: Conditionally render current tab content (AC #1)
        if self.current_tab == DetailTab.INFO:
            self._render_info_tab(surface)
        elif self.current_tab == DetailTab.STATS:
            self._render_stats_tab(surface)
        elif self.current_tab == DetailTab.EVOLUTION:
            self._render_evolution_tab(surface)
        
        # Story 5.7: Render tab indicator (always visible at bottom) (AC #7)
        self._render_tab_indicator(surface)
    
    def _render_header(self, surface: pygame.Surface):
        """
        Render header section with Pokémon name and National Dex number.
        
        Args:
            surface: pygame.Surface to draw on
            
        AC #3: Name in title case (left), dex number #025 format (right)
        Uses Orbitron Bold 24px, white color per UX spec
        """
        if not self.pokemon_data or not self.header_font:
            return
        
        # Pokémon name (title case, left-aligned in header)
        name = self.pokemon_data['name'].capitalize()
        name_text = self.header_font.render(name, True, Colors.HOLOGRAM_WHITE)
        name_rect = name_text.get_rect(left=20, top=16)
        surface.blit(name_text, name_rect)
        
        # National Dex number (right-aligned in header, #025 format)
        dex_number = f"#{self.pokemon_data['id']:03d}"
        dex_text = self.header_font.render(dex_number, True, Colors.HOLOGRAM_WHITE)
        dex_rect = dex_text.get_rect(right=surface.get_width() - 20, top=16)
        surface.blit(dex_text, dex_rect)
    
    def _render_info_tab(self, surface: pygame.Surface):
        """
        Render Info tab content: sprite (128x128) + description panel.
        
        Args:
            surface: pygame.Surface to draw on
            
        Story 5.7 AC #2: Info tab displays sprite and full Pokédex description
        - Sprite: 128x128 pixels, center-left positioning
        - Description: Full text with wrapping, fits viewport
        - Total vertical: ~290px (header 40px + sprite 140px + description 80px + indicator 30px)
        """
        # Render sprite (128x128)
        self._render_sprite(surface, size=128)
        
        # Render description panel
        self._render_description_panel(surface)
    
    def _render_stats_tab(self, surface: pygame.Surface):
        """
        Render Stats tab content: sprite (128x128) + stat bars + type badges + physical measurements.
        
        Args:
            surface: pygame.Surface to draw on
            
        Story 5.7 AC #3: Stats tab displays complete stat information
        - Sprite: 128x128 pixels, left side
        - Stat bars: 6 bars with values (HP, Attack, Defense, Sp.Atk, Sp.Def, Speed)
        - Type badges: 1-2 type badges with holographic styling
        - Physical measurements: Height (m), Weight (kg)
        - Total vertical: ~280px (optimized side-by-side layout)
        """
        # Render sprite (128x128)
        self._render_sprite(surface, size=128)
        
        # Render stat bars
        self._render_stat_bars(surface)
        
        # Render type badges
        self._render_type_badges(surface)
        
        # Render physical measurements (height, weight)
        self._render_physical_data(surface)
    
    def _render_evolution_tab(self, surface: pygame.Surface):
        """
        Render Evolution tab content: evolution panel only (no separate sprite).
        
        Args:
            surface: pygame.Surface to draw on
            
        Story 5.7 AC #4: Evolution tab displays evolution chain
        - Evolution panel: 3-stage horizontal layout with requirements
        - Current Pokémon highlighted with cyan glow in evolution panel
        - No separate sprite needed (evolution panel shows all sprites)
        - Story 5.7 Fix: Removed redundant sprite display for cleaner layout
        """
        # Render evolution panel (no separate sprite - panel shows all Pokemon)
        if self.evolution_panel:
            # Position higher without sprite taking up space
            screen_height = surface.get_height()
            is_small_screen = surface.get_width() <= 480
            # Story 5.7 Fix: Position evolution panel higher, leave 45px for tab indicator
            evolution_y = 60 if is_small_screen else 80
            self.evolution_panel.render(surface, x=10 if is_small_screen else 20, y=evolution_y)
    
    def _render_tab_indicator(self, surface: pygame.Surface):
        """
        Render tab indicator at bottom of screen with holographic badge styling.
        
        Args:
            surface: pygame.Surface to draw on
            
        Story 5.7 AC #7: Tab indicator display with holographic styling
        - Three tab badges: "Info", "Stats", "Evolution"
        - Active tab: ELECTRIC_BLUE border/glow, HOLOGRAM_WHITE text, glowing effect
        - Inactive tabs: ICE_BLUE border, ICE_BLUE text, subtle background
        - Positioned at bottom center with badge containers
        - Holographic styling: rounded rectangles, glow effects, semi-transparent backgrounds
        - Always visible regardless of current tab
        
        UX Review (2025-12-08): Enhanced with badge design for better holographic aesthetic
        - Replaces plain text-and-pipes with rounded badge containers
        - Active badge has glowing border and semi-transparent blue background
        - Inactive badges have subtle styling for clear visual hierarchy
        """
        screen_width = surface.get_width()
        screen_height = surface.get_height()
        
        # Tab badge configuration
        tab_labels = ["Info", "Stats", "Evolution"]
        badge_padding_x = 12
        badge_padding_y = 6
        badge_gap = 12
        badge_radius = 4
        badge_height = 24
        
        # Calculate badge widths based on text
        badge_widths = []
        for label in tab_labels:
            text_surface = self.body_font.render(label, True, Colors.HOLOGRAM_WHITE)
            badge_widths.append(text_surface.get_width() + badge_padding_x * 2)
        
        # Center all badges horizontally
        total_width = sum(badge_widths) + badge_gap * (len(tab_labels) - 1)
        start_x = (screen_width - total_width) // 2
        y = screen_height - 35
        
        current_x = start_x
        
        for i, (label, width) in enumerate(zip(tab_labels, badge_widths)):
            is_active = (i == self.current_tab.value)
            
            # Create badge rectangle
            badge_rect = pygame.Rect(current_x, y, width, badge_height)
            
            if is_active:
                # Active tab: glowing electric blue styling
                border_color = Colors.ELECTRIC_BLUE
                border_width = 2
                text_color = Colors.HOLOGRAM_WHITE
                
                # Draw glow effect layers (outer to inner)
                for glow_size in range(3, 0, -1):
                    glow_rect = badge_rect.inflate(glow_size * 2, glow_size * 2)
                    glow_surface = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
                    glow_color = pygame.Color(Colors.ELECTRIC_BLUE)
                    glow_alpha = 20  # Subtle glow
                    pygame.draw.rect(
                        glow_surface,
                        (glow_color.r, glow_color.g, glow_color.b, glow_alpha),
                        glow_surface.get_rect(),
                        border_radius=badge_radius + glow_size
                    )
                    surface.blit(glow_surface, glow_rect.topleft)
                
                # Draw semi-transparent blue background
                badge_surface = pygame.Surface(badge_rect.size, pygame.SRCALPHA)
                bg_color = pygame.Color(Colors.ELECTRIC_BLUE)
                bg_alpha = 51  # 20% opacity
                pygame.draw.rect(
                    badge_surface,
                    (bg_color.r, bg_color.g, bg_color.b, bg_alpha),
                    badge_surface.get_rect(),
                    border_radius=badge_radius
                )
                surface.blit(badge_surface, badge_rect.topleft)
            else:
                # Inactive tab: subtle ice blue styling
                border_color = Colors.ICE_BLUE
                border_width = 1
                text_color = Colors.ICE_BLUE
                
                # Draw very subtle background
                badge_surface = pygame.Surface(badge_rect.size, pygame.SRCALPHA)
                bg_color = pygame.Color(Colors.ICE_BLUE)
                bg_alpha = 13  # 5% opacity
                pygame.draw.rect(
                    badge_surface,
                    (bg_color.r, bg_color.g, bg_color.b, bg_alpha),
                    badge_surface.get_rect(),
                    border_radius=badge_radius
                )
                surface.blit(badge_surface, badge_rect.topleft)
            
            # Draw badge border (rounded rectangle)
            pygame.draw.rect(
                surface,
                border_color,
                badge_rect,
                border_width,
                border_radius=badge_radius
            )
            
            # Draw text centered in badge
            text_surface = self.body_font.render(label, True, text_color)
            text_rect = text_surface.get_rect(center=badge_rect.center)
            surface.blit(text_surface, text_rect)
            
            # Move to next badge position
            current_x += width + badge_gap
    
    def _render_sprite(self, surface: pygame.Surface, size: int = 128):
        """
        Render Pokémon sprite with configurable size.
        
        Args:
            surface: pygame.Surface to draw on
            size: Sprite size in pixels (128 for Info/Stats tabs, 96 for Evolution tab)
            
        Story 3.1 AC #2: 128x128 sprite, 50-60% screen real estate, center-left position
        Story 5.7 AC #4: Evolution tab uses smaller 96x96 sprite to save vertical space
        Sprite has electric blue border for holographic effect
        """
        if not self.sprite:
            return
        
        # Scale sprite if size differs from loaded sprite size
        sprite_to_render = self.sprite
        if self.sprite.get_width() != size:
            sprite_to_render = pygame.transform.scale(self.sprite, (size, size))
        
        # Calculate center-left position (50-60% width allocation)
        screen_width = surface.get_width()
        screen_height = surface.get_height()
        
        # Story 3.7: Adaptive sprite positioning for 480x320
        is_small_screen = screen_width <= 480
        
        # Calculate left zone width (area before stats panel)
        # Stats panel starts at screen_width // 2 + offset
        left_zone_width = screen_width // 2 + (10 if is_small_screen else 20)
        
        # Center sprite horizontally within left zone
        sprite_x = (left_zone_width - size) // 2
        
        # Vertical positioning - keep sprite higher to leave room below
        # For small screen: position higher to leave room for badges + measurements
        if is_small_screen:
            sprite_y = 50  # Fixed top position for small screens
        else:
            sprite_y = screen_height // 2 - size // 2 - 20
        
        # Story 3.7: Store sprite bounds for type badge and measurements positioning
        self._sprite_x = sprite_x
        self._sprite_y = sprite_y
        self._sprite_width = size
        self._sprite_height = size
        self._sprite_bottom_y = sprite_y + size
        self._left_zone_width = left_zone_width  # Store for centering other elements
        
        # Draw holographic border around sprite (AC #5: electric blue)
        border_rect = pygame.Rect(
            sprite_x - 4,
            sprite_y - 4,
            size + 8,
            size + 8
        )
        pygame.draw.rect(surface, Colors.ELECTRIC_BLUE, border_rect, 2)
        
        # Blit sprite to surface
        surface.blit(sprite_to_render, (sprite_x, sprite_y))
    
    def _render_stat_bars(self, surface: pygame.Surface):
        """
        Render all 6 base stats with visual progress bars.
        
        Args:
            surface: pygame.Surface to draw on
            
        Story 3.2 Implementation:
        AC #1: Display all 6 stats (HP, Attack, Defense, Sp.Atk, Sp.Def, Speed)
        AC #2: Proportional bar width (base_stat / 255) * max_bar_width
        AC #3: Color-coded bars by value ranges
        AC #4: Glow effect for high stats (>= 100)
        AC #5: Labels and values with proper fonts and colors
        AC #6: Stats panel layout on right side with holographic styling
        AC #9: Rendering must complete in < 10ms per frame
        
        Story 3.7 Updates:
        AC #4: Use STAT_LABEL_MAP for proper label formatting (HP, Sp.Atk, etc.)
        AC #5: All 6 stats visible with 8px spacing, adaptive for 480x320
        """
        if not self.stats:
            # No stats loaded - show placeholder or skip
            return
        
        start_time = time.perf_counter()
        
        # Stats panel positioning (right side, ~45% width)
        screen_width = surface.get_width()
        screen_height = surface.get_height()
        
        # Story 3.7: Adaptive layout for 480x320 and 800x480
        # For 480x320: tighter spacing, smaller panel
        # For 800x480: more comfortable spacing
        is_small_screen = screen_width <= 480
        
        STATS_PANEL_X = screen_width // 2 + (10 if is_small_screen else 20)
        STATS_PANEL_Y = 50 if is_small_screen else 60
        STATS_PANEL_WIDTH = screen_width // 2 - (20 if is_small_screen else 40)
        
        # Story 3.7 AC #5: Calculate panel height to fit all 6 stats
        # Row height + spacing calculation ensures no cutoff
        STAT_BAR_HEIGHT = 14 if is_small_screen else 18
        STAT_SPACING = 22 if is_small_screen else 28
        PADDING = 10 if is_small_screen else 16
        
        # Height = top padding + (6 stats * spacing) + bottom padding
        STATS_PANEL_HEIGHT = PADDING + (6 * STAT_SPACING) + PADDING
        
        # Draw stats panel background (AC #6: holographic blue styling)
        panel_surface = pygame.Surface((STATS_PANEL_WIDTH, STATS_PANEL_HEIGHT), pygame.SRCALPHA)
        panel_surface.fill((*Colors.DARK_BLUE, 230))  # 0.9 alpha ~= 230
        pygame.draw.rect(panel_surface, Colors.ELECTRIC_BLUE, 
                        pygame.Rect(0, 0, STATS_PANEL_WIDTH, STATS_PANEL_HEIGHT), 2)
        surface.blit(panel_surface, (STATS_PANEL_X, STATS_PANEL_Y))
        
        # Stat bar layout constants - adaptive for screen size
        # Layout: [PADDING][LABEL 50px][GAP 4px][BAR variable][GAP 4px][VALUE 30px][PADDING]
        LABEL_WIDTH = 50 if is_small_screen else 60
        VALUE_WIDTH = 30 if is_small_screen else 35
        GAP = 4
        
        # Calculate positions within panel
        STAT_LABEL_X = STATS_PANEL_X + PADDING
        STAT_BAR_X = STAT_LABEL_X + LABEL_WIDTH + GAP
        STAT_VALUE_X = STATS_PANEL_X + STATS_PANEL_WIDTH - PADDING
        
        # Bar width = panel width - padding*2 - label - value - gaps
        STAT_BAR_MAX_WIDTH = STATS_PANEL_WIDTH - (PADDING * 2) - LABEL_WIDTH - VALUE_WIDTH - (GAP * 2)
        
        # Render each of the 6 stats (AC #1)
        for i, stat_dict in enumerate(self.stats[:6]):  # Limit to 6 stats
            y = STATS_PANEL_Y + PADDING + (i * STAT_SPACING)
            
            stat_name = stat_dict.get('name', '???')
            base_stat = stat_dict.get('base_stat', 0)
            
            # Story 3.2 AC #8: Validate and clamp stat values
            if base_stat is None:
                base_stat = 0
                logging.warning(f"Null stat value for {stat_name} on Pokemon #{self.pokemon_id}")
            
            if base_stat < 0 or base_stat > 255:
                logging.warning(f"Stat value {base_stat} for {stat_name} clamped to 0-255")
                base_stat = max(0, min(255, base_stat))
            
            # Calculate bar width (AC #2: proportional to stat value)
            bar_width = max(1, int((base_stat / 255) * STAT_BAR_MAX_WIDTH))
            
            # Get bar color (AC #3: color-coded by value)
            bar_color = get_stat_color(base_stat)
            
            # Draw empty bar background (dark gray)
            bg_rect = pygame.Rect(STAT_BAR_X, y, STAT_BAR_MAX_WIDTH, STAT_BAR_HEIGHT)
            pygame.draw.rect(surface, (40, 40, 40), bg_rect)
            
            # Draw filled bar (stat color)
            bar_rect = pygame.Rect(STAT_BAR_X, y, bar_width, STAT_BAR_HEIGHT)
            pygame.draw.rect(surface, bar_color, bar_rect)
            
            # AC #4: Glow effect for high stats (>= 100)
            if base_stat >= 100:
                # Draw glow bar with alpha=128, offset +2px
                glow_surface = pygame.Surface((bar_width, STAT_BAR_HEIGHT), pygame.SRCALPHA)
                glow_rect = pygame.Rect(2, 2, bar_width - 2, STAT_BAR_HEIGHT - 2)
                pygame.draw.rect(glow_surface, (*bar_color, 128), glow_rect)
                surface.blit(glow_surface, (STAT_BAR_X, y))
            
            # AC #5: Render stat label (left-aligned, ice blue)
            # Story 3.7 AC #4: Use STAT_LABEL_MAP for proper formatting
            if self.stat_label_font:
                display_name = format_stat_label(stat_name)
                label_surface = self.stat_label_font.render(display_name, True, Colors.ICE_BLUE)
                surface.blit(label_surface, (STAT_LABEL_X, y + 2))
            
            # AC #5: Render stat value (right-aligned, white, monospace)
            if self.stat_value_font:
                value_text = str(base_stat) if base_stat is not None else "???"
                value_surface = self.stat_value_font.render(value_text, True, Colors.HOLOGRAM_WHITE)
                value_rect = value_surface.get_rect(right=STAT_VALUE_X, top=y + 1)
                surface.blit(value_surface, value_rect)
        
        # Performance logging (AC #9: < 10ms target)
        render_time = (time.perf_counter() - start_time) * 1000
        if render_time > 10:
            logging.warning(f"Stat bars rendered in {render_time:.2f}ms (target: <10ms)")
        else:
            logging.debug(f"Stat bars rendered in {render_time:.2f}ms")
    
    def _lighten_color(self, color: tuple, percent: int = 20) -> tuple:
        """
        Lighten a color by percentage for badge borders.
        
        Args:
            color: Original RGB color tuple
            percent: Percentage to lighten (default 20%)
            
        Returns:
            Lightened RGB color, clamped to 255
            
        Story 3.3 AC #3: Border uses lighter shade of type color
        """
        return tuple(min(255, int(c * (1 + percent / 100))) for c in color)
    
    def _render_type_badge(self, surface: pygame.Surface, type_name: str, x: int, y: int) -> int:
        """
        Render a single type badge with rounded rectangle and text.
        
        Args:
            surface: Target surface to draw on
            type_name: Type name (e.g., "Fire", "Electric")
            x: X position for badge top-left
            y: Y position for badge top-left
            
        Returns:
            Width of rendered badge (for positioning next badge)
            
        Story 3.3 Implementation:
        AC #1, #2: Single and dual type badge rendering
        AC #3: Rounded rectangle (8px radius), 2px border, type-specific colors
        AC #5: Rajdhani Bold 14px, white text, uppercase, centered
        AC #9: Fixed height, auto width (80-120px), padding
        Story 5.7 Fix: Reduced height from 32px to 28px for better vertical spacing
        """
        # Badge dimension constants
        HEIGHT = 28  # Story 5.7 Fix: Reduced from 32px to save vertical space
        PADDING_X = 16
        PADDING_Y = 6
        BORDER_RADIUS = 8
        BORDER_WIDTH = 2
        
        # Get type color, default to gray if unknown (AC #8: error handling)
        type_lower = type_name.lower()
        if type_lower not in TYPE_COLORS:
            logging.warning(f"Unknown type '{type_name}', using default gray")
            bg_color = (128, 128, 128)  # Default gray
        else:
            bg_color = TYPE_COLORS[type_lower]
        
        border_color = self._lighten_color(bg_color, 20)
        
        # Render text to measure width (AC #5: uppercase)
        if not self.type_badge_font:
            return 0  # Can't render without font
        
        text_surface = self.type_badge_font.render(type_name.upper(), True, Colors.HOLOGRAM_WHITE)
        text_width = text_surface.get_width()
        
        # Calculate badge width (AC #9: min 80px, max 120px, auto-adjust)
        badge_width = max(80, min(120, text_width + (PADDING_X * 2)))
        
        # Draw rounded rectangle background (AC #3)
        badge_rect = pygame.Rect(x, y, badge_width, HEIGHT)
        pygame.draw.rect(surface, bg_color, badge_rect, border_radius=BORDER_RADIUS)
        
        # Draw border (AC #3: 2px solid, lighter shade)
        pygame.draw.rect(surface, border_color, badge_rect, BORDER_WIDTH, border_radius=BORDER_RADIUS)
        
        # Center text within badge (AC #5: centered horizontally and vertically)
        text_rect = text_surface.get_rect(center=(x + badge_width // 2, y + HEIGHT // 2))
        surface.blit(text_surface, text_rect)
        
        return badge_width
    
    def _render_type_badges(self, surface: pygame.Surface):
        """
        Render all type badges (1 or 2) below the sprite in LEFT ZONE.
        
        Args:
            surface: pygame.Surface to draw on
            
        Story 3.3 Implementation:
        AC #1: Single type display (one badge)
        AC #2: Dual type display (two badges side-by-side, 8px spacing)
        AC #4: Positioned near sprite without overlapping sprite or stats
        AC #10: Performance target <5ms per frame
        
        Story 3.7 Updates (AC #8):
        - Badges positioned 8px BELOW sprite bottom edge (not over sprite)
        - Badges centered relative to sprite width in LEFT ZONE
        - Badges don't overlap with stats panel (right zone)
        """
        if not self.types or not self.type_badge_font:
            return  # No types to display or font not loaded
        
        start_time = time.perf_counter()
        
        screen_width = surface.get_width()
        is_small_screen = screen_width <= 480
        
        # Story 3.7 AC #8: Position badges 8px below sprite bottom edge
        # Use sprite bounds stored by _render_sprite()
        sprite_bottom = getattr(self, '_sprite_bottom_y', 180)
        left_zone_width = getattr(self, '_left_zone_width', screen_width // 2 + 10)
        
        BADGE_SPACING = 8  # AC #2: 8px spacing between dual-type badges
        # Story 5.7 Fix: Increase margin to prevent overlap with height/weight below
        BADGE_MARGIN_TOP = 12 if is_small_screen else 8  # Story 3.7: margin below sprite
        
        # Calculate total width of badges for centering
        badge_widths = []
        for type_name in self.types:
            # Estimate badge width (same calculation as _render_type_badge)
            text_surface = self.type_badge_font.render(type_name.upper(), True, Colors.HOLOGRAM_WHITE)
            text_width = text_surface.get_width()
            badge_width = max(80, min(120, text_width + 32))  # 16px padding each side
            badge_widths.append(badge_width)
        
        total_badges_width = sum(badge_widths) + (BADGE_SPACING * (len(badge_widths) - 1)) if badge_widths else 0
        
        # Center badges within left zone
        badges_start_x = (left_zone_width - total_badges_width) // 2
        TYPES_Y = sprite_bottom + BADGE_MARGIN_TOP
        
        # Store badge bottom for physical measurements positioning
        # Story 5.7 Fix: Updated from 32px to 28px to match new badge height
        self._badges_bottom_y = TYPES_Y + 28  # Badge height is 28px
        
        # Render badges
        x = badges_start_x
        for type_name in self.types:
            badge_width = self._render_type_badge(surface, type_name, x, TYPES_Y)
            x += badge_width + BADGE_SPACING  # Position next badge
        
        # Performance logging (AC #10: <5ms target)
        render_time = (time.perf_counter() - start_time) * 1000
        if render_time > 5:
            logging.warning(f"Type badges rendered in {render_time:.2f}ms (target: <5ms)")
        else:
            logging.debug(f"Type badges rendered in {render_time:.2f}ms")
    
    def _render_physical_data(self, surface: pygame.Surface):
        """
        Render height and weight measurements with labels and values.
        
        Args:
            surface: pygame.Surface to draw on
            
        Story 3.4 Implementation:
        AC #1: Height displayed in meters with format "X.Xm" (one decimal place)
        AC #2: Weight displayed in kilograms with format "X.Xkg" (one decimal place)
        AC #3: Positioned in lower section without overlapping sprite, stats, types
        AC #4: Labels right-aligned (80px width), values left-aligned (10px offset), 8px spacing
        AC #9: Labels ice blue (#a8e6ff), values white (#ffffff), Rajdhani 16px
        AC #10: Rendering must complete in < 2ms per frame
        
        Story 3.7 Updates (AC #6):
        - Position in LEFT ZONE below type badges (not in description panel)
        - 12px margin below type badge before height line
        - 8px vertical gap between height and weight lines
        - Plain text (NO panel border)
        - Labels use ice blue, values use white
        """
        if self.height == 0.0 and self.weight == 0.0:
            return  # No data loaded yet
        
        start_time = time.perf_counter()
        
        screen_width = surface.get_width()
        screen_height = surface.get_height()
        is_small_screen = screen_width <= 480
        
        # Story 3.7 AC #6: Position in LEFT ZONE below type badges
        # Use badge bottom stored by _render_type_badges(), or calculate fallback
        badges_bottom = getattr(self, '_badges_bottom_y', 220)
        left_zone_width = getattr(self, '_left_zone_width', screen_width // 2 + 10)
        
        # Story 5.7 Fix: On Stats tab there's no description panel below
        # Leave room for tab indicator at bottom (35px from bottom)
        # Plus safety margin of 10px = 45px total
        tab_indicator_space = 45
        max_y_position = screen_height - tab_indicator_space
        
        # Use body_font (16px) for physical data - matches Rajdhani 16px spec
        if not self.body_font:
            return  # Can't render without font
        
        # Get font height for calculations
        font_height = self.body_font.get_height()
        
        # Calculate required space for height + weight (2 lines + spacing)
        LINE_SPACING = 4 if is_small_screen else 8  # Tighter on small screens
        required_height = (font_height * 2) + LINE_SPACING
        
        # Position measurements below badges with adequate spacing
        # Story 5.7 Fix: Ensure measurements don't overlap badges OR tab indicator
        MARGIN_BELOW_BADGE = 20 if is_small_screen else 24  # Increased for better separation
        
        # Calculate Y position: start from badges + margin, but don't go below tab indicator
        ideal_y = badges_bottom + MARGIN_BELOW_BADGE
        max_allowed_y = max_y_position - required_height - 4  # 4px safety margin
        
        PHYSICAL_DATA_Y = min(ideal_y, max_allowed_y)
        
        # Format values with placeholders for invalid data (AC #6, #7, #8)
        height_str = f"{self.height:.1f}m" if self.height > 0 else "???"
        weight_str = f"{self.weight:.1f}kg" if self.weight > 0 else "???"
        
        # Story 3.7 AC #6: Height line - "Height: X.Xm" with ice blue label, white value
        height_label = self.body_font.render("Height: ", True, Colors.ICE_BLUE)
        height_value = self.body_font.render(height_str, True, Colors.HOLOGRAM_WHITE)
        
        # Calculate total width and center within left zone
        height_total_width = height_label.get_width() + height_value.get_width()
        height_x = (left_zone_width - height_total_width) // 2
        
        surface.blit(height_label, (height_x, PHYSICAL_DATA_Y))
        surface.blit(height_value, (height_x + height_label.get_width(), PHYSICAL_DATA_Y))
        
        # Story 3.7 AC #6: Weight line - below height with spacing
        weight_y = PHYSICAL_DATA_Y + font_height + LINE_SPACING
        
        weight_label = self.body_font.render("Weight: ", True, Colors.ICE_BLUE)
        weight_value = self.body_font.render(weight_str, True, Colors.HOLOGRAM_WHITE)
        
        # Center weight line within left zone
        weight_total_width = weight_label.get_width() + weight_value.get_width()
        weight_x = (left_zone_width - weight_total_width) // 2
        
        surface.blit(weight_label, (weight_x, weight_y))
        surface.blit(weight_value, (weight_x + weight_label.get_width(), weight_y))
        
        # Performance logging (AC #10: < 2ms target)
        render_time = (time.perf_counter() - start_time) * 1000
        if render_time > 2:
            logging.warning(f"Physical data rendered in {render_time:.2f}ms (target: <2ms)")
        else:
            logging.debug(f"Physical data rendered in {render_time:.2f}ms)")
    
    def _wrap_description_text(self, text: str, font: pygame.font.Font, 
                               max_width: int, max_lines: int) -> List[str]:
        """
        Wrap text at word boundaries to fit within max_width.
        
        Args:
            text: Description text to wrap
            font: pygame Font object for measuring text width
            max_width: Maximum width in pixels per line
            max_lines: Maximum number of lines to return
            
        Returns:
            List of wrapped lines (max max_lines entries)
            
        Story 3.5 AC #2: Wraps at word boundaries (not mid-word)
        Story 3.5 AC #3: Maximum 4 lines displayed
        Story 3.5 AC #4: Truncates with ellipsis if exceeds max_lines
        """
        if not text:
            return []
        
        lines = []
        words = text.split(' ')
        current_line = ""
        
        for word in words:
            # Test if adding this word would exceed max_width
            test_line = current_line + (" " if current_line else "") + word
            test_width = font.size(test_line)[0]
            
            if test_width <= max_width:
                # Word fits, add to current line
                current_line = test_line
            else:
                # Word doesn't fit, finalize current line and start new one
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    # Single word exceeds max_width - force add it
                    lines.append(word)
                    current_line = ""
            
            # Stop if we've reached max_lines
            if len(lines) >= max_lines:
                break
        
        # Add final line if not empty and room exists
        if current_line and len(lines) < max_lines:
            lines.append(current_line)
        
        # Handle truncation with ellipsis (AC #4)
        if len(lines) >= max_lines and len(words) > 0:
            # Check if we truncated text (more words exist)
            words_in_lines = sum(len(line.split()) for line in lines)
            if words_in_lines < len(words):
                # More text exists, need ellipsis
                last_line = lines[max_lines - 1]
                
                # Try adding ellipsis
                if font.size(last_line + "...")[0] <= max_width:
                    lines[max_lines - 1] = last_line + "..."
                else:
                    # Shorten last line to fit ellipsis
                    while len(last_line) > 0 and font.size(last_line + "...")[0] > max_width:
                        last_line = last_line[:-1].rstrip()
                    lines[max_lines - 1] = last_line + "..."
        
        return lines[:max_lines]
    
    def _render_description_lines(self):
        """
        Pre-render description text to surfaces for efficient blitting.
        
        Story 3.5 AC #9: Text wrapped and rendered in on_enter() (not per frame)
        Story 3.5 AC #9: Cached in self.description_lines for render() to blit
        Story 3.5 AC #9: Pre-rendering must complete in < 5ms
        """
        self.description_lines = []
        
        if not self.description_font or not self.description:
            return
        
        start_time = time.perf_counter()
        
        # Story 3.5 AC #2, #3, #4: Wrap text to max 4 lines, 400px width
        wrapped_lines = self._wrap_description_text(
            self.description, 
            self.description_font, 
            max_width=400, 
            max_lines=4
        )
        
        # Render each line to surface (cache for blit) - AC #5: ice blue color
        for line_text in wrapped_lines:
            line_surface = self.description_font.render(line_text, True, Colors.ICE_BLUE)
            self.description_lines.append(line_surface)
        
        # Performance logging (AC #9: < 5ms target, changed from 50ms per spec clarification)
        render_time = (time.perf_counter() - start_time) * 1000
        if render_time > 5:
            logging.warning(f"Description pre-rendering took {render_time:.2f}ms (target: <5ms)")
        else:
            logging.debug(f"Description pre-rendered in {render_time:.2f}ms")
    
    def _render_description_panel(self, surface: pygame.Surface):
        """
        Render description panel with pre-rendered text lines.
        
        Args:
            surface: pygame.Surface to draw on
            
        Story 3.5 Implementation:
        AC #1: Authentic description text from database
        AC #5: Typography: Rajdhani 16px, ice blue (#a8e6ff)
        AC #6: Layout in lower section with holographic styling
        AC #10: Blit performance < 5ms per frame
        """
        if not self.description_lines:
            return  # No description to render
        
        start_time = time.perf_counter()
        
        # Description panel positioning (AC #6: lower section)
        screen_width = surface.get_width()
        screen_height = surface.get_height()
        
        # Story 3.7: Adaptive layout for 480x320
        is_small_screen = screen_width <= 480
        
        DESC_PANEL_X = 10 if is_small_screen else 20
        # Story 5.7 Fix: Leave 45px at bottom for tab indicator to prevent overlap
        DESC_PANEL_Y = screen_height - (145 if is_small_screen else 185)
        DESC_PANEL_WIDTH = screen_width - (20 if is_small_screen else 40)
        DESC_PANEL_HEIGHT = 80 if is_small_screen else 120
        DESC_TEXT_X = DESC_PANEL_X + (8 if is_small_screen else 16)  # padding
        DESC_TEXT_Y = DESC_PANEL_Y + (8 if is_small_screen else 16)
        DESC_LINE_HEIGHT = 18 if is_small_screen else 22.4  # Tighter for small screens
        
        # Draw panel background (AC #6: holographic blue styling)
        panel_surface = pygame.Surface((DESC_PANEL_WIDTH, DESC_PANEL_HEIGHT), pygame.SRCALPHA)
        panel_surface.fill((*Colors.DARK_BLUE, 230))  # rgba(26, 47, 74, 0.9)
        pygame.draw.rect(panel_surface, Colors.ELECTRIC_BLUE, 
                        pygame.Rect(0, 0, DESC_PANEL_WIDTH, DESC_PANEL_HEIGHT), 2)
        surface.blit(panel_surface, (DESC_PANEL_X, DESC_PANEL_Y))
        
        # Blit pre-rendered description lines (AC #9: no text processing per frame)
        for i, line_surface in enumerate(self.description_lines):
            y = DESC_TEXT_Y + int(i * DESC_LINE_HEIGHT)
            surface.blit(line_surface, (DESC_TEXT_X, y))
        
        # Performance logging (AC #10: < 5ms target)
        render_time = (time.perf_counter() - start_time) * 1000
        if render_time > 5:
            logging.warning(f"Description blit took {render_time:.2f}ms (target: <5ms)")
        else:
            logging.debug(f"Description blit completed in {render_time:.2f}ms")

