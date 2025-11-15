# ShokeDex - Product Requirements Document

**Author:** King
**Date:** 2025-11-14
**Version:** 1.0

---

## Executive Summary

ShokeDex is a handheld Pokédex device that delivers authentic, physical nostalgia for Pokémon fans. Built on Raspberry Pi with LCD display and GPIO button controls, it's designed to be **"a nostalgic experience you can hold"**—the physical sensation of holding a piece of the Pokémon world in your hands, just like the characters in the anime.

This is NOT about having the best Pokémon database (smartphones already do that). This is about **tangible nostalgia**: a collectible that happens to be functional, not software that happens to be physical.

**Target Users:**
- **Primary:** Nostalgic adults (25-35) who grew up with Pokémon Red/Blue/Gold/Silver
- **Secondary:** Kids (8-12) receiving as birthday/holiday gifts who are current Pokémon fans
- **Tertiary:** Pokémon collectors who appreciate physical memorabilia

### What Makes This Special

**Physical authenticity** - A real device you hold and interact with, not just an app. The device embodies the Pokédex experience from the anime through:
- **Anime Season 1 aesthetic** - Visual design inspired by Dexter's interface from the original series
- **Appliance simplicity** - Zero configuration, pick it up and it just works
- **Always-on display** - Never shows blank menus, always displaying a Pokémon
- **Generation organization** - Natural browsing by Kanto/Johto/Hoenn regions
- **Large sprite showcase** - Pokémon images dominate the screen (50-60% of real estate)

---

## Project Classification

**Technical Type:** Embedded Hardware + Software Application
**Domain:** Consumer Entertainment / Fan Project
**Platform:** Raspberry Pi 3B+ or newer
**Complexity:** Medium (Level 2-4)

**Technology Stack:**
- Python 3.11+ with pygame for graphics
- SQLite for local data storage
- GPIO controls for physical buttons
- Small LCD displays (480x320 to 800x480 resolution)
- Offline-first architecture

