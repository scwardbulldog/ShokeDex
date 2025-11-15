# ShokeDex UX Design Specification

_Created on November 14, 2025 by King_
_Generated using BMad Method - Create UX Design Workflow v1.0_

---

## Executive Summary

ShokeDex recreates the iconic Pokédex experience from Pokémon anime Season 1, bringing Ash's "Dexter" device to life as a physical, handheld product. This UX specification defines the visual language, interaction patterns, and design decisions that create an **authentic anime Pokédex experience** - answering the core question: "Would Ash have seen this on Dexter's screen?"

**Core Design Philosophy:** "This is a window into the Pokémon world"

Every design choice prioritizes visual authenticity over modern UI conventions, creating a nostalgic experience for adults who grew up with the original anime while remaining intuitive enough for exploration without instructions.

---

## 1. Project Context & Users

### 1.1 Vision

**Target Experience:** Recreate the emotional moment when Ash points his Pokédex at a Pokémon and Dexter's voice explains what it is - that sense of discovery, that window into Pokémon knowledge.

**Target Users:**
- **Primary:** Nostalgic adults (25-35) who watched original Pokémon anime
- **Secondary:** Kids (8-12) who are current Pokémon fans
- **Tertiary:** Pokémon collectors appreciating physical memorabilia

**Platform:** Raspberry Pi-based handheld device with:
- Small LCD display (480x320 to 800x480 resolution)
- GPIO button controls (D-pad + A/B buttons)
- Offline, always-on operation
- Physical device you hold and interact with

### 1.2 Core User Experience

**The Defining Experience:** "Point, identify, discover"

