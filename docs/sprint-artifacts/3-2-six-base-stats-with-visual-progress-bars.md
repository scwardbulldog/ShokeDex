# Story 3.2: Six Base Stats with Visual Progress Bars

Status: ready-for-dev

## Story

As a user,
I want to see all six base stats with visual bars,
So that I can quickly compare a Pokémon's strengths and weaknesses.

## Acceptance Criteria

1. **Six Base Stats Display (AC #1)**
   - **Given** DetailScreen is displaying a Pokémon
   - **When** the stats section renders
   - **Then** all 6 base stats are shown: HP, Attack, Defense, Sp.Atk, Sp.Def, Speed
   - **And** stats are displayed in canonical order (HP first, Speed last)
   - **And** each stat displays three elements: label (left), visual progress bar (center), numeric value (right)
   - **And** stat values are accurate from database (no hardcoded values)
   - **And** stats panel is positioned on the right side of the screen

2. **Proportional Bar Width (AC #2)**
   - **Given** a Pokémon has base stats with various values
   - **When** stat bars render
   - **Then** bar width is proportional to stat value: (base_stat / 255) * max_bar_width
   - **And** stat of 255 (max) fills bar completely (100%)
   - **And** stat of 1 (min) shows minimal visible bar (not invisible)
   - **And** stat of 127-128 (half max) fills approximately 50% of bar
   - **And** all bars have the same max width for visual comparison

3. **Stat Bar Color Coding (AC #3)**
   - **Given** stats have different value ranges
   - **When** stat bars render with colors
   - **Then** stats 0-50 use Gray color (#718096)
   - **And** stats 51-100 use Electric blue (#00d4ff)
   - **And** stats 101-150 use Bright cyan (#4df7ff)
   - **And** stats 151+ use Plasma orange (#ff6b35)
   - **And** color choice makes high stats visually prominent

4. **High Stat Glow Effect (AC #4)**
   - **Given** a stat value is 100 or higher
   - **When** the stat bar renders
   - **Then** a subtle glow effect is applied to the bar
   - **And** glow is implemented by drawing a second bar with alpha=128, offset by 2px
   - **And** glow uses the same stat color as the main bar
   - **And** glow effect does not impact frame rate (target: 30+ FPS)

5. **Stat Labels and Values Display (AC #5)**
   - **Given** each stat has a name and numeric value
   - **When** stat section renders
   - **Then** stat labels use Share Tech Mono font, 14px, ice blue color (#a8e6ff)
   - **And** stat labels are left-aligned within stats panel
   - **And** stat values use Share Tech Mono font, 16px, white color (#ffffff)
   - **And** stat values are right-aligned within stats panel
   - **And** monospace font ensures values align vertically for easy comparison

6. **Stats Panel Layout (AC #6)**
   - **Given** DetailScreen displays with sprite on left and stats on right
   - **When** stats panel renders
   - **Then** panel is positioned on right side of screen (40% width per layout spec)
   - **And** panel uses holographic blue styling: dark blue background rgba(26, 47, 74, 0.9)
   - **And** panel border is 2px solid electric blue (#00d4ff)
   - **And** all 6 stat bars fit within panel without overflow
   - **And** 16px padding between panel edge and stat elements
   - **And** stats panel does not overlap sprite or other UI elements

7. **Database Query Integration (AC #7)**
   - **Given** DetailScreen needs to load stat data
   - **When** DetailScreen._load_pokemon_data() executes
   - **Then** Database.get_pokemon_stats(pokemon_id) is called
   - **And** query returns List[Tuple[str, int]] with 6 stat entries
   - **And** query completes in < 50ms (per performance target)
   - **And** query uses parameterized statement (SQL injection prevention)
   - **And** all 6 stats are validated (HP, Attack, Defense, Sp.Atk, Sp.Def, Speed)

8. **Error Handling and Data Validation (AC #8)**
   - **Given** database query returns unexpected data
   - **When** stats are processed
   - **Then** if stat count ≠ 6, warning is logged and missing stats show "???" placeholder
   - **And** if stat value < 0 or > 255, value is clamped and warning logged
   - **And** if stat value is null/missing, "???" placeholder displayed
   - **And** application does not crash on invalid stat data
   - **And** error messages logged for debugging: "Stats query returned {count}, expected 6"

9. **Performance Requirements (AC #9)**
   - **Given** DetailScreen renders with stat bars
   - **When** any operation occurs
   - **Then** frame rate maintains 30+ FPS during rendering
   - **And** stat bar rendering completes in < 10ms per frame
   - **And** glow effects do not cause frame drops
   - **And** DetailScreen total render time remains < 33ms per frame

## Tasks / Subtasks

- [ ] **Task 1: Implement Database Query for Stats** (AC: #7)
  - [ ] Create `Database.get_pokemon_stats(pokemon_id: int)` method if not exists
  - [ ] Use parameterized query: `SELECT s.name, ps.base_stat FROM stats s JOIN pokemon_stats ps ON s.id = ps.stat_id WHERE ps.pokemon_id = ? ORDER BY s.id`
  - [ ] Return List[Tuple[str, int]] with stat entries in canonical order
  - [ ] Profile query time with `time.perf_counter()`, assert < 50ms
  - [ ] Add unit test: `test_get_pokemon_stats_returns_six_values()`
  - [ ] Test with multiple Pokémon IDs (Pikachu #25, Bulbasaur #1, Deoxys #386)

- [ ] **Task 2: Load Stats in DetailScreen Lifecycle** (AC: #7)
  - [ ] Modify `DetailScreen._load_pokemon_data()` to call `get_pokemon_stats(pokemon_id)`
  - [ ] Store result in `self.stats: List[Tuple[str, int]]` instance variable
  - [ ] Validate stat count equals 6, log warning if not
  - [ ] Add error handling: try/except with logging for database failures
  - [ ] Verify stats loaded in `on_enter()` before first render

- [ ] **Task 3: Create Stat Bar Color Mapping Function** (AC: #3)
  - [ ] Define STAT_COLORS constant dict in `src/ui/colors.py` or DetailScreen:
    ```python
    STAT_COLORS = {
        'low': (113, 128, 150),      # 0-50: Gray
        'medium': (0, 212, 255),     # 51-100: Electric blue
        'high': (77, 247, 255),      # 101-150: Bright cyan
        'exceptional': (255, 107, 53) # 151+: Plasma orange
    }
    ```
  - [ ] Implement `get_stat_color(value: int) -> Tuple[int, int, int]`:
    ```python
    if value <= 50: return STAT_COLORS['low']
    elif value <= 100: return STAT_COLORS['medium']
    elif value <= 150: return STAT_COLORS['high']
    else: return STAT_COLORS['exceptional']
    ```
  - [ ] Add unit tests for each color range boundary (50, 51, 100, 101, 150, 151, 255)

- [ ] **Task 4: Implement Stat Bar Rendering Logic** (AC: #1, #2, #4)
  - [ ] Create `DetailScreen._render_stat_bars(surface: pygame.Surface)` method
  - [ ] Define layout constants:
    - STATS_PANEL_X = screen_width * 0.55 (right side)
    - STATS_PANEL_WIDTH = screen_width * 0.40
    - STAT_BAR_HEIGHT = 18
    - STAT_BAR_MAX_WIDTH = STATS_PANEL_WIDTH - 120 (room for label + value)
    - STAT_SPACING = 28 (vertical spacing between bars)
  - [ ] For each stat in self.stats (6 iterations):
    - Calculate y position: STATS_PANEL_Y + (index * STAT_SPACING)
    - Extract stat_name, base_stat from tuple
    - Calculate bar_width: (base_stat / 255) * STAT_BAR_MAX_WIDTH
    - Get bar_color: get_stat_color(base_stat)
    - Draw background bar (empty state): dark gray, full max width
    - Draw filled bar: bar_color, calculated width
    - If base_stat >= 100: Draw glow bar with alpha=128, offset +2px
    - Render stat label (left): Share Tech Mono 14px, ice blue
    - Render stat value (right): Share Tech Mono 16px, white, right-aligned

- [ ] **Task 5: Apply Holographic Styling to Stats Panel** (AC: #6)
  - [ ] Define stats panel rectangle: (STATS_PANEL_X, STATS_PANEL_Y, STATS_PANEL_WIDTH, STATS_PANEL_HEIGHT)
  - [ ] Create panel surface with SRCALPHA for transparency
  - [ ] Fill with PANEL_BG color: rgba(26, 47, 74, 0.9)
  - [ ] Draw 2px electric blue border (#00d4ff) around panel
  - [ ] Add 16px padding between panel edge and first stat bar
  - [ ] Ensure panel background renders before stat bars (z-order)
  - [ ] Verify visual consistency with sprite panel and header

- [ ] **Task 6: Implement Font Loading for Stat Labels/Values** (AC: #5)
  - [ ] In `DetailScreen.on_enter()`, load fonts:
    - `stat_label_font = pygame.font.Font("Share Tech Mono", 14)` or fallback
    - `stat_value_font = pygame.font.Font("Share Tech Mono", 16)` or fallback
  - [ ] Cache fonts in instance variables to avoid reloading each frame
  - [ ] Handle missing font: Use `pygame.font.Font(None, size)` as fallback
  - [ ] Log warning if custom font not found

- [ ] **Task 7: Implement Data Validation and Error Handling** (AC: #8)
  - [ ] In `_load_pokemon_data()`, validate stat count:
    ```python
    if len(self.stats) != 6:
        logging.warning(f"Stats query returned {len(self.stats)}, expected 6")
    ```
  - [ ] In `_render_stat_bars()`, validate stat values:
    ```python
    if base_stat is None:
        base_stat = 0  # or show "???" placeholder
        logging.warning(f"Null stat value for {stat_name}")
    if base_stat < 0 or base_stat > 255:
        base_stat = max(0, min(255, base_stat))
        logging.warning(f"Stat value {base_stat} clamped to 0-255")
    ```
  - [ ] Test with invalid data: mock database return with 5 stats, negative value, null value

- [ ] **Task 8: Performance Optimization** (AC: #9)
  - [ ] Profile stat bar rendering with PerformanceMonitor:
    ```python
    start = time.perf_counter()
    self._render_stat_bars(surface)
    elapsed = time.perf_counter() - start
    logging.debug(f"Stat bars rendered in {elapsed*1000:.2f}ms")
    ```
  - [ ] Optimize if > 10ms:
    - Pre-calculate bar widths and colors in on_enter() (cache in instance var)
    - Use dirty rects to only update stat panel region
    - Simplify glow effect or make it optional
  - [ ] Verify frame rate stays 30+ FPS with PerformanceMonitor.get_average_fps()
  - [ ] Test with rapid L/R navigation (stress test stat loading/rendering)

- [ ] **Task 9: Integration Testing** (AC: All)
  - [ ] Create integration tests in `tests/test_detail_screen.py`:
    - `test_six_stats_display()` - Verify all 6 stats rendered with labels and values
    - `test_stat_bar_proportional_width()` - Verify bar width matches stat value
    - `test_stat_color_coding()` - Verify correct colors for low/medium/high/exceptional
    - `test_stat_glow_effect()` - Verify glow applied to stats >= 100
    - `test_stats_panel_layout()` - Verify panel positioning and styling
    - `test_missing_stats_handled()` - Mock database return with < 6 stats, verify graceful handling
  - [ ] Test with specific Pokémon:
    - Pikachu #25: Mixed stats, some above/below 100
    - Shedinja #292: HP=1 (edge case - minimal bar visible)
    - Blissey #242: HP=255 (edge case - bar fills completely)
    - Mewtwo #150: High stats (multiple stats > 100, test glow)
  - [ ] Visual verification: Compare rendered stats to UX spec mockup

- [ ] **Task 10: Update Tests and Documentation** (AC: All)
  - [ ] Run all existing tests to verify no regressions
  - [ ] Add docstrings to new methods explaining stat rendering logic
  - [ ] Update TESTING.md with stat rendering test coverage
  - [ ] Document STAT_COLORS constant and get_stat_color() usage

## Dev Notes

### Learnings from Previous Story

**From Story 3-1-detail-screen-layout-and-sprite-display (Status: review)**

Story 3.1 established the DetailScreen foundation with layout, sprite display, and placeholder panels. This story builds directly on that infrastructure:

**Infrastructure Ready:**
- DetailScreen class exists with Screen lifecycle (on_enter/on_exit/update/render)
- Manager access pattern established via screen_manager injection
- StateManager integration working (set_last_viewed on enter, save_state on exit)
- SpriteLoader integrated for detail sprites (128x128)
- Holographic blue styling applied to panels (dark blue bg, electric blue borders)
- Placeholder panels created for stats (right side), types, physical data, description
- Error handling patterns established (text placeholders, friendly messages)

**Performance Baseline:**
- DetailScreen render time: < 10ms average (well under 33ms target)
- Transition time HomeScreen → DetailScreen: < 50ms
- Frame rate consistently 30+ FPS
- Database query time: < 10ms for get_pokemon_by_id()
- All performance targets exceeded by wide margins

**Stats Panel Placeholder:**
- Stats panel area already defined on right side (40% screen width)
- Panel uses holographic styling (dark blue background, electric blue border)
- 16px padding established around panel edges
- This story fills in the stats panel with actual stat bars and values

**What This Story Adds:**
- Database.get_pokemon_stats(pokemon_id) method (new or verify exists)
- Stat data loading in DetailScreen._load_pokemon_data()
- Stat bar rendering with proportional widths and color coding
- Glow effect for high stats (>= 100)
- Stat labels and values with Share Tech Mono font
- Data validation and error handling for stat queries

[Source: docs/sprint-artifacts/3-1-detail-screen-layout-and-sprite-display.md#Completion-Notes-List]

---

**From Epic 1 Stories - Performance Patterns**

Epic 1 (Stories 1.1-1.7) established performance patterns and optimization strategies that apply to stat rendering:

**Rendering Optimization Patterns:**
- Pre-render static elements in on_enter() to avoid per-frame overhead
- Cache fonts and colors in instance variables (don't reload each frame)
- Use dirty rects if full screen flip impacts performance
- Profile with PerformanceMonitor to identify bottlenecks
- Target: Individual render operations < 10ms, total frame < 33ms

**Color Constants Pattern:**
- Define color constants in src/ui/colors.py or at module level
- Use tuple format: (r, g, b) for RGB, (r, g, b, a) for RGBA
- Holographic blue palette already established for consistency

**Font Loading Pattern:**
- Load fonts once in on_enter(), cache in instance variables
- Use pygame.font.Font(None, size) as fallback for missing custom fonts
- Log warning if custom font not available
- Monospace fonts (Share Tech Mono) ideal for aligned numeric values

[Source: docs/sprint-artifacts/1-7-performance-optimization-and-3-press-navigation-rule.md#Dev-Notes]

### Architecture Context

This story implements the **stat visualization** component from the DetailScreen architecture, following established database query patterns and rendering optimizations.

**Database Access Pattern (from Architecture):**

```python
# ✅ CORRECT - Parameterized query
def get_pokemon_stats(self, pokemon_id: int) -> List[Tuple[str, int]]:
    cursor = self.conn.execute(
        """SELECT s.name, ps.base_stat 
           FROM stats s 
           JOIN pokemon_stats ps ON s.id = ps.stat_id 
           WHERE ps.pokemon_id = ? 
           ORDER BY s.id""",
        (pokemon_id,)
    )
    return cursor.fetchall()

# ❌ INCORRECT - Never use string formatting
query = f"SELECT * FROM stats WHERE pokemon_id = {pokemon_id}"  # SQL injection risk
```

**Stat Rendering Performance Pattern:**

```python
class DetailScreen(Screen):
    def on_enter(self):
        """Pre-calculate stat bar data to optimize rendering."""
        self._load_pokemon_data()  # Loads self.stats from database
        
        # Pre-calculate bar widths and colors (cache for render calls)
        self.stat_bars = []
        for stat_name, base_stat in self.stats:
            bar_width = (base_stat / 255) * STAT_BAR_MAX_WIDTH
            bar_color = get_stat_color(base_stat)
            self.stat_bars.append({
                'name': stat_name,
                'value': base_stat,
                'width': bar_width,
                'color': bar_color,
                'has_glow': base_stat >= 100
            })
    
    def render(self, surface: pygame.Surface):
        """Blit pre-calculated stat bars - fast."""
        for i, bar_data in enumerate(self.stat_bars):
            y = STATS_PANEL_Y + (i * STAT_SPACING)
            # Draw using cached data (no recalculation per frame)
            self._draw_stat_bar(surface, y, bar_data)
```

**Manager Integration (from Architecture):**

```python
class DetailScreen(Screen):
    def __init__(self, screen_manager, pokemon_id: int):
        super().__init__(screen_manager)
        self.pokemon_id = pokemon_id
        self.database = screen_manager.database  # ✅ Access via screen_manager
        self.stats = []  # Will store [(stat_name, base_stat), ...]
        
    def _load_pokemon_data(self):
        """Load all Pokemon data including stats."""
        # Load basic data (from Story 3.1)
        self.pokemon_data = self.database.get_pokemon_by_id(self.pokemon_id)
        
        # Load stats (new in Story 3.2)
        self.stats = self.database.get_pokemon_stats(self.pokemon_id)
        
        if len(self.stats) != 6:
            logging.warning(f"Stats query returned {len(self.stats)}, expected 6")
```

[Source: docs/architecture.md#Database-Access-Pattern]
[Source: docs/architecture.md#Performance-Patterns]

### Epic Technical Specification Context

This story implements **AC #1 and AC #2** from the Epic 3 Tech Spec, focusing on stat display with visual bars and color coding.

**Stat Display Requirements (from Tech Spec):**

**Stat Bar Specification:**
- Width calculation: `(base_stat / 255) * max_bar_width`
- Max stat (255) fills bar 100%
- Min stat (1) shows minimal visible bar (not invisible)
- All bars same max width for visual comparison

**Color Coding (from Tech Spec):**
```python
STAT_COLORS = {
    'low': (113, 128, 150),      # 0-50: Gray #718096
    'medium': (0, 212, 255),     # 51-100: Electric blue #00d4ff
    'high': (77, 247, 255),      # 101-150: Bright cyan #4df7ff
    'exceptional': (255, 107, 53) # 151+: Plasma orange #ff6b35
}
```

**Glow Effect for High Stats:**
- Apply to stats >= 100
- Implementation: Draw second bar with alpha=128, offset +2px
- Use same color as main bar
- Must not impact frame rate (30+ FPS maintained)

**Layout Specification:**
```
DetailScreen Stats Panel (Right Side):

┌─────────────────────────────┐
│ HP       ████████████  35   │
│ Attack   ██████████    55   │
│ Defense  ████████      40   │
│ Sp.Atk   █████████████ 50   │
│ Sp.Def   █████████████ 50   │
│ Speed    ████████████████ 90 │
└─────────────────────────────┘

- Labels: Share Tech Mono 14px, ice blue, left-aligned
- Values: Share Tech Mono 16px, white, right-aligned
- Bars: Proportional width, color-coded by value
- Spacing: 28px vertical between bars
- Padding: 16px from panel edges
```

[Source: docs/sprint-artifacts/tech-spec-epic-2-detail-view-with-audio.md#AC-1-Comprehensive-Stat-Display]
[Source: docs/sprint-artifacts/tech-spec-epic-2-detail-view-with-audio.md#Data-Models-Stat-Colors]

### Database Schema for Stats

**Database Tables:**
- `stats` table: id, name (HP, Attack, Defense, Special Attack, Special Defense, Speed)
- `pokemon_stats` table: pokemon_id, stat_id, base_stat (value 1-255)

**Query Pattern:**
```sql
SELECT s.name, ps.base_stat
FROM stats s
JOIN pokemon_stats ps ON s.id = ps.stat_id
WHERE ps.pokemon_id = ?
ORDER BY s.id
```

**Expected Return (6 rows):**
```python
[
    ('HP', 35),
    ('Attack', 55),
    ('Defense', 40),
    ('Sp. Atk', 50),
    ('Sp. Def', 50),
    ('Speed', 90)
]
```

**Stat ID Mapping (from database schema):**
- 1: HP
- 2: Attack
- 3: Defense
- 4: Special Attack (display as "Sp.Atk")
- 5: Special Defense (display as "Sp.Def")
- 6: Speed

**Performance Requirement:**
- Query must complete in < 50ms (per architecture)
- Use parameterized query for SQL injection prevention
- Return results in canonical stat order (ORDER BY s.id)

[Source: docs/database_schema.md#stats-table]
[Source: docs/database_schema.md#pokemon_stats-table]

### Component Locations

**Files to Modify:**
- `src/ui/detail_screen.py` - Add stat bar rendering logic
- `src/data/database.py` - Add get_pokemon_stats() method (if not exists)
- `src/ui/colors.py` - Add STAT_COLORS constant (if not present)

**Files to Create:**
- None - all infrastructure exists from Story 3.1

**Files to Reference (Already Exist):**
- `src/ui/screen.py` - Base Screen class
- `src/state_manager.py` - StateManager singleton
- `src/performance_monitor.py` - PerformanceMonitor for profiling
- `tests/test_detail_screen.py` - Add new stat-specific tests

**No New Dependencies:**
- Uses pygame for rendering (already required)
- Uses existing database connection
- Uses existing font loading (pygame.font)

### Stat Bar Rendering Implementation Details

**Bar Width Calculation:**
```python
def calculate_bar_width(base_stat: int, max_width: int) -> int:
    """Calculate proportional bar width.
    
    Args:
        base_stat: Stat value (1-255)
        max_width: Maximum bar width in pixels
        
    Returns:
        Bar width in pixels (1 to max_width)
    """
    # Ensure minimum 1px visible bar for non-zero stats
    width = max(1, int((base_stat / 255) * max_width))
    return width
```

**Glow Effect Implementation:**
```python
def draw_stat_bar_with_glow(surface: pygame.Surface, rect: pygame.Rect, 
                            color: Tuple[int, int, int], has_glow: bool):
    """Draw stat bar with optional glow effect.
    
    Args:
        surface: Target surface to draw on
        rect: Bar rectangle (x, y, width, height)
        color: RGB color tuple
        has_glow: True if stat >= 100, False otherwise
    """
    # Draw main bar
    pygame.draw.rect(surface, color, rect)
    
    # Draw glow if high stat
    if has_glow:
        glow_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        glow_rect = pygame.Rect(2, 2, rect.width, rect.height)  # Offset by 2px
        pygame.draw.rect(glow_surface, (*color, 128), glow_rect)  # Alpha = 128
        surface.blit(glow_surface, rect.topleft)
```

**Complete Stat Bar Rendering:**
```python
def _render_stat_bars(self, surface: pygame.Surface):
    """Render all 6 stat bars with labels and values."""
    STAT_LABEL_X = STATS_PANEL_X + 16  # 16px padding
    STAT_BAR_X = STAT_LABEL_X + 80  # Room for label
    STAT_VALUE_X = STATS_PANEL_X + STATS_PANEL_WIDTH - 16  # Right-aligned
    
    for i, (stat_name, base_stat) in enumerate(self.stats):
        y = STATS_PANEL_Y + 20 + (i * STAT_SPACING)
        
        # Validate and clamp stat value
        if base_stat is None or base_stat < 0 or base_stat > 255:
            logging.warning(f"Invalid stat {stat_name}={base_stat}, clamping")
            base_stat = max(0, min(255, base_stat or 0))
        
        # Calculate bar dimensions
        bar_width = calculate_bar_width(base_stat, STAT_BAR_MAX_WIDTH)
        bar_color = get_stat_color(base_stat)
        
        # Draw empty bar background
        bg_rect = pygame.Rect(STAT_BAR_X, y, STAT_BAR_MAX_WIDTH, STAT_BAR_HEIGHT)
        pygame.draw.rect(surface, (40, 40, 40), bg_rect)  # Dark gray
        
        # Draw filled bar with optional glow
        bar_rect = pygame.Rect(STAT_BAR_X, y, bar_width, STAT_BAR_HEIGHT)
        draw_stat_bar_with_glow(surface, bar_rect, bar_color, base_stat >= 100)
        
        # Render stat label (left)
        label_surface = self.stat_label_font.render(stat_name, True, ICE_BLUE)
        surface.blit(label_surface, (STAT_LABEL_X, y))
        
        # Render stat value (right)
        value_surface = self.stat_value_font.render(str(base_stat), True, WHITE)
        value_rect = value_surface.get_rect(right=STAT_VALUE_X, top=y)
        surface.blit(value_surface, value_rect)
```

### Performance Profiling Strategy

**Profiling Stat Rendering:**
```python
import time

def render(self, surface: pygame.Surface):
    """Render DetailScreen with performance tracking."""
    # ... other rendering ...
    
    # Profile stat bar rendering
    start = time.perf_counter()
    self._render_stat_bars(surface)
    elapsed = time.perf_counter() - start
    
    if elapsed > 0.010:  # 10ms threshold
        logging.warning(f"Stat bars took {elapsed*1000:.2f}ms (target: <10ms)")
    
    # Track overall frame rate
    self.perf_monitor.record_frame()
    if self.perf_monitor.get_average_fps() < 30:
        logging.warning(f"FPS drop: {self.perf_monitor.get_average_fps():.1f}")
```

**Optimization Checklist (if performance issues):**
1. Pre-calculate bar widths and colors in on_enter() (cache in list)
2. Use dirty rects to only update stats panel region
3. Simplify glow effect (single draw instead of second surface)
4. Reduce glow alpha or make it optional for low-power mode
5. Profile font rendering - pre-render static labels

### Testing Strategy

**Unit Tests:**
```python
def test_calculate_bar_width():
    """Test proportional bar width calculation."""
    assert calculate_bar_width(255, 100) == 100  # Max fills completely
    assert calculate_bar_width(1, 100) >= 1      # Min is visible
    assert 49 <= calculate_bar_width(127, 100) <= 51  # Half is ~50%

def test_get_stat_color():
    """Test stat color coding for each range."""
    assert get_stat_color(25) == STAT_COLORS['low']      # 0-50
    assert get_stat_color(75) == STAT_COLORS['medium']   # 51-100
    assert get_stat_color(125) == STAT_COLORS['high']    # 101-150
    assert get_stat_color(200) == STAT_COLORS['exceptional']  # 151+

def test_stat_validation():
    """Test stat value clamping."""
    assert clamp_stat(-10) == 0
    assert clamp_stat(300) == 255
    assert clamp_stat(None) == 0
```

**Integration Tests:**
```python
def test_six_stats_display():
    """Verify all 6 stats rendered with correct data."""
    detail_screen = DetailScreen(screen_manager, pokemon_id=25)
    detail_screen.on_enter()
    
    assert len(detail_screen.stats) == 6
    assert detail_screen.stats[0][0] == "HP"
    assert detail_screen.stats[5][0] == "Speed"

def test_stat_bar_proportional_width():
    """Verify bar widths match stat values."""
    detail_screen = DetailScreen(screen_manager, pokemon_id=242)  # Blissey
    detail_screen.on_enter()
    
    # Blissey has HP=255 (max) - should fill bar completely
    hp_stat = detail_screen.stats[0][1]
    assert hp_stat == 255
```

**Edge Cases:**
- Shedinja (#292): HP=1 (minimal bar, still visible)
- Blissey (#242): HP=255 (max bar, fills 100%)
- Mewtwo (#150): Multiple high stats (test glow on multiple bars)
- Invalid data: Mock database return with None, negative, > 255 values

### References

- [Source: docs/PRD.md#FR3.2-Base-Stats-Visualization] - Stat display requirements
- [Source: docs/architecture.md#Database-Access-Pattern] - Parameterized queries
- [Source: docs/architecture.md#Performance-Patterns] - Rendering optimization
- [Source: docs/sprint-artifacts/tech-spec-epic-2-detail-view-with-audio.md#AC-1] - Stat bar spec
- [Source: docs/sprint-artifacts/tech-spec-epic-2-detail-view-with-audio.md#Data-Models] - Color coding
- [Source: docs/database_schema.md#stats-table] - Database schema
- [Source: docs/epics.md#Story-3.2] - Original story definition

## Change Log

**2025-11-16: Story Drafted by SM Agent (Bob)**
- Created story file with BDD-style acceptance criteria (9 ACs covering stat display, bars, colors, glow, layout, database, error handling, performance)
- Added 10 detailed tasks with subtasks for stat bar implementation
- Integrated learnings from Story 3.1 (DetailScreen foundation, placeholder panels ready, holographic styling established)
- Documented database schema and query patterns for stats retrieval
- Specified stat bar rendering logic with proportional widths and color coding
- Defined STAT_COLORS constant and get_stat_color() mapping function
- Created comprehensive dev notes covering: architecture patterns, tech spec alignment, database integration, rendering implementation, performance profiling, testing strategy
- Status: **drafted** - Ready for story context generation or developer implementation

## Dev Agent Record

### Context Reference

- `docs/sprint-artifacts/3-2-six-base-stats-with-visual-progress-bars.context.xml` - Story Context (generated 2025-11-16)

### Agent Model Used

<!-- Agent model details will be added during implementation -->

### Debug Log References

<!-- Debug log entries will be added during implementation -->

### Completion Notes List

<!-- Completion notes will be added after story is implemented -->

### File List

<!-- Files modified/created will be listed after implementation -->
