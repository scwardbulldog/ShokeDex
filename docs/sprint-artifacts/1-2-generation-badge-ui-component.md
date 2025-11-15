# Story 1.2: Generation Badge UI Component

Status: ready-for-dev

## Story

As a user,
I want to see which generation (Kanto/Johto/Hoenn) I'm currently browsing,
So that I know which region's Pokémon I'm viewing.

## Acceptance Criteria

1. **Badge Visibility and Positioning (AC #1)**
   - **Given** HomeScreen is displaying Pokémon from a specific generation
   - **When** the screen renders
   - **Then** a generation badge is visible in the top-left or top-center area
   - **And** the badge shows the current region name ("KANTO", "JOHTO", or "HOENN")
   - **And** the badge shows position counter format: "#025/151" (current Pokémon number / total in generation)

2. **Badge Styling and Visual Design (AC #2)**
   - **Given** the generation badge is displayed
   - **When** the badge renders
   - **Then** the badge uses holographic blue styling with background rgba(26, 47, 74, 0.9)
   - **And** the badge has a 2px solid electric blue (#00d4ff) border
   - **And** corner accent lines are visible (45° cuts per UX spec)
   - **And** the badge displays the appropriate region logo (Pokéball for Kanto, GS Ball for Johto, Master Ball for Hoenn)

3. **Badge Asset Fallback (AC #3)**
   - **Given** badge logo assets may be unavailable
   - **When** badge assets are missing
   - **Then** a text-only badge is displayed with region name and counter
   - **And** a warning is logged indicating missing assets
   - **And** the application continues without crashing
   - **And** badge maintains consistent styling (background, border, text)

## Tasks / Subtasks

- [ ] **Task 1: Create GenerationBadge Component** (AC: #1, #2)
  - [ ] Create `GenerationBadge` class or component in `src/ui/home_screen.py` or separate module
  - [ ] Accept parameters: generation (1-3), current_pokemon_id, total_pokemon_count
  - [ ] Implement render method returning pygame.Surface
  - [ ] Position badge in top-left or top-center (coordinate TBD based on HomeScreen layout)
  - [ ] Ensure badge doesn't overlap Pokémon sprite or other UI elements

- [ ] **Task 2: Define Generation Display Data** (AC: #1)
  - [ ] Create GENERATION_NAMES constant: {1: "KANTO", 2: "JOHTO", 3: "HOENN"}
  - [ ] Create GENERATION_RANGES constant: {1: (1,151), 2: (152,251), 3: (252,386)}
  - [ ] Create GENERATION_TOTALS constant: {1: 151, 2: 100, 3: 135}
  - [ ] Add logic to format position counter: f"#{pokemon_id:03d}/{total:03d}"

- [ ] **Task 3: Implement Badge Styling** (AC: #2)
  - [ ] Create badge background: pygame.Surface with rgba(26, 47, 74, 0.9)
  - [ ] Draw 2px electric blue (#00d4ff) border using pygame.draw.rect()
  - [ ] Add corner accent lines (45° diagonal cuts) - use pygame.draw.line()
  - [ ] Use Orbitron Bold font (24px) for generation name
  - [ ] Use Share Tech Mono font (18px) for position counter
  - [ ] Ensure text is white (#ffffff) for readability

- [ ] **Task 4: Load Generation Logo Assets** (AC: #2, #3)
  - [ ] Define logo asset paths:
    - `assets/icons/badge_kanto.png` for Generation 1
    - `assets/icons/badge_johto.png` for Generation 2
    - `assets/icons/badge_hoenn.png` for Generation 3
  - [ ] Load logo using Pillow/pygame image loading
  - [ ] Scale logo to fit within badge (approximately 40x40px)
  - [ ] Position logo on left side of badge

- [ ] **Task 5: Implement Asset Fallback Logic** (AC: #3)
  - [ ] Wrap logo loading in try/except block
  - [ ] On FileNotFoundError or image loading error:
    - Log warning: f"Generation badge asset not found: {asset_path}"
    - Set logo_surface to None
    - Continue rendering badge with text-only
  - [ ] Test fallback by temporarily removing asset files

- [ ] **Task 6: Integrate Badge into HomeScreen** (AC: #1, #2, #3)
  - [ ] Add `self.generation_badge = GenerationBadge(...)` in HomeScreen.__init__()
  - [ ] Update badge in HomeScreen._switch_generation() when generation changes
  - [ ] Update badge in HomeScreen scrolling logic when pokemon_id changes
  - [ ] Call badge.render() in HomeScreen.render() method
  - [ ] Blit badge surface to screen at configured position

- [ ] **Task 7: Testing** (AC: #1, #2, #3)
  - [ ] Unit test: GenerationBadge rendering for each generation (1, 2, 3)
  - [ ] Unit test: Badge text formatting with various pokemon_ids
  - [ ] Unit test: Asset fallback behavior (mock missing files)
  - [ ] Visual test: Verify badge appearance matches UX spec (colors, borders, fonts)
  - [ ] Integration test: Badge updates correctly when switching generations
  - [ ] Integration test: Badge position counter updates during scrolling

## Dev Notes

### Learnings from Previous Story

**From Story 1-1-project-foundation-setup (Status: ready-for-dev)**

The foundation story established:
- **Core Managers Available**: StateManager, InputManager, ScreenManager, SpriteLoader all initialized as singletons
- **HomeScreen Structure**: Base Screen lifecycle (on_enter, render, handle_input, on_exit) implemented
- **Manager Access Pattern**: Access managers via `self.screen_manager.state_manager` (injected singletons)
- **Database Ready**: SQLite connection established with parameterized query pattern enforced
- **Directory Structure**: `data/` and `assets/sprites/` directories validated on startup

**Key Interfaces to Reuse:**
- **HomeScreen class**: Located at `src/ui/home_screen.py` - extend with badge rendering
- **Colors module**: Use `src/ui/colors.py` for holographic blue palette constants
- **GENERATION_RANGES**: Define in HomeScreen or shared constants module per tech spec

**Architectural Patterns Established:**
- Singleton managers accessed via ScreenManager
- Screen lifecycle: `__init__() → on_enter() → render() loop → on_exit()`
- Component-based UI: Badge should be a composable component within HomeScreen
- Graceful degradation: Fallback to text-only if assets unavailable

**Technical Debt to Note:**
- Generation badge assets (3 PNG files) need to be created/sourced separately
- Font files (Orbitron, Share Tech Mono) availability should be verified

[Source: docs/sprint-artifacts/1-1-project-foundation-setup.md#Dev-Agent-Record]

### Architecture Context

**Generation Badge Component Design:**

The GenerationBadge is a UI component that displays the current browsing context (which of the three regions the user is viewing). It communicates state without requiring interaction.

**Component Responsibilities:**
1. Display current region name (KANTO/JOHTO/HOENN)
2. Show position within region (#025/151)
3. Display region-appropriate logo icon
4. Apply holographic blue visual styling
5. Update in real-time as user scrolls or switches generations

**Integration with HomeScreen:**
- HomeScreen maintains current_generation (1, 2, or 3) state
- HomeScreen tracks current_pokemon_id for position counter
- Badge is rendered as part of HomeScreen.render() pipeline
- Badge receives updates when generation changes or pokemon_id changes

**Visual Hierarchy:**
- Badge positioned to not obscure main Pokémon sprite (hero element)
- Badge size: approximately 200x60px (flexible based on testing)
- Badge is informational - not interactive (no button handlers needed)

### Component Locations

Based on project structure and architecture patterns:

- **Badge Implementation**: Add to `src/ui/home_screen.py` as GenerationBadge class
  - Alternative: Create `src/ui/components/generation_badge.py` for separation
  - Decision: Start inline in home_screen.py, extract if component grows large
- **Constants**: Define GENERATION_NAMES, GENERATION_RANGES in HomeScreen class or config
- **Assets**: Store badge logos in `assets/icons/badge_kanto.png`, etc.
- **Colors**: Use existing `src/ui/colors.py` for holographic blue palette
- **Fonts**: Load from `assets/fonts/` directory (Orbitron, Share Tech Mono)

### Technical Constraints

**Performance:**
- Badge rendering must not impact 30+ FPS target (NFR-P1)
- Pre-render badge text surfaces in on_enter() or cache rendered surfaces
- Only re-render badge when generation or pokemon_id changes (not every frame)

**Visual Requirements (from UX Design Spec):**
- Background: rgba(26, 47, 74, 0.9) - dark blue with transparency
- Border: 2px solid electric blue (#00d4ff)
- Corner accents: 45° diagonal lines, 10px length, electric blue
- Text colors: White (#ffffff) for primary text, ice blue (#a8e6ff) for secondary
- Fonts: Orbitron Bold (24px) for region name, Share Tech Mono (18px) for counter

**Asset Requirements:**
- 3 badge logo files needed (Kanto, Johto, Hoenn)
- Logos should be 40x40px PNG with transparency
- Logo design: Pokéball (Kanto), GS Ball (Johto), Master Ball (Hoenn) per tech spec
- Fallback: Text-only badge if assets unavailable

**Positioning:**
- Top-left or top-center placement
- Margin: 16px from screen edges (per UX spec padding standard)
- Z-order: Badge renders above background, below any modal overlays

### Testing Strategy

**Unit Tests (pytest):**
```python
def test_generation_badge_kanto():
    """Test badge displays Kanto with correct text."""
    badge = GenerationBadge(generation=1, pokemon_id=25, total=151)
    assert badge.generation_name == "KANTO"
    assert badge.position_text == "#025/151"

def test_generation_badge_johto():
    """Test badge displays Johto with correct formatting."""
    badge = GenerationBadge(generation=2, pokemon_id=152, total=100)
    assert badge.generation_name == "JOHTO"
    assert badge.position_text == "#152/100"

def test_badge_asset_fallback():
    """Test badge falls back to text-only when assets missing."""
    # Mock missing file
    with patch('pygame.image.load', side_effect=FileNotFoundError):
        badge = GenerationBadge(generation=1, pokemon_id=1, total=151)
        surface = badge.render()
        assert surface is not None  # Badge still renders
```

**Visual Tests:**
- Run application and verify badge appearance matches UX mockup
- Check colors: background, border, text against spec
- Verify corner accent lines are visible and correct angle
- Test with all three generations (Kanto, Johto, Hoenn)
- Test text-only fallback by removing asset files

**Integration Tests:**
```python
def test_badge_updates_on_generation_switch():
    """Test badge updates when user switches generation."""
    # Navigate HomeScreen, press R button
    # Verify badge text changes from KANTO to JOHTO

def test_badge_position_counter_updates():
    """Test position counter updates during scrolling."""
    # Scroll from Pokemon #25 to #26
    # Verify badge shows #026/151
```

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-1-generation-navigation.md#Acceptance-Criteria] - AC #1: Generation Badge Display requirements
- [Source: docs/ux-design-specification.md#Visual-Identity] - Holographic blue color palette and styling
- [Source: docs/architecture.md#Screen-Lifecycle] - Screen rendering pipeline and component integration
- [Source: docs/epics.md#Story-1.2] - Original story definition and acceptance criteria
- [Source: docs/PRD.md#FR6] - Generation Badge Display functional requirement

## Dev Agent Record

### Context Reference

- `docs/sprint-artifacts/1-2-generation-badge-ui-component.context.xml`

### Agent Model Used

_Not yet implemented_

### Debug Log References

_To be added during implementation_

### Completion Notes List

_To be added after story completion:_
- Badge component structure and location (inline vs. separate module)
- Asset availability status (logos found or text-only fallback used)
- Performance impact of badge rendering (FPS measurements)
- Any styling adjustments from UX spec (if needed)
- Recommendations for Story 1.3 (generation filtering integration)

### File List

_To be added during implementation:_
- NEW: List newly created files (badge component, asset files if created)
- MODIFIED: `src/ui/home_screen.py` (badge integration)
- MODIFIED: `src/ui/colors.py` (if badge colors added)
