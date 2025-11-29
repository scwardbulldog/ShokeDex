# Story 3.8: Home Screen Holographic Theme Alignment

Status: review

## Story

As a user,
I want the Home Screen to use the same holographic blue color scheme as the Detail Screen,
So that the visual experience feels cohesive and polished across all screens.

## Acceptance Criteria

1. **Background Color Update (AC #1)**
   - **Given** a user is on the Home Screen
   - **When** the screen renders
   - **Then** the background uses `DEEP_SPACE_BLACK` (#0a0e1a)
   - **And** the background does NOT use `DARK_GREEN` (#0f380f)
   - **And** the dark background provides sufficient contrast for all UI elements

2. **Grid Cell Border Styling (AC #2)**
   - **Given** the Home Screen displays the Pokémon grid
   - **When** grid cells render
   - **Then** cell borders use `ELECTRIC_BLUE` (#00d4ff) for consistency with Detail Screen panels
   - **And** border width matches Detail Screen panel styling (2px)
   - **And** borders are clearly visible against the dark background

3. **Selected Cell Highlighting (AC #3)**
   - **Given** a user is navigating the Pokémon grid
   - **When** a cell is selected/highlighted
   - **Then** the selected cell uses `DARK_BLUE` (#1a2f4a) background
   - **And** the selected cell has `BRIGHT_CYAN` (#4df7ff) border
   - **And** the selection is clearly distinguishable from non-selected cells
   - **And** the glow effect (if present) uses holographic colors

4. **Title Text Styling (AC #4)**
   - **Given** the Home Screen renders the title
   - **When** "ShokeDex" title displays
   - **Then** title uses `HOLOGRAM_WHITE` (#e8f4f8) color
   - **And** title remains readable and prominent against dark background

5. **Secondary Text Styling (AC #5)**
   - **Given** the Home Screen displays secondary information
   - **When** page indicator, view mode, and help text render
   - **Then** secondary text uses `ICE_BLUE` (#a8e6ff) color
   - **And** text includes: page indicator ("Page X/Y"), view mode ("View: All"), help text ("SELECT: View | START: Settings")
   - **And** all secondary text is readable against dark background

6. **Search/Filter Bar Styling (AC #6)**
   - **Given** the Home Screen displays the search/filter bar
   - **When** the bar and buttons render
   - **Then** buttons use holographic styling matching Detail Screen panels
   - **And** active button has `DARK_BLUE` (#1a2f4a) background with visible selection
   - **And** button borders use `ELECTRIC_BLUE` (#00d4ff)
   - **And** button text uses appropriate holographic colors (white for active, ice blue for inactive)

7. **Visual Transition Consistency (AC #7)**
   - **Given** a user navigates between Home Screen and Detail Screen
   - **When** transitioning between screens
   - **Then** no jarring color change occurs
   - **And** both screens share the same dark background (#0a0e1a)
   - **And** the holographic aesthetic is consistent across transitions

8. **Generation Badge Preservation (AC #8)**
   - **Given** the Generation Badge component already uses holographic colors
   - **When** the Home Screen theme is updated
   - **Then** the Generation Badge continues to render correctly
   - **And** no regression in badge styling (border, glow, text colors)
   - **And** badge remains visually integrated with new background

## Tasks / Subtasks

- [x] **Task 1: Update HomeScreen Background (AC #1)**
  - [x] 1.1: Modify `HomeScreen.render()` to use `Colors.DEEP_SPACE_BLACK` instead of `Colors.BACKGROUND`
  - [x] 1.2: Verify background renders correctly on 480x320 display

- [x] **Task 2: Update Grid Cell Styling (AC #2, #3)**
  - [x] 2.1: Update `_render_grid()` to use `Colors.ELECTRIC_BLUE` for cell borders
  - [x] 2.2: Update selected cell to use `Colors.DARK_BLUE` background
  - [x] 2.3: Update selected cell border to use `Colors.BRIGHT_CYAN`
  - [x] 2.4: Verify grid cells render correctly with new colors

- [x] **Task 3: Update Text Colors (AC #4, #5)**
  - [x] 3.1: Update title rendering to use `Colors.HOLOGRAM_WHITE`
  - [x] 3.2: Update page indicator text to use `Colors.ICE_BLUE`
  - [x] 3.3: Update view mode text to use `Colors.ICE_BLUE`
  - [x] 3.4: Update help text to use `Colors.ICE_BLUE`

- [x] **Task 4: Update Search/Filter Bar (AC #6)**
  - [x] 4.1: Update `_render_search_bar()` button backgrounds to use holographic colors
  - [x] 4.2: Update button borders to use `Colors.ELECTRIC_BLUE`
  - [x] 4.3: Update active/inactive button text colors

- [x] **Task 5: Verify Visual Consistency (AC #7, #8)**
  - [x] 5.1: Test transition between Home Screen and Detail Screen
  - [x] 5.2: Verify Generation Badge renders correctly against new background
  - [x] 5.3: Capture before/after screenshots for visual comparison
  - [x] 5.4: Test on target display resolution (480x320)

- [x] **Task 6: Update Color Constants (Optional Enhancement)**
  - [x] 6.1: Consider adding `Colors.SELECTION_BG_HOLOGRAPHIC` alias if useful for consistency
  - [x] 6.2: Document any new color constant additions

## Dev Notes

### Color Mapping Reference

The following color substitutions should be applied:

| Current Usage | Old Color | New Color | Hex Value |
|---------------|-----------|-----------|-----------|
| Background | `Colors.BACKGROUND` (DARK_GREEN) | `Colors.DEEP_SPACE_BLACK` | #0a0e1a |
| Cell Border | `Colors.BORDER` (GREEN) | `Colors.ELECTRIC_BLUE` | #00d4ff |
| Selection BG | `Colors.SELECTION_BG` (LIGHT_GREEN) | `Colors.DARK_BLUE` | #1a2f4a |
| Selection Border | (implicit) | `Colors.BRIGHT_CYAN` | #4df7ff |
| Title Text | `Colors.TEXT_PRIMARY` (WHITE) | `Colors.HOLOGRAM_WHITE` | #e8f4f8 |
| Secondary Text | `Colors.TEXT_SECONDARY` (LIGHT_GRAY) | `Colors.ICE_BLUE` | #a8e6ff |

### Files to Modify

1. **`src/ui/home_screen.py`** - Primary file with all rendering logic
   - `render()` method - background fill
   - `_render_grid()` method - cell borders and selection styling
   - `_render_search_bar()` method - button styling
   - Text rendering calls throughout

### Existing Infrastructure

- `src/ui/colors.py` already contains all holographic color constants (lines 51-57)
- `GenerationBadge` class already uses holographic palette - serves as reference implementation
- Detail Screen uses same colors - follow its patterns for consistency

### Project Structure Notes

- All changes confined to `src/ui/home_screen.py`
- No new files required
- No database or state changes
- Colors already defined in `src/ui/colors.py`

### References

- [Source: docs/ux-design-specification.md#Color-System] - Holographic Blue Palette definition
- [Source: src/ui/colors.py#L51-L57] - Color constants for holographic system
- [Source: src/ui/detail_screen.py] - Reference implementation of holographic styling
- [Source: docs/epics.md#Story-3.8] - Story definition and acceptance criteria

### Learnings from Previous Story

**From Story 3.7 (Status: done)**

- **Holographic Styling Applied**: Detail Screen successfully implemented holographic blue palette
- **Color Constants Available**: `Colors.DEEP_SPACE_BLACK`, `Colors.DARK_BLUE`, `Colors.ELECTRIC_BLUE`, `Colors.BRIGHT_CYAN`, `Colors.ICE_BLUE`, `Colors.HOLOGRAM_WHITE` all defined and working
- **Panel Styling Pattern**: Use 2px borders with `ELECTRIC_BLUE`, backgrounds with `DARK_BLUE` transparency
- **Text Hierarchy**: White/Hologram White for primary, Ice Blue for secondary
- **Performance Maintained**: Color changes have no performance impact - purely visual

[Source: docs/sprint-artifacts/3-7-detail-view-performance-and-visual-polish.md]

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2025-11-29 | Story drafted | SM Agent (Bob) |
| 2025-11-29 | Implemented holographic theme, all ACs satisfied, 387 tests passing | Dev Agent (Amelia) |

## Dev Agent Record

### Context Reference

- docs/sprint-artifacts/3-8-home-screen-holographic-theme-alignment.context.xml

### Agent Model Used

Claude Opus 4.5 (Preview)

### Debug Log References

Implementation Plan:
1. Task 1: Updated render() background from Colors.BACKGROUND → Colors.DEEP_SPACE_BLACK
2. Task 2: Updated _render_cell() with ELECTRIC_BLUE borders (2px), DARK_BLUE selection bg, BRIGHT_CYAN selection border
3. Task 3: Updated title to HOLOGRAM_WHITE, secondary text (page indicator, view mode, help) to ICE_BLUE
4. Task 4: Updated _render_search_bar() with DARK_BLUE active bg, ELECTRIC_BLUE borders, HOLOGRAM_WHITE/ICE_BLUE text
5. Task 5: Verified visual consistency - both screens share DEEP_SPACE_BLACK background, Generation Badge unchanged
6. Task 6: No new constants needed - existing holographic palette (Colors.DARK_BLUE) sufficient for selection backgrounds

### Completion Notes List

✅ **AC #1 (Background)**: HomeScreen.render() now fills with DEEP_SPACE_BLACK (#0a0e1a) instead of DARK_GREEN
✅ **AC #2 (Grid Cell Borders)**: All cells have 2px ELECTRIC_BLUE (#00d4ff) borders
✅ **AC #3 (Selection Highlighting)**: Selected cells use DARK_BLUE (#1a2f4a) background with BRIGHT_CYAN (#4df7ff) border
✅ **AC #4 (Title)**: "ShokeDex" title uses HOLOGRAM_WHITE (#e8f4f8)
✅ **AC #5 (Secondary Text)**: Page indicator, view mode, help text all use ICE_BLUE (#a8e6ff)
✅ **AC #6 (Search Bar)**: Buttons use DARK_BLUE active bg, ELECTRIC_BLUE borders, HOLOGRAM_WHITE/ICE_BLUE text
✅ **AC #7 (Transition Consistency)**: Home and Detail screens share identical DEEP_SPACE_BLACK background
✅ **AC #8 (Generation Badge)**: Badge unchanged - already uses holographic palette, renders correctly

**Tests Added**: 9 new tests in TestHomeScreenHolographicTheme class covering all ACs
**Regression Tests**: 387 total tests passing (0 failures)
**Performance**: Color changes have no performance impact - purely visual updates

### File List

**Modified:**
- src/ui/home_screen.py - Holographic theme applied to render(), _render_search_bar(), _render_grid(), _render_cell()

**Tests Updated:**
- tests/test_home_screen.py - Added TestHomeScreenHolographicTheme class with 9 new tests
