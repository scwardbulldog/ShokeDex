# 3-Press Navigation Validation Checklist (Story 1.7)

**Requirement:** Any Pokémon shall be reachable within 3 button presses from any screen (FR2.4)

**Definition:** "Press" includes hold-to-scroll as a single action regardless of distance traveled.

---

## Test Environment

**Test Date:** ____________  
**Tester:** ____________  
**Device:** ☐ Desktop    ☐ Raspberry Pi 3B+  
**Input Mode:** ☐ Keyboard    ☐ GPIO Buttons  
**Software Version:** ____________

---

## Cross-Generation Navigation (AC #3)

Tests navigation between different generations (Kanto ↔ Johto ↔ Hoenn).

| Test ID | Start Pokemon | End Pokemon | Expected Path | Actual Presses | Pass/Fail | Notes |
|---------|--------------|-------------|---------------|----------------|-----------|-------|
| CG-1    | #001 Bulbasaur (Kanto) | #152 Chikorita (Johto) | R (1) | ___ | ☐ | First in Johto |
| CG-2    | #001 Bulbasaur (Kanto) | #252 Treecko (Hoenn) | R→R (2) | ___ | ☐ | First in Hoenn |
| CG-3    | #025 Pikachu (Kanto) | #252 Treecko (Hoenn) | R→R (2) | ___ | ☐ | Mid-Kanto to Hoenn |
| CG-4    | #025 Pikachu (Kanto) | #386 Deoxys (Hoenn) | R→R→Hold Down (3) | ___ | ☐ | Last in Hoenn |
| CG-5    | #151 Mew (Kanto) | #152 Chikorita (Johto) | R (1) | ___ | ☐ | Last Kanto → First Johto |
| CG-6    | #200 Misdreavus (Johto) | #050 Diglett (Kanto) | L→Hold Down (2) | ___ | ☐ | Mid-Johto back to Kanto |
| CG-7    | #251 Celebi (Johto) | #252 Treecko (Hoenn) | R (1) | ___ | ☐ | Last Johto → First Hoenn |
| CG-8    | #300 Skitty (Hoenn) | #001 Bulbasaur (Kanto) | L→L (2) | ___ | ☐ | Mid-Hoenn → First Kanto |
| CG-9    | #386 Deoxys (Hoenn) | #152 Chikorita (Johto) | L (1) | ___ | ☐ | Last Hoenn → First Johto |
| CG-10   | #200 Misdreavus (Johto) | #300 Skitty (Hoenn) | R→Hold Down (2) | ___ | ☐ | Mid gen to mid gen |

**Cross-Generation Summary:**
- Total paths tested: ___/10
- Paths ≤ 3 presses: ___
- Paths > 3 presses: ___ (should be 0)

---

## Within-Generation Navigation - Kanto (AC #4)

Tests scrolling within Generation 1 (151 Pokémon).

| Test ID | Start Pokemon | End Pokemon | Expected Path | Actual Presses | Pass/Fail | Notes |
|---------|--------------|-------------|---------------|----------------|-----------|-------|
| WG-K1   | #001 Bulbasaur | #002 Ivysaur | Down (1) | ___ | ☐ | Adjacent next |
| WG-K2   | #025 Pikachu | #026 Raichu | Down (1) | ___ | ☐ | Mid-gen adjacent |
| WG-K3   | #001 Bulbasaur | #151 Mew | Up (wrap) (1) | ___ | ☐ | Wrap to end |
| WG-K4   | #151 Mew | #001 Bulbasaur | Down (wrap) (1) | ___ | ☐ | Wrap to start |
| WG-K5   | #001 Bulbasaur | #050 Diglett | Hold Down (1) | ___ | ☐ | Fast scroll forward |
| WG-K6   | #050 Diglett | #001 Bulbasaur | Hold Up (1) | ___ | ☐ | Fast scroll backward |
| WG-K7   | #025 Pikachu | #075 Graveler | Hold Down (1) | ___ | ☐ | Mid to mid distant |
| WG-K8   | #001 Bulbasaur | #012 Butterfree | Hold Down (1) | ___ | ☐ | Within 12 range |
| WG-K9   | #100 Voltorb | #001 Bulbasaur | Hold Up (1) | ___ | ☐ | Large backward scroll |
| WG-K10  | #076 Golem | #151 Mew | Hold Down (1) | ___ | ☐ | Mid to last |

