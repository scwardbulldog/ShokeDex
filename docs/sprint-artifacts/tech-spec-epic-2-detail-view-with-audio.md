# Epic Technical Specification: Detail View Implementation

Date: 2025-11-15
Author: King
Epic ID: 2
Status: Draft

---

## Overview

Epic 2 implements the comprehensive Pokémon detail screen that transforms the DetailScreen from showing basic information to displaying complete Pokémon data including base stats with visual progress bars, type badges, physical measurements, and Pokédex flavor text. This epic focuses on the visual presentation and data display that makes the detail view informative and beautiful.

The core user experience is: user presses A on HomeScreen → DetailScreen loads with large sprite → user sees all 6 base stats with colored bars → can navigate to adjacent Pokémon with L/R while staying in detail view → press B to return to HomeScreen. This delivers the comprehensive Pokémon information display central to the Pokédex experience.

This epic implements stat visualization with holographic blue styling per UX spec, description text wrapping for readability, and ensures rendering maintains the 30+ FPS performance target on Raspberry Pi 3B+ hardware. Audio integration is deferred to a post-MVP epic to allow focus on visual polish and data presentation.

## Objectives and Scope

**In Scope:**
- DetailScreen layout with sprite, stats, types, and description per UX design
- 6 base stats displayed with visual progress bars (HP, Attack, Defense, Sp.Atk, Sp.Def, Speed)
- Stat bars color-coded by value (low=gray, high=cyan, exceptional=orange)
- Type badges with holographic styling matching HomeScreen
- Physical measurements display (height, weight in metric)
- Pokédex description text with 4-line wrapping and ellipsis (authentic flavor text from database)
- Description rendering: 16px Rajdhani, ice blue, max 400px width, 4 lines with "..." truncation
- L/R navigation within detail view (stay in DetailScreen, switch Pokémon)
- Smooth sprite transitions when navigating to adjacent Pokémon

**Out of Scope:**
- Audio integration and Pokémon cries (deferred to post-MVP Audio epic)
- Evolution chain display (covered in Epic 4)
- Type effectiveness/matchups (covered in Epic 6 - Relationships View)
- Pokémon forms and variants (Alolan, Mega, etc. - future)
- Move lists (structure exists but not populated per PRD)
- Ability descriptions (basic ability name shown, details future)
- Background music or UI sound effects
- Scrollable description text (fixed 4-line display)

**Success Criteria:**
- DetailScreen displays all 6 base stats with accurate values from database
- Stat bars render proportionally (max 255 = 100% bar width)
- Description text wraps correctly at 4 lines with ellipsis for overflow
- L/R buttons navigate to adjacent Pokémon without leaving DetailScreen
- Frame rate maintains 30+ FPS during all operations
- Adjacent navigation completes in < 300ms (sprite load + data fetch)
- Visual design matches UX spec (holographic blue, stat bar colors)
- All text remains within display boundaries (no cutoff)

## System Architecture Alignment

This epic aligns with the architecture's **AudioManager Integration** and **DetailScreen** sections, following established manager singleton patterns.

**Architecture Components Involved:**
- `src/ui/detail_screen.py` - Primary implementation for stats, types, description rendering
- `src/state_manager.py` - Stores/retrieves last viewed Pokémon
- `src/data/database.py` - Queries for stats, types, description, physical data
- `src/ui/sprite_loader.py` - Loads detail-sized sprites (128x128)
- `src/ui/screen_manager.py` - Screen lifecycle management (on_enter/on_exit)
- `src/ui/colors.py` - Holographic blue palette and stat bar colors

**Architectural Patterns Applied:**
1. **Manager Access Pattern:** DetailScreen accesses managers via screen_manager (no new instances)
2. **Screen Lifecycle:** Use on_enter() to load data, on_exit() to save state
3. **Lazy Loading:** Sprites loaded on demand with caching
4. **Database Queries:** Parameterized statements for stat and type lookups
5. **Text Rendering:** Multi-line wrapping with word boundaries, fixed 4-line max

