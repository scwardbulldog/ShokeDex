# ShokeDex Architecture

**Project:** ShokeDex - Handheld Pokédex Device
**Date:** 2025-11-14
**Architect:** Winston
**For:** King

---

## Executive Summary

ShokeDex is a Raspberry Pi-based embedded application using pygame for rendering, SQLite for data storage, and GPIO for physical button controls. The architecture is built around a **screen-based navigation pattern** with **centralized manager classes** for state persistence (StateManager), audio playback (AudioManager), and input handling (InputManager).

The MVP focuses on browsing 386 Pokémon (Gen 1-3) with generation-based navigation, detailed stat views, and evolution chains. The architecture prioritizes **resource efficiency** for Raspberry Pi 3B+ hardware, **offline-first operation**, and **appliance simplicity** (zero configuration).

**Key Architectural Patterns:**
- Screen-based UI with ScreenManager coordinator
- Manager singleton pattern for cross-cutting concerns
- Lazy-loading for sprites and audio
- SQLite with parameterized queries for data access
- Hardware abstraction for input portability

---

## Decision Summary

| Category | Decision | Version/Details | Affects Epics | Rationale |
|----------|----------|-----------------|---------------|-----------|
| **Language** | Python | 3.11+ | All | Target platform standard, pygame ecosystem |
| **Graphics** | pygame | 2.5.0+ | All UI | Best Raspberry Pi graphics library, hardware acceleration support |
| **Database** | SQLite | 3.x (stdlib) | All data access | Embedded, zero-config, single-file portability |
| **Audio** | pygame.mixer | Via pygame | Audio playback | Integrated with pygame, low latency |
| **GPIO** | gpiozero | 2.0.0+ | Input hardware | Clean API, built-in debouncing |
| **Image Processing** | Pillow | 10.0.0+ | Sprite loading | pygame compatibility, format flexibility |
| **Screen Pattern** | Screen base class | Custom | All UI | Consistent lifecycle, easy navigation |
| **State Persistence** | JSON file | Custom StateManager | Session state | Human-readable, easy backup/restore |
| **Audio Caching** | LRU cache | 20 items max | Audio system | Balance memory vs load time |
| **Sprite Loading** | Lazy + cache | On-demand | UI rendering | Minimize memory footprint |
| **Generation Nav** | SQL range queries | WHERE id BETWEEN | Browse features | Clean database filtering |
| **Input Mode** | Keyboard/GPIO dual | Runtime switchable | All input | Development flexibility |

---

## Project Structure

```
ShokeDex/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Application entry point
│   ├── state_manager.py           # ✅ Session state persistence
│   ├── audio_manager.py           # ✅ Audio playback & caching
│   ├── input_manager.py           # ✅ Input abstraction (keyboard/GPIO)
│   ├── performance_monitor.py     # Performance tracking
│   ├── sync_manager.py            # Future: Data sync
│   ├── data/
│   │   ├── __init__.py
│   │   ├── database.py            # ✅ SQLite database interface
│   │   ├── loader.py              # ✅ PokéAPI data loader
│   │   ├── migrations.py          # Schema versioning
│   │   ├── sprite_processor.py    # ✅ Sprite optimization
│   │   └── manage_db.py           # CLI database tools
│   └── ui/
│       ├── __init__.py
│       ├── screen.py              # ✅ Base Screen class
│       ├── screen_manager.py      # ✅ Screen navigation coordinator
│       ├── home_screen.py         # ✅ Grid view (needs generation filter)
│       ├── detail_screen.py       # ✅ Pokémon details (needs audio integration)
│       ├── list_screen.py         # Alternative list view
│       ├── search_screen.py       # Search functionality
│       ├── settings_screen.py     # Settings UI
│       ├── stub_screen.py         # Placeholder screen
│       ├── sprite_loader.py       # ✅ Sprite loading utilities
│       └── colors.py              # ✅ Color palette constants
├── tests/
│   ├── test_database.py           # ✅ Database tests
│   ├── test_state_manager.py      # ✅ StateManager tests
│   ├── test_audio_manager.py      # ✅ AudioManager tests
│   ├── test_input_manager.py      # ✅ InputManager tests
│   ├── test_sprite_processor.py   # ✅ Sprite processing tests
│   └── test_performance_monitor.py # ✅ Performance tests
├── data/
│   ├── pokedex.db                 # SQLite database (created on init)
│   └── shokedex_state.json        # User state file (created on first run)
├── assets/
│   ├── sprites/
│   │   ├── thumb/                 # 64x64 thumbnails (001.png - 386.png)
│   │   └── detail/                # 128x128 detail sprites
│   ├── audio/
│   │   └── cries/                 # Pokémon cries (001.ogg - 386.ogg)
│   ├── icons/                     # Type badges, UI icons
│   └── fonts/                     # Custom fonts (if needed)
├── docs/
│   ├── PRD.md                     # ✅ Product Requirements
│   ├── architecture.md            # ✅ This document
│   ├── database_schema.md         # Database documentation
│   └── ui_guide.md                # UI implementation guide
├── requirements.txt               # Python dependencies
└── README.md                      # Project overview & setup
```

