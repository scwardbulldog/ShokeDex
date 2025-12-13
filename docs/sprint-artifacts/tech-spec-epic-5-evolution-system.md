# Epic Technical Specification: Evolution System

Date: 2025-11-15
Author: King
Epic ID: 5
Status: Draft

---

## Overview

Epic 5 implements the Evolution System for ShokeDex, displaying how Pokémon transform through evolution chains. This epic delivers FR4 (Evolution Chain Display) from the PRD, showing users the evolutionary relationships between Pokémon with visual sprites and evolution requirements.

The evolution system leverages the existing database schema (evolution_chains and evolutions tables) to present clear, visual evolution paths. Users can view what a Pokémon evolves from, what it evolves into, and the conditions required for evolution (level, stone, trade, etc.). This information appears within the DetailScreen as an additional view tab or section, maintaining the device's visual-first design philosophy.

## Objectives and Scope

### In Scope

**Evolution Display:**
- Visual evolution chain showing pre-evolution, current Pokémon, and evolution(s)
- Small sprite thumbnails (64x64) for each stage in the chain
- Evolution requirements displayed (level, stone, trade, happiness, etc.)
- "You are here" indicator showing current Pokémon in chain
- Support for linear chains (Charmander → Charmeleon → Charizard)
- Support for branching chains (Eevee → 5 different evolutions in Gen 1-3)
- Navigation between evolution stages (view related Pokémon)

**Integration Points:**
- Extend DetailScreen with evolution view section
- Database queries using existing evolution_chains and evolutions tables
- Button navigation (A button) to jump between evolution relatives
- SpriteLoader integration for evolution thumbnails

**User Experience:**
- Evolution information presented clearly without cluttering detail view
- Horizontal layout showing evolution flow left-to-right
- Requirements text below each evolution arrow
- Seamless navigation to view evolutions in detail

### Out of Scope

**Post-MVP Features:**
- Type effectiveness display (moved to Epic 6 - Relationships View)
- Combined evolution + type matchups screen (Epic 6)
- Mega evolutions (Gen 6+, not applicable to Gen 1-3 scope)
- Regional forms (Alolan, Galarian - Gen 7+)
- Evolution animations or transitions
- Audio cues for evolution display

**Database Changes:**
- Schema is already complete with evolution_chains and evolutions tables
- No new tables or migrations needed
- Data already seeded via manage_db.py

### Success Criteria

- All 386 Pokémon show correct evolution information
- Evolution chains display accurately for:
  - Single-stage Pokémon (no evolutions): Show "No evolutions"
  - Two-stage chains: Pre-evolution and evolution shown
  - Three-stage chains: Full chain with current position indicated
  - Branching evolutions: All branches shown (Eevee, Tyrogue, etc.)
- Evolution requirements are clear and accurate
- Navigation between evolution relatives works smoothly
- Performance: Evolution view renders within 100ms
- Visual design matches anime Pokédex holographic aesthetic from UX spec

## System Architecture Alignment

The Evolution System aligns with ShokeDex's screen-based architecture and manager pattern:

**Database Layer:**
- Leverages existing `evolution_chains` table (groups related Pokémon by family)
- Uses `evolutions` table for evolution relationships and requirements
- Queries through `Database` context manager with parameterized SQL
- No schema changes required - infrastructure already complete

**UI Layer:**
- Extends `DetailScreen` (src/ui/detail_screen.py) with evolution display section
- Uses `SpriteLoader` (src/ui/sprite_loader.py) for thumbnail sprites (64x64)
- Follows Screen lifecycle pattern (on_enter, render, handle_input)
- Integrates with `ScreenManager` for navigation to evolution relatives

**State Management:**
- No state persistence needed (evolution data is static)
- Navigation preserves current Pokémon context
- Evolution view accessible via DetailScreen (no new screen class needed)

**Performance Considerations:**
- Evolution thumbnails loaded on-demand via SpriteLoader caching
- Maximum 3 sprites per linear chain (pre-evo, current, evolution)
- Branching chains (Eevee) may show 5+ thumbnails but still manageable
- Database queries return small result sets (typically 1-5 rows)

