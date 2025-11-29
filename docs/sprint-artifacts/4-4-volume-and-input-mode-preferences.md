# Story 4.4: Volume and Input Mode Preferences

Status: review

## Story

As a user,
I want my volume and input preferences saved,
so that they persist across sessions.

## Acceptance Criteria

1. **Volume Preference Persistence (AC #1)**
   - **Given** a user sets volume to 0.5 (50%)
   - **When** the user exits the application
   - **Then** StateManager saves volume=0.5 to state file
   - **And** the volume value is stored in `preferences.volume` field
   - **And** the save operation uses atomic write pattern (temp file + rename)

2. **Volume Preference Restoration on Boot (AC #2)**
   - **Given** the application restarts with volume=0.5 in state file
   - **When** StateManager loads state
   - **Then** `StateManager.get_volume()` returns 0.5
   - **And** the volume preference is available immediately after StateManager initialization
   - **And** (future audio feature will use this volume setting via AudioManager)

3. **Input Mode Preference Persistence (AC #3)**
   - **Given** a user's input mode is set to "gpio"
   - **When** the application exits
   - **Then** StateManager saves input_mode="gpio" to state file
   - **And** the value is stored in `preferences.input_mode` field

4. **Input Mode Preference Restoration on Boot (AC #4)**
   - **Given** the application restarts with input_mode="gpio" in state file
   - **When** StateManager loads state
   - **Then** `StateManager.get_input_mode()` returns "gpio"
   - **And** InputManager can use this value to configure button controls

5. **Volume Validation and Clamping (AC #5)**
   - **Given** a volume value outside valid range (e.g., -0.5 or 1.5)
   - **When** `StateManager.set_volume()` is called
   - **Then** the value is clamped to 0.0-1.0 range
   - **And** -0.5 becomes 0.0, 1.5 becomes 1.0
   - **And** no error or exception is raised

6. **Input Mode Validation (AC #6)**
   - **Given** an invalid input_mode value (e.g., "touchscreen" or "joystick")
   - **When** StateManager loads state or `set_input_mode()` is called
   - **Then** invalid values are rejected (set_input_mode ignores invalid input)
   - **And** on load, invalid values reset to "keyboard" default
   - **And** a warning is logged for invalid values

7. **Volume Validation on Load (AC #7)**
   - **Given** a state file with volume=2.5 (invalid, out of range)
   - **When** StateManager loads the state file
   - **Then** volume is clamped to 1.0
   - **And** warning is logged: "volume 2.5 out of range, clamped to 1.0"
   - **And** corrected value is written back to state file

8. **Preferences Survive Power Cycle (AC #8)**
   - **Given** user sets volume=0.3 and input_mode="gpio"
   - **When** application saves state and restarts (simulated power cycle)
   - **Then** both preferences are restored correctly
   - **And** get_volume() returns 0.3
   - **And** get_input_mode() returns "gpio"

## Tasks / Subtasks

- [x] **Task 1: Verify StateManager Volume Methods Exist and Work (AC #1, #2, #5)**
  - [x] 1.1: Verify `get_volume()` returns float from `preferences.volume`
  - [x] 1.2: Verify `set_volume()` updates `preferences.volume` in memory
  - [x] 1.3: Verify `set_volume()` clamps values to 0.0-1.0 range
  - [x] 1.4: Verify volume persists through save_state() and reload cycle

- [x] **Task 2: Verify StateManager Input Mode Methods Exist and Work (AC #3, #4, #6)**
  - [x] 2.1: Verify `get_input_mode()` returns string from `preferences.input_mode`
  - [x] 2.2: Verify `set_input_mode()` updates `preferences.input_mode` in memory
  - [x] 2.3: Verify `set_input_mode()` only accepts "keyboard" or "gpio"
  - [x] 2.4: Verify invalid mode values are silently ignored (no exception)
  - [x] 2.5: Verify input_mode persists through save_state() and reload cycle

- [x] **Task 3: Verify Load-Time Validation (AC #5, #6, #7)**
  - [x] 3.1: Review `_load_state()` validation logic for volume clamping
  - [x] 3.2: Review `_load_state()` validation logic for input_mode validation
  - [x] 3.3: Verify invalid values trigger warning logs
  - [x] 3.4: Verify corrected values are written back to state file on load

- [x] **Task 4: Write Unit Tests for Volume Preference (AC #1, #2, #5, #7)**
  - [x] 4.1: Test `test_set_and_get_volume()` - set volume, verify getter returns same value
  - [x] 4.2: Test `test_volume_clamping_low()` - set -0.5, verify 0.0 returned
  - [x] 4.3: Test `test_volume_clamping_high()` - set 1.5, verify 1.0 returned
  - [x] 4.4: Test `test_volume_persists_through_save_reload()` - save, create new StateManager, verify restored
  - [x] 4.5: Test `test_volume_validation_on_load()` - write invalid volume to file, load, verify clamped
  - [x] 4.6: Test `test_volume_default_value()` - new state file has volume=0.7

- [x] **Task 5: Write Unit Tests for Input Mode Preference (AC #3, #4, #6)**
  - [x] 5.1: Test `test_set_and_get_input_mode_keyboard()` - set "keyboard", verify returned
  - [x] 5.2: Test `test_set_and_get_input_mode_gpio()` - set "gpio", verify returned
  - [x] 5.3: Test `test_input_mode_invalid_ignored()` - set invalid mode, verify previous value retained
  - [x] 5.4: Test `test_input_mode_persists_through_save_reload()` - save "gpio", reload, verify "gpio"
  - [x] 5.5: Test `test_input_mode_validation_on_load()` - write invalid mode to file, load, verify "keyboard"
  - [x] 5.6: Test `test_input_mode_default_value()` - new state file has input_mode="keyboard"

- [x] **Task 6: Write Integration Test for Power Cycle Simulation (AC #8)**
  - [x] 6.1: Test `test_preferences_survive_power_cycle()`:
    - Create StateManager with temp file
    - Set volume=0.3, input_mode="gpio"
    - Call save_state()
    - Create NEW StateManager instance with same file path
    - Verify get_volume() returns 0.3
    - Verify get_input_mode() returns "gpio"

- [x] **Task 7: Verify Logging for Validation Warnings (AC #6, #7)**
  - [x] 7.1: Test that loading invalid volume logs warning with clamped values
  - [x] 7.2: Test that loading invalid input_mode logs warning about default reset
  - [x] 7.3: Use `caplog` pytest fixture to capture and assert log messages

## Dev Notes

### Existing Implementation Review

The `StateManager` class in `src/state_manager.py` already has the required methods implemented:

**Volume Methods (lines 360-368):**
```python
def get_volume(self) -> float:
    """Get audio volume (0.0 to 1.0)."""
    return self.get_preference('volume', 0.7)

def set_volume(self, volume: float):
    """Set audio volume (0.0 to 1.0)."""
    volume = max(0.0, min(1.0, volume))  # Clamp to valid range
    self.set_preference('volume', volume)
```

**Input Mode Methods (lines 370-378):**
```python
def get_input_mode(self) -> str:
    """Get input mode ('keyboard' or 'gpio')."""
    return self.get_preference('input_mode', 'keyboard')

def set_input_mode(self, mode: str):
    """Set input mode."""
    if mode in ('keyboard', 'gpio'):
        self.set_preference('input_mode', mode)
```

**Load-Time Validation (lines 130-160 in `_load_state()`):**
- Volume clamping: `max(0.0, min(1.0, float(original_volume)))`
- Input mode validation: checks if mode is in `('keyboard', 'gpio')`, resets to 'keyboard' if not
- Warning logging for out-of-range values
- Corrected values written back to file

### This Story's Focus

This story is primarily a **verification and testing story**. The implementation exists; the focus is:
1. **Verify** the existing implementation meets all acceptance criteria
2. **Write comprehensive tests** to document and validate behavior
3. **Ensure edge cases** are handled (clamping, validation, persistence)

### State File Structure Reference

```json
{
  "version": "1.0.0",
  "last_viewed": {
    "pokemon_id": 25,
    "generation": 1
  },
  "preferences": {
    "input_mode": "keyboard",  ← Story 4.4 focus
    "volume": 0.7              ← Story 4.4 focus
  },
  "favorites": [],
  "recent": [],
  "stats": {...}
}
```

### Project Structure Notes

**Files to Verify:**
- `src/state_manager.py` - Existing implementation (lines 350-378 for preference methods)

**Test Files:**
- `tests/test_state_manager.py` - Add `TestVolumePreference` and `TestInputModePreference` classes

### Learnings from Previous Story

**From Story 4.3: Boot to HomeScreen Behavior (Status: done)**

- **Test Patterns Established**: Use `tempfile.mkdtemp()` for isolated temp directories
- **StateManager API Confirmed**: `save_state()`, `get_*()`, `set_*()` patterns verified
- **Atomic Write Pattern**: Uses temp file + `Path.replace()` for atomicity
- **Existing Test Classes**: `TestFirstBootHomeScreen`, `TestFirstBootStateInitialization` provide templates

**Files Modified in Story 4.3:**
- `src/main.py` - Boot sequence verification
- `tests/test_home_screen.py` - Added boot behavior tests
- (No `test_screen_manager.py` was created - tests integrated into existing files)

[Source: docs/sprint-artifacts/4-3-boot-to-homescreen-behavior.md#Dev-Agent-Record]

**From Story 4.1: First Boot State Initialization (Status: done)**

- **`_persist_default_state()` Method**: Ensures defaults written atomically
- **Validation in `_load_state()`**: Already clamps pokemon_id (1-386), generation (1-3), volume (0.0-1.0), input_mode
- **Test File Location**: `tests/test_state_manager.py` contains existing StateManager tests

[Source: docs/sprint-artifacts/4-1-first-boot-state-initialization.md#Dev-Notes]

### Testing Strategy

Per project testing standards (`TESTING.md`):
- Use pytest with fixtures from `tests/conftest.py`
- Use temporary state file paths via `temp_state_file` fixture
- Clean up in teardown or use pytest's tmp_path
- Use `caplog` fixture to verify warning log messages
- Follow existing `TestStateManager` patterns in `tests/test_state_manager.py`

### Edge Cases to Test

1. **Volume at boundaries**: 0.0, 1.0, 0.5 (mid), 0.001 (near zero), 0.999 (near max)
2. **Volume out of bounds**: -1.0, 2.0, -0.001, 1.001, float('inf'), None
3. **Input mode valid**: "keyboard", "gpio"
4. **Input mode invalid**: "touchscreen", "", None, 123, "KEYBOARD" (case sensitive?)
5. **Missing preference keys**: State file missing `preferences` section entirely
6. **Type coercion**: Volume as string "0.5" in JSON (should work with float() conversion)

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-3-state-persistence.md#Data-Models-and-Contracts]
- [Source: docs/architecture.md#StateManager-Integration]
- [Source: docs/epics.md#Story-4.4]
- [Source: src/state_manager.py - lines 350-378]

## Dev Agent Record

### Context Reference

- docs/sprint-artifacts/4-4-volume-and-input-mode-preferences.context.xml

### Agent Model Used

Claude Opus 4.5 (Preview)

### Debug Log References

Implementation Plan: This was a verification and testing story. The StateManager implementation already existed with proper volume clamping (lines 365-368), input mode validation (lines 374-377), and load-time validation (lines 145-169). Focus was on writing comprehensive tests to verify all acceptance criteria.

### Completion Notes List

- **Tasks 1-3 (Verification)**: Confirmed existing implementation in `src/state_manager.py` meets all ACs:
  - `get_volume()` returns float from preferences with 0.7 default
  - `set_volume()` clamps to 0.0-1.0 using `max(0.0, min(1.0, volume))`
  - `get_input_mode()` returns string from preferences with "keyboard" default
  - `set_input_mode()` validates mode is in `('keyboard', 'gpio')`, ignores invalid
  - `_load_state()` validates and clamps on load, logs warnings, writes back corrections

- **Tasks 4-7 (Tests)**: Added 23 comprehensive pytest tests in 4 new test classes:
  - `TestVolumePreference`: 9 tests covering set/get, clamping, persistence, load validation
  - `TestInputModePreference`: 8 tests covering set/get, invalid rejection, persistence
  - `TestPreferencesPowerCycle`: 3 tests for power cycle simulation (AC #8)
  - `TestValidationLogging`: 3 tests for warning log verification using `caplog`

- **All 455 project tests pass** with no regressions

### File List

- `tests/test_state_manager.py` - Added 4 pytest test classes with 23 new tests (lines 740-1050)