---

## Technology Stack Details

### Core Technologies

**Python 3.11+**
- Primary development language
- Target: Raspberry Pi OS (Bookworm) default Python
- Type hints used for clarity (not strict typing)
- PEP 8 style guidelines

**pygame 2.5.0+**
- Graphics rendering engine
- Display management (480x320 to 800x480 resolutions)
- Event loop and input handling
- Hardware-accelerated blitting on Raspberry Pi
- pygame.mixer for audio playback

**SQLite 3.x**
- Embedded database (Python stdlib)
- Single-file portability (data/pokedex.db)
- Full relational schema (12 tables)
- 386 Pokémon with types, stats, evolutions, abilities

**gpiozero 2.0.0+**
- GPIO button interface for hardware mode
- Built-in debouncing and pull-up/down resistors
- Graceful fallback when GPIO unavailable (dev mode)

### Supporting Libraries

**Pillow 10.0.0+**
- Image loading and processing
- Sprite format conversion
- Thumbnail generation

**requests 2.31.0+**
- HTTP client for PokéAPI data loading (initial setup only)
- Not used at runtime (offline-first)

---

## Epic to Architecture Mapping

| Epic | Architecture Components | Screens | Managers |
|------|------------------------|---------|----------|
| **Generation Navigation** | HomeScreen, Database queries, StateManager | HomeScreen | StateManager (last generation) |
| **Pokémon Detail View** | DetailScreen, SpriteLoader, AudioManager | DetailScreen | AudioManager (play cry), StateManager (save view) |
| **Evolution Display** | DetailScreen tabs, Database evolution queries | DetailScreen | Database |
| **State Persistence** | StateManager, JSON file I/O | All screens | StateManager (singleton) |
| **Audio Playback** | AudioManager, pygame.mixer, LRU cache | DetailScreen | AudioManager (singleton) |
| **Input Handling** | InputManager, pygame events, GPIO | All screens | InputManager (singleton) |
| **Sprite Display** | SpriteLoader, Pillow, pygame.Surface | HomeScreen, DetailScreen | (module-level caching) |

---

## Manager Architecture Pattern

### Singleton Manager Pattern

All manager classes (StateManager, AudioManager, InputManager) follow this pattern:

```python
# In main.py or application initialization
state_manager = StateManager()
audio_manager = AudioManager(volume=state_manager.get_volume())
input_manager = InputManager(mode=InputMode.KEYBOARD)

# Pass to ScreenManager
screen_manager = ScreenManager(
    database=db,
    state_manager=state_manager,
    audio_manager=audio_manager,
    input_manager=input_manager
)
```

**Rule:** Manager instances are created ONCE at application startup and passed to ScreenManager, which provides them to all screens.

### StateManager Integration

**Purpose:** Persist user session data across power cycles