**Kanto Summary:**
- Total paths tested: ___/10
- Paths ≤ 3 presses: ___
- Hold-to-scroll works efficiently: ☐ Yes  ☐ No

---

## Within-Generation Navigation - Johto (AC #4)

Tests scrolling within Generation 2 (100 Pokémon).

| Test ID | Start Pokemon | End Pokemon | Expected Path | Actual Presses | Pass/Fail | Notes |
|---------|--------------|-------------|---------------|----------------|-----------|-------|
| WG-J1   | #152 Chikorita | #153 Bayleef | Down (1) | ___ | ☐ | Adjacent next |
| WG-J2   | #152 Chikorita | #251 Celebi | Up (wrap) (1) | ___ | ☐ | Wrap to end |
| WG-J3   | #251 Celebi | #152 Chikorita | Down (wrap) (1) | ___ | ☐ | Wrap to start |
| WG-J4   | #152 Chikorita | #200 Misdreavus | Hold Down (1) | ___ | ☐ | Fast scroll forward |
| WG-J5   | #200 Misdreavus | #152 Chikorita | Hold Up (1) | ___ | ☐ | Fast scroll backward |
| WG-J6   | #175 Togepi | #225 Delibird | Hold Down (1) | ___ | ☐ | Mid to mid distant |

**Johto Summary:**
- Total paths tested: ___/6
- Paths ≤ 3 presses: ___

---

## Within-Generation Navigation - Hoenn (AC #4)

Tests scrolling within Generation 3 (135 Pokémon).

| Test ID | Start Pokemon | End Pokemon | Expected Path | Actual Presses | Pass/Fail | Notes |
|---------|--------------|-------------|---------------|----------------|-----------|-------|
| WG-H1   | #252 Treecko | #253 Grovyle | Down (1) | ___ | ☐ | Adjacent next |
| WG-H2   | #252 Treecko | #386 Deoxys | Up (wrap) (1) | ___ | ☐ | Wrap to end |
| WG-H3   | #386 Deoxys | #252 Treecko | Down (wrap) (1) | ___ | ☐ | Wrap to start |
| WG-H4   | #252 Treecko | #300 Skitty | Hold Down (1) | ___ | ☐ | Fast scroll forward |
| WG-H5   | #300 Skitty | #252 Treecko | Hold Up (1) | ___ | ☐ | Fast scroll backward |
| WG-H6   | #350 Milotic | #386 Deoxys | Hold Down (1) | ___ | ☐ | Near end to last |

**Hoenn Summary:**
- Total paths tested: ___/6
- Paths ≤ 3 presses: ___

---

## Home → Detail View Navigation

Tests navigation from home screen to detail view (involves A button).

