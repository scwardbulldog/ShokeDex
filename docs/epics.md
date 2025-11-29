# ShokeDex - Epic Breakdown

**Author:** King
**Date:** 2025-11-15
**Project Level:** Medium (Level 2-4)
**Target Scale:** Embedded Hardware + Software Application

---

## Overview

This document provides the complete epic and story breakdown for ShokeDex, decomposing the requirements from the [PRD](./PRD.md) into implementable stories.

**Living Document Notice:** This is the initial version. It will be updated after UX Design and Architecture workflows add interaction and technical details to stories.

---

## Functional Requirements Inventory

Here's every FR from the PRD - this is our coverage checklist to ensure complete implementation:

- **FR1:** Pokémon Data Management (Database, Type System, Evolution Data, Sprite Assets)
- **FR2:** Browse and Navigation (Generation-Based Browsing, Scroll Navigation, Always-On Display, 3-Press Navigation Rule)
- **FR3:** Pokémon Detail View (Detail Screen Display, Base Stats Visualization, Type Display, Navigation Within Detail View)
- **FR4:** Evolution Chain Display (Evolution Information, Evolution Navigation)
- **FR5:** State Persistence (Session State, User Preferences)
- **FR6:** Generation Badge Display (Region Indicators)
- **FR7:** Growth Feature - Type Badges (Colorful Type Icons) [POST-MVP]
- **FR8:** Growth Feature - Relationships View (Unified Relationships Screen, Type Effectiveness Display) [POST-MVP]
- **FR9:** Growth Feature - Quiz Mode ("Who's That Pokémon?" Game, Quiz Scoring) [POST-MVP]
- **FR10:** Growth Feature - Screensaver Mode (Idle Display, Wake from Screensaver) [POST-MVP]
- **FR11:** Growth Feature - Audio System (Pokémon Cries, Volume Control, Audio Infrastructure) [POST-MVP]

---

## Epic Structure Summary

After analyzing the PRD, here's how the work is organized into natural, value-driven groupings:

**Implementation Note:** While conceptually separated below for clarity, **Tech Spec 1** combines Epic 1 and Epic 2 implementation since the foundation work (database setup, managers, screen lifecycle) is inseparable from the core browsing features that validate and exercise those systems. This consolidation reflects the practical reality that you can't build browsing without the infrastructure, and infrastructure isn't truly validated until browsing works.

### **Epic 1: Foundation & Infrastructure**
**Value:** Establishes the technical foundation that enables all subsequent features  
**Scope:** Project setup, core systems initialization, build pipeline, deployment basics  
**FR Coverage:** Infrastructure needs for all FRs (enables everything else)  
**📋 Tech Spec:** Combined with Epic 2 in `tech-spec-epic-1-generation-navigation.md`

### **Epic 2: Core Browsing Experience**
**Value:** Enables users to browse and navigate through all 386 Pokémon efficiently  
**Scope:** Generation switching, scroll navigation, always-on display, generation badge display  
**FR Coverage:** FR2 (Browse and Navigation), FR6 (Generation Badge Display)  
**📋 Tech Spec:** Combined with Epic 1 in `tech-spec-epic-1-generation-navigation.md`

### **Epic 3: Detail View Implementation**
**Value:** Shows complete Pokémon information with large sprites and detailed stats  
**Scope:** Detail screen layout, stats visualization, type display, sprite rendering, description text display  
**FR Coverage:** FR1.4 (Sprite Assets), FR3 (Pokémon Detail View)  
**📋 Tech Spec:** `tech-spec-epic-2-detail-view-with-audio.md`  
**⚠️ Descoped to Post-MVP:** Audio cry playback (moved to Epic 8 - Audio Integration)

### **Epic 4: State Persistence**
**Value:** Device remembers last viewed Pokémon and user preferences across power cycles  
**Scope:** Last viewed Pokémon ID, generation tracking, volume and input mode preferences, state file with JSON persistence  
**FR Coverage:** FR5 (State Persistence - core functionality)  
**📋 Tech Spec:** `tech-spec-epic-3-state-persistence.md`  
**⚠️ Descoped to Post-MVP:** Favorites list, recent history, usage statistics (moved to Epic 9 - User Preferences & History)

### **Epic 5: Evolution System**
**Value:** Displays evolution chains showing how Pokémon transform  
**Scope:** Evolution chain display, evolution navigation, requirements display  
**FR Coverage:** FR1.3 (Evolution Data), FR4 (Evolution Chain Display)  
**📋 Tech Spec:** To be created

---

## Post-MVP Epics (Growth Features)

### **Epic 6: Enhanced Visual Identity** [POST-MVP]
**Value:** Polishes the visual experience with type badges and generation aesthetics  
**Scope:** Type icon system, colorful badges, generation-specific styling  
**FR Coverage:** FR7 (Type Badges)

### **Epic 7: Interactive Features** [POST-MVP]
**Value:** Adds engaging interactions beyond basic browsing  
**Scope:** Quiz mode, relationships view, type effectiveness  
**FR Coverage:** FR8 (Relationships View), FR9 (Quiz Mode)

### **Epic 8: Audio Integration** [POST-MVP]
**Value:** Brings Pokémon to life with authentic cry audio playback  
**Scope:** AudioManager integration, Pokémon cry playback on DetailScreen, LRU audio caching, volume control  
**FR Coverage:** FR11 (Audio System - Pokémon Cries)  
**📦 Source:** Descoped from Epic 3 - requires sourcing 386 audio cry files  
**Dependencies:** Epic 3 (Detail View) must be complete, audio assets sourced

### **Epic 9: User Preferences & History** [POST-MVP]
**Value:** Tracks user behavior and enables personalization features  
**Scope:** Recent Pokémon history (last 10 viewed), favorites list with toggle UI, usage statistics tracking, favorites display on HomeScreen  
**FR Coverage:** FR5.2 (User Preferences - extended)  
**📦 Source:** Descoped from Epic 4 - extends StateManager with additional tracking  
**Dependencies:** Epic 4 (State Persistence) must be complete

