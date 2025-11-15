# Epic Technical Specification: State Persistence

Date: 2025-11-15
Author: King
Epic ID: 3
Status: Draft

---

## Overview

Epic 3 implements the state persistence system that transforms ShokeDex from a stateless browser into a true appliance device with memory. This epic delivers the "pick up where you left off" experience: when you power on the device, it remembers the last Pokémon you viewed, the generation you were browsing, and your preferences (volume level, input mode). The core user experience is: browse to Pikachu → view details → power off → power back on → you're immediately back at Pikachu, ready to continue exploring.

This session memory creates the authentic Pokédex appliance feel - it's YOUR Pokédex with YOUR exploration history, not a generic device that resets every time. The system also tracks usage statistics (views, favorites, recent Pokémon) for future features and enables fast startup by restoring previous state without requiring configuration menus.

## Objectives and Scope

**In Scope:**
- StateManager class integration with JSON file persistence
- Last viewed Pokémon ID tracking across power cycles
- Last viewed generation tracking (Kanto/Johto/Hoenn)
- Volume preference storage (for future audio epic)
- Input mode preference storage (keyboard/GPIO)
- State file corruption handling with graceful fallback to defaults
- Automatic state save on screen exit lifecycle (on_exit)
- Final state save on application shutdown
- Fast startup restore (< 5 second target, loads to HomeScreen)
- Boot behavior: Always restore to HomeScreen with last Pokémon selected
- State file location: `data/shokedex_state.json`
- Minimal JSON structure (< 1KB for fast I/O)

**Out of Scope (Post-MVP - User Preferences & History Epic):**
- Recent Pokémon history tracking (last 10 viewed)
- Favorites list implementation and UI
- Usage statistics tracking (total views, unique Pokémon, session count)
- Favorites toggle functionality in DetailScreen
- Recent history display screen
- Cloud sync or backup (offline-first architecture)
- Multiple user profiles (single-user device)
- State export/import functionality
- Undo/redo history (not applicable to browsing)
- Settings UI screen (preference changes happen in-app)
- Encrypted state file (no sensitive data stored)