**Usage Pattern:**
```python
class SomeScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        self.state_manager = screen_manager.state_manager
    
    def on_enter(self):
        # Load last viewed Pokemon
        pokemon_id = self.state_manager.get_last_viewed_id()
        generation = self.state_manager.get_last_viewed_generation()
    
    def _select_pokemon(self, pokemon_id):
        # Update state when Pokemon changes
        self.state_manager.set_last_viewed(pokemon_id)
        
    def on_exit(self):
        # Save state on screen exit
        self.state_manager.save_state()
```

**When to call save_state():**
- On screen exit (on_exit method)
- On app shutdown (main loop cleanup)
- After significant state changes (optional, for data safety)

**What StateManager tracks:**
- Last viewed Pokémon ID and generation
- Favorites list (for future feature)
- Recent views (last 10 Pokémon)
- User preferences (volume, input mode)
- Usage statistics (total views, sessions)

### AudioManager Integration

**Purpose:** Play Pokémon cries with memory-efficient caching

**Usage Pattern:**
```python
class DetailScreen(Screen):
    def __init__(self, screen_manager, pokemon_id):
        super().__init__(screen_manager)
        self.audio_manager = screen_manager.audio_manager
        self.pokemon_id = pokemon_id
    
    def on_enter(self):
        # Play cry when entering detail view
        if self.audio_manager.is_enabled():
            self.audio_manager.play_cry(self.pokemon_id)
    
    def on_exit(self):
        # Stop audio when leaving (optional, for clean transitions)
        self.audio_manager.stop()
```

**AudioManager Features:**
- **Lazy loading:** Audio files loaded on first play, not all at startup
- **LRU caching:** Keeps last 20 cries in memory
- **Volume control:** StateManager stores preference, AudioManager applies it
- **Graceful degradation:** Missing audio files don't crash app

**File format:** OGG Vorbis (compressed, good for Raspberry Pi)
**File location:** `assets/audio/cries/{pokemon_id:03d}.ogg` (e.g., 025.ogg for Pikachu)

### InputManager Integration

**Purpose:** Abstract keyboard (dev) and GPIO (hardware) input

**Usage Pattern:**
```python
class SomeScreen(Screen):
    def handle_input(self, action: InputAction):
        if action == InputAction.UP:
            self._move_up()
        elif action == InputAction.SELECT:
            self._select_item()
        elif action == InputAction.BACK:
            self.screen_manager.pop()
```

**InputAction enum:**
- `UP`, `DOWN`, `LEFT`, `RIGHT` - Navigation
- `SELECT` - Confirm/choose
- `BACK` - Cancel/return
- `START` - Menu/settings

**Input modes:**
- **Keyboard mode:** Development on desktop (arrows, WASD, Enter, Esc, Tab)
- **GPIO mode:** Hardware buttons on Raspberry Pi (BCM pin numbers configurable)

---

## Screen Lifecycle & Navigation

### Screen Base Class

All UI screens inherit from `Screen` base class:

```python
class Screen:
    def on_enter(self):
        """Called when screen becomes active"""
        pass
    
    def on_exit(self):
        """Called when screen becomes inactive"""
        pass
    
    def update(self, delta_time: float):
        """Called every frame for logic updates"""
        pass
    
    def render(self, surface: pygame.Surface):
        """Called every frame to draw the screen"""
        pass
    
    def handle_input(self, action: InputAction):
        """Called when input action received"""
        pass
```

**Lifecycle order:**
1. Screen instantiated
2. `on_enter()` called (load data, initialize fonts)
3. `update()` and `render()` called every frame
4. `handle_input()` called on user input
5. `on_exit()` called when navigating away

### ScreenManager Navigation

**Methods:**
- `push(screen)` - Navigate to new screen (adds to stack)
- `pop()` - Return to previous screen (removes from stack)
- `replace(screen)` - Replace current screen (no stack change)