### **Epic 10: Screensaver Mode** [POST-MVP]
**Value:** Transforms device into an always-interesting display piece  
**Scope:** Idle detection, screensaver mode with cycling Pokémon, optional cry playback, wake on any button  
**FR Coverage:** FR10 (Screensaver Mode)  
**Dependencies:** Epic 3 (Detail View), optionally Epic 8 (Audio)

**MVP Sequencing Rationale:**
- **Epic 1 (Foundation)** must come first - establishes technical foundation for all subsequent work
- **Epic 2 (Core Browsing)** provides the primary navigation experience - browse and switch between generations
- **Epic 3 (Detail View)** enables viewing complete Pokémon information with sprites and stats
- **Epic 4 (State Persistence)** ensures device remembers user's place across power cycles
- **Epic 5 (Evolution System)** rounds out the core information display by showing evolution chains
- Together, Epics 1-5 deliver the complete MVP: browse → view details → persist state → see evolution chains

**Post-MVP Sequencing Rationale:**
- Epic 6 (visual polish) before complex features
- Epic 8 (audio) independent, can be done anytime after Epic 3
- Epic 9 (preferences/history) extends Epic 4's state system
- Epic 10 (screensaver) benefits from Epic 8 (audio) but doesn't require it
- Epics 7 (interactive features) adds engagement after core is solid

---

## FR Coverage Map

**MVP Epics:**
- **Epic 1:** Infrastructure foundation (enables all FRs)
- **Epic 2:** FR2, FR6 (Browse and Navigation, Generation Badges)
- **Epic 3:** FR1.4, FR3 (Sprite Assets, Detail View)
- **Epic 4:** FR5 (State Persistence)
- **Epic 5:** FR1.3, FR4 (Evolution Data, Evolution Display)

**Post-MVP Epics:**
- **Epic 6:** FR7 (Type Badges) [POST-MVP]
- **Epic 7:** FR8, FR9 (Relationships View, Quiz Mode) [POST-MVP]
- **Epic 8:** FR11 (Audio System - Pokémon Cries) [POST-MVP]
- **Epic 9:** FR5 extended (Favorites, History) [POST-MVP]
- **Epic 10:** FR10 (Screensaver Mode) [POST-MVP]

**Note:** FR1.1 (Database) and FR1.2 (Type System) are already implemented per the architecture documents, so they're foundational infrastructure that Epic 1 will validate and integrate.

---

# Epic Story Breakdowns

## Epic 1 & 2: Foundation & Core Browsing (Combined)

**Epic Goal:** Establish the technical foundation and enable users to browse all 386 Pokémon efficiently across three generations (Kanto/Johto/Hoenn) with smooth navigation and persistent state.

**Tech Spec Reference:** `tech-spec-epic-1-generation-navigation.md`

### Story 1.1: Project Foundation Setup

As a developer,
I want the project structure, dependencies, and core managers initialized,
So that all subsequent features can be built on a solid foundation.

**Acceptance Criteria:**

**Given** a fresh development environment  
**When** the application is initialized  
**Then** all core managers (StateManager, InputManager, ScreenManager, SpriteLoader) are instantiated as singletons  
**And** the database connection is established and validated  
**And** all required directories exist (data/, assets/sprites/, etc.)  
**And** configuration is loaded from environment or defaults  

**And** the application can start without errors  
**And** HomeScreen is set as the initial screen  
**And** the main game loop runs at 30+ FPS

**Prerequisites:** None (foundation story)

**Technical Notes:**
- Use singleton pattern for all managers
- StateManager handles JSON persistence in `data/shokedex_state.json`
- InputManager abstracts keyboard/GPIO inputs to InputAction enum
- SpriteLoader implements LRU cache (max 50 sprites)
- Database validates schema on startup
- Graceful degradation if GPIO unavailable (use keyboard fallback)

---

### Story 1.2: Generation Badge UI Component

As a user,
I want to see which generation (Kanto/Johto/Hoenn) I'm currently browsing,
So that I know which region's Pokémon I'm viewing.

**Acceptance Criteria:**

**Given** HomeScreen is displaying Pokémon from a specific generation  
**When** the screen renders  
**Then** a generation badge is visible in the top-left or top-center area  
**And** the badge shows the current region name ("KANTO", "JOHTO", or "HOENN")  
**And** the badge shows position counter format: "#025/151" (current Pokémon number / total in generation)  