**Constraints:**
- Must maintain 30+ FPS during rendering (per NFR-P1)
- Description text limited to 4 lines to prevent layout overflow
- Sprite size fixed at 128x128 for detail view
- Database queries must return all data in single transaction (< 50ms)

**Integration Points:**
- DetailScreen.on_enter() → StateManager.get_last_viewed() for restoration
- DetailScreen.on_exit() → StateManager.set_last_viewed(pokemon_id)
- DetailScreen._load_pokemon_data() → Database.get_pokemon_stats(id)
- DetailScreen._render_stat_bars() → Uses colors.py holographic palette
- DetailScreen._render_description() → Text wrapping utility with 4-line limit

## Detailed Design

### Services and Modules

| Module | Responsibility | Inputs | Outputs | Owner |
|--------|---------------|--------|---------|-------|
| **DetailScreen** | Comprehensive Pokémon information display | pokemon_id, InputAction (L/R/B) | Rendered screen with stats, types, description | UI Team |
| **Database** | Stats, types, physical data, descriptions | pokemon_id | Stat values, type names, height/weight, description | Data Team |
| **StateManager** | Last viewed Pokémon persistence | get_last_viewed(), set_last_viewed(id) | pokemon_id for restoration | Core Team |
| **SpriteLoader** | Detail-sized sprite loading | pokemon_id, size="detail" | 128x128 sprite Surface | UI Team |
| **TextRenderer** | Multi-line text wrapping | text, font, max_width, max_lines | List of rendered line Surfaces | UI Team |

**Key Interfaces:**

```python
# DetailScreen new/modified methods
class DetailScreen(Screen):
    def __init__(self, screen_manager, pokemon_id: int):
        self.pokemon_id: int = pokemon_id
        self.pokemon_data: Dict = {}
        self.stats: List[Dict] = []  # 6 stat entries
        self.types: List[str] = []
        self.description_lines: List[pygame.Surface] = []  # Pre-rendered text
        
    def on_enter(self) -> None:
        """Called when screen becomes active - load data."""
        self._load_pokemon_data()
        self._render_description_lines()
    
    def on_exit(self) -> None:
        """Called when leaving screen - save state."""
        self.screen_manager.state_manager.set_last_viewed(self.pokemon_id)
        
    def _load_pokemon_data(self) -> None:
        """Query database for all Pokemon details."""
        
    def _render_stat_bars(self, surface: pygame.Surface) -> None:
        """Draw 6 stat bars with color coding."""
        
    def _render_description_lines(self) -> None:
        """Wrap description text to max 4 lines with ellipsis.
        
        Uses 16px Rajdhani font, ice blue color (#a8e6ff).
        Max width: 400px, max lines: 4.
        Truncates with '...' on line 4 if needed.
        """
        
    def _navigate_adjacent(self, direction: int) -> None:
        """Switch to next/prev Pokemon, stay in DetailScreen.
        Args:
            direction: 1 for next (R), -1 for previous (L)
        """
```

### Data Models and Contracts

**Pokemon Data Schema (from Database):**
```python
# Complete Pokemon record
{
    'id': int,              # National Dex number
    'name': str,            # Pokemon name
    'height': float,        # Meters (e.g., 0.4)
    'weight': float,        # Kilograms (e.g., 6.0)
    'description': str      # Pokedex flavor text (may be long, needs wrapping)
}
```

**Description Rendering Specification:**
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

**Stat Record Schema:**
```python
# Single stat entry (6 per Pokemon)
{
    'stat_name': str,       # "HP", "Attack", "Defense", "Sp.Atk", "Sp.Def", "Speed"
    'base_stat': int,       # Value 1-255
    'percentage': float     # base_stat / 255 for bar width
}
```

**Type Data:**
```python
# List of 1-2 type names
['Electric']              # Single type
['Water', 'Flying']       # Dual type
```