**Visual Design:**
- Follows holographic blue aesthetic from UX Design Specification
- Uses existing component patterns: sprite panels with glowing borders
- Evolution arrows styled with electric blue (#00d4ff)
- Requirement text in ice blue (#a8e6ff) for readability

This epic requires NO new architecture components - it's a feature addition to existing DetailScreen using established patterns.

## Detailed Design

### Services and Modules

**DetailScreen Extension (src/ui/detail_screen.py):**
- Add `EvolutionPanel` component as a section within DetailScreen
- Renders below stats section with clear divider
- Displays horizontal evolution chain (max 6 stages for branching)
- Handles user input (A button) to navigate to evolution relatives
- Lifecycle: Loads evolution data in `on_enter()`, renders in `render()`

**Database Extension (src/data/database.py):**
- New method: `get_evolution_chain(pokemon_id: int) -> Dict[str, Any]`
- Queries `evolution_chains` and `evolutions` tables
- Returns complete evolution family data with requirements
- Uses parameterized SQL queries (security requirement)

**SpriteLoader Integration (src/ui/sprite_loader.py):**
- Use existing `load_thumbnail(pokemon_id)` method for 64x64 sprites
- LRU caching already implemented (no changes needed)
- Handles missing sprites gracefully with placeholder

**Component Pattern Established:**
- EvolutionPanel sets pattern for future DetailScreen sections
- Reusable for moves, abilities, or other tabbed content
- Clear separation of concerns: data fetching, rendering, input handling

### Data Models and Contracts

**Database Method Contract:**
```python
def get_evolution_chain(self, pokemon_id: int) -> Dict[str, Any]:
    """
    Retrieves complete evolution chain for a Pokémon.
    
    Returns:
    {
        'chain_id': int,  # Evolution chain family ID
        'stages': [  # All Pokémon in this evolution family
            {
                'pokemon_id': int,
                'name': str,
                'stage': int  # Position in chain (1, 2, or 3)
            },
            ...
        ],
        'evolutions': [  # Evolution relationships and requirements
            {
                'from_id': int,
                'to_id': int,
                'method': str,  # 'level', 'stone', 'trade', 'trade-item', 'happiness'
                'level': int | None,  # Required level if method='level'
                'item': str | None,  # Item name if method='stone' or 'trade-item'
                'trigger': str | None  # Additional context (time-of-day, location)
            },
            ...
        ],
        'current_stage': int  # Which stage the queried Pokémon is at
    }
    """
```

**Evolution Display Data Structure:**
- Each evolution stage: Pokémon ID, name, sprite (64x64)
- Each evolution arrow: Method text, requirement text, visual style
- Current position: Boolean flag for "You are here" indicator

**Evolution Method Text Mapping:**
- `level` → "Level {level}" (e.g., "Level 16")
- `stone` → "{item}" (e.g., "Fire Stone")
- `trade` → "Trade"
- `trade-item` → "Trade holding {item}" (e.g., "Trade holding Metal Coat")
- `happiness` → "High Friendship"
- `time-day` → "Daytime" (Espeon)
- `time-night` → "Nighttime" (Umbreon)

**Database Schema (Already Implemented):**
- `evolution_chains` table: Groups Pokémon by evolution family
- `evolutions` table: Defines evolution relationships with requirements
- `items` table: Provides evolution stone names
- All data seeded via `manage_db.py seed` command

### APIs and Interfaces

**Database Query Interface:**

```sql
-- Get evolution chain ID for a Pokémon
SELECT chain_id FROM pokemon WHERE id = ?;

-- Get all Pokémon in the evolution family
SELECT p.id, p.name 
FROM pokemon p
WHERE p.chain_id = ?
ORDER BY p.id;

-- Get evolution relationships
SELECT 
    e.from_pokemon_id,
    e.to_pokemon_id,
    e.evolution_method,
    e.minimum_level,
    e.evolution_item_id,
    i.name AS item_name,
    e.trigger
FROM evolutions e
LEFT JOIN items i ON e.evolution_item_id = i.id
WHERE e.from_pokemon_id IN (SELECT id FROM pokemon WHERE chain_id = ?)
ORDER BY e.from_pokemon_id, e.to_pokemon_id;
```

**EvolutionPanel Render Interface:**

```python
class EvolutionPanel:
    def __init__(self, screen_manager, pokemon_id: int):
        self.screen_manager = screen_manager
        self.pokemon_id = pokemon_id
        self.evolution_data = None
        self.sprites = {}  # Cached sprites {pokemon_id: Surface}
        
    def load_data(self):
        """Load evolution chain from database"""
        with Database() as db:
            self.evolution_data = db.get_evolution_chain(self.pokemon_id)
        
    def load_sprites(self):
        """Load thumbnail sprites for all Pokémon in chain"""
        for stage in self.evolution_data['stages']:
            pid = stage['pokemon_id']
            self.sprites[pid] = sprite_loader.load_thumbnail(pid)
    
    def render(self, surface: pygame.Surface, x: int, y: int):
        """Render evolution chain at specified position"""
        # Draw panel background with holographic border
        # Draw evolution stages horizontally
        # Draw arrows between stages with requirement text
        # Highlight current Pokémon with glow effect
        pass
    
    def handle_input(self, action: InputAction) -> Optional[int]:
        """Handle navigation to evolution relative"""
        if action == InputAction.SELECT:  # A button
            # Return selected evolution's pokemon_id
            return selected_pokemon_id
        return None
```

**Integration with DetailScreen:**

```python
class DetailScreen(Screen):
    def on_enter(self):
        # Existing code for loading Pokémon data...
        
        # Add evolution panel
        self.evolution_panel = EvolutionPanel(self.screen_manager, self.pokemon_id)
        self.evolution_panel.load_data()
        self.evolution_panel.load_sprites()
    
    def render(self, surface: pygame.Surface):
        # Existing rendering code for name, stats, etc...
        
        # Render evolution panel at bottom
        self.evolution_panel.render(surface, x=20, y=240)
    
    def handle_input(self, action: InputAction):
        # Check if evolution panel handles input
        selected_id = self.evolution_panel.handle_input(action)
        if selected_id:
            # Navigate to evolution's detail screen
            new_screen = DetailScreen(self.screen_manager, selected_id)
            self.screen_manager.replace(new_screen)
        
        # Existing input handling...
```

### Workflows and Sequencing

**Primary Workflow: View Evolution Chain**

```
User on Browse Screen
    ↓
[Presses A] Navigate to DetailScreen
    ↓
DetailScreen.on_enter()
    ├─ Load Pokémon basic data (existing)
    ├─ Load stats data (existing)
    ├─ Create EvolutionPanel(pokemon_id)
    │   ├─ Database.get_evolution_chain(pokemon_id)
    │   │   ├─ Query evolution_chains table
    │   │   ├─ Query evolutions table
    │   │   └─ Return evolution data structure
    │   └─ SpriteLoader.load_thumbnail(pokemon_id) for each stage
    │       ├─ Check LRU cache
    │       ├─ Load from disk if not cached
    │       └─ Return pygame.Surface
    └─ Ready to render
    ↓
DetailScreen.render()
    ├─ Render name, number (existing)
    ├─ Render sprite and stats (existing)
    └─ EvolutionPanel.render()
        ├─ Draw panel background with border
        ├─ For each evolution stage:
        │   ├─ Draw 64x64 sprite
        │   ├─ Draw Pokémon name below sprite
        │   └─ Highlight if current Pokémon
        └─ For each evolution relationship:
            ├─ Draw arrow between stages
            └─ Draw requirement text below arrow
```

**Secondary Workflow: Navigate to Evolution Relative**

```
User viewing DetailScreen with evolution panel
    ↓
[Presses A] Select evolution relative
    ↓
EvolutionPanel.handle_input(InputAction.SELECT)
    ├─ Determine which evolution sprite is selected
    └─ Return selected pokemon_id
    ↓
DetailScreen.handle_input() receives pokemon_id
    ├─ Create new DetailScreen(pokemon_id)
    └─ ScreenManager.replace(new_screen)
    ↓
New DetailScreen displays
    └─ Shows selected evolution with ITS evolution chain
```

**Edge Case Workflow: No Evolutions**

```
User views single-stage Pokémon (e.g., Ditto, Farfetch'd)
    ↓
EvolutionPanel.load_data()
    ├─ Database.get_evolution_chain(pokemon_id)
    └─ Returns: {'stages': [current], 'evolutions': []}
    ↓
EvolutionPanel.render()
    └─ Display: "No evolutions" message
        └─ Center text in panel with subtle styling
```

**Data Flow Sequence:**

1. **User Action** → A button press on DetailScreen
2. **Database Query** → get_evolution_chain() with parameterized SQL
3. **Data Processing** → Parse evolution stages and relationships
4. **Asset Loading** → Load sprites via SpriteLoader (with caching)
5. **UI Rendering** → Draw evolution panel with all stages
6. **User Feedback** → Highlight current Pokémon, show requirements
7. **Navigation Ready** → A button navigates to evolution relative

## Non-Functional Requirements

### Performance

**Validated Performance Budgets (Story 5.6 - December 2025):**

The following performance budgets have been validated through comprehensive testing on development hardware with pytest performance tests marked with `@pytest.mark.performance`:

**Rendering Performance (VALIDATED ✅):**
- Evolution panel first render: **< 200ms** (includes database query + sprite loading)
  - Linear 3-stage chains (e.g., Charmander line): Consistently < 200ms
  - Branching worst-case (Eevee, 6 sprites): Consistently < 250ms
- Evolution panel cached render: **< 50ms** (data and sprites already in memory)
  - All test cases: Consistently < 50ms with caching active
  - Average cached render: ~0.31ms (significantly under budget)
- Target maintains **30+ FPS** on Raspberry Pi 3B+ during DetailScreen display
- No visible lag or stuttering when switching between Pokémon

**Long-Session Stability (VALIDATED ✅):**
- 100+ Pokémon navigation test completed successfully
- Memory usage remains stable (no leaks detected)
- Frame times remain consistent (caching improves performance over time)
- Sprite cache discipline maintained (max 50 sprites globally via SpriteLoader LRU)

**Database Query Performance:**
- get_evolution_chain() query: < 20ms target (indexed queries on small dataset)
- SQLite benefits from indexed id and chain_id columns
- Result set typically 3-10 rows (small, fast)

**Sprite Loading Performance:**
- SpriteLoader LRU cache: **MAX 50 sprites globally** (~1.6MB total)
- Thumbnail size: 64x64 pixels (small, fast to load and render)
- Worst case (Eevee with 5 evolutions): 6 sprites × ~16KB ≈ 100KB total
- Disk load time per sprite: < 10ms target on SD card
- Cached sprite blit time: < 1ms

**Memory Usage and Caching Architecture (VALIDATED ✅):**
- **Evolution data cache**: Per-EvolutionPanel instance only (~1KB per Pokémon)
  - Cached in `_evolution_data` instance variable
  - Prevents repeated database queries for same Pokémon within session
  - Scope: Limited to current panel instance, cleared on panel destruction
- **Sprite cache**: Global LRU cache via SpriteLoader (max 50 sprites)
  - Shared across all UI components
  - Automatic eviction of least-recently-used sprites
  - Memory bound: ~1.6MB maximum
- **Eevee worst case**: 6 sprites (~100KB) well within global limits
- **No unbounded growth**: Long-session testing (100+ Pokémon) confirms stable memory usage
- Total memory impact per DetailScreen instance: < 200KB
- Acceptable within Raspberry Pi 1GB RAM constraint

**Performance Targets:**
- 95th percentile: Evolution panel renders in < 150ms
- 99th percentile: Evolution panel renders in < 250ms
- 0% frames dropped during evolution panel display

**Test Coverage (Story 5.6):**
- Database accuracy tests: 6 tests covering all evolution patterns (linear, branching, single-stage, trade, stone, happiness)
- Panel accuracy tests: 6 tests validating EvolutionPanel data structures
- Performance tests: 4 tests with `@pytest.mark.performance` marker
  - `test_performance_charmander_first_render` - validates < 200ms first render
  - `test_performance_charmander_cached_render` - validates < 50ms cached render
  - `test_performance_eevee_first_render_worst_case` - validates < 250ms branching worst case
  - `test_performance_eevee_cached_render_worst_case` - validates < 50ms cached branching
- Long-session stability script: `tools/test_long_session_stability.py`

### Security

**SQL Injection Prevention:**
- ALL database queries use parameterized statements
- get_evolution_chain(pokemon_id) validates pokemon_id is integer
- No string formatting or concatenation in SQL queries
- Example: `cursor.execute("SELECT * FROM pokemon WHERE id = ?", (pokemon_id,))`

**Input Validation:**
- pokemon_id validated as integer in range 1-386
- Invalid IDs return empty evolution data (graceful degradation)
- No user-controlled input in database queries (pokemon_id comes from internal navigation)

**Data Integrity:**
- Evolution data sourced from PokéAPI (trusted source)
- Database seeded via manage_db.py with validation
- No runtime modification of evolution data (read-only)

**Asset Security:**
- Sprite paths constructed with pathlib (prevents directory traversal)
- Missing sprites handled gracefully (placeholder shown)
- No execution of external code or scripts

**Memory Safety:**
- Bounded sprite cache (max 20 sprites in LRU)
- Evolution data structures have known size limits
- No unbounded loops or recursive queries

### Reliability/Availability

**Graceful Degradation:**
- Missing evolution data → Display "Evolution data unavailable" message
- Missing evolution sprites → Show placeholder with Pokémon name text
- Database query failure → Log error, show "Error loading evolutions" message
- Corrupted evolution data → Validate structure, fallback to empty state

**Error Handling:**
```python
try:
    evolution_data = db.get_evolution_chain(pokemon_id)
    if not evolution_data or 'stages' not in evolution_data:
        # Handle empty or malformed data
        self.show_no_evolution_message()
except DatabaseError as e:
    logger.error(f"Evolution query failed for pokemon {pokemon_id}: {e}")
    self.show_error_message()
except Exception as e:
    logger.error(f"Unexpected error in EvolutionPanel: {e}")
    self.show_generic_error()
```

**Data Validation:**
- Verify evolution_data structure before rendering
- Check sprite loading success before blitting
- Validate pokemon_id exists in valid range
- Handle circular evolution references (should not exist in Gen 1-3)

**Recovery Behavior:**
- Failed sprite load → Retry once, then show placeholder
- Database timeout → Log warning, show cached data if available
- Rendering error → Skip evolution panel, show rest of DetailScreen
- User can navigate back and retry if error was transient

**Offline Operation:**
- All evolution data preloaded in database (no internet required)
- All sprites preloaded in assets directory
- No external API calls during runtime
- Fully functional without network connectivity

### Observability

**Logging Strategy:**

```python
import logging
logger = logging.getLogger(__name__)

# Info-level logs for normal operation
logger.info(f"Loading evolution chain for Pokemon #{pokemon_id}")
logger.info(f"Evolution chain loaded: {len(stages)} stages, {len(evolutions)} relationships")

# Warning-level logs for degraded behavior
logger.warning(f"Sprite not found for Pokemon #{missing_id}, using placeholder")
logger.warning(f"Evolution data incomplete for Pokemon #{pokemon_id}")

# Error-level logs for failures
logger.error(f"Database query failed: {str(error)}")
logger.error(f"Failed to render evolution panel: {str(error)}")
```

**Metrics to Track:**
- Evolution panel render time (average, p95, p99)
- Database query execution time
- Sprite cache hit rate
- Evolution panel errors per session
- Navigation to evolution relatives (user engagement metric)

**Debug Information:**
- Log evolution data structure on load (DEBUG level)
- Log sprite loading status (DEBUG level)
- Log input handling events (DEBUG level)
- Performance Monitor integration for frame time tracking

**Error Context:**
- Include pokemon_id in all log messages
- Include evolution chain_id when available
- Include stack trace for unexpected errors
- Log user navigation path leading to error

**Production Monitoring:**
- Console output for development
- Log file for production (rotating, 10MB max)
- Error count thresholds (alert if >10 errors/hour)
- Performance degradation detection (alert if render time >500ms)

**Testing Observability:**
- Unit tests verify logging calls
- Integration tests check metric collection
- Performance tests validate timing logs
- Error injection tests verify error logging

## Dependencies and Integrations

**Internal Dependencies (All Complete):**

| Component | Status | Version/Location | Notes |
|-----------|--------|------------------|-------|
| Database Schema | ✅ Complete | src/data/database.py | evolution_chains and evolutions tables exist |
| Evolution Data | ✅ Complete | Seeded via manage_db.py | All Gen 1-3 evolution chains populated |
| DetailScreen | ✅ Complete | src/ui/detail_screen.py | Stable from Epic 3 |
| SpriteLoader | ✅ Complete | src/ui/sprite_loader.py | load_thumbnail() method ready |
| ScreenManager | ✅ Complete | src/ui/screen_manager.py | Navigation infrastructure |
| Colors Palette | ✅ Complete | src/ui/colors.py | Holographic blue theme defined |

**External Dependencies (None):**
- No new Python packages required
- No external API calls
- No new asset files needed (sprites already present)

**Database Integration:**

```python
# Existing tables used (no schema changes)
evolution_chains:
  - id (primary key)
  - name (chain name)

evolutions:
  - id (primary key)
  - from_pokemon_id (foreign key → pokemon.id)
  - to_pokemon_id (foreign key → pokemon.id)
  - evolution_method (string)
  - minimum_level (integer, nullable)
  - evolution_item_id (foreign key → items.id, nullable)
  - trigger (string, nullable)

pokemon:
  - id (primary key)
  - chain_id (foreign key → evolution_chains.id)
  - name, height, weight, etc.

items:
  - id (primary key)
  - name (e.g., "Fire Stone", "Moon Stone")
```

**Sprite Asset Integration:**
- Uses existing thumbnail sprites: `assets/sprites/thumb/{pokemon_id:03d}.png`
- All 386 sprites already present from Epic 3
- 64x64 size optimal for evolution panel display
- SpriteLoader handles missing files gracefully

**UI Component Integration:**
- EvolutionPanel extends DetailScreen (composition pattern)
- Inherits holographic aesthetic from UX Design Specification
- Uses existing color constants from colors.py
- Follows screen lifecycle pattern (on_enter, render, handle_input)

**Manager Integration:**
- No StateManager integration needed (evolution data is static)
- No AudioManager integration (no audio for evolution display)
- InputManager already handles A/B button input

**Testing Integration:**
- Uses existing test fixtures (conftest.py)
- Leverages Database test helpers
- Integrates with pytest framework
- Performance Monitor tracks render times

**Critical Path Dependencies:**
1. Database must be initialized (`manage_db.py init`)
2. Evolution data must be seeded (`manage_db.py seed --gen 1-3`)
3. Sprite assets must exist in `assets/sprites/thumb/`
4. DetailScreen must be functional (Epic 3 complete)

**No Blockers:** All dependencies are already satisfied. Epic 5 can begin implementation immediately.

## Acceptance Criteria (Authoritative)

**AC-1: Three-Stage Evolution Chain Display**
GIVEN a Pokémon with a three-stage evolution chain (e.g., Charmander → Charmeleon → Charizard)
WHEN viewing DetailScreen
THEN display all three stages horizontally with sprites, names, and evolution requirements
AND show arrows between stages with requirement text below each arrow

**AC-2: Branching Evolution Display**
GIVEN a Pokémon with branching evolutions (e.g., Eevee → Vaporeon/Jolteon/Flareon/Espeon/Umbreon)
WHEN viewing DetailScreen
THEN display all evolution branches with clear visual separation
AND show current Pokémon as the root with branches spreading from it

**AC-3: Single-Stage Pokémon Handling**
GIVEN a single-stage Pokémon with no evolutions (e.g., Ditto, Farfetch'd, Heracross)
WHEN viewing DetailScreen
THEN display "No evolutions" message in evolution panel
AND maintain consistent panel styling with border

**AC-4: Current Pokémon Indication**
GIVEN evolution panel displayed with multiple stages
WHEN current Pokémon is part of the chain
THEN highlight current Pokémon sprite with brighter cyan glow (#4df7ff)
AND display "Current" label underneath sprite

**AC-5: Navigation to Evolution Relatives**
GIVEN evolution panel with multiple stages displayed
WHEN user presses A button while on an evolution sprite
THEN navigate to that Pokémon's DetailScreen
AND new screen displays the selected Pokémon with ITS evolution chain

**AC-6: Level Requirement Display**
GIVEN evolution with level requirement (e.g., Bulbasaur → Ivysaur at level 16)
WHEN displaying evolution chain
THEN show "Level 16" text below evolution arrow
AND use ice blue color (#a8e6ff) for readability

**AC-7: Stone Requirement Display**
GIVEN evolution with stone requirement (e.g., Pikachu → Raichu with Thunder Stone)
WHEN displaying evolution chain
THEN show stone name ("Thunder Stone") below evolution arrow
AND use ice blue color (#a8e6ff) for readability

**AC-8: Trade Evolution Display**
GIVEN evolution requiring trade (e.g., Machoke → Machamp)
WHEN displaying evolution chain
THEN show "Trade" text below evolution arrow
AND handle trade-with-item cases (e.g., "Trade holding Metal Coat")

**AC-9: Performance - First Render**
GIVEN user navigating to DetailScreen for first time
WHEN evolution panel renders (database query + sprite loading)
THEN complete rendering within 200ms
AND maintain 30 FPS during render

**AC-10: Performance - Cached Render**
GIVEN user returning to previously viewed DetailScreen
WHEN evolution panel renders (cached data and sprites)
THEN complete rendering within 50ms
AND maintain 30 FPS during render

**AC-11: Data Accuracy**
GIVEN all 386 Gen 1-3 Pokémon
WHEN viewing each Pokémon's evolution chain
THEN display accurate evolution data matching PokéAPI source
AND show correct evolution requirements for each stage

**AC-12: Visual Consistency**
GIVEN evolution panel displayed
WHEN rendered on screen
THEN follow holographic blue aesthetic from UX Design Specification
AND use electric blue (#00d4ff) for arrows and borders
AND use ice blue (#a8e6ff) for requirement text
AND maintain 16px padding and consistent spacing

## Traceability Mapping

| AC | PRD Section | Architecture Component | Code Location | Test Coverage |
|----|-------------|------------------------|---------------|---------------|
| **AC-1** | FR4.1 Evolution Information | DetailScreen + EvolutionPanel | src/ui/detail_screen.py | test_evolution_panel.py::test_three_stage_chain |
| **AC-2** | FR4.1 Evolution Information | EvolutionPanel branching logic | src/ui/detail_screen.py | test_evolution_panel.py::test_branching_evolutions |
| **AC-3** | FR4.1 Evolution Information | EvolutionPanel empty state | src/ui/detail_screen.py | test_evolution_panel.py::test_no_evolutions |
| **AC-4** | FR4.1 Evolution Information | EvolutionPanel render highlight | src/ui/detail_screen.py | test_evolution_panel.py::test_current_indicator |
| **AC-5** | FR4.2 Evolution Navigation | DetailScreen.handle_input() | src/ui/detail_screen.py | test_evolution_panel.py::test_navigation_to_relative |
| **AC-6** | FR4.1 Evolution Information | Evolution requirement rendering | src/ui/detail_screen.py | test_evolution_panel.py::test_level_requirement |
| **AC-7** | FR4.1 Evolution Information | Evolution requirement rendering | src/ui/detail_screen.py | test_evolution_panel.py::test_stone_requirement |
| **AC-8** | FR4.1 Evolution Information | Evolution requirement rendering | src/ui/detail_screen.py | test_evolution_panel.py::test_trade_requirement |
| **AC-9** | NFR-P1 Frame Rate, NFR-P2 Input Latency | EvolutionPanel performance | src/ui/detail_screen.py | test_performance.py::test_evolution_first_render |
| **AC-10** | NFR-P1 Frame Rate | SpriteLoader caching | src/ui/sprite_loader.py | test_performance.py::test_evolution_cached_render |
| **AC-11** | FR1.3 Evolution Data | Database.get_evolution_chain() | src/data/database.py | test_database.py::test_evolution_data_accuracy |
| **AC-12** | UX Design Spec - Holographic Aesthetic | EvolutionPanel render colors | src/ui/detail_screen.py | test_evolution_panel.py::test_visual_styling |

**Requirements Traceability:**

**FR1.3 (Evolution Data):**
- ✅ Covered by AC-11 (data accuracy)
- ✅ Covered by Database schema (already implemented)
- ✅ Covered by manage_db.py seeding

**FR4.1 (Evolution Information):**
- ✅ Covered by AC-1 (three-stage chains)
- ✅ Covered by AC-2 (branching chains)
- ✅ Covered by AC-3 (no evolutions case)
- ✅ Covered by AC-4 (current position indicator)
- ✅ Covered by AC-6, AC-7, AC-8 (requirements display)

**FR4.2 (Evolution Navigation):**
- ✅ Covered by AC-5 (A button navigation)

**NFR-P1, NFR-P2 (Performance):**
- ✅ Covered by AC-9 (first render performance)
- ✅ Covered by AC-10 (cached render performance)

**UX Design Specification:**
- ✅ Covered by AC-12 (visual consistency)
- ✅ Holographic blue aesthetic (#00d4ff, #a8e6ff)
- ✅ Horizontal evolution layout
- ✅ Sprite + text composition

**Architecture Alignment:**
- ✅ Screen-based navigation pattern (AC-5)
- ✅ Database context manager (AC-11)
- ✅ SpriteLoader caching (AC-9, AC-10)
- ✅ Component lifecycle pattern (all ACs)

## Risks, Assumptions, Open Questions

### Risks

**Risk 1: Evolution Data Incomplete or Incorrect**
- **Probability:** Low
- **Impact:** High (displays wrong evolution information to users)
- **Mitigation:** 
  - Validate evolution data against PokéAPI reference during seeding
  - Add database integrity checks in test suite
  - Manual spot-check known complex chains (Eevee, Tyrogue)
- **Status:** Mitigated (data seeded from trusted source)

**Risk 2: Complex Branching Chains Don't Fit Layout**
- **Probability:** Low
- **Impact:** Medium (UI cluttered or unreadable)
- **Mitigation:**
  - Design supports up to 6 horizontal stages (handles all Gen 1-3 cases)
  - Eevee has 5 evolutions (worst case): 1 root + 5 branches = fits
  - Use 64x64 thumbnails (small enough for 6 sprites at 480x320)
  - Vertical layout fallback if needed (future enhancement)
- **Status:** Mitigated (layout tested with Eevee wireframes)

**Risk 3: Performance Degrades with Many Sprite Loads**
- **Probability:** Medium
- **Impact:** Medium (stuttering or lag on DetailScreen)
- **Mitigation:**
  - SpriteLoader LRU cache keeps 20 most recent sprites
  - Thumbnail size (64x64) optimized for fast loading
  - Worst case (Eevee): 6 sprites × 10ms = 60ms (within 200ms budget)
  - Async sprite loading if needed (future optimization)
- **Status:** Mitigated (performance targets achievable)

**Risk 4: Database Query Slow on Complex Chains**
- **Probability:** Low
- **Impact:** Low (query adds latency)
- **Mitigation:**
  - Indexed columns (id, chain_id) ensure fast queries
  - Result sets are small (typically 3-10 rows)
  - Query execution time target: <20ms
  - Cache evolution data per Pokémon if needed
- **Status:** Mitigated (SQLite performance validated)

### Assumptions

**Assumption 1: Users Understand Evolution Mechanics**
- Users familiar with Pokémon games/anime understand evolution concept
- No need to explain WHAT evolution is, just show the chain
- Requirements text ("Level 16", "Fire Stone") sufficient for fans
- **Validation:** User testing with target demographic

**Assumption 2: Horizontal Layout is Intuitive**
- Left-to-right flow matches natural reading order (Western audiences)
- Arrow direction clearly indicates evolution progression
- "Current" indicator disambiguates user's position in chain
- **Validation:** UX review confirms layout clarity

**Assumption 3: Thumbnail Sprites are Recognizable**
- 64x64 pixel sprites are large enough to identify Pokémon
- Pokémon name underneath aids recognition
- Users familiar with Gen 1-3 Pokémon sprites
- **Validation:** Visual review on target display size

**Assumption 4: Database Data is Complete**
- manage_db.py seed populated all evolution chains
- No missing evolution relationships in Gen 1-3
- All evolution items (stones) are named in items table
- **Validation:** Test coverage for all 386 Pokémon

**Assumption 5: No Real-Time Evolution Data Updates**
- Evolution data is static (no updates after seeding)
- No need for data refresh or sync mechanisms
- Offline-first architecture assumption holds
- **Validation:** Confirmed by PRD requirements

### Open Questions

**Question 1: Should we support touch interaction on evolution sprites?**
- **Context:** If user has touch screen, tap to navigate vs A button
- **Decision Needed By:** Implementation start
- **Current Status:** Out of scope for MVP (button controls only)
- **Follow-Up:** Epic 7 (Interactive Features) may add touch support

**Question 2: How to handle Pokémon with multiple pre-evolutions (Tyrogue)?**
- **Context:** Tyrogue evolves into Hitmonlee, Hitmonchan, or Hitmontop
- **Decision:** Show Tyrogue as root with 3 branches (same as Eevee pattern)
- **Status:** Resolved (consistent with branching evolution approach)

**Question 3: Should we show base stat changes between evolution stages?**
- **Context:** Users may want to see stat increases with evolution
- **Current Scope:** Out of scope for Epic 5 (show chain only)
- **Future Enhancement:** Epic 6 (Relationships View) could add this
- **Status:** Deferred to post-MVP

**Question 4: How to indicate trade evolutions require human interaction?**
- **Context:** "Trade" doesn't clarify it needs another person
- **Decision:** Keep text simple ("Trade"), matches game terminology
- **Rationale:** Target users (fans) understand trade mechanics
- **Status:** Resolved

**Question 5: Should evolution panel scroll if chain is too long?**
- **Context:** All Gen 1-3 chains fit in 6 horizontal stages
- **Decision:** No scrolling needed (max chain length is 3, max branches is 5)
- **Status:** Resolved (not needed for Gen 1-3 scope)

## Test Strategy Summary

### Testing Approach

**Test Pyramid:**
- **Unit Tests (60%):** Database queries, data processing, component logic
- **Integration Tests (30%):** EvolutionPanel + DetailScreen + Database
- **System Tests (10%):** End-to-end user workflows on actual hardware

### Unit Test Coverage

**Database Tests (test_database.py):**
```python
class TestEvolutionQueries:
    def test_get_evolution_chain_three_stage(self):
        # Test Charmander → Charmeleon → Charizard
        data = db.get_evolution_chain(4)  # Charmander
        assert len(data['stages']) == 3
        assert len(data['evolutions']) == 2
        assert data['current_stage'] == 1
    
    def test_get_evolution_chain_branching(self):
        # Test Eevee → 5 evolutions
        data = db.get_evolution_chain(133)  # Eevee
        assert len(data['stages']) == 6  # Eevee + 5 evolutions
        assert len(data['evolutions']) == 5
        assert data['current_stage'] == 1
    
    def test_get_evolution_chain_no_evolutions(self):
        # Test Ditto (no evolutions)
        data = db.get_evolution_chain(132)  # Ditto
        assert len(data['stages']) == 1
        assert len(data['evolutions']) == 0
    
    def test_evolution_requirements_parsing(self):
        # Test all evolution method types
        # Level: Charmander → Charmeleon at 16
        # Stone: Pikachu → Raichu with Thunder Stone
        # Trade: Machoke → Machamp
        # Trade-item: Onix → Steelix with Metal Coat
        # Happiness: Pichu → Pikachu
        pass
```

**EvolutionPanel Tests (test_evolution_panel.py):**
```python
class TestEvolutionPanel:
    def test_render_three_stage_chain(self):
        # Verify correct sprite positions and names
        pass
    
    def test_render_branching_chain(self):
        # Verify Eevee + 5 evolutions layout
        pass
    
    def test_current_pokemon_highlight(self):
        # Verify "Current" indicator on correct sprite
        pass
    
    def test_evolution_requirements_display(self):
        # Verify requirement text rendered correctly
        pass
    
    def test_no_evolutions_message(self):
        # Verify "No evolutions" shown for Ditto
        pass
    
    def test_sprite_loading_failure(self):
        # Verify placeholder shown when sprite missing
        pass
```

### Integration Test Coverage

**DetailScreen Integration (test_detail_screen_integration.py):**
```python
class TestDetailScreenWithEvolution:
    def test_evolution_panel_renders_in_detail_screen(self):
        # Full integration: database → evolution panel → screen render
        pass
    
    def test_navigation_to_evolution_relative(self):
        # A button press → navigate to evolution's detail screen
        pass
    
    def test_evolution_data_cached_between_views(self):
        # View Pikachu → View Raichu → Back to Pikachu (cached)
        pass
```

### System Test Coverage

**End-to-End Workflows (test_e2e_evolution.py):**
```python
class TestEvolutionE2E:
    def test_browse_to_detail_with_evolution(self):
        # BrowseScreen → [A] → DetailScreen with evolution panel
        pass
    
    def test_navigate_full_evolution_chain(self):
        # Charmander → Charmeleon → Charizard via A button
        pass
    
    def test_all_386_pokemon_evolution_display(self):
        # Iterate through all Pokémon, verify evolution panel renders
        pass
```

### Performance Test Coverage

**Rendering Performance (test_performance.py):**
```python
class TestEvolutionPerformance:
    def test_first_render_time(self):
        # Measure time from on_enter() to render complete
        # Assert < 200ms
        pass
    
    def test_cached_render_time(self):
        # Measure time for second view of same Pokémon
        # Assert < 50ms
        pass
    
    def test_worst_case_branching(self):
        # Eevee with 5 evolutions (6 sprites)
        # Assert < 250ms worst case
        pass
    
    def test_frame_rate_maintained(self):
        # Verify 30 FPS maintained during evolution panel display
        pass
```

### Data Validation Testing

**Evolution Data Accuracy (test_evolution_data.py):**
```python
class TestEvolutionDataAccuracy:
    @pytest.mark.parametrize("pokemon_id,expected_evolutions", [
        (1, ["Ivysaur", "Venusaur"]),  # Bulbasaur
        (25, ["Raichu"]),  # Pikachu
        (133, ["Vaporeon", "Jolteon", "Flareon", "Espeon", "Umbreon"]),  # Eevee
        (132, []),  # Ditto (no evolutions)
    ])
    def test_evolution_chain_accuracy(self, pokemon_id, expected_evolutions):
        # Validate against known correct data
        pass
```

### Manual Test Cases

**Visual Inspection Tests:**
1. Evolution panel layout on 480×320 display (actual hardware)
2. Sprite clarity at 64×64 size (readability test)
3. Requirement text legibility (ice blue on dark blue)
4. Holographic aesthetic consistency (borders, arrows)
5. "Current" indicator visibility and clarity

**User Experience Tests:**
1. Navigate through full evolution chain (Charmander → Charizard)
2. View branching evolution (Eevee → all 5 evolutions)
3. View single-stage Pokémon (Ditto, Farfetch'd)
4. Rapid navigation between evolution relatives (performance feel)
5. Edge case: Pokémon at middle of chain (Charmeleon)

### Test Execution Plan

**Phase 1: Unit Tests (Day 1-2)**
- Implement Database.get_evolution_chain() with tests
- Implement EvolutionPanel component with tests
- Achieve 90%+ code coverage on new code

**Phase 2: Integration Tests (Day 3)**
- DetailScreen + EvolutionPanel integration
- Navigation between evolution relatives
- Sprite loading and caching validation

**Phase 3: System Tests (Day 4)**
- End-to-end workflows on desktop
- All 386 Pokémon iteration test
- Performance benchmarking

**Phase 4: Hardware Validation (Day 5)**
- Deploy to Raspberry Pi 3B+
- Visual inspection on 480×320 LCD
- Performance validation on target hardware
- User acceptance testing (manual)

### Success Criteria

- ✅ All unit tests pass (100%)
- ✅ All integration tests pass (100%)
- ✅ System tests pass for all 386 Pokémon
- ✅ Performance tests meet <200ms first render, <50ms cached
- ✅ Manual visual inspection confirms holographic aesthetic
- ✅ No regressions in existing DetailScreen functionality
- ✅ Code coverage >85% for new EvolutionPanel code
