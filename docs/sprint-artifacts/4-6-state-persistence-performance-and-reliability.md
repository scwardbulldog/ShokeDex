# Story 4.6: State Persistence Performance and Reliability

Status: ready-for-dev

## Story

As a user,
I want state saving to be fast and reliable,
so that it doesn't slow down navigation or cause data loss.

## Acceptance Criteria

1. **Save Operation Performance (AC #1)**
   - **Given** the application is running
   - **When** `StateManager.save_state()` is called
   - **Then** save operation completes in < 50ms
   - **And** no perceptible delay in screen transitions
   - **And** performance timing is logged at DEBUG level

2. **Load Operation Performance (AC #2)**
   - **Given** the application starts
   - **When** `StateManager._load_state()` executes
   - **Then** load operation completes in < 50ms
   - **And** performance timing is logged if exceeding target
   - **And** application boots to HomeScreen in < 5 seconds total

3. **Frame Rate Maintained During Navigation (AC #3)**
   - **Given** rapid navigation through screens
   - **When** screens call `on_exit()` triggering saves
   - **Then** frame rate remains 30+ FPS
   - **And** save operations don't cause stuttering or visual glitches
   - **And** user experience remains smooth

4. **Atomic Write Pattern for Data Integrity (AC #4)**
   - **Given** a save operation is in progress
   - **When** `StateManager.save_state()` executes
   - **Then** state is written to `data/shokedex_state.json.tmp` first
   - **And** temp file is renamed to final path atomically
   - **And** no partial writes corrupt the state file
   - **And** interrupted writes leave the previous valid state intact

5. **Final State Save on Application Shutdown (AC #5)**
   - **Given** the application is running
   - **When** the user exits (clean shutdown via ESC or BACK on HomeScreen)
   - **Then** `cleanup()` in main.py calls `state_manager.save_state()`
   - **And** final state is written to file before exit
   - **And** "State saved successfully" message is logged/printed

6. **State Save on Screen Transitions (AC #6)**
   - **Given** a user is on HomeScreen
   - **When** the user navigates to DetailScreen (or vice versa)
   - **Then** the exiting screen's `on_exit()` triggers state save
   - **And** current pokemon_id and generation are persisted
   - **And** user can quit anytime with minimal data loss

7. **Graceful Handling of Save Failures (AC #7)**
   - **Given** a save operation fails (disk full, permissions, I/O error)
   - **When** `StateManager.save_state()` catches the exception
   - **Then** an error is logged: "Error saving state file: {error}"
   - **And** the application continues running without crash
   - **And** in-memory state remains valid for future save attempts

8. **Memory Stability During Repeated Saves (AC #8)**
   - **Given** the application runs for an extended session
   - **When** save_state() is called repeatedly (100+ times)
   - **Then** no memory leaks occur from save operations
   - **And** StateManager in-memory footprint remains < 10KB
   - **And** JSON file size remains stable (< 1KB for typical use)

9. **Performance Logging for Monitoring (AC #9)**
   - **Given** performance monitoring is enabled
   - **When** save/load operations execute
   - **Then** operations exceeding 50ms log a WARNING with timing
   - **And** successful fast operations log at DEBUG level
   - **And** timing format: "{operation}() took {ms:.2f}ms (target: <50ms)"

10. **Startup Performance Validation (AC #10)**
    - **Given** the application starts from cold boot
    - **When** StateManager and screens initialize
    - **Then** total startup time to HomeScreen is < 5 seconds
    - **And** state loading contributes < 50ms to startup time
    - **And** startup is tested on actual Raspberry Pi hardware

## Tasks / Subtasks

- [ ] **Task 1: Verify Save Operation Performance (AC #1, #9)**
  - [ ] 1.1: Review `save_state()` timing code (lines 200-230 in state_manager.py)
  - [ ] 1.2: Verify `time.perf_counter()` is used for accurate measurement
  - [ ] 1.3: Verify DEBUG log for successful saves, WARNING log if > 50ms
  - [ ] 1.4: Profile save_state() on Raspberry Pi SD card

- [ ] **Task 2: Verify Load Operation Performance (AC #2, #9)**
  - [ ] 2.1: Review `_load_state()` timing code (lines 102-197 in state_manager.py)
  - [ ] 2.2: Verify timing measurement wraps entire load operation
  - [ ] 2.3: Verify WARNING log if load exceeds 50ms target
  - [ ] 2.4: Profile _load_state() on Raspberry Pi SD card

- [ ] **Task 3: Verify Atomic Write Pattern (AC #4)**
  - [ ] 3.1: Review save_state() writes to temp file first
  - [ ] 3.2: Verify Path.replace() is used for atomic rename
  - [ ] 3.3: Test interrupted write scenario (simulate power loss)
  - [ ] 3.4: Verify original file intact if write fails mid-operation

- [ ] **Task 4: Verify Shutdown Save Flow (AC #5)**
  - [ ] 4.1: Review main.py cleanup() calls state_manager.save_state()
  - [ ] 4.2: Verify cleanup() is in finally block (runs even on exception)
  - [ ] 4.3: Verify "State saved successfully" message appears on exit
  - [ ] 4.4: Test shutdown saves with various exit scenarios

- [ ] **Task 5: Verify Screen Transition Saves (AC #6)**
  - [ ] 5.1: Review HomeScreen.on_exit() saves state
  - [ ] 5.2: Review DetailScreen.on_exit() saves state
  - [ ] 5.3: Verify state updates are saved before screen transitions
  - [ ] 5.4: Test rapid screen transitions maintain state

- [ ] **Task 6: Verify Save Failure Handling (AC #7)**
  - [ ] 6.1: Review save_state() exception handling
  - [ ] 6.2: Verify IOError is caught and logged
  - [ ] 6.3: Verify function returns False on failure
  - [ ] 6.4: Verify app continues running after save failure

- [ ] **Task 7: Write Performance Tests (AC #1, #2, #3, #10)**
  - [ ] 7.1: Test `test_save_state_under_50ms()` - measure and assert timing
  - [ ] 7.2: Test `test_load_state_under_50ms()` - measure and assert timing
  - [ ] 7.3: Test `test_rapid_saves_maintain_fps()` - simulate navigation
  - [ ] 7.4: Test `test_startup_time_under_5_seconds()` - full boot measurement

- [ ] **Task 8: Write Atomic Write Tests (AC #4)**
  - [ ] 8.1: Test `test_temp_file_created_during_save()` - check .tmp file exists
  - [ ] 8.2: Test `test_temp_file_renamed_to_final()` - verify atomic rename
  - [ ] 8.3: Test `test_original_intact_on_write_failure()` - simulate failure
  - [ ] 8.4: Test `test_no_partial_writes()` - verify all-or-nothing

- [ ] **Task 9: Write Memory Stability Tests (AC #8)**
  - [ ] 9.1: Test `test_repeated_saves_no_memory_leak()` - 100+ save cycles
  - [ ] 9.2: Test `test_state_file_size_stable()` - verify < 1KB
  - [ ] 9.3: Test `test_in_memory_footprint_stable()` - verify < 10KB
  - [ ] 9.4: Use psutil to track memory before/after save cycles

- [ ] **Task 10: Write Integration Tests (AC #5, #6)**
  - [ ] 10.1: Test `test_shutdown_saves_state()` - exit app, verify file updated
  - [ ] 10.2: Test `test_screen_transition_saves_state()` - navigate, check file
  - [ ] 10.3: Test `test_save_failure_continues_operation()` - simulate failure

## Dev Notes

### Existing Implementation Review

Performance timing is already implemented in `src/state_manager.py`:

**Save Timing (lines 200-230 in `save_state()`):**
```python
import time
start_time = time.perf_counter()
# ... save operations ...
elapsed_ms = (time.perf_counter() - start_time) * 1000
if elapsed_ms > 50:
    logger.warning(f"save_state() took {elapsed_ms:.2f}ms (target: <50ms)")
else:
    logger.debug(f"save_state() completed in {elapsed_ms:.2f}ms")
```

**Load Timing (lines 102-197 in `_load_state()`):**
```python
start_time = time.perf_counter()
# ... load operations ...
elapsed_ms = (time.perf_counter() - start_time) * 1000
if elapsed_ms > 50:
    logger.warning(f"_load_state() took {elapsed_ms:.2f}ms (target: <50ms)")
else:
    logger.debug(f"_load_state() completed in {elapsed_ms:.2f}ms")
```

**Atomic Write Pattern (in `save_state()`):**
```python
# Atomic write pattern: write to temp file then rename
temp_file = Path(str(self.state_file) + '.tmp')

# Write to temporary file
with open(temp_file, 'w', encoding='utf-8') as f:
    json.dump(self.state, f, indent=2, ensure_ascii=False)

# Atomic rename (POSIX systems guarantee atomicity)
temp_file.replace(self.state_file)
```

**Shutdown Save (in main.py cleanup()):**
```python
def cleanup(self):
    """Clean up resources before exit."""
    print("Shutting down...")
    
    # Save state
    if self.state_manager.save_state():
        print("State saved successfully")
```

### This Story's Focus

This story is primarily a **verification and performance testing story**. The implementation exists; the focus is:
1. **Verify** timing code is correct and covers all operations
2. **Profile** on actual Raspberry Pi hardware for realistic measurements
3. **Write performance tests** that assert timing targets
4. **Write memory stability tests** for long-running sessions
5. **Document** the reliability guarantees

### Performance Targets Summary

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| save_state() | < 50ms | time.perf_counter() |
| _load_state() | < 50ms | time.perf_counter() |
| Total startup | < 5 seconds | Application timer |
| Frame rate during saves | 30+ FPS | PerformanceMonitor |
| Memory footprint | < 10KB | psutil memory_info() |
| State file size | < 1KB | os.path.getsize() |

### Project Structure Notes

**Files to Verify:**
- `src/state_manager.py` - Lines 200-230 (save timing), Lines 102-197 (load timing)
- `src/main.py` - Lines 270-285 (cleanup/shutdown)
- `src/ui/home_screen.py` - on_exit() state save
- `src/ui/detail_screen.py` - on_exit() state save

**Test Files:**
- `tests/test_state_manager.py` - Add `TestPerformance` class
- `tests/test_performance_monitor.py` - Existing performance tests to reference

### Learnings from Previous Stories

**From Story 4.5: State File Corruption Recovery (Status: ready-for-dev)**

- **Atomic Write Pattern Verified**: temp file + Path.replace() confirmed
- **Exception Handling**: IOError caught and logged, function returns False
- **File Size**: State file remains small (< 1KB typical)

[Source: docs/sprint-artifacts/4-5-state-file-corruption-recovery.md#Existing-Implementation-Review]

**From Story 4.3: Boot to HomeScreen Behavior (Status: done)**

- **Shutdown Flow Verified**: cleanup() in finally block
- **save_state() Called on Exit**: "State saved successfully" printed
- **Boot Behavior**: Always boots to HomeScreen with last viewed Pokémon

[Source: docs/sprint-artifacts/4-3-boot-to-homescreen-behavior.md#main.py-Boot-Sequence]

### Testing Strategy

Per project testing standards (`TESTING.md`):
- Use `@pytest.mark.performance` for performance tests
- Use psutil for memory tracking
- Profile on actual Raspberry Pi hardware for realistic I/O
- Use `time.perf_counter()` for high-precision timing
- Consider using `pytest-benchmark` for formal benchmarking

### Raspberry Pi Testing Considerations

Per hardware_guide.md and pi_optimization_guide.md:
- SD card I/O is slower than SSD - validate 50ms target on actual hardware
- Run performance tests multiple times to account for I/O variance
- Test during idle and under load conditions
- Consider testing on both Raspberry Pi 3B+ and 4B models

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-3-state-persistence.md#Performance]
- [Source: docs/sprint-artifacts/tech-spec-epic-3-state-persistence.md#Reliability/Availability]
- [Source: docs/architecture.md#StateManager-Integration]
- [Source: docs/epics.md#Story-4.6]
- [Source: src/state_manager.py - lines 200-230]
- [Source: src/main.py - lines 270-285]

## Dev Agent Record

### Context Reference

- [Story Context XML](./4-6-state-persistence-performance-and-reliability.context.xml)

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