**Stat Bar Color Coding (from UX Spec):**
```python
STAT_COLORS = {
    'low': (113, 128, 150),      # 0-50: Gray
    'medium': (0, 212, 255),     # 51-100: Electric blue
    'high': (77, 247, 255),      # 101-150: Bright cyan
    'exceptional': (255, 107, 53) # 151+: Plasma orange
}

def get_stat_color(value: int) -> Tuple[int, int, int]:
    if value <= 50: return STAT_COLORS['low']
    elif value <= 100: return STAT_COLORS['medium']
    elif value <= 150: return STAT_COLORS['high']
    else: return STAT_COLORS['exceptional']
```

### APIs and Interfaces

**DetailScreen Public Interface:**
```python
class DetailScreen(Screen):
    def __init__(self, screen_manager, pokemon_id: int):
        """Initialize detail view for specific Pokemon.
        
        Args:
            screen_manager: ScreenManager instance (provides managers)
            pokemon_id: National Dex number to display (1-386)
        """
    
    def handle_input(self, action: InputAction) -> None:
        """Handle button press actions.
        
        Args:
            action: InputAction.LEFT (L) - previous Pokemon
                   InputAction.RIGHT (R) - next Pokemon
                   InputAction.BACK (B) - return to HomeScreen
        """
```

**Database Interface (New Methods):**
```python
class Database:
    def get_pokemon_stats(self, pokemon_id: int) -> List[Tuple[str, int]]:
        """Get all 6 base stats for Pokemon.
        
        Args:
            pokemon_id: National Dex number
            
        Returns:
            List of tuples: (stat_name, base_stat_value)
            Order: HP, Attack, Defense, Sp.Atk, Sp.Def, Speed
        """
    
    def get_pokemon_physical_data(self, pokemon_id: int) -> Tuple[float, float, str]:
        """Get height, weight, and description.
        
        Args:
            pokemon_id: National Dex number
            
        Returns:
            Tuple: (height_m, weight_kg, description_text)
        """
```

**AudioManager Interface (From Architecture):**
```python
class AudioManager:
    def __init__(self, volume: float = 0.7, cache_size: int = 20):
        """Initialize audio manager with LRU cache.
        
        Args:
            volume: Initial volume 0.0-1.0
            cache_size: Max number of cries in memory
        """
        
    def play_cry(self, pokemon_id: int) -> bool:
        """Play Pokemon cry, loading from disk if not cached.
        
        Args:
            pokemon_id: National Dex number (1-386)
            
        Returns:
            True if played successfully, False if file missing/error
            
        Side Effects:
            - Loads audio file if not in cache
            - Evicts LRU item if cache full
            - Logs warning if file not found
        """
```

### Workflows and Sequencing

**DetailScreen Entry Flow (From HomeScreen A Button):**
```
1. User presses A on HomeScreen
2. HomeScreen.handle_input() creates DetailScreen(screen_manager, pokemon_id)
3. ScreenManager.push(detail_screen)
4. DetailScreen.on_enter() called
   ├─> Call _load_pokemon_data()
   │   ├─> Database.get_pokemon_by_id(pokemon_id)
   │   ├─> Database.get_pokemon_stats(pokemon_id)
   │   ├─> Database.get_pokemon_types(pokemon_id)
   │   └─> Database.get_pokemon_physical_data(pokemon_id)
   ├─> Load detail sprite (128x128)
   └─> Play cry: audio_manager.play_cry(pokemon_id)
       ├─> Check cache for pokemon_id
       ├─> If not cached: Load from assets/audio/cries/{id:03d}.ogg
       ├─> If file missing: Return False, log warning, continue
       └─> If loaded: Play audio, add to cache
5. Render DetailScreen with all data
```

**Adjacent Pokemon Navigation (L/R in Detail View):**
```
1. User presses L or R while in DetailScreen
2. DetailScreen.handle_input(LEFT or RIGHT) called
3. DetailScreen._navigate_adjacent(direction) executed
   ├─> Calculate new pokemon_id: self.pokemon_id + direction
   ├─> Wrap at boundaries: 386 → 1, 0 → 386
   ├─> Stop current audio: audio_manager.stop()
   ├─> Update self.pokemon_id
   ├─> Call _load_pokemon_data() for new Pokemon
   ├─> Play new cry: audio_manager.play_cry(new_pokemon_id)
   └─> Trigger fade transition (sprite crossfade)
4. Render updated DetailScreen
```