**Navigation Pattern:**
```python
# From HomeScreen to DetailScreen
def _select_pokemon(self, pokemon_id):
    detail_screen = DetailScreen(self.screen_manager, pokemon_id)
    self.screen_manager.push(detail_screen)

# From DetailScreen back to HomeScreen
def handle_input(self, action: InputAction):
    if action == InputAction.BACK:
        self.screen_manager.pop()
```

**Stack Management:**
- HomeScreen is root (never popped)
- DetailScreen pushed on top when viewing Pokémon
- BACK button pops screen stack
- StateManager saves on pop (preserves last viewed)

---

## Generation Navigation Architecture

### Generation Boundaries

**Generation 1 (Kanto):** Pokémon #1-151 (Bulbasaur to Mew)
**Generation 2 (Johto):** Pokémon #152-251 (Chikorita to Celebi)
**Generation 3 (Hoenn):** Pokémon #252-386 (Treecko to Deoxys)

### Database Query Pattern

```python
# Generation filtering using ID ranges
GENERATION_RANGES = {
    1: (1, 151),
    2: (152, 251),
    3: (252, 386)
}

def get_pokemon_by_generation(generation: int):
    start, end = GENERATION_RANGES[generation]
    cursor = db.execute(
        "SELECT id, name FROM pokemon WHERE id BETWEEN ? AND ? ORDER BY id",
        (start, end)
    )
    return cursor.fetchall()
```

**Rule:** Always use `BETWEEN ? AND ?` with parameterized queries. Never hardcode ranges in SQL strings.

### HomeScreen Generation Switching

**L/R button behavior:**
- L button: Previous generation (3 → 2 → 1 → 3...)
- R button: Next generation (1 → 2 → 3 → 1...)
- Visual indicator: Generation badge (Kanto/Johto/Hoenn logo)

**State persistence:**
```python
def _switch_generation(self, delta: int):
    self.current_generation = ((self.current_generation + delta - 1) % 3) + 1
    self.state_manager.set_last_viewed(
        pokemon_id=self._get_first_in_generation(),
        generation=self.current_generation
    )
    self._reload_pokemon_list()
```

**On startup:**
- Load last viewed generation from StateManager
- If no saved state, default to Generation 1
- Load Pokémon list for that generation
- Scroll to last viewed Pokémon (or first in generation)

---

## Data Architecture

### Database Schema Overview

**12 tables covering:**
- `pokemon` - Core Pokémon data (id, name, height, weight, generation)
- `types` - 17 types for Gen 1-3 (no Fairy type)
- `pokemon_types` - Pokémon type assignments (1-2 types per Pokémon)
- `stats` - Base stats (HP, Attack, Defense, Sp.Atk, Sp.Def, Speed)
- `pokemon_stats` - Stat values per Pokémon
- `abilities` - Pokémon abilities
- `pokemon_abilities` - Ability assignments (regular + hidden)
- `evolution_chains` - Evolution family groups
- `evolutions` - Evolution relationships with requirements
- `moves` - Move data (structure exists, not populated in MVP)
- `pokemon_moves` - Move learning (structure exists, not populated)
- `items` - Evolution items and held items

### Database Access Pattern

**Context Manager:**
```python
from src.data.database import Database

with Database() as db:
    pokemon = db.get_pokemon_by_id(25)
    stats = db.get_pokemon_stats(25)
    types = db.get_pokemon_types(25)
```

**Helper Methods Available:**
- `get_pokemon_by_id(id)` - Get Pokémon basic info
- `get_pokemon_by_name(name)` - Search by name
- `get_pokemon_stats(id)` - Get all 6 base stats
- `get_pokemon_types(id)` - Get type(s)
- `get_evolutions(id)` - Get evolution chain
- `get_evolution_chain(id)` - Get full evolution family

**SQL Safety:**
- **ALWAYS use parameterized queries:** `cursor.execute("SELECT * FROM pokemon WHERE id = ?", (pokemon_id,))`
- **NEVER use string formatting:** ❌ `f"SELECT * FROM pokemon WHERE id = {pokemon_id}"`
- **Close cursors:** Let context manager handle it, or use `cursor.close()`

### State File Format

**Location:** `data/shokedex_state.json`

