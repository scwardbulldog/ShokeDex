# Story 5.5: Navigation to Evolution Relatives

Status: ready-for-dev

## Story

As a user,
I want to select and jump to evolution relatives directly from the evolution panel,
so that I can explore related Pokémon in an evolution family without going back to the main browse view.

## Acceptance Criteria

1. **Selectable Evolution Relatives (AC #1)**
   - **Given** the evolution panel is displayed on DetailScreen for a Pokémon that has evolution relatives (pre-evolutions and/or evolutions)
   - **When** the user views the evolution panel
   - **Then** each sprite in the evolution panel (pre-evolution, current Pokémon, and all evolutions/branches) is treated as a selectable target for navigation
   - **And** the component maintains a single focused evolution entry (for example, via an index or cursor) that determines which relative will be activated by A button.

2. **Focus and Navigation Within the Evolution Panel (AC #2)**
   - **Given** the evolution panel is visible
   - **When** the user uses the D-pad (for example, Up/Down and/or Left/Right, depending on layout)
   - **Then** the focus moves between available evolution sprites in a predictable order (for example, left-to-right for three-stage chains, top-to-bottom for branching chains)
   - **And** the currently focused evolution relative is visually indicated (for example, a brighter border or additional highlight distinct from the "Current" label used for the active Pokémon)
   - **And** focus movement never goes out of bounds and wraps or stops in a way that feels consistent with the layout.

3. **A-Button Navigation to Selected Relative (AC #3)**
   - **Given** a particular evolution relative sprite in the panel is focused
   - **When** the user presses the A button
   - **Then** DetailScreen navigates to a new DetailScreen instance for that selected Pokémon ID
   - **And** the newly opened DetailScreen shows that Pokémon as the current Pokémon, including its own evolution panel populated from `Database.get_evolution_chain()`
   - **And** navigation completes in under 300ms on Raspberry Pi hardware (database query + sprite loading + render) for any Gen 1–3 Pokémon.

4. **Back-Stack and B-Button Behavior (AC #4)**
   - **Given** the user has navigated from one Pokémon’s DetailScreen to an evolution relative’s DetailScreen using the evolution panel and A button
   - **When** the user presses the B button
   - **Then** the ScreenManager pops back to the previous DetailScreen (the one they navigated from), preserving its state (including tab selection and last focused evolution entry where reasonable)
   - **And** B button from the original DetailScreen without any evolution navigation continues to return to the browse/home screen as it does today.

5. **Integration with Existing DetailScreen Navigation (AC #5)**
   - **Given** DetailScreen already supports adjacent navigation via L/R buttons (Story 3.6)
   - **When** the user navigates into a new DetailScreen instance via the evolution panel (for example, selecting Raichu from Pikachu’s panel)
   - **Then** L/R adjacent navigation continues to work from that new Pokémon (for example, Raichu’s neighbors) exactly as defined in Story 3.6
   - **And** evolution-based navigation does not break or regress adjacent navigation, state persistence, or tab-based layout behavior introduced in Story 5.7.

6. **Graceful Handling of No-Evolution and Single-Stage Cases (AC #6)**
   - **Given** the evolution panel is showing the "No evolutions" message for a single-stage Pokémon (Story 5.3)
   - **When** the user attempts to move focus or press A while viewing the evolution panel
   - **Then** no navigation to a different Pokémon occurs (because there are no relatives to navigate to)
   - **And** the app does not crash, throw exceptions, or show error styling.

7. **Performance and Stability (AC #7)**
   - **Given** a user repeatedly navigates between evolution relatives using the panel (for example, stepping through an entire family such as Charmander → Charmeleon → Charizard → back to Charmander)
   - **When** this navigation pattern is exercised for multiple families (three-stage, branching like Eevee, and single-stage edge cases)
   - **Then** navigation remains smooth with frame rate ≥ 30 FPS
   - **And** no memory leaks or runaway growth in sprite caches occur beyond existing budgets defined in the Evolution System tech spec
   - **And** all database queries invoked as part of this navigation remain fully parameterized and complete in under 50ms.

## Tasks / Subtasks

- [ ] **Task 1: Define Focus Model for EvolutionPanel (AC: #1, #2, #6)**
  - [ ] 1.1: Extend EvolutionPanel’s internal state (in `src/ui/detail_screen.py`) to track a focused evolution index or key that maps onto a specific evolution-relative entry in the current evolution data.
  - [ ] 1.2: For three-stage (linear) chains, define a left-to-right focus order (for example, pre-evolution → current → evolution) that matches the horizontal layout from Story 5.1.
  - [ ] 1.3: For branching chains, define a deterministic focus order that matches the vertical or radial layout from Story 5.2 (for example, root first, then each branch top-to-bottom).
  - [ ] 1.4: Ensure that when there are zero evolution sprites (single-stage / "No evolutions" case from Story 5.3), the focus model gracefully treats the panel as having no selectable entries (so that input handlers become no-ops for A/focus movement).

- [ ] **Task 2: Wire D-Pad / Input Actions into EvolutionPanel (AC: #2, #6)**
  - [ ] 2.1: Decide which `InputAction` values (for example, LEFT/RIGHT and/or UP/DOWN) should be interpreted as movement within the evolution panel vs movement handled by the outer DetailScreen.
  - [ ] 2.2: Implement a `handle_input(action: InputAction) -> Optional[int]` (or similar) method on EvolutionPanel that updates the focused index when movement actions are received and returns a selected Pokémon ID when A/SELECT is pressed.
  - [ ] 2.3: Ensure focus movement stays within bounds and either wraps or clamps in a way that feels natural for the layout.
  - [ ] 2.4: For single-stage and no-evolution cases, ensure `handle_input()` returns `None` for all actions and does not raise errors.

- [ ] **Task 3: Integrate A-Button Navigation with ScreenManager (AC: #3, #4, #5)**
  - [ ] 3.1: In DetailScreen’s `handle_input` method, delegate A/SELECT actions to the evolution panel when the Evolution tab is active (per Story 5.7) and the panel exists.
  - [ ] 3.2: When EvolutionPanel.handle_input() returns a target Pokémon ID, construct a new DetailScreen instance for that Pokémon and push it onto the ScreenManager stack (not replace), so that B correctly pops back.
  - [ ] 3.3: Confirm that from the newly pushed DetailScreen, B button pops back to the previous DetailScreen; from the original DetailScreen, B continues to pop back to HomeScreen as before.
  - [ ] 3.4: Verify that existing adjacent L/R navigation implemented in Story 3.6 continues to function for all DetailScreen instances, regardless of whether they were reached from HomeScreen or via evolution navigation.

- [ ] **Task 4: Visual Focus and Highlighting (AC: #2, #3)**
  - [ ] 4.1: Add a distinct visual focus indicator (for example, a secondary border treatment or inner highlight) to differentiate "focused" entries from the existing "Current" glow used for the active Pokémon.
  - [ ] 4.2: Ensure the focus indicator works in both linear and branching layouts and does not conflict with the current Pokémon highlight.
  - [ ] 4.3: Validate that focus and current-state visuals remain readable and legible on both 480x320 and 800x480 targets while maintaining the holographic blue aesthetic documented in the UX spec.

- [ ] **Task 5: Tests for Evolution Navigation (AC: #1, #2, #3, #4, #5, #6, #7)**
  - [ ] 5.1: Add unit tests to `tests/test_evolution_panel.py` that exercise focus movement and selection logic for:
        - a three-stage line (for example, Charmander family),
        - a branching family (for example, Eevee),
        - and a single-stage Pokémon (for example, Ditto), verifying that no selection occurs when there are no relatives.
  - [ ] 5.2: Add integration tests (in an appropriate DetailScreen test module) that simulate input sequences: navigate to Evolution tab → move focus → press A → verify ScreenManager now has a new DetailScreen for the selected Pokémon → press B → verify back-stack behavior.
  - [ ] 5.3: Include at least one performance-oriented test or benchmark ensuring that multiple successive evolution-based navigations do not violate existing performance budgets or cause runaway sprite cache growth.

- [ ] **Task 6: Demo and Visual Validation (AC: #2, #3, #4, #5)**
  - [ ] 6.1: Update `demo_evolution_display.py` (or add a similar demo) to illustrate evolution navigation flows for a small set of representative Pokémon (for example, Charmander, Eevee, Ditto).
  - [ ] 6.2: Manually verify that focus movement, highlighting, and A/B navigation all behave as expected using keyboard input on desktop and, when possible, GPIO input on actual Raspberry Pi hardware.
  - [ ] 6.3: Capture updated screenshots for Evolution tab showing selected/focused relatives and navigation in-progress, to support future documentation or reviews.

## Dev Notes

### Implementation Overview

This story layers **interactive navigation behavior** on top of the evolution visualization work done in:
- Story 5.1: three-stage evolution chain display
- Story 5.2: branching evolution display
- Story 5.3: single-stage Pokémon handling
- Story 5.4: evolution requirement formatting
- Story 5.7: tab-based layout for DetailScreen

The UI and data plumbing for evolution chains are already in place. The primary new responsibilities introduced here are:
- A focus model within EvolutionPanel so that evolution relatives can be selected with the D-pad.
- Wiring A/SELECT to push a new DetailScreen for the focused relative.
- Ensuring B/back correctly unwinds the navigation stack without breaking existing HomeScreen → DetailScreen flows.

The navigation patterns should stay aligned with the architecture and UX patterns defined in:
- Evolution system tech spec: [docs/sprint-artifacts/tech-spec-epic-5-evolution-system.md](docs/sprint-artifacts/tech-spec-epic-5-evolution-system.md)
- Epic-level story definition for 5.5: [docs/epics.md](docs/epics.md)
- Overall architecture (ScreenManager, Screen lifecycle, Database, SpriteLoader): [docs/architecture.md](docs/architecture.md)
- Detail view UX and holographic design system: [docs/ux-design-specification.md](docs/ux-design-specification.md)

### Architectural Alignment

Expected code touch points:
- EvolutionPanel and DetailScreen integration in [src/ui/detail_screen.py](src/ui/detail_screen.py)
- Screen stacking and navigation via ScreenManager in [src/ui/screen_manager.py](src/ui/screen_manager.py)
- Existing adjacent navigation behavior from Story 3.6 (DetailScreen L/R navigation)
- Tests in [tests/test_detail_screen.py](tests/test_detail_screen.py) and [tests/test_evolution_panel.py](tests/test_evolution_panel.py)
- Demo script(s) in the repo root (for example, [demo_evolution_display.py](demo_evolution_display.py))

Non-functional constraints to keep in mind (per PRD and architecture docs):
- Maintain ≥ 30 FPS on Raspberry Pi 3B+ during navigation.
- Keep evolution navigation fully offline and data-driven from the local SQLite database.
- Ensure all SQL remains parameterized.
- Avoid duplicate manager instances; continue to access managers (StateManager, InputManager, etc.) only via ScreenManager injection.

### Testing and Quality Notes

- Reuse the patterns established in Stories 5.1–5.3 for EvolutionPanel testing: clear, focused unit tests for data and layout behavior plus integration tests that exercise real screen flows.
- When simulating navigation in tests, prefer using the project’s existing `InputAction` abstractions rather than reaching for raw pygame events.
- Include at least one regression-style test that confirms B-button behavior from DetailScreen is unchanged for flows that *do not* involve evolution navigation (for example, HomeScreen → DetailScreen → B → HomeScreen).

### References

- PRD evolution navigation requirement: FR4.2 in [docs/PRD.md](docs/PRD.md)
- Epic 5 story definition for navigation to relatives: [docs/epics.md](docs/epics.md)
- Evolution system technical design and navigation scenarios: [docs/sprint-artifacts/tech-spec-epic-5-evolution-system.md](docs/sprint-artifacts/tech-spec-epic-5-evolution-system.md)
- Existing story docs for evolution system:
  - [docs/sprint-artifacts/5-1-three-stage-evolution-chain-display.md](docs/sprint-artifacts/5-1-three-stage-evolution-chain-display.md)
  - [docs/sprint-artifacts/5-2-branching-evolution-display.md](docs/sprint-artifacts/5-2-branching-evolution-display.md)
  - [docs/sprint-artifacts/5-3-single-stage-pokemon-handling.md](docs/sprint-artifacts/5-3-single-stage-pokemon-handling.md)
  - [docs/sprint-artifacts/5-4-evolution-requirement-display-level-stone-trade.md](docs/sprint-artifacts/5-4-evolution-requirement-display-level-stone-trade.md)
  - [docs/story-5.7-tab-layout-fixes.md](docs/story-5.7-tab-layout-fixes.md)

## Dev Agent Record

### Context Reference

- Primary planning inputs: PRD (FR4.2), epics.md (Story 5.5), architecture.md, ux-design-specification.md, and tech-spec-epic-5-evolution-system.md, plus completed Story 3.6 (adjacent navigation) and Stories 5.1–5.4 and 5.7.
- Sprint tracking source of truth: [docs/sprint-artifacts/sprint-status.yaml](docs/sprint-artifacts/sprint-status.yaml).

### Agent Model Used

- GPT-5.1 (Preview) via GitHub Copilot

### Completion Notes List

- Story 5.5 is now fully drafted with end-to-end acceptance criteria covering focus, selection, navigation, back-stack behavior, integration with adjacent navigation, and performance.
- A concrete task breakdown and implementation guidance are provided to keep EvolutionPanel behavior, DetailScreen navigation, and ScreenManager stack handling consistent with existing architecture patterns.
- This story is marked `ready-for-dev` and represents the navigation half of FR4.2 (Evolution Navigation) for the Evolution System epic.
- After implementation and tests are complete, update this story file’s Status to `done` and ensure [docs/sprint-artifacts/sprint-status.yaml](docs/sprint-artifacts/sprint-status.yaml) reflects the final state.
