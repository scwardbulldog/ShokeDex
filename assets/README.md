# Assets Directory

This directory contains all visual and media assets for ShokeDex.

## Structure

- **sprites/** - Pokémon sprites and images
- **icons/** - UI icons and buttons
- **fonts/** - Custom fonts for the interface

## Asset Sources

### Pokémon Sprites
Pokémon sprites are automatically processed using the sprite pipeline:
- Source: [PokéAPI Sprites](https://pokeapi.co/docs/v2#pokemon-sprites)
- Processing: Converted to Gameboy Color palette with dithering
- Sizes: Thumbnail (32x32) and Detail (96x96)
- Tool: `src/data/sprite_processor.py`

See [docs/sprite_pipeline.md](../docs/sprite_pipeline.md) for detailed documentation on generating sprites.

### Icons
UI icons should be:
- Simple and clear for small LCD displays
- High contrast for visibility
- Consistent in style

### Fonts
Recommended fonts:
- Pixel/retro fonts for authentic feel
- Clear, readable fonts for small screens
- Licenses allowing redistribution

## Copyright Notice

All Pokémon-related assets are property of Nintendo, Creatures Inc., and GAME FREAK Inc.
This project uses them for educational and personal purposes only.
See LICENSE file for full disclaimer.
