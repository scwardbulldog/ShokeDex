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
  - [ ] 1.1: Add `current_tab` enum property with values: INFO, STATS, EVOLUTION
  - [ ] 1.2: Add `tab_state_cache` dict to store last tab per pokemon_id (session only)
  - [ ] 1.3: Initialize current_tab to INFO on on_enter()
  - [ ] 1.4: Implement `_switch_tab(direction)` method for L/R navigation
  - [ ] 1.5: Add tab wrapping logic (INFO ← EVOLUTION, EVOLUTION → INFO)
  - [ ] 1.6: Update on_exit() to reset current_tab to INFO

- [ ] **Task 2: Refactor Rendering into Tab Methods (AC: #2, #3, #4)**
  - [ ] 2.1: Create `_render_info_tab(surface)` method
  - [ ] 2.2: Move sprite and description panel to _render_info_tab()
  - [ ] 2.3: Create `_render_stats_tab(surface)` method
  - [ ] 2.4: Move sprite, stat bars, type badges, physical measurements to _render_stats_tab()
  - [ ] 2.5: Create `_render_evolution_tab(surface)` method
  - [ ] 2.6: Move evolution panel rendering to _render_evolution_tab()
  - [ ] 2.7: Adjust sprite size to 96x96 in evolution tab for better layout
  - [ ] 2.8: Update main render() method to call tab-specific render based on current_tab

- [ ] **Task 3: Implement Tab Indicator UI (AC: #7)**
  - [ ] 3.1: Create `_render_tab_indicator(surface)` method
  - [ ] 3.2: Position indicator at bottom of screen (y = screen_height - 30)
  - [ ] 3.3: Render three tab labels: "Info | Stats | Evolution"
  - [ ] 3.4: Highlight current tab with electric blue (#00d4ff)
  - [ ] 3.5: Render inactive tabs with ice blue (#a8e6ff)
  - [ ] 3.6: Add subtle separator lines between tab labels

- [ ] **Task 4: Update Input Handling (AC: #5, #6, #9)**
  - [ ] 4.1: Update handle_input() to intercept L/R button presses
  - [ ] 4.2: L button: call _switch_tab(direction=-1)
  - [ ] 4.3: R button: call _switch_tab(direction=1)
  - [ ] 4.4: Verify Up/Down buttons continue to navigate between Pokémon
  - [ ] 4.5: Preserve current_tab when navigating between Pokémon
  - [ ] 4.6: Verify B button exits to HomeScreen

- [ ] **Task 5: Optimize Layout for Each Tab (AC: #2, #3, #4)**
  - [ ] 5.1: Verify Info tab fits in 320px (sprite + description text)
  - [ ] 5.2: Verify Stats tab fits in 320px (sprite + stats + types + measurements)
  - [ ] 5.3: Verify Evolution tab fits in 320px (smaller sprite + evolution panel)
  - [ ] 5.4: Adjust spacing/padding if needed to prevent overflow
  - [ ] 5.5: Test on both 480x320 and 800x480 displays

- [ ] **Task 6: Write Unit and Integration Tests (AC: #5, #6, #10)**
  - [ ] 6.1: Test `test_tab_switching_left_right()` verifies L/R cycle through tabs
  - [ ] 6.2: Test `test_tab_wrapping()` verifies Info ← Evolution and Evolution → Info
  - [ ] 6.3: Test `test_pokemon_navigation_preserves_tab()` verifies Up/Down maintain tab
  - [ ] 6.4: Test `test_tab_indicator_highlights_current()` verifies visual state
  - [ ] 6.5: Test `test_info_tab_renders_description()` verifies Info tab completeness
  - [ ] 6.6: Test `test_stats_tab_renders_all_content()` verifies Stats tab
  - [ ] 6.7: Test `test_evolution_tab_renders_panel()` verifies Evolution tab
  - [ ] 6.8: Performance test: `test_tab_switch_under_100ms()`

- [ ] **Task 7: Visual Testing and Polish (AC: #1, #7, #10)**
  - [ ] 7.1: Test tab switching on both 480x320 and 800x480 displays
  - [ ] 7.2: Verify tab indicator is visible and clear on small screens
  - [ ] 7.3: Verify no content overflow on any tab
  - [ ] 7.4: Compare visual styling with existing holographic theme
  - [ ] 7.5: Profile rendering performance for each tab
  - [ ] 7.6: Generate updated demo screenshots showing tab navigation

## Dev Notes

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

### Tab Navigation Pattern

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