**And** the badge uses holographic blue styling with background rgba(26, 47, 74, 0.9)  
**And** the badge has a 2px solid electric blue (#00d4ff) border  
**And** the badge displays the appropriate region logo (Pokéball for Kanto, GS Ball for Johto, Master Ball for Hoenn)  
**And** if badge assets are missing, fallback to text-only badge with warning logged

**Prerequisites:** Story 1.1 (Foundation)

**Technical Notes:**
- Badge component rendered in HomeScreen._render_generation_badge()
- Use GENERATION_RANGES constant: {1: (1,151), 2: (152,251), 3: (252,386)}
- Logo assets in assets/icons/generation/ directory
- Position counter updates in real-time during scrolling
- Badge positioned to not overlap Pokémon sprite

---

### Story 1.3: Generation Filtering and Database Queries

As a user,
I want to see only Pokémon from the current generation,
So that I can browse regional Pokédexes just like in the games.

**Acceptance Criteria:**

**Given** a user is browsing Pokémon  
**When** a specific generation is selected  
**Then** only Pokémon within that generation's ID range are displayed  
**And** Kanto shows Pokémon #1-151 (Bulbasaur through Mew)  
**And** Johto shows Pokémon #152-251 (Chikorita through Celebi)  
**And** Hoenn shows Pokémon #252-386 (Treecko through Deoxys)  

**And** the database query uses parameterized BETWEEN statement  
**And** query completes in < 50ms  
**And** scroll position resets to first Pokémon when switching generations

**Prerequisites:** Story 1.1 (Foundation)

**Technical Notes:**
- Database.get_pokemon_by_generation(generation: int) method
- SQL: `SELECT id, name, sprite_path FROM pokemon WHERE id BETWEEN ? AND ? ORDER BY id`
- Use GENERATION_RANGES for boundary values
- Return List[Dict] with keys: id, name, sprite_path
- Never use string formatting for SQL queries (security requirement)

---

### Story 1.4: L/R Button Generation Switching

As a user,
I want to switch between Kanto, Johto, and Hoenn using L/R buttons,
So that I can quickly navigate between regional Pokédexes.

**Acceptance Criteria:**

**Given** a user is on HomeScreen viewing a generation  
**When** the user presses the L button (LEFT action)  
**Then** the display switches to the previous generation with circular wrapping: Kanto → Hoenn → Johto → Kanto  
**And** the generation badge updates to show the new region  
**And** the first Pokémon of the new generation is displayed  

**When** the user presses the R button (RIGHT action)  
**Then** the display switches to the next generation with circular wrapping: Kanto → Johto → Hoenn → Kanto  
**And** the transition completes in < 300ms  
**And** visual transition uses fade-out (100ms) → load new list → fade-in (100ms)  
**And** active generation badge glows with bright cyan (#4df7ff)

**Prerequisites:** Story 1.2 (Badge), Story 1.3 (Filtering)

**Technical Notes:**
- HomeScreen._switch_generation(direction: int) method
- Direction: 1 for next (R button), -1 for previous (L button)
- Use modulo arithmetic for circular wrapping: (current + direction - 1) % 3 + 1
- StateManager.set_last_viewed() called with new generation
- Sprite fade implemented using pygame alpha blending

---

### Story 1.5: State Persistence for Generation and Pokémon

As a user,
I want the device to remember which Pokémon and generation I was viewing,
So that when I power it back on, I return to where I left off.

**Acceptance Criteria:**

**Given** a user is viewing Pikachu (#25) in Kanto generation  
**When** the user exits the application  
**Then** StateManager saves pokemon_id=25 and generation=1 to `data/shokedex_state.json`  

**Given** the application starts up  
**When** StateManager loads the state file  
**Then** HomeScreen displays the last viewed Pokémon (Pikachu #25)  
**And** the generation badge shows "KANTO"  

**Given** no state file exists (first boot)  
**When** the application starts  
**Then** default to pokemon_id=1 (Bulbasaur) and generation=1 (Kanto)  

**Given** the state file is corrupted (invalid JSON)  
**When** StateManager attempts to load  
**Then** fallback to defaults without crashing  
**And** log warning about corruption  
**And** overwrite corrupt file with valid defaults

**Prerequisites:** Story 1.1 (Foundation)

**Technical Notes:**
- StateManager stores: pokemon_id, generation, input_mode, volume
- JSON format with atomic write (write to temp file, rename)
- Load time < 50ms, save time < 50ms (measured on Raspberry Pi)
- Validation: clamp pokemon_id (1-386), generation (1-3), volume (0.0-1.0)
- Screen.on_exit() triggers StateManager.save_state()

---

### Story 1.6: Up/Down Scrolling Within Generation

As a user,
I want to scroll through Pokémon within my current generation using Up/Down buttons,
So that I can browse the regional Pokédex sequentially.

**Acceptance Criteria:**

**Given** a user is viewing a Pokémon in a generation  
**When** the user presses the Down button  
**Then** the next Pokémon in the current generation is displayed  
**And** the position counter updates (e.g., #025/151 → #026/151)  
**And** sprite transitions smoothly (fade effect, < 300ms)  

**When** the user presses the Up button  
**Then** the previous Pokémon in the current generation is displayed  

**When** the user holds the Down or Up button  
**Then** scrolling accelerates (hold-to-scroll feature)  
**And** scrolling speed increases after 500ms hold  

**When** the user reaches the last Pokémon in a generation  
**Then** Down button either wraps to first Pokémon OR stops at boundary (configurable behavior)

**Prerequisites:** Story 1.3 (Filtering), Story 1.5 (State Persistence)

**Technical Notes:**
- HomeScreen.handle_input() processes UP/DOWN actions
- Track button hold duration for acceleration
- Acceleration: 1 Pokémon/frame at 500ms hold, 3 Pokémon/frame at 1000ms hold
- Update StateManager.set_last_viewed() on each navigation
- Maintain 30+ FPS during rapid scrolling

---

### Story 1.7: Performance Optimization and 3-Press Navigation Rule

As a user,
I want navigation to feel instant and reach any Pokémon quickly,
So that browsing the Pokédex is efficient and enjoyable.

**Acceptance Criteria:**

**Given** the user is navigating HomeScreen  
**When** performing any operation (generation switch, scrolling, rendering)  
**Then** frame rate remains at 30+ FPS  
**And** button press response time is < 100ms  
**And** visual feedback appears immediately on button press  

**Given** a user is on any screen  
**When** navigating to any specific Pokémon  
**Then** the Pokémon is reachable within 3 button presses  
**And** example paths verified:
  - Kanto (#25) to Hoenn (#252): L/R twice + scroll once = 3 presses ✅
  - Any Pokémon to adjacent Pokémon in same gen: 1 press ✅

**Given** the application runs for extended periods  
**When** monitoring memory usage  
**Then** no memory leaks detected (stable memory footprint)  
**And** sprite cache stays within 50-sprite limit

**Prerequisites:** All previous stories in Epic 1 & 2

**Technical Notes:**
- Profile with tools/profile_performance.py
- Use pygame dirty rects for efficient rendering
- Sprite cache uses LRU eviction policy
- Monitor with PerformanceMonitor class (track FPS, frame time, memory)
- Test on actual Raspberry Pi 3B+ hardware

---

## Epic 3: Detail View Implementation

**Epic Goal:** Show complete Pokémon information with large sprites, detailed stats, type display, and physical measurements.

**Tech Spec Reference:** `tech-spec-epic-2-detail-view-with-audio.md`

**Note:** Audio cry playback originally planned for this epic has been descoped to Epic 8 (Post-MVP).

### Story 3.1: Detail Screen Layout and Sprite Display

As a user,
I want to see a large, clear sprite of the current Pokémon on the detail screen,
So that I can admire the Pokémon artwork prominently.

**Acceptance Criteria:**

**Given** a user presses A button on HomeScreen to view details  
**When** DetailScreen loads  
**Then** a large Pokémon sprite is displayed at 120-150px size  
**And** the sprite occupies 50-60% of screen real estate (hero element)  
**And** sprite is loaded from SpriteLoader cache (detail size variant)  

**And** the screen header shows Pokémon name and National Dex number  
**And** layout matches UX spec DetailScreen mockup  
**And** holographic blue styling applied (electric blue #00d4ff borders)  
**And** all UI elements remain within display boundaries (no cutoff)

**Prerequisites:** Epic 1 & 2 stories (HomeScreen navigation complete)

**Technical Notes:**
- DetailScreen class extends Screen base class
- Constructor accepts pokemon_id parameter from HomeScreen
- SpriteLoader.load_sprite(pokemon_id, "detail") returns 128x128 surface
- Header font: Orbitron Bold, 24px, white (#ffffff)
- Panel backgrounds: rgba(26, 47, 74, 0.9) with 2px electric blue borders

---

### Story 3.2: Six Base Stats with Visual Progress Bars

As a user,
I want to see all six base stats with visual bars,
So that I can quickly compare a Pokémon's strengths and weaknesses.

**Acceptance Criteria:**

**Given** DetailScreen is displaying a Pokémon  
**When** the stats section renders  
**Then** all 6 base stats are shown: HP, Attack, Defense, Sp.Atk, Sp.Def, Speed  
**And** each stat displays: label (left), visual progress bar (center), numeric value (right)  
**And** stat bars fill proportionally: (base_stat / 255) * bar_width  
**And** stat values are accurate from database (no hardcoded values)  

**And** stats are color-coded:
  - 0-50: Gray (#718096)
  - 51-100: Electric blue (#00d4ff)
  - 101-150: Bright cyan (#4df7ff)
  - 151+: Plasma orange (#ff6b35)  
**And** high stats (100+) have subtle glow effect  
**And** stat panel fits within designated screen area (no overflow)

**Prerequisites:** Story 3.1 (Detail Screen Layout)

**Technical Notes:**
- Database.get_pokemon_stats(pokemon_id) returns List[Tuple[str, int]]
- DetailScreen._render_stat_bars() draws bars using pygame.draw.rect()
- Font: Share Tech Mono, 14px for labels, 16px for values
- Use STAT_COLORS constant for color mapping
- Glow effect: draw second bar with alpha=128, offset by 2px

---

### Story 3.3: Type Badge Display on Detail View

As a user,
I want to see the Pokémon's type(s) with visual badges,
So that I can quickly identify what type(s) it is.

**Acceptance Criteria:**

**Given** a Pokémon with a single type (e.g., Pikachu - Electric)  
**When** DetailScreen displays types  
**Then** one type badge is shown with appropriate color and icon  

**Given** a Pokémon with dual types (e.g., Charizard - Fire/Flying)  
**When** DetailScreen displays types  
**Then** two type badges are shown side-by-side  
**And** badges use type-specific colors from holographic palette  
**And** type names are displayed in the badges  

**And** badge styling matches HomeScreen type badges (consistent UI)  
**And** badges positioned near sprite, not overlapping other elements

**Prerequisites:** Story 3.1 (Detail Screen Layout)

**Technical Notes:**
- Database.get_pokemon_types(pokemon_id) returns List[str]
- Type colors defined in src/ui/colors.py TYPE_COLORS dict
- Render type badges as rounded rectangles with type name text
- Font: Rajdhani Bold, 14px, white text
- Position badges in top-right corner or below sprite

---

### Story 3.4: Physical Measurements Display

As a user,
I want to see the Pokémon's height and weight,
So that I understand its physical characteristics.

**Acceptance Criteria:**

**Given** DetailScreen is displaying a Pokémon  
**When** the physical data section renders  
**Then** height is displayed in meters (e.g., "0.4m")  
**And** weight is displayed in kilograms (e.g., "6.0kg")  
**And** values are accurate from database pokemon table  
**And** formatting is consistent (one decimal place for height, one for weight)  

**And** labels "Height:" and "Weight:" use ice blue color (#a8e6ff)  
**And** values are displayed in white (#ffffff)  
**And** font: Rajdhani, 16px

**Prerequisites:** Story 3.1 (Detail Screen Layout)

**Technical Notes:**
- Database.get_pokemon_physical_data(pokemon_id) returns (height: float, weight: float)
- Format strings: f"{height:.1f}m", f"{weight:.1f}kg"
- Position in lower section of detail panel
- Align labels right, values left for clean layout

---

### Story 3.5: Pokédex Description Text Display

As a user,
I want to read the Pokémon's Pokédex entry description,
So that I can learn about its lore and characteristics.

**Acceptance Criteria:**

**Given** DetailScreen is displaying a Pokémon  
**When** the description section renders  
**Then** authentic flavor text is displayed from database  
**And** text is wrapped at word boundaries to max 400px width  
**And** maximum 4 lines displayed with 22.4px line height  

**And** text exceeding 4 lines is truncated with "..." on line 4  
**And** font: Rajdhani, 16px, ice blue color (#a8e6ff)  
**And** all text remains within display boundaries  
**And** description is readable against dark blue background

**Prerequisites:** Story 3.1 (Detail Screen Layout)

**Technical Notes:**
- Database.get_pokemon_description(pokemon_id) returns str
- Use pygame font.render() with wrapping logic
- Pre-render description lines in on_enter() for performance
- Test with longest descriptions (legendary Pokémon often have long text)
- Cache rendered text surfaces to avoid re-rendering each frame

---

### Story 3.6: Adjacent Pokémon Navigation in Detail View

As a user,
I want to navigate to the previous/next Pokémon using L/R buttons while in detail view,
So that I can browse details without returning to HomeScreen.

**Acceptance Criteria:**

**Given** a user is viewing DetailScreen for Pokémon #25 (Pikachu)  
**When** the user presses L button (LEFT action)  
**Then** DetailScreen navigates to Pokémon #24 (Arbok)  
**And** all data and sprite update to show Arbok  
**And** user stays in DetailScreen (doesn't return to HomeScreen)  

**When** the user presses R button (RIGHT action)  
**Then** DetailScreen navigates to Pokémon #26 (Raichu)  

**When** at Pokémon #1 and user presses L  
**Then** wrap to Pokémon #386 (Deoxys)  

**When** at Pokémon #386 and user presses R  
**Then** wrap to Pokémon #1 (Bulbasaur)  

**And** transition completes in < 300ms (database query + sprite load + render)  
**And** smooth fade transition between Pokémon

**Prerequisites:** All previous Epic 3 stories (complete DetailScreen)

**Technical Notes:**
- DetailScreen._navigate_adjacent(direction: int) method
- Wrapping logic: next = (current % 386) + 1, prev = ((current - 2) % 386) + 1
- StateManager.set_last_viewed() updates with new pokemon_id
- SpriteLoader cache ensures fast sprite retrieval
- B button returns to HomeScreen (original behavior)

---

### Story 3.7: Detail View Performance and Visual Polish

As a user,
I want the detail view to load quickly and render smoothly,
So that browsing details feels responsive and polished.

**Acceptance Criteria:**

**Given** a user navigates to DetailScreen  
**When** the screen renders  
**Then** frame rate maintains 30+ FPS during all operations  
**And** DetailScreen initial render time < 33ms per frame  

**Given** a user navigates between adjacent Pokémon  
**When** using L/R buttons  
**Then** navigation completes in < 300ms total (load + render)  
**And** database query time < 50ms for all Pokémon data  

**Given** a user returns to previously viewed DetailScreen  
**When** screen loads with cached data  
**Then** render completes within 50ms (cached sprites and data)  
**And** no memory leaks from sprite cache  

**And** all visual elements match UX Design Specification  
**And** holographic blue styling consistently applied  
**And** panel backgrounds use dark blue with transparency  
**And** layout tested on target display resolutions (480x320, 800x480)

**Prerequisites:** All previous Epic 3 stories

**Technical Notes:**
- Profile with tools/profile_performance.py
- Monitor with PerformanceMonitor.track_frame_time()
- Pre-render static text surfaces in on_enter()
- Use dirty rects for efficient screen updates
- Test on Raspberry Pi 3B+ to validate performance
- Compare rendered output to UX mockup for visual accuracy

---

### Story 3.8: Home Screen Holographic Theme Alignment

As a user,
I want the Home Screen to use the same holographic blue color scheme as the Detail Screen,
So that the visual experience feels cohesive and polished across all screens.

**Acceptance Criteria:**

**Given** a user is on the Home Screen  
**When** the screen renders  
**Then** the background uses `DEEP_SPACE_BLACK` (#0a0e1a) instead of `DARK_GREEN`  
**And** the grid cell borders use `ELECTRIC_BLUE` (#00d4ff) for consistency with Detail Screen panels  
**And** selected Pokémon cell uses `DARK_BLUE` (#1a2f4a) background with `BRIGHT_CYAN` (#4df7ff) border  
**And** the title "ShokeDex" uses `HOLOGRAM_WHITE` (#e8f4f8)  
**And** secondary text (page indicator, view mode, help text) uses `ICE_BLUE` (#a8e6ff)  
**And** the search/filter bar buttons use holographic styling matching the Detail Screen panels  
**And** visual transition between Home Screen and Detail Screen feels seamless (no jarring color change)

**Prerequisites:** Story 3.7 (Epic 3 Detail View complete)

**Technical Notes:**
- Update `HomeScreen.render()` to use `Colors.DEEP_SPACE_BLACK` instead of `Colors.BACKGROUND`
- Update grid cell rendering (`_render_grid()`) to use holographic colors for borders and selection
- Update search bar (`_render_search_bar()`) button styling to use holographic palette
- The `GenerationBadge` class already uses holographic colors - no changes needed there
- Consider adding `Colors.SELECTION_BG_HOLOGRAPHIC` alias for consistency
- Verify all text remains readable against dark background
- Screenshot comparison for visual regression testing

---

## Epic 4: State Persistence

**Epic Goal:** Device remembers last viewed Pokémon, generation, and user preferences across power cycles.

**Tech Spec Reference:** `tech-spec-epic-3-state-persistence.md`

**Note:** Favorites list, recent history, and usage statistics originally planned for this epic have been descoped to Epic 9 (Post-MVP).

### Story 4.1: First Boot State Initialization

As a user,
I want the device to work perfectly on first boot without any setup,
So that I can start using it immediately.

**Acceptance Criteria:**

**Given** the application launches for the first time (no state file exists)  
**When** StateManager initializes  
**Then** a state file is created at `data/shokedex_state.json`  
**And** the file contains valid JSON with default values:
  - pokemon_id: 1 (Bulbasaur)
  - generation: 1 (Kanto)
  - input_mode: "keyboard"
  - volume: 0.7  

**And** HomeScreen displays Bulbasaur (#1) on first boot  
**And** generation badge shows "KANTO"  
**And** no errors or warnings logged for missing state

**Prerequisites:** Epic 1 Story 1.1 (Foundation with StateManager)

**Technical Notes:**
- StateManager.__init__() checks if state file exists
- If not, create with DEFAULT_STATE constants
- JSON format: {"pokemon_id": 1, "generation": 1, "input_mode": "keyboard", "volume": 0.7}
- Use atomic write (write temp file, rename) to prevent corruption
- File permissions: readable/writable by user only

---

### Story 4.2: Last Viewed Pokémon Persistence

As a user,
I want the device to remember which Pokémon I was viewing,
So that I pick up right where I left off.

**Acceptance Criteria:**

**Given** a user views Pikachu (#25) in Kanto generation  
**When** the user exits HomeScreen (transitions to DetailScreen or quits app)  
**Then** StateManager saves pokemon_id=25 and generation=1 to state file  
**And** save operation completes in < 50ms (non-blocking)  

**Given** the application restarts  
**When** HomeScreen.on_enter() executes  
**Then** StateManager.get_last_viewed_id() returns 25  
**And** StateManager.get_last_viewed_generation() returns 1  
**And** HomeScreen displays Pikachu (#25)  
**And** generation badge shows "KANTO"

**Given** a user views Chikorita (#152) in Johto, then exits  
**When** the application restarts  
**Then** HomeScreen displays Chikorita (#152) in Johto generation

**Prerequisites:** Story 4.1 (State Initialization)

**Technical Notes:**
- StateManager.set_last_viewed(pokemon_id, generation) method
- Called from HomeScreen.on_exit() and DetailScreen.on_exit()
- JSON updated with current pokemon_id and generation fields
- Load operation in __init__() or get methods < 50ms
- Validation: clamp pokemon_id to 1-386, generation to 1-3

---

### Story 4.3: Boot to HomeScreen Behavior

As a user,
I want the device to always boot to the browse screen,
So that I have a consistent starting point.

**Acceptance Criteria:**

**Given** a user is viewing DetailScreen showing Raichu (#26)  
**When** the user powers off the device  
**Then** StateManager saves pokemon_id=26  

**Given** the application restarts  
**When** the screen stack initializes  
**Then** the application boots to HomeScreen (not DetailScreen)  
**And** HomeScreen shows Raichu (#26) selected (last viewed)  
**And** user can press A button to navigate back to DetailScreen if desired  

**And** the device never boots directly into DetailScreen  
**And** boot to HomeScreen is the consistent behavior regardless of where user exited

**Prerequisites:** Story 4.2 (Last Viewed Persistence)

**Technical Notes:**
- main.py startup logic always initializes ScreenManager with HomeScreen
- StateManager provides pokemon_id to HomeScreen for selection cursor
- DetailScreen accessed via A button from HomeScreen (standard navigation)
- This design decision ensures predictable boot behavior
- Documented in architecture: "Always boot to browse view"

---

### Story 4.4: Volume and Input Mode Preferences

As a user,
I want my volume and input preferences saved,
So that they persist across sessions.

**Acceptance Criteria:**

**Given** a user sets volume to 0.5 (50%)  
**When** the user exits the application  
**Then** StateManager saves volume=0.5 to state file  

**Given** the application restarts  
**When** StateManager loads state  
**Then** StateManager.get_volume() returns 0.5  
**And** (future audio feature will use this volume setting)  

**Given** a user's input mode is set to "gpio"  
**When** the application restarts  
**Then** StateManager.get_input_mode() returns "gpio"  
**And** InputManager can use this to configure button controls  

**And** volume is validated and clamped to 0.0-1.0 range  
**And** input_mode validated to be "keyboard" or "gpio"  
**And** invalid values reset to defaults with warning logged

**Prerequisites:** Story 4.1 (State Initialization)

**Technical Notes:**
- StateManager.set_volume(volume: float) and get_volume() methods
- StateManager.set_input_mode(mode: str) and get_input_mode() methods
- Volume clamping: max(0.0, min(1.0, volume))
- Input mode validation: mode in ["keyboard", "gpio"] else "keyboard"
- State file updated atomically (temp file + rename)

---

### Story 4.5: State File Corruption Recovery

As a user,
I want the device to recover gracefully if the state file is corrupted,
So that the device always works even if something goes wrong.

**Acceptance Criteria:**

**Given** the state file is manually corrupted (invalid JSON)  
**When** the application starts and StateManager initializes  
**Then** the application does not crash  
**And** StateManager loads default values (Bulbasaur, Kanto, keyboard, 0.7 volume)  
**And** corrupt file is overwritten with valid defaults  
**And** warning logged: "State file corrupted, resetting to defaults"  

**Given** the state file contains invalid values (e.g., pokemon_id=999, generation=5)  
**When** StateManager loads state  
**Then** invalid values are clamped to valid ranges:
  - pokemon_id clamped to 1-386
  - generation clamped to 1-3
  - volume clamped to 0.0-1.0  
**And** the application continues with valid clamped values  
**And** corrected values written back to state file

**Prerequisites:** Story 4.1 (State Initialization)

**Technical Notes:**
- Wrap JSON parsing in try/except block
- Catch json.JSONDecodeError and reset to defaults
- Validation functions for each field with clamping logic
- Log warnings for corruption and invalid values
- Test by manually corrupting state file and restarting app

---

### Story 4.6: State Persistence Performance and Reliability

As a user,
I want state saving to be fast and reliable,
So that it doesn't slow down navigation or cause data loss.

**Acceptance Criteria:**

**Given** the application is running  
**When** StateManager.save_state() is called  
**Then** save operation completes in < 50ms  
**And** no perceptible delay in screen transitions  

**Given** rapid navigation through screens  
**When** screens call on_exit() triggering saves  
**Then** frame rate remains 30+ FPS  
**And** save operations don't cause stuttering  

**Given** the application starts  
**When** StateManager loads state file  
**Then** load operation completes in < 50ms  
**And** application boots to HomeScreen in < 5 seconds total (per NFR-P3)  

**Given** the application shuts down cleanly  
**When** the finally block in main.py executes  
**Then** state_manager.save_state() is called  
**And** final state is written to file before exit  

**And** state file uses atomic write (temp + rename) to prevent corruption during write  
**And** no state data is lost during normal shutdowns

**Prerequisites:** All previous Epic 4 stories

**Technical Notes:**
- Profile save_state() and load_state() with timing measurements
- Use PerformanceMonitor to track save durations
- Atomic write pattern:
  1. Write to data/shokedex_state.tmp
  2. os.rename() to data/shokedex_state.json (atomic on POSIX)
- main.py structure: try/except with finally calling save_state()
- Test on Raspberry Pi SD card for realistic I/O performance

---

## Epic 5: Evolution System

**Epic Goal:** Display evolution chains showing how Pokémon transform, with navigation to evolution relatives.

**Tech Spec Reference:** `tech-spec-epic-5-evolution-system.md`

### Story 5.1: Three-Stage Evolution Chain Display

As a user,
I want to see complete evolution chains for three-stage evolutions,
So that I understand the full evolutionary path.

**Acceptance Criteria:**

**Given** a Pokémon with a three-stage evolution chain (e.g., Charmander → Charmeleon → Charizard)  
**When** viewing DetailScreen  
**Then** all three stages are displayed horizontally with sprites, names, and Dex numbers  
**And** arrows are shown between stages pointing in the direction of evolution  
**And** evolution requirements are displayed below each arrow (e.g., "Level 16", "Level 36")  

**And** sprites are thumbnail size (64x64 or similar)  
**And** current Pokémon is highlighted with brighter cyan glow (#4df7ff)  
**And** "Current" label displayed underneath the current Pokémon's sprite  
**And** panel uses holographic blue styling with electric blue (#00d4ff) borders

**Prerequisites:** Epic 3 (DetailScreen complete)

**Technical Notes:**
- Database.get_evolution_chain(pokemon_id) returns List[Dict] with evolution data
- EvolutionPanel component within DetailScreen renders chain
- Query evolution_chain table: pre_evolution_id, pokemon_id, evolution_id, method, requirement
- Horizontal layout: [Sprite 1] → [Sprite 2] → [Sprite 3]
- SpriteLoader loads thumbnail sprites for all chain members

---

### Story 5.2: Branching Evolution Display

As a user,
I want to see all branching evolution paths,
So that I understand all possible evolution options (like Eevee).

**Acceptance Criteria:**

**Given** a Pokémon with branching evolutions (e.g., Eevee → Vaporeon/Jolteon/Flareon/Espeon/Umbreon)  
**When** viewing DetailScreen  
**Then** all evolution branches are displayed with clear visual separation  
**And** current Pokémon is shown as the root with branches spreading from it  
**And** each branch shows the evolved form with its sprite and name  
**And** evolution requirements are shown for each branch (e.g., "Water Stone", "Thunder Stone", "Fire Stone", "Happiness (Day)", "Happiness (Night)")  

**And** layout accommodates up to 5 branches (Gen 1-3 max is 5 for Eevee)  
**And** branching indicator (split arrows or tree structure) clearly shows relationship  
**And** all branches fit within evolution panel boundaries

**Prerequisites:** Story 5.1 (Three-Stage Display)

**Technical Notes:**
- Database query identifies branching: COUNT(evolution_id) > 1 for same pre_evolution_id
- Vertical stacking or fan-out layout for branches
- Consider space constraints: may need smaller sprites for 5+ branches
- Test with Eevee (#133), Tyrogue (#236), Wurmple (#265)

---

### Story 5.3: Single-Stage Pokémon Handling

As a user,
I want to see a clear message when a Pokémon has no evolutions,
So that I understand it's a standalone species.

**Acceptance Criteria:**

**Given** a single-stage Pokémon with no evolutions (e.g., Ditto #132, Farfetch'd #83, Heracross #214)  
**When** viewing DetailScreen  
**Then** the evolution panel displays "No evolutions" message  
**And** message is centered in the panel  
**And** message uses ice blue color (#a8e6ff)  
**And** panel maintains consistent styling with holographic blue border  

**And** the panel is still visible (not hidden) to maintain visual consistency  
**And** message is clear and not perceived as an error

**Prerequisites:** Story 5.1 (Three-Stage Display)

**Technical Notes:**
- Database query returns empty list for get_evolution_chain(pokemon_id)
- EvolutionPanel checks if chain list is empty
- Render centered text: "No evolutions" in Rajdhani 16px
- Keep panel structure consistent with other DetailScreen panels
- Test with various single-stage Pokémon across generations

---

### Story 5.4: Evolution Requirement Display (Level/Stone/Trade)

As a user,
I want to see exactly how each Pokémon evolves,
So that I know what's required for evolution.

**Acceptance Criteria:**

**Given** an evolution with a level requirement (e.g., Bulbasaur → Ivysaur at level 16)  
**When** displaying the evolution chain  
**Then** "Level 16" text is shown below the evolution arrow  
**And** text uses ice blue color (#a8e6ff)  

**Given** an evolution with a stone requirement (e.g., Pikachu → Raichu with Thunder Stone)  
**When** displaying the evolution chain  
**Then** "Thunder Stone" text is shown below the evolution arrow  

**Given** an evolution requiring trade (e.g., Machoke → Machamp)  
**When** displaying the evolution chain  
**Then** "Trade" text is shown below the evolution arrow  
**And** trade-with-item cases handled (e.g., "Trade holding Metal Coat" for Onix → Steelix)  

**And** all requirement text is readable and not truncated  
**And** font: Rajdhani, 14px, ice blue (#a8e6ff)

**Prerequisites:** Story 5.1 (Three-Stage Display)

**Technical Notes:**
- evolution_chain.method column: "level", "stone", "trade", "happiness", etc.
- evolution_chain.requirement column: level number, stone name, item name, etc.
- Format requirement string based on method:
  - level: "Level {requirement}"
  - stone: "{requirement}" (e.g., "Thunder Stone")
  - trade: "Trade" or "Trade holding {requirement}"
- Handle null requirements gracefully (some evolutions have complex conditions)

---

### Story 5.5: Navigation to Evolution Relatives

As a user,
I want to tap or select an evolution relative to view its details,
So that I can explore the evolution chain interactively.

**Acceptance Criteria:**

**Given** the evolution panel displays multiple Pokémon in a chain  
**When** the user presses A button while focused on an evolution sprite  
**Then** DetailScreen navigates to that Pokémon's detail view  
**And** the new DetailScreen displays the selected Pokémon with ITS evolution chain  
**And** user can continue navigating through evolution relatives  

**And** B button returns to previous DetailScreen (navigation stack)  
**And** selection cursor or highlight indicates which evolution sprite is focused  
**And** Up/Down buttons navigate between evolution sprites in the panel  

**And** navigation is smooth and responsive (< 300ms transition)

**Prerequisites:** Story 5.1, 5.2 (Evolution Display Complete)

**Technical Notes:**
- EvolutionPanel maintains list of clickable/selectable evolution sprites
- Track focused_evolution_index for keyboard/button navigation
- A button triggers: screen_manager.push_screen(DetailScreen(selected_pokemon_id))
- B button pops screen stack: screen_manager.pop_screen()
- Visual focus indicator: border or glow around selected evolution sprite
- Update StateManager.set_last_viewed() when navigating to new Pokémon

---

### Story 5.6: Evolution System Performance and Data Accuracy

As a user,
I want the evolution panel to load quickly and show accurate data,
So that browsing evolution chains is smooth and trustworthy.

**Acceptance Criteria:**

**Given** a user navigates to DetailScreen for the first time  
**When** the evolution panel renders (database query + sprite loading)  
**Then** rendering completes within 200ms  
**And** frame rate maintains 30+ FPS during render  

**Given** a user returns to a previously viewed DetailScreen  
**When** the evolution panel renders with cached data and sprites  
**Then** rendering completes within 50ms  

**Given** all 386 Gen 1-3 Pokémon  
**When** viewing each Pokémon's evolution chain  
**Then** evolution data is accurate matching PokéAPI source  
**And** evolution requirements are correct for each stage  

**And** visual consistency: holographic blue aesthetic applied  
**And** electric blue (#00d4ff) for arrows and borders  
**And** ice blue (#a8e6ff) for requirement text  
**And** 16px padding and consistent spacing maintained  

**And** no crashes or errors for any Pokémon's evolution data  
**And** graceful handling of missing or incomplete evolution data

**Prerequisites:** All previous Epic 5 stories

**Technical Notes:**
- Profile with tools/profile_performance.py
- Cache evolution chain queries in-memory (Dict[int, List[Dict]])
- SpriteLoader cache handles thumbnail sprite reuse
- Validate evolution data against known chains (e.g., Charizard line, Eevee branches)
- Test edge cases: Pokémon with no evolutions, branching evolutions, item-based evolutions
- Verify layout on both 480x320 and 800x480 resolutions

---

## FR Coverage Matrix

This matrix shows exactly which stories implement which functional requirements from the PRD:

| FR | Description | Stories |
|----|-------------|---------|
| **FR1.1** | Pokémon Database | Foundation (pre-existing, validated by all stories using Database) |
| **FR1.2** | Type System | Foundation (pre-existing), Story 3.3 (Type Badge Display) |
| **FR1.3** | Evolution Data | Story 5.1-5.6 (Evolution System) |
| **FR1.4** | Sprite Assets | Story 3.1 (Detail Screen Sprite Display), all stories using SpriteLoader |
| **FR2.1** | Generation-Based Browsing | Story 1.3 (Generation Filtering), Story 1.4 (L/R Switching) |
| **FR2.2** | Scroll Navigation | Story 1.6 (Up/Down Scrolling) |
| **FR2.3** | Always-On Display | Story 1.1 (Foundation), Story 4.2 (Last Viewed Persistence) |
| **FR2.4** | 3-Press Navigation Rule | Story 1.7 (Performance and 3-Press Rule) |
| **FR3.1** | Detail Screen Display | Story 3.1 (Layout and Sprite), Stories 3.2-3.5 (Stats, Types, Physical, Description) |
| **FR3.2** | Base Stats Visualization | Story 3.2 (Six Base Stats with Visual Bars) |
| **FR3.3** | Type Display | Story 3.3 (Type Badge Display) |
| **FR3.4** | Navigation Within Detail View | Story 3.6 (Adjacent Pokémon Navigation) |
| **FR4.1** | Evolution Information | Story 5.1 (Three-Stage), Story 5.2 (Branching), Story 5.3 (No Evolutions), Story 5.4 (Requirements) |
| **FR4.2** | Evolution Navigation | Story 5.5 (Navigation to Evolution Relatives) |
| **FR5.1** | Session State | Story 4.1 (First Boot), Story 4.2 (Last Viewed Persistence), Story 4.3 (Boot Behavior) |
| **FR5.2** | User Preferences | Story 4.4 (Volume and Input Mode Preferences) |
| **FR6.1** | Region Indicators | Story 1.2 (Generation Badge UI Component) |

**Non-Functional Requirements Coverage:**

| NFR | Description | Stories |
|-----|-------------|---------|
| **NFR-P1** | Frame Rate (30+ FPS) | Story 1.7, Story 3.7, Story 5.6 (Performance stories in each epic) |
| **NFR-P2** | Input Latency (<100ms) | Story 1.7 (Performance and 3-Press Rule) |
| **NFR-P3** | Startup Time (<5s) | Story 4.6 (State Persistence Performance) |
| **NFR-P4** | Memory Efficiency | Story 1.7 (sprite cache limits), Story 3.7 (no memory leaks) |
| **NFR-U1** | Zero Configuration | Story 4.1 (First Boot Defaults) |
| **NFR-U2** | Intuitive Navigation | Story 1.4 (L/R Switching), Story 1.6 (Up/Down Scrolling) |
| **NFR-R1** | Stability | Story 4.5 (Corruption Recovery), all stories with error handling |
| **NFR-R2** | Data Integrity | Story 4.5 (Corruption Recovery), Story 4.6 (Atomic Writes) |

**Post-MVP Features (Epics 6-10):** Not yet decomposed into stories. These will be detailed when prioritized for implementation.

---

## Summary

**MVP Story Breakdown Complete:**

✅ **Epic 1 & 2 (Foundation + Core Browsing):** 7 stories covering infrastructure, generation navigation, state persistence, and scrolling  
✅ **Epic 3 (Detail View):** 7 stories covering layout, stats, types, physical data, descriptions, and adjacent navigation  
✅ **Epic 4 (State Persistence):** 6 stories covering first boot, last viewed Pokémon, preferences, corruption recovery, and performance  
✅ **Epic 5 (Evolution System):** 6 stories covering evolution chains, branching, requirements, navigation, and performance

**Total MVP Stories:** 26 implementable stories with detailed BDD-style acceptance criteria

**FR Coverage:** All MVP functional requirements (FR1-FR6) mapped to specific stories with complete traceability

**Next Steps in BMad Method:**

1. **UX Design Workflow** (if UI refinement needed) - Add interaction details to story acceptance criteria
2. **Architecture Review** - Validate technical approach, add implementation notes to stories  
3. **Story Drafting** - Create individual story files in `docs/sprint-artifacts/stories/` for each story
4. **Implementation** - Dev agents pick up stories from backlog with full context (PRD + epics.md + tech specs + UX + architecture)

**This Document is Now Ready For:**
- Story-level planning and estimation
- Individual story file creation (drafting workflow)
- Developer implementation reference
- Progress tracking against FR coverage matrix

