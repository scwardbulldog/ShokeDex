# Story 5.2: Branching Evolution Display

Status: ready-for-dev

## Story

As a user,
I want to see all branching evolution paths,
so that I understand all possible evolution options (like Eevee's multiple forms).

## Acceptance Criteria

1. **Branching Evolution Detection (AC #1)**
   - **Given** a Pokémon with multiple evolution paths (e.g., Eevee → Vaporeon/Jolteon/Flareon/Espeon/Umbreon)
   - **When** viewing DetailScreen
   - **Then** Database.get_evolution_chain() identifies branching evolutions
   - **And** all evolution branches are loaded into evolution data structure
   - **And** database query uses COUNT() to detect multiple evolutions from same pre-evolution

2. **Branching Layout Rendering (AC #2)**
   - **Given** evolution panel displays a Pokémon with branching evolutions
   - **When** the panel renders
   - **Then** current Pokémon is shown as the root/center position
   - **And** all evolution branches spread from the root with clear visual separation
   - **And** layout accommodates up to 5 branches (Eevee has 5 in Gen 1-3)
   - **And** each branch shows sprite (64x64), name, and Dex number
   - **And** all branches fit within panel boundaries without overflow

3. **Branch Visual Separation (AC #3)**
   - **Given** multiple evolution branches are displayed
   - **When** rendering the branching layout
   - **Then** each branch is visually distinct from others
   - **And** branching indicator (split arrows or tree structure) clearly shows relationship
   - **And** arrows from root to each branch use electric blue (#00d4ff)
   - **And** spacing between branches prevents visual cluttering
   - **And** vertical or radial layout used for clarity (not just horizontal)

4. **Evolution Requirements per Branch (AC #4)**
   - **Given** each evolution branch has different requirements
   - **When** displaying requirement text
   - **Then** each branch shows its specific requirement (e.g., "Water Stone", "Thunder Stone", "Fire Stone", "Happiness (Day)", "Happiness (Night)")
   - **And** requirement text uses ice blue color (#a8e6ff)
   - **And** requirement text is positioned below or beside each branch arrow
   - **And** all requirement text is readable and not truncated

5. **Current Pokémon Highlighting in Branches (AC #5)**
   - **Given** user is viewing a Pokémon that is one of the branching evolutions
   - **When** the evolution panel renders
   - **Then** current Pokémon sprite is highlighted with bright cyan glow (#4df7ff)
   - **And** "Current" label is displayed underneath current Pokémon's sprite
   - **And** root Pokémon (pre-evolution) is shown without highlighting
   - **And** other branch options are shown at normal brightness

6. **Pre-Evolution Display with Branches (AC #6)**
   - **Given** user views one of Eevee's evolutions (e.g., Vaporeon)
   - **When** the evolution panel renders
   - **Then** Eevee is shown as the pre-evolution (not highlighted)
   - **And** all 5 evolution options are shown as branches
   - **And** Vaporeon is highlighted as "Current"
   - **And** other 4 evolutions (Jolteon, Flareon, Espeon, Umbreon) are shown at normal brightness

7. **Database Query for Branching (AC #7)**
   - **Given** Database.get_evolution_chain() is called for a branching Pokémon
   - **When** the query executes
   - **Then** the evolutions table is queried with GROUP BY from_pokemon_id
   - **And** parameterized SQL prevents injection
   - **And** query returns all evolution branches with requirements
   - **And** query completes in < 50ms (per performance requirements)
   - **And** data structure includes: from_pokemon_id, list of to_pokemon_ids with methods/items

8. **Panel Styling Consistency (AC #8)**
   - **Given** branching evolution panel is rendered
   - **When** comparing with three-stage evolution panel (Story 5.1)
   - **Then** panel uses same holographic blue styling
   - **And** panel has electric blue (#00d4ff) 2px border
   - **And** panel background uses dark blue rgba(26, 47, 74, 0.9)
   - **And** font choices match: Rajdhani Bold for names, Share Tech Mono for Dex numbers
   - **And** 16px padding and consistent spacing maintained

9. **Rendering Performance with Branches (AC #9)**
   - **Given** user navigates to DetailScreen showing Eevee (5 branches, worst case)
   - **When** evolution panel renders for the first time
   - **Then** rendering completes within 250ms (database query + 6 sprites: Eevee + 5 evolutions)
   - **And** frame rate maintains 30+ FPS during render
   - **And** no visual stuttering or lag

10. **Edge Case: Two-Branch Evolution (AC #10)**
    - **Given** a Pokémon with only 2 evolution branches (e.g., Wurmple → Silcoon/Cascoon)
    - **When** viewing the evolution panel
    - **Then** layout adapts to show 2 branches clearly
    - **And** visual layout is balanced and not skewed
    - **And** same branching indicator pattern applies

## Tasks / Subtasks

- [ ] **Task 1: Extend Database Method for Branching Detection (AC: #1, #7)**
  - [ ] 1.1: Modify `get_evolution_chain(pokemon_id)` to detect branching evolutions
  - [ ] 1.2: Add SQL query using `GROUP BY from_pokemon_id` with `COUNT(to_pokemon_id) > 1`
  - [ ] 1.3: Update data structure to include `is_branching: bool` flag
  - [ ] 1.4: For branching chains, include all evolution branches in `evolutions` list
  - [ ] 1.5: Test with Eevee (#133), Tyrogue (#236), Wurmple (#265)
  - [ ] 1.6: Add database test: `test_get_evolution_chain_branching()`

- [ ] **Task 2: Design Branching Layout Algorithm (AC: #2, #3)**
  - [ ] 2.1: Implement vertical branching layout for 2-5 branches
  - [ ] 2.2: Calculate sprite positions: root at center-left, branches spread vertically on right
  - [ ] 2.3: Define spacing formula: `vertical_spacing = panel_height / (num_branches + 1)`
  - [ ] 2.4: Test layout fits within panel boundaries for 2, 3, 5 branch scenarios
  - [ ] 2.5: Document layout algorithm in code comments

- [ ] **Task 3: Render Branching Evolution Sprites (AC: #2, #6)**
  - [ ] 3.1: Render root Pokémon (pre-evolution) on left side of panel
  - [ ] 3.2: Render all branch evolution sprites vertically aligned on right side
  - [ ] 3.3: Use SpriteLoader.load_thumbnail() for all sprites (root + branches)
  - [ ] 3.4: Render Pokémon names below each sprite (Rajdhani Bold, 14px, white)
  - [ ] 3.5: Render Dex numbers below names (Share Tech Mono, 12px, ice blue #a8e6ff)
  - [ ] 3.6: Test with Eevee (6 total sprites: 1 root + 5 branches)

- [ ] **Task 4: Render Branch Arrows and Indicators (AC: #3, #4)**
  - [ ] 4.1: Draw arrows from root Pokémon to each branch evolution
  - [ ] 4.2: Style arrows with electric blue (#00d4ff) and appropriate thickness
  - [ ] 4.3: Use branching indicator (split point or tree-like structure) to show divergence
  - [ ] 4.4: Position requirement text along each arrow path
  - [ ] 4.5: Format requirement text: "Water Stone", "Happiness (Day)", etc.
  - [ ] 4.6: Render requirement text (Rajdhani, 14px, ice blue #a8e6ff)
  - [ ] 4.7: Verify arrows and text don't overlap with sprites

- [ ] **Task 5: Implement Current Pokémon Highlighting for Branches (AC: #5, #6)**
  - [ ] 5.1: Determine which sprite is current Pokémon from evolution data
  - [ ] 5.2: If current is root (e.g., Eevee): highlight root, show all branches normal
  - [ ] 5.3: If current is branch (e.g., Vaporeon): show root normal, highlight current branch, show other branches normal
  - [ ] 5.4: Draw bright cyan glow (#4df7ff) border around current sprite
  - [ ] 5.5: Render "Current" label below current Pokémon (ice blue #a8e6ff)
  - [ ] 5.6: Test highlighting with root Pokémon and each branch evolution

- [ ] **Task 6: Integrate Branching Layout into EvolutionPanel (AC: #2, #8)**
  - [ ] 6.1: Add conditional logic in EvolutionPanel.render() to detect branching vs linear chains
  - [ ] 6.2: If `is_branching == True`, use branching layout algorithm
  - [ ] 6.3: If `is_branching == False`, use existing three-stage horizontal layout from Story 5.1
  - [ ] 6.4: Ensure consistent panel styling regardless of layout type
  - [ ] 6.5: Verify panel background, border, and padding match Story 5.1

- [ ] **Task 7: Write Unit and Integration Tests (AC: #1, #7, #9)**
  - [ ] 7.1: Test `test_get_evolution_chain_eevee()` verifies 5 branches detected
  - [ ] 7.2: Test `test_evolution_panel_render_branching()` verifies all sprites rendered
  - [ ] 7.3: Test `test_evolution_panel_branch_layout()` verifies vertical positioning
  - [ ] 7.4: Test `test_evolution_panel_highlights_branch()` verifies correct highlighting
  - [ ] 7.5: Test `test_branching_arrows_and_requirements()` verifies all requirement text
  - [ ] 7.6: Performance test: `test_branching_panel_renders_under_250ms()`
  - [ ] 7.7: Edge case test: `test_two_branch_evolution()` for Wurmple

- [ ] **Task 8: Visual Testing and Polish (AC: #8, #9, #10)**
  - [ ] 8.1: Test rendering on both 480x320 and 800x480 displays
  - [ ] 8.2: Verify branching layout is clear and not cluttered with 5 branches
  - [ ] 8.3: Verify requirement text is legible for all branches
  - [ ] 8.4: Compare styling with Story 5.1 three-stage panel (consistency check)
  - [ ] 8.5: Profile rendering performance on Raspberry Pi 3B+ if available
  - [ ] 8.6: Test with Eevee, Tyrogue, Wurmple for visual accuracy

## Dev Notes

### Existing Implementation to Build On

**From Story 5.1 (Three-Stage Evolution Chain Display):**
- EvolutionPanel component class established in `src/ui/detail_screen.py`
- Database.get_evolution_chain() method exists (will be extended)
- SpriteLoader.load_thumbnail() integration working
- Horizontal layout pattern for linear chains complete
- Holographic blue styling and color palette applied
- Panel rendering integrated into DetailScreen.render()

[Source: docs/sprint-artifacts/5-1-three-stage-evolution-chain-display.md]

**Database Schema (Already Implemented):**
- `evolutions` table supports multiple rows with same `from_pokemon_id`
- Branching detection: `SELECT from_pokemon_id, COUNT(*) FROM evolutions GROUP BY from_pokemon_id HAVING COUNT(*) > 1`
- All evolution requirements stored in method, level, item fields
- Data seeded via manage_db.py includes all Gen 1-3 branching evolutions

**SpriteLoader (Already Implemented):**
- LRU cache can handle 6 sprites (Eevee + 5 evolutions) within 20-sprite capacity
- load_thumbnail() gracefully handles missing sprites
- 64x64 size fits multiple sprites in vertical layout

### Branching Evolution Cases in Gen 1-3

**Eevee (#133) - 5 branches (worst case):**
- Vaporeon (#134) - Water Stone
- Jolteon (#135) - Thunder Stone
- Flareon (#136) - Fire Stone
- Espeon (#196) - Happiness during day
- Umbreon (#197) - Happiness during night

**Tyrogue (#236) - 3 branches:**
- Hitmonlee (#106) - Attack > Defense at level 20
- Hitmonchan (#107) - Defense > Attack at level 20
- Hitmontop (#237) - Attack = Defense at level 20

**Wurmple (#265) - 2 branches:**
- Silcoon (#266) - Level 7 (random, personality-based)
- Cascoon (#268) - Level 7 (random, personality-based)

**Oddish (#43) - 2 branches (Gen 1 only has Gloom, but included for completeness):**
- Gloom evolves to Vileplume (Leaf Stone) or Bellossom (Sun Stone)

**Poliwhirl (#61) - 2 branches:**
- Poliwrath (#62) - Water Stone
- Politoed (#186) - Trade holding King's Rock

**Slowpoke (#79) - 2 branches:**
- Slowbro (#80) - Level 37
- Slowking (#199) - Trade holding King's Rock

### Layout Algorithm Details

**Vertical Branching Layout (for 2-5 branches):**

```
Panel dimensions: 440px wide × 150px tall (example)

┌────────────────────────────────────────────────┐
│  [Root]  →  [Branch 1] (Water Stone)          │
│   Eevee  ┌→ [Branch 2] (Thunder Stone)        │
│          │→ [Branch 3] (Fire Stone)           │
│          │→ [Branch 4] (Happiness Day)        │
│          └→ [Branch 5] (Happiness Night)      │
└────────────────────────────────────────────────┘

Root sprite: x=50, y=panel_center_y
Branch sprites: x=300, y positions calculated with vertical_spacing
Arrows: From root to each branch with requirement text along path
```

**Spacing Formula:**
- `vertical_spacing = (panel_height - 40) / (num_branches + 1)` (40px for padding)
- `branch_y[i] = 20 + (i + 1) * vertical_spacing` for i in 0..num_branches-1

**Alternative: Radial Layout (future enhancement):**
- Root at center, branches radiate outward in semicircle
- Better for 5+ branches, but more complex rendering
- Defer to future story if vertical layout is insufficient

### Learnings from Previous Story

**From Story 5.1: Three-Stage Evolution Chain Display (Status: in-progress)**

- **EvolutionPanel Component Pattern:** Established reusable component for evolution display
- **Database Query Performance:** get_evolution_chain() completes in < 50ms for linear chains
- **Sprite Caching:** SpriteLoader LRU cache efficiently handles multiple thumbnails
- **Holographic Styling:** Electric blue (#00d4ff) borders, ice blue (#a8e6ff) text established
- **Current Indicator:** Bright cyan glow (#4df7ff) with "Current" label pattern works well

[Source: docs/sprint-artifacts/5-1-three-stage-evolution-chain-display.md#Dev-Agent-Record]

**Key Takeaway:** Extend existing EvolutionPanel.render() with conditional branching layout rather than creating separate component. Maintain styling consistency from Story 5.1.

### Project Structure Notes

**Files to Modify:**
- `src/data/database.py` - Extend `get_evolution_chain()` to detect branching (add `is_branching` flag to return data)
- `src/ui/detail_screen.py` - Extend `EvolutionPanel.render()` with branching layout algorithm
- `tests/test_database.py` - Add branching evolution query tests
- `tests/test_detail_screen.py` - Add branching evolution panel rendering tests

**No New Files Needed:**
- Branching logic integrates into existing EvolutionPanel class
- Database method extension, not new method
- Tests extend existing test files

**Alignment with Architecture:**
- Component pattern from Story 5.1 maintained
- Database access follows context manager pattern
- SpriteLoader integration unchanged
- Holographic styling pattern consistent
- Screen lifecycle pattern (on_enter, render) unchanged

**No Conflicts Detected:**
- Branching layout uses same panel space as three-stage layout
- Conditional logic separates linear vs branching rendering paths
- Database schema already supports branching (no migrations needed)
- Sprite assets already present for all evolutions

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-5-evolution-system.md#Branching-Evolution-Display]
- [Source: docs/sprint-artifacts/tech-spec-epic-5-evolution-system.md#Database-Query-for-Branching]
- [Source: docs/sprint-artifacts/tech-spec-epic-5-evolution-system.md#Layout-Algorithm]
- [Source: docs/epics.md#Story-5.2-Branching-Evolution-Display]
- [Source: docs/PRD.md#FR4-Evolution-Chain-Display]
- [Source: docs/architecture.md#Manager-Architecture-Pattern]
- [Source: docs/database_schema.md - evolutions table structure]
- [Source: docs/ux-design-specification.md#Holographic-Blue-Color-Palette]
- [Source: docs/sprint-artifacts/5-1-three-stage-evolution-chain-display.md - established patterns]

## Dev Agent Record

### Context Reference

- [5-2-branching-evolution-display.context.xml](5-2-branching-evolution-display.context.xml) - Generated 2025-12-08

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
| 2025-12-06 | 1.0.0 | Story drafted by SM agent (Bob) based on Epic 5 tech spec and previous story learnings |