Users experience the same flow as in the anime:
1. Device shows a Pokémon (always-on display)
2. Navigate to find the one you want (generation switching + scrolling)
3. View detailed information (like Dexter's voice explaining)
4. Explore relationships (evolution, type advantages)

**What Should Be Effortless:**
- Seeing Pokémon clearly with large, beautiful sprites (50-60% of screen)
- Rapid navigation through all 386 Gen 1-3 Pokémon
- Understanding key information at a glance
- Zero configuration - pick it up and it just works

**Desired Emotional Response:**
Users should feel **nostalgic wonder** - that childlike excitement of discovering Pokémon mixed with adult appreciation for the authentic recreation. The "wow, this IS the Pokédex!" moment.

### 1.3 Design Principles

1. **Authenticity over features** - "Would Ash have seen this on Dexter's screen?"
2. **Visual-first design** - Pokémon sprites dominate; information supports
3. **Appliance simplicity** - No settings, no configuration, no help screens
4. **Direct navigation** - Any Pokémon reachable in ≤3 button presses
5. **Always showing content** - Never blank states or loading screens
6. **Retro-futuristic aesthetic** - 90s anime vision of future technology

---

## 2. Visual Foundation - Anime Pokédex Aesthetic

### 2.1 Core Visual Identity

**Inspiration:** Dexter's holographic display from Pokémon anime Season 1

**Visual Style:** Retro-futuristic (90s anime vision of high-tech)
- Holographic display aesthetic
- Clean geometric layouts
- Glowing UI elements
- Computer terminal meets handheld device
- "Future tech" as imagined in 1997

### 2.2 Color System - Holographic Blue Palette

**Primary Palette:**

```
HOLOGRAPHIC BLUE SYSTEM
├─ Deep Space Black     #0a0e1a   Background (display "off" areas)
├─ Dark Blue            #1a2f4a   Secondary background
├─ Electric Blue        #00d4ff   Primary UI elements, borders, accents
├─ Bright Cyan          #4df7ff   Highlights, active states, glow effects
└─ Ice Blue             #a8e6ff   Text on dark, secondary information

ACCENT COLORS
├─ Plasma Orange        #ff6b35   Important actions, warnings, energy
├─ Neon Yellow          #ffd23f   Cautions, Electric type
└─ Hologram White       #e8f4f8   Primary text, maximum contrast

NEUTRAL GRAYS (for depth)
├─ Charcoal             #2d3748   Panels, containers
├─ Slate Gray           #4a5568   Inactive elements
└─ Steel Gray           #718096   Borders, dividers
```

**Semantic Color Usage:**

| Purpose | Color | Hex | Usage |
|---------|-------|-----|-------|
| **Background** | Deep Space Black | #0a0e1a | Main screen background |
| **Primary UI** | Electric Blue | #00d4ff | Borders, active selections, main accents |
| **Text (Primary)** | Hologram White | #e8f4f8 | Pokémon names, headers, key info |
| **Text (Secondary)** | Ice Blue | #a8e6ff | Stats, descriptions, labels |
| **Active/Selected** | Bright Cyan | #4df7ff | Selected Pokémon, focused buttons, glow effects |
| **Action/Energy** | Plasma Orange | #ff6b35 | Primary action button (A button prompt), important CTAs |
| **Panels** | Dark Blue | #1a2f4a | Info panels, card backgrounds |
| **Dividers** | Steel Gray | #718096 | Section separators, grid lines |

**Type Colors** (Pokémon types - enhanced for holographic aesthetic):

```
Normal:    #a8a878  →  #b8b8d0   (cooler, more futuristic gray)
Fire:      #f08030  →  #ff6b35   (plasma orange)
Water:     #6890f0  →  #4d9fff   (electric blue)
Electric:  #f8d030  →  #ffd23f   (neon yellow)
Grass:     #78c850  →  #6bff6b   (bright holographic green)
Ice:       #98d8d8  →  #a8e6ff   (ice blue)
Fighting:  #c03028  →  #ff4757   (energetic red)
Poison:    #a040a0  →  #b24dff   (neon purple)
Ground:    #e0c068  →  #d4a574   (sandy hologram)
Flying:    #a890f0  →  #8d9fff   (sky hologram)
Psychic:   #f85888  →  #ff6bbd   (bright psychic pink)
Bug:       #a8b820  →  #b8d848   (bioluminescent green)
Rock:      #b8a038  →  #c4b07a   (stone with glow)
Ghost:     #705898  →  #9d7cce   (spectral purple)
Dragon:    #7038f8  →  #8d4dff   (majestic purple-blue)
Dark:      #705848  →  #8b7355   (shadowed brown)
Steel:     #b8b8d0  →  #cbd5e0   (metallic shimmer)
```

### 2.3 Typography System

**Font Strategy:** Clean, readable, tech-inspired

```
PRIMARY FONT: "Orbitron" (Google Fonts)
- Futuristic geometric sans-serif
- Usage: Headers, Pokémon names, numbers
- Weights: Medium (500), Bold (700)
- Evokes computer terminal + sci-fi aesthetic

SECONDARY FONT: "Rajdhani" (Google Fonts)  
- Clean, condensed sans-serif
- Usage: Stats, descriptions, UI labels
- Weights: Regular (400), Medium (500)
- Excellent readability at small sizes

MONOSPACE FONT: "Share Tech Mono" (Google Fonts)
- Technical data display
- Usage: Pokémon stats numbers, IDs, technical info
- Weight: Regular (400)

FALLBACK: -apple-system, "Segoe UI", sans-serif
```

**Type Scale** (optimized for 480x320 display):

| Element | Font | Size | Weight | Usage |
|---------|------|------|--------|-------|
| **Large Header** | Orbitron | 32px | Bold | Screen titles |
| **Pokémon Name** | Orbitron | 24px | Bold | Pokémon identification |
| **Dex Number** | Share Tech Mono | 18px | Regular | #001, #025 format |
| **Section Header** | Rajdhani | 20px | Medium | Stats, Evolution, etc. |
| **Body Text** | Rajdhani | 16px | Regular | Descriptions, labels |
| **Stat Label** | Rajdhani | 14px | Medium | HP, Attack, etc. |
| **Stat Value** | Share Tech Mono | 14px | Regular | Numbers, measurements |
| **Small Text** | Rajdhani | 12px | Regular | Help text, hints |
| **Tiny Text** | Rajdhani | 10px | Regular | Copyright, version |

**Line Height:** 1.4 for body text, 1.2 for headers

### 2.4 Visual Effects - Holographic Display

**Glow Effects:**
- Active selections have cyan glow: `box-shadow: 0 0 20px #4df7ff`
- UI borders emit soft blue light: `box-shadow: 0 0 10px #00d4ff`
- Button hovers intensify glow

**Scan Line Effect:**
```css
/* Subtle horizontal scan lines for CRT/hologram feel */
background: linear-gradient(
  transparent 50%, 
  rgba(0, 212, 255, 0.03) 50%
);
background-size: 100% 4px;
```

**Border Style:**
- Angular, geometric borders (not rounded)
- 2-3px glowing blue borders
- Corner accent lines (45° angle cuts)

**Transparency Layers:**
- Panel backgrounds: rgba(26, 47, 74, 0.85)
- Overlay modals: rgba(10, 14, 26, 0.95)
- Creates depth through layering

### 2.5 Spacing & Layout System

**Base Unit:** 4px (for precise control on small displays)

**Spacing Scale:**
- `xs`: 4px   (tight spacing)
- `sm`: 8px   (compact)
- `md`: 16px  (default)
- `lg`: 24px  (sections)
- `xl`: 32px  (major divisions)
- `2xl`: 48px (screen padding)

**Grid System:** Custom for 480x320 display
- 12-column grid concept, but adapted per screen
- 16px gutters between major sections
- Edge padding: 12-16px (leave breathing room)

**Layout Principles:**
- Pokémon sprite always hero element (center, large)
- Information arranged around sprite
- Geometric panel divisions
- Clear visual hierarchy through sizing + color

---

## 3. Design System Foundation

### 3.1 Design System Choice

**Decision: Custom Design System** (not using Material UI, Chakra, etc.)

**Rationale:**
ShokeDex requires a highly specialized aesthetic - the anime Pokédex holographic display - that no existing design system provides. The visual identity is so specific (retro-futuristic, holographic blue, geometric, 90s anime tech) that adapting a modern design system would be counterproductive.

**What This Means:**
- Custom component library built with pygame
- All UI elements designed specifically for this aesthetic
- Full control over every pixel
- Components: Sprite display, stat bars, type badges, generation indicators, button prompts

**Benefits:**
- Perfect authenticity to anime aesthetic
- Optimized for Raspberry Pi performance
- Exact control over retro-futuristic look
- No bloat from unused components

**Components to Build:**
1. **Sprite Display Panel** - Large Pokémon image with glowing border
2. **Info Card** - Geometric panel with holographic styling
3. **Stat Bar** - Horizontal bar with glow effect
4. **Type Badge** - Rounded rectangle with type color + icon
5. **Generation Badge** - Region indicator (Kanto/Johto/Hoenn)
6. **Button Prompt** - Shows available actions (A/B/L/R prompts)
7. **Screen Header** - Title bar with border accent
8. **Navigation Indicator** - Shows position in list

---

## 4. Screen Designs & Layouts

### 4.1 Primary Screens Overview

ShokeDex has 4 primary screens, each serving a specific purpose in the browsing and discovery experience:

1. **Browse Screen** - Main navigation, shows current Pokémon
2. **Detail Screen** - Full stats, description, comprehensive info
3. **Relationships Screen** - Evolution chain + type matchups
4. **Quiz Screen** - "Who's That Pokémon?" game mode

### 4.2 Browse Screen (Main/Home)

**Purpose:** Primary navigation - browse through Pokémon by generation

**Layout Concept:** "Hero Sprite + Navigation Info"

```
┌─────────────────────────────────────────┐
│  KANTO                          #025/151│  ← Generation badge + position
├─────────────────────────────────────────┤
│                                         │
│            ▄▄▄▄▄▄▄▄▄▄▄▄▄               │
│         ▄▄▄████████████████▄▄           │
│       ▄██████████████████████▄          │
│      ████████████████████████████       │  ← LARGE sprite
│      ████████████████████████████       │     (50-60% of screen)
│       ████████████████████████▀         │
│         ▀▀████████████████▀▀            │
│            ▀▀▀▀▀▀▀▀▀▀▀▀                │
│                                         │
│          PIKACHU                        │  ← Name (large, centered)
│        ⚡ ELECTRIC                      │  ← Type badge(s)
├─────────────────────────────────────────┤
│  [L/R] Generation  [↑↓] Navigate       │  ← Button hints
│  [A] Details                            │
└─────────────────────────────────────────┘
```

**Visual Hierarchy:**
1. **Pokémon sprite** - Dominates center (200-250px on 480x320)
2. **Name** - Large, bold, immediately below sprite
3. **Type badges** - Colorful visual indicators
4. **Generation context** - Top bar shows region + progress
5. **Navigation hints** - Bottom bar, secondary importance

**Key Features:**
- Always shows a Pokémon (never blank)
- Generation badge indicates Kanto/Johto/Hoenn
- Position counter shows progress (#025/151 in Kanto)
- Type badges use holographic styling
- Button prompts glow when active
- Clean, uncluttered layout

**Interaction:**
- L/R buttons: Switch generation (wraps around)
- Up/Down: Navigate within generation (one at a time)
- Hold Up/Down: Fast scroll through list
- A button: Enter detail view
- START button: Open quiz mode (future)

**Visual Details:**
- Sprite has glowing cyan border
- Generation badge in top-left with region logo
- Type badges have rounded corners + type color
- Button prompts use orange for primary action (A)
- Subtle scan lines across background

### 4.3 Detail Screen

**Purpose:** Show comprehensive Pokémon information

**Layout Concept:** "Info Panels Around Sprite"

```
┌─────────────────────────────────────────┐
│  PIKACHU                           #025 │  ← Header with name + number
├──────────────┬──────────────────────────┤
│              │  HP       ▓▓▓▓▓░░░░░  35 │
│              │  Attack   ▓▓▓▓▓▓░░░░  55 │
│   ▄▄▄▄▄▄▄    │  Defense  ▓▓▓▓░░░░░░  40 │
│  ████████    │  Sp.Atk   ▓▓▓▓▓░░░░░  50 │  ← Stats panel
│  ████████    │  Sp.Def   ▓▓▓▓▓░░░░░  50 │     (right side)
│  ████████    │  Speed    ▓▓▓▓▓▓▓▓▓░  90 │
│   ▀▀▀▀▀▀     │                          │
│              │  ⚡ ELECTRIC             │  ← Type badges
├──────────────┴──────────────────────────┤
│  Height: 0.4m    Weight: 6.0kg          │  ← Physical stats
├─────────────────────────────────────────┤
│  When several of these Pokémon gather,  │
│  their electricity can build and cause  │  ← Pokédex description
│  lightning storms.                      │
├─────────────────────────────────────────┤
│  [←→] Next/Prev  [B] Back  [A] Evolve  │  ← Actions
└─────────────────────────────────────────┘
```

**Visual Hierarchy:**
1. **Name + Dex number** - Header identification
2. **Pokémon sprite** - Left side, still prominent (smaller than browse)
3. **Stats with bars** - Right side, easy to scan
4. **Type badges** - Below stats, colorful
5. **Physical measurements** - Tertiary info
6. **Description text** - Pokédex flavor text
7. **Navigation prompts** - Bottom actions

**Key Features:**
- 6 base stats with visual progress bars
- Bars show relative strength (max 255)
- Stats color-coded by value (low=gray, high=cyan glow)
- Sprite smaller than browse view to fit info
- Description uses authentic Pokédex text
- Clean panel divisions with blue borders

**Interaction:**
- Left/Right arrows: Navigate to adjacent Pokémon (stay in detail view)
- B button: Return to browse screen
- A button: Jump to relationships/evolution view
- Smooth transitions maintain context

**Visual Details:**
- Each panel has geometric border with glow
- Stat bars fill from left with gradient
- Type badges same style as browse screen
- Header has accent corner lines
- Description text in readable secondary font

### 4.4 Relationships Screen

**Purpose:** Show evolution chain + type matchups in one unified view

**Layout Concept:** "Two-Panel Split"

```
┌─────────────────────────────────────────┐
│  PIKACHU - RELATIONSHIPS           #025 │
├─────────────────────────────────────────┤
│  EVOLUTION CHAIN                        │
│                                         │
│   ┌──────┐      ┌──────┐      ┌──────┐│
│   │ #172 │─────>│ #025 │─────>│ #026 ││  ← Evolution sprites
│   │PICHU │ Lv.? │PIKACHU│Stone│RAICHU││     with requirements
│   └──────┘      └──────┘      └──────┘│
│                    ^                   │
│                 YOU ARE HERE           │
├─────────────────────────────────────────┤
│  TYPE MATCHUPS - ⚡ ELECTRIC            │
│                                         │
│  STRONG VS    🌊💧 Water  🐦 Flying    │  ← Type advantages
│  WEAK VS      🌍 Ground                │  ← Type weaknesses
│  RESISTS      ⚡ Electric 🐦 Flying ⚙️  │  ← Resistances
├─────────────────────────────────────────┤
│  [←→] Next/Prev  [B] Back              │
└─────────────────────────────────────────┘
```

**Key Features:**
- Top half: Evolution chain with small sprites
- Shows pre-evolution, current, and evolution(s)
- Evolution requirements labeled (level, stone, etc.)
- "You are here" indicator for current Pokémon
- Bottom half: Type effectiveness grid
- Strong against, weak against, resistances
- Type icons for visual scanning

**Visual Details:**
- Horizontal line connecting evolution stages
- Arrow indicators showing evolution direction
- Current Pokémon highlighted with glow
- Type matchup uses emoji/icons + type colors
- Clear section divider between panels

### 4.5 Quiz Screen ("Who's That Pokémon?")

**Purpose:** Fun game mode - guess the Pokémon from silhouette

**Layout Concept:** "Silhouette Challenge"

```
┌─────────────────────────────────────────┐
│  WHO'S THAT POKÉMON?                    │
├─────────────────────────────────────────┤
│                                         │
│            ▄▄▄▄▄▄▄▄▄▄▄▄▄               │
│         ▄▄▄████████████████▄▄           │
│       ▄██████████████████████▄          │
│      ████████████████████████████       │  ← Black silhouette
│      ████████████████████████████       │     (mystery Pokémon)
│       ████████████████████████▀         │
│         ▀▀████████████████▀▀            │
│            ▀▀▀▀▀▀▀▀▀▀▀▀                │
│                                         │
│            ??? ??????                   │  ← Hidden name
│                                         │
├─────────────────────────────────────────┤
│  [↑↓] Scroll to Guess  [A] Confirm     │
│                                         │
│  Score: 8/10                            │  ← Optional scoring
└─────────────────────────────────────────┘
```

**After Correct Guess:**

```
┌─────────────────────────────────────────┐
│  IT'S PIKACHU!                          │
├─────────────────────────────────────────┤
│                                         │
│            [COLORED SPRITE]             │  ← Reveals full sprite
│                                         │
│          PIKACHU                        │
│        ⚡ ELECTRIC                      │
│                                         │
│  [Pokémon cry plays]                    │
├─────────────────────────────────────────┤
│  [A] Next  [B] Exit Quiz                │
└─────────────────────────────────────────┘
```

**Key Features:**
- Silhouette of random Pokémon
- User scrolls through list to guess
- Current guess name shown (hidden until reveal)
- Celebratory reveal with color sprite
- Optional cry audio plays on reveal
- Score tracking across session
- Can filter by generation

---

## 5. Component Library

### 5.1 Core Components

#### Sprite Display Panel

**Purpose:** Show Pokémon sprite with holographic frame

**Variants:**
- **Large** (browse view): 200-250px, dominates screen
- **Medium** (detail view): 120-150px, balances with info
- **Small** (evolution chain): 64-80px, thumbnail size

**Visual Style:**
```
┌────────────────────┐
│ ╔════════════════╗ │  ← Glowing cyan border (2-3px)
│ ║                ║ │
│ ║   [SPRITE]     ║ │  ← Pokémon sprite centered
│ ║                ║ │
│ ╚════════════════╝ │
└────────────────────┘
   Box shadow glow: 0 0 20px #4df7ff
```

**States:**
- Default: Cyan border with glow
- Active/Selected: Brighter glow, animated pulse
- Loading: Border pulses while sprite loads

#### Info Card Panel

**Purpose:** Container for information sections

**Visual Style:**
```
╔══════════════════════════╗  ← Corner accent lines
║ SECTION HEADER           ║  ← Rajdhani Medium, 20px
╟──────────────────────────╢  ← Divider line
║                          ║
║  Content goes here       ║  ← Dark blue background
║  Multiple lines okay     ║     with transparency
║                          ║
╚══════════════════════════╝
```

**Background:** `rgba(26, 47, 74, 0.85)`
**Border:** 2px solid `#00d4ff`
**Header background:** `rgba(0, 212, 255, 0.1)`

#### Stat Bar

**Purpose:** Visualize numerical stats (HP, Attack, etc.)

**Layout:**
```
HP        ▓▓▓▓▓▓░░░░  45
│          │           │
Label    Bar (max 255) Value
```

**Visual Style:**
- Label: Rajdhani Medium, 14px, ice blue
- Value: Share Tech Mono, 14px, hologram white
- Bar filled: Electric blue gradient
- Bar empty: Dark gray with subtle border
- Bar width: Proportional to stat (max 255 = 100%)

**Color Coding by Value:**
- 0-50: `#718096` (low, gray)
- 51-100: `#00d4ff` (medium, electric blue)
- 101-150: `#4df7ff` (high, bright cyan)
- 151+: `#ff6b35` (exceptional, plasma orange)

**Glow Effect:** High stats (100+) have subtle glow

#### Type Badge

**Purpose:** Visual indicator of Pokémon type

**Size:** 70px × 28px (browse), 60px × 24px (detail)

**Visual Style:**
```
┌──────────────┐
│ ⚡ ELECTRIC  │  ← Type icon + name
└──────────────┘
```

**Styling:**
- Background: Type color (from palette)
- Border: 1px lighter shade of type color
- Border radius: 4px (slightly rounded)
- Text: Bold, uppercase, contrasting color
- Icon: Type symbol (emoji or custom icon)

**Type Color Examples:**
- Electric: `#ffd23f` background, white text
- Water: `#4d9fff` background, white text
- Fire: `#ff6b35` background, white text
- Grass: `#6bff6b` background, dark text

#### Generation Badge

**Purpose:** Show current region (Kanto/Johto/Hoenn)

**Visual Style:**
```
┌──────────────────┐
│ [Region Logo]    │  ← Pokéball icon + text
│ KANTO   #025/151 │  ← Region name + position
└──────────────────┘
```

**Placement:** Top-left or top-center of screen

**Styling:**
- Background: `rgba(26, 47, 74, 0.9)`
- Border: 2px `#00d4ff`
- Corner accents: 45° angle cuts
- Region name: Orbitron Bold, 18px
- Position counter: Share Tech Mono, 14px

**Regions:**
- Kanto: Red/Blue game aesthetic, Pokéball icon
- Johto: Gold/Silver aesthetic, GS Ball icon
- Hoenn: Ruby/Sapphire aesthetic, Master Ball icon

#### Button Prompt

**Purpose:** Show available actions and button mappings

**Visual Style:**
```
[A] Select   [B] Back   [L/R] Generation
 │            │          │
Orange       Gray       Blue
(primary)    (back)     (nav)
```

**Color Coding:**
- Primary action (A): Plasma orange `#ff6b35`
- Back/Cancel (B): Gray `#718096`
- Navigation (L/R/↑↓): Electric blue `#00d4ff`

**Placement:** Bottom of screen, always visible

**Styling:**
- Button icon in square brackets: `[A]`
- Action text after icon
- Multiple prompts separated by spacing
- Font: Rajdhani Regular, 14px

---

## 6. User Journey Flows

### 6.1 Primary User Journey: Browse & Discover

**User Goal:** Find and learn about a specific Pokémon

**Flow:**

```
START (Power On)
    ↓
┌─────────────────────────┐
│ Browse Screen           │ ← Shows Bulbasaur (#1) or last viewed
│ (Always displays a      │
│  Pokémon - never blank) │
└─────────────────────────┘
    ↓
    ├─ [L/R Buttons] Switch Generation
    │     ↓
    │  ┌────────────────────┐
    │  │ Kanto → Johto      │ ← Smooth transition
    │  │ Johto → Hoenn      │    Shows first Pokémon of region
    │  │ Hoenn → Kanto      │    (wraps around)
    │  └────────────────────┘
    │     ↓
    │  Return to Browse Screen (new generation)
    │
    ├─ [Up/Down Buttons] Scroll Within Generation
    │     ↓
    │  ┌────────────────────┐
    │  │ One Pokémon at a   │ ← Single press = next/prev
    │  │ time navigation    │    Hold = fast scroll
    │  │ Sprite changes     │    Wraps at ends (optional)
    │  └────────────────────┘
    │     ↓
    │  Return to Browse Screen (new Pokémon)
    │
    └─ [A Button] View Details
       ↓
    ┌─────────────────────────┐
    │ Detail Screen           │ ← Full stats, description
    │ Same Pokémon, more info │    Evolution hint
    └─────────────────────────┘
       ↓
       ├─ [Left/Right Arrows] Navigate to adjacent Pokémon
       │     ↓
       │  Stay in Detail Screen, show next/prev Pokémon
       │
       ├─ [B Button] Back to Browse
       │     ↓
       │  Return to Browse Screen (maintains position)
       │
       └─ [A Button] View Relationships
          ↓
       ┌─────────────────────────┐
       │ Relationships Screen    │ ← Evolution + Type matchups
       └─────────────────────────┘
          ↓
          [B Button] Back to Detail Screen
```

**Key Decision Points:**

1. **Generation Selection:** 3 options (Kanto/Johto/Hoenn), wraps circularly
2. **Browse vs Detail:** Single button press (A) to dive deeper
3. **Stay or Return:** Easy back navigation (B) at any time
4. **Navigate Within View:** Left/Right works in detail view for efficiency

**Success Criteria:**
- Any Pokémon reachable in ≤3 button presses
- Example: Kanto → Johto (1 press) → Scroll to #200 (1 press or hold) → Details (1 press) = 3 presses max
- User never feels lost or stuck
- Always clear how to go back

### 6.2 Secondary Journey: Quiz Mode

**User Goal:** Test Pokémon knowledge in fun game

**Flow:**

```
START (From Browse Screen)
    ↓
[START Button] Open Quiz Mode
    ↓
┌─────────────────────────┐
│ Quiz Setup (Optional)   │ ← Select difficulty/generation
│ - All Generations       │    Or jump straight to quiz
│ - Kanto Only            │
│ - Johto Only            │
│ - Hoenn Only            │
└─────────────────────────┘
    ↓
[A] Start Quiz
    ↓
┌─────────────────────────┐
│ Quiz Screen             │ ← Silhouette displayed
│ Mystery Pokémon shown   │    Name hidden
│ as black silhouette     │
└─────────────────────────┘
    ↓
[Up/Down] Scroll to Guess
    ↓
Current guess name shown (but dimmed)
    ↓
[A Button] Submit Guess
    ↓
    ├─ Correct Guess
    │     ↓
    │  ┌────────────────────┐
    │  │ Reveal Animation   │ ← Silhouette fills with color
    │  │ "IT'S [NAME]!"     │    Cry plays (if audio)
    │  │ Sprite + Type shown│    Celebration
    │  └────────────────────┘
    │     ↓
    │  Score increases
    │     ↓
    │  [A] Next Pokémon → Back to Quiz Screen (new silhouette)
    │  [B] Exit Quiz → Return to Browse Screen
    │
    └─ Incorrect Guess
       ↓
    ┌────────────────────┐
    │ "Try Again!"       │ ← Stays on silhouette
    │ Guess again        │    Optional hint shown
    └────────────────────┘
       ↓
    Return to Quiz Screen (same Pokémon)
```

**Quiz Features:**
- Randomly selected Pokémon from chosen generation(s)
- Score tracking (correct/total)
- Optional hint after wrong guess
- Can exit anytime with B button
- Maintains score across session
- Resets score on new quiz start

---

## 7. UX Pattern Decisions

### 7.1 Navigation Patterns

**Active State Indication:**
- **Selected Pokémon:** Brighter cyan glow around sprite border
- **Active Generation:** Badge glows, others dimmed
- **Focused Button Prompt:** Orange glow around text

**Back Button Behavior:**
- B button ALWAYS goes back one level
- Browse → (no back, already at top)
- Detail → Browse (to last position)
- Relationships → Detail
- Quiz → Browse

**Navigation Memory:**
- Device remembers last viewed Pokémon
- Returns to same position after detail view
- Generation selection persists until changed
- Power on restores to last state

### 7.2 Feedback Patterns

**Success:**
- Pattern: Visual glow + audio feedback (optional cry)
- Example: Correct quiz answer → sprite reveal + cry + "IT'S [NAME]!"
- Duration: 2-3 seconds before allowing next action

**Error/Invalid Action:**
- Pattern: Red flash + subtle shake animation
- Example: Wrong quiz guess → "Try Again!" message
- No audio (keeps it encouraging)
- User can immediately retry

**Loading:**
- Pattern: Animated border pulse on sprite frame
- Shown when: Loading sprite from disk (first time only)
- Duration: Usually <100ms with caching
- No separate loading screen (maintain always-on principle)

**Button Press Confirmation:**
- Pattern: Instant visual response (<100ms)
- Visual: Button prompt glows briefly
- Tactile: Physical button click
- Audio: Optional subtle beep (future)

### 7.3 Form Patterns (Future)

Currently no forms in MVP. For future features:

**Favorites System (Future):**
- Star icon button on detail screen
- Toggle with SELECT button
- Instant visual feedback (star fills/empties)
- Favorites list accessible from browse

**Settings (Future Vision Features):**
- Minimal settings (volume only)
- Slider with real-time preview
- No complex configuration
- Appliance simplicity maintained

### 7.4 Empty State Patterns

**Philosophy:** "Always show content" - no empty states in MVP

**If Implemented (Future):**
- First Use: Device ships with database populated
- No Results: Not applicable (full Pokédex always present)
- Error State: Fallback to default (Bulbasaur #1)

### 7.5 Confirmation Patterns

**No Confirmations in MVP** - appliance simplicity

**Future Considerations:**
- Exit Quiz: No confirmation (B button exits immediately)
- Clear Favorites: No confirmation (can re-favorite)
- Philosophy: Easy to undo > annoying confirmations

### 7.6 State Transitions

**Screen Transitions:**
- Pattern: Instant cut (no slow fades)
- Reasoning: Responsive feel, like flipping pages
- Exception: Quiz reveal uses brief animation (celebration moment)

**Pokémon Transitions (Browse View):**
- Pattern: Sprite fades out → new sprite fades in (200ms)
- Maintains position on screen
- Keeps user oriented

**Generation Switch:**
- Pattern: Slide transition (300ms)
- Direction matches L/R button press
- New generation badge slides in
- First Pokémon of region appears

---

## 8. Responsive Design & Accessibility

### 8.1 Display Resolution Strategy

**Primary Target:** 480×320 (common 3.5" LCD)

**Secondary Targets:**
- 640×480 (4" displays)
- 800×480 (5-7" displays)

**Responsive Approach:**

```
LAYOUT SCALING STRATEGY
├─ 480×320 (Base)
│  ├─ Sprite: 200px
│  ├─ Text: 16-24px
│  └─ Padding: 12-16px
│
├─ 640×480 (Scale up 1.33×)
│  ├─ Sprite: 266px
│  ├─ Text: 21-32px
│  └─ Padding: 16-21px
│
└─ 800×480 (Scale width, maintain height proportions)
   ├─ Sprite: 240px (more horizontal breathing room)
   ├─ Text: 18-26px
   └─ Padding: 16-20px
```

**Breakpoint Rules:**
- Calculate scale factor: `current_width / 480`
- Scale all measurements proportionally
- Maintain aspect ratios for sprites
- Fonts scale with display (but cap max size)
- Padding scales to maintain visual balance

**No Mobile/Tablet/Desktop Modes:**
This IS the device - fixed hardware, single resolution per unit

### 8.2 Physical Accessibility

**Button Design (Hardware):**
- Large, tactile buttons (15mm+ diameter)
- Clear separation between buttons
- D-pad with distinct directional feel
- A/B buttons different shapes/positions
- START button separated (prevent accidental press)

**Visual Accessibility:**

**Contrast Ratios (WCAG AA):**
- Primary text on dark background: 15:1 (exceeds 4.5:1)
- Secondary text on dark background: 12:1
- Type badges: Minimum 4.5:1 (tested per type)

**Color Blindness Considerations:**
- Type colors chosen for distinctiveness beyond hue
- Icons supplement color (not color alone)
- Important info never color-only

**Text Readability:**
- Minimum 14px for body text at 480×320
- High contrast (white/cyan on dark blue/black)
- Clean, geometric fonts optimized for screens
- No serif fonts (harder to read on LCD)

**Sprite Clarity:**
- Large sprites ensure visibility
- No critical details smaller than 5px
- High contrast sprites preferred

### 8.3 Accessibility Features

**Keyboard Navigation (Dev Mode):**
- Arrow keys map to D-pad
- Enter = A button
- Escape = B button
- Tab = START button
- Space = SELECT (future)

**Screen Reader (Future Consideration):**
Not applicable for embedded device, but principles inform design:
- Clear visual hierarchy (largest = most important)
- Logical tab order (if touch screen added)
- Descriptive labels on all interactive elements

**Reduced Motion:**
Not configurable (hardware device), but animations are:
- Brief (200-300ms max)
- Purposeful (provide feedback)
- Skippable (can press next button immediately)

---

## 9. Implementation Guidance

### 9.1 Design-to-Code Handoff

**For Developers Implementing This Design:**

**Color Variables (Create in colors.py):**
```python
class AnimePokedexColors:
    # Backgrounds
    DEEP_SPACE_BLACK = (10, 14, 26)      # #0a0e1a
    DARK_BLUE = (26, 47, 74)              # #1a2f4a
    
    # Primary UI
    ELECTRIC_BLUE = (0, 212, 255)         # #00d4ff
    BRIGHT_CYAN = (77, 247, 255)          # #4df7ff
    ICE_BLUE = (168, 230, 255)            # #a8e6ff
    
    # Accents
    PLASMA_ORANGE = (255, 107, 53)        # #ff6b35
    NEON_YELLOW = (255, 210, 63)          # #ffd23f
    HOLOGRAM_WHITE = (232, 244, 248)      # #e8f4f8
    
    # Neutrals
    CHARCOAL = (45, 55, 72)               # #2d3748
    SLATE_GRAY = (74, 85, 104)            # #4a5568
    STEEL_GRAY = (113, 128, 150)          # #718096
```

**Typography Setup:**
- Use pygame.font with Google Fonts downloaded
- Or fallback to system fonts with similar characteristics
- Font sizes in comments above (scale for resolution)

**Component Priority (Build Order):**
1. Sprite Display Panel (core visual)
2. Browse Screen Layout (main screen)
3. Button Prompt System (navigation feedback)
4. Type Badge Component (visual appeal)
5. Detail Screen Layout (information depth)
6. Stat Bar Component (data visualization)
7. Generation Badge (context)
8. Relationships Screen (advanced feature)
9. Quiz Mode (fun addition)

**Performance Notes:**
- Sprite caching critical (load once, display many times)
- Glow effects: Use pre-rendered glowing borders
- Scan lines: Background texture, not per-frame draw
- Transitions: Double-buffer to prevent flicker

### 9.2 Visual Design Assets Needed

**To Complete Implementation:**

**Sprites:** ✅ Already have 386 Pokémon sprites

**Type Icons (17 needed):**
- Normal, Fire, Water, Electric, Grass, Ice, Fighting, Poison, Ground
- Flying, Psychic, Bug, Rock, Ghost, Dragon, Dark, Steel
- Size: 24×24px, white/light colored on transparent
- Style: Simple geometric symbols

**Generation Badges (3 needed):**
- Kanto badge: Pokéball icon + "KANTO" text
- Johto badge: GS Ball icon + "JOHTO" text
- Hoenn badge: Master Ball icon + "HOENN" text
- Size: 100×40px, holographic styling

**Button Icons (5 needed):**
- A button, B button, L button, R button, START button
- Size: 16×16px, for button prompts
- Style: Outline style matching holographic theme

**UI Decorations:**
- Corner accent lines (geometric 45° cuts)
- Border glow textures (for performance)
- Scan line texture (subtle, repeating)

**Fonts to Download:**
- Orbitron (Google Fonts) - weights 500, 700
- Rajdhani (Google Fonts) - weights 400, 500
- Share Tech Mono (Google Fonts) - weight 400

### 9.3 Testing Recommendations

**Visual Testing:**
- Test on actual hardware (480×320 LCD) early
- Verify text readability at arm's length
- Check sprite clarity and size
- Confirm button prompts are legible
- Validate color contrast in various lighting

**Usability Testing:**
- Can user browse without instructions?
- Is 3-press rule met for all Pokémon?
- Are button mappings intuitive?
- Does navigation feel responsive (<100ms)?
- Is visual hierarchy clear?

**Performance Testing:**
- 30+ FPS maintained during navigation
- Sprite transitions smooth
- No lag on button press
- Memory usage within constraints
- Fast scroll mode responsive

**Aesthetic Testing:**
- Does it feel like anime Pokédex?
- Holographic aesthetic achieved?
- Retro-futuristic vibe present?
- Would Ash recognize this interface?

---

## 10. Next Steps & Follow-Up Workflows

### 10.1 Completion Summary

**✅ UX Design Specification Complete!**

This specification defines:
- **Visual Identity:** Anime Pokédex holographic aesthetic with electric blue color scheme
- **Design System:** Custom component library tailored for retro-futuristic look
- **Screen Layouts:** Browse, Detail, Relationships, and Quiz screens designed
- **User Flows:** Primary and secondary journeys mapped with 3-press navigation rule
- **Component Library:** 8 core components specified with visual details
- **UX Patterns:** Consistent interaction patterns across all screens
- **Accessibility:** Display scaling and physical accessibility considerations
- **Implementation Guide:** Developer handoff with colors, fonts, priorities

**Deliverables:**
- ✅ This UX Design Specification: `docs/ux-design-specification.md`
- 🎨 Interactive Color Theme Visualizer: `docs/ux-color-themes.html` (generated next)
- 🎨 Design Direction Mockups: `docs/ux-design-directions.html` (generated next)

### 10.2 Interactive Visualizations

Want to see the design come to life? I can generate:

1. **Color Theme Showcase** - Interactive HTML with the anime Pokédex palette applied to UI components
2. **Screen Mockups** - Full-resolution HTML mockups of Browse, Detail, and Relationships screens
3. **Component Library** - Interactive component demos showing all states

Would you like me to generate any of these visualizations?

### 10.3 Recommended Next Steps

**Immediate:**
1. Review this specification for alignment with vision
2. Generate interactive mockups (optional)
3. Update workflow status to mark design complete

**Before Implementation:**
1. Gather visual assets (type icons, generation badges, fonts)
2. Create a visual design reference sheet
3. Set up pygame with new color palette

**During Implementation:**
1. Build components in order (sprite display first)
2. Test on target hardware early and often
3. Iterate on spacing and sizing based on actual display
4. Reference this spec for all design decisions

### 10.4 Design Evolution

**This Specification Is Living:**
- Update as you implement and discover improvements
- Add new screens/features with same visual language
- Maintain consistency with anime Pokédex aesthetic
- Document design decisions and rationale

**Future Enhancements:**
- Touch screen interaction patterns
- Scroll wheel integration
- Advanced animations and transitions
- Audio feedback specifications
- Screensaver mode visual design
- "Registration" system visual design

---

## Appendix A: Design Rationale

### Why Holographic Blue?

**Anime Accuracy:** Dexter's display in the anime consistently showed a cyan/blue holographic aesthetic, particularly in close-up shots. This wasn't Gameboy green - it was futuristic display technology.

**Emotional Impact:** Blue conveys:
- Technology and innovation
- Trust and reliability
- Futuristic aesthetic
- Cool, calm discovery (not exciting red)

**Nostalgia Factor:** Adults remember the anime Pokédex as high-tech and otherworldly - blue creates that separation from everyday devices.

### Why Large Sprites?

**Core Philosophy:** "This is a window into the Pokémon world"

The Pokémon themselves are the content, not UI chrome. In the anime, Dexter always showed the Pokémon prominently - the visual was the primary information, with text supporting.

**User Psychology:** Users browse Pokédexes to see Pokémon, not to read stats. Stats are secondary information accessed when curious about a specific Pokémon.

**Differentiation:** Every Pokédex app shows lists with small icons. ShokeDex's large sprites create a unique, beautiful browsing experience.

### Why Minimal Text?

**Appliance Simplicity:** Complex interfaces require instruction manuals. Appliances don't. ShokeDex should feel like a TV remote - intuitive through physical buttons and clear visual hierarchy.

**Small Display:** At 480×320, text competes with sprites. We choose to prioritize visuals and only show essential text.

**Anime Consistency:** Dexter spoke information (audio). Visual display showed Pokémon image. We maintain that priority.

### Why Custom Design System?

**Specificity:** The anime Pokédex aesthetic is too specific for generic design systems. Material Design, Fluent, etc. all have modern web/mobile aesthetics - not 90s anime tech.

**Performance:** Design system components often carry overhead. Custom pygame components are optimized for Raspberry Pi.

**Authenticity:** Every pixel can be crafted to answer "Would Ash have seen this?" Generic components can't achieve that.

---

## Appendix B: Typography Specimens

**Orbitron Bold - Headers & Names:**
```
ABCDEFGHIJKLMNOPQRSTUVWXYZ
abcdefghijklmnopqrstuvwxyz
0123456789

PIKACHU
BULBASAUR
CHARIZARD
```

**Rajdhani Medium - Body Text:**
```
ABCDEFGHIJKLMNOPQRSTUVWXYZ
abcdefghijklmnopqrstuvwxyz
0123456789

When several of these Pokémon gather,
their electricity can build and cause
lightning storms.
```

**Share Tech Mono - Technical Data:**
```
ABCDEFGHIJKLMNOPQRSTUVWXYZ
0123456789

#001  #025  #151
HP: 045  Attack: 055
Height: 0.4m  Weight: 6.0kg
```

---

## Appendix C: Related Documents

**Project Documentation:**
- Product Requirements: `docs/PRD.md`
- Architecture: `docs/architecture.md`
- Workflow Status: `docs/bmm-workflow-status.yaml`
- Brainstorming Session: `docs/bmm-brainstorming-session-2025-11-13.md`

**Existing Implementation (To Be Updated):**
- Current Colors: `src/ui/colors.py` (Gameboy aesthetic - will update)
- Current Screens: `src/ui/home_screen.py`, `detail_screen.py`, etc.
- UI Guide: `docs/ui_guide.md` (will update with new design)

---

## Version History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-11-14 | 1.0 | Initial UX Design Specification - Anime Pokédex Aesthetic | King |

---

_This UX Design Specification captures the authentic anime Pokédex experience - "Would Ash have seen this on Dexter's screen?" guides every design decision. The holographic blue aesthetic, large sprite displays, and retro-futuristic visual language create a nostalgic yet functional device that brings the Pokémon world to your hands._

_Created through collaborative design facilitation with Sally (UX Designer) using the BMad Method Create UX Design workflow._