**Structure:**
```json
{
  "version": "1.0.0",
  "last_viewed": {
    "pokemon_id": 25,
    "generation": 1
  },
  "favorites": [],
  "recent": [25, 1, 150],
  "preferences": {
    "input_mode": "keyboard",
    "volume": 0.7
  },
  "stats": {
    "total_views": 42,
    "unique_viewed": 15,
    "sessions": 3
  }
}
```

**Corruption handling:** If JSON parse fails, reset to defaults and log error.

---

## Implementation Patterns

### Naming Conventions

**Python Files:**
- `snake_case.py` for all module names
- `CapitalizedWords` for class names
- `snake_case` for function and variable names

**Database:**
- Table names: `lowercase_plural` (e.g., `pokemon`, `types`, `pokemon_stats`)
- Column names: `snake_case` (e.g., `pokemon_id`, `base_stat`, `is_hidden`)
- Foreign keys: `{table}_id` format (e.g., `pokemon_id`, `type_id`)

**Assets:**
- Sprites: `{id:03d}.png` (e.g., `001.png`, `025.png`)
- Audio: `{id:03d}.ogg` (e.g., `001.ogg`, `025.ogg`)
- Icons: `type_{type_name}.png` (e.g., `type_fire.png`)

### Code Organization

**Screen files:**
- One screen class per file
- File name matches class name (e.g., `HomeScreen` in `home_screen.py`)
- All screens in `src/ui/` directory

**Manager files:**
- One manager class per file (e.g., `StateManager` in `state_manager.py`)
- Managers in `src/` root (cross-cutting concerns)

**Tests:**
- Test file per module: `test_{module_name}.py`
- Test class naming: `Test{ClassName}`
- Test method naming: `test_{method_name}_{scenario}`

### Error Handling

**Missing Resources:**
```python
# Sprites
if sprite is None:
    # Show placeholder with Pokemon name text
    placeholder = self._create_text_placeholder(pokemon_name)

# Audio
if not audio_manager.play_cry(pokemon_id):
    # Silent failure, log warning, continue
    print(f"Warning: Could not play cry for Pokemon #{pokemon_id}")

# Database
try:
    pokemon = db.get_pokemon_by_id(pokemon_id)
except Exception as e:
    print(f"Database error: {e}")
    # Show error screen with friendly message
    self._show_error_screen("Could not load Pokémon data")
```

**Graceful Degradation:**
- Missing sprites → Text placeholder
- Missing audio → Silent (no crash)
- Database error → Error screen with retry option
- Corrupted state file → Reset to defaults

### Performance Patterns

**Lazy Loading:**
```python
# Sprites loaded on demand, not at startup
def get_sprite(pokemon_id):
    if pokemon_id not in sprite_cache:
        sprite_cache[pokemon_id] = load_sprite(pokemon_id)
    return sprite_cache[pokemon_id]
```

**Pagination:**
```python
# Load only visible Pokemon (not all 386)
page_size = 12
offset = page * page_size
cursor = db.execute(
    "SELECT id, name FROM pokemon WHERE id BETWEEN ? AND ? LIMIT ? OFFSET ?",
    (gen_start, gen_end, page_size, offset)
)
```

**Frame Rate Management:**
```python
# Target 30 FPS on Raspberry Pi
clock = pygame.time.Clock()
while running:
    delta_time = clock.tick(30) / 1000.0  # 30 FPS cap
    # ... update and render
```

---

## Consistency Rules

### Manager Access Pattern

**✅ Correct:**
```python
class MyScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        self.state_manager = screen_manager.state_manager
        self.audio_manager = screen_manager.audio_manager
```

**❌ Incorrect:**
```python
# Don't create new manager instances
self.state_manager = StateManager()  # ❌ Creates duplicate instance

# Don't import and use global managers
from src.state_manager import state_manager  # ❌ Bypasses injection
```

### StateManager Save Points

