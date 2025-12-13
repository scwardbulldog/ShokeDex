# Story 5.4: Evolution Requirement Display (Level/Stone/Trade)

Status: ready-for-dev

## Story

As a user,
I want to see exactly how each Pokémon evolves,
so that I know what is required for evolution.

## Acceptance Criteria

1. **Level-Based Evolution Requirements (AC #1)**
   - **Given** an evolution with a level requirement (for example, Bulbasaur → Ivysaur at level 16)
   - **When** the evolution chain is displayed in the evolution panel on DetailScreen
   - **Then** the requirement text "Level 16" is rendered directly below the evolution arrow between Bulbasaur and Ivysaur
   - **And** level-based requirement strings follow the format `Level {level}` (for example, "Level 16", "Level 36")
   - **And** requirement text uses ice blue color (#a8e6ff)
   - **And** font is Rajdhani, 14px
   - **And** the text is fully readable and not truncated on 480x320 and 800x480 displays

2. **Stone-Based Evolution Requirements (AC #2)**
   - **Given** an evolution with a stone requirement (for example, Pikachu → Raichu with Thunder Stone)
   - **When** the evolution chain is displayed in the evolution panel
   - **Then** the requirement text shows the full stone name (for example, "Thunder Stone", "Fire Stone", "Water Stone") below the corresponding evolution arrow
   - **And** requirement text uses ice blue color (#a8e6ff)
   - **And** font is Rajdhani, 14px
   - **And** stone-based requirement text is fully readable and not truncated on 480x320 and 800x480 displays

3. **Trade and Trade-with-Item Requirements (AC #3)**
   - **Given** an evolution requiring trade (for example, Machoke → Machamp)
   - **When** the evolution chain is displayed in the evolution panel
   - **Then** the requirement text "Trade" is rendered below the evolution arrow for that relationship
   - **Given** an evolution requiring trade while holding an item (for example, Onix → Steelix with Metal Coat)
   - **When** the evolution chain is displayed in the evolution panel
   - **Then** the requirement text follows the format "Trade holding {item_name}" (for example, "Trade holding Metal Coat") below the appropriate arrow
   - **And** all trade-related requirement text uses ice blue color (#a8e6ff) and Rajdhani 14px
   - **And** trade and trade-with-item requirement strings are fully readable and not truncated on 480x320 and 800x480 displays

4. **Requirement Formatting Logic and Data Source (AC #4)**
   - **Given** evolution data loaded from the database via `Database.get_evolution_chain(pokemon_id)`
   - **When** the evolution panel formats requirement text for any supported evolution method (for example, `level`, `stone`, `trade`, `trade-item`, `happiness`, or similar values from the `evolutions` table)
   - **Then** the requirement string is derived from database fields (for example, `minimum_level`, `item_name`, `evolution_method`, `trigger`) and not hard-coded per Pokémon
   - **And** level-based, stone-based, and trade-based evolutions reuse a single formatting function or helper so that requirements render consistently in both three-stage (Story 5.1) and branching (Story 5.2) layouts
   - **And** null or unsupported requirement combinations fall back to a safe, human-readable string (for example, "See evolution data") without breaking panel rendering

5. **Consistency Across Linear and Branching Layouts (AC #5)**
   - **Given** a three-stage evolution chain (Story 5.1) or a branching evolution chain (Story 5.2)
   - **When** the evolution panel renders level, stone, or trade requirements for each evolution relationship
   - **Then** requirement text appears in a consistent relative position for both layouts (for example, directly beneath the arrow or arrow path) without overlapping sprites, names, or Dex numbers
   - **And** requirement text styling (font, size, color) matches between linear and branching layouts
   - **And** requirement text remains readable and non-overlapping when tested with worst-case examples such as Eevee and multi-stage lines like Charmander → Charmeleon → Charizard

6. **Performance and Safety (AC #6)**
   - **Given** evolution requirements are rendered for any Pokémon in Gen 1–3
   - **When** the evolution panel is constructed and rendered on Raspberry Pi hardware
   - **Then** requirement formatting does not introduce noticeable performance regressions beyond the budgets already established in Stories 5.1 and 5.2 (first render ≤ 200–250ms, cached renders ≤ 50ms)
   - **And** all SQL used to fetch requirement data remains fully parameterized (no string interpolation)
   - **And** missing or malformed evolution data is handled gracefully without crashes (for example, log a warning and display a neutral fallback string or omit requirement text for that arrow).

## Tasks / Subtasks

- [ ] **Task 1: Centralize Evolution Requirement Formatting (AC: #1, #2, #3, #4)**
  - [ ] 1.1: Identify current locations in EvolutionPanel (and any helpers) where level, stone, and trade requirements are formatted for display (for example, inline `f"Level {level}"` strings from Story 5.1 or 5.2).
  - [ ] 1.2: Introduce a dedicated helper (for example, `_format_requirement(evolution_record: Dict[str, Any]) -> str`) that takes one evolution row from `get_evolution_chain()` and returns the final human-readable requirement string.
  - [ ] 1.3: Implement formatting rules in the helper based on `evolution_method`, `minimum_level`, `item_name`, and any `trigger` or auxiliary fields:
        - `level` → `Level {minimum_level}`
        - `stone` → `{item_name}` (for example, "Thunder Stone")
        - `trade` with no item → `Trade`
        - `trade` or `trade-item` with item → `Trade holding {item_name}`
        - other / complex cases (for example, happiness/time-of-day) → readable string that matches existing tech spec patterns.
  - [ ] 1.4: Ensure the helper is used for both three-stage and branching layouts so there is exactly one place where requirement strings are constructed.

- [ ] **Task 2: Wire Requirement Formatting into Linear (Three-Stage) Layout (AC: #1, #2, #3, #5)**
  - [ ] 2.1: Update the linear three-stage rendering path in EvolutionPanel (from Story 5.1) to call the new `_format_requirement()` helper instead of building strings inline.
  - [ ] 2.2: Verify that arrows between three-stage evolutions render requirement text beneath the arrow using Rajdhani 14px and ice blue (#a8e6ff).
  - [ ] 2.3: Test with representative examples for each method type (for example, Bulbasaur line for level, a stone-based evolution like Pikachu, and a trade evolution line) to confirm text content and positioning.
  - [ ] 2.4: Confirm that requirement labels do not overlap sprites, names, or Dex numbers on 480x320 and 800x480 layouts (adjust vertical offsets or line wrapping if needed).

- [ ] **Task 3: Wire Requirement Formatting into Branching Layout (AC: #2, #3, #4, #5)**
  - [ ] 3.1: Update the branching layout rendering path in EvolutionPanel (from Story 5.2) to use `_format_requirement()` for each branch arrow.
  - [ ] 3.2: Ensure requirement text is anchored consistently under or alongside each branch arrow, with enough spacing to avoid overlap in the worst-case branching scenario (Eevee with 5 evolutions).
  - [ ] 3.3: Validate that requirement text remains legible for long strings like "Trade holding Metal Coat" and that they do not bleed outside the evolution panel on 480x320.
  - [ ] 3.4: Adjust panel spacing, line wrapping, or text clipping logic as needed to keep all requirement labels inside the panel while preserving readability.

- [ ] **Task 4: Database Contract and Safety Validation (AC: #4, #6)**
  - [ ] 4.1: Review `Database.get_evolution_chain()` in `src/data/database.py` to confirm that all fields required for requirement formatting (`evolution_method`, `minimum_level`, `item_name` or equivalent) are present in the returned structure for both linear and branching chains.
  - [ ] 4.2: If needed, extend the SQL query or result mapping so that `item_name` and any additional trigger fields are available without violating the existing method contract used by Stories 5.1 and 5.2.
  - [ ] 4.3: Double-check that all SQL related to evolution data remains parameterized and free of string interpolation.
  - [ ] 4.4: Add or update unit tests in `tests/test_database.py` to cover level-, stone-, and trade-based evolutions, asserting that the evolution records contain the expected method and requirement data.

- [ ] **Task 5: Unit and Integration Tests for Requirement Display (AC: #1, #2, #3, #4, #5, #6)**
  - [ ] 5.1: Add focused tests in `tests/test_evolution_panel.py` that exercise `_format_requirement()` for each method type (level, stone, trade, trade-with-item) using small synthetic evolution records.
  - [ ] 5.2: Add integration-style tests that construct an EvolutionPanel for representative Pokémon (for example, Bulbasaur, Pikachu, Machoke, Onix) and verify that rendered requirement strings match expectations.
  - [ ] 5.3: Where possible, validate that requirement strings are not empty and that fallbacks are used when database fields are missing or null.
  - [ ] 5.4: Add at least one performance-oriented test (for example, marked with `@pytest.mark.performance`) to confirm that rendering with requirement text remains within existing performance budgets.

- [ ] **Task 6: Visual / Layout Validation (AC: #1, #2, #3, #5)**
  - [ ] 6.1: Update or extend `demo_evolution_display.py` to include specific test Pokémon that exercise level, stone, and trade evolutions.
  - [ ] 6.2: Manually verify on the demo that requirement labels are visually aligned, readable, and consistent between three-stage and branching layouts on the target resolutions.
  - [ ] 6.3: Capture updated screenshots for key examples (for example, a three-stage line with level-based requirements, a stone-based evolution, and a trade-with-item evolution) to attach to design/implementation docs if needed.

## Dev Notes

### Implementation Overview

This story builds directly on the EvolutionPanel implementation and database/query work completed in:
- Story 5.1: three-stage evolution chain display
- Story 5.2: branching evolution display
- Story 5.3: single-stage Pokémon handling ("No evolutions" message)

The primary goal is not to invent new UI, but to **consolidate and harden** how evolution requirements are derived from the database and rendered across both linear and branching layouts. Requirement formatting should become a **single, well-tested responsibility** instead of being scattered across inline string constructions.

Key implementation points:
- Treat the evolution record from `Database.get_evolution_chain()` as the single source of truth for determining which requirement string to display.
- Introduce a helper that maps `(evolution_method, minimum_level, item_name, trigger, ...)` to a user-facing string, matching the method contracts and examples in the Epic 5 tech spec.
- Ensure the same helper is used for three-stage, branching, and any future evolution layouts so behavior stays consistent.
- Keep all styling (font, color) aligned with the holographic detail view design from the UX specification and with the patterns established in Stories 5.1 and 5.2.

### Architecture and Code Alignment

Relevant architecture and planning references:
- Evolution system technical spec: [docs/sprint-artifacts/tech-spec-epic-5-evolution-system.md](docs/sprint-artifacts/tech-spec-epic-5-evolution-system.md)
- Epic and story breakdown (including this story): [docs/epics.md](docs/epics.md)
- Overall architecture (screen/manager pattern, database access, sprite loading): [docs/architecture.md](docs/architecture.md)
- UX design system and holographic styling for DetailScreen: [docs/ux-design-specification.md](docs/ux-design-specification.md)

Expected code touch points:
- EvolutionPanel and its helpers in [src/ui/detail_screen.py](src/ui/detail_screen.py)
- Evolution-related queries and mapping in [src/data/database.py](src/data/database.py)
- Evolution panel tests in [tests/test_evolution_panel.py](tests/test_evolution_panel.py)
- Database tests for evolution data in [tests/test_database.py](tests/test_database.py)
- Visual demo harness in [demo_evolution_display.py](demo_evolution_display.py)

Implementation must continue to honor existing architectural constraints:
- Use parameterized SQL only (no string interpolation) for all evolution queries.
- Preserve the Screen and ScreenManager lifecycle patterns described in architecture docs.
- Maintain evolution panel performance within the budgets validated in previous stories.

### Testing and Quality Notes

- Leverage existing test patterns from Stories 5.1, 5.2, and 5.3 for both database integration and EvolutionPanel rendering.
- For each new requirement type or formatting branch, add at least one explicit unit test to prevent regressions.
- Validate worst-case text lengths (for example, long stone names or trade-with-item strings) on 480x320 to ensure labels do not clip or overlap.
- Use the demo script and screenshots to visually confirm that requirement labels still feel balanced and legible within the holographic detail view aesthetic.

### References

- PRD evolution requirements: [docs/PRD.md](docs/PRD.md)
- Epic 5 story definition for 5.4: [docs/epics.md](docs/epics.md)
- Evolution system technical design and data contracts: [docs/sprint-artifacts/tech-spec-epic-5-evolution-system.md](docs/sprint-artifacts/tech-spec-epic-5-evolution-system.md)
- Existing story implementations for context and patterns:
  - [docs/sprint-artifacts/5-1-three-stage-evolution-chain-display.md](docs/sprint-artifacts/5-1-three-stage-evolution-chain-display.md)
  - [docs/sprint-artifacts/5-2-branching-evolution-display.md](docs/sprint-artifacts/5-2-branching-evolution-display.md)
  - [docs/sprint-artifacts/5-3-single-stage-pokemon-handling.md](docs/sprint-artifacts/5-3-single-stage-pokemon-handling.md)
  - [docs/story-5.7-tab-layout-fixes.md](docs/story-5.7-tab-layout-fixes.md)

## Dev Agent Record

### Context Reference

- Primary planning inputs: PRD, epics, architecture, UX design spec, Epic 5 tech spec, and completed stories 5.1–5.3 and 5.7.
- Sprint tracking source of truth: [docs/sprint-artifacts/sprint-status.yaml](docs/sprint-artifacts/sprint-status.yaml).

### Agent Model Used

- GPT-5.1 (Preview) via GitHub Copilot

### Completion Notes List

- Story 5.4 is now fully drafted with clear acceptance criteria, tasks, and implementation guidance.
- This story is marked `ready-for-dev` and is intended to be implemented on top of the existing EvolutionPanel, database, and DetailScreen infrastructure completed in earlier Epic 5 stories.
- Once implementation and tests are complete, update this story file's Status to `done` and ensure [docs/sprint-artifacts/sprint-status.yaml](docs/sprint-artifacts/sprint-status.yaml) reflects the final state.