**Stat Bar Rendering Flow:**
```
1. DetailScreen._render_stat_bars() called during render()
2. For each of 6 stats:
   ├─> Calculate bar width: (base_stat / 255) * max_bar_width
   ├─> Determine color: get_stat_color(base_stat)
   ├─> Draw empty bar background (dark gray)
   ├─> Draw filled bar (stat color with glow if high)
   ├─> Render stat label (left aligned)
   └─> Render stat value (right aligned, monospace font)
3. Apply holographic styling (borders, subtle glow)
```

**Audio Caching Flow (LRU):**
```
1. AudioManager.play_cry(pokemon_id) called
2. Check if pokemon_id in cache:
   ├─> Cache hit: Move to front of LRU, play immediately
   └─> Cache miss:
       ├─> Construct file path: f"assets/audio/cries/{pokemon_id:03d}.ogg"
       ├─> Check if file exists
       ├─> If exists: Load into pygame.mixer.Sound
       ├─> If cache full: Evict least recently used cry
       ├─> Add new cry to cache front
       └─> Play audio
3. If file missing: Log warning, return False, silent operation
```

## Non-Functional Requirements

### Performance

**Target Metrics (Raspberry Pi 3B+):**
- Frame rate: 30+ FPS during all operations
- DetailScreen render: < 33ms per frame (maintains 30 FPS)
- Adjacent navigation: < 300ms to load new Pokemon data + sprite
- Stat bar rendering: < 10ms per frame (6 bars + labels)
- Description rendering: < 5ms (pre-rendered lines, blit only)
- Database queries: < 50ms for all Pokemon data (single transaction)

**Performance Strategies:**
- **Sprite caching:** Reuse sprite cache from HomeScreen (shared loader)
- **Single query optimization:** Fetch all Pokemon data in one database transaction
- **Stat bar pre-calculation:** Calculate bar widths once, not per frame
- **Description pre-rendering:** Wrap and render text lines in on_enter(), blit cached surfaces in render()
- **Dirty rect optimization:** Only redraw changed screen regions if performance requires

**Bottleneck Mitigation:**
- If frame rate < 30 FPS: Simplify stat bar glow effects or use dirty rects
- If memory > 250MB: Reduce sprite cache size
- If navigation lag: Pre-load adjacent Pokemon sprites during transition
- If text rendering slow: Cache rendered lines, only re-render on Pokemon change

### Security

**SQL Injection Prevention:**
- ✅ All stat queries use parameterized statements
- ✅ Pokemon IDs validated as integers 1-386 before queries
- ❌ Never use string formatting in SQL

**File Path Safety:**
```python
# ✅ CORRECT - Safe path construction
audio_path = Path("assets/audio/cries") / f"{pokemon_id:03d}.ogg"

# ❌ WRONG - Potential directory traversal
audio_path = f"assets/audio/cries/{user_input}.ogg"
```

**Audio File Validation:**
- Only load .ogg files from known directory
- Pokemon ID constrained to 001-386 (no arbitrary paths)
- File existence checked before load attempt

### Reliability/Availability

**Error Handling:**
- **Database query failure:** Show error message, display partial data if possible
- **Missing sprite:** Text placeholder (per Epic 1 pattern)
- **Invalid stat values:** Clamp to 0-255 range, log validation warning
- **Description text too long:** Truncate at 4 lines with ellipsis (expected behavior)
- **Missing description:** Show "No description available" placeholder

**Graceful Degradation:**
- Missing stats → Show "???" placeholder, log error
- Missing description → Show placeholder text
- Sprite load failure → Text-only display with Pokemon name

**Recovery Strategies:**
- Database transaction failure: Retry up to 3 times with exponential backoff
- Memory pressure: Clear sprite cache except current Pokemon
- Render failure: Fall back to simplified layout without glow effects

### Observability

