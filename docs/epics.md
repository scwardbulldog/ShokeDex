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

