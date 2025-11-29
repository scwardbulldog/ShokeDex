# Story 4.3: Boot to HomeScreen Behavior

Status: done

## Story

As a user,
I want the device to always boot to the browse screen,
So that I have a consistent starting point.

## Acceptance Criteria

1. **Boot Destination is Always HomeScreen (AC #1)**
   - **Given** the application starts up (fresh boot or restart)
   - **When** the screen stack initializes
   - **Then** the application boots to HomeScreen (not DetailScreen or any other screen)
   - **And** HomeScreen is the first and only screen on the screen stack

2. **Last Viewed Pokemon Displayed on Boot (AC #2)**
   - **Given** a user was viewing Raichu (#26) on DetailScreen before powering off
   - **When** the application restarts
   - **Then** HomeScreen shows Raichu (#26) as the selected/highlighted Pokémon
   - **And** the Pokémon sprite and info for Raichu are visible
   - **And** the generation badge shows the correct generation (Kanto for #26)

3. **State Preserved When Exiting DetailScreen (AC #3)**
   - **Given** a user is viewing DetailScreen showing Treecko (#252)
   - **When** the user powers off the device (or quits app)
   - **Then** StateManager saves pokemon_id=252 and generation=3 to state file
   - **And** the next boot displays Treecko (#252) on HomeScreen

4. **User Can Navigate Back to DetailScreen (AC #4)**
   - **Given** the application has booted to HomeScreen with last viewed Pokémon selected
   - **When** the user presses the A button
   - **Then** DetailScreen opens for the selected Pokémon
   - **And** the transition is seamless (no additional button presses needed)

5. **Consistent Boot Behavior Regardless of Exit Point (AC #5)**
   - **Given** various exit scenarios:
     - User exits from HomeScreen
     - User exits from DetailScreen
     - Application crashes unexpectedly
     - Power loss during operation
   - **When** the application restarts
   - **Then** the device always boots to HomeScreen
   - **And** the last successfully saved Pokémon is displayed

6. **ScreenManager Initialization Verification (AC #6)**
   - **Given** the main.py application entry point executes
   - **When** ScreenManager is initialized
   - **Then** HomeScreen is pushed as the initial screen
   - **And** no other screens are pre-loaded or pushed automatically
   - **And** the screen stack depth is exactly 1

## Tasks / Subtasks

- [x] **Task 1: Verify main.py Boot Sequence (AC #1, #6)**
  - [x] 1.1: Review `src/main.py` startup logic to confirm HomeScreen is always the first screen
  - [x] 1.2: Verify ScreenManager.push() is called with HomeScreen class only at startup
  - [x] 1.3: Confirm no conditional logic that could push DetailScreen on boot
  - [x] 1.4: Add debug logging for boot sequence ("Booting to HomeScreen with Pokémon #{pokemon_id}")

- [x] **Task 2: Verify HomeScreen State Restoration (AC #2)**
  - [x] 2.1: Confirm HomeScreen.on_enter() retrieves last viewed Pokémon from StateManager
  - [x] 2.2: Verify HomeScreen scrolls/highlights the correct Pokémon in the list
  - [x] 2.3: Verify generation badge displays correct region for restored Pokémon
  - [x] 2.4: Test restoration with Pokémon from all three generations (Kanto, Johto, Hoenn)

- [x] **Task 3: Verify DetailScreen State Persistence on Exit (AC #3)**
  - [x] 3.1: Confirm DetailScreen.on_exit() calls `state_manager.set_last_viewed(self.pokemon_id)`
  - [x] 3.2: Verify DetailScreen.on_exit() triggers state file save (directly or via ScreenManager)
  - [x] 3.3: Test that navigating back from DetailScreen preserves the Pokémon state
  - [x] 3.4: Test that application quit from DetailScreen saves current Pokémon state

- [x] **Task 4: Verify A Button Navigation to DetailScreen (AC #4)**
  - [x] 4.1: Confirm HomeScreen handles A button (SELECT action) to push DetailScreen
  - [x] 4.2: Verify DetailScreen receives correct pokemon_id from HomeScreen selection
  - [x] 4.3: Test round-trip: HomeScreen → DetailScreen → HomeScreen maintains selection

- [x] **Task 5: Write Integration Tests for Boot Behavior (AC #1, #2, #5)**
  - [x] 5.1: Test `test_always_boots_to_homescreen()` - verify initial screen is HomeScreen
  - [x] 5.2: Test `test_boots_to_homescreen_not_detailscreen()` - verify DetailScreen state doesn't change boot target
  - [x] 5.3: Test `test_last_viewed_displayed_on_boot()` - set state, boot, verify displayed Pokémon
  - [x] 5.4: Test `test_generation_restored_correctly_on_boot()` - verify badge matches restored state
  - [x] 5.5: Test `test_all_generations_restore_on_boot()` - test Kanto, Johto, Hoenn restoration

- [x] **Task 6: Write Integration Tests for Exit-to-Boot Cycle (AC #3, #5)**
  - [x] 6.1: Test `test_detailscreen_exit_saves_state()` - view DetailScreen, exit, verify state saved
  - [x] 6.2: Test `test_homescreen_exit_preserves_state()` - navigate HomeScreen, exit, verify state
  - [x] 6.3: Test `test_boot_after_detailscreen_exit()` - exit from DetailScreen, boot, verify HomeScreen shows correct Pokémon

- [x] **Task 7: Write Unit Tests for ScreenManager Initialization (AC #6)**
  - [x] 7.1: Test `test_screen_stack_starts_with_homescreen()` - verify initial stack
  - [x] 7.2: Test `test_screen_stack_depth_is_one_on_boot()` - verify only one screen
  - [x] 7.3: Test `test_no_automatic_screen_transitions_on_boot()` - verify HomeScreen is stable

## Dev Notes

### Architectural Decision: Always Boot to HomeScreen

Per the architecture.md and tech-spec-epic-3-state-persistence.md:

> "This design decision ensures predictable boot behavior."
> "Device powers on to HomeScreen showing last viewed Pokémon within 5 seconds."

The device ALWAYS boots to HomeScreen regardless of where the user was when they exited. This provides:
1. **Predictable UX**: Users always know where they'll start
2. **Simpler Recovery**: No need to handle restoring arbitrary screen states
3. **Quick Access**: One A button press returns to DetailScreen if desired

### main.py Boot Sequence

The boot sequence in `src/main.py` should follow this pattern:

```python
def main():
    # 1. Initialize managers
    state_manager = StateManager()
    # ... other managers ...
    
    # 2. Create ScreenManager with managers
    screen_manager = ScreenManager(...)
    
    # 3. ALWAYS push HomeScreen as initial screen
    screen_manager.push(HomeScreen)
    
    # 4. Enter main loop
    running = True
    while running:
        # Process events, render, etc.
```

### State Flow: DetailScreen → Boot → HomeScreen

```
1. User views Raichu (#26) on DetailScreen
2. User powers off device
   └─> DetailScreen.on_exit() called
       └─> state_manager.set_last_viewed(26, 1)  # Raichu, Kanto
       └─> state_manager.save_state()
3. Device powers on
   └─> main.py starts
       └─> StateManager loads state: pokemon_id=26, generation=1
       └─> ScreenManager.push(HomeScreen)
4. HomeScreen.on_enter() executes
   └─> Calls get_last_viewed_id() → 26
   └─> Calls get_last_viewed_generation() → 1
   └─> Loads Kanto Pokémon list
   └─> Scrolls to and highlights Raichu (#26)
5. User sees HomeScreen with Raichu selected
6. User presses A button → DetailScreen for Raichu opens
```

### Project Structure Notes

**Files to Verify/Modify:**
- `src/main.py` - Boot sequence, ScreenManager initialization
- `src/ui/screen_manager.py` - push() logic, initial screen handling
- `src/ui/home_screen.py` - on_enter() state restoration (verified in 4.1, 4.2)
- `src/ui/detail_screen.py` - on_exit() state save (implement if not present)

**Test Files:**
- `tests/test_home_screen.py` - Add TestBootBehavior class
- `tests/test_screen_manager.py` - Test initial stack state (create if needed)

### Learnings from Previous Story

**From Story 4.2: Last Viewed Pokémon Persistence (Status: ready-for-dev)**

While Story 4.2 is ready-for-dev (not yet implemented), the drafted story provides important context:

- **State Update Points**: HomeScreen.on_exit(), DetailScreen.on_exit(), navigation handlers
- **Integration Verified in 4.1**: HomeScreen.on_enter() correctly calls get_last_viewed_*() methods
- **Test Patterns**: Use temporary directories with `tempfile.mkdtemp()` for isolation
- **StateManager API**: `set_last_viewed(pokemon_id, generation)`, `save_state()`, `get_last_viewed_id()`, `get_last_viewed_generation()`

**From Story 4.1: First Boot State Initialization (Status: done)**

- **`_persist_default_state()` Method**: Ensures state file exists on first boot
- **HomeScreen Integration Verified**: `on_enter()` correctly restores state at lines 335-339
- **Atomic Write Pattern**: Save operations use temp file + rename for safety
- **Test Classes to Extend**:
  - `TestFirstBootHomeScreen` in `tests/test_home_screen.py` - follow this pattern
  - `TestFirstBootStateInitialization` in `tests/test_state_manager.py`

**Files Created/Modified in Story 4.1:**
- `src/state_manager.py` - Added `_persist_default_state()`, updated `_load_state()`
- `tests/test_state_manager.py` - Added TestFirstBootStateInitialization, TestDirectoryCreation
- `tests/test_home_screen.py` - Added TestFirstBootHomeScreen class

[Source: docs/sprint-artifacts/4-1-first-boot-state-initialization.md#Dev-Agent-Record]
[Source: docs/sprint-artifacts/4-2-last-viewed-pokemon-persistence.md#Learnings-from-Previous-Story]

### Testing Strategy

Per project testing standards:
- Use temporary state file paths (not production `data/shokedex_state.json`)
- Clean up state files in tearDown()
- Use pytest fixtures for StateManager and ScreenManager instances
- Mock pygame where needed for screen tests
- Focus on integration tests that verify the boot sequence end-to-end

### Performance Considerations

- Boot time target: < 5 seconds from power-on to HomeScreen displayed
- State load time: < 50ms (established in previous stories)
- HomeScreen render time: < 33ms per frame (30+ FPS target)

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-3-state-persistence.md#Workflows-and-Sequencing] - Boot workflow
- [Source: docs/sprint-artifacts/tech-spec-epic-3-state-persistence.md#Success-Criteria] - Boot to HomeScreen within 5 seconds
- [Source: docs/epics.md#Story-4.3] - Story definition
- [Source: docs/architecture.md#Manager-Architecture-Pattern] - StateManager integration pattern
- [Source: docs/architecture.md#Project-Structure] - Screen structure and main.py
- [Source: src/main.py] - Application entry point
- [Source: src/ui/screen_manager.py] - Screen stack management

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2025-11-29 | Story drafted from Epic 4 tech spec and epics.md | SM Agent (Bob) |

## Dev Agent Record

### Context Reference

- docs/sprint-artifacts/4-3-boot-to-homescreen-behavior.context.xml

### Agent Model Used

<!-- Will be filled by dev agent -->

### Debug Log References

### Completion Notes List

### File List