**Project Context:**
- Greenfield fan project for personal use
- Educational/hobby project (not commercial)
- Supports Pokémon Generations 1-3 (National Pokédex #1-386)
- Resource-constrained hardware environment

---

## Success Criteria

Success means users experience that **"wow, this feels like the real Pokédex"** moment when they first power it on and start browsing. The device should evoke the same feeling of discovery and collection that the anime portrayed.

**Measurable Success Indicators:**
- Device can browse all 386 Gen 1-3 Pokémon smoothly at 30+ FPS
- **Navigation efficiency:** Any Pokémon reachable in ≤3 button presses from home screen
- **Input responsiveness:** Button press latency < 100ms
- **Visual impact:** Sprites take 50-60% of screen real estate
- **Usability:** Users can pick it up without instructions and start using it immediately
- **Authenticity:** Design choices consistently answer "Would Ash have seen this on Dexter's screen?"
- **Performance:** Runs reliably on Raspberry Pi 3B+ without stuttering or lag

---

## Product Scope

### MVP - Minimum Viable Product

The core browsing and viewing experience that makes ShokeDex functional and authentic:

**Essential Features:**
1. **Browse all 386 Pokémon (Gen 1-3)**
   - Complete data for Bulbasaur (#1) through Deoxys (#386)
   - Organized by generation
   
2. **View Pokémon details**
   - Name and National Dex number
   - Type(s) (Fire, Water, Electric, etc.)
   - Base stats (HP, Attack, Defense, Sp.Atk, Sp.Def, Speed) with visual bars
   - Physical stats (height, weight)
   - Pokédex description text
   
3. **Evolution chain display**
   - Show what Pokémon evolves from/into
   - Display evolution requirements where applicable
   
4. **Generation-based navigation**
   - L/R buttons (or equivalent) switch between Kanto/Johto/Hoenn
   - Up/Down buttons scroll through Pokémon within current generation
   - Generation badge/indicator shows current region
   
5. **Large sprite display**
   - Pokémon sprite takes 50-60% of screen real estate
   - High-quality pixel art from Gen 1-3 era
   - Clean, uncluttered layouts
   
6. **Always-on Pokémon display**
   - Device boots directly to showing a Pokémon (last viewed or #1)
   - No blank menu screens or loading screens
   - Every state shows a Pokémon
   
7. **State persistence**
   - Remember last viewed Pokémon across power cycles
   - Fast startup (restores to previous state)

### Growth Features (Pre-GA Release)

Features that enhance the experience and move toward "complete" product:

1. **Type badges as colorful icons**
   - Visual type indicators instead of just text
   - All 18 Pokémon type icons designed
   
2. **Relationships view**
   - Unified screen combining evolution chain + type advantages/weaknesses
   - One-screen view of "how this Pokémon relates to others"
   - Evolution tree on top half, type matchup grid on bottom half
   
3. **"Who's that Pokémon?" quiz/trivia mode**
   - Classic anime segment brought to life
   - Show silhouette, user scrolls to guess
   - Reveals answer with cry and sprite
   - Optional score tracking
   
4. **Screensaver display mode**
   - Activates after 2-3 minutes of inactivity
   - Slowly cycles through Pokémon with occasional cries
   - Any button press to wake
   - Transforms device into desk decoration
   
5. **Pokémon cries audio**
   - Play authentic cry sound when viewing details
   - 386 audio files (one per Pokémon)
   - Volume control
   - **Note:** Audio infrastructure (AudioManager) already implemented

### Vision (Future Enhancements)

Ideas for future iterations beyond GA:

1. **Touch screen interface**
   - Tap to select, swipe to scroll
   - Modern interaction model
   
2. **Physical scroll wheel (iPod-style)**
   - Rotate to browse with tactile detents
   - Press to select
   
3. **Hybrid scroll wheel + touch screen**
   - Best of both worlds: tactile browsing + touch interaction
   
4. **Full anime Season 1 UI replica**
   - Exact recreation of Dexter's interface
   - Holographic blue display aesthetic
   
5. **Mechanical button sounds**
   - Authentic "beep-boop" audio feedback matching anime Pokédex
   
6. **Startup sequence animation**
   - Classic Pokédex boot-up from anime with audio
   
7. **Favorites system with visual indicators**
   - ⭐ marker for favorite Pokémon
   - Quick access to favorites list
   
8. **Pokémon "registration" system**
   - Silhouettes for unseen Pokémon
   - "Pokémon registered!" confirmation on first view
   - Completion tracker showing progress

---

## User Experience Principles

### Core UX Philosophy

**"This is a window into the Pokémon world"** - Prioritize seeing the Pokémon clearly over information density.

**Design Principles:**
1. **Authenticity over features** - Every design choice asks: "Would Ash have seen this on Dexter's screen?"
2. **Visual-first design** - Large, beautiful sprites dominate; clean, uncluttered layouts
3. **Appliance simplicity** - Zero configuration, no settings menu, no help screens
4. **Direct navigation** - 3-press rule ensures efficiency
5. **Always showing content** - Never blank states or empty menus

### Key Interactions

**Primary Navigation Flow:**
```
Power On → See Pokémon (last viewed or Bulbasaur #1)
↓
L/R Buttons → Switch generation (Kanto ↔ Johto ↔ Hoenn)
↓
Up/Down Buttons → Scroll through Pokémon within generation
↓
A Button → View full details (stats, evolution, description)
↓
B Button → Return to browse view
```

**Navigation Constraints:**
- **3-press rule:** Any Pokémon reachable in ≤3 button presses from any screen
- **No dead ends:** Every screen has clear "back" action
- **Instant feedback:** Button press response < 100ms
- **Visual continuity:** Transitions show the same Pokémon to maintain context

**Visual Hierarchy:**
1. **Pokémon sprite** (hero element, 50-60% of screen)
2. **Name and number** (clear identification)
3. **Types** (colorful badges)
4. **Generation indicator** (subtle context)
5. **Additional info** (stats, description - secondary)

**Interaction Design:**
- Hold button for speed scrolling (rapid navigation through list)
- Single press for precise navigation (one Pokémon at a time)
- Wrapping behavior at list boundaries (optional: loop around or stop at edges)
- Smooth transitions between screens (maintain context, avoid jarring changes)

---

## Functional Requirements

### FR1: Pokémon Data Management

**FR1.1 - Pokémon Database**
- System shall store complete data for all 386 Pokémon (Gen 1-3)
- Each Pokémon shall include: National Dex number, name, type(s), base stats, height, weight, Pokédex entry text
- Database shall be preloaded and operate entirely offline

**FR1.2 - Type System**
- System shall support all 17 Pokémon types applicable to Gen 1-3 (excludes Fairy type)
- Types: Normal, Fire, Water, Electric, Grass, Ice, Fighting, Poison, Ground, Flying, Psychic, Bug, Rock, Ghost, Dragon, Dark, Steel
- Pokémon can have 1 or 2 types (dual-typing support)

**FR1.3 - Evolution Data**
- System shall store evolution chains for all Pokémon
- Evolution data shall include pre-evolutions, evolutions, and evolution requirements where applicable
- Support for linear chains (Charmander → Charmeleon → Charizard) and branching chains (Eevee → multiple)

**FR1.4 - Sprite Assets**
- System shall display high-quality pixel art sprites for all 386 Pokémon
- Sprites shall be authentic Gen 1-3 era artwork
- Both thumbnail (small) and detail (large) sprite sizes available

### FR2: Browse and Navigation

**FR2.1 - Generation-Based Browsing**
- System shall organize Pokémon by generation: Kanto (1-151), Johto (152-251), Hoenn (252-386)
- User shall be able to switch between generations using L/R buttons
- Current generation shall be visually indicated with generation badge/logo

**FR2.2 - Scroll Navigation**
- User shall be able to scroll through Pokémon within current generation using Up/Down buttons
- System shall support single-press navigation (one Pokémon at a time)
- System shall support hold-to-scroll navigation (rapid browsing)

**FR2.3 - Always-On Display**
- System shall always display a Pokémon on screen (no blank menus)
- On first startup, system shall display Bulbasaur (#1)
- On subsequent startups, system shall display last viewed Pokémon

**FR2.4 - 3-Press Navigation Rule**
- Any Pokémon shall be reachable within 3 button presses from any screen
- Navigation paths shall be optimized for efficiency

### FR3: Pokémon Detail View

**FR3.1 - Detail Screen Display**
- System shall display detailed Pokémon information when user presses A button
- Large sprite shall occupy 50-60% of screen real estate
- Display shall include: Name, National Dex number, type(s), base stats, height, weight, description

**FR3.2 - Base Stats Visualization**
- System shall display all 6 base stats: HP, Attack, Defense, Special Attack, Special Defense, Speed
- Stats shall be shown with visual progress bars for easy comparison
- Stat values shall be displayed numerically alongside bars

**FR3.3 - Type Display**
- Pokémon type(s) shall be displayed with clear visual indicators
- Type badges shall use type-specific colors for recognition

**FR3.4 - Navigation Within Detail View**
- User shall be able to navigate to adjacent Pokémon using L/R buttons while in detail view
- B button shall return to browse view

### FR4: Evolution Chain Display

**FR4.1 - Evolution Information**
- System shall display evolution chain for current Pokémon
- Show what the Pokémon evolves from (if applicable)
- Show what the Pokémon evolves into (if applicable)
- Display evolution requirements (level, item, method) where applicable

**FR4.2 - Evolution Navigation**
- User shall be able to view evolution stages with sprite thumbnails
- User shall be able to navigate to evolution/pre-evolution from detail view

### FR5: State Persistence

**FR5.1 - Session State**
- System shall remember last viewed Pokémon across power cycles
- System shall restore to last viewed Pokémon on startup

**FR5.2 - User Preferences**
- System shall persist user settings (if any) across sessions
- Volume level shall be remembered (for future audio feature)

### FR6: Generation Badge Display

**FR6.1 - Region Indicators**
- System shall display generation badge showing current region (Kanto/Johto/Hoenn)
- Badge shall use official game logos (Red/Blue, Gold/Silver, Ruby/Sapphire aesthetic)
- Badge shall be visible in browse view

### FR7: Growth Feature - Type Badges

**FR7.1 - Colorful Type Icons** (Post-MVP)
- System shall display type information using colorful icon badges
- All 17 types shall have distinct, recognizable icons
- Icons shall use official Pokémon type colors

### FR8: Growth Feature - Relationships View

**FR8.1 - Unified Relationships Screen** (Post-MVP)
- System shall provide a relationships view combining evolution chain and type matchups
- Evolution chain shall be displayed in top half of screen
- Type advantages/weaknesses shall be displayed in bottom half
- User shall be able to navigate to relationships view from detail screen

**FR8.2 - Type Effectiveness Display** (Post-MVP)
- System shall show types this Pokémon is strong against
- System shall show types this Pokémon is weak against
- Visual indicators (color coding, icons) shall make matchups clear

### FR9: Growth Feature - Quiz Mode

**FR9.1 - "Who's That Pokémon?" Game** (Post-MVP)
- System shall provide a quiz/trivia mode accessible from main menu
- Quiz shall display Pokémon silhouette
- User shall scroll through Pokémon to guess
- System shall reveal answer with sprite and cry (if audio available)

**FR9.2 - Quiz Scoring** (Post-MVP)
- System may optionally track score during quiz session
- System may support difficulty levels (by generation)

### FR10: Growth Feature - Screensaver Mode

**FR10.1 - Idle Display** (Post-MVP)
- System shall enter screensaver mode after 2-3 minutes of inactivity
- Screensaver shall slowly cycle through Pokémon with sprites and names
- Screensaver may occasionally play Pokémon cries (if audio available)

**FR10.2 - Wake from Screensaver** (Post-MVP)
- Any button press shall exit screensaver and return to last active screen
- Screensaver shall not affect application state

### FR11: Growth Feature - Audio System

**FR11.1 - Pokémon Cries** (Post-MVP)
- System shall play authentic Pokémon cry when viewing detail screen
- System shall support all 386 Pokémon cries
- Audio files shall be OGG Vorbis format for compression

**FR11.2 - Volume Control** (Post-MVP)
- System shall support volume adjustment
- Volume setting shall persist across sessions
- User shall be able to mute audio

**FR11.3 - Audio Infrastructure** (Implemented)
- AudioManager class shall lazy-load cry files on demand
- System shall cache up to 20 recently played cries in memory
- System shall handle missing audio files gracefully without crashing

---

## Non-Functional Requirements

### Performance

**NFR-P1: Frame Rate**
- System shall maintain 30+ FPS on Raspberry Pi 3B+ during all operations
- No visible stuttering or lag during navigation or screen transitions

**NFR-P2: Input Latency**
- Button press response time shall be < 100ms
- User shall perceive instant feedback on all button presses

**NFR-P3: Startup Time**
- System shall boot and display a Pokémon within 5 seconds of power-on
- State restoration shall be seamless (no loading screens)

**NFR-P4: Memory Efficiency**
- System shall operate within Raspberry Pi 3B+ memory constraints (1GB RAM)
- Sprite loading shall be optimized (lazy-loading, appropriate caching)
- Audio caching shall be bounded (max 20 cries in memory)

**NFR-P5: Storage**
- Complete application with all data shall fit within 500MB of storage
- Database file shall be portable (single SQLite file)

### Usability

**NFR-U1: Zero Configuration**
- System shall require no setup or configuration by user
- No settings menus or preference screens in MVP
- Device shall work immediately upon power-on

**NFR-U2: Intuitive Navigation**
- Users shall be able to use device without instructions
- Button mappings shall be discoverable through exploration
- Navigation shall feel natural and consistent

**NFR-U3: Visual Clarity**
- All text shall be readable on target display resolutions (480x320 to 800x480)
- Sprites shall be displayed at optimal size for screen
- High contrast between UI elements and background

**NFR-U4: Accessibility**
- Physical buttons shall be easily distinguishable by touch
- Visual feedback shall confirm all button presses
- Color choices shall have sufficient contrast

### Reliability

**NFR-R1: Stability**
- System shall run continuously without crashes
- Graceful error handling for all edge cases (missing data, corrupted files)
- No memory leaks during extended operation

**NFR-R2: Data Integrity**
- Database shall not corrupt during normal operation or power loss
- State file shall be resilient to corruption (fallback to defaults)

**NFR-R3: Offline Operation**
- System shall function completely offline (no internet required)
- All data shall be preloaded during device setup

### Maintainability

**NFR-M1: Code Quality**
- Code shall follow PEP 8 Python style guidelines
- All public functions shall have docstrings
- Type hints shall be used for clarity
- Parameterized SQL queries only (no string formatting)

**NFR-M2: Testability**
- Unit tests shall cover all core functionality
- Test coverage shall be maintained as features are added
- Hardware dependencies shall be mockable for testing

**NFR-M3: Documentation**
- Code shall be well-documented with comments
- README shall explain setup and development workflow
- User quick-start guide shall be provided

### Compatibility

**NFR-C1: Hardware**
- System shall run on Raspberry Pi 3B+ or newer
- Compatible with Raspberry Pi OS (Bookworm - Debian 12)
- Support for small LCD displays (3.5"-7", 480x320 to 800x480)

**NFR-C2: Input Methods**
- Support GPIO buttons (primary)
- Keyboard fallback for development/testing
- Clean abstraction to support future input methods (touch, scroll wheel)

---

## Technical Constraints

### Platform Constraints

1. **Hardware:** Raspberry Pi 3B+ (or newer) required
   - ARM Cortex-A53 CPU
   - 1GB RAM
   - Limited processing power vs. desktop
   
2. **Operating System:** Raspberry Pi OS (Bookworm/Debian 12)
   - Python 3.11+ standard
   - GPIO access via gpiozero library
   
3. **Display:** Small LCD screens
   - Resolution: 480x320 to 800x480 pixels
   - Limited screen real estate
   - Pixel-perfect rendering required

### Software Stack

1. **Python 3.11+** - Primary development language
2. **pygame 2.5.0+** - Graphics rendering and display management
3. **Pillow 10.0.0+** - Image processing and sprite manipulation
4. **SQLite3** - Local database (Python standard library)
5. **gpiozero 2.0.0+** - GPIO interface for physical buttons
6. **requests** - HTTP client (for initial data loading only)

### Architecture Constraints

1. **Offline-first** - No runtime internet dependency
2. **Single-user** - No multi-user or multi-tenancy
3. **Local storage** - All data in SQLite database
4. **Resource-constrained** - Optimize for Raspberry Pi performance
5. **Headless capable** - Can run without desktop environment

### Data Constraints

1. **Pokémon scope:** Gen 1-3 only (National Dex #1-386)
2. **No move data** - Structure exists but not populated (future enhancement)
3. **Static data** - No dynamic updates from external sources after initial setup
4. **Sprite assets** - Must source legally for fan project use

### Development Constraints

1. **Fan project** - Non-commercial, educational use only
2. **Respect Pokémon IP** - Educational fair use, maintain attribution
3. **Open source spirit** - Code should be shareable for learning
4. **Solo developer** - Hobby project pace, burst productivity patterns

---

## Dependencies and Risks

### External Dependencies

**Asset Dependencies:**
1. **Pokémon sprite images** (✅ COMPLETE)
   - 386 sprite files (thumb + detail sizes)
   - Source: Currently populated in project
   
2. **Pokémon cry audio files** (❌ BLOCKER for audio feature)
   - 386 OGG audio files required
   - Sources to investigate: PokeAPI, Veekun database, GitHub repos
   - Legal considerations for fan project use
   - **Estimated effort:** 4-8 hours to source, download, convert
   
3. **Type icon graphics** (⚠️ NEEDED for Growth features)
   - 17 type badge icons
   - Can be created or sourced from fan resources
   
4. **Generation badge graphics** (⚠️ NEEDED for MVP)
   - 3 generation logos (Kanto, Johto, Hoenn)
   - Based on official game logos (Red/Blue, Gold/Silver, Ruby/Sapphire)

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Cannot source audio files legally | Medium | High | Use synthesized cries or defer audio to post-GA |
| Performance insufficient on Pi 3B+ | Low | High | Already validated; optimization tools ready |
| Sprite display too slow | Low | Medium | Lazy loading and caching already implemented |
| GPIO hardware unavailable for testing | Medium | Low | Keyboard fallback exists; prototype on desktop first |
| Screen real estate too limited | Low | Medium | Design for 480x320; test on actual hardware early |

### Project Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Scope creep from "moonshot" ideas | Medium | Medium | Clear MVP → Growth → Vision separation; disciplined prioritization |
| Hobby timeline extends indefinitely | Medium | Low | Kanban flow allows progress at any pace; no hard deadlines |
| Loss of motivation during development | Low | High | Focus on quick wins; always-working MVP approach |

---

## Implementation Planning

### Development Phases

**Phase 1: MVP Foundation (Priority 1)**
- Generation navigation screen
- Detail view with stats
- Evolution chain display
- State persistence
- Generation badges
- Performance optimization

**Phase 2: Growth Features (Priority 2)**
- Type badge icons
- Relationships view
- Audio cry integration
- Quiz/trivia mode
- Screensaver mode

**Phase 3: Polish & GA Release (Priority 3)**
- User quick-start guide
- Final performance tuning
- Hardware deployment and testing
- Bug fixes and edge cases

**Phase 4: Vision Features (Future)**
- Touch screen support
- Scroll wheel hardware
- Advanced UI animations
- Additional generations

### Epic Breakdown Required

This PRD defines requirements comprehensively. Next step is decomposition into:
- **Epics:** Major feature areas
- **User Stories:** Implementable units (200k context limit friendly)
- **Acceptance Criteria:** Clear definition of done

**Next Workflow:** Run epic and story breakdown with Scrum Master (Bob)

---

## References

- **Brainstorming Session:** `docs/bmm-brainstorming-session-2025-11-13.md`
- **Workflow Status:** `docs/bmm-workflow-status.yaml`
- **Architecture Validation Plan:** `docs/architecture-validation-plan.md` (Winston's technical assessment)
- **Architecture Foundation Summary:** `docs/architecture-foundation-summary.md` (Infrastructure implementation)

---

## Next Steps

1. **✅ PRD Complete** - This document
2. **→ Architecture Design** - Winston (Architect) creates system design based on this PRD
3. **→ UX Mockups** - Sally (UX Designer) creates visual designs for key screens
4. **→ Test Strategy** - Murat (Test Architect) defines testing approach
5. **→ Epic & Story Breakdown** - Bob (Scrum Master) decomposes into kanban backlog
6. **→ Implementation** - Amelia (Developer) implements stories from backlog

---

_This PRD captures the essence of ShokeDex: a nostalgic, tangible Pokédex experience that brings the magic of the anime into your hands._

_Created through collaborative discovery between King and the BMAD Product Management team._
