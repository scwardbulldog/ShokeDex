# Story 3.5: Pokédex Description Text Display

Status: ready-for-dev

## Story

As a user,
I want to read the Pokémon's Pokédex entry description,
So that I can learn about its lore and characteristics.

## Acceptance Criteria

1. **Authentic Description Display (AC #1)**
   - **Given** DetailScreen is displaying a Pokémon
   - **When** the description section renders
   - **Then** authentic flavor text from the database is displayed
   - **And** text originates from the pokemon table description column
   - **And** no placeholder or dummy text is shown (except when description missing)
   - **And** text maintains original wording from PokéAPI source

2. **Text Wrapping at Word Boundaries (AC #2)**
   - **Given** description text exceeds the available width
   - **When** text rendering processes the description
   - **Then** text wraps at word boundaries (not mid-word)
   - **And** maximum width is 400px per line
   - **And** wrapping algorithm splits on spaces, not within words
   - **And** hyphenated words may split at hyphens if necessary

3. **Four-Line Display Limit (AC #3)**
   - **Given** description text is rendered
   - **When** calculating line count
   - **Then** maximum 4 lines are displayed
   - **And** line height is 22.4px (1.4 × 16px font size)
   - **And** lines are evenly spaced vertically
   - **And** total description height does not exceed 89.6px (4 lines × 22.4px)

4. **Truncation with Ellipsis (AC #4)**
   - **Given** description text exceeds 4 lines
   - **When** rendering the fourth line
   - **Then** text is truncated to fit within 4 lines
   - **And** "..." ellipsis is appended to the end of line 4
   - **And** ellipsis does not overflow the 400px width limit
   - **And** ellipsis is clearly visible (not cut off)
   - **And** if text fits naturally in 4 lines, no ellipsis is added

5. **Typography Specifications (AC #5)**
   - **Given** description text is rendered
   - **When** applying text styling
   - **Then** font is Rajdhani Regular, 16px size
   - **And** color is ice blue (#a8e6ff / rgb(168, 230, 255))
   - **And** text is antialiased for smooth rendering
   - **And** font fallback is pygame default if Rajdhani unavailable

6. **Layout and Positioning (AC #6)**
   - **Given** DetailScreen is displayed with all panels
   - **When** description panel renders
   - **Then** panel is positioned in the lower section of the detail area
   - **And** panel uses holographic blue styling: dark blue background rgba(26, 47, 74, 0.9)
   - **And** panel border is 2px solid electric blue (#00d4ff)
   - **And** 16px padding between panel edge and description text
   - **And** all text remains within display boundaries (no cutoff)
   - **And** description does not overlap other UI elements (stats, types, sprite)

7. **Database Query Integration (AC #7)**
   - **Given** DetailScreen needs to load description data
   - **When** DetailScreen._load_pokemon_data() executes
   - **Then** description is retrieved from pokemon table description column
   - **And** query uses parameterized statement (SQL injection prevention)
   - **And** query completes in < 50ms (per performance target)
   - **And** description stored in self.description: str instance variable

8. **Error Handling and Missing Data (AC #8)**
   - **Given** database query returns no description (None or empty string)
   - **When** description section renders
   - **Then** placeholder text "No description available" is displayed
   - **And** placeholder uses same styling as normal description
   - **And** warning is logged: "No description found for Pokemon #{id}"
   - **And** application does not crash on missing description
   - **And** if description is null, it is coerced to empty string

9. **Pre-Rendering Optimization (AC #9)**
   - **Given** description text is loaded in on_enter()
   - **When** description is processed for rendering
   - **Then** text is wrapped and rendered to surfaces in on_enter() (not per frame)
   - **And** rendered line surfaces are cached in self.description_lines: List[pygame.Surface]
   - **And** render() method blits cached surfaces (no text processing per frame)
   - **And** pre-rendering completes in < 5ms (per performance target)
   - **And** cached surfaces are cleared and regenerated when navigating to new Pokémon

10. **Performance Requirements (AC #10)**
    - **Given** DetailScreen renders with description text
    - **When** any operation occurs
    - **Then** frame rate maintains 30+ FPS during rendering
    - **And** description rendering (blit cached surfaces) completes in < 5ms per frame
    - **And** text wrapping in on_enter() completes in < 50ms
    - **And** DetailScreen total render time remains < 33ms per frame

## Tasks / Subtasks

- [ ] **Task 1: Extend Database Query to Include Description** (AC: #7)
  - [ ] Verify `Database.get_pokemon_by_id()` returns description field
  - [ ] If not, modify query to include: `SELECT id, name, height, weight, description FROM pokemon WHERE id = ?`
  - [ ] Alternative: Create `Database.get_pokemon_physical_data(pokemon_id)` method returning (height, weight, description)
  - [ ] Use parameterized query for SQL injection prevention
  - [ ] Profile query time with `time.perf_counter()`, assert < 50ms
  - [ ] Add unit test: `test_get_pokemon_description()` verifies description returned
  - [ ] Test with multiple Pokémon: Pikachu #25, Mewtwo #150 (long description), Caterpie #10 (short)

- [ ] **Task 2: Load Description in DetailScreen Lifecycle** (AC: #7, #8)
  - [ ] Modify `DetailScreen._load_pokemon_data()` to extract description from database result
  - [ ] Store in `self.description: str` instance variable
  - [ ] Handle None/null: `self.description = pokemon_data.get('description') or ""`
  - [ ] If description is empty string, set to placeholder: "No description available"
  - [ ] Log warning if description missing: `logging.warning(f"No description found for Pokemon #{self.pokemon_id}")`
  - [ ] Add error handling: try/except with logging for database failures
  - [ ] Verify description loaded in `on_enter()` before rendering

- [ ] **Task 3: Implement Text Wrapping Function** (AC: #2, #3, #4)
  - [ ] Create `_wrap_description_text(text: str, font: pygame.font.Font, max_width: int, max_lines: int) -> List[str]` helper
  - [ ] Algorithm:
    ```python
    lines = []
    words = text.split(' ')
    current_line = ""
    
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
                current_line = word
            else:
                # Word too long, force add
                lines.append(word)
                current_line = ""
        
        if len(lines) >= max_lines:
            break
    
    if current_line and len(lines) < max_lines:
        lines.append(current_line)
    
    return lines
    ```
  - [ ] Handle truncation: if text would exceed max_lines, append "..." to last line
  - [ ] Ensure "..." fits within max_width by shortening line 4 if needed
  - [ ] Add unit tests: short text (1 line), medium text (3 lines), long text (5+ lines truncates to 4)

- [ ] **Task 4: Pre-Render Description Lines in on_enter** (AC: #9)
  - [ ] Create `DetailScreen._render_description_lines()` method called from `on_enter()`
  - [ ] Implementation:
    ```python
    def _render_description_lines(self):
        """Pre-render description text to surfaces for efficient blitting."""
        self.description_lines = []
        
        if not self.description_font or not self.description:
            return
        
        # Wrap text to max 4 lines, 400px width
        wrapped_lines = self._wrap_description_text(
            self.description, 
            self.description_font, 
            max_width=400, 
            max_lines=4
        )
        
        # Render each line to surface (cache for blit)
        for line_text in wrapped_lines:
            line_surface = self.description_font.render(line_text, True, Colors.ICE_BLUE)
            self.description_lines.append(line_surface)
    ```
  - [ ] Profile pre-rendering time: < 50ms target (measure with perf_counter)
  - [ ] Call `_render_description_lines()` in `on_enter()` after description loaded
  - [ ] Clear cached lines when navigating to new Pokémon

- [ ] **Task 5: Implement Description Panel Rendering** (AC: #1, #5, #6)
  - [ ] Create `DetailScreen._render_description_panel(surface: pygame.Surface)` method
  - [ ] Define layout constants:
    - DESC_PANEL_X = 20 (left margin)
    - DESC_PANEL_Y = screen_height - 140 (lower section)
    - DESC_PANEL_WIDTH = screen_width - 40 (full width minus margins)
    - DESC_PANEL_HEIGHT = 120
    - DESC_TEXT_X = DESC_PANEL_X + 16 (16px padding)
    - DESC_TEXT_Y = DESC_PANEL_Y + 16
    - DESC_LINE_HEIGHT = 22.4 (1.4 × 16px font)
  - [ ] Render holographic blue panel:
    ```python
    panel_surface = pygame.Surface((DESC_PANEL_WIDTH, DESC_PANEL_HEIGHT), pygame.SRCALPHA)
    panel_surface.fill((*Colors.DARK_BLUE, 230))  # rgba(26, 47, 74, 0.9)
    pygame.draw.rect(panel_surface, Colors.ELECTRIC_BLUE, 
                    pygame.Rect(0, 0, DESC_PANEL_WIDTH, DESC_PANEL_HEIGHT), 2)
    surface.blit(panel_surface, (DESC_PANEL_X, DESC_PANEL_Y))
    ```
  - [ ] Blit pre-rendered description lines:
    ```python
    for i, line_surface in enumerate(self.description_lines):
        y = DESC_TEXT_Y + (i * DESC_LINE_HEIGHT)
        surface.blit(line_surface, (DESC_TEXT_X, y))
    ```
  - [ ] Call `_render_description_panel()` from `render()` method

- [ ] **Task 6: Implement Font Loading for Description** (AC: #5)
  - [ ] In `DetailScreen.on_enter()`, load description font:
    ```python
    try:
        self.description_font = pygame.font.Font("assets/fonts/Rajdhani-Regular.ttf", 16)
    except:
        self.description_font = pygame.font.Font(None, 16)  # Fallback
        logging.warning("Rajdhani font not found, using fallback")
    ```
  - [ ] Cache font in `self.description_font` instance variable
  - [ ] Use antialiasing in render calls: `font.render(text, True, color)`
  - [ ] Handle missing font gracefully with pygame default

- [ ] **Task 7: Implement Truncation with Ellipsis** (AC: #4)
  - [ ] Modify `_wrap_description_text()` to handle truncation:
    ```python
    # After building wrapped_lines list
    if len(lines) >= max_lines:
        # Need to truncate and add ellipsis
        last_line = lines[max_lines - 1]
        
        # Check if ellipsis fits
        test_with_ellipsis = last_line + "..."
        if font.size(test_with_ellipsis)[0] <= max_width:
            lines[max_lines - 1] = test_with_ellipsis
        else:
            # Shorten last line to fit ellipsis
            while font.size(last_line + "...")[0] > max_width and len(last_line) > 0:
                last_line = last_line[:-1]
            lines[max_lines - 1] = last_line + "..."
    ```
  - [ ] Test truncation with very long descriptions (legendary Pokémon)
  - [ ] Verify ellipsis visible and not cut off
  - [ ] Add unit test: `test_long_description_truncates_with_ellipsis()`

- [ ] **Task 8: Error Handling and Placeholder Display** (AC: #8)
  - [ ] In `_load_pokemon_data()`, validate description:
    ```python
    self.description = pokemon_data.get('description') or ""
    
    if not self.description:
        self.description = "No description available"
        logging.warning(f"No description found for Pokemon #{self.pokemon_id}")
    ```
  - [ ] Test with mock data: null description, empty string, missing key
  - [ ] Verify placeholder displays with same styling as normal text
  - [ ] Add unit test: `test_missing_description_shows_placeholder()`

- [ ] **Task 9: Performance Optimization** (AC: #9, #10)
  - [ ] Profile description rendering with `time.perf_counter()`:
    ```python
    # In on_enter()
    start = time.perf_counter()
    self._render_description_lines()
    elapsed = time.perf_counter() - start
    logging.debug(f"Description pre-rendering: {elapsed*1000:.2f}ms")
    
    # In render()
    start = time.perf_counter()
    self._render_description_panel(surface)
    elapsed = time.perf_counter() - start
    if elapsed > 0.005:  # 5ms threshold
        logging.warning(f"Description blit took {elapsed*1000:.2f}ms (target: <5ms)")
    ```
  - [ ] Verify pre-rendering < 50ms (measured in on_enter)
  - [ ] Verify blitting < 5ms per frame (measured in render)
  - [ ] Verify frame rate stays 30+ FPS
  - [ ] Test with rapid L/R navigation (stress test pre-rendering)

- [ ] **Task 10: Integration Testing** (AC: All)
  - [ ] Create integration tests in `tests/test_detail_screen.py`:
    - `test_description_displays_authentic_text()` - Verify text from database
    - `test_description_wraps_at_word_boundaries()` - No mid-word breaks
    - `test_description_max_four_lines()` - Line count limit enforced
    - `test_long_description_truncates_with_ellipsis()` - Ellipsis added
    - `test_short_description_no_ellipsis()` - No ellipsis if fits
    - `test_description_typography_styling()` - Font, color, size correct
    - `test_description_panel_layout()` - Panel positioning and styling
    - `test_missing_description_placeholder()` - Placeholder displayed
    - `test_description_pre_rendering_performance()` - < 50ms pre-render
    - `test_description_blit_performance()` - < 5ms per frame
  - [ ] Test with specific Pokémon:
    - Pikachu #25: Medium-length description (fits in 3 lines)
    - Mewtwo #150: Very long description (truncates at 4 lines)
    - Caterpie #10: Short description (1-2 lines)
  - [ ] Visual verification: Compare rendered description to UX spec mockup

- [ ] **Task 11: Update Tests and Documentation** (AC: All)
  - [ ] Run all existing tests to verify no regressions
  - [ ] Add docstrings to new methods explaining description rendering logic
  - [ ] Update TESTING.md with description rendering test coverage
  - [ ] Document text wrapping algorithm and truncation behavior
  - [ ] Add comments explaining DESC_LINE_HEIGHT calculation (1.4 × font size)

## Dev Notes

### Learnings from Previous Story

**From Story 3-2-six-base-stats-with-visual-progress-bars (Status: done)**

Story 3.2 implemented stat bar rendering with pre-calculation optimizations and cached rendering. This story follows the same performance pattern for description text:

**Performance Pattern Applied:**
- **Pre-rendering in on_enter():** Stats pre-calculated bar widths/colors once, descriptions pre-render text surfaces once
- **Cached rendering in render():** Stats blit cached bars, descriptions blit cached line surfaces
- **Profiling with perf_counter():** Both stories measure pre-render time and per-frame blit time
- **Target metrics:** < 10ms for stat bars (exceeded), < 5ms for description blit (to be verified)
- **Result:** Maintains 30+ FPS by avoiding text processing per frame

**Holographic Styling Consistency:**
- Description panel uses same DARK_BLUE background with alpha 230 (~0.9)
- 2px ELECTRIC_BLUE border (#00d4ff)
- 16px padding standard applied to all panels
- ICE_BLUE color (#a8e6ff) for readable text on dark background

**Database Integration Pattern:**
- Use parameterized queries: `cursor.execute("SELECT ... WHERE id = ?", (pokemon_id,))`
- Load data in `_load_pokemon_data()` method (called from on_enter)
- Store in instance variables for render access
- Validate data and log warnings for missing/invalid values
- Handle None values by coercing to empty string or placeholder

**Error Handling Approach:**
- Validate data immediately after loading (not during render)
- Log warnings for debugging without crashing
- Provide user-friendly placeholders for missing data
- Guard clauses prevent render crashes: `if not self.description_lines: return`

[Source: docs/sprint-artifacts/3-2-six-base-stats-with-visual-progress-bars.md#Dev-Agent-Record]

---

**From Story 3-1-detail-screen-layout-and-sprite-display (Status: review)**

Story 3.1 established the DetailScreen foundation. This story adds the final data display component (description) to complete the information presentation:

**Infrastructure Ready:**
- DetailScreen lifecycle established (on_enter/on_exit/update/render)
- Manager access via screen_manager injection
- StateManager integration working
- Holographic blue styling applied to all panels
- Panel layout structure defined (stats right, description lower)
- Font loading pattern established (load in on_enter, cache in instance var)

**Description Panel Placeholder:**
- Lower section panel already positioned for description text
- Panel styling matches other panels (dark blue bg, electric blue border)
- 16px padding around panel edges established
- This story fills in the description panel with wrapped text

**What This Story Adds:**
- Description field retrieval from database pokemon table
- Text wrapping algorithm for word boundary breaks
- 4-line truncation with ellipsis for long descriptions
- Pre-rendering optimization for text surfaces
- Description panel rendering with cached line surfaces

[Source: docs/sprint-artifacts/3-1-detail-screen-layout-and-sprite-display.md#Completion-Notes-List]

### Architecture Context

This story implements **description text display** from the DetailScreen architecture, following established text rendering and performance optimization patterns.

**Text Rendering Performance Pattern (from Architecture):**

```python
class DetailScreen(Screen):
    def on_enter(self):
        """Pre-render static text elements to optimize frame rate."""
        self._load_pokemon_data()  # Loads self.description from database
        
        # Pre-render description lines (cache for blit)
        self._render_description_lines()  # Creates self.description_lines surfaces
    
    def render(self, surface: pygame.Surface):
        """Blit pre-rendered text - fast."""
        # No text processing per frame, just blit cached surfaces
        self._render_description_panel(surface)  # Blits self.description_lines
```

**Font Loading Pattern (from Architecture):**

```python
# Load fonts once in on_enter(), cache in instance variables
try:
    self.description_font = pygame.font.Font("assets/fonts/Rajdhani-Regular.ttf", 16)
except:
    self.description_font = pygame.font.Font(None, 16)  # Fallback
    logging.warning("Rajdhani font not found, using fallback")

# Use antialiasing: True parameter for smooth rendering
line_surface = self.description_font.render(line_text, True, Colors.ICE_BLUE)
```

**Database Access Pattern (from Architecture):**

```python
# ✅ CORRECT - Parameterized query
def get_pokemon_physical_data(self, pokemon_id: int) -> Tuple[float, float, str]:
    cursor = self.conn.execute(
        """SELECT height, weight, description 
           FROM pokemon 
           WHERE id = ?""",
        (pokemon_id,)
    )
    result = cursor.fetchone()
    return (result['height'], result['weight'], result['description'] or "")

# ❌ INCORRECT - Never use string formatting
query = f"SELECT description FROM pokemon WHERE id = {pokemon_id}"  # SQL injection risk
```

[Source: docs/architecture.md#Performance-Patterns]
[Source: docs/architecture.md#Database-Access-Pattern]

### Epic Technical Specification Context

This story implements **AC #5** from the Epic 3 Tech Spec, focusing on Pokédex description text display with wrapping and truncation.

**Description Rendering Specification (from Tech Spec):**

```python
DESCRIPTION_SPEC = {
    'font': 'Rajdhani',
    'size': 16,  # px
    'color': (168, 230, 255),  # Ice blue #a8e6ff
    'max_width': 400,  # px
    'max_lines': 4,
    'line_height': 22.4,  # 1.4 × font size
    'truncation': '...'  # Append to line 4 if text exceeds
}
```

**Text Wrapping Requirements:**
- Wrap at word boundaries (split on spaces)
- Maximum 400px width per line
- Maximum 4 lines total
- Line height: 22.4px (1.4 × 16px font size for readability)
- Truncate with "..." if text exceeds 4 lines

**Layout Specification:**
```
DetailScreen Description Panel (Lower Section):

┌─────────────────────────────────────────┐
│  When several of these Pokémon gather,  │
│  their electricity could build and       │
│  cause lightning storms. Pikachu is a   │
│  beloved Electric-type Pokémon that...  │
└─────────────────────────────────────────┘

- Font: Rajdhani 16px, ice blue
- Max width: 400px
- Max lines: 4 with 22.4px spacing
- Padding: 16px from panel edges
- Panel: Dark blue bg, electric blue border
```

**Performance Requirements:**
- Pre-rendering in on_enter(): < 50ms
- Blitting per frame in render(): < 5ms
- No text processing per frame (use cached surfaces)
- Frame rate maintained at 30+ FPS

[Source: docs/sprint-artifacts/tech-spec-epic-2-detail-view-with-audio.md#AC-5]
[Source: docs/sprint-artifacts/tech-spec-epic-2-detail-view-with-audio.md#Data-Models-Description-Spec]

### Database Schema for Description

**Database Table:**
- `pokemon` table: id, name, height, weight, description

**Query Pattern:**
```sql
SELECT id, name, height, weight, description
FROM pokemon
WHERE id = ?
```

**Expected Return:**
```python
{
    'id': 25,
    'name': 'Pikachu',
    'height': 0.4,
    'weight': 6.0,
    'description': 'When several of these Pokémon gather, their electricity could build and cause lightning storms.'
}
```

**Description Field:**
- Type: TEXT (variable length string)
- May be null or empty for some Pokémon
- Contains authentic flavor text from PokéAPI
- Length varies: 50-300 characters typical, some legendary Pokémon 400+ characters

**Performance Requirement:**
- Query must complete in < 50ms (per architecture)
- Use parameterized query for SQL injection prevention
- Include description in existing pokemon query (no separate query needed)

[Source: docs/database_schema.md#pokemon-table]

### Component Locations

**Files to Modify:**
- `src/ui/detail_screen.py` - Add description text rendering logic
- `src/data/database.py` - Verify get_pokemon_by_id() returns description (or add get_pokemon_physical_data)

**Files to Reference (Already Exist):**
- `src/ui/screen.py` - Base Screen class
- `src/ui/colors.py` - ICE_BLUE, DARK_BLUE, ELECTRIC_BLUE constants
- `src/state_manager.py` - StateManager singleton
- `src/performance_monitor.py` - PerformanceMonitor for profiling
- `tests/test_detail_screen.py` - Add new description-specific tests

**Assets to Use:**
- `assets/fonts/Rajdhani-Regular.ttf` - Primary font (if available)
- Fallback: pygame.font.Font(None, 16) - System default

**No New Dependencies:**
- Uses pygame for text rendering (already required)
- Uses existing database connection
- Uses existing font loading pattern

### Text Wrapping Algorithm Details

**Word Boundary Wrapping:**
```python
def _wrap_description_text(self, text: str, font: pygame.font.Font, 
                          max_width: int, max_lines: int) -> List[str]:
    """Wrap text at word boundaries to fit within max_width.
    
    Args:
        text: Description text to wrap
        font: pygame Font object for measuring text width
        max_width: Maximum width in pixels per line
        max_lines: Maximum number of lines to return
        
    Returns:
        List of wrapped lines (max max_lines entries)
    """
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
    
    # Handle truncation with ellipsis
    if len(lines) >= max_lines and words:
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
```

**Edge Cases Handled:**
- Empty description: Return empty list
- Single word longer than max_width: Force add to line (may overflow)
- Exactly 4 lines: No ellipsis needed
- > 4 lines: Truncate and add ellipsis
- Ellipsis doesn't fit: Shorten line 4 to make room

### Performance Profiling Strategy

**Profiling Description Rendering:**
```python
import time

def on_enter(self):
    """Pre-render description text surfaces."""
    # ... other on_enter logic ...
    
    # Profile description pre-rendering
    start = time.perf_counter()
    self._render_description_lines()
    elapsed = time.perf_counter() - start
    
    logging.debug(f"Description pre-rendering: {elapsed*1000:.2f}ms")
    if elapsed > 0.050:  # 50ms threshold
        logging.warning(f"Description pre-render took {elapsed*1000:.2f}ms (target: <50ms)")

def render(self, surface: pygame.Surface):
    """Render DetailScreen with performance tracking."""
    # ... other rendering ...
    
    # Profile description blit
    start = time.perf_counter()
    self._render_description_panel(surface)
    elapsed = time.perf_counter() - start
    
    if elapsed > 0.005:  # 5ms threshold
        logging.warning(f"Description blit took {elapsed*1000:.2f}ms (target: <5ms)")
```

**Optimization Checklist (if performance issues):**
1. ✅ Pre-render text surfaces in on_enter() (already planned)
2. Use dirty rects to only update description panel region
3. Simplify panel styling (solid color instead of alpha blending)
4. Reduce max lines from 4 to 3 (less text processing)
5. Cache wrapped text strings (not just surfaces) for faster re-render

### Testing Strategy

**Unit Tests:**
```python
def test_wrap_description_short():
    """Test wrapping short text (fits in 1 line)."""
    short_text = "A small Electric-type Pokémon."
    lines = detail_screen._wrap_description_text(short_text, font, 400, 4)
    assert len(lines) == 1
    assert lines[0] == short_text

def test_wrap_description_medium():
    """Test wrapping medium text (fits in 3 lines)."""
    medium_text = "When several of these Pokémon gather, their electricity could build and cause lightning storms."
    lines = detail_screen._wrap_description_text(medium_text, font, 400, 4)
    assert 2 <= len(lines) <= 3
    # Verify no mid-word breaks
    for line in lines:
        assert not line.endswith('-')  # No forced hyphenation

def test_wrap_description_long_truncates():
    """Test wrapping long text (truncates at 4 lines with ellipsis)."""
    long_text = "A very long description " * 50  # 250 words
    lines = detail_screen._wrap_description_text(long_text, font, 400, 4)
    assert len(lines) == 4
    assert lines[3].endswith("...")  # Ellipsis on line 4

def test_wrap_description_exactly_four_lines():
    """Test text that fits exactly in 4 lines (no ellipsis)."""
    exact_text = "Line one text. " * 10 + "Line two. " * 10 + "Line three. " * 10 + "Line four."
    lines = detail_screen._wrap_description_text(exact_text, font, 400, 4)
    assert len(lines) == 4
    assert not lines[3].endswith("...")  # No ellipsis if exact fit
```

**Integration Tests:**
```python
def test_description_displays_from_database():
    """Verify description loaded from database and displayed."""
    detail_screen = DetailScreen(screen_manager, pokemon_id=25)  # Pikachu
    detail_screen.on_enter()
    
    assert detail_screen.description  # Not empty
    assert len(detail_screen.description_lines) > 0  # Lines rendered
    
def test_long_description_truncates():
    """Verify long descriptions truncate at 4 lines."""
    detail_screen = DetailScreen(screen_manager, pokemon_id=150)  # Mewtwo (long desc)
    detail_screen.on_enter()
    
    assert len(detail_screen.description_lines) == 4
    # Check last line ends with ellipsis
    last_line_text = detail_screen.description_lines[3]  # Surface object
    # Note: Can't easily check surface text content, verify in visual test

def test_missing_description_placeholder():
    """Verify placeholder shown when description missing."""
    # Mock database to return None description
    detail_screen = DetailScreen(screen_manager, pokemon_id=999)
    detail_screen.description = None  # Simulate missing
    detail_screen._load_pokemon_data()
    
    assert detail_screen.description == "No description available"
```

**Edge Cases:**
- Pikachu #25: Medium-length description (fits in 2-3 lines)
- Mewtwo #150: Very long description (truncates at 4 lines with ellipsis)
- Caterpie #10: Short description (1 line, no wrapping needed)
- Missing description: Placeholder "No description available" displayed
- Empty string description: Coerced to placeholder
- Single very long word: Forced onto line (may overflow)

**Visual Tests:**
- Verify text readable with ice blue on dark blue background
- Verify 22.4px line spacing looks natural (not cramped or loose)
- Verify ellipsis clearly visible at end of line 4
- Verify no text cutoff at panel edges
- Compare to UX spec mockup for visual accuracy

### References

- [Source: docs/PRD.md#FR3.1-Detail-Screen-Display] - Description display requirement
- [Source: docs/architecture.md#Performance-Patterns] - Text pre-rendering optimization
- [Source: docs/architecture.md#Database-Access-Pattern] - Parameterized queries
- [Source: docs/sprint-artifacts/tech-spec-epic-2-detail-view-with-audio.md#AC-5] - Description spec
- [Source: docs/sprint-artifacts/tech-spec-epic-2-detail-view-with-audio.md#Data-Models-Description] - Layout details
- [Source: docs/database_schema.md#pokemon-table] - Database schema
- [Source: docs/epics.md#Story-3.5] - Original story definition
- [Source: docs/sprint-artifacts/3-2-six-base-stats-with-visual-progress-bars.md#Dev-Agent-Record] - Performance pattern learnings

## Change Log

**2025-11-16: Story Drafted by SM Agent (Bob)**
- Created story file with BDD-style acceptance criteria (10 ACs covering authentic text, wrapping, truncation, typography, layout, database, error handling, pre-rendering, performance)
- Added 11 detailed tasks with subtasks for description text rendering implementation
- Integrated learnings from Story 3.2 (pre-rendering pattern, cached surfaces, performance profiling) and Story 3.1 (panel styling, font loading, lifecycle)
- Documented database schema and query patterns for description retrieval
- Specified text wrapping algorithm with word boundary detection and ellipsis truncation
- Defined DESCRIPTION_SPEC from tech spec with typography and layout requirements
- Created comprehensive dev notes covering: architecture patterns, tech spec alignment, database integration, text wrapping implementation, performance profiling, testing strategy
- Status: **drafted** - Ready for story context generation or developer implementation

## Dev Agent Record

### Context Reference

- `docs/sprint-artifacts/3-5-pokedex-description-text-display.context.xml`

### Agent Model Used

<!-- Agent model name and version will be recorded here during implementation -->

### Debug Log References

<!-- Debug log entries will be added here during implementation -->

### Completion Notes List

<!-- Completion notes will be added here after implementation -->

### File List

<!-- File changes will be tracked here during implementation -->