**Success Criteria:**
- Device powers on to HomeScreen showing last viewed Pokémon within 5 seconds
- Last viewed generation restored correctly (Kanto/Johto/Hoenn)
- User preferences (volume, input mode) persist across sessions
- State file corruption handled gracefully (reset to defaults, log error, continue)
- No data loss during normal power cycles (shutdown or screen transitions)
- StateManager accessible from all screens via ScreenManager injection
- State saved automatically on screen exit (on_exit lifecycle)
- Final save on application shutdown preserves all state
- First boot creates state file with sensible defaults (Bulbasaur #1, Kanto, keyboard mode)
- JSON file remains under 1KB for fast read/write operations

## System Architecture Alignment

This epic directly implements the **StateManager Integration** section of the architecture, following the established manager singleton pattern already used by AudioManager and InputManager.

**Architecture Components Involved:**
- `src/state_manager.py` - Core state persistence module (already exists, needs integration)
- `src/ui/screen_manager.py` - Provides StateManager to all screens
- `src/ui/home_screen.py` - Loads last viewed on startup, saves on generation switch
- `src/ui/detail_screen.py` - Saves last viewed Pokémon on exit
- `src/main.py` - Initializes StateManager on app startup, saves on shutdown
- `data/shokedex_state.json` - JSON file storing user state (created on first run)

**Architectural Patterns Applied:**
1. **Manager Singleton Pattern:** StateManager instantiated once in main.py, passed via ScreenManager
2. **Screen Lifecycle Integration:** Use on_enter() to load state, on_exit() to save state
3. **Graceful Degradation:** Corrupted state file → reset to defaults, continue operation
4. **Lazy File Creation:** State file created on first save, not required to exist at startup
5. **Human-Readable Format:** JSON for easy debugging and manual editing if needed

**Constraints:**
- State file must be JSON (not binary) for portability and debugging
- No database for state (separate from Pokédex data in SQLite)
- Save operations must be fast (< 50ms) to avoid impacting navigation
- State file size kept minimal (< 10KB) for fast reads
- No network dependencies (purely local file I/O)

**Integration Points:**
- HomeScreen.on_enter() → StateManager.get_last_viewed_generation()
- DetailScreen.on_exit() → StateManager.set_last_viewed(pokemon_id)
- All screens can call StateManager.get_volume(), set_volume()
- main.py shutdown → StateManager.save_state() for final persistence

## Detailed Design

### Services and Modules

| Module | Responsibility | Inputs | Outputs | Owner |
|--------|---------------|--------|---------|-------|
| **StateManager** | Session state persistence with JSON file I/O | State updates from screens | Persisted state, restored values | Core Team |
| **ScreenManager** | Inject StateManager into all screens | StateManager instance | Access point for screens | UI Team |
| **HomeScreen** | Load last viewed on startup, save on generation switch | StateManager.get_last_viewed() | Restored Pokémon and generation | UI Team |
| **DetailScreen** | Save last viewed Pokémon when exiting | StateManager.set_last_viewed(id, gen) | Updated state | UI Team |
| **main.py** | Initialize StateManager at startup, save on shutdown | Application lifecycle | StateManager singleton | Core Team |

**Key Responsibilities:**

**StateManager:**
- Load state from JSON file on initialization (or create with defaults)
- Provide getter methods for all state values (last_viewed_id, last_generation, volume, input_mode)
- Provide setter methods that update in-memory state
- Save state to JSON file when save_state() called
- Handle JSON parse errors gracefully (corrupt file → use defaults)
- Log all state operations for debugging

**ScreenManager:**
- Hold reference to StateManager singleton
- Pass StateManager to all Screen instances via self.screen_manager.state_manager
- Call state_manager.save_state() on screen transitions if needed

**Screens (HomeScreen, DetailScreen):**
- Access StateManager via self.screen_manager.state_manager
- Call get methods in on_enter() to restore state
- Call set methods when user changes state (view Pokémon, switch generation)
- Rely on on_exit() and app shutdown for persistence (don't manually save)

### Data Models and Contracts

**State File JSON Schema:**

```json
{
  "version": "1.0.0",
  "last_viewed": {
    "pokemon_id": 25,
    "generation": 1
  },
  "preferences": {
    "input_mode": "keyboard",
    "volume": 0.7
  }
}
```

**Field Specifications:**

| Field | Type | Default | Constraints | Description |
|-------|------|---------|-------------|-------------|
| `version` | string | "1.0.0" | Semantic versioning | State file format version |
| `last_viewed.pokemon_id` | int | 1 | 1-386 | National Dex number of last viewed Pokémon |
| `last_viewed.generation` | int | 1 | 1-3 | Generation (1=Kanto, 2=Johto, 3=Hoenn) |
| `preferences.input_mode` | string | "keyboard" | "keyboard" or "gpio" | Current input mode |
| `preferences.volume` | float | 0.7 | 0.0-1.0 | Audio volume (for future audio epic) |

**Default State (First Boot):**

```python
DEFAULT_STATE = {
    "version": "1.0.0",
    "last_viewed": {
        "pokemon_id": 1,      # Bulbasaur
        "generation": 1        # Kanto
    },
    "preferences": {
        "input_mode": "keyboard",
        "volume": 0.7
    }
}
```

**Validation Rules:**

- `pokemon_id`: Must be 1-386, otherwise reset to 1
- `generation`: Must be 1-3, otherwise reset to 1
- `input_mode`: Must be "keyboard" or "gpio", otherwise reset to "keyboard"
- `volume`: Must be 0.0-1.0, otherwise clamp to range
- Missing fields: Populate with defaults, don't fail
- Extra fields: Ignore (forward compatibility)

### APIs and Interfaces

**StateManager Public Interface:**

```python
class StateManager:
    """Manages user session state with JSON file persistence."""
    
    def __init__(self, state_file_path: str = "data/shokedex_state.json"):
        """Initialize StateManager and load state from file.
        
        Args:
            state_file_path: Path to JSON state file
            
        Side Effects:
            - Creates state file with defaults if not exists
            - Loads existing state or resets to defaults if corrupt
            - Logs initialization status
        """
    
    # Last Viewed Pokémon
    def get_last_viewed_id(self) -> int:
        """Get last viewed Pokémon National Dex number.
        
        Returns:
            int: Pokémon ID (1-386)
        """
    
    def get_last_viewed_generation(self) -> int:
        """Get last viewed generation number.
        
        Returns:
            int: Generation (1=Kanto, 2=Johto, 3=Hoenn)
        """
    
    def set_last_viewed(self, pokemon_id: int, generation: int = None) -> None:
        """Update last viewed Pokémon and optionally generation.
        
        Args:
            pokemon_id: National Dex number (1-386)
            generation: Generation number (1-3), or None to auto-detect
            
        Side Effects:
            - Updates in-memory state
            - Does NOT automatically save to file (call save_state())
            - Validates and clamps values to allowed ranges
        """
    
    # Preferences
    def get_input_mode(self) -> str:
        """Get current input mode preference.
        
        Returns:
            str: "keyboard" or "gpio"
        """
    
    def set_input_mode(self, mode: str) -> None:
        """Set input mode preference.
        
        Args:
            mode: "keyboard" or "gpio"
            
        Raises:
            ValueError: If mode not in allowed values
        """
    
    def get_volume(self) -> float:
        """Get audio volume preference.
        
        Returns:
            float: Volume level 0.0-1.0
        """
    
    def set_volume(self, volume: float) -> None:
        """Set audio volume preference.
        
        Args:
            volume: Volume level 0.0-1.0
            
        Side Effects:
            - Clamps to 0.0-1.0 range if outside bounds
        """
    
    # Persistence
    def save_state(self) -> bool:
        """Persist current state to JSON file.
        
        Returns:
            bool: True if saved successfully, False on error
            
        Side Effects:
            - Writes JSON to disk
            - Creates parent directories if needed
            - Logs save operation (success or failure)
        """
    
    def reset_to_defaults(self) -> None:
        """Reset all state to default values.
        
        Side Effects:
            - Clears in-memory state to defaults
            - Does NOT automatically save (call save_state() to persist)
        """
```

**Screen Integration Pattern:**

```python
# In HomeScreen
class HomeScreen(Screen):
    def on_enter(self):
        # Load last viewed state
        pokemon_id = self.screen_manager.state_manager.get_last_viewed_id()
        generation = self.screen_manager.state_manager.get_last_viewed_generation()
        
        # Restore UI to that state
        self._load_generation(generation)
        self._scroll_to_pokemon(pokemon_id)
    
    def on_exit(self):
        # Save state when leaving screen
        self.screen_manager.state_manager.save_state()
    
    def _switch_generation(self, new_gen: int):
        # Update state when user switches generation
        first_pokemon_id = self._get_first_in_generation(new_gen)
        self.screen_manager.state_manager.set_last_viewed(
            pokemon_id=first_pokemon_id,
            generation=new_gen
        )

# In DetailScreen
class DetailScreen(Screen):
    def on_exit(self):
        # Save current Pokémon as last viewed
        self.screen_manager.state_manager.set_last_viewed(
            pokemon_id=self.pokemon_id,
            generation=self._get_generation_for_id(self.pokemon_id)
        )
        self.screen_manager.state_manager.save_state()
```

**Application Lifecycle Integration:**

```python
# In main.py
def main():
    # Initialize StateManager first
    state_manager = StateManager()
    
    # Create other managers
    input_manager = InputManager()
    
    # Create ScreenManager with StateManager
    screen_manager = ScreenManager(
        database=db,
        state_manager=state_manager,
        input_manager=input_manager
    )
    
    # Main loop...
    try:
        while running:
            # Game loop
            pass
    finally:
        # Save state on shutdown
        state_manager.save_state()
        logging.info("Application shutdown - state saved")
```

### Workflows and Sequencing

**First Boot Workflow:**

```
1. Application starts (main.py)
2. StateManager.__init__() called
   ├─> Check if data/shokedex_state.json exists
   ├─> File NOT found (first boot)
   ├─> Create DEFAULT_STATE in memory
   ├─> Call save_state() to create file
   └─> Log: "State file created with defaults"
3. ScreenManager initialized with StateManager
4. HomeScreen created and pushed
5. HomeScreen.on_enter() called
   ├─> get_last_viewed_id() → returns 1 (Bulbasaur)
   ├─> get_last_viewed_generation() → returns 1 (Kanto)
   └─> Display Bulbasaur in Kanto generation view
6. User sees Bulbasaur on first boot (expected default)
```

**Subsequent Boot Workflow (Normal Operation):**

```
1. Application starts
2. StateManager.__init__() called
   ├─> Load data/shokedex_state.json
   ├─> Parse JSON successfully
   ├─> Validate fields (pokemon_id, generation, etc.)
   ├─> Store in memory
   └─> Log: "State loaded: Pokemon #25, Generation 1"
3. ScreenManager initialized with StateManager
4. HomeScreen created and pushed
5. HomeScreen.on_enter() called
   ├─> get_last_viewed_id() → returns 25 (Pikachu)
   ├─> get_last_viewed_generation() → returns 1 (Kanto)
   ├─> Load Kanto generation Pokémon list
   ├─> Scroll to Pikachu (#25) in list
   └─> Display Pikachu sprite and info
6. User sees Pikachu (last viewed from previous session)
```

**State Update Workflow (User Browses):**

```
1. User on HomeScreen (Kanto, Pikachu #25)
2. User presses R button to switch to Johto
3. HomeScreen._switch_generation(2) called
   ├─> Calculate first Pokémon in Johto (Chikorita #152)
   ├─> Call state_manager.set_last_viewed(152, 2)
   │   ├─> Update in-memory state
   │   └─> Do NOT save yet (wait for exit)
   ├─> Load Johto Pokémon list
   └─> Display Chikorita
4. User presses A to view Chikorita details
5. DetailScreen(152) created and pushed
6. HomeScreen.on_exit() called
   └─> Call state_manager.save_state()
       ├─> Write JSON to disk
       └─> Log: "State saved: Pokemon #152, Generation 2"
7. DetailScreen displays Chikorita details
8. User powers off device
9. Application shutdown (finally block in main.py)
   └─> state_manager.save_state() (redundant but safe)
```

**Corrupted State File Workflow:**

```
1. Application starts
2. StateManager.__init__() called
   ├─> Attempt to load data/shokedex_state.json
   ├─> JSON parse fails (corrupted file)
   ├─> Catch exception
   ├─> Log: "ERROR: State file corrupted, resetting to defaults"
   ├─> Load DEFAULT_STATE in memory
   ├─> Call save_state() to overwrite corrupt file
   └─> Log: "State file reset successfully"
3. Application continues normally
4. User sees Bulbasaur (default) instead of crash
```

**State Save Timing Decision Tree:**

```
When to call save_state()?

1. Screen.on_exit() → YES
   - Saves state when navigating between screens
   - Ensures no data loss on normal navigation
   - Low frequency (only on screen changes)

2. Application shutdown → YES
   - Final safety save in case on_exit() missed
   - Handled in finally block

3. After every setter call (set_last_viewed, etc.) → NO
   - Too frequent, impacts performance
   - Unnecessary writes to SD card
   - State still in memory, safe until next save point

4. On timer (auto-save every N seconds) → NO
   - Adds complexity
   - Unnecessary for this use case
   - on_exit() is sufficient

5. On power loss → IMPOSSIBLE
   - Can't detect, rely on frequent saves
   - on_exit() provides good coverage
```

## Non-Functional Requirements

### Performance

**NFR-P1: Fast Startup**
- Application boots and displays HomeScreen within 5 seconds
- State file load time < 50ms (JSON parse + validation)
- State file kept under 1KB for fast I/O on SD card

**NFR-P2: Non-Blocking Saves**
- save_state() completes in < 50ms
- No perceptible lag when navigating between screens
- State saves do not impact frame rate (30+ FPS maintained)

**NFR-P3: Memory Efficiency**
- StateManager in-memory footprint < 10KB
- No memory leaks from repeated save operations
- JSON file size does not grow unbounded over time

**Performance Validation:**
- Profile startup time on Raspberry Pi 3B+ hardware
- Measure save_state() duration under normal operation
- Test with 1000 save cycles to verify no memory growth

### Security

**SQL Injection Prevention:**
- N/A - StateManager does not use SQL queries
- All data stored in JSON file with validated structure

**File Path Safety:**
- State file path is fixed constant: `data/shokedex_state.json`
- No user-provided paths accepted
- Parent directory created if not exists (safe operation)

**Data Validation:**
- All loaded values validated against allowed ranges
- Invalid values clamped or reset to defaults
- Malicious JSON values cannot cause crashes

**No Sensitive Data:**
- State file contains only Pokédex browsing data
- No passwords, tokens, or personal information
- File readable by any user (no encryption needed)

### Reliability/Availability

**Corruption Recovery:**
- JSON parse errors handled gracefully
- Corrupt state file overwritten with defaults
- Application continues operation (no crash)
- User sees default state (Bulbasaur) on recovery

**Power Loss Resilience:**
- State saved on screen transitions (frequent enough for good coverage)
- Final save on shutdown (best-effort if clean shutdown)
- Worst case: lose last screen's changes (acceptable trade-off)

**File System Errors:**
- If save fails (disk full, permissions), log error but continue
- Application remains functional even if saves failing
- User experience degraded but not broken

**State Consistency:**
- In-memory state always valid (validated on load, validated on set)
- Atomic file write using temp file + rename pattern
- No partial writes that corrupt state

### Observability

**Logging Requirements:**

```python
logging.info("StateManager initialized")
logging.info(f"State loaded: Pokemon #{pokemon_id}, Generation {gen}")
logging.info(f"State updated: Pokemon #{pokemon_id}, Generation {gen}")
logging.info(f"State saved successfully to {file_path}")
logging.warning(f"State file corrupted, resetting to defaults")
logging.warning(f"Invalid pokemon_id {id}, clamping to range 1-386")
logging.error(f"Failed to save state: {error}")
logging.error(f"Failed to create state directory: {error}")
```

**Debug Information:**
- Log state file path on initialization
- Log full state contents at DEBUG level
- Log save duration for performance monitoring
- Log validation failures with details

**Metrics to Track:**
- State file size over time (should remain < 1KB)
- Save operation duration (target < 50ms)
- Number of corruption recoveries (should be rare)
- Number of successful saves per session

## Dependencies and Integrations

**Python Dependencies:**
- `json` (stdlib) - JSON serialization/deserialization
- `pathlib` (stdlib) - File path operations
- `logging` (stdlib) - Error and operation logging
- No external packages required

**Internal Module Dependencies:**
- `src/ui/screen_manager.py` - Holds StateManager reference, passes to screens
- `src/ui/screen.py` - Base Screen class provides lifecycle hooks (on_enter, on_exit)
- `src/ui/home_screen.py` - Loads last viewed on startup, saves on generation switch
- `src/ui/detail_screen.py` - Saves last viewed Pokémon on exit
- `src/main.py` - Initializes StateManager, saves on shutdown

**File System Dependencies:**
- `data/` directory must be writable (created if not exists)
- `data/shokedex_state.json` file (created on first run)
- SD card with sufficient write cycles (minimal concern, infrequent saves)

**Integration Points:**
- **main.py startup**: Create StateManager before ScreenManager
- **ScreenManager.__init__()**: Store StateManager reference, pass to screens
- **HomeScreen.on_enter()**: Load last viewed state to restore UI
- **HomeScreen.on_exit()**: Save state when navigating away
- **DetailScreen.on_exit()**: Update last viewed, save state
- **main.py shutdown**: Final save in finally block

**Integration Sequence:**

```
main.py
  ├─> StateManager() created
  ├─> ScreenManager(state_manager=state_manager) created
  ├─> HomeScreen(screen_manager) created
  │     ├─> screen_manager.state_manager accessible
  │     └─> on_enter() calls get_last_viewed_*()
  ├─> DetailScreen(screen_manager, pokemon_id) created
  │     ├─> screen_manager.state_manager accessible
  │     └─> on_exit() calls set_last_viewed() + save_state()
  └─> Shutdown: state_manager.save_state()
```

**No External Integrations:**
- No network calls (offline-first)
- No database for state (separate from Pokédex data)
- No third-party state libraries

## Acceptance Criteria (Authoritative)

**AC #1: First Boot Defaults**
- On first application launch, state file created at `data/shokedex_state.json`
- File contains valid JSON with default values
- Default pokemon_id = 1 (Bulbasaur), generation = 1 (Kanto)
- Default input_mode = "keyboard", volume = 0.7
- HomeScreen displays Bulbasaur on first boot

**AC #2: Last Viewed Pokémon Persistence**
- User views Pikachu (#25) in Kanto, then exits application
- On restart, HomeScreen displays Pikachu (#25) in Kanto generation
- User switches to Johto, views Chikorita (#152), exits
- On restart, HomeScreen displays Chikorita (#152) in Johto generation
- Pokémon ID persists correctly across power cycles

**AC #3: Generation Persistence**
- User switches from Kanto to Johto, exits application
- On restart, HomeScreen shows Johto generation (not Kanto)
- Generation indicator badge shows "JOHTO"
- First Pokémon of Johto generation displayed

**AC #4: Boot to HomeScreen Always**
- User navigates to DetailScreen showing Raichu, powers off
- On restart, boots to HomeScreen (not DetailScreen)
- HomeScreen shows Raichu selected (last viewed)
- User can press A to return to DetailScreen if desired
- Never boots directly into DetailScreen

**AC #5: Volume Preference Persistence**
- User sets volume to 0.5, exits application
- On restart, volume preference retrieved as 0.5
- StateManager.get_volume() returns 0.5
- (Audio playback will use this in future audio epic)

**AC #6: Input Mode Persistence**
- User's input mode set to "gpio", exits application
- On restart, input mode retrieved as "gpio"
- StateManager.get_input_mode() returns "gpio"
- InputManager can use this to configure controls

**AC #7: State File Corruption Recovery**
- State file manually corrupted (invalid JSON)
- Application starts without crashing
- Defaults loaded (Bulbasaur, Kanto, keyboard, 0.7 volume)
- Corrupt file overwritten with valid defaults
- Log warning about corruption and recovery

**AC #8: Fast Startup Performance**
- Application boots from power-on to HomeScreen in < 5 seconds
- State file load time < 50ms (measured on Raspberry Pi)
- No perceptible delay from state loading

**AC #9: Non-Blocking Save Performance**
- save_state() completes in < 50ms
- Screen transitions feel instant (no lag from saving)
- Frame rate remains 30+ FPS during save operations

**AC #10: State Save on Screen Transitions**
- User navigates HomeScreen → DetailScreen
- HomeScreen.on_exit() saves state automatically
- No manual save button required
- State file updated with current pokemon_id and generation

**AC #11: State Save on Application Shutdown**
- User quits application (clean shutdown)
- finally block in main.py executes
- state_manager.save_state() called
- State file written with latest values

**AC #12: Validation and Clamping**
- Invalid pokemon_id (e.g., 999) loaded from corrupted state
- StateManager clamps to valid range (1-386)
- Invalid generation (e.g., 5) clamped to 1-3
- Invalid volume (e.g., 1.5) clamped to 0.0-1.0
- Application continues with valid clamped values

## Traceability Mapping

| AC | Spec Section(s) | Component(s)/API(s) | Test Idea |
|----|-----------------|---------------------|-----------|
| **AC #1** | Data Models → Default State | StateManager.__init__(), DEFAULT_STATE | Unit test: Delete state file, init StateManager, verify defaults |
| **AC #2** | Workflows → Subsequent Boot | get_last_viewed_id(), set_last_viewed() | Integration test: Set Pikachu, restart app, verify HomeScreen shows Pikachu |
| **AC #3** | Workflows → State Update | get_last_viewed_generation(), set_last_viewed() | Integration test: Switch to Johto, restart, verify Johto shown |
| **AC #4** | Boot Behavior Decision | HomeScreen.on_enter(), main.py startup | Integration test: Exit from DetailScreen, restart, verify HomeScreen appears |
| **AC #5** | APIs → Volume Methods | get_volume(), set_volume() | Unit test: Set volume 0.5, save, reload, verify 0.5 |
| **AC #6** | APIs → Input Mode Methods | get_input_mode(), set_input_mode() | Unit test: Set GPIO, save, reload, verify "gpio" |
| **AC #7** | Workflows → Corrupted File | __init__() exception handling | Integration test: Corrupt JSON, start app, verify defaults + no crash |
| **AC #8** | NFR Performance → Startup | StateManager.__init__() timing | Performance test: Measure boot time with state load |
| **AC #9** | NFR Performance → Save | save_state() timing | Performance test: Measure save duration, verify < 50ms |
| **AC #10** | Workflows → Save Timing | Screen.on_exit(), save_state() | Integration test: Navigate screens, verify file updated |
| **AC #11** | Integration → Shutdown | main.py finally block | Integration test: Normal quit, verify final save occurred |
| **AC #12** | Data Models → Validation | Field validation logic | Unit test: Load invalid values, verify clamping |

## Risks, Assumptions, Open Questions

**Risks:**

1. **SD Card Write Failures** (Low Impact, Medium Probability)
   - Risk: Raspberry Pi SD cards can fail or become read-only over time
   - Mitigation: Log save errors but continue operation, test with aged SD cards
   - Fallback: Application works fine without persistence, just resets each boot

2. **Rapid Save Frequency** (Medium Impact, Low Probability)
   - Risk: User rapidly switches screens, causing excessive saves to SD card
   - Mitigation: save_state() optimized to < 50ms, saves only on screen exit (not every action)
   - Monitor: Track save frequency in logs, optimize if excessive

3. **State File Size Growth** (Low Impact, Low Probability)
   - Risk: Future features (favorites, history) could grow state file
   - Mitigation: MVP keeps state minimal (< 1KB), monitor size in tests
   - Deferred: Favorites/history moved to post-MVP epic

**Assumptions:**

- ✅ `data/` directory is writable on Raspberry Pi
- ✅ JSON file I/O is fast enough on SD card (< 50ms)
- ✅ Python `json` module handles UTF-8 Pokémon names correctly
- ✅ File system supports atomic rename for safe writes
- ✅ Screen lifecycle methods (on_enter, on_exit) are reliably called
- ✅ Application shutdown is usually clean (not forced power-off)

**Open Questions:**

1. **Q:** Should we use temp file + rename for atomic writes?
   - **A:** Yes - write to `.shokedex_state.json.tmp`, then rename to avoid partial writes

2. **Q:** What if user forces power-off (no clean shutdown)?
   - **A:** Acceptable - we save on screen transitions, so worst case is losing last screen's changes

3. **Q:** Should we backup old state file before overwriting?
   - **A:** Not in MVP - adds complexity, state is not critical data, can always reset to defaults

4. **Q:** Do we need state file versioning for future changes?
   - **A:** Yes - `version` field in JSON allows migration logic later if schema changes

**Next Steps / Blockers:**

- ✅ **Ready:** StateManager class exists per architecture (needs integration updates)
- ✅ **Ready:** Screen lifecycle hooks available (on_enter, on_exit)
- ✅ **Ready:** ScreenManager can hold StateManager reference
- ⚠️ **Action Required:** Update main.py to initialize StateManager and pass to ScreenManager
- ⚠️ **Action Required:** Update HomeScreen to use get_last_viewed_*() on startup
- ⚠️ **Action Required:** Update DetailScreen to call set_last_viewed() on exit

**Post-MVP Epic Planning:**

Create separate epic "User Preferences & History" for:
- Recent Pokémon history tracking (last 10 viewed)
- Favorites list with toggle UI in DetailScreen
- Usage statistics (total views, unique Pokémon, sessions)
- Recent history display screen
- Favorites filter on HomeScreen

## Test Strategy Summary

**Test Levels:**

**1. Unit Tests**

- `test_state_manager.py`:
  - `test_init_creates_default_state()` - First run creates file with defaults
  - `test_init_loads_existing_state()` - Subsequent runs load existing file
  - `test_get_last_viewed_id()` - Returns correct Pokémon ID
  - `test_get_last_viewed_generation()` - Returns correct generation
  - `test_set_last_viewed_updates_state()` - Updates in-memory state
  - `test_save_state_writes_json()` - Writes valid JSON to file
  - `test_corrupted_json_recovery()` - Invalid JSON loads defaults
  - `test_invalid_pokemon_id_clamping()` - Out-of-range IDs clamped to 1-386
  - `test_invalid_generation_clamping()` - Out-of-range gen clamped to 1-3
  - `test_invalid_volume_clamping()` - Out-of-range volume clamped to 0.0-1.0
  - `test_get_volume()` - Returns volume preference
  - `test_set_volume()` - Updates volume
  - `test_get_input_mode()` - Returns input mode
  - `test_set_input_mode()` - Updates input mode with validation
  - `test_reset_to_defaults()` - Resets all fields to default values

**2. Integration Tests**

- `test_state_integration.py`:
  - `test_first_boot_shows_bulbasaur()` - App starts with Bulbasaur on first run
  - `test_last_viewed_persists_across_restart()` - View Pikachu, restart, verify Pikachu shown
  - `test_generation_persists_across_restart()` - Switch to Johto, restart, verify Johto shown
  - `test_boot_to_homescreen_after_detailscreen()` - Exit from DetailScreen, restart boots to HomeScreen
  - `test_state_saves_on_screen_transition()` - Navigate screens, verify file updated
  - `test_state_saves_on_app_shutdown()` - Normal quit, verify final save
  - `test_homescreen_restores_last_pokemon()` - HomeScreen.on_enter() loads correct Pokémon
  - `test_detailscreen_saves_on_exit()` - DetailScreen.on_exit() updates state

**3. Performance Tests**

- `test_state_performance.py`:
  - `test_startup_time_with_state_load()` - Measure boot time < 5 seconds
  - `test_state_load_duration()` - Measure JSON load < 50ms
  - `test_save_state_duration()` - Measure save < 50ms
  - `test_repeated_saves_no_memory_leak()` - Save 1000 times, verify no memory growth
  - `test_state_file_size_remains_small()` - Verify file < 1KB

**4. Manual/Hardware Tests**

- Test on actual Raspberry Pi 3B+ with SD card
- Power-off during various operations, verify recovery
- Manually corrupt state file, verify graceful recovery
- Test with aged/slow SD cards for I/O performance
- Verify boot time on hardware meets < 5 second target

**Edge Cases:**

- State file deleted mid-session (recreate with defaults)
- State file read-only permissions (log error, use in-memory state)
- Disk full during save (log error, continue with old state)
- Invalid JSON (missing braces, wrong types, etc.)
- Extra fields in JSON (forward compatibility - ignore extras)
- Missing required fields (use defaults for missing fields)
- Pokémon ID = 0 or 387 (clamp to 1-386)
- Generation = 0 or 4 (clamp to 1-3)
- Volume = -1.0 or 2.0 (clamp to 0.0-1.0)
- Input mode = "touch" (invalid, reset to "keyboard")
- Rapid screen navigation (multiple saves in quick succession)

**Coverage Goals:**

- Unit test coverage: 95%+ for StateManager
- Integration test coverage: All AC scenarios validated
- Performance test: All NFR-P metrics verified on Pi hardware
- Error handling: All corruption/failure scenarios tested

**Test Data:**

- Default state (Bulbasaur #1, Kanto)
- Mid-range Pokémon (Pikachu #25, Kanto)
- Boundary Pokémon (Mew #151, Chikorita #152, Deoxys #386)
- Invalid values (0, 387, negative, null)
- Corrupted JSON samples (malformed, missing fields, wrong types)

**Acceptance Test Mapping:**

- AC #1 → Unit test for first boot defaults
- AC #2 → Integration test for last viewed persistence
- AC #3 → Integration test for generation persistence
- AC #4 → Integration test for boot to HomeScreen
- AC #5-6 → Unit tests for preference persistence
- AC #7 → Integration test for corruption recovery
- AC #8-9 → Performance tests for startup and save
- AC #10-11 → Integration tests for save timing
- AC #12 → Unit tests for validation and clamping
