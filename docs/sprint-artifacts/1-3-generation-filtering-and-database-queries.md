# Story 1.3: Generation Filtering and Database Queries

Status: ready-for-dev

## Story

As a user,
I want to see only Pokémon from the current generation,
So that I can browse regional Pokédexes just like in the games.

## Acceptance Criteria

1. **Generation Boundary Filtering (AC #1)**
   - **Given** a user is browsing Pokémon
   - **When** a specific generation is selected
   - **Then** only Pokémon within that generation's ID range are displayed
   - **And** Kanto shows Pokémon #1-151 (Bulbasaur through Mew)
   - **And** Johto shows Pokémon #152-251 (Chikorita through Celebi)
   - **And** Hoenn shows Pokémon #252-386 (Treecko through Deoxys)

2. **Database Query Performance (AC #2)**
   - **Given** the application queries Pokémon by generation
   - **When** the database query executes
   - **Then** the query uses parameterized BETWEEN statement for security
   - **And** query completes in < 50ms
   - **And** scroll position resets to first Pokémon when switching generations

## Tasks / Subtasks

- [ ] **Task 1: Define Generation Range Constants** (AC: #1)
  - [ ] Create `GENERATION_RANGES` constant dict in shared config or HomeScreen
  - [ ] Map generations to ID boundaries: {1: (1,151), 2: (152,251), 3: (252,386)}
  - [ ] Add `GENERATION_NAMES` constant: {1: "Kanto", 2: "Johto", 3: "Hoenn"}
  - [ ] Document generation boundary rationale (matches original game regions)

- [ ] **Task 2: Implement Database Query Method** (AC: #1, #2)
  - [ ] Add `Database.get_pokemon_by_generation(generation: int)` method
  - [ ] Use SQL: `SELECT id, name, sprite_path FROM pokemon WHERE id BETWEEN ? AND ? ORDER BY id`
  - [ ] Use `GENERATION_RANGES[generation]` to get (start, end) parameters
  - [ ] Return `List[Dict]` with keys: id, name, sprite_path
  - [ ] Validate generation parameter (must be 1, 2, or 3) - raise ValueError if invalid

- [ ] **Task 3: Integrate Query in HomeScreen** (AC: #1, #2)
  - [ ] Add `HomeScreen._load_pokemon_by_generation(generation: int)` method
  - [ ] Call `db.get_pokemon_by_generation(self.current_generation)` in `on_enter()`
  - [ ] Store results in `self.pokemon_list` for rendering
  - [ ] Update `self.current_generation` attribute tracking current filter
  - [ ] Reset scroll position to index 0 when generation changes

- [ ] **Task 4: Scroll Position Reset Logic** (AC: #2)
  - [ ] In `_switch_generation()` method, set `self.selected_index = 0`
  - [ ] Update displayed Pokémon to first in new generation
  - [ ] Ensure position counter reflects first Pokémon (#001/151 for Kanto)
  - [ ] Clear any sprite pre-loading cache when switching generations

- [ ] **Task 5: SQL Security Validation** (AC: #2)
  - [ ] Verify all queries use parameterized statements with `?` placeholders
  - [ ] Never use string formatting or f-strings in SQL queries
  - [ ] Add input validation for generation parameter before database call
  - [ ] Write unit test attempting SQL injection (should fail safely)

- [ ] **Task 6: Testing** (AC: #1, #2)
  - [ ] Unit test: `test_generation_ranges_constant()` - verify dict values correct
  - [ ] Unit test: `test_get_pokemon_by_generation_kanto()` - returns 151 Pokémon
  - [ ] Unit test: `test_get_pokemon_by_generation_johto()` - returns 100 Pokémon  
  - [ ] Unit test: `test_get_pokemon_by_generation_hoenn()` - returns 135 Pokémon
  - [ ] Unit test: `test_parameterized_query_safety()` - SQL injection prevention
  - [ ] Unit test: `test_invalid_generation_raises_error()` - generation 0 or 4 raises ValueError
  - [ ] Performance test: `test_query_performance()` - measure query time, assert < 50ms
  - [ ] Integration test: `test_home_screen_filters_by_generation()` - full flow

## Dev Notes

### Learnings from Previous Story

**From Story 1-1-project-foundation-setup (Status: ready-for-dev)**

This story builds directly on the foundation established in Story 1.1:

- **Database Connection Available**: `Database` class is initialized in main.py with context manager pattern ready to use
- **Architecture Pattern Established**: Use parameterized queries with `cursor.execute("SELECT ... WHERE id BETWEEN ? AND ?", (start, end))`  
- **Security Requirement**: All SQL queries must use parameterized statements - no string formatting
- **HomeScreen Class Ready**: Story 1.1 created HomeScreen as initial screen with basic structure
- **Performance Target**: All operations must maintain 30+ FPS on Raspberry Pi 3B+

**Key Files to Reference:**
- `src/data/database.py` - Add new `get_pokemon_by_generation()` method here
- `src/ui/home_screen.py` - Integrate filtering logic in this existing screen
- `tests/test_database.py` - Add generation filtering tests to existing test suite

[Source: docs/sprint-artifacts/1-1-project-foundation-setup.md#Dev-Notes]

### Architecture Context

This story implements the **Generation Navigation Architecture** pattern from the architecture document.

**Generation Boundaries (Architectural Constraint):**
- Hardcoded ID ranges per architecture decision (ADR-005)
- Kanto: National Dex #1-151 (Bulbasaur to Mew)
- Johto: National Dex #152-251 (Chikorita to Celebi)
- Hoenn: National Dex #252-386 (Treecko to Deoxys)
- Rationale: Matches original Pokémon game regions and mental model

**Database Query Pattern (Security Requirement):**
```python
# ✅ CORRECT - Parameterized query (architecture mandated)
GENERATION_RANGES = {
    1: (1, 151),
    2: (152, 251),
    3: (252, 386)
}

def get_pokemon_by_generation(generation: int):
    if generation not in GENERATION_RANGES:
        raise ValueError(f"Invalid generation: {generation}")
    
    start, end = GENERATION_RANGES[generation]
    cursor = db.execute(
        "SELECT id, name, sprite_path FROM pokemon WHERE id BETWEEN ? AND ? ORDER BY id",
        (start, end)
    )
    return cursor.fetchall()

# ❌ WRONG - String formatting (SQL injection risk, violates architecture)
cursor.execute(f"SELECT * FROM pokemon WHERE id BETWEEN {start} AND {end}")
```

**Performance Requirement:**
- Query must complete in < 50ms (per NFR-P1, NFR-P2)
- Database already indexed on id column (primary key)
- 151 rows (Kanto) should return instantly on Raspberry Pi

**Integration with StateManager:**
- This story focuses on database filtering logic
- Story 1.5 will add StateManager integration for persistence
- For now, generation defaults to 1 (Kanto) if not specified

### Component Locations

**Files to Modify:**
- `src/data/database.py` - Add `get_pokemon_by_generation()` method
- `src/ui/home_screen.py` - Add `_load_pokemon_by_generation()` method
- `tests/test_database.py` - Add generation filtering unit tests
- `tests/test_home_screen.py` - Add integration tests (if file exists)

**Constants to Define:**
- `GENERATION_RANGES` - Can live in `src/ui/home_screen.py` or create `src/config.py` if shared
- `GENERATION_NAMES` - Display names for UI rendering

**No New Files Required:**
- All work happens in existing modules from Story 1.1

### Data Schema

**Database Table: `pokemon`**
```sql
CREATE TABLE pokemon (
    id INTEGER PRIMARY KEY,           -- National Dex number (1-386)
    name TEXT NOT NULL,               -- Pokémon name (e.g., "Pikachu")
    height REAL,                      -- Height in meters
    weight REAL,                      -- Weight in kilograms
    generation INTEGER,               -- Generation number (1-3)
    sprite_path TEXT                  -- Relative path to sprite
);

-- Query pattern for generation filtering:
-- WHERE id BETWEEN ? AND ? covers generation boundaries
-- id is PRIMARY KEY → automatically indexed → fast query
```

**Query Return Format:**
```python
# List[Tuple[int, str, str]]
[
    (1, "Bulbasaur", "assets/sprites/thumb/001.png"),
    (2, "Ivysaur", "assets/sprites/thumb/002.png"),
    # ... 149 more for Kanto
]
```

**Conversion to HomeScreen Format:**
```python
pokemon_list = [
    {"id": row[0], "name": row[1], "sprite_path": row[2]}
    for row in query_results
]
```

### Technical Constraints

**Performance:**
- Query time < 50ms (measured on Raspberry Pi 3B+)
- No N+1 queries - single query per generation load
- Use ORDER BY id to maintain Dex number sequence

**Security:**
- Parameterized queries MANDATORY (prevents SQL injection)
- Input validation on generation parameter (1-3 only)
- No user input reaches SQL query directly

**Reliability:**
- Graceful handling of empty results (shouldn't happen with valid data)
- Validate generation parameter before database call
- Log query failures with context for debugging

**Memory:**
- Kanto query returns 151 rows × ~100 bytes each = ~15KB
- Negligible memory impact (well within Pi's 1GB RAM)
- No need for pagination at this story level

### Testing Strategy

**Unit Tests (Fast, Isolated):**
```python
# tests/test_database.py
def test_get_pokemon_by_generation_kanto(test_database):
    """Kanto generation should return Pokémon #1-151."""
    results = test_database.get_pokemon_by_generation(1)
    
    assert len(results) == 151
    assert results[0][0] == 1    # First is Bulbasaur
    assert results[-1][0] == 151 # Last is Mew

def test_get_pokemon_by_generation_johto(test_database):
    """Johto generation should return Pokémon #152-251."""
    results = test_database.get_pokemon_by_generation(2)
    
    assert len(results) == 100
    assert results[0][0] == 152  # First is Chikorita
    assert results[-1][0] == 251 # Last is Celebi

def test_parameterized_query_safety(test_database):
    """Query must use parameterized statements (SQL injection test)."""
    # Attempt SQL injection
    malicious_gen = "1; DROP TABLE pokemon; --"
    
    with pytest.raises(ValueError):
        test_database.get_pokemon_by_generation(malicious_gen)
    
    # Verify table still exists
    assert test_database.table_exists("pokemon")
```

**Integration Tests (HomeScreen + Database):**
```python
# tests/test_home_screen.py
def test_home_screen_loads_kanto_on_startup(mock_screen_manager):
    """HomeScreen should default to Kanto generation on startup."""
    screen = HomeScreen(mock_screen_manager)
    screen.on_enter()
    
    assert screen.current_generation == 1
    assert len(screen.pokemon_list) == 151
    assert screen.pokemon_list[0]["name"] == "Bulbasaur"

def test_switching_generation_resets_scroll(mock_screen_manager):
    """Scroll position should reset when changing generation."""
    screen = HomeScreen(mock_screen_manager)
    screen.on_enter()
    
    # Scroll to middle of Kanto
    screen.selected_index = 75
    
    # Switch to Johto
    screen._switch_generation(1)  # direction = 1 (next)
    
    # Should reset to first Pokémon
    assert screen.selected_index == 0
    assert screen.pokemon_list[0]["name"] == "Chikorita"
```

**Performance Tests:**
```python
# tests/test_performance.py
def test_generation_query_performance(test_database):
    """Generation queries must complete in < 50ms."""
    import time
    
    for generation in [1, 2, 3]:
        start = time.time()
        results = test_database.get_pokemon_by_generation(generation)
        duration = time.time() - start
        
        assert duration < 0.050, f"Gen {generation} query took {duration*1000:.1f}ms (>50ms)"
        assert len(results) > 0
```

**Test Data Setup:**
Use pytest fixture with in-memory SQLite:
```python
# tests/conftest.py
@pytest.fixture
def test_database():
    """Provide test database with Gen 1-3 Pokémon seeded."""
    db = Database(":memory:")
    db.initialize_schema()
    db.seed_pokemon_data()  # Load all 386 Pokémon
    yield db
    db.close()
```

### Edge Cases to Handle

1. **Invalid Generation Parameter:**
   - Input: generation = 0 or 4
   - Expected: Raise ValueError with clear message
   - Test: `test_invalid_generation_raises_error()`

2. **Empty Database:**
   - Input: generation = 1 but no Pokémon in database
   - Expected: Return empty list, log warning
   - Test: `test_empty_database_returns_empty_list()`

3. **Missing sprite_path Column:**
   - Input: Database schema missing sprite_path
   - Expected: Return id and name only, log warning
   - Test: Query should still work with SELECT id, name

4. **SQL Injection Attempt:**
   - Input: malicious string in generation parameter
   - Expected: ValueError raised, no SQL executed
   - Test: `test_parameterized_query_safety()`

5. **Rapid Generation Switching:**
   - Input: User presses L/R rapidly 10 times
   - Expected: Each query completes, no race conditions
   - Test: Integration test with rapid calls

### References

- [Source: docs/PRD.md#FR2.1-Generation-Based-Browsing] - Generation organization requirement
- [Source: docs/architecture.md#Generation-Navigation-Architecture] - Database query pattern
- [Source: docs/architecture.md#Database-Access-Pattern] - Context manager usage
- [Source: docs/architecture.md#ADR-005-Generation-Based-Navigation] - Architectural decision rationale
- [Source: docs/sprint-artifacts/tech-spec-epic-1-generation-navigation.md#Data-Models-and-Contracts] - Query return format
- [Source: docs/epics.md#Story-1.3] - Original acceptance criteria and tasks
- [Source: docs/database_schema.md] - Full pokemon table schema (if exists)

## Dev Agent Record

### Context Reference

- Story Context XML: `docs/sprint-artifacts/1-3-generation-filtering-and-database-queries.context.xml`

### Agent Model Used

_Not yet implemented_

### Debug Log References

_To be added during implementation_

### Completion Notes List

_To be added after story completion:_
- New database methods created (get_pokemon_by_generation)
- Query performance measured on target hardware
- SQL injection prevention validated
- Integration with HomeScreen completed
- Unit test coverage percentage
- Any deviations from original design

### File List

_To be added during implementation:_
- MODIFIED: `src/data/database.py` (add get_pokemon_by_generation method)
- MODIFIED: `src/ui/home_screen.py` (add _load_pokemon_by_generation method)  
- MODIFIED: `tests/test_database.py` (add generation filtering tests)
- NEW: `tests/test_home_screen.py` (if doesn't exist yet)
- MODIFIED: `src/config.py` or add GENERATION_RANGES constant (if centralized config chosen)
