# Story 4.5: State File Corruption Recovery

Status: done

## Story

As a user,
I want the device to recover gracefully if the state file is corrupted,
so that the device always works even if something goes wrong.

## Acceptance Criteria

1. **Application Does Not Crash on Corrupted JSON (AC #1)**
   - **Given** the state file contains invalid JSON (e.g., `{invalid json...}` or truncated content)
   - **When** the application starts and StateManager initializes
   - **Then** the application does not crash
   - **And** no unhandled exceptions propagate to main.py
   - **And** the application continues to boot normally

2. **Default Values Loaded on Corruption (AC #2)**
   - **Given** the state file is corrupted (invalid JSON)
   - **When** StateManager._load_state() executes
   - **Then** StateManager loads default values:
     - pokemon_id = 1 (Bulbasaur)
     - generation = 1 (Kanto)
     - input_mode = "keyboard"
     - volume = 0.7
   - **And** HomeScreen displays Bulbasaur (#1) in Kanto generation

3. **Corrupt File Overwritten with Valid Defaults (AC #3)**
   - **Given** the state file contains invalid JSON
   - **When** StateManager initializes and recovers
   - **Then** the corrupt file is overwritten with valid JSON defaults
   - **And** subsequent application restarts load the new valid defaults
   - **And** the file contains properly formatted JSON with all default fields

4. **Warning Logged for Corruption (AC #4)**
   - **Given** the state file is corrupted
   - **When** StateManager._load_state() catches the parse error
   - **Then** a warning is logged: "State file corrupted, resetting to defaults - {error details}"
   - **And** the log includes the specific JSONDecodeError or IOError message
   - **And** the log level is WARNING (not ERROR) since recovery is successful

5. **Invalid pokemon_id Clamped to Valid Range (AC #5)**
   - **Given** a state file with pokemon_id=999 (invalid, out of 1-386 range)
   - **When** StateManager loads state
   - **Then** pokemon_id is clamped to 386 (max valid value)
   - **And** warning logged: "pokemon_id 999 out of range, clamped to 386"
   - **And** corrected value written back to state file

6. **Invalid Generation Clamped to Valid Range (AC #6)**
   - **Given** a state file with generation=5 (invalid, out of 1-3 range)
   - **When** StateManager loads state
   - **Then** generation is clamped to 3 (max valid value)
   - **And** warning logged: "generation 5 out of range, clamped to 3"
   - **And** corrected value written back to state file

7. **Invalid Volume Clamped to Valid Range (AC #7)**
   - **Given** a state file with volume=2.5 (invalid, out of 0.0-1.0 range)
   - **When** StateManager loads state
   - **Then** volume is clamped to 1.0 (max valid value)
   - **And** warning logged: "volume 2.5 out of range, clamped to 1.0"
   - **And** corrected value written back to state file

8. **Invalid Input Mode Reset to Default (AC #8)**
   - **Given** a state file with input_mode="touchscreen" (invalid)
   - **When** StateManager loads state
   - **Then** input_mode is reset to "keyboard" (default)
   - **And** warning logged: "invalid input_mode 'touchscreen', defaulting to 'keyboard'"
   - **And** corrected value written back to state file

9. **Negative Values Clamped Correctly (AC #9)**
   - **Given** a state file with pokemon_id=-5 or volume=-0.5
   - **When** StateManager loads state
   - **Then** pokemon_id=-5 is clamped to 1 (min valid value)
   - **And** volume=-0.5 is clamped to 0.0 (min valid value)
   - **And** warnings logged for each invalid value

10. **Application Continues After Recovery (AC #10)**
    - **Given** any corruption recovery scenario (AC #1-9)
    - **When** recovery completes
    - **Then** the application continues normal operation
    - **And** HomeScreen displays correctly with recovered/default values
    - **And** user can navigate and browse Pokémon normally
    - **And** new state changes are saved correctly

## Tasks / Subtasks

- [x] **Task 1: Verify JSON Parse Error Handling (AC #1, #2, #3, #4)**
  - [x] 1.1: Review `_load_state()` try/except block catches `json.JSONDecodeError`
  - [x] 1.2: Review `_load_state()` try/except block catches `IOError`
  - [x] 1.3: Verify default state is returned on exception
  - [x] 1.4: Verify corrupt file is overwritten with valid defaults
  - [x] 1.5: Verify warning log message format matches AC #4

- [x] **Task 2: Verify Field Validation Logic (AC #5, #6, #7, #8, #9)**
  - [x] 2.1: Review pokemon_id validation: `max(1, min(386, original_id))`
  - [x] 2.2: Review generation validation: `max(1, min(3, original_gen))`
  - [x] 2.3: Review volume validation: `max(0.0, min(1.0, float(original_volume)))`
  - [x] 2.4: Review input_mode validation: check against `('keyboard', 'gpio')`
  - [x] 2.5: Verify `needs_correction` flag triggers file save with corrected values

- [x] **Task 3: Write Unit Tests for Corrupt JSON Handling (AC #1, #2, #3, #4)**
  - [x] 3.1: Test `test_corrupt_json_does_not_crash()` - write invalid JSON, init StateManager
  - [x] 3.2: Test `test_corrupt_json_returns_defaults()` - verify default values loaded
  - [x] 3.3: Test `test_corrupt_json_overwrites_file()` - verify file now contains valid JSON
  - [x] 3.4: Test `test_corrupt_json_logs_warning()` - use caplog to verify warning message
  - [x] 3.5: Test `test_truncated_json_handled()` - test with incomplete JSON like `{"version": "1`
  - [x] 3.6: Test `test_empty_file_handled()` - test with 0-byte file

- [x] **Task 4: Write Unit Tests for pokemon_id Validation (AC #5, #9)**
  - [x] 4.1: Test `test_pokemon_id_above_max_clamped()` - id=999 clamped to 386
  - [x] 4.2: Test `test_pokemon_id_below_min_clamped()` - id=-5 clamped to 1
  - [x] 4.3: Test `test_pokemon_id_zero_clamped()` - id=0 clamped to 1
  - [x] 4.4: Test `test_pokemon_id_valid_unchanged()` - id=25 remains 25
  - [x] 4.5: Test `test_pokemon_id_boundary_values()` - id=1 and id=386 unchanged

- [x] **Task 5: Write Unit Tests for Generation Validation (AC #6, #9)**
  - [x] 5.1: Test `test_generation_above_max_clamped()` - gen=5 clamped to 3
  - [x] 5.2: Test `test_generation_below_min_clamped()` - gen=-1 clamped to 1
  - [x] 5.3: Test `test_generation_zero_clamped()` - gen=0 clamped to 1
  - [x] 5.4: Test `test_generation_valid_unchanged()` - gen=2 remains 2
  - [x] 5.5: Test `test_generation_boundary_values()` - gen=1 and gen=3 unchanged

- [x] **Task 6: Write Unit Tests for Volume Validation (AC #7, #9)**
  - [x] 6.1: Test `test_volume_above_max_clamped()` - vol=2.5 clamped to 1.0
  - [x] 6.2: Test `test_volume_below_min_clamped()` - vol=-0.5 clamped to 0.0
  - [x] 6.3: Test `test_volume_valid_unchanged()` - vol=0.5 remains 0.5
  - [x] 6.4: Test `test_volume_boundary_values()` - vol=0.0 and vol=1.0 unchanged
  - [x] 6.5: Test `test_volume_string_coerced()` - vol="0.5" converted to float 0.5

- [x] **Task 7: Write Unit Tests for Input Mode Validation (AC #8)**
  - [x] 7.1: Test `test_input_mode_invalid_reset_to_keyboard()` - "touchscreen" → "keyboard"
  - [x] 7.2: Test `test_input_mode_empty_string_reset()` - "" → "keyboard"
  - [x] 7.3: Test `test_input_mode_case_sensitive()` - "GPIO" (uppercase) → "keyboard"
  - [x] 7.4: Test `test_input_mode_valid_keyboard_unchanged()` - "keyboard" remains
  - [x] 7.5: Test `test_input_mode_valid_gpio_unchanged()` - "gpio" remains

- [x] **Task 8: Write Unit Tests for Logging Verification (AC #4, #5, #6, #7, #8)**
  - [x] 8.1: Test `test_corrupt_json_warning_logged()` - verify caplog contains expected message
  - [x] 8.2: Test `test_pokemon_id_clamping_warning_logged()` - verify warning format
  - [x] 8.3: Test `test_generation_clamping_warning_logged()` - verify warning format
  - [x] 8.4: Test `test_volume_clamping_warning_logged()` - verify warning format
  - [x] 8.5: Test `test_input_mode_reset_warning_logged()` - verify warning format

- [x] **Task 9: Write Integration Test for Full Recovery Flow (AC #10)**
  - [x] 9.1: Test `test_recovery_allows_normal_operation()`:
    - Write corrupt JSON to state file
    - Initialize StateManager (triggers recovery)
    - Verify defaults loaded
    - Simulate navigation: set_last_viewed(25, 1)
    - Call save_state()
    - Create new StateManager with same file
    - Verify Pikachu (#25) restored correctly
  - [x] 9.2: Test `test_recovery_file_usable_after_overwrite()`:
    - Write corrupt JSON
    - Initialize StateManager
    - Re-read file and verify it's valid JSON
    - Verify all expected fields present

## Dev Notes

### Existing Implementation Review

The corruption recovery logic is already implemented in `src/state_manager.py` in the `_load_state()` method (lines 102-197):

**JSON Parse Error Handling (lines 188-197):**
```python
except (json.JSONDecodeError, IOError) as e:
    logger.warning(f"State file corrupted, resetting to defaults - {e}")
    # Overwrite corrupt file with defaults
    default_state = self._get_default_state()
    try:
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(default_state, f, indent=2, ensure_ascii=False)
    except IOError:
        pass  # Don't fail if we can't write defaults
    return default_state
```

**Field Validation and Clamping (lines 130-175):**
```python
# Clamp pokemon_id to valid range (1-386)
state['last_viewed']['pokemon_id'] = max(1, min(386, original_id))

# Clamp generation to valid range (1-3)
state['last_viewed']['generation'] = max(1, min(3, original_gen))

# Clamp volume to valid range (0.0-1.0)
state['preferences']['volume'] = max(0.0, min(1.0, float(original_volume)))

# Validate input_mode
if state['preferences']['input_mode'] not in ('keyboard', 'gpio'):
    state['preferences']['input_mode'] = 'keyboard'
```

**Corrected Values Written Back (lines 167-172):**
```python
if needs_correction:
    try:
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        logger.info("Corrected state file saved")
    except IOError:
        pass  # Don't fail on save error during load
```

### This Story's Focus

This story is a **verification and testing story**. The implementation exists; the focus is:
1. **Verify** the existing error handling meets all acceptance criteria
2. **Write comprehensive tests** for all corruption scenarios
3. **Ensure edge cases** are covered (truncated JSON, empty files, boundary values)
4. **Document** the recovery behavior for future maintenance

### Corruption Scenarios to Test

| Scenario | Example Content | Expected Behavior |
|----------|-----------------|-------------------|
| Invalid JSON syntax | `{invalid json}` | Reset to defaults |
| Truncated JSON | `{"version": "1` | Reset to defaults |
| Empty file | (0 bytes) | Reset to defaults |
| Non-JSON content | `Hello World` | Reset to defaults |
| Binary garbage | Random bytes | Reset to defaults |
| pokemon_id too high | `999` | Clamp to 386 |
| pokemon_id too low | `-5` or `0` | Clamp to 1 |
| generation too high | `5` | Clamp to 3 |
| generation too low | `-1` or `0` | Clamp to 1 |
| volume too high | `2.5` | Clamp to 1.0 |
| volume too low | `-0.5` | Clamp to 0.0 |
| invalid input_mode | `"touchscreen"` | Reset to "keyboard" |
| missing sections | `{"version": "1.0.0"}` | Add missing with defaults |

### Project Structure Notes

**Files to Verify:**
- `src/state_manager.py` - Lines 102-197 (corruption handling in `_load_state()`)

**Test Files:**
- `tests/test_state_manager.py` - Add `TestCorruptionRecovery` class

### Learnings from Previous Story

**From Story 4.4: Volume and Input Mode Preferences (Status: drafted)**

- **Validation Logic Confirmed**: Volume clamping and input_mode validation already verified
- **Test Patterns**: Use `caplog` pytest fixture for log message verification
- **Edge Case Coverage**: Boundary values, type coercion, missing fields

[Source: docs/sprint-artifacts/4-4-volume-and-input-mode-preferences.md#Existing-Implementation-Review]

**From Story 4.3: Boot to HomeScreen Behavior (Status: done)**

- **Test Patterns Established**: Use `tempfile.mkdtemp()` for isolated temp directories
- **File Operations**: Path.replace() for atomic writes confirmed working
- **Recovery Continues to HomeScreen**: After recovery, app boots to HomeScreen with defaults

[Source: docs/sprint-artifacts/4-3-boot-to-homescreen-behavior.md#Learnings-from-Previous-Story]

**From Story 4.1: First Boot State Initialization (Status: done)**

- **Default State Structure**: All required fields documented
- **Atomic Write Pattern**: Uses temp file + rename for safety
- **Directory Creation**: `mkdir(parents=True, exist_ok=True)` handles missing parent directories

[Source: docs/sprint-artifacts/4-1-first-boot-state-initialization.md#Dev-Notes]

### Testing Strategy

Per project testing standards (`TESTING.md`):
- Use pytest with fixtures from `tests/conftest.py`
- Use `tmp_path` fixture for isolated temp directories
- Use `caplog` fixture to verify warning log messages
- Create corrupt files directly in test setup, don't rely on external fixtures
- Clean up handled automatically by pytest temp directory fixtures

### Security Considerations

Per tech spec NFR Security section:
- **Data Validation**: All loaded values validated against allowed ranges
- **Invalid values clamped or reset to defaults**: Prevents crashes from malicious JSON
- **No crash vectors**: Application continues even with adversarial input
- **File path fixed**: No user-controlled paths prevent path traversal attacks

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-3-state-persistence.md#Reliability/Availability]
- [Source: docs/sprint-artifacts/tech-spec-epic-3-state-persistence.md#Corrupted-State-File-Workflow]
- [Source: docs/epics.md#Story-4.5]
- [Source: src/state_manager.py - lines 102-197]

## Dev Agent Record

### Context Reference

- docs/sprint-artifacts/4-5-state-file-corruption-recovery.context.xml

### Agent Model Used

Claude Opus 4.5 (Preview)

### Debug Log References

Implementation Plan: This was primarily a verification and testing story. The corruption recovery logic existed in `_load_state()`. During testing, discovered and fixed two edge cases:
1. `UnicodeDecodeError` not caught (binary files)
2. String volume comparison failed when `original_volume` is still a string

### Completion Notes List

- **Tasks 1-2 (Verification)**: Reviewed existing implementation in `src/state_manager.py`:
  - JSON parse errors caught via try/except for JSONDecodeError, IOError
  - Now also catches UnicodeDecodeError and ValueError for edge cases
  - Field validation with clamping for pokemon_id (1-386), generation (1-3), volume (0.0-1.0)
  - Input mode validation against ('keyboard', 'gpio')
  - `needs_correction` flag triggers save of corrected values

- **Code Improvements Made**:
  - Added `UnicodeDecodeError` and `ValueError` to exception handling for binary garbage files
  - Fixed volume validation to handle string type coercion safely (avoids TypeError on comparison)

- **Tasks 3-9 (Tests)**: Added 40 comprehensive pytest tests in 7 new test classes:
  - `TestCorruptionRecovery`: 8 tests for corrupt JSON handling (invalid, truncated, empty, binary)
  - `TestPokemonIdValidation`: 6 tests for pokemon_id clamping (above/below/zero/boundary)
  - `TestGenerationValidation`: 6 tests for generation clamping
  - `TestVolumeValidationOnLoad`: 5 tests for volume clamping including string coercion
  - `TestInputModeValidationOnLoad`: 6 tests for input mode validation
  - `TestValidationWarningLogs`: 5 tests for warning log format verification
  - `TestFullRecoveryFlow`: 4 tests for end-to-end recovery scenarios

- **All 495 project tests pass** with no regressions

### File List

- `src/state_manager.py` - Enhanced exception handling in `_load_state()` (lines 150-168, 197)
- `tests/test_state_manager.py` - Added 7 pytest test classes with 40 new tests

## Senior Developer Review (AI)

### Reviewer
King

### Date
November 29, 2025

### Outcome
✅ **APPROVE**

### Summary
Corruption recovery implementation is robust and comprehensive. All corruption scenarios (invalid JSON, truncated files, empty files, binary garbage) are handled gracefully with default fallback. Field validation properly clamps all values to valid ranges with appropriate warning logs.

### Acceptance Criteria Coverage

| AC # | Description | Status | Evidence |
|------|-------------|--------|----------|
| AC #1 | No crash on corrupted JSON | ✅ IMPLEMENTED | `state_manager.py:188-197` |
| AC #2 | Default values on corruption | ✅ IMPLEMENTED | `state_manager.py:192` |
| AC #3 | Corrupt file overwritten | ✅ IMPLEMENTED | `state_manager.py:194-196` |
| AC #4 | Warning logged for corruption | ✅ IMPLEMENTED | `state_manager.py:189` |
| AC #5 | pokemon_id clamping | ✅ IMPLEMENTED | `state_manager.py:133-138` |
| AC #6 | generation clamping | ✅ IMPLEMENTED | `state_manager.py:141-146` |
| AC #7 | volume clamping | ✅ IMPLEMENTED | `state_manager.py:150-165` |
| AC #8 | input_mode reset to default | ✅ IMPLEMENTED | `state_manager.py:168-171` |
| AC #9 | Negative values clamped | ✅ IMPLEMENTED | Same clamping logic |
| AC #10 | App continues after recovery | ✅ IMPLEMENTED | `TestFullRecoveryFlow` |

**Summary:** 10 of 10 acceptance criteria fully implemented

### Task Completion Validation

| Task | Marked As | Verified As | Evidence |
|------|-----------|-------------|----------|
| Tasks 1-2 | ✅ Complete | ✅ Verified | Code review |
| Tasks 3-9 | ✅ Complete | ✅ Verified | 40 tests in 7 classes |

**Summary:** 9 of 9 tasks verified complete, 0 false completions

### Test Coverage
- **TestCorruptionRecovery:** 8 tests
- **TestPokemonIdValidation:** 6 tests
- **TestGenerationValidation:** 6 tests
- **TestVolumeValidationOnLoad:** 5 tests
- **TestInputModeValidationOnLoad:** 6 tests
- **TestValidationWarningLogs:** 5 tests
- **TestFullRecoveryFlow:** 4 tests

### Code Quality Notes
- Implementation handles additional edge cases: UnicodeDecodeError, ValueError
- String-to-float coercion for volume values works correctly

### Action Items

**Advisory Notes:**
- Note: All 119 state manager tests pass
- Note: Robust handling of adversarial inputs (binary garbage, etc.)

## Change Log

| Date | Version | Description |
|------|---------|-------------|
| 2025-11-29 | 1.0.0 | Story drafted |
| 2025-11-29 | 1.1.0 | Implementation complete - code enhancements + 40 tests |
| 2025-11-29 | 1.2.0 | Senior Developer Review notes appended - APPROVED |
