# Story 1.1: Project Foundation Setup

Status: ready-for-dev

## Story

As a developer,
I want the project structure, dependencies, and core managers initialized,
So that all subsequent features can be built on a solid foundation.

## Acceptance Criteria

1. **Core Manager Initialization (AC #1)**
   - **Given** a fresh development environment
   - **When** the application is initialized
   - **Then** all core managers (StateManager, InputManager, ScreenManager, SpriteLoader) are instantiated as singletons
   - **And** the database connection is established and validated
   - **And** all required directories exist (data/, assets/sprites/, etc.)
   - **And** configuration is loaded from environment or defaults

2. **Application Startup (AC #2)**
   - **Given** core managers are initialized
   - **When** the application starts
   - **Then** the application can start without errors
   - **And** HomeScreen is set as the initial screen
   - **And** the main game loop runs at 30+ FPS

## Tasks / Subtasks

- [ ] **Task 1: Initialize Core Managers** (AC: #1)
  - [ ] Implement StateManager as singleton with JSON persistence in `data/shokedex_state.json`
  - [ ] Implement InputManager with keyboard/GPIO abstraction using InputAction enum
  - [ ] Implement ScreenManager with screen stack navigation pattern
  - [ ] Implement SpriteLoader with LRU cache (max 50 sprites)
  - [ ] Add graceful degradation if GPIO unavailable (keyboard fallback)

- [ ] **Task 2: Database Connection** (AC: #1)
  - [ ] Initialize database connection in main.py startup
  - [ ] Validate schema exists and is correct version
  - [ ] Add error handling for database connection failures
  - [ ] Test parameterized query pattern is enforced

- [ ] **Task 3: Directory Structure Setup** (AC: #1)
  - [ ] Create data/ directory if missing
  - [ ] Create assets/sprites/ directory structure if missing
  - [ ] Validate sprite assets are accessible
  - [ ] Log warnings for missing directories or assets

- [ ] **Task 4: Configuration Loading** (AC: #1)
  - [ ] Load configuration from environment variables or config file
  - [ ] Set defaults for: display resolution, target FPS, input mode
  - [ ] Validate configuration values (resolution, FPS > 0, etc.)
  - [ ] Log loaded configuration for debugging

- [ ] **Task 5: Application Lifecycle** (AC: #2)
  - [ ] Create main.py entry point with pygame initialization
  - [ ] Initialize ScreenManager with HomeScreen as initial screen
  - [ ] Implement main game loop at 30+ FPS target
  - [ ] Add proper cleanup in finally block (save state, close DB)
  - [ ] Test startup completes without errors

- [ ] **Task 6: Testing** (AC: #1, #2)
  - [ ] Unit test: StateManager singleton pattern
  - [ ] Unit test: InputManager keyboard/GPIO abstraction
  - [ ] Unit test: SpriteLoader LRU cache eviction
  - [ ] Integration test: Full application startup
  - [ ] Performance test: Verify 30+ FPS in game loop

## Dev Notes

### Architecture Context

This story establishes the foundational architecture patterns that all subsequent stories will build upon:

**Manager Pattern:**
- All managers use singleton pattern accessed via ScreenManager
- Managers are instantiated once in main.py and passed to ScreenManager
- Screens access managers through `self.screen_manager.state_manager`, etc.
- Never create new manager instances - always use injected singletons

**Screen Lifecycle:**
- All screens extend base Screen class
- Lifecycle: `__init__()` → `on_enter()` → `render()` loop → `handle_input()` → `on_exit()`
- HomeScreen is the initial screen (always boot to browse view)
- ScreenManager handles screen stack for navigation

**Database Pattern:**
- SQLite database at `data/pokedex.db`
- **Always use parameterized queries** - never string formatting
- Connection managed by Database class using context manager pattern
- Schema validation on startup

**Input Abstraction:**
- InputManager converts keyboard/GPIO to InputAction enum
- Actions: LEFT, RIGHT, UP, DOWN, SELECT, BACK
- Supports runtime switching between keyboard and GPIO modes
- Keyboard fallback when GPIO unavailable (development mode)

### Component Locations

Based on architecture.md and existing project structure:

- **Main entry:** `src/main.py`
- **Managers:** `src/state_manager.py`, `src/input_manager.py`, `src/audio_manager.py`
- **Screens:** `src/ui/screen_manager.py`, `src/ui/screen.py`, `src/ui/home_screen.py`
- **Data:** `src/data/database.py`, `data/pokedex.db`
- **Assets:** `assets/sprites/thumb/`, `assets/sprites/detail/`
- **Sprite Loading:** `src/ui/sprite_loader.py`

### Technical Constraints

**Performance Requirements:**
- Main loop must maintain 30+ FPS on Raspberry Pi 3B+ (NFR-P1)
- Button press response < 100ms (NFR-P2)
- Startup time < 5 seconds from power-on to HomeScreen (NFR-P3)

**Hardware Constraints:**
- Raspberry Pi 3B+: 1GB RAM, ARM Cortex-A53 CPU
- Small LCD displays: 480x320 to 800x480 resolution
- Limited processing power vs. desktop - optimize rendering

**Security Requirements:**
- Parameterized SQL queries only (prevent SQL injection)
- Never use string formatting for database queries
- Validate all user inputs before processing

**Reliability Requirements:**
- Graceful error handling for all edge cases
- No crashes from missing files or corrupted state
- Fallback to safe defaults when configuration invalid

### Testing Strategy

Follow existing test patterns in `tests/` directory:

**Unit Tests:**
- Test manager singleton behavior (only one instance)
- Test InputManager action mapping (keyboard → InputAction)
- Test SpriteLoader cache eviction (LRU with 50-sprite limit)
- Test StateManager JSON persistence (save/load cycle)

**Integration Tests:**
- Test full application startup sequence
- Test manager initialization and injection
- Test HomeScreen initialization and rendering
- Test database connection and schema validation

**Performance Tests:**
- Measure FPS in main game loop (target: 30+ FPS)
- Measure startup time (target: < 5 seconds)
- Profile memory usage during extended operation
- Test on actual Raspberry Pi 3B+ hardware

### References

- [Source: docs/PRD.md#Project-Classification] - Technology stack: Python 3.11+, pygame 2.5.0+, SQLite, gpiozero
- [Source: docs/architecture.md#Decision-Summary] - Manager singleton pattern, screen lifecycle
- [Source: docs/architecture.md#Project-Structure] - Component organization and file locations
- [Source: docs/sprint-artifacts/tech-spec-epic-1-generation-navigation.md#System-Architecture-Alignment] - Manager integration points
- [Source: docs/epics.md#Story-1.1] - Acceptance criteria and prerequisites

## Dev Agent Record

### Context Reference

- `docs/sprint-artifacts/1-1-project-foundation-setup.context.xml`

### Agent Model Used

_Not yet implemented_

### Debug Log References

_To be added during implementation_

### Completion Notes List

_To be added after story completion:_
- New patterns/services created
- Architectural deviations or decisions
- Technical debt deferred
- Warnings/recommendations for next story
- Interfaces/methods created for reuse

### File List

_To be added during implementation:_
- NEW: List newly created files
- MODIFIED: List modified files
- DELETED: List deleted files (if any)