**When to call `save_state()`:**
- ✅ Screen `on_exit()` method
- ✅ Application shutdown (main loop cleanup)
- ✅ After user changes preferences (volume, favorites)
- ❌ Every frame (too frequent, performance hit)
- ❌ On every Pokemon view (use on_exit instead)

### AudioManager Usage

**When to play cries:**
- ✅ DetailScreen `on_enter()` - Play cry when viewing Pokemon details
- ✅ User explicit action (button press to hear cry again)
- ❌ HomeScreen sprite hover (too noisy, performance issue)
- ❌ Every frame/update (audio spam)

### Database Query Safety

**✅ Always use parameterized queries:**
```python
cursor.execute("SELECT * FROM pokemon WHERE id = ?", (pokemon_id,))
cursor.execute("SELECT * FROM pokemon WHERE name LIKE ?", (f"%{search}%",))
```

**❌ Never use string formatting:**
```python
cursor.execute(f"SELECT * FROM pokemon WHERE id = {pokemon_id}")  # ❌ SQL injection risk
cursor.execute("SELECT * FROM pokemon WHERE name = '%s'" % name)  # ❌ Unsafe
```

### Screen Navigation Rules

**Stack discipline:**
- HomeScreen is always at bottom of stack (never pop it)
- DetailScreen always pushed on top (never replaces)
- BACK button always pops (never push on back)
- Settings/Search screens push (allow return)

**State consistency:**
- Save state in `on_exit()` before navigation
- Load state in `on_enter()` after navigation
- Update StateManager BEFORE pushing new screen

---

## Security & Data Protection

### SQL Injection Prevention

**Mandatory:** All database queries MUST use parameterized statements.

```python
# ✅ Safe
cursor.execute("SELECT * FROM pokemon WHERE name = ?", (user_input,))

# ❌ Unsafe
cursor.execute(f"SELECT * FROM pokemon WHERE name = '{user_input}'")
```

### File Path Safety

**Asset loading:**
```python
from pathlib import Path

# ✅ Safe path construction
asset_dir = Path("assets/sprites/thumb")
sprite_path = asset_dir / f"{pokemon_id:03d}.png"

# ❌ Unsafe string concatenation
sprite_path = "assets/sprites/thumb/" + user_input + ".png"  # Directory traversal risk
```

### State File Integrity

**Validation on load:**
```python
def _load_state(self):
    try:
        with open(self.state_file, 'r') as f:
            state = json.load(f)
        
        # Validate required keys exist
        if 'version' not in state or 'last_viewed' not in state:
            return self._get_default_state()
        
        return state
    except (json.JSONDecodeError, IOError):
        # Corrupted file - reset to defaults
        return self._get_default_state()
```

---

## Performance Considerations

### Raspberry Pi 3B+ Constraints

**Hardware limits:**
- CPU: 1.4 GHz quad-core ARM Cortex-A53
- RAM: 1GB
- GPU: VideoCore IV (hardware-accelerated blitting)
- Storage: SD card (variable I/O speed)

**Performance targets:**
- 30+ FPS during all operations
- < 100ms button input latency
- < 5 second boot time
- < 500MB total storage (app + data + assets)

### Optimization Strategies

**Sprite Management:**
- Use hardware-accelerated surfaces (`convert()` or `convert_alpha()`)
- Cache converted sprites in memory
- Lazy-load on demand (not all 386 at startup)
- Use appropriately sized sprites (64x64 thumb, 128x128 detail)

**Audio Management:**
- LRU cache (max 20 cries)
- OGG Vorbis compression (smaller than WAV)
- Preload evolution chain cries (optional optimization)
- Single channel playback (stop previous before playing new)

**Database Queries:**
- Indexed columns (id, name, generation)
- LIMIT clauses for pagination
- Prepared statements (SQLite query plan caching)
- Batch fetches (not row-by-row iteration)

**Frame Rate Management:**
```python
# Only update what changed
dirty_rects = []  # Track which areas need redrawing
pygame.display.update(dirty_rects)  # Update only changed areas

# Alternative: Full screen update (simpler, usually fast enough)
pygame.display.flip()  # Update entire screen
```

