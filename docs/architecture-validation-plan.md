# Architecture Validation Plan
**Created:** 2025-11-14
**Status:** Active Development Plan

## Purpose
Validate core architectural decisions from brainstorming session before full implementation.

---

## Bottom Line Items (Winston's Assessment)

### 1. De-Risk Technical Assumptions ✅ PARTIALLY COMPLETE

#### Hardware Performance
**Status:** ✅ VALIDATED
- Performance monitoring tools implemented
- Input latency testing complete
- 30 FPS target achievable on Pi 3B+
- Sprite rendering validated

**Evidence:**
- `tools/profile_performance.py` - FPS/CPU/Memory profiling
- `tools/test_input_latency.py` - Input responsiveness testing
- `docs/PERFORMANCE_TESTING_SUMMARY.md` - Complete results

#### Asset Availability
**Status:** ✅ COMPLETE
- All 386 Pokémon sprites present (thumb + detail)
- Located in `assets/sprites/thumb/` and `assets/sprites/detail/`
- PNG format, properly numbered (001.png - 386.png)
- Ready for use

**Action Required:** Validate sprite quality and dimensions on actual LCD display

### 2. Define System Boundaries ⏳ IN PROGRESS

#### State Persistence
**Status:** ❌ NOT IMPLEMENTED
- No state file exists
- Last viewed Pokémon not saved between sessions
- No favorites/recents tracking

**Required Implementation:**
```python
# Proposed: src/state_manager.py
class StateManager:
    - load_state() -> dict
    - save_state(state: dict)
    - get_last_viewed() -> int
    - set_last_viewed(pokemon_id: int)
    - get_favorites() -> list[int]
    - add_favorite(pokemon_id: int)
```

**Storage Format:** Simple JSON file
```json
{
  "last_viewed_id": 25,
  "last_viewed_generation": 1,
  "favorites": [25, 150, 249],
  "app_version": "1.0.0"
}
```

#### Input Abstraction
**Status:** ✅ COMPLETE
- `InputManager` class with mode switching
- Keyboard + GPIO support
- Clean action abstraction
- Hardware fallback working

#### Audio System
**Status:** ❌ NOT IMPLEMENTED
- No audio module exists
- Pokémon cries not integrated
- pygame.mixer not configured

**Required Implementation:**
```python
# Proposed: src/audio_manager.py
class AudioManager:
    - load_cry(pokemon_id: int)
    - play_cry(pokemon_id: int)
    - stop()
    - set_volume(level: float)
```

**Storage Format:** Individual audio files
- Location: `assets/audio/cries/{pokemon_id:03d}.ogg`
- Format: OGG Vorbis (compressed, Pi-friendly)
- Lazy loading (load on demand, not all 386 at once)

### 3. Build Thin Vertical Slice ⏳ IN PROGRESS

#### Navigation Skeleton
**Status:** ⏳ PARTIAL - Needs Generation-Based Organization

**Current State:**
- Screen stack management ✅
- Basic list/grid browsing ✅
- Detail view transitions ✅

**Missing from Brainstorming Requirements:**
- ❌ Generation-based navigation (L/R to switch Kanto/Johto/Hoenn)
- ❌ Always-on Pokémon display (currently starts with menu)
- ❌ 3-press rule validation
- ❌ Generation badges/indicators

**Required Implementation:**
```python
# Proposed: src/ui/generation_browser_screen.py
class GenerationBrowserScreen:
    - current_generation: int (1, 2, or 3)
    - current_index: int (within generation)
    - switch_generation(direction: int)
    - scroll_pokemon(direction: int)
    - get_pokemon_range() -> (start_id, end_id)
```

**Generation Ranges:**
- Gen 1 (Kanto): #1-151
- Gen 2 (Johto): #152-251
- Gen 3 (Hoenn): #252-386

#### Relationships View
**Status:** ❌ NOT IMPLEMENTED

**Required:** Single screen combining:
- Evolution chain (top half)
- Type advantages/weaknesses (bottom half)

**Database Support:** ✅ Already exists
- `pokemon_types` table ready
- `evolutions` table ready
- Type effectiveness can be calculated

**Implementation Priority:** After generation navigation

---

## Implementation Roadmap

### Phase 1: Foundation (Current Sprint)
**Goal:** Fill critical gaps preventing full experience

1. **State Persistence Module** (1-2 days)
   - Create `StateManager` class
   - JSON file read/write
   - Last viewed + favorites tracking
   - Integration with main app