| Test ID | Start Screen | Target Pokemon | Expected Path | Actual Presses | Pass/Fail | Notes |
|---------|-------------|----------------|---------------|----------------|-----------|-------|
| HD-1    | Home (current) | Current Pokemon | A (1) | ___ | ☐ | View current |
| HD-2    | Home (#025) | #026 Raichu | Down→A (2) | ___ | ☐ | Adjacent + view |
| HD-3    | Home (#001) | #050 Diglett | Hold Down→A (2) | ___ | ☐ | Fast scroll + view |
| HD-4    | Home (#025) | #252 Treecko (Hoenn) | R→R→A (3) | ___ | ☐ | Cross-gen + view |

**Home → Detail Summary:**
- Total paths tested: ___/4
- Paths ≤ 3 presses: ___

---

## Detail → Adjacent Navigation

Tests L/R navigation between adjacent Pokémon in detail view (Story 3.6 - may not be implemented yet).

| Test ID | Start Pokemon | End Pokemon | Expected Path | Status | Notes |
|---------|--------------|-------------|---------------|---------|-------|
| DA-1    | #025 Pikachu Detail | #026 Raichu Detail | R (1) | ☐ N/A (Story 3.6) | Adjacent nav in detail |
| DA-2    | #025 Pikachu Detail | #024 Arbok Detail | L (1) | ☐ N/A (Story 3.6) | Adjacent nav backward |

**Detail → Adjacent Summary:**
- Feature implemented: ☐ Yes  ☐ No (Expected: No for Story 1.7)

---

## Edge Cases & Boundary Testing

Special scenarios that might violate 3-press rule.

| Test ID | Scenario | Expected | Actual | Pass/Fail | Notes |
|---------|----------|----------|--------|-----------|-------|
| EC-1    | Longest possible path (any to any) | ≤ 3 presses | ___ | ☐ | Should be Kanto #1 → Hoenn #386 |
| EC-2    | Boundary wrapping doesn't add presses | 1 press | ___ | ☐ | #151 → #001 via Down |
| EC-3    | Hold-to-scroll counts as 1 action | 1 action | ___ | ☐ | Regardless of distance |
| EC-4    | Generation switch during fast scroll | Works correctly | ___ | ☐ | Doesn't interfere |
| EC-5    | Rapid alternating L/R switches | No crash/hang | ___ | ☐ | Performance test |

**Edge Cases Summary:**
- Total edge cases tested: ___/5
- Edge cases passing: ___

---

## Hold-to-Scroll Performance (AC #4)

Validate that hold-to-scroll acceleration enables efficient navigation.

| Metric | Target | Actual | Pass/Fail | Notes |
|--------|--------|--------|-----------|-------|
| Acceleration start threshold | 0.5s | ___ | ☐ | Time before 3 Pokemon/frame |
| Turbo mode threshold | 1.0s | ___ | ☐ | Time before 5 Pokemon/frame |
| Time to scroll Kanto (#1 → #151) | < 5 seconds | ___ | ☐ | With hold-to-scroll |
| Time to scroll Johto (#152 → #251) | < 3 seconds | ___ | ☐ | 100 Pokemon |
| Time to scroll Hoenn (#252 → #386) | < 4 seconds | ___ | ☐ | 135 Pokemon |
| Boundary wrap instant | Instant | ___ | ☐ | #151 → #001 via Up/Down |

**Hold-to-Scroll Summary:**
- Feature working as expected: ☐ Yes  ☐ No
- Acceleration thresholds correct: ☐ Yes  ☐ No

---

## Overall Test Results

**Total Paths Tested:** ___  
**Paths ≤ 3 Presses:** ___  
**Paths > 3 Presses:** ___ (should be 0)  
**Pass Rate:** ___% (should be 100%)

**3-Press Navigation Rule Validation:**
- ☐ **PASS** - All paths reachable in ≤ 3 presses
- ☐ **FAIL** - Some paths require > 3 presses

**Issues Found:**

1. ___________________________________________________________
2. ___________________________________________________________
3. ___________________________________________________________

**Optimization Recommendations:**

1. ___________________________________________________________
2. ___________________________________________________________
3. ___________________________________________________________

---

## Sign-Off

**Tester Signature:** ________________________  **Date:** __________

**Notes:**

- Any path requiring > 3 presses is a requirement violation and must be documented
- Hold-to-scroll should enable traversing entire generations in seconds
- Boundary wrapping (first ↔ last) should always be 1 press
- Cross-generation navigation is limited by 3 generation count (max 2 presses for gen switch)
- If any test fails, investigate and propose navigation improvements

---

**Related Requirements:**
- Story 1.7: Performance Optimization and 3-Press Navigation Rule
- AC #3: 3-Press Navigation Rule - Cross-Generation
- AC #4: 3-Press Navigation Rule - Within Generation
- PRD FR2.4: 3-Press Navigation Rule
