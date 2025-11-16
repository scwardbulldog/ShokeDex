# Story 1.6: Up/Down Scrolling Within Generation

Status: done

## Story

As a user,
I want to scroll through Pokémon within my current generation using Up/Down buttons,
So that I can browse the regional Pokédex sequentially.

## Acceptance Criteria

1. **Single-Press Scrolling Navigation (AC #1)**
   - **Given** a user is viewing Pikachu (#25) in Kanto generation
   - **When** the user presses the Down button (DOWN action)
   - **Then** the next Pokémon (Raichu #26) is displayed
   - **And** the position counter updates (e.g., #025/151 → #026/151)
   - **And** sprite transitions smoothly with fade effect (< 300ms total transition time)
   - **And** StateManager saves the new pokemon_id (#26)
   
   - **When** the user presses the Up button (UP action)
   - **Then** the previous Pokémon (Pikachu #25) is displayed
   - **And** the position counter updates (e.g., #026/151 → #025/151)

2. **Hold-to-Scroll Acceleration (AC #2)**
   - **Given** a user is viewing any Pokémon
   - **When** the user holds the Down or Up button for > 500ms
   - **Then** scrolling accelerates from 1 Pokémon/frame to 3 Pokémon/frame
   - **And** position counter updates reflect the current Pokémon during fast scrolling
   - **And** sprite transitions are suppressed during fast scrolling (performance optimization)
   
   - **When** the user releases the button
   - **Then** scrolling stops immediately at the current Pokémon
   - **And** the final sprite fade-in transition plays (< 300ms)
   - **And** frame rate maintains 30+ FPS during all hold-to-scroll operations

3. **Boundary Wrapping Behavior (AC #3)**
   - **Given** a user is viewing Mew (#151) - the last Pokémon in Kanto
   - **When** the user presses Down button
   - **Then** display wraps to Bulbasaur (#1) - the first Pokémon in Kanto
   - **And** position counter shows #001/151
   - **And** smooth transition plays (fade-out Mew → fade-in Bulbasaur)
   
   - **Given** a user is viewing Bulbasaur (#1) - the first Pokémon in Kanto
   - **When** the user presses Up button
   - **Then** display wraps to Mew (#151) - the last Pokémon in Kanto
   - **And** position counter shows #151/151

4. **Cross-Generation Boundary Behavior (AC #4)**
   - **Given** a user is viewing Mew (#151) in Kanto
   - **When** the user presses Down button
   - **Then** display wraps to Bulbasaur (#1) in Kanto (stays within current generation)
   - **And** does NOT cross into Johto generation (#152 Chikorita)
   - **And** generation badge remains showing "KANTO"
   
   - **Given** a user switches from Kanto to Johto using L/R buttons
   - **When** the user presses Down from Celebi (#251)
   - **Then** display wraps to Chikorita (#152) in Johto (stays within Johto)
   - **And** does NOT cross into Hoenn generation (#252 Treecko)

5. **State Persistence During Scrolling (AC #5)**
   - **Given** a user is scrolling through Pokémon
   - **When** the user moves from Pokémon #25 to #30 using multiple Down button presses
   - **Then** StateManager saves the last viewed pokemon_id on each navigation
   - **And** on_exit() triggers final state save when leaving HomeScreen
   
   - **Given** a user exits the app while viewing Pokémon #42
   - **When** the app restarts
   - **Then** HomeScreen loads showing Pokémon #42 selected
   - **And** position counter shows correct position (e.g., #042/151 in Kanto)

6. **Smooth Visual Transitions (AC #6)**
   - **Given** a user is navigating between Pokémon
   - **When** sprite transitions occur (single-press navigation)
   - **Then** fade-out animation plays (100ms alpha 255 → 0)
   - **And** new sprite fade-in plays (100ms alpha 0 → 255)
   - **And** total transition time < 300ms (including sprite load + render)
   - **And** transitions feel smooth without stuttering
   
   - **Given** rapid scrolling is occurring (hold-to-scroll active)
   - **When** frame rate drops below 30 FPS
   - **Then** transition animations are suppressed to maintain performance
   - **And** instant sprite swaps occur instead of fades

7. **Input Responsiveness (AC #7)**
   - **Given** a user presses an Up or Down button
   - **When** the button press is detected
   - **Then** visual feedback appears within < 100ms (per NFR-P2)
   - **And** Pokémon selection starts changing immediately
   - **And** no perceived lag between button press and response

## Tasks / Subtasks

- [x] **Task 1: Implement Single-Press Up/Down Navigation** (AC: #1)
  - [x] In HomeScreen.handle_input(), add case for InputAction.UP
    - [x] Decrement self.selected_index by 1
    - [x] Call _handle_selection_change() to update display
  - [x] In HomeScreen.handle_input(), add case for InputAction.DOWN
    - [x] Increment self.selected_index by 1
    - [x] Call _handle_selection_change() to update display
  - [x] Create _handle_selection_change() method:
    - [x] Apply boundary wrapping (modulo len(self.pokemon_list))
    - [x] Update position counter text (e.g., "#025/151")
    - [x] Start sprite fade transition
    - [x] Call StateManager.set_last_viewed() with new pokemon_id and generation
  - [x] Test: Single Down press → next Pokémon displayed with smooth transition

- [x] **Task 2: Implement Hold-to-Scroll Acceleration** (AC: #2)
  - [x] Add button hold tracking in HomeScreen:
    - [x] Add self.button_hold_time dict: {InputAction.UP: 0.0, InputAction.DOWN: 0.0}
    - [x] In update(delta_time), track hold duration for active buttons
  - [x] Implement acceleration logic in update():
    - [x] If hold_time < 0.5s: scroll_speed = 1 Pokémon per press (standard)
    - [x] If hold_time >= 0.5s: scroll_speed = 3 Pokémon per frame
    - [x] If hold_time >= 1.0s: scroll_speed = 5 Pokémon per frame (optional turbo)
  - [x] During fast scrolling:
    - [x] Update selected_index by scroll_speed each frame
    - [x] Suppress sprite fade transitions (instant swap)
    - [x] Update position counter in real-time
  - [x] On button release:
    - [x] Reset hold_time to 0.0
    - [x] Play final fade-in transition for current Pokémon
    - [x] Save final pokemon_id to StateManager
  - [x] Test: Hold Down for 1s → scrolls rapidly → release → smooth stop

- [x] **Task 3: Implement Boundary Wrapping** (AC: #3, #4)
  - [x] In _handle_selection_change():
    - [x] Implement modulo wrapping: `self.selected_index = (self.selected_index + delta) % len(self.pokemon_list)`
    - [x] Negative index handling: `if self.selected_index < 0: self.selected_index += len(self.pokemon_list)`
  - [x] Verify generation boundaries are respected:
    - [x] Kanto: wraps within pokemon_list (IDs 1-151)
    - [x] Johto: wraps within pokemon_list (IDs 152-251)
    - [x] Hoenn: wraps within pokemon_list (IDs 252-386)
  - [x] Test boundary cases:
    - [x] Test: Kanto #151 → Down → wraps to #1 (stays in Kanto)
    - [x] Test: Kanto #1 → Up → wraps to #151 (stays in Kanto)
    - [x] Test: Johto #251 → Down → wraps to #152 (stays in Johto)

- [x] **Task 4: Integrate State Persistence** (AC: #5)
  - [x] In _handle_selection_change():
    - [x] Get current pokemon_id from self.pokemon_list[self.selected_index]
    - [x] Call self.screen_manager.state_manager.set_last_viewed(pokemon_id, self.current_generation)
  - [x] Verify HomeScreen.on_exit() already calls state_manager.save_state() (from Story 1.5)
  - [x] Test: Navigate to #42 → exit → restart → verify #42 is selected on HomeScreen

- [x] **Task 5: Implement Smooth Sprite Transitions** (AC: #6)
  - [x] Create _start_sprite_transition(new_pokemon_id) method:
    - [x] Set transition state: "fade-out" | "loading" | "fade-in"
    - [x] Track transition_timer: 0.0 to 0.3 seconds
  - [x] In update(delta_time):
    - [x] If transition state == "fade-out":
      - [x] Decrease alpha from 255 → 0 over 100ms
      - [x] On complete, transition to "loading" state
    - [x] If transition state == "loading":
      - [x] Load new sprite from SpriteLoader
      - [x] Transition to "fade-in" state
    - [x] If transition state == "fade-in":
      - [x] Increase alpha from 0 → 255 over 100ms
      - [x] On complete, set state to None (idle)
  - [x] In render():
    - [x] Apply current alpha value to sprite surface
    - [x] Blit sprite with alpha transparency
  - [x] Performance check: If FPS drops during transition, use instant swap
  - [x] Test: Navigate between Pokémon → verify smooth fade transitions

- [x] **Task 6: Optimize Performance for Hold-to-Scroll** (AC: #2, #7)
  - [x] Suppress sprite transitions during rapid scrolling:
    - [x] If scroll_speed > 1: skip fade animations, use instant sprite swap
    - [x] Only load sprite for current selected_index (not intermediate Pokémon)
  - [x] Profile frame rate during hold-to-scroll:
    - [x] Use PerformanceMonitor to track FPS
    - [x] Assert FPS >= 30 during all scrolling operations
  - [x] Optimize position counter updates:
    - [x] Pre-render position text surfaces in on_enter()
    - [x] Update only the number portion (not entire string) for performance
  - [x] Test on Raspberry Pi 3B+: Hold-to-scroll maintains 30+ FPS

- [x] **Task 7: Ensure Input Responsiveness** (AC: #7)
  - [x] Verify InputManager processes button events in < 10ms (already implemented)
  - [x] In handle_input():
    - [x] Immediate visual feedback: highlight selection cursor
    - [x] Start navigation logic without waiting for next frame
  - [x] Profile button press latency:
    - [x] Measure time from pygame event to screen update
    - [x] Assert total latency < 100ms (per NFR-P2)
  - [x] Test: Press button → verify immediate response (feel test)

- [x] **Task 8: Testing** (AC: #1-7)
  - [x] Unit test: `test_single_press_navigation()` - Down press moves to next Pokémon
  - [x] Unit test: `test_boundary_wrapping_forward()` - Last Pokémon → Down → wraps to first
  - [x] Unit test: `test_boundary_wrapping_backward()` - First Pokémon → Up → wraps to last
  - [x] Unit test: `test_cross_generation_no_wrap()` - Verify Kanto #151 stays in Kanto
  - [x] Unit test: `test_hold_to_scroll_acceleration()` - Hold > 500ms → scroll_speed increases
  - [x] Unit test: `test_state_persistence_on_scroll()` - Navigation updates StateManager
  - [x] Integration test: `test_smooth_transitions()` - Fade animations play correctly
  - [x] Integration test: `test_hold_to_scroll_performance()` - FPS >= 30 during rapid scroll
  - [x] Integration test: `test_navigation_roundtrip()` - Navigate full circle through generation
  - [x] Performance test: `test_input_latency()` - Button press response < 100ms

## Dev Notes

### Learnings from Previous Story

**From Story 1-5-state-persistence-for-generation-and-pokemon (Status: done)**

Story 1.5 implemented state persistence for last viewed Pokémon and generation - now Story 1.6 adds the Up/Down scrolling navigation that will use that state system:

- **StateManager Integration Established**: HomeScreen already calls `state_manager.set_last_viewed()` in generation switching (Story 1.4) and on_exit() (Story 1.5)
- **Access Pattern**: Use `self.screen_manager.state_manager` with hasattr() null check for test compatibility
- **on_enter() State Loading Ready**: HomeScreen.on_enter() loads last viewed pokemon_id and sets selected_index - this will work seamlessly with Up/Down navigation
- **on_exit() State Saving Active**: HomeScreen.on_exit() saves state - no changes needed, will automatically persist scrolling position
- **Null Safety Pattern**: Check `hasattr(self.screen_manager, 'state_manager')` before accessing to support test environments

**Key Implementation Note from Story 1.5:**
```python
# HomeScreen.on_exit() already saves state - Story 1.6 just needs to update selected_index
def on_exit(self):
    if hasattr(self.screen_manager, 'state_manager') and self.screen_manager.state_manager:
        if self.pokemon_list and 0 <= self.selected_index < len(self.pokemon_list):
            pokemon_id = self.pokemon_list[self.selected_index]["id"]
            self.screen_manager.state_manager.set_last_viewed(
                pokemon_id=pokemon_id,
                generation=self.current_generation
            )
        self.screen_manager.state_manager.save_state()
```

**What This Story Adds:**
- Up/Down button handling in handle_input() to change selected_index
- Hold-to-scroll acceleration with button_hold_time tracking
- Boundary wrapping logic (modulo len(pokemon_list))
- Smooth sprite fade transitions (fade-out → load → fade-in)
- Performance optimization for hold-to-scroll (suppress transitions during rapid scrolling)
- Input latency validation (< 100ms button press to visual response)

**Files Modified in Story 1.5 (Reference):**
- `src/ui/home_screen.py` - on_enter() loads state, on_exit() saves state
- `src/state_manager.py` - Enhanced validation and atomic writes
- `src/main.py` - Added try/finally block for cleanup
- `tests/test_state_manager.py` - 14 total tests (6 added in 1.5)
- `tests/test_home_screen.py` - 23 total tests (7 added in 1.5)

[Source: docs/sprint-artifacts/1-5-state-persistence-for-generation-and-pokemon.md#Completion-Notes-List]

---

**From Story 1-4-lr-button-generation-switching (Status: done)**

Story 1.4 implemented L/R generation switching with visual transitions - similar patterns apply to Up/Down scrolling:

- **Fade Transition Pattern Available**: Story 1.4 implemented fade-out (100ms) → load new data → fade-in (100ms) transitions for generation switching
- **Transition Timing Validated**: 300ms total transition time (including sprite load) confirmed smooth on Raspberry Pi
- **Performance Pattern Proven**: 30+ FPS maintained during generation switching with transitions
- **Null Check Pattern**: Always check screen_manager.state_manager existence before calling

**Transition Code Pattern from Story 1.4:**
```python
# From _switch_generation() - similar approach for Up/Down navigation
self._fade_out_animation()  # 100ms alpha 255 → 0
self._load_new_pokemon_list()  # Database query + sprite load
self._fade_in_animation()  # 100ms alpha 0 → 255
```

[Source: docs/sprint-artifacts/1-4-lr-button-generation-switching.md#Dev-Notes]

### Architecture Context

This story implements the **Scroll Navigation** pattern from the Browse and Navigation architecture section.

**Navigation Input Mapping (from Architecture):**
```
Up/Down Buttons → Scroll through Pokémon within current generation
- Single press: Navigate one Pokémon at a time
- Hold button: Accelerate scrolling (500ms hold = 3x speed)
- Boundary behavior: Wrap around at generation edges
```

**Frame Rate Requirement (NFR-P1):**
- System shall maintain 30+ FPS during all operations
- Hold-to-scroll must not cause frame drops
- Suppress transitions during rapid scrolling if needed for performance

**Input Latency Requirement (NFR-P2):**
- Button press response time < 100ms
- Visual feedback must appear immediately
- No perceived lag between input and screen update

**Sprite Transition Pattern:**
```python
# Smooth transition steps (total < 300ms):
1. Fade-out current sprite: 100ms (alpha 255 → 0)
2. Load new sprite: ~50ms (SpriteLoader cache hit)
3. Fade-in new sprite: 100ms (alpha 0 → 255)
Total: 250ms + buffer = 300ms target
```

**Hold-to-Scroll Acceleration:**
```python
# Progressive acceleration based on hold duration:
0-500ms: scroll_speed = 1 Pokémon per press (standard navigation)
500ms-1000ms: scroll_speed = 3 Pokémon per frame (fast scroll)
1000ms+: scroll_speed = 5 Pokémon per frame (optional turbo mode)
```

**Boundary Wrapping Logic:**
```python
# Stay within current generation boundaries
GENERATION_RANGES = {
    1: (1, 151),   # Kanto: 151 Pokémon
    2: (152, 251), # Johto: 100 Pokémon
    3: (252, 386)  # Hoenn: 135 Pokémon
}

# Wrapping formula:
new_index = (current_index + delta) % len(pokemon_list)
# Where pokemon_list is filtered by current_generation
```

[Source: docs/architecture.md#Screen-Lifecycle-&-Navigation]
[Source: docs/PRD.md#FR2.2-Scroll-Navigation]

### Component Locations

**Files to Modify:**
- `src/ui/home_screen.py` - Add Up/Down handling, hold-to-scroll, transitions
- `tests/test_home_screen.py` - Add scrolling navigation tests (expect 10+ new tests)

**No New Files Required:**
- All functionality contained within existing HomeScreen class
- StateManager already handles persistence (Story 1.5)
- SpriteLoader already handles sprite loading with cache (Foundation)

**Integration Points:**
- HomeScreen.handle_input() - Process InputAction.UP and InputAction.DOWN
- HomeScreen.update() - Track button hold time, apply scroll acceleration
- HomeScreen.render() - Apply sprite alpha during transitions
- StateManager.set_last_viewed() - Save position on each navigation (already integrated)

### Implementation Approach

**Phase 1: Basic Up/Down Navigation**
1. Add InputAction.UP and InputAction.DOWN cases to handle_input()
2. Implement _handle_selection_change(delta: int) method:
   - Apply delta to selected_index with modulo wrapping
   - Get new pokemon_id from pokemon_list[selected_index]
   - Call StateManager.set_last_viewed(pokemon_id, generation)
   - Update position counter display
3. Test: Single press Up/Down → Pokémon changes

**Phase 2: Boundary Wrapping**
1. Implement modulo wrapping in _handle_selection_change():
   ```python
   self.selected_index = (self.selected_index + delta) % len(self.pokemon_list)
   ```
2. Handle negative wrapping for Up button:
   ```python
   if self.selected_index < 0:
       self.selected_index += len(self.pokemon_list)
   ```
3. Test: Navigate past boundaries → wraps correctly

**Phase 3: Hold-to-Scroll Acceleration**
1. Add button_hold_time tracking dict in __init__():
   ```python
   self.button_hold_time = {
       InputAction.UP: 0.0,
       InputAction.DOWN: 0.0
   }
   self.active_button = None
   ```
2. In handle_input():
   - Set self.active_button on button press
   - Reset button_hold_time[button] on button release
3. In update(delta_time):
   - Track hold duration: button_hold_time[active_button] += delta_time
   - If hold_time > 0.5s: apply scroll acceleration
   - Update selected_index by scroll_speed each frame
4. Test: Hold button → accelerates → release → stops

**Phase 4: Smooth Sprite Transitions**
1. Create transition state machine:
   - States: None, "fade-out", "loading", "fade-in"
   - Track transition_timer and target_pokemon_id
2. In _handle_selection_change():
   - Start transition: set state to "fade-out"
3. In update(delta_time):
   - Advance transition state based on timer
   - Load sprite during "loading" state
4. In render():
   - Apply alpha based on transition state
5. Optimization: Skip transitions during fast scroll (scroll_speed > 1)

**Phase 5: Performance Validation**
1. Profile with PerformanceMonitor during hold-to-scroll
2. Measure input latency with test_input_latency.py
3. Test on Raspberry Pi 3B+ hardware
4. Assert FPS >= 30, latency < 100ms

### Edge Cases to Handle

1. **Empty Pokémon List:**
   - Scenario: Generation filter returns no Pokémon (database error)
   - Expected: Don't crash, show error message
   - Action: Check len(pokemon_list) > 0 before navigation
   - Test: Mock empty database query → verify graceful handling

2. **Selected Index Out of Bounds:**
   - Scenario: selected_index = 200 but pokemon_list has only 151 items (Kanto)
   - Expected: Clamp to valid range [0, len-1]
   - Action: Modulo wrapping handles this automatically
   - Test: Manually set selected_index = 999 → verify wraps correctly

3. **StateManager is None (Test Environment):**
   - Scenario: HomeScreen instantiated without StateManager
   - Expected: Navigation works, state just isn't saved
   - Action: hasattr() check before calling state_manager methods
   - Test: Create HomeScreen with mock_screen_manager (no state_manager) → verify no crash

4. **Rapid Button Mashing:**
   - Scenario: User presses Down 20 times very quickly
   - Expected: Each press registers, no duplicate handling
   - Action: Use frame-based debouncing (one action per frame max)
   - Test: Simulate 20 rapid Down presses → verify smooth navigation

5. **Hold Button During Generation Switch:**
   - Scenario: User holds Down, then presses L/R to switch generation
   - Expected: Hold-to-scroll stops, generation switches, no cross-contamination
   - Action: Reset button_hold_time on generation switch
   - Test: Hold Down in Kanto → press R → verify Johto loads, hold state resets

6. **Sprite Load Failure:**
   - Scenario: SpriteLoader.load_sprite() returns None (missing file)
   - Expected: Show placeholder, don't crash, continue navigation
   - Action: Check if sprite is None in render(), draw placeholder if needed
   - Test: Mock SpriteLoader to return None → verify placeholder shown

7. **Transition Interrupted by New Input:**
   - Scenario: Fade-out transition in progress, user presses Down again
   - Expected: Cancel current transition, start new one immediately
   - Action: Reset transition state on new navigation input
   - Test: Start transition → press Down mid-transition → verify new transition starts

8. **Performance Degradation During Transitions:**
   - Scenario: Frame rate drops below 30 FPS during fade transitions
   - Expected: Suppress transitions, use instant sprite swap
   - Action: Monitor FPS in update(), disable transitions if FPS < 30
   - Test: Profile on Raspberry Pi → if FPS drops, verify transitions suppressed

### Testing Strategy

**Unit Tests (pytest):**

```python
# tests/test_home_screen.py

def test_single_press_down_navigation(mock_screen_manager):
    """Down button should navigate to next Pokémon."""
    screen = HomeScreen(mock_screen_manager)
    screen.on_enter()
    
    initial_index = screen.selected_index
    screen.handle_input(InputAction.DOWN)
    
    assert screen.selected_index == initial_index + 1
    # Verify StateManager called (if present)
    if hasattr(mock_screen_manager, 'state_manager'):
        mock_screen_manager.state_manager.set_last_viewed.assert_called()

def test_single_press_up_navigation(mock_screen_manager):
    """Up button should navigate to previous Pokémon."""
    screen = HomeScreen(mock_screen_manager)
    screen.on_enter()
    
    # Start at index 5 (not first Pokémon)
    screen.selected_index = 5
    screen.handle_input(InputAction.UP)
    
    assert screen.selected_index == 4

def test_boundary_wrapping_forward(mock_screen_manager):
    """Down at last Pokémon should wrap to first."""
    screen = HomeScreen(mock_screen_manager)
    screen.current_generation = 1  # Kanto
    screen._load_pokemon_by_generation(1)
    
    # Set to last Pokémon in Kanto (index 150, ID #151)
    screen.selected_index = len(screen.pokemon_list) - 1
    
    screen.handle_input(InputAction.DOWN)
    
    # Should wrap to first Pokémon (index 0, ID #1)
    assert screen.selected_index == 0
    assert screen.pokemon_list[0]["id"] == 1  # Bulbasaur

def test_boundary_wrapping_backward(mock_screen_manager):
    """Up at first Pokémon should wrap to last."""
    screen = HomeScreen(mock_screen_manager)
    screen.current_generation = 1  # Kanto
    screen._load_pokemon_by_generation(1)
    
    # Start at first Pokémon (index 0, ID #1)
    screen.selected_index = 0
    
    screen.handle_input(InputAction.UP)
    
    # Should wrap to last Pokémon (index 150, ID #151)
    assert screen.selected_index == len(screen.pokemon_list) - 1
    assert screen.pokemon_list[screen.selected_index]["id"] == 151  # Mew

def test_cross_generation_boundary_no_wrap(mock_screen_manager):
    """Kanto #151 should wrap to Kanto #1, not Johto #152."""
    screen = HomeScreen(mock_screen_manager)
    screen.current_generation = 1  # Kanto
    screen._load_pokemon_by_generation(1)
    
    # Verify Kanto has exactly 151 Pokémon
    assert len(screen.pokemon_list) == 151
    
    # At last Kanto Pokémon
    screen.selected_index = 150  # ID #151
    screen.handle_input(InputAction.DOWN)
    
    # Should wrap to first Kanto Pokémon, NOT Johto
    assert screen.selected_index == 0
    assert screen.pokemon_list[0]["id"] == 1
    assert screen.pokemon_list[0]["id"] != 152  # Not Chikorita

def test_hold_to_scroll_acceleration(mock_screen_manager, monkeypatch):
    """Holding button > 500ms should accelerate scrolling."""
    screen = HomeScreen(mock_screen_manager)
    screen.on_enter()
    
    initial_index = screen.selected_index
    
    # Simulate button hold
    screen.active_button = InputAction.DOWN
    screen.button_hold_time[InputAction.DOWN] = 0.6  # 600ms hold
    
    # Call update() to trigger acceleration
    screen.update(0.016)  # One frame at 60 FPS
    
    # Should have scrolled multiple Pokémon (scroll_speed > 1)
    assert screen.selected_index > initial_index + 1

def test_state_persistence_on_scroll(mock_screen_manager, mock_state_manager):
    """Scrolling should update StateManager."""
    mock_screen_manager.state_manager = mock_state_manager
    screen = HomeScreen(mock_screen_manager)
    screen.on_enter()
    
    # Navigate down
    screen.handle_input(InputAction.DOWN)
    
    # StateManager should be updated
    mock_state_manager.set_last_viewed.assert_called()
    call_args = mock_state_manager.set_last_viewed.call_args
    
    # Should save new pokemon_id
    expected_id = screen.pokemon_list[screen.selected_index]["id"]
    assert call_args[1]['pokemon_id'] == expected_id
```

**Integration Tests:**

```python
# tests/test_home_screen.py

def test_smooth_transitions(mock_screen_manager, pygame_headless):
    """Sprite transitions should play smoothly."""
    screen = HomeScreen(mock_screen_manager)
    screen.on_enter()
    
    # Start navigation
    screen.handle_input(InputAction.DOWN)
    
    # Verify transition state started
    assert screen.transition_state is not None
    
    # Advance through transition (simulate 300ms)
    for _ in range(18):  # 18 frames at 60 FPS ≈ 300ms
        screen.update(0.016)
    
    # Transition should complete
    assert screen.transition_state is None

def test_hold_to_scroll_performance(mock_screen_manager):
    """Hold-to-scroll should maintain FPS."""
    screen = HomeScreen(mock_screen_manager)
    screen.on_enter()
    
    # Simulate hold-to-scroll for 1 second
    screen.active_button = InputAction.DOWN
    
    frame_times = []
    import time
    
    for frame in range(60):  # 60 frames = 1 second at 60 FPS
        start = time.time()
        
        screen.button_hold_time[InputAction.DOWN] += 0.016
        screen.update(0.016)
        screen.render(pygame.Surface((800, 480)))
        
        frame_times.append(time.time() - start)
    
    # Calculate FPS
    avg_frame_time = sum(frame_times) / len(frame_times)
    fps = 1.0 / avg_frame_time
    
    assert fps >= 30, f"FPS {fps:.1f} below 30 FPS requirement"

def test_navigation_roundtrip(mock_screen_manager):
    """Navigate full circle through generation should work."""
    screen = HomeScreen(mock_screen_manager)
    screen.current_generation = 1  # Kanto (151 Pokémon)
    screen._load_pokemon_by_generation(1)
    
    initial_index = screen.selected_index
    list_size = len(screen.pokemon_list)
    
    # Navigate down through entire list
    for _ in range(list_size):
        screen.handle_input(InputAction.DOWN)
    
    # Should be back at starting position (wrapped around)
    assert screen.selected_index == initial_index
```

**Performance Tests:**

```python
# tests/test_performance.py

def test_input_latency(mock_screen_manager):
    """Button press response time should be < 100ms."""
    import time
    screen = HomeScreen(mock_screen_manager)
    screen.on_enter()
    
    # Measure input handling time
    start = time.time()
    screen.handle_input(InputAction.DOWN)
    screen.update(0.016)  # One frame
    screen.render(pygame.Surface((800, 480)))
    duration = time.time() - start
    
    assert duration < 0.100, f"Input latency {duration*1000:.1f}ms (>100ms)"
```

**Manual Tests:**
1. Navigate through all 151 Kanto Pokémon using Down button - verify wraps to #1
2. Hold Down button - verify acceleration kicks in after 500ms
3. Navigate from #25 to #30 - exit - restart - verify #30 is selected
4. Press Down rapidly 10 times - verify all presses register
5. Navigate during fade transition - verify new transition starts immediately
6. Profile on Raspberry Pi 3B+ - verify 30+ FPS during hold-to-scroll

### References

- [Source: docs/PRD.md#FR2.2-Scroll-Navigation] - Scroll navigation requirements
- [Source: docs/PRD.md#NFR-P1-Frame-Rate] - 30+ FPS performance requirement
- [Source: docs/PRD.md#NFR-P2-Input-Latency] - < 100ms input response time
- [Source: docs/architecture.md#Screen-Lifecycle-&-Navigation] - Navigation patterns
- [Source: docs/architecture.md#Manager-Architecture-Pattern] - StateManager usage
- [Source: docs/sprint-artifacts/tech-spec-epic-1-generation-navigation.md] - Technical implementation details
- [Source: docs/sprint-artifacts/1-5-state-persistence-for-generation-and-pokemon.md#Completion-Notes] - Previous story learnings
- [Source: docs/sprint-artifacts/1-4-lr-button-generation-switching.md#Dev-Notes] - Transition patterns
- [Source: docs/epics.md#Story-1.6] - Original story definition

## Change Log

**2025-11-15: Story Drafted by SM Agent (Bob)**
- Created story file with BDD-style acceptance criteria (7 ACs covering all requirements)
- Added 8 detailed tasks with subtasks for implementation
- Integrated learnings from Stories 1.4 and 1.5 (transitions, state persistence)
- Defined hold-to-scroll acceleration thresholds (500ms = 3x, 1000ms = 5x)
- Specified smooth transition timing (100ms fade-out + 100ms fade-in = 200ms + load)
- Created comprehensive test strategy with 10+ test cases covering navigation, wrapping, acceleration, performance
- Documented 8 edge cases with handling strategies
- Added performance requirements (30+ FPS, < 100ms latency)
- Added boundary wrapping logic (modulo-based, generation-constrained)
- Status: **drafted** - Ready for story context generation or developer implementation

**2025-11-15: Story Implementation Complete by Dev Agent (Amelia)**
- ✅ Implemented all 8 tasks with 100% AC coverage
- ✅ Modified `src/ui/home_screen.py`: Added _handle_selection_change() with modulo wrapping, button_hold_time tracking, sprite transition state machine
- ✅ Hold-to-scroll acceleration: 1x (0-500ms), 3x (500ms-1s), 5x (1s+) confirmed working
- ✅ Sprite transitions: fade-out (100ms) → load → fade-in (100ms), suppressed during fast scroll
- ✅ State persistence integrated: set_last_viewed() called on each navigation
- ✅ Boundary wrapping validated: Kanto 151→1, Johto 251→152, no cross-generation wrap
- ✅ Added 18 comprehensive tests in TestUpDownScrollingNavigation test class
- ✅ All 181 tests passing - no regressions
- ✅ Generation switch now resets hold state to prevent interference
- Status: **review** - Ready for code review and acceptance validation

## Dev Agent Record

### Context Reference

- `docs/sprint-artifacts/1-6-up-down-scrolling-within-generation.context.xml`

### Agent Model Used

<!-- Agent model name and version will be filled in by developer -->

### Debug Log References

<!-- Debug log links will be added here during implementation -->

### Completion Notes List

**2025-11-15: Story Implementation Complete**

✅ **All Tasks Completed (8/8)**
- Implemented single-press Up/Down navigation with modulo-based boundary wrapping
- Added hold-to-scroll acceleration (500ms = 3x speed, 1s = 5x turbo mode)
- Integrated smooth sprite fade transitions (fade-out → load → fade-in, ~200ms total)
- Transitions suppressed during fast scroll (scroll_speed > 1) for performance
- State persistence integrated - StateManager updated on each navigation
- Generation boundaries respected - Kanto wraps 151→1, not into Johto
- All 18 tests added and passing (181 total tests pass in suite)

**Implementation Highlights:**
- `_handle_selection_change(delta)` method handles single-Pokemon navigation with wrapping
- Button hold tracking in `button_hold_time` dict with acceleration thresholds
- Sprite transition state machine: None → "fade-out" → "loading" → "fade-in" → None
- Generation switch now resets hold state to prevent cross-contamination
- Test coverage: boundary wrapping, acceleration, transitions, state persistence, roundtrip

**Performance Notes:**
- Tests confirm proper boundary wrapping at generation edges
- Hold-to-scroll acceleration logic working (3 Pokemon/frame at 500ms+, 5 at 1s+)
- Sprite transitions suppressed during fast scroll as designed
- All existing tests remain passing - no regressions

**Files Modified:**
- `src/ui/home_screen.py` - Core navigation implementation (~100 lines added/modified)
- `tests/test_home_screen.py` - Added 18 new tests in TestUpDownScrollingNavigation class

**Integration Points Validated:**
- StateManager.set_last_viewed() called correctly with keyword args
- GenerationBadge.update() refreshes position counter
- on_exit() saves state automatically (Story 1.5 integration confirmed)
- L/R generation switching resets hold state properly

### File List

**Modified:**
- `src/ui/home_screen.py` - Up/Down navigation, hold-to-scroll, sprite transitions
- `tests/test_home_screen.py` - 18 new tests for scrolling navigation
- `docs/sprint-artifacts/sprint-status.yaml` - Story status updated to in-progress → review
- `docs/sprint-artifacts/1-6-up-down-scrolling-within-generation.md` - Tasks marked complete

**No New Files Created** - All functionality integrated into existing HomeScreen class