**Logging Requirements:**
```python
logging.info(f"DetailScreen entered for Pokemon #{pokemon_id}: {name}")
logging.info(f"Loaded {len(stats)} stats for Pokemon #{pokemon_id}")
logging.info(f"Description wrapped to {line_count} lines")
logging.warning(f"Stats query returned {len(results)}, expected 6")
logging.warning(f"Description exceeds 4 lines, truncating")
logging.error(f"Database query failed: {error}")
logging.debug(f"DetailScreen render time: {render_ms}ms")
```

**Performance Metrics:**
- Track DetailScreen render time (target < 33ms for 30 FPS)
- Track adjacent navigation time (target < 300ms)
- Track database query time (target < 50ms)
- Track description rendering time (target < 5ms)

**Debug Signals:**
- Render events: `DEBUG: DetailScreen rendered in 28ms`
- Navigation: `DEBUG: Adjacent nav #25 → #26 (sprite loaded in 120ms)`
- Text wrapping: `DEBUG: Description wrapped to 3 lines (no truncation)`

## Dependencies and Integrations

**Python Dependencies:**
- `pygame >= 2.5.0` - Graphics + pygame.mixer for audio
- `Pillow >= 10.0.0` - Image loading
- SQLite3 (stdlib) - Database queries

**Internal Module Dependencies:**
- `src/ui/screen.py` - Base Screen class
- `src/ui/screen_manager.py` - Manager injection, navigation
- `src/state_manager.py` - Last viewed Pokemon persistence
- `src/data/database.py` - Stats, types, physical data queries
- `src/ui/sprite_loader.py` - Detail sprite loading
- `src/ui/colors.py` - Stat bar color palette and holographic styling

**Asset Dependencies:**
- Pokemon sprites (✅ exists): `assets/sprites/detail/*.png` (128x128)
- Fonts (from UX spec): 
  - Rajdhani Regular/Medium for body text and labels
  - Orbitron Bold for Pokemon names
  - Share Tech Mono for stat values and Dex numbers

**Database Schema Dependencies:**
- `pokemon` table: id, name, height, weight
- `pokemon_stats` table: pokemon_id, stat_id, base_stat
- `stats` table: id, name (HP, Attack, Defense, etc.)
- `pokemon_types` table: pokemon_id, type_id, slot
- `types` table: id, name
- `pokemon` table: description column (Pokedex flavor text)

**Integration Points:**
- **StateManager:** Save last viewed Pokemon on screen exit
- **Database:** Single transaction for all Pokemon data fetch
- **Epic 1 HomeScreen:** Passes pokemon_id to DetailScreen constructor
- **SpriteLoader:** Shared cache for efficient sprite reuse

## Acceptance Criteria (Authoritative)

**AC #1: Comprehensive Stat Display**
- DetailScreen shows all 6 base stats: HP, Attack, Defense, Sp.Atk, Sp.Def, Speed
- Each stat displays: label (left), visual progress bar (center), numeric value (right)
- Stat bars fill proportionally: (base_stat / 255) * bar_width
- Stat values accurate from database (no hardcoded values)

