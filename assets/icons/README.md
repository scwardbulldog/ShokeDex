# ShokeDex Badge Icons

This directory contains generation badge icons for the ShokeDex UI.

## Icons Included

### Generation Badge Icons (40x40px PNG with transparency)

#### `badge_kanto.png` - Generation 1 (Kanto)
- **Design:** Circular Poké Ball inspired pattern
- **Colors:** Electric blue (#00d4ff) with bright cyan (#4df7ff)
- **Style:** Holographic outline with center circle

#### `badge_johto.png` - Generation 2 (Johto)
- **Design:** Diamond/star GS Ball inspired pattern
- **Colors:** Electric blue (#00d4ff) with bright cyan (#4df7ff)
- **Style:** 4-pointed diamond with crosshair center

#### `badge_hoenn.png` - Generation 3 (Hoenn)
- **Design:** Triangular Master Ball inspired pattern
- **Colors:** Electric blue (#00d4ff) with bright cyan (#4df7ff)
- **Style:** Upward triangle with center circle

## Generation Script

These icons were generated using `tools/create_badge_icons.py`, which uses PIL/Pillow to create geometric designs matching the holographic blue aesthetic from the UX specification.

To regenerate icons:
```bash
python tools/create_badge_icons.py
```

## Design Notes

- All icons use transparent backgrounds (RGBA format)
- Colors match the holographic blue palette from `src/ui/colors.py`
- Simple geometric shapes ensure clarity at small sizes (40x40px)
- Inspired by iconic Poké Ball variants from the games/anime:
  - Poké Ball (classic red/white) → Kanto circle
  - GS Ball (gold/silver) → Johto diamond/star
  - Master Ball (purple) → Hoenn triangle

## License

These icons are original designs created for the ShokeDex project and are subject to the same license as the project (see root LICENSE file).

**Note:** While inspired by Pokémon game elements, these are simplified geometric interpretations and not direct reproductions of official artwork.