---

## Deployment Architecture

### Raspberry Pi Setup

**Prerequisites:**
- Raspberry Pi 3B+ or newer
- Raspberry Pi OS (Bookworm - Debian 12 based)
- Python 3.11+ (included in Raspberry Pi OS)
- Small LCD display (3.5"-7", 480x320 to 800x480)
- GPIO buttons (optional, keyboard fallback available)

**Installation:**
```bash
# Clone repository
git clone <repository_url> ~/ShokeDex
cd ~/ShokeDex

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python src/data/manage_db.py init
python src/data/manage_db.py seed --gen 1-3

# Run application
python src/main.py
```

**Auto-start on boot (optional):**
```bash
# Add to /etc/rc.local or create systemd service
# Ensures ShokeDex starts when Raspberry Pi powers on
```

### Development Environment

**Desktop Development:**
- Works on Windows, macOS, Linux
- Keyboard mode for input (no GPIO required)
- pygame window simulates LCD display
- Hot-reload possible with watchdog tools

**Development workflow:**
```bash
# On desktop (any OS)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python src/data/manage_db.py init
python src/data/manage_db.py seed --gen 1-3
python src/main.py
```

**Testing:**
```bash
# Run all tests
python -m unittest discover tests -v

# Run specific test
python -m unittest tests.test_state_manager -v

# Performance profiling
python tools/profile_performance.py
```

---

## Architecture Decision Records (ADRs)

### ADR-001: Screen-Based UI Architecture

**Decision:** Use Screen base class with push/pop navigation stack

**Rationale:**
- Common pygame pattern, well-understood
- Clean separation between screens
- Easy to add new screens without touching existing ones
- Stack-based navigation supports natural back-button behavior

**Consequences:**
- All UI must inherit from Screen
- ScreenManager becomes single point of coordination
- Memory footprint grows with stack depth (minimal for ShokeDex use case)

---

### ADR-002: Manager Singleton Pattern

**Decision:** Create manager instances once at startup, pass via ScreenManager

**Rationale:**
- Ensures single source of truth for state, audio, input
- Avoids global variables while providing global access
- Easy dependency injection for testing
- Explicit dependencies in screen constructors

**Consequences:**
- ScreenManager must hold references to all managers
- Screens access managers via `screen_manager.{manager_name}`
- Cannot create screens without ScreenManager (testing requires mocks)

---

### ADR-003: JSON for State Persistence

**Decision:** Use JSON file for StateManager storage (not database)

**Rationale:**
- Human-readable (easy debugging, manual editing if needed)
- Simple serialization (no ORM needed)
- Portable across systems (just copy file)
- Easy backup and restore
- State data is small (< 1KB), JSON overhead acceptable

**Consequences:**
- Not suitable for large datasets (but state is tiny)
- No ACID guarantees (but single-user app, low risk)
- File corruption possible (handled with try/catch + defaults)

---

### ADR-004: Lazy Loading for Assets

**Decision:** Load sprites and audio on-demand, not at startup

**Rationale:**
- 386 sprites + audio = significant memory on Raspberry Pi (1GB RAM)
- Faster startup (5 second target)
- LRU caching provides good hit rate for frequently viewed Pokémon
- User only views small fraction of Pokémon per session

**Consequences:**
- First view of Pokémon has slight delay (load sprite/audio)
- Cache eviction can cause re-loads
- Need placeholder handling for missing assets
- More complex resource management code

---

### ADR-005: Generation-Based Navigation

**Decision:** Filter Pokémon by generation using L/R buttons on HomeScreen

**Rationale:**
- Matches mental model (Kanto/Johto/Hoenn regions)
- Reduces visual clutter (151 max per page vs 386)
- Aligns with Pokédex canon (regional Pokédexes)
- Simple SQL range queries (BETWEEN id_start AND id_end)

**Consequences:**
- Cannot view all 386 at once (must switch generations)
- Generation boundaries hardcoded (id ranges 1-151, 152-251, 252-386)
- Future generations (4+) require architecture change

