# Epic Technical Specification: Generation Navigation Screen

Date: 2025-11-15
Author: King
Epic ID: 1
Status: Draft

---

## Overview

Epic 1 implements generation-based navigation for ShokeDex, enabling users to efficiently browse through all 386 Pokémon (Gen 1-3) organized by their original game regions: Kanto (#1-151), Johto (#152-251), and Hoenn (#252-386). This epic transforms the current HomeScreen from showing all Pokémon in one list to a generation-filtered view with L/R button navigation to switch regions.

The core user experience is: user powers on device → sees a Pokémon from their last viewed generation → can press L/R to switch between Kanto/Johto/Hoenn → uses Up/Down to scroll within the current generation → press A to view details. This implements the anime Pokédex experience where regional Pokédexes were distinct, and aligns with the "3-press navigation rule" (any Pokémon reachable in ≤3 button presses).

This epic integrates StateManager to persist the last viewed generation across power cycles, displays a generation badge (Kanto/Johto/Hoenn logo with position counter), and ensures 30+ FPS performance during generation switching and scrolling on Raspberry Pi 3B+ hardware.

## Objectives and Scope

**In Scope:**
- Generation filtering on HomeScreen (show only Kanto OR Johto OR Hoenn at once)
- L/R button handlers for generation switching with circular wrapping (3 → 1 → 2 → 3)
- Generation badge UI component displaying current region with logo + position counter (#025/151)
- StateManager integration to save/restore last viewed generation
- Database queries using BETWEEN ranges for generation filtering
- Smooth sprite transitions when changing generations (200-300ms fade)
- Hold-to-scroll acceleration within current generation
- Visual feedback for active generation (badge glow effect)
- Performance optimization to maintain 30+ FPS during navigation

**Out of Scope:**
- "All Generations" view (showing all 386 at once) - design decision to maintain regional organization
- Search/filter by type, name, or stat - covered in separate Search epic
- Generation 4+ support (only Gen 1-3 per PRD scope)
- Touch screen gesture navigation - hardware uses buttons only
- Custom generation groupings (user-defined collections) - future feature

**Success Criteria:**
- User can switch between Kanto/Johto/Hoenn with single L/R button press
- Generation badge clearly indicates current region (visual + text)
- Last viewed generation persists across power cycles (device remembers state)
- Any Pokémon reachable within 3 button presses from any screen
- Frame rate stays above 30 FPS during generation switching
- No visible lag or stuttering during transitions

## System Architecture Alignment

This epic aligns directly with the architecture's **Generation Navigation Architecture** section and **Screen Lifecycle & Navigation** patterns.

**Architecture Components Involved:**
- `src/ui/home_screen.py` - Primary modification point, adding generation filtering logic
- `src/state_manager.py` - Stores/retrieves last viewed generation
- `src/data/database.py` - Generation-filtered queries using BETWEEN ranges
- `src/ui/screen_manager.py` - Screen stack navigation (no changes needed, already supports)
- `src/input_manager.py` - L/R button handling (already implemented, extend with generation logic)

**Architectural Patterns Applied:**
1. **Generation Boundaries:** Uses hardcoded ID ranges per architecture decision
   - Kanto: 1-151, Johto: 152-251, Hoenn: 252-386
2. **Database Query Pattern:** Parameterized queries with BETWEEN operator
3. **StateManager Integration:** Follows manager access pattern via screen_manager
4. **Screen Lifecycle:** Uses on_enter() to load generation, on_exit() to save state
5. **Input Abstraction:** InputAction enum handles L/R regardless of keyboard/GPIO mode

**Constraints:**
- Must maintain 30+ FPS on Raspberry Pi 3B+ (per NFR-P1)
- Button press latency must be < 100ms (per NFR-P2)
- Database queries must use parameterized statements (security pattern)
- No new manager instances (use injected singletons via ScreenManager)

**Integration Points:**
- HomeScreen.on_enter() → StateManager.get_last_viewed_generation()
- HomeScreen._switch_generation() → StateManager.set_last_viewed(generation=X)
- HomeScreen.on_exit() → StateManager.save_state()
- HomeScreen._load_pokemon_list() → Database.get_pokemon_by_generation(gen)

## Detailed Design

### Services and Modules

| Module | Responsibility | Inputs | Outputs | Owner |
|--------|---------------|--------|---------|-------|
| **HomeScreen** | Primary UI for browsing, handles generation switching and Pokemon list display | InputAction (L/R/UP/DOWN), current_generation, pokemon_list | Rendered screen surface, state updates | UI Team |
| **StateManager** | Persists user session data including last viewed generation | get_last_viewed_generation(), set_last_viewed(pokemon_id, generation) | Generation number (1-3), Pokemon ID | Core Team |
| **Database** | Provides generation-filtered Pokemon queries | generation number (1-3) | List of Pokemon records with id, name, sprite_path | Data Team |
| **InputManager** | Abstracts button/keyboard input to actions | Physical button press or keyboard event | InputAction enum (LEFT, RIGHT, UP, DOWN, SELECT, BACK) | Input Team |
| **SpriteLoader** | Loads and caches Pokemon sprites | pokemon_id, size variant (thumb/detail) | pygame.Surface with sprite image | UI Team |

**Key Interfaces:**

```python
# HomeScreen new/modified methods
class HomeScreen(Screen):
    def __init__(self, screen_manager):
        self.current_generation: int = 1  # 1, 2, or 3
        self.generation_badge: GenerationBadge = None
        self.pokemon_list: List[Dict] = []
        
    def _switch_generation(self, direction: int) -> None:
        """Switch to next/previous generation with wrapping.
        Args:
            direction: 1 for next (R button), -1 for previous (L button)
        """
        
    def _load_pokemon_by_generation(self, generation: int) -> List[Dict]:
        """Load Pokemon for specified generation from database.
        Args:
            generation: 1 (Kanto), 2 (Johto), or 3 (Hoenn)
        Returns:
            List of dicts with keys: id, name, sprite_path
        """
        
    def _render_generation_badge(self, surface: pygame.Surface) -> None:
        """Draw generation badge with logo and position counter.
        Args:
            surface: pygame Surface to draw on
        """

# Database new method
class Database:
    def get_pokemon_by_generation(self, generation: int) -> List[Tuple]:
        """Query Pokemon within generation ID range.
        Args:
            generation: 1, 2, or 3
        Returns:
            List of tuples: (id, name, sprite_path)
        """
        # Uses GENERATION_RANGES constant: {1: (1,151), 2: (152,251), 3: (252,386)}
```

### Data Models and Contracts

**Generation Range Constants:**
```python
GENERATION_RANGES = {
    1: (1, 151),    # Kanto: Bulbasaur to Mew
    2: (152, 251),  # Johto: Chikorita to Celebi
    3: (252, 386)   # Hoenn: Treecko to Deoxys
}

GENERATION_NAMES = {
    1: "Kanto",
    2: "Johto",
    3: "Hoenn"
}
```

**Pokemon List Item Schema:**
```python
# Returned by get_pokemon_by_generation()
{
    'id': int,              # National Dex number (1-386)
    'name': str,            # Pokemon name (e.g., "Pikachu")
    'sprite_path': str      # Relative path to sprite image
}
```

**State Manager Schema (JSON):**
```json
{
  "version": "1.0.0",
  "last_viewed": {
    "pokemon_id": 25,
    "generation": 1
  }
}
```

**Generation Badge Data:**
```python
# Internal data structure for rendering badge
{
    'generation': int,      # 1, 2, or 3
    'name': str,           # "Kanto", "Johto", "Hoenn"
    'position': int,       # Current Pokemon position in generation
    'total': int,          # Total Pokemon in generation (151, 100, 135)
    'logo_path': str       # Path to generation logo asset
}
```

**Database Query Contract:**
```sql
-- Generation filtering query (parameterized)
SELECT id, name, sprite_path 
FROM pokemon 
WHERE id BETWEEN ? AND ? 
ORDER BY id;
-- Parameters: (gen_start, gen_end) from GENERATION_RANGES
```

### APIs and Interfaces

**HomeScreen Public Interface:**
```python
class HomeScreen(Screen):
    def handle_input(self, action: InputAction) -> None:
        """Handle button press actions.
        
        Args:
            action: InputAction.LEFT (L button) - previous generation
                   InputAction.RIGHT (R button) - next generation  
                   InputAction.UP - previous Pokemon
                   InputAction.DOWN - next Pokemon
                   InputAction.SELECT (A button) - view details
        """
```

**StateManager Interface (Relevant Methods):**
```python
class StateManager:
    def get_last_viewed_generation(self) -> int:
        """Retrieve last viewed generation from saved state.
        
        Returns:
            Generation number (1, 2, or 3). Defaults to 1 if not set.
        """
    
    def set_last_viewed(self, pokemon_id: int, generation: int) -> None:
        """Update last viewed Pokemon and generation.
        
        Args:
            pokemon_id: National Dex number of viewed Pokemon
            generation: Generation number (1, 2, or 3)
        """
    
    def save_state(self) -> None:
        """Persist current state to disk (JSON file)."""
```

**Database Interface (New Method):**
```python
class Database:
    def get_pokemon_by_generation(self, generation: int) -> List[Tuple[int, str, str]]:
        """Fetch all Pokemon within generation boundaries.
        
        Args:
            generation: 1 (Kanto), 2 (Johto), or 3 (Hoenn)
            
        Returns:
            List of tuples: (id, name, sprite_path)
            Ordered by National Dex number ascending
            
        Raises:
            ValueError: If generation not in range 1-3
        """
```

**InputAction Enum (from InputManager):**
```python
from enum import Enum

class InputAction(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"      # L button - previous generation
    RIGHT = "right"    # R button - next generation
    SELECT = "select"  # A button
    BACK = "back"      # B button
    START = "start"    # START button
```

### Workflows and Sequencing

**Startup Flow (Loading Last Viewed Generation):**
```
1. main.py initializes StateManager
2. ScreenManager creates HomeScreen, passes state_manager reference
3. HomeScreen.on_enter() called
   ├─> Call state_manager.get_last_viewed_generation()
   ├─> Set self.current_generation to returned value (or default to 1)
   ├─> Call self._load_pokemon_by_generation(self.current_generation)
   └─> Render generation badge and Pokemon list
```

**Generation Switch Flow (User Presses L or R):**
```
1. InputManager detects button press → emits InputAction.LEFT or InputAction.RIGHT
2. HomeScreen.handle_input(action) receives action
3. HomeScreen._switch_generation(direction) called
   ├─> Calculate new generation: ((current + direction - 1) % 3) + 1
   ├─> Update self.current_generation
   ├─> Trigger fade-out transition (current Pokemon sprite)
   ├─> Call self._load_pokemon_by_generation(new_generation)
   ├─> Reset scroll position to first Pokemon in generation
   ├─> Call state_manager.set_last_viewed(first_pokemon_id, new_generation)
   ├─> Trigger fade-in transition (new Pokemon sprite)
   └─> Update generation badge display
4. Render updated screen at 30+ FPS
```

**Pokemon Scroll Flow (Within Generation):**
```
1. User presses UP or DOWN
2. HomeScreen.handle_input() receives InputAction.UP or DOWN
3. Move selection index by ±1 within pokemon_list bounds
4. Check if holding button → enable fast scroll (skip render frames)
5. Load sprite for new Pokemon (lazy load with caching)
6. Update displayed Pokemon name, type, Dex number
7. Update position counter in generation badge (#25/151)
```

**State Persistence Flow (On Navigation Away):**
```
1. User presses A button → navigate to DetailScreen
2. HomeScreen.on_exit() called by ScreenManager
   ├─> Call state_manager.set_last_viewed(current_pokemon_id, current_generation)
   └─> Call state_manager.save_state()
3. State written to data/shokedex_state.json
4. Next startup will restore to this exact position
```

**Database Query Sequence:**
```
1. HomeScreen calls db.get_pokemon_by_generation(generation)
2. Database looks up GENERATION_RANGES[generation] → (start_id, end_id)
3. Execute SQL: SELECT id, name FROM pokemon WHERE id BETWEEN ? AND ? ORDER BY id
4. Parameters: (start_id, end_id) - prevents SQL injection
5. Fetch all results (151 for Kanto, 100 for Johto, 135 for Hoenn)
6. Return list of tuples to HomeScreen
7. HomeScreen populates pokemon_list for rendering
```

## Non-Functional Requirements

### Performance

**Target Metrics (Raspberry Pi 3B+):**
- Frame rate: Maintain 30+ FPS during generation switching and scrolling
- Button latency: < 100ms from button press to visual feedback
- Generation switch time: < 300ms total (fade-out + query + fade-in)
- Sprite load time: < 50ms (with caching, first load may be longer)
- State save time: < 20ms (non-blocking, background acceptable)

**Performance Strategies:**
- **Sprite caching:** Keep last 20 viewed Pokemon sprites in memory (LRU cache)
- **Database query optimization:** Single query per generation switch (not per Pokemon)
- **Lazy rendering:** Only render visible Pokemon (no off-screen pre-rendering)
- **Hardware acceleration:** Use pygame convert_alpha() for sprites (GPU blitting)
- **Transition optimization:** 200-300ms fade avoids perception of lag while maintaining smooth feel

**Bottleneck Mitigation:**
- If generation switch > 300ms: Pre-load first sprite of adjacent generations
- If scrolling drops below 30 FPS: Reduce sprite resolution or simplify badge rendering
- If memory exceeds 200MB: Reduce sprite cache from 20 to 10 items

**Performance Testing:**
- Profile with `tools/profile_performance.py` during rapid generation switching
- Monitor frame rate with pygame.time.Clock() during 10-second scroll test
- Measure input latency with `tools/test_input_latency.py`

### Security

**SQL Injection Prevention:**
- ✅ **MANDATORY:** All database queries use parameterized statements
- ✅ Generation numbers validated as integers in range 1-3 before database call
- ❌ **NEVER:** String formatting or concatenation in SQL queries

**Example Safe Query:**
```python
# ✅ CORRECT - Parameterized query
cursor.execute(
    "SELECT id, name FROM pokemon WHERE id BETWEEN ? AND ? ORDER BY id",
    (start_id, end_id)
)

# ❌ WRONG - String formatting (SQL injection risk)
cursor.execute(
    f"SELECT id, name FROM pokemon WHERE id BETWEEN {start_id} AND {end_id}"
)
```

**Input Validation:**
- Generation numbers validated: `if generation not in [1, 2, 3]: raise ValueError`
- Pokemon IDs range-checked before database queries
- File paths sanitized when loading sprites (no user-provided paths)

**State File Integrity:**
- State file is JSON (no code execution risk)
- Corruption handling: Try/catch on load, fallback to defaults
- Invalid generation values reset to 1 (safe default)

**No External Inputs:**
- This epic has no user text input (buttons only)
- No network requests during runtime (offline-first)
- Asset paths are hardcoded relative paths (no directory traversal)

### Reliability/Availability

**Error Handling:**
- **Missing sprites:** Display text placeholder with Pokemon name, log warning, continue
- **Database query failure:** Show error message, fallback to generation 1, retry available
- **State file corruption:** Reset to defaults (generation 1, Pokemon #1), log error
- **Invalid generation value:** Clamp to range 1-3, log validation error

**Graceful Degradation:**
- If generation badge assets missing → show text-only badge
- If sprite cache full → evict least recently used, continue operation
- If StateManager save fails → log error but don't block navigation

**Recovery Strategies:**
- State corruption: Auto-reset to safe defaults without user intervention
- Database locked: Retry query up to 3 times with 50ms delay
- Memory pressure: Clear sprite cache, reload current view only

**Availability Targets:**
- Application uptime: 100% (no crashes from this epic's code)
- Feature degradation acceptable: Can browse without generation badges
- State persistence non-critical: Device works even if state save fails

**Defensive Programming:**
- Null checks before rendering sprites
- Try/except around all database operations
- Validate generation bounds before array access
- Log all errors with context for debugging

### Observability

**Logging Requirements:**
```python
import logging

# Key events to log:
logging.info(f"Generation switched: {old_gen} → {new_gen}")
logging.info(f"Loaded {len(pokemon_list)} Pokemon for generation {gen}")
logging.warning(f"Sprite not found for Pokemon #{pokemon_id}")
logging.error(f"Database query failed: {error}")
logging.debug(f"State saved: gen={gen}, pokemon_id={pokemon_id}")
```

**Performance Metrics (Optional Enhancement):**
- Track generation switch frequency (how often users switch)
- Track most viewed generation (Kanto vs Johto vs Hoenn popularity)
- Track average time spent per generation
- Frame rate drops (when FPS < 30)

**Debug Signals:**
- Button press events: `DEBUG: InputAction.RIGHT received at 12:34:56.789`
- State changes: `DEBUG: current_generation changed from 1 to 2`
- Database queries: `DEBUG: Querying generation 2 (ids 152-251)`
- Cache hits/misses: `DEBUG: Sprite cache hit for Pokemon #25`

**Error Context:**
All errors logged with:
- Current generation number
- Current Pokemon ID
- Timestamp
- Stack trace (for unexpected errors)

**Performance Monitoring:**
- Frame rate logged every 100 frames when < 30 FPS
- Generation switch duration logged if > 300ms
- Memory usage logged when > 80% of cache capacity

## Dependencies and Integrations

**Python Dependencies (from requirements.txt):**
- `pygame >= 2.5.0` - Graphics rendering, event loop, Surface management
- `Pillow >= 10.0.0` - Image loading (sprite assets)
- SQLite3 (stdlib) - Database queries for Pokemon data

**Internal Module Dependencies:**
- `src/ui/screen.py` - Base Screen class (inheritance)
- `src/ui/screen_manager.py` - Navigation and manager injection
- `src/state_manager.py` - Session persistence
- `src/data/database.py` - Pokemon queries
- `src/input_manager.py` - Button input abstraction
- `src/ui/sprite_loader.py` - Sprite loading utilities
- `src/ui/colors.py` - Holographic blue color palette

**Asset Dependencies:**
- Generation badge images (3 files needed):
  - `assets/icons/badge_kanto.png` (100×40px)
  - `assets/icons/badge_johto.png` (100×40px)
  - `assets/icons/badge_hoenn.png` (100×40px)
- Pokemon sprites (existing):
  - `assets/sprites/thumb/001.png` through `386.png`
- Font files (from UX spec):
  - Orbitron (headers, names)
  - Rajdhani (body text)
  - Share Tech Mono (numbers)

**Database Schema Dependencies:**
- `pokemon` table must have columns: id, name
- Pokemon IDs must be continuous 1-386
- No schema changes required for this epic

**Configuration Dependencies:**
- `GENERATION_RANGES` constant defined in HomeScreen or shared config
- StateManager initialized in main.py before HomeScreen creation
- InputManager configured with L/R button mappings

**Integration Points:**
- **StateManager:** Must be initialized before HomeScreen instantiation
- **Database:** Context manager pattern used for all queries
- **ScreenManager:** Provides manager references to HomeScreen via constructor
- **InputManager:** Maps physical/keyboard buttons to InputAction enum

**External Integrations:**
- None (offline-first, no API calls)

**Version Constraints:**
- Python 3.11+ required (for type hints and modern features)
- Raspberry Pi OS Bookworm (Debian 12) for GPIO support

## Acceptance Criteria (Authoritative)

**AC #1: Generation Badge Display**
- Generation badge visible in top-left or top-center of HomeScreen
- Badge shows current region name ("KANTO", "JOHTO", "HOENN")
- Badge shows position counter format: #025/151 (current/total for generation)
- Badge uses holographic blue styling per UX spec:
  - Background: rgba(26, 47, 74, 0.9)
  - Border: 2px solid electric blue (#00d4ff)
  - Corner accent lines (45° cuts)
- Region logo displayed (Pokéball, GS Ball, Master Ball)

**AC #2: L/R Button Generation Switching**
- L button (LEFT action) switches to previous generation with circular wrapping:
  - Kanto (1) → Hoenn (3) → Johto (2) → Kanto (1)
- R button (RIGHT action) switches to next generation with circular wrapping:
  - Kanto (1) → Johto (2) → Hoenn (3) → Kanto (1)
- Generation switch completes in < 300ms
- Visual transition: fade-out current Pokemon (100ms) → load new list → fade-in first Pokemon (100ms)
- Active generation badge glows with bright cyan (#4df7ff)

**AC #3: Generation Filtering**
- Only Pokemon from current generation displayed in browse list
- Kanto: Shows Pokemon #1-151 (Bulbasaur through Mew)
- Johto: Shows Pokemon #152-251 (Chikorita through Celebi)
- Hoenn: Shows Pokemon #252-386 (Treecko through Deoxys)
- Scroll position resets to first Pokemon when switching generations
- Database query uses parameterized BETWEEN statement (security requirement)

**AC #4: State Persistence**
- Last viewed generation saved to state file on screen exit
- On device startup, HomeScreen loads last viewed generation from StateManager
- If no saved state exists, default to Generation 1 (Kanto)
- State file format: JSON with keys "generation" (1-3) and "pokemon_id"
- State corruption handled gracefully (reset to Gen 1 without crash)

**AC #5: Performance Requirements**
- Frame rate maintains 30+ FPS during generation switching
- Frame rate maintains 30+ FPS during Pokemon scrolling within generation
- Button press latency < 100ms (visual feedback appears immediately)
- Generation switch total time < 300ms (meets responsiveness target)
- Memory usage stable (no leaks during repeated switching)

**AC #6: Navigation Efficiency (3-Press Rule)**
- From Kanto, user can reach any Hoenn Pokemon in ≤3 presses:
  - Example: Kanto → R (1) → R (2) → Scroll to Pokemon (3) ✅
- From any generation, user can reach any Pokemon in current gen in ≤2 presses:
  - Example: View Pokemon #25 → UP/DOWN (1) → View Pokemon #26 (2) ✅

**AC #7: Visual Feedback (UX Requirements)**
- Generation badge glows when active (bright cyan glow effect)
- Sprite transitions use fade effect (no instant pop)
- Button press shows immediate visual response (< 100ms)
- Position counter updates in real-time during scrolling
- Holographic blue color scheme applied (electric blue #00d4ff primary)

**AC #8: Error Handling**
- Missing generation badge assets → show text-only badge, log warning
- Invalid generation value from state → reset to 1, log error
- Database query failure → show error message, allow retry
- No crashes from null sprites, missing data, or corrupted state

## Traceability Mapping

| AC | Spec Section(s) | Component(s)/API(s) | Test Idea |
|----|-----------------|---------------------|--------|
| **AC #1** | Overview, Detailed Design → Generation Badge | `HomeScreen._render_generation_badge()`, badge assets | Unit test: Render badge for each generation, verify text and colors |
| **AC #2** | Objectives, APIs → L/R Button Handling | `HomeScreen.handle_input(LEFT/RIGHT)`, `_switch_generation()` | Integration test: Press L/R, verify generation cycles correctly |
| **AC #3** | System Alignment → Database Query Pattern | `Database.get_pokemon_by_generation()`, GENERATION_RANGES | Unit test: Query each generation, verify correct ID ranges returned |
| **AC #4** | System Alignment → StateManager Integration | `StateManager.get/set_last_viewed_generation()`, `save_state()` | Integration test: Switch gen, restart app, verify restored to last gen |
| **AC #5** | NFR Performance | All components | Performance test: Profile with tools/profile_performance.py, measure FPS |
| **AC #6** | Objectives → 3-Press Rule | Navigation workflows | Manual test: Navigate from any screen to any Pokemon, count presses |
| **AC #7** | UX Design Spec → Visual Feedback | Rendering methods, UX colors | Visual test: Verify badge glow, transition smoothness, color accuracy |
| **AC #8** | NFR Reliability → Error Handling | Try/except blocks, fallback logic | Unit test: Mock failures, verify graceful degradation |

## Risks, Assumptions, Open Questions

**Risks:**
1. **Performance on Pi 3B+** (Medium Impact, Low Probability)
   - Risk: Generation switch might drop below 30 FPS on actual hardware
   - Mitigation: Profile on real Pi early, optimize sprite loading if needed
   - Fallback: Reduce transition animation duration or use simpler effects

2. **Generation Badge Asset Availability** (Low Impact, Medium Probability)
   - Risk: Don't have Kanto/Johto/Hoenn logo assets ready
   - Mitigation: Can use text-only badges initially, add logos later
   - Action: Create/source badge assets before implementation starts

3. **State File Corruption** (Low Impact, Low Probability)
   - Risk: JSON corruption causes startup crash
   - Mitigation: Try/except with fallback to defaults (AC #8)
   - Already handled in architecture patterns

**Assumptions:**
1. ✅ Database already populated with all 386 Pokemon (per architecture docs)
2. ✅ StateManager class already implemented and tested (per architecture status)
3. ✅ InputManager already handles L/R button mapping (per architecture status)
4. ✅ Sprite files exist for all Pokemon #1-386 (per asset inventory)
5. ✅ pygame and dependencies installed on target Raspberry Pi
6. ⚠️ Generation badge assets will be created/sourced separately

**Open Questions:**
1. **Q:** Should generation wrap around (3 → 1) or stop at edges?
   - **A:** Wrap around (circular navigation) per PRD 3-press rule efficiency

2. **Q:** What happens if user is viewing Pokemon #151 in Kanto and switches to Johto?
   - **A:** Reset to first Pokemon of new generation (#152) per design

3. **Q:** Should we pre-load adjacent generation data for faster switching?
   - **A:** Not in MVP - optimize only if performance testing shows need

4. **Q:** Text-only badge acceptable for MVP if logo assets delayed?
   - **A:** Yes - badge functionality > visual polish for Epic 1

**Next Steps / Blockers:**
- ⚠️ **Need:** Generation badge assets (3 PNG files) - assign to design/asset team
- ⚠️ **Need:** Confirm font files (Orbitron, Rajdhani) available in assets/fonts/
- ✅ **Ready:** All code dependencies exist per architecture status

## Test Strategy Summary

**Test Levels:**

**1. Unit Tests** (pytest framework)
- `test_home_screen.py`:
  - `test_switch_generation_forward()` - R button cycles 1→2→3→1
  - `test_switch_generation_backward()` - L button cycles 1→3→2→1
  - `test_load_pokemon_by_generation()` - Verify correct ID ranges loaded
  - `test_generation_badge_rendering()` - Mock Surface, verify draw calls
  - `test_invalid_generation_handling()` - Generation 0 or 4 raises ValueError

- `test_database.py`:
  - `test_get_pokemon_by_generation_kanto()` - Returns 151 Pokemon
  - `test_get_pokemon_by_generation_johto()` - Returns 100 Pokemon
  - `test_get_pokemon_by_generation_hoenn()` - Returns 135 Pokemon
  - `test_parameterized_query_safety()` - Verify no SQL injection possible

- `test_state_manager.py`:
  - `test_save_and_load_generation()` - Roundtrip generation persistence
  - `test_corrupted_state_fallback()` - Invalid JSON returns default gen 1

**2. Integration Tests**
- `test_generation_navigation_flow()`:
  - Start app → verify Gen 1 loaded → press R → verify Gen 2 → press L → verify Gen 1
- `test_state_persistence_across_sessions()`:
  - Switch to Gen 3 → exit → restart → verify Gen 3 restored
- `test_pokemon_scroll_within_generation()`:
  - Load Gen 1 → scroll 10 Pokemon → verify IDs 1-11 displayed

**3. Performance Tests** (using tools/profile_performance.py)
- `test_generation_switch_performance()`:
  - Measure time: Press R → screen fully rendered
  - Assert: Total time < 300ms
- `test_frame_rate_during_switching()`:
  - Rapidly press L/R for 10 seconds
  - Assert: Average FPS ≥ 30, no frame drops
- `test_memory_stability()`:
  - Switch generations 100 times
  - Assert: Memory usage increase < 10MB (no major leaks)

**4. Manual/Visual Tests**
- Generation badge appearance matches UX spec (holographic blue, glow)
- Smooth fade transitions during generation switch
- Position counter updates correctly (#XXX/YYY)
- Badge glow effect visible on active generation
- All three generation logos display correctly
- Test on actual Raspberry Pi hardware (not just desktop)

**Edge Cases to Test:**
- Generation wrapping: Gen 3 + R = Gen 1, Gen 1 + L = Gen 3
- Rapid button mashing: No crashes or race conditions
- State file missing: App starts with Gen 1 default
- State file invalid JSON: App resets to Gen 1, logs error
- Database connection failure: Error message, allow retry
- Missing sprites: Text placeholder shown, no crash

**Coverage Goals:**
- Unit test coverage: 90%+ for generation logic
- Integration test coverage: All AC scenarios covered
- Performance test: All NFR-P metrics validated on Pi hardware

**Test Data:**
- Use test database with subset of Pokemon (10 per generation)
- Mock StateManager for unit tests
- Real database for integration tests
- Actual Raspberry Pi for performance tests

**Acceptance Test Mapping:**
- AC #1 → Manual visual test + unit test for badge rendering
- AC #2 → Integration test for L/R cycling + unit test for direction logic
- AC #3 → Unit tests for database queries per generation
- AC #4 → Integration test for state persistence roundtrip
- AC #5 → Performance tests with profiling tools
- AC #6 → Manual navigation efficiency test
- AC #7 → Visual tests on actual hardware
- AC #8 → Unit tests for error scenarios with mocks

**Test Environment:**
- Development: Desktop (macOS/Linux/Windows) with keyboard mode
- Integration: Raspberry Pi OS in virtual environment
- Performance: Actual Raspberry Pi 3B+ with LCD display
- CI/CD: Automated unit/integration tests on GitHub Actions
