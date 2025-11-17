# Story 3.4: Physical Measurements Display

Status: ready-for-dev

## Story

As a user,
I want to see the Pokémon's height and weight displayed clearly on the detail screen,
So that I understand its physical characteristics and can compare sizes across Pokémon.

## Acceptance Criteria

1. **Height Display (AC #1)**
   - **Given** DetailScreen is displaying a Pokémon
   - **When** the physical data section renders
   - **Then** height is displayed in meters with format "X.Xm" (one decimal place)
   - **And** label "Height:" uses ice blue color (#a8e6ff)
   - **And** value is displayed in white (#ffffff)
   - **And** height value is accurate from database pokemon table

2. **Weight Display (AC #2)**
   - **Given** DetailScreen is displaying a Pokémon
   - **When** the physical data section renders
   - **Then** weight is displayed in kilograms with format "X.Xkg" (one decimal place)
   - **And** label "Weight:" uses ice blue color (#a8e6ff)
   - **And** value is displayed in white (#ffffff)
   - **And** weight value is accurate from database pokemon table

3. **Physical Data Positioning (AC #3)**
   - **Given** DetailScreen is rendering with sprite, stats, and type badges
   - **When** physical data is positioned
   - **Then** height and weight are displayed in the lower section of the detail panel
   - **And** physical data does not overlap sprite, stats bars, or type badges
   - **And** physical data remains fully within display boundaries (no cutoff)
   - **And** positioning is consistent across all Pokémon (short and tall, light and heavy)

4. **Physical Data Layout and Typography (AC #4)**
   - **Given** height and weight are being rendered
   - **When** the layout is applied
   - **Then** labels ("Height:" and "Weight:") are right-aligned
   - **And** values (e.g., "0.4m", "6.0kg") are left-aligned after labels
   - **And** vertical spacing between height and weight is 8px
   - **And** font is Rajdhani, 16px for both labels and values
   - **And** layout provides clean, readable alignment

5. **Database Query Integration (AC #5)**
   - **Given** DetailScreen needs to load physical data
   - **When** DetailScreen._load_pokemon_data() executes
   - **Then** height and weight are fetched from pokemon table
   - **And** query uses parameterized statement (SQL injection prevention)
   - **And** query completes in < 50ms (per performance target)
   - **And** height and weight values are stored in instance variables (self.height, self.weight)

6. **Data Validation and Unit Conversion (AC #6)**
   - **Given** database stores height in decimeters and weight in hectograms (PokéAPI format)
   - **When** physical data is loaded
   - **Then** height is converted from decimeters to meters: meters = decimeters / 10
   - **And** weight is converted from hectograms to kilograms: kilograms = hectograms / 10
   - **And** converted values are validated as positive numbers
   - **And** if height or weight is 0 or negative, warning is logged and "???" placeholder shown

7. **Edge Case Handling (AC #7)**
   - **Given** database returns missing or invalid physical data
   - **When** physical data is processed
   - **Then** if height is None or null, display "???" with warning logged
   - **And** if weight is None or null, display "???" with warning logged
   - **And** if height > 100m (unrealistic), warning logged but value shown (data integrity check)
   - **And** if weight > 10000kg (unrealistic), warning logged but value shown
   - **And** application does not crash on invalid physical data

8. **Formatting Consistency (AC #8)**
   - **Given** physical measurements are being formatted
   - **When** values are converted to strings
   - **Then** height uses format f"{height:.1f}m" (one decimal place, meters suffix)
   - **And** weight uses format f"{weight:.1f}kg" (one decimal place, kilograms suffix)
   - **And** examples: "0.4m" (Pikachu), "17.0m" (Onix), "6.0kg" (Pikachu), "210.0kg" (Onix)
   - **And** formatting is consistent for all 386 Gen 1-3 Pokémon

9. **Visual Consistency with Holographic Aesthetic (AC #9)**
   - **Given** physical data section is part of DetailScreen
   - **When** styling is applied
   - **Then** labels use ice blue color (#a8e6ff) matching stat labels
   - **And** values use white color (#ffffff) matching stat values
   - **And** font (Rajdhani 16px) matches detail screen typography
   - **And** overall visual style aligns with holographic blue aesthetic established in Epic 1 and 3

10. **Performance Requirements (AC #10)**
    - **Given** DetailScreen renders with physical data
    - **When** any operation occurs
    - **Then** frame rate maintains 30+ FPS during rendering
    - **And** physical data rendering completes in < 2ms per frame
    - **And** database query for height/weight included in overall < 50ms data load time
    - **And** DetailScreen total render time remains < 33ms per frame

## Tasks / Subtasks

- [ ] **Task 1: Verify Database Schema for Physical Data** (AC: #5, #6)
  - [ ] Confirm pokemon table contains height (INTEGER, decimeters) and weight (INTEGER, hectograms)
  - [ ] Review existing Database methods to see if get_pokemon_physical_data() exists
  - [ ] If method missing, note to create in Task 2
  - [ ] Verify data format: height in decimeters (e.g., Pikachu: 4 dm = 0.4m), weight in hectograms (e.g., 60 hg = 6.0kg)
  - [ ] Test query with known Pokémon (Pikachu #25: 4dm/60hg, Onix #95: 88dm/2100hg)

- [ ] **Task 2: Implement Database Query for Physical Data** (AC: #5, #6)
  - [ ] Add or verify `Database.get_pokemon_physical_data(pokemon_id: int)` method:
    ```python
    def get_pokemon_physical_data(self, pokemon_id: int) -> Tuple[float, float]:
        """Get height (meters) and weight (kg) for a Pokémon.
        
        Args:
            pokemon_id: National Dex number (1-386)
            
        Returns:
            Tuple of (height_meters, weight_kg)
        """
        cursor = self.conn.execute(
            "SELECT height, weight FROM pokemon WHERE id = ?",
            (pokemon_id,)
        )
        row = cursor.fetchone()
        if not row:
            return (0.0, 0.0)  # Invalid Pokemon
        
        height_dm, weight_hg = row
        height_m = height_dm / 10.0 if height_dm else 0.0
        weight_kg = weight_hg / 10.0 if weight_hg else 0.0
        
        return (height_m, weight_kg)
    ```
  - [ ] Use parameterized query with ? placeholder (SQL injection prevention)
  - [ ] Convert units: decimeters → meters (÷10), hectograms → kilograms (÷10)
  - [ ] Return Tuple[float, float] with converted values
  - [ ] Handle None/null from database gracefully (return 0.0, 0.0)

- [ ] **Task 3: Load Physical Data in DetailScreen Lifecycle** (AC: #5)
  - [ ] Modify `DetailScreen._load_pokemon_data()` to call `get_pokemon_physical_data(pokemon_id)`
  - [ ] Store result in instance variables:
    ```python
    self.height, self.weight = self.database.get_pokemon_physical_data(self.pokemon_id)
    ```
  - [ ] Add validation and logging:
    ```python
    if self.height <= 0 or self.weight <= 0:
        logging.warning(f"Invalid physical data for Pokemon #{self.pokemon_id}: height={self.height}, weight={self.weight}")
    ```
  - [ ] Verify physical data loaded in `on_enter()` before first render
  - [ ] Profile query time with perf_counter(), ensure < 50ms as part of total data load

- [ ] **Task 4: Create Physical Data Rendering Method** (AC: #1, #2, #3, #4, #9)
  - [ ] Create `DetailScreen._render_physical_data(surface: pygame.Surface)` method
  - [ ] Define positioning constants:
    ```python
    PHYSICAL_DATA_X = 30  # Left margin in detail panel
    PHYSICAL_DATA_Y = sprite_y + sprite_height + 100  # Below sprite
    LABEL_WIDTH = 80  # Fixed width for right-aligned labels
    VALUE_OFFSET = 10  # Gap between label and value
    LINE_HEIGHT = 24  # Spacing between height and weight lines
    ```
  - [ ] Load fonts in on_enter() if not already loaded:
    ```python
    self.physical_data_font = pygame.font.Font("Rajdhani", 16) or pygame.font.Font(None, 16)
    ```
  - [ ] Render height line:
    ```python
    # Height label (ice blue, right-aligned)
    height_label = self.physical_data_font.render("Height:", True, Colors.ICE_BLUE)
    label_rect = height_label.get_rect(topright=(PHYSICAL_DATA_X + LABEL_WIDTH, PHYSICAL_DATA_Y))
    surface.blit(height_label, label_rect)
    
    # Height value (white, left-aligned after label)
    height_value = f"{self.height:.1f}m"
    height_text = self.physical_data_font.render(height_value, True, Colors.HOLOGRAM_WHITE)
    value_rect = height_text.get_rect(topleft=(PHYSICAL_DATA_X + LABEL_WIDTH + VALUE_OFFSET, PHYSICAL_DATA_Y))
    surface.blit(height_text, value_rect)
    ```
  - [ ] Render weight line (same pattern, offset by LINE_HEIGHT):
    ```python
    weight_y = PHYSICAL_DATA_Y + LINE_HEIGHT
    # ... same label/value pattern for weight ...
    ```
  - [ ] Handle placeholder display if height or weight is 0 or negative:
    ```python
    height_value = "???" if self.height <= 0 else f"{self.height:.1f}m"
    weight_value = "???" if self.weight <= 0 else f"{self.weight:.1f}kg"
    ```

- [ ] **Task 5: Integrate Physical Data into DetailScreen Render Flow** (AC: #3)
  - [ ] Add call to `_render_physical_data()` in `DetailScreen.render()` method:
    ```python
    def render(self, surface: pygame.Surface):
        # ... existing sprite, stats, type badges rendering ...
        self._render_physical_data(surface)  # NEW
    ```
  - [ ] Ensure physical data renders AFTER sprite and type badges (visual layering)
  - [ ] Verify positioning does not overlap other UI elements
  - [ ] Test on both 480x320 and 800x480 resolutions for layout consistency

- [ ] **Task 6: Implement Data Validation and Edge Case Handling** (AC: #6, #7)
  - [ ] In `_load_pokemon_data()`, add validation after loading physical data:
    ```python
    # Warn about unrealistic values (data quality check)
    if self.height > 100:
        logging.warning(f"Unusually large height for Pokemon #{self.pokemon_id}: {self.height}m")
    if self.weight > 10000:
        logging.warning(f"Unusually heavy weight for Pokemon #{self.pokemon_id}: {self.weight}kg")
    
    # Replace invalid with placeholder indicators
    if self.height <= 0:
        logging.warning(f"Invalid height for Pokemon #{self.pokemon_id}, using placeholder")
        self.height = -1  # Signals to render "???"
    if self.weight <= 0:
        logging.warning(f"Invalid weight for Pokemon #{self.pokemon_id}, using placeholder")
        self.weight = -1  # Signals to render "???"
    ```
  - [ ] Test with mock database returning None, 0, negative values
  - [ ] Test with extreme values (very tall: Wailord, very heavy: Groudon)
  - [ ] Verify application does not crash on invalid data

- [ ] **Task 7: Apply Color and Typography Styling** (AC: #4, #9)
  - [ ] Use Colors.ICE_BLUE (168, 230, 255) for labels
  - [ ] Use Colors.HOLOGRAM_WHITE (232, 244, 248) for values
  - [ ] Load Rajdhani font in on_enter():
    ```python
    try:
        self.physical_data_font = pygame.font.Font("path/to/Rajdhani-Regular.ttf", 16)
    except:
        logging.warning("Rajdhani font not found, using default")
        self.physical_data_font = pygame.font.Font(None, 16)
    ```
  - [ ] Cache font in instance variable to avoid reloading each frame
  - [ ] Verify right-alignment for labels, left-alignment for values
  - [ ] Test visual consistency with stat labels and values (same color scheme)

- [ ] **Task 8: Add Unit Tests for Physical Data Methods** (AC: #5, #6, #7, #8)
  - [ ] Create tests in `tests/test_database.py`:
    ```python
    def test_get_pokemon_physical_data_valid():
        """Test loading physical data for Pikachu."""
        with Database() as db:
            height, weight = db.get_pokemon_physical_data(25)  # Pikachu
            assert abs(height - 0.4) < 0.01  # 4 dm = 0.4 m
            assert abs(weight - 6.0) < 0.01  # 60 hg = 6.0 kg
    
    def test_get_pokemon_physical_data_large():
        """Test loading physical data for Onix (very large)."""
        with Database() as db:
            height, weight = db.get_pokemon_physical_data(95)  # Onix
            assert height > 8.0  # Onix is 8.8m
            assert weight > 200.0  # Onix is 210kg
    
    def test_get_pokemon_physical_data_invalid():
        """Test handling invalid Pokemon ID."""
        with Database() as db:
            height, weight = db.get_pokemon_physical_data(999)  # Invalid ID
            assert height == 0.0
            assert weight == 0.0
    ```
  - [ ] Create tests in `tests/test_detail_screen.py`:
    ```python
    def test_physical_data_display_pikachu():
        """Test height and weight rendered for Pikachu."""
        detail_screen = DetailScreen(screen_manager, pokemon_id=25)
        detail_screen.on_enter()
        
        assert detail_screen.height == 0.4
        assert detail_screen.weight == 6.0
        # Render and verify no crashes
        surface = pygame.Surface((480, 320))
        detail_screen.render(surface)
    
    def test_physical_data_formatting():
        """Test height/weight string formatting."""
        detail_screen = DetailScreen(screen_manager, pokemon_id=25)
        detail_screen.on_enter()
        
        height_str = f"{detail_screen.height:.1f}m"
        weight_str = f"{detail_screen.weight:.1f}kg"
        
        assert height_str == "0.4m"
        assert weight_str == "6.0kg"
    
    def test_physical_data_placeholder_handling():
        """Test placeholder display for invalid data."""
        detail_screen = DetailScreen(screen_manager, pokemon_id=25)
        detail_screen.height = -1  # Invalid marker
        detail_screen.weight = -1
        
        # Should render "???" without crashing
        surface = pygame.Surface((480, 320))
        detail_screen.render(surface)
    ```

- [ ] **Task 9: Performance Profiling and Optimization** (AC: #10)
  - [ ] Profile physical data rendering with PerformanceMonitor:
    ```python
    start = time.perf_counter()
    self._render_physical_data(surface)
    elapsed = time.perf_counter() - start
    
    if elapsed > 0.002:  # 2ms threshold
        logging.warning(f"Physical data rendering took {elapsed*1000:.2f}ms (target: <2ms)")
    ```
  - [ ] Optimize if > 2ms:
    - Pre-render text surfaces in on_enter() (cache formatted strings)
    - Use smaller font size if text rendering is slow
    - Simplify layout calculations
  - [ ] Verify overall DetailScreen render time < 33ms per frame
  - [ ] Test with rapid L/R navigation (stress test physical data loading/rendering)

- [ ] **Task 10: Integration Testing and Visual Verification** (AC: All)
  - [ ] Test with specific Pokémon covering edge cases:
    - Pikachu #25: Small (0.4m, 6.0kg) - typical size
    - Onix #95: Very tall (8.8m, 210.0kg) - test large values
    - Diglett #50: Very small (0.2m, 0.8kg) - test small values
    - Wailord #321: Huge (14.5m, 398.0kg) - test extreme size (Gen 3)
  - [ ] Verify physical data positioning on different screen sizes (480x320, 800x480)
  - [ ] Verify no overlap with sprite, stats, type badges
  - [ ] Verify text is fully visible (no cutoff)
  - [ ] Verify color and typography match holographic aesthetic
  - [ ] Compare visual output to UX spec (if detailed mockups exist)
  - [ ] Test error handling: mock database with missing data, verify "???" displayed

- [ ] **Task 11: Update Documentation and Code Comments** (AC: All)
  - [ ] Add docstrings to new methods:
    - `Database.get_pokemon_physical_data()` - explain unit conversion
    - `DetailScreen._render_physical_data()` - explain layout and formatting
  - [ ] Document unit conversion formulas in comments:
    ```python
    # PokéAPI stores height in decimeters (dm), weight in hectograms (hg)
    # Convert: meters = decimeters / 10, kilograms = hectograms / 10
    ```
  - [ ] Update architecture.md if physical data pattern is reusable
  - [ ] Run all existing tests to verify no regressions
  - [ ] Verify all 10 ACs satisfied before marking story complete

## Dev Notes

### Learnings from Previous Story (Story 3.3)

**From Story 3-3-type-badge-display-on-detail-view (Status: review)**

Story 3.3 added type badge display near the sprite, establishing patterns for database integration, rendering, and styling. Physical measurements will follow similar patterns but with simpler rendering (no rounded rectangles, just text).

**Database Query Pattern Established:**
- Use `Database.get_pokemon_types(pokemon_id)` as reference for query structure
- Always use parameterized queries: `cursor.execute("SELECT ... WHERE id = ?", (pokemon_id,))`
- Return processed data from Database methods (type names as List[str])
- Profile query time: < 50ms target
- Handle None/missing data gracefully

**Rendering Pattern from Type Badges:**
- Create dedicated `_render_X()` method for each UI component
- Load fonts in `on_enter()`, cache in instance variables
- Define positioning constants at method level or class level
- Use Colors constants (ICE_BLUE for labels, HOLOGRAM_WHITE for values)
- Profile rendering time: < 5ms for type badges, target < 2ms for physical data (simpler rendering)

**Color and Typography Consistency:**
- Labels use ice blue (#a8e6ff) - matches stat labels
- Values use white (#ffffff) - matches stat values
- Font: Rajdhani 16px - matches other DetailScreen text
- Holographic aesthetic maintained throughout

**Performance Baseline from Story 3.3:**
- Type badge rendering: < 2ms per frame (actual performance)
- Database query (get_pokemon_types): < 10ms typical
- Total DetailScreen render: < 20ms (under 33ms budget for 30 FPS)

**What This Story Adds:**
- Physical data (height, weight) from pokemon table
- Unit conversion: decimeters → meters, hectograms → kilograms
- Simple text rendering (no complex shapes like type badges)
- Label/value layout with right/left alignment
- Validation for unrealistic values (data quality checks)
- Placeholder "???" for missing data

**Key Differences from Type Badges:**
- Simpler rendering: just text labels and values, no rounded rectangles or borders
- Fixed positioning: height and weight always appear below sprite
- No variable count: always 2 lines (height + weight), unlike 1-2 type badges
- Unit conversion required: database stores decimeters/hectograms, display meters/kilograms

[Source: docs/sprint-artifacts/3-3-type-badge-display-on-detail-view.md#Dev-Agent-Record]

---

**From Story 3.2 - Stat Bars**

Story 3.2 established the stat display panel on the right side of DetailScreen. Physical data will complement this by showing additional Pokémon characteristics.

**Layout Established:**
- Sprite on left (50-60% width)
- Stats panel on right (40% width)
- Type badges below/near sprite (Story 3.3)
- Physical data below sprite and type badges (this story)

**Typography Pattern:**
- Label: Rajdhani, ice blue (#a8e6ff)
- Value: Rajdhani, white (#ffffff)
- Right-align labels, left-align values for clean layout

[Source: docs/sprint-artifacts/3-2-six-base-stats-with-visual-progress-bars.md]

### Architecture Context

This story implements **physical measurements display** on DetailScreen following established database query and rendering patterns.

**Database Schema:**
```
pokemon table columns:
- id (INTEGER PRIMARY KEY)
- name (TEXT)
- height (INTEGER) -- stored in decimeters (dm)
- weight (INTEGER) -- stored in hectograms (hg)
```

**Unit Conversion Requirement:**
PokéAPI (data source) uses:
- Height: decimeters (1 dm = 0.1 m)
- Weight: hectograms (1 hg = 0.1 kg)

Display uses:
- Height: meters (m)
- Weight: kilograms (kg)

Conversion: divide by 10 for both height and weight

**Database Access Pattern:**
```python
# ✅ CORRECT - Parameterized query
def get_pokemon_physical_data(self, pokemon_id: int) -> Tuple[float, float]:
    cursor = self.conn.execute(
        "SELECT height, weight FROM pokemon WHERE id = ?",
        (pokemon_id,)
    )
    row = cursor.fetchone()
    if not row:
        return (0.0, 0.0)
    
    height_dm, weight_hg = row
    height_m = height_dm / 10.0 if height_dm else 0.0
    weight_kg = weight_hg / 10.0 if weight_hg else 0.0
    
    return (height_m, weight_kg)

# ❌ INCORRECT - Never use string formatting
query = f"SELECT height, weight FROM pokemon WHERE id = {pokemon_id}"  # SQL injection risk
```

**Rendering Pattern:**
```python
class DetailScreen(Screen):
    def on_enter(self):
        """Pre-load physical data."""
        self._load_pokemon_data()  # Loads self.height, self.weight
        self.physical_data_font = pygame.font.Font("Rajdhani", 16)
    
    def render(self, surface: pygame.Surface):
        """Render all DetailScreen elements."""
        self._render_sprite(surface)
        self._render_stat_bars(surface)
        self._render_type_badges(surface)
        self._render_physical_data(surface)  # NEW in Story 3.4
        
    def _render_physical_data(self, surface: pygame.Surface):
        """Render height and weight below sprite."""
        x, y = PHYSICAL_DATA_X, PHYSICAL_DATA_Y
        
        # Height line
        height_label = self.physical_data_font.render("Height:", True, Colors.ICE_BLUE)
        surface.blit(height_label, (x, y))
        
        height_value = f"{self.height:.1f}m" if self.height > 0 else "???"
        height_text = self.physical_data_font.render(height_value, True, Colors.HOLOGRAM_WHITE)
        surface.blit(height_text, (x + LABEL_WIDTH + VALUE_OFFSET, y))
        
        # Weight line
        y += LINE_HEIGHT
        weight_label = self.physical_data_font.render("Weight:", True, Colors.ICE_BLUE)
        surface.blit(weight_label, (x, y))
        
        weight_value = f"{self.weight:.1f}kg" if self.weight > 0 else "???"
        weight_text = self.physical_data_font.render(weight_value, True, Colors.HOLOGRAM_WHITE)
        surface.blit(weight_text, (x + LABEL_WIDTH + VALUE_OFFSET, y))
```

[Source: docs/architecture.md#Database-Access-Pattern]

### Epic Technical Specification Context

This story implements part of **AC #1** from Epic 3 Tech Spec (Detail Screen Display).

**Physical Data Specification:**
- Height displayed in meters with one decimal place (e.g., "0.4m", "8.8m")
- Weight displayed in kilograms with one decimal place (e.g., "6.0kg", "210.0kg")
- Labels use ice blue (#a8e6ff)
- Values use white (#ffffff)
- Font: Rajdhani, 16px
- Positioning: Lower section of detail panel, below sprite and type badges

**Layout Rules:**
```
DetailScreen Physical Data (Below Sprite):

   Height:  0.4m
   Weight:  6.0kg

Label alignment: Right-aligned at fixed width (80px)
Value alignment: Left-aligned after label with 10px gap
Vertical spacing: 8px between height and weight lines
```

**Formatting Examples:**
- Pikachu #25: Height: 0.4m, Weight: 6.0kg
- Onix #95: Height: 8.8m, Weight: 210.0kg
- Diglett #50: Height: 0.2m, Weight: 0.8kg

[Source: docs/sprint-artifacts/tech-spec-epic-2-detail-view-with-audio.md#AC-1-Detail-Screen-Display]

### Database Schema Details

**pokemon Table Structure:**
```sql
CREATE TABLE pokemon (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    height INTEGER,        -- decimeters (dm)
    weight INTEGER,        -- hectograms (hg)
    base_experience INTEGER,
    generation INTEGER
);
```

**Example Data:**
```sql
-- Pikachu #25
INSERT INTO pokemon VALUES (25, 'Pikachu', 4, 60, 112, 1);
-- height: 4 dm = 0.4 m
-- weight: 60 hg = 6.0 kg

-- Onix #95
INSERT INTO pokemon VALUES (95, 'Onix', 88, 2100, 77, 1);
-- height: 88 dm = 8.8 m
-- weight: 2100 hg = 210.0 kg
```

**Query Performance:**
- Single row fetch by id: < 1ms typical (indexed primary key)
- Part of _load_pokemon_data() batch load: < 50ms total budget

[Source: docs/database_schema.md#pokemon-table]

### Component Locations

**Files to Modify:**
- `src/data/database.py` - Add `get_pokemon_physical_data()` method (if not exists)
- `src/ui/detail_screen.py` - Add `_render_physical_data()` method, update `_load_pokemon_data()` and `render()`
- `tests/test_database.py` - Add tests for physical data query
- `tests/test_detail_screen.py` - Add tests for physical data rendering

**Files to Reference (Already Exist):**
- `src/ui/colors.py` - ICE_BLUE and HOLOGRAM_WHITE constants
- `src/ui/screen.py` - Base Screen class with lifecycle methods
- `src/performance_monitor.py` - For profiling render time

**No New Dependencies:**
- Uses pygame for text rendering (already required)
- Uses existing database connection
- Uses existing font loading pattern

### Physical Data Rendering Implementation Details

**Label/Value Alignment Pattern:**
```python
# Right-align label at fixed width
label_surface = font.render("Height:", True, Colors.ICE_BLUE)
label_rect = label_surface.get_rect(topright=(LABEL_X + LABEL_WIDTH, y))
surface.blit(label_surface, label_rect)

# Left-align value after label
value_surface = font.render("0.4m", True, Colors.HOLOGRAM_WHITE)
value_rect = value_surface.get_rect(topleft=(LABEL_X + LABEL_WIDTH + VALUE_OFFSET, y))
surface.blit(value_surface, value_rect)
```

**Unit Conversion Helper (Optional):**
```python
def convert_height_to_meters(decimeters: int) -> float:
    """Convert height from decimeters to meters.
    
    Args:
        decimeters: Height in decimeters (PokéAPI format)
        
    Returns:
        Height in meters (display format)
    """
    return decimeters / 10.0 if decimeters else 0.0

def convert_weight_to_kg(hectograms: int) -> float:
    """Convert weight from hectograms to kilograms.
    
    Args:
        hectograms: Weight in hectograms (PokéAPI format)
        
    Returns:
        Weight in kilograms (display format)
    """
    return hectograms / 10.0 if hectograms else 0.0
```

**Complete Physical Data Method:**
```python
def _render_physical_data(self, surface: pygame.Surface):
    """Render height and weight measurements.
    
    Displays physical measurements below the sprite with clean label/value layout.
    Labels are right-aligned, values are left-aligned for readability.
    """
    # Positioning constants
    x = 30  # Left margin
    y = self.sprite_y + self.sprite_height + 100  # Below sprite and type badges
    label_width = 80  # Fixed width for right-aligned labels
    value_offset = 10  # Gap between label and value
    line_height = 24  # Spacing between lines
    
    # Format values with placeholders for invalid data
    height_str = f"{self.height:.1f}m" if self.height > 0 else "???"
    weight_str = f"{self.weight:.1f}kg" if self.weight > 0 else "???"
    
    # Render height line
    height_label = self.physical_data_font.render("Height:", True, Colors.ICE_BLUE)
    label_rect = height_label.get_rect(topright=(x + label_width, y))
    surface.blit(height_label, label_rect)
    
    height_value = self.physical_data_font.render(height_str, True, Colors.HOLOGRAM_WHITE)
    value_rect = height_value.get_rect(topleft=(x + label_width + value_offset, y))
    surface.blit(height_value, value_rect)
    
    # Render weight line
    y += line_height
    weight_label = self.physical_data_font.render("Weight:", True, Colors.ICE_BLUE)
    label_rect = weight_label.get_rect(topright=(x + label_width, y))
    surface.blit(weight_label, label_rect)
    
    weight_value = self.physical_data_font.render(weight_str, True, Colors.HOLOGRAM_WHITE)
    value_rect = weight_value.get_rect(topleft=(x + label_width + value_offset, y))
    surface.blit(weight_value, value_rect)
```

### Performance Profiling Strategy

**Profiling Physical Data Rendering:**
```python
import time

def render(self, surface: pygame.Surface):
    """Render DetailScreen with performance tracking."""
    # ... sprite, stats, type badges rendering ...
    
    # Profile physical data rendering
    start = time.perf_counter()
    self._render_physical_data(surface)
    elapsed = time.perf_counter() - start
    
    if elapsed > 0.002:  # 2ms threshold
        logging.warning(f"Physical data rendering took {elapsed*1000:.2f}ms (target: <2ms)")
    
    # Track overall frame rate
    self.perf_monitor.record_frame()
    if self.perf_monitor.get_average_fps() < 30:
        logging.warning(f"FPS drop: {self.perf_monitor.get_average_fps():.1f}")
```

**Optimization Strategies (if needed):**
1. Pre-render text surfaces in on_enter() with formatted strings
2. Cache surfaces for common patterns (most Pokémon have height < 10m, weight < 100kg)
3. Simplify font rendering if bottleneck
4. Reduce font size if text rendering is slow (unlikely for 2 lines)

### Testing Strategy

**Unit Tests:**
```python
def test_convert_height_dm_to_m():
    """Test decimeter to meter conversion."""
    assert convert_height_to_meters(4) == 0.4  # Pikachu
    assert convert_height_to_meters(88) == 8.8  # Onix
    assert convert_height_to_meters(0) == 0.0  # Invalid

def test_convert_weight_hg_to_kg():
    """Test hectogram to kilogram conversion."""
    assert convert_weight_to_kg(60) == 6.0  # Pikachu
    assert convert_weight_to_kg(2100) == 210.0  # Onix
    assert convert_weight_to_kg(0) == 0.0  # Invalid
```

**Integration Tests:**
```python
def test_physical_data_display_pikachu():
    """Test height and weight for Pikachu."""
    detail_screen = DetailScreen(screen_manager, pokemon_id=25)
    detail_screen.on_enter()
    
    assert detail_screen.height == 0.4
    assert detail_screen.weight == 6.0

def test_physical_data_display_onix():
    """Test large physical measurements (Onix)."""
    detail_screen = DetailScreen(screen_manager, pokemon_id=95)
    detail_screen.on_enter()
    
    assert detail_screen.height == 8.8
    assert detail_screen.weight == 210.0

def test_physical_data_formatting():
    """Test string formatting for display."""
    detail_screen = DetailScreen(screen_manager, pokemon_id=25)
    detail_screen.on_enter()
    
    height_str = f"{detail_screen.height:.1f}m"
    weight_str = f"{detail_screen.weight:.1f}kg"
    
    assert height_str == "0.4m"
    assert weight_str == "6.0kg"

def test_physical_data_placeholder():
    """Test placeholder display for invalid data."""
    detail_screen = DetailScreen(screen_manager, pokemon_id=25)
    detail_screen.height = -1  # Invalid
    detail_screen.weight = -1
    
    # Should render without crashing
    surface = pygame.Surface((480, 320))
    detail_screen.render(surface)
```

**Edge Cases to Test:**
- Pikachu #25: Normal size (0.4m, 6.0kg)
- Onix #95: Very large (8.8m, 210.0kg)
- Diglett #50: Very small (0.2m, 0.8kg)
- Wailord #321: Extreme size (14.5m, 398.0kg) - Gen 3
- Invalid ID (999): Should return (0.0, 0.0)
- Database missing data: Should show "???" placeholder

### References

- [Source: docs/PRD.md#FR3.1-Detail-Screen-Display] - Physical measurements requirement
- [Source: docs/architecture.md#Database-Access-Pattern] - Parameterized queries
- [Source: docs/database_schema.md#pokemon-table] - Height and weight storage format
- [Source: docs/sprint-artifacts/tech-spec-epic-2-detail-view-with-audio.md#AC-1] - Physical data spec
- [Source: docs/sprint-artifacts/3-3-type-badge-display-on-detail-view.md#Learnings] - Rendering patterns

## Dev Agent Record

### Context Reference
- `docs/sprint-artifacts/3-4-physical-measurements-display.context.xml` (Generated: 2025-11-16)

### Agent Model Used
<!-- AI agent model name and version will be recorded here -->

### Debug Log References
<!-- Links to relevant debug logs or error traces during implementation -->

### Completion Notes List
<!-- After implementation:
- What was implemented
- What was deferred or descoped
- What technical decisions were made
- What learnings should carry forward
-->

### File List
<!-- After implementation, list all files created or modified -->

## Change Log

**2025-11-16: Story Drafted by SM Agent (Bob)**
- Created story file with BDD-style acceptance criteria (10 ACs covering height display, weight display, positioning, layout, database integration, unit conversion, edge cases, formatting, visual consistency, performance)
- Added 11 detailed tasks with subtasks for physical data implementation
- Integrated learnings from Story 3.3 (database patterns, rendering patterns, color/typography consistency, performance baseline)
- Documented database schema (height in decimeters, weight in hectograms requiring conversion)
- Specified unit conversion formulas: meters = decimeters / 10, kilograms = hectograms / 10
- Created comprehensive dev notes covering: architecture patterns, tech spec alignment, database schema, rendering implementation, performance profiling, testing strategy
- Defined layout specifications: right-aligned labels (80px width), left-aligned values (10px offset), 8px vertical spacing
- Specified typography: Rajdhani 16px for labels and values, ice blue for labels, white for values
- Status: **drafted** - Ready for story context generation or developer implementation

**2025-11-16: Story Context Generated and Marked Ready for Dev by SM Agent (Bob)**
- Generated comprehensive story context XML: `docs/sprint-artifacts/3-4-physical-measurements-display.context.xml`
- Context includes: 10 acceptance criteria (detailed Given/When/Then), 11 tasks, 5 doc artifacts (PRD, Architecture, UX Spec, Epic Tech Spec, DB Schema), 6 code artifacts (DetailScreen, Database, Colors, sprite_loader, tests)
- Documented dependencies: pygame, sqlite3, logging, internal modules, Rajdhani font
- Specified technical constraints: unit conversion (dm→m, hg→kg), parameterized queries, <2ms render time, <50ms query time, positioning to avoid overlap
- Defined 4 interfaces: Database.get_pokemon_by_id (existing), optional Database.get_pokemon_physical_data (new), DetailScreen._render_physical_data (new), DetailScreen.render modification
- Added testing strategy with 15 test ideas mapped to ACs: unit conversion, edge cases (None/0/negative/extreme values), formatting consistency, positioning, performance
- Updated story status: **drafted** → **ready-for-dev**
- Updated sprint-status.yaml: 3-4-physical-measurements-display marked ready-for-dev
- Story ready for developer (Amelia) implementation with complete context