---

### ADR-006: Offline-First Architecture

**Decision:** All data preloaded, no runtime internet dependency

**Rationale:**
- Appliance simplicity (zero configuration, works immediately)
- Reliable operation (no API failures or network issues)
- Fast response (no network latency)
- Raspberry Pi may not have internet access after setup

**Consequences:**
- Initial setup requires internet (PokéAPI data load)
- Data is static (no live updates)
- Database and assets must be distributed with app
- Future features requiring live data need architecture change

---

## Next Steps for Implementation

### MVP Phase 1 - Core Integration (Priority 1)

**Epic: Generation Navigation Screen**
1. Update HomeScreen to filter by generation
2. Add L/R button handlers for generation switching
3. Integrate StateManager to save last viewed generation
4. Add generation badge UI element
5. Test generation switching performance (30 FPS target)

**Epic: Detail View with Audio**
1. Integrate AudioManager in DetailScreen
2. Play cry on screen enter (on_enter lifecycle)
3. Add volume control (up/down while holding START)
4. Handle missing audio files gracefully
5. Test audio latency and LRU cache effectiveness

**Epic: State Persistence**
1. Initialize StateManager in main.py
2. Save state on screen transitions (on_exit)
3. Load last viewed on startup
4. Add favorites toggle (for future feature)
5. Test state file corruption handling

### MVP Phase 2 - Polish (Priority 2)

**Epic: Evolution Display**
1. Query evolution chains from database
2. Display evolution tree in DetailScreen
3. Add navigation to evolution relatives
4. Show evolution requirements (level, item, etc.)

**Epic: Performance Optimization**
1. Profile frame rate under load (all screens)
2. Optimize sprite blitting (dirty rects if needed)
3. Reduce database query frequency (cache lists)
4. Test on actual Raspberry Pi 3B+ hardware

### Growth Features (Priority 3)

- Type badges with colorful icons
- Relationships view (evolutions + type matchups)
- "Who's That Pokémon?" quiz mode
- Screensaver display mode

---

## Validation Checklist

**Architecture Completeness:**
- ✅ All manager integration patterns defined
- ✅ Screen lifecycle documented
- ✅ Generation navigation architecture specified
- ✅ State persistence strategy clear
- ✅ Audio playback integration detailed
- ✅ Database query patterns established
- ✅ Error handling strategy defined
- ✅ Performance targets specified
- ✅ Security patterns (SQL injection prevention)
- ✅ File structure complete and specific
- ✅ No placeholder content ("TBD", "TODO" sections)

**PRD Coverage:**
- ✅ MVP features architecturally supported
- ✅ NFR performance targets addressed (30 FPS, 100ms latency)
- ✅ Growth features have clear extension points
- ✅ Technical constraints respected (Raspberry Pi limits)
- ✅ All 7 epics mapped to architecture components

**Implementation Readiness:**
- ✅ Developers can build HomeScreen with generation filtering
- ✅ Developers can integrate AudioManager in DetailScreen
- ✅ Developers can use StateManager consistently
- ✅ Database query patterns prevent SQL injection
- ✅ Error handling prevents crashes on missing assets
- ✅ Code organization and naming conventions clear

---

## Appendix: Technology Versions

**Verified as of:** 2025-11-14

| Technology | Version | Notes |
|------------|---------|-------|
| Python | 3.11+ | Raspberry Pi OS Bookworm default |
| pygame | 2.5.0+ | Latest stable, Raspberry Pi compatible |
| Pillow | 10.0.0+ | Image processing |
| SQLite | 3.x | Python stdlib |
| gpiozero | 2.0.0+ | GPIO interface |
| requests | 2.31.0+ | HTTP client (setup only) |

---

_This architecture document serves as the consistency contract for all AI agents implementing ShokeDex. All implementation decisions should align with the patterns and rules defined here._

_Generated by BMAD Decision Architecture Workflow v1.0_
_Architect: Winston_
_For: King_
_Date: 2025-11-14_