**AC #2: Stat Bar Color Coding**
- Stats 0-50: Gray (#718096)
- Stats 51-100: Electric blue (#00d4ff)
- Stats 101-150: Bright cyan (#4df7ff)
- Stats 151+: Plasma orange (#ff6b35)
- High stats (100+) have subtle glow effect

**AC #3: Type Badge Display**
- Pokemon types shown as visual badges (matching HomeScreen style)
- Single type: One badge displayed
- Dual type: Two badges displayed side-by-side
- Type colors match holographic palette from UX spec

**AC #4: Physical Measurements**
- Height displayed in meters (e.g., "0.4m")
- Weight displayed in kilograms (e.g., "6.0kg")
- Values accurate from database pokemon table

**AC #5: Pokedex Description Display**
- Authentic flavor text displayed from database
- Text wrapped at word boundaries to max 400px width
- Maximum 4 lines displayed with 22.4px line height
- Text exceeding 4 lines truncated with "..." on line 4
- Rajdhani font, 16px size (per UX spec)
- Ice blue color (#a8e6ff) for readability
- All text remains within display boundaries

**AC #6: Adjacent Pokemon Navigation**
- L button (LEFT) navigates to previous Pokemon (id - 1)
- R button (RIGHT) navigates to next Pokemon (id + 1)
- Wrapping at boundaries: 1 → 386, 386 → 1
- Stay in DetailScreen (don't return to HomeScreen)
- New Pokemon loads with all data and sprite
- Smooth transition between Pokemon (< 300ms total)

**AC #7: Performance Requirements**
- Frame rate maintains 30+ FPS during all operations
- DetailScreen render time < 33ms per frame
- Adjacent navigation completes in < 300ms (load + render)
- Database query time < 50ms for all Pokemon data
- No memory leaks from sprite cache

**AC #8: Visual Design Compliance**
- Layout matches UX spec DetailScreen mockup
- Holographic blue styling applied (electric blue borders)
- Sprite displayed prominently (120-150px size)
- Header shows Pokemon name + Dex number
- Panel backgrounds use dark blue with transparency
- All UI elements within display boundaries (no cutoff)

## Traceability Mapping

| AC | Spec Section(s) | Component(s)/API(s) | Test Idea |
|----|-----------------|---------------------|-----------|
| **AC #1** | Detailed Design → Stat Display | `DetailScreen._render_stat_bars()`, Database.get_pokemon_stats() | Unit test: Query stats for Pikachu, verify 6 values |
| **AC #2** | Data Models → Stat Colors | `get_stat_color()`, STAT_COLORS constant | Unit test: Verify color returned for each value range |
| **AC #3** | Detailed Design → Type Badges | Database.get_pokemon_types(), type badge component | Integration test: Load dual-type Pokemon, verify 2 badges |
| **AC #4** | APIs → Physical Data | Database.get_pokemon_physical_data() | Unit test: Query Pikachu, verify height=0.4, weight=6.0 |
| **AC #5** | Data Models → Description Spec | `_render_description_lines()` | Unit test: Long text truncates at 4 lines with ellipsis |
| **AC #6** | Workflows → Adjacent Navigation | `_navigate_adjacent()`, wrapping logic | Unit test: Navigate from #1, verify wraps to #386 |
| **AC #7** | NFR Performance | All components | Performance test: Measure FPS and render times |
| **AC #8** | UX Spec → Visual Design | Rendering methods, colors.py | Visual test: Compare to UX mockup on actual hardware |

## Risks, Assumptions, Open Questions

**Risks:**
1. **Long Description Text Overflow** (Medium Impact, Low Probability)
   - Risk: Some Pokédex descriptions very long, might not fit in 4 lines
   - Mitigation: Truncate with ellipsis (per AC #5), tested with longest descriptions
   - Action: Profile with Pokémon known for long descriptions (e.g., legendary Pokémon)

2. **Rendering Performance on Pi** (Medium Impact, Low Probability)
   - Risk: Complex stat bars + text rendering might drop below 30 FPS
   - Mitigation: Pre-render description lines in on_enter(), use dirty rects if needed
   - Fallback: Simplify glow effects, use cached surfaces

3. **Sprite Load Time on SD Card** (Low Impact, Medium Probability)
   - Risk: First sprite load from SD card might cause navigation lag
   - Mitigation: Sprite caching from Epic 1 already addresses this
   - Monitor: Track adjacent navigation time (target < 300ms)

**Assumptions:**
- ✅ Database has stats, types, physical data, descriptions populated
- ✅ StateManager stores last viewed Pokemon
- ✅ Detail sprites (128x128) exist for all 386 Pokemon
- ✅ Fonts (Rajdhani, Orbitron, Share Tech Mono) available or fallback works
- ✅ pygame font rendering supports multi-line text wrapping
- ✅ Description text from database is properly formatted (no HTML/markup)

**Open Questions:**
1. **Q:** What if description has special characters or formatting?
   - **A:** Database should store plain text; sanitize on load if needed

2. **Q:** Should we show ability names in detail view?
   - **A:** Not in this epic - structure exists, defer to future enhancement

3. **Q:** Do we need scrolling for descriptions longer than 4 lines?
   - **A:** No - truncate with ellipsis (keeps UX simple, most fit in 4 lines)

4. **Q:** Should adjacent navigation pre-load sprites?
   - **A:** Test performance first; add only if navigation lags > 300ms

**Next Steps / Blockers:**
- ✅ **Ready:** All code dependencies exist per architecture
- ✅ **Ready:** Database schema supports all queries
- ✅ **Ready:** Sprites available for all 386 Pokemon
- ⚠️ **Action Required:** Test with longest description text to validate 4-line truncation
- 📝 **Deferred:** Audio integration moved to post-MVP epic (asset sourcing needed)

## Test Strategy Summary

**Test Levels:**

**1. Unit Tests**
- `test_detail_screen.py`:
  - `test_load_pokemon_data()` - Verify all data fetched correctly
  - `test_stat_bar_color_coding()` - Each range returns correct color
  - `test_stat_bar_width_calculation()` - Proportional width for various values
  - `test_adjacent_navigation_wrapping()` - #1 → #386, #386 → #1
  - `test_description_wrapping_short()` - Text under 4 lines renders fully
  - `test_description_wrapping_long()` - Text over 4 lines truncates with ellipsis
  - `test_description_word_boundaries()` - Wrapping breaks at words, not mid-word

- `test_database.py`:
  - `test_get_pokemon_stats()` - Returns 6 stats in correct order
  - `test_get_pokemon_physical_data()` - Returns height, weight, description
  - `test_get_pokemon_types()` - Single and dual type cases

**2. Integration Tests**
- `test_detail_screen_integration()`:
  - Navigate from HomeScreen → DetailScreen → verify data loaded
  - Test L/R navigation within DetailScreen with different Pokemon
  - Verify state saved on exit (last viewed Pokemon)
  - Test with Pokemon having long descriptions (truncation)
  - Test with dual-type Pokemon (two badges displayed)

**3. Performance Tests**
- `test_detail_screen_performance()`:
  - Measure FPS during rendering (target: 30+)
  - Measure DetailScreen render time (target: <33ms per frame)
  - Navigate adjacent 50 times, measure average time (target: <300ms each)
  - Measure description rendering time (target: <5ms)
- `test_sprite_cache_memory()`:
  - Load 50 Pokemon, measure sprite cache memory usage
  - Verify memory stays within reasonable bounds

**4. Manual/Visual Tests**
- Stat bars render correctly with proper colors and widths
- Type badges match UX spec styling
- Holographic blue color scheme applied throughout
- Description text wraps at 4 lines with proper truncation
- All text readable with ice blue color on dark background
- No UI elements cut off at screen edges
- Test on actual Raspberry Pi hardware with target display resolution

**Edge Cases:**
- Pokemon with max stat (255) - bar fills completely
- Pokemon with min stat (1) - small but visible bar
- Pokemon with all low stats - all gray bars
- Pokemon with mixed stat ranges - correct colors per stat
- Very long description (200+ chars) - truncates at 4 lines with ellipsis
- Empty/missing description - show placeholder text
- Single-word description - renders on single line
- Description with exactly 4 lines - no truncation, no ellipsis
- Database missing stats - show placeholder, log error
- Rapid L/R navigation - sprite cache effectiveness, no lag

**Coverage Goals:**
- Unit test coverage: 90%+ for DetailScreen rendering and data loading
- Integration test coverage: All AC scenarios
- Performance test: All NFR-P metrics on Pi hardware
- Visual test: Manual verification on target display

**Test Data:**
- Test Pokemon: Pikachu (#25) - known stats, medium description length
- Edge cases: Shedinja (#292) - HP=1, Blissey (#242) - HP=255
- Long description: Legendary Pokemon (Mewtwo #150) for truncation test
- Short description: Early Pokemon (Caterpie #10) for single-line test

**Acceptance Test Mapping:**
- AC #1-2 → Unit tests for stat rendering + color logic
- AC #3 → Integration test with database types
- AC #4 → Unit tests for physical data display
- AC #5 → Unit tests for description wrapping and truncation
- AC #6 → Integration test for L/R navigation
- AC #7 → Performance tests on Pi hardware
- AC #8 → Manual visual verification against UX spec
