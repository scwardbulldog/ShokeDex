# Story 5.7: Tab-Based Detail View for Information Organization

Status: drafted

## Story

As a user,
I want to navigate between different information tabs on the DetailScreen using L/R buttons,
so that I can view stats, evolution, and description information without a cramped layout.

## Background

**Problem Identified:** After implementing Story 5.1 (Evolution Chain Display), the DetailScreen has ~635px of vertical content competing for only 320px of screen space on small displays. This creates a cramped, cluttered experience that violates the "at-a-glance" design principle.

**UX Decision (Dec 6, 2025):** Implement tab-based navigation to organize DetailScreen content into three focused tabs, each fitting comfortably within the viewport.

## Acceptance Criteria

1. **Three Tab Structure (AC #1)**
   - **Given** user is viewing DetailScreen
   - **When** screen loads
   - **Then** three tabs are available: "Info", "Stats", "Evolution"
   - **And** "Info" tab is shown by default
   - **And** each tab fits within 320px vertical space without overflow

2. **Info Tab Content (AC #2)**
   - **Given** user is on "Info" tab
   - **When** tab renders
   - **Then** Pokémon sprite (128x128) is displayed
   - **And** full Pokédex description text is shown
   - **And** description uses proper text wrapping and formatting
   - **And** all content fits within viewport without scrolling

3. **Stats Tab Content (AC #3)**
   - **Given** user is on "Stats" tab
   - **When** tab renders
   - **Then** Pokémon sprite (128x128) is displayed
   - **And** six stat bars with values are shown (HP, Attack, Defense, Sp.Atk, Sp.Def, Speed)
   - **And** type badges (1-2) are displayed
   - **And** physical measurements (height, weight) are shown
   - **And** all content fits within viewport without scrolling

4. **Evolution Tab Content (AC #4)**
   - **Given** user is on "Evolution" tab
   - **When** tab renders
   - **Then** Pokémon sprite (96x96, smaller to make room) is displayed
   - **And** evolution chain panel shows 3-stage horizontal layout
   - **And** evolution requirements are displayed (from Story 5.1)
   - **And** current Pokémon is highlighted with cyan glow
   - **And** all content fits within viewport without scrolling

5. **L/R Button Tab Switching (AC #5)**
   - **Given** user is viewing any tab
   - **When** user presses L button
   - **Then** view switches to previous tab (wraps around: Info ← Evolution)
   - **And** tab transition is smooth (< 100ms)
   - **When** user presses R button
   - **Then** view switches to next tab (wraps around: Evolution → Info)
   - **And** tab transition is smooth (< 100ms)

6. **Up/Down Pokémon Navigation (AC #6)**
   - **Given** user is viewing any tab
   - **When** user presses Up button
   - **Then** DetailScreen navigates to next Pokémon (existing behavior)
   - **And** current tab selection is preserved
   - **When** user presses Down button
   - **Then** DetailScreen navigates to previous Pokémon (existing behavior)
   - **And** current tab selection is preserved

7. **Tab Indicator Display (AC #7)**
   - **Given** user is viewing any tab
   - **When** tab indicator renders
   - **Then** three tab labels are shown at bottom: "Info | Stats | Evolution"
   - **And** current tab is highlighted with electric blue color (#00d4ff)
   - **And** inactive tabs use ice blue color (#a8e6ff)
   - **And** indicator uses holographic styling consistent with UI

8. **State Persistence Across Tabs (AC #8)**
   - **Given** user switches from Pokémon A to Pokémon B
   - **When** returning to Pokémon A
   - **Then** last viewed tab for Pokémon A is preserved
   - **And** tab state is maintained in session memory (not persisted to disk)

9. **B Button Behavior (AC #9)**
   - **Given** user is on any tab
   - **When** user presses B button
   - **Then** DetailScreen exits and returns to HomeScreen
   - **And** tab state is reset to "Info" for next viewing

10. **Rendering Performance (AC #10)**
    - **Given** user switches tabs
    - **When** new tab renders
    - **Then** render completes within 100ms
    - **And** frame rate maintains 30+ FPS during transition
    - **And** no visual stuttering or lag occurs

## Tasks / Subtasks

- [ ] **Task 1: Add Tab State Management to DetailScreen (AC: #1, #5, #8)**
  - [ ] 1.1: Create DetailTab enum in detail_screen.py with values: INFO, STATS, EVOLUTION
  - [ ] 1.2: Add `current_tab: DetailTab` property to DetailScreen, default to INFO
  - [ ] 1.3: Add `tab_state_cache: Dict[int, DetailTab]` for session-only tab memory
  - [ ] 1.4: Update on_enter() to restore last tab from cache: `self.current_tab = self.tab_state_cache.get(self.pokemon_id, DetailTab.INFO)`
  - [ ] 1.5: Implement `_switch_tab(direction: int)` method with modulo wrapping
  - [ ] 1.6: Update on_exit() to save current tab to cache AND reset to INFO for next session
  - [ ] 1.7: Test tab state persistence across Pokémon navigation in same session

- [ ] **Task 2: Refactor Rendering into Tab Methods (AC: #2, #3, #4)**
  - [ ] 2.1: Create `_render_info_tab(surface: pygame.Surface)` method
  - [ ] 2.2: Move sprite rendering (128x128) and description panel to _render_info_tab()
  - [ ] 2.3: Optimize Info tab vertical layout: header (40px) + sprite (140px) + description (80px) = ~260px
  - [ ] 2.4: Create `_render_stats_tab(surface: pygame.Surface)` method
  - [ ] 2.5: Move sprite, stat bars (6), type badges, physical measurements to _render_stats_tab()
  - [ ] 2.6: Optimize Stats tab layout: side-by-side sprite+stats to save vertical space
  - [ ] 2.7: Create `_render_evolution_tab(surface: pygame.Surface)` method
  - [ ] 2.8: Move EvolutionPanel.render() call to _render_evolution_tab()
  - [ ] 2.9: Reduce sprite to 96x96 in Evolution tab (save 32px vertical space)
  - [ ] 2.10: Update main render() method with conditional: `if self.current_tab == DetailTab.INFO: self._render_info_tab(surface)` etc.
  - [ ] 2.11: Verify each tab fits within 320px vertical constraint

- [ ] **Task 3: Implement Tab Indicator UI (AC: #7)**
  - [ ] 3.1: Create `_render_tab_indicator(surface: pygame.Surface)` method
  - [ ] 3.2: Position indicator at bottom: `y = self.screen_height - 30`
  - [ ] 3.3: Calculate center position for three tab labels with spacing
  - [ ] 3.4: Render tab labels: ["Info", "Stats", "Evolution"] with Rajdhani font, 14px
  - [ ] 3.5: Highlight current tab with ELECTRIC_BLUE (#00d4ff) and bold font
  - [ ] 3.6: Render inactive tabs with ICE_BLUE (#a8e6ff) and regular font
  - [ ] 3.7: Draw separator lines between tabs: `pygame.draw.line()` with ICE_BLUE
  - [ ] 3.8: Pre-render tab label surfaces in on_enter() for performance (optional optimization)

- [ ] **Task 4: Update Input Handling (AC: #5, #6, #9)**
  - [ ] 4.1: Update handle_input(action) to intercept LEFT and RIGHT actions
  - [ ] 4.2: LEFT action (L button): call `self._switch_tab(direction=-1)`
  - [ ] 4.3: RIGHT action (R button): call `self._switch_tab(direction=1)`
  - [ ] 4.4: Verify UP action still navigates to next Pokémon (preserve existing behavior)
  - [ ] 4.5: Verify DOWN action still navigates to previous Pokémon (preserve existing behavior)
  - [ ] 4.6: Ensure current_tab is NOT reset during UP/DOWN navigation (tab preserved)
  - [ ] 4.7: Verify BACK action (B button) still exits to HomeScreen
  - [ ] 4.8: Test rapid L/R presses for smooth tab switching without lag

- [ ] **Task 5: Optimize Layout for Each Tab (AC: #2, #3, #4)**
  - [ ] 5.1: Measure Info tab vertical usage: header + sprite (128x128) + description text
  - [ ] 5.2: Verify Info tab ≤ 320px total (target: ~290px with margins)
  - [ ] 5.3: Measure Stats tab vertical usage: header + sprite + stats + types + physical
  - [ ] 5.4: Use side-by-side layout for sprite and stats if needed to save vertical space
  - [ ] 5.5: Verify Stats tab ≤ 320px total (target: ~280px with margins)
  - [ ] 5.6: Measure Evolution tab vertical usage: header + sprite (96x96) + evolution panel
  - [ ] 5.7: Verify Evolution tab ≤ 320px total (target: ~270px with margins)
  - [ ] 5.8: Adjust padding/margins if any tab exceeds 320px
  - [ ] 5.9: Test all three tabs on 480x320 display (actual hardware or emulator)
  - [ ] 5.10: Test all three tabs on 800x480 display for visual consistency

- [ ] **Task 6: Write Unit and Integration Tests (AC: #5, #6, #10)**
  - [ ] 6.1: Test `test_detail_tab_enum_values()` verifies enum has INFO, STATS, EVOLUTION
  - [ ] 6.2: Test `test_tab_switching_right_cycles_forward()` verifies R button: INFO → STATS → EVOLUTION → INFO
  - [ ] 6.3: Test `test_tab_switching_left_cycles_backward()` verifies L button: INFO → EVOLUTION → STATS → INFO
  - [ ] 6.4: Test `test_tab_wrapping_forward()` verifies EVOLUTION + R → INFO
  - [ ] 6.5: Test `test_tab_wrapping_backward()` verifies INFO + L → EVOLUTION
  - [ ] 6.6: Test `test_pokemon_navigation_preserves_current_tab()` verifies Up/Down maintain tab state
  - [ ] 6.7: Test `test_tab_state_cache_remembers_per_pokemon()` verifies Pikachu on STATS, Bulbasaur on INFO, return to Pikachu shows STATS
  - [ ] 6.8: Test `test_tab_resets_to_info_on_exit()` verifies B button exit resets to INFO
  - [ ] 6.9: Test `test_tab_indicator_highlights_current_tab()` verifies correct color highlighting
  - [ ] 6.10: Test `test_info_tab_renders_sprite_and_description()` verifies Info tab completeness
  - [ ] 6.11: Test `test_stats_tab_renders_all_components()` verifies Stats tab has stats, types, physical
  - [ ] 6.12: Test `test_evolution_tab_renders_evolution_panel()` verifies Evolution tab calls EvolutionPanel.render()
  - [ ] 6.13: Performance test: `test_tab_switch_completes_under_100ms()` marked with `@pytest.mark.performance`
  - [ ] 6.14: Add all tests to tests/test_detail_screen.py

- [ ] **Task 7: Visual Testing and Polish (AC: #1, #7, #10)**
  - [ ] 7.1: Update demo_screenshot.py to capture all three tabs for sample Pokémon
  - [ ] 7.2: Generate screenshots for Pikachu on all three tabs (Info, Stats, Evolution)
  - [ ] 7.3: Generate screenshots for Eevee on Evolution tab (branching evolution test)
  - [ ] 7.4: Generate screenshots for Ditto on Evolution tab ("No evolutions" message test)
  - [ ] 7.5: Verify tab indicator is clearly visible and readable on all screenshots
  - [ ] 7.6: Verify no content overflow or cutoff on any tab
  - [ ] 7.7: Verify holographic styling consistency: ELECTRIC_BLUE highlights, ICE_BLUE inactive
  - [ ] 7.8: Profile tab switching performance with `time.perf_counter()` (target: <100ms)
  - [ ] 7.9: Test on both 480x320 and 800x480 displays using demo_evolution_display.py
  - [ ] 7.10: Compare visual output to UX design specification for alignment

- [ ] **Task 8: Documentation and Code Comments (AC: ALL)**
  - [ ] 8.1: Add docstring to DetailTab enum explaining tab purpose and order
  - [ ] 8.2: Add docstring to _switch_tab() explaining direction parameter and wrapping
  - [ ] 8.3: Add docstrings to _render_info_tab(), _render_stats_tab(), _render_evolution_tab()
  - [ ] 8.4: Add inline comments explaining tab state cache lifecycle
  - [ ] 8.5: Add inline comment explaining why current_tab is preserved during Pokémon navigation
  - [ ] 8.6: Update Dev Notes with implementation learnings and edge cases discovered
  - [ ] 8.7: Document tab switching performance metrics in Completion Notes

## Dev Notes

### Learnings from Previous Stories

**From Story 5.1: Three-Stage Evolution Chain Display (Status: done)**

**UX Review Finding That Led to This Story:**
- After implementing Story 5.1, DetailScreen has ~635px of vertical content competing for only 320px of screen space
- **Root Cause:** Evolution panel (150px) added to already-full screen (header, sprite, stats, types, physical, description)
- **Impact:** Cramped layout, information competing for space, violates "at-a-glance" design principle
- **Decision:** Implement tab-based navigation to organize information (Stats / Evolution / Info tabs)

**EvolutionPanel Integration:**
- EvolutionPanel is inner class within DetailScreen in `src/ui/detail_screen.py`
- Component lifecycle: `__init__()` → `load_data()` → `load_sprites()` → `render()`
- Already optimized: <200ms first render, <5ms cached
- **This story:** Move EvolutionPanel.render() into Evolution tab conditional block

**Performance Metrics from Story 5.1:**
- Database query: <50ms ✅
- Evolution panel render: <200ms first load, <5ms cached ✅
- Frame rate maintained at 30+ FPS
- **Tab switching target:** <100ms (faster than full panel render)

[Source: docs/sprint-artifacts/5-1-three-stage-evolution-chain-display.md#Dev-Agent-Record]

**From Story 5.2: Branching Evolution Display (Status: review)**

**Branching Layout Challenges:**
- Branching evolutions (Eevee) require more vertical space than 3-stage chains
- Vertical stacking or fan-out layout for 5+ branches
- **This story:** Evolution tab provides dedicated space for complex evolution displays
- Smaller sprite (96x96 vs 128x128) allows more room for evolution panel

**Component Pattern:**
- EvolutionPanel handles both 3-stage and branching layouts
- Conditional rendering based on evolution data structure
- **This story:** No changes to EvolutionPanel logic, just conditional display in Evolution tab

[Source: docs/sprint-artifacts/5-2-branching-evolution-display.md]

**From Story 5.3: Single-Stage Pokémon Handling (Status: drafted)**

**Empty Evolution Handling:**
- Single-stage Pokémon (Ditto, Farfetch'd, Absol) display "No evolutions" message
- EvolutionPanel checks `len(self.evolutions) == 0` before rendering
- **This story:** Evolution tab will show "No evolutions" message for single-stage Pokémon
- Panel always visible (never hidden) for visual consistency

**Message Styling:**
- "No evolutions" text: Rajdhani 16px, ice blue (#a8e6ff)
- Centered within panel
- **This story:** Same styling applies in Evolution tab context

[Source: docs/sprint-artifacts/5-3-single-stage-pokemon-handling.md]

**From Story 3.6: Adjacent Pokémon Navigation (Status: done)**

**Up/Down Navigation Pattern:**
- Up/Down buttons already working for Pokémon navigation
- Fade transitions between Pokémon established
- Wrapping logic: #1 wraps to #386, #386 wraps to #1
- **This story:** Preserve Up/Down behavior, add L/R for tab switching
- Navigation should maintain current tab when switching Pokémon

**Performance Targets:**
- Navigation transition: <300ms (database query + sprite load + render)
- **This story:** Tab switching faster (<100ms, no data reload)

[Source: docs/sprint-artifacts/3-6-adjacent-pokemon-navigation-in-detail-view.md]

**From Story 3.7: Detail View Performance (Status: done)**

**Holographic Styling Standards:**
- Panel background: `rgba(26, 47, 74, 0.9)` (DARK_BLUE)
- Border: `2px solid #00d4ff` (ELECTRIC_BLUE)
- Text colors: `#e8f4f8` (HOLOGRAM_WHITE), `#a8e6ff` (ICE_BLUE)
- Fonts: Rajdhani for UI text, Share Tech Mono for numeric data
- **This story:** Tab indicator uses same holographic styling

**Performance Benchmarks:**
- DetailScreen total render: <300ms including all panels
- Individual panel render: <50ms cached
- **This story:** Tab switching <100ms (render only current tab)

**Pre-rendering Optimization:**
- Static text surfaces pre-rendered in on_enter()
- Cached surfaces reused each frame
- **This story:** Pre-render tab indicator labels for efficiency

[Source: docs/sprint-artifacts/3-7-detail-view-performance-and-visual-polish.md]

### Existing Implementation to Build On

**From Story 3.6: Adjacent Pokémon Navigation (Status: done)**
- Up/Down button handling already working for Pokémon navigation
- Fade transitions between Pokémon established
- This story preserves that behavior, adds L/R for tab switching

**From Story 5.1: Evolution Chain Display (Status: review)**
- EvolutionPanel component ready to move into Evolution tab
- Rendering already optimized and tested
- Just needs to be conditionally rendered based on current_tab

**From Story 3.7: Detail View Performance (Status: done)**
- Holographic styling pattern established
- Panel rendering performance targets met
- Tab indicator can reuse existing color constants

### Implementation Approach

**Tab Enum Definition:**
```python
from enum import Enum

class DetailTab(Enum):
    INFO = 0
    STATS = 1
    EVOLUTION = 2
```

**State Management:**
```python
def __init__(self, screen_manager, pokemon_id):
    super().__init__(screen_manager)
    self.pokemon_id = pokemon_id
    self.current_tab = DetailTab.INFO  # Default to Info tab
    self.tab_state_cache = {}  # {pokemon_id: DetailTab} - session memory only
    
def on_enter(self):
    # Restore last tab for this Pokémon if exists
    self.current_tab = self.tab_state_cache.get(self.pokemon_id, DetailTab.INFO)
    # ... existing data loading code
    
def on_exit(self):
    # Save current tab for this Pokémon
    self.tab_state_cache[self.pokemon_id] = self.current_tab
    # Reset to default for next viewing session
    self.current_tab = DetailTab.INFO
```

**Conditional Rendering Logic:**
```python
def render(self, surface):
    # Render header (always visible)
    self._render_header(surface)
    
    # Render current tab content
    if self.current_tab == DetailTab.INFO:
        self._render_info_tab(surface)
    elif self.current_tab == DetailTab.STATS:
        self._render_stats_tab(surface)
    elif self.current_tab == DetailTab.EVOLUTION:
        self._render_evolution_tab(surface)
    
    # Render tab indicator (always visible)
    self._render_tab_indicator(surface)
```

**Tab Switching Logic:**
```python
def _switch_tab(self, direction):
    """Switch to next/previous tab with wrapping.
    
    Args:
        direction: 1 for next (R button), -1 for previous (L button)
    """
    tab_order = [DetailTab.INFO, DetailTab.STATS, DetailTab.EVOLUTION]
    current_index = tab_order.index(self.current_tab)
    new_index = (current_index + direction) % len(tab_order)
    self.current_tab = tab_order[new_index]
```

**Input Handling:**
```python
def handle_input(self, action: InputAction):
    if action == InputAction.LEFT:
        # L button: previous tab
        self._switch_tab(direction=-1)
    elif action == InputAction.RIGHT:
        # R button: next tab
        self._switch_tab(direction=1)
    elif action == InputAction.UP:
        # Navigate to next Pokémon, preserve tab
        next_id = self._get_next_pokemon_id()
        self.pokemon_id = next_id
        self._load_pokemon_data()
        # current_tab is preserved
    elif action == InputAction.DOWN:
        # Navigate to previous Pokémon, preserve tab
        prev_id = self._get_previous_pokemon_id()
        self.pokemon_id = prev_id
        self._load_pokemon_data()
        # current_tab is preserved
    elif action == InputAction.BACK:
        # B button: exit to HomeScreen
        self.screen_manager.pop()
```

**Tab Indicator Rendering:**
```python
def _render_tab_indicator(self, surface):
    """Render tab indicator at bottom of screen."""
    y = self.screen_height - 30
    x_center = self.screen_width // 2
    
    tabs = ["Info", "Stats", "Evolution"]
    tab_width = 80
    spacing = 10
    
    for i, tab_name in enumerate(tabs):
        x = x_center - (len(tabs) * (tab_width + spacing)) // 2 + i * (tab_width + spacing)
        
        # Determine color based on current tab
        if i == self.current_tab.value:
            color = Colors.ELECTRIC_BLUE  # #00d4ff
            font = self.font_bold
        else:
            color = Colors.ICE_BLUE  # #a8e6ff
            font = self.font_regular
        
        # Render tab label
        text_surface = font.render(tab_name, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        surface.blit(text_surface, text_rect)
        
        # Draw separator if not last tab
        if i < len(tabs) - 1:
            separator_x = x + tab_width // 2 + spacing // 2
            pygame.draw.line(surface, Colors.ICE_BLUE, 
                           (separator_x, y - 10), (separator_x, y + 10), 1)
```

**Performance Optimization:**
- Pre-render tab indicator labels in on_enter() or first render
- Cache rendered surfaces to avoid re-creating each frame
- Only render current tab's content (skip other tabs)
- Result: <100ms tab switch time (only rendering, no data loading)

### Project Structure Notes

**Files to Modify:**
- `src/ui/detail_screen.py` - Major refactor to add tab system (~200-300 lines added/changed)
  - Add DetailTab enum
  - Add tab state management (current_tab, tab_state_cache)
  - Refactor render() into _render_info_tab(), _render_stats_tab(), _render_evolution_tab()
  - Add _switch_tab() method
  - Add _render_tab_indicator() method
  - Update handle_input() for L/R tab switching
  - Preserve Up/Down Pokémon navigation

- `tests/test_detail_screen.py` - Add comprehensive tab switching tests (~100-150 lines)
  - Test tab switching with L/R buttons
  - Test tab wrapping (INFO ← EVOLUTION, EVOLUTION → INFO)
  - Test Pokémon navigation preserves tab
  - Test tab indicator rendering
  - Test each tab's content rendering
  - Performance test for tab switching

**No New Files Created:**
- All changes are modifications to existing DetailScreen class
- DetailTab enum added within detail_screen.py (could be separate file if preferred)

**Alignment with Architecture:**
- Extends existing Screen base class pattern
- Reuses EvolutionPanel component (no changes to component)
- Follows InputManager pattern for button handling
- Maintains holographic styling consistency
- No new architecture components introduced

**No Conflicts Detected:**
- L/R buttons currently unused on DetailScreen (safe to repurpose for tabs)
- Up/Down navigation preserved (Pokémon switching)
- B button behavior unchanged (exit to HomeScreen)
- Evolution panel logic unchanged (just conditional rendering)

### Edge Cases to Handle

**1. Tab Preservation During Pokémon Navigation:**
- User on Evolution tab, presses Up to next Pokémon
- Should remain on Evolution tab for new Pokémon
- Implementation: Don't reset current_tab during Pokémon navigation

**2. Tab Reset on Screen Exit:**
- User exits DetailScreen with B button
- Next time DetailScreen opens, should default to Info tab
- Implementation: Reset current_tab to INFO in on_exit()

**3. Single-Stage Pokémon on Evolution Tab:**
- User navigates to Ditto while on Evolution tab
- Should show "No evolutions" message (from Story 5.3)
- Implementation: EvolutionPanel already handles this, no changes needed

**4. Tab State Cache Management:**
- tab_state_cache grows unbounded during session
- Consider LRU cache or clear on HomeScreen return
- Implementation: Accept unbounded for now (max 386 entries), optimize if needed

**5. Rapid Tab Switching:**
- User rapidly presses L/R buttons
- Should handle smoothly without lag or skipped inputs
- Implementation: Debounce or queue inputs if needed

### Testing Strategy

**Unit Tests:**
- Tab enum and state management
- Tab switching logic with wrapping
- Tab indicator rendering
- Input handling for L/R buttons

**Integration Tests:**
- Full tab rendering on DetailScreen
- Pokémon navigation preserves tab
- Tab reset on screen exit
- Each tab content completeness

**Visual Tests:**
- Update demo_screenshot.py to capture all three tabs
- Verify layout fits on 480x320 displays
- Verify tab indicator visibility
- Compare against holographic styling standards

**Performance Tests:**
- Tab switch time <100ms
- Frame rate 30+ FPS during tab switching
- No memory leaks from tab state cache
- Verify tab switching faster than Pokémon navigation

### Story Dependencies and Implementation Order

**This story (5.7) has unique relationship with other Epic 5 stories:**

**Prerequisites (MUST be complete):**
- ✅ Story 5.1: Three-Stage Evolution Chain Display (done) - EvolutionPanel component exists
- ✅ Epic 3: Detail View Implementation (done) - Stats, description, sprite rendering exists

**Recommended Implementation Order:**

**Option A: Implement 5.7 BEFORE 5.2, 5.3, 5.4, 5.5, 5.6**
- **Pros:**
  - Solves vertical space problem immediately
  - Provides clean foundation for remaining evolution features
  - Evolution tab becomes dedicated space for complex evolution displays
  - Stories 5.2-5.6 can be developed and tested within Evolution tab context
- **Cons:**
  - Larger refactoring upfront
  - Affects multiple existing components

**Option B: Implement 5.7 AFTER 5.2, 5.3, 5.4, 5.5, 5.6**
- **Pros:**
  - Complete all evolution features with simpler vertical layout first
  - Tab refactoring is final polish step
  - Less churn during active development
- **Cons:**
  - DetailScreen remains cramped during Stories 5.2-5.6
  - May need to adjust evolution features after tab refactoring
  - Vertical space constraints complicate development

**Recommended: Option A (Implement 5.7 BEFORE remaining Epic 5 stories)**

**Rationale:**
1. Tab system provides dedicated Evolution tab space for complex features
2. Stories 5.2 (branching), 5.4 (requirements), 5.5 (navigation) benefit from extra vertical room
3. Prevents rework - evolution features developed once in final tab context
4. Maintains "at-a-glance" UX principle throughout Epic 5 development

**Impact on Other Stories:**

**Story 5.2: Branching Evolution Display**
- Benefits from Evolution tab's dedicated space
- Branching evolutions (Eevee with 5 branches) fit more comfortably
- No changes to EvolutionPanel logic needed

**Story 5.3: Single-Stage Pokémon Handling**
- "No evolutions" message displays in Evolution tab
- Component behavior unchanged, just conditional tab rendering

**Story 5.4: Evolution Requirement Display**
- Requirements display within Evolution tab
- More vertical space for detailed requirement explanations

**Story 5.5: Navigation to Evolution Relatives**
- A button navigation could work within Evolution tab context
- Or remains available for use (A button freed up by tab system)

**Story 5.6: Evolution System Performance**
- Tab switching adds performance metric (<100ms)
- Evolution tab rendering included in overall performance testing

**Decision Point for King:**
After reviewing this story, would you like to:
1. Implement Story 5.7 next (before Stories 5.4, 5.5, 5.6)?
2. Continue with Stories 5.4-5.6 first, then do 5.7 as polish?
3. Discuss implementation order with the team?

**Similar to Pokémon Games:**
- Pokémon Summary screens have multiple pages (Skills, Moves, Ribbons, etc.)
- L/R buttons cycle through pages
- Familiar pattern for target audience

**Button Mapping:**
- **L/R**: Tab switching (NEW behavior, currently unused on DetailScreen)
- **Up/Down**: Pokémon navigation (EXISTING behavior, preserved)
- **B**: Back to HomeScreen (EXISTING behavior, preserved)
- **A**: Future use (could navigate to evolution relative, etc.)

### Layout Optimization Strategy

**Info Tab (simplest, shown first):**
```
┌─────────────────────────────────────────┐
│  PIKACHU                           #025 │  ← Header (40px)
├──────────────────────────────────────────┤
│         [SPRITE 128x128]                │  ← Sprite (140px)
├─────────────────────────────────────────┤
│  When several of these Pokémon gather,  │
│  their electricity can build and cause  │  ← Description (80px)
│  lightning storms.                      │
├─────────────────────────────────────────┤
│  INFO | Stats | Evolution               │  ← Tab indicator (30px)
└─────────────────────────────────────────┘
Total: ~290px (fits in 320px ✓)
```

**Stats Tab (most dense):**
```
┌─────────────────────────────────────────┐
│  PIKACHU                           #025 │  ← Header (40px)
├──────────────┬──────────────────────────┤
│              │  HP       ▓▓▓▓▓░░░░░  35 │
│   [SPRITE]   │  Attack   ▓▓▓▓▓▓░░░░  55 │
│   128x128    │  Defense  ▓▓▓▓░░░░░░  40 │  ← Stats (120px)
│              │  Sp.Atk   ▓▓▓▓▓░░░░░  50 │
│              │  Sp.Def   ▓▓▓▓▓░░░░░  50 │
│              │  Speed    ▓▓▓▓▓▓▓▓▓░  90 │
├──────────────┴──────────────────────────┤
│  ⚡ ELECTRIC                            │  ← Types (30px)
│  Height: 0.4m    Weight: 6.0kg          │  ← Physical (25px)
├─────────────────────────────────────────┤
│  Info | STATS | Evolution               │  ← Tab indicator (30px)
└─────────────────────────────────────────┘
Total: ~245px (fits in 320px ✓)
```

**Evolution Tab (needs room for chain):**
```
┌─────────────────────────────────────────┐
│  PIKACHU                           #025 │  ← Header (40px)
├──────────┬──────────────────────────────┤
│          │  ┌──────┐    ┌──────┐       │
│ [SPRITE] │  │ #172 │───>│ #025 │───>   │
│  96x96   │  │PICHU │Lv? │PIKACHU│Stone│  ← Evolution panel (150px)
│          │  └──────┘    └──────┘       │
│          │     [Highlighted]            │
├──────────┴──────────────────────────────┤
│  Info | Stats | EVOLUTION               │  ← Tab indicator (30px)
└─────────────────────────────────────────┘
Total: ~220px (fits in 320px ✓)
```

### Performance Considerations

- Tab switching should be instant (< 100ms)
- No need to reload data when switching tabs (data already in memory)
- Only render current tab's content (conditional rendering)
- Tab indicator renders on all tabs (lightweight, < 5ms)

### Future Extensibility

This pattern makes it easy to add future tabs:
- **"Moves"** tab - shows learnable moves
- **"Abilities"** tab - shows abilities and effects
- **"Location"** tab - shows where to find in games

Tab system designed to scale to 5+ tabs without changes.

### Alignment with Architecture

- No new architecture components needed
- Extends existing DetailScreen class
- Reuses EvolutionPanel component (already implemented)
- Follows Screen lifecycle pattern (on_enter, render, handle_input)
- Maintains holographic styling consistency

### References

- [Source: docs/ux-design-specification.md#Detail-Screen]
- [Source: docs/sprint-artifacts/5-1-three-stage-evolution-chain-display.md#UX-Review-Finding]
- [Source: docs/sprint-artifacts/3-6-adjacent-pokemon-navigation-in-detail-view.md - Up/Down navigation pattern]
- [Source: docs/sprint-artifacts/3-7-detail-view-performance-and-visual-polish.md - Holographic styling]

## Dev Agent Record

### Context Reference

<!-- Context XML will be generated by story-context workflow -->

### Agent Model Used

<!-- Agent model name and version will be added here during implementation -->

### Debug Log References

<!-- Debug logs will be added here during implementation -->

### Completion Notes List

<!-- Completion notes will be added here during implementation -->

### File List

<!-- Modified/created files will be listed here during implementation -->

## Change Log

| Date | Version | Description |
|------|---------|-------------|
| 2025-12-06 | 1.0.0 | Story drafted by UX Designer (Sally) based on visual review findings from Story 5.1 |
| 2025-12-08 | 1.1.0 | Enhanced by SM agent (Bob) - added learnings from Stories 5.1-5.3, detailed implementation approach with code examples, expanded tasks with 60+ subtasks, added edge case handling, testing strategy, and comprehensive technical notes |