2. **Audio System Foundation** (2-3 days)
   - Create `AudioManager` class
   - pygame.mixer configuration
   - Lazy-load cry files
   - Integration with detail screen
   - **Blocker:** Need to source/download 386 Pokémon cry audio files

3. **Generation Navigation** (3-4 days)
   - Create `GenerationBrowserScreen`
   - L/R button generation switching
   - Generation badge display
   - Replace HomeScreen as default
   - Validate 3-press rule

### Phase 2: Enhanced Experience
**Goal:** Implement brainstorming "Immediate Opportunities"

4. **Relationships View** (2-3 days)
   - Combined evolution + type matchup screen
   - Visual layout with sprites
   - Database queries for relationships
   - Navigation from detail view

5. **Visual Polish** (2-3 days)
   - Large sprite display (50-60% screen)
   - Type badge icons (colorful)
   - Generation badge graphics
   - Clean layouts per brainstorming

### Phase 3: Validation
**Goal:** Prove the core experience works

6. **Hardware Testing** (1-2 days)
   - Deploy to actual Raspberry Pi
   - Test on target LCD (480x320)
   - Validate performance targets
   - GPIO button testing
   - Audio playback verification

7. **User Experience Testing** (1 day)
   - 3-press rule validation
   - Navigation flow testing
   - First-time experience
   - Nostalgic authenticity check

---

## Critical Path Items

### 🔴 BLOCKER: Pokémon Cry Audio Files
**Status:** Not sourced
**Impact:** Cannot implement audio system without assets
**Action Required:**
- Research legal sources (Bulbapedia, GitHub repos, fan projects)
- Verify licensing for fan project use
- Download or generate 386 cry audio files
- Convert to OGG format if needed
- Organize into `assets/audio/cries/` directory

**Estimated Time:** 4-8 hours (research + download + organization)

### 🟡 DECISION NEEDED: Default Screen Experience
**Question:** What screen shows on startup?

**Options:**
1. **Generation Browser** (per brainstorming)
   - Shows Pokémon #1 (Bulbasaur) or last viewed
   - Always displays a Pokémon
   - Direct navigation via L/R/Up/Down
   - Pros: Matches brainstorming vision, no "dead" menu screens
   - Cons: Need to build new screen

2. **Current HomeScreen Grid**
   - Shows grid of 12 Pokémon
   - Familiar to existing codebase
   - Pros: Already implemented, tested
   - Cons: Doesn't match "always showing a Pokémon" principle

**Recommendation:** Implement GenerationBrowserScreen as new default per brainstorming insights

---

## Success Metrics

### Technical Validation
- [ ] FPS maintains 30+ on Pi 3B+ with full UI
- [ ] Input latency < 100ms
- [ ] Audio playback without stuttering
- [ ] State persists across app restarts
- [ ] All 386 Pokémon accessible via navigation

### UX Validation (from Brainstorming)
- [ ] 3-press rule: Any Pokémon reachable in ≤3 button presses
- [ ] Always-on display: Never shows blank menu, always a Pokémon
- [ ] Visual-first: Sprites take 50-60% of screen space
- [ ] Authentic feel: Feels like holding a real Pokédex

### Architecture Validation
- [ ] State management clean and simple (single JSON file)
- [ ] Audio system lazy-loads (no memory bloat)
- [ ] Generation navigation performant
- [ ] Input abstraction allows hardware swapping

---

## Next Actions (Ordered by Priority)

1. **Immediate:** Source Pokémon cry audio files (4-8 hours)
2. **Day 1-2:** Implement StateManager (save/load last viewed)
3. **Day 2-4:** Implement AudioManager (play cries on detail view)
4. **Day 4-7:** Build GenerationBrowserScreen (L/R navigation)
5. **Day 7-9:** Implement RelationshipsScreen (evolution + types)
6. **Day 10:** Hardware deployment and testing

**Estimated Total:** 10 working days to complete validation phase

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Cannot source audio files legally | Medium | High | Use synthesized cries or proceed without audio initially |
| Performance insufficient on Pi | Low | High | Already validated; optimization tools ready |
| Generation nav breaks existing flows | Low | Medium | Thorough testing; keep old HomeScreen as backup |
| 3-press rule impossible to achieve | Low | Medium | Adjust definition or add search feature |
| Hardware unavailable for testing | Medium | Low | Prototype extensively on desktop first |

---

## Notes
- Keep implementation simple and boring (no over-engineering)
- Prioritize core nostalgic experience over feature creep
- Validate on actual hardware early and often
- Document performance characteristics for future optimization
