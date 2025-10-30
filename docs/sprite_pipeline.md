# Sprite Pipeline & Asset Generation

## Overview

The ShokeDex sprite pipeline converts Pokémon sprites to a Gameboy Color (GBC) style palette with dithering, creating retro-styled assets optimized for display on the Raspberry Pi LCD screen.

## Gameboy Color Palette

The Gameboy Color had a 15-bit color depth (32,768 possible colors) but could only display 56 colors simultaneously across 8 palettes. Our pipeline uses a carefully selected 56-color palette that covers the full range needed for Pokémon sprites:

### Palette Breakdown

1. **Grayscale (4 colors)**: White, Light gray, Dark gray, Black
2. **Reds/Pinks (4 colors)**: Red, Light red, Dark red, Pink
3. **Blues (4 colors)**: Blue, Light blue, Dark blue, Cyan
4. **Greens (4 colors)**: Green, Light green, Dark green, Teal
5. **Yellows/Oranges (4 colors)**: Yellow, Gold, Orange, Brown
6. **Purples (4 colors)**: Purple, Magenta, Light purple, Dark purple
7. **Extended colors (32 colors)**: Additional shades and variations for better color representation

### Color Values

The complete palette is defined in `src/data/sprite_processor.py` as `GAMEBOY_COLOR_PALETTE`. Each color is represented as an RGB tuple with values from 0-255.

## Sprite Processing Pipeline

### Process Overview

1. **Source Acquisition**: Download high-quality sprites from PokéAPI
2. **Resizing**: Scale sprites to target dimensions while preserving aspect ratio
3. **Quantization**: Map colors to the closest GBC palette colors
4. **Dithering**: Apply Floyd-Steinberg dithering for smooth color transitions
5. **Output Generation**: Save both thumbnail and detail versions

### Sprite Sizes

- **Thumbnail**: 32x32 pixels - Used in list views and quick browsing
- **Detail**: 96x96 pixels - Used in detailed Pokémon information screens

Both sizes maintain aspect ratio with centered positioning on a transparent background.

## Usage

### Command Line Interface

The sprite processor can be run as a standalone script:

```bash
# Process all generations (1-3)
python src/data/sprite_processor.py --all

# Process a specific generation
python src/data/sprite_processor.py --gen 1
python src/data/sprite_processor.py --gen 2
python src/data/sprite_processor.py --gen 3

# Process a specific Pokémon by ID
python src/data/sprite_processor.py --pokemon 25  # Pikachu

# Customize output directory
python src/data/sprite_processor.py --all --output /path/to/output

# Adjust API rate limiting (delay in seconds)
python src/data/sprite_processor.py --gen 1 --delay 0.2
```

### Programmatic Usage

```python
from src.data.sprite_processor import SpriteProcessor

# Create processor
processor = SpriteProcessor(output_dir='assets/sprites')

# Process a single Pokémon
processor.process_pokemon_sprite(pokemon_id=25, pokemon_name='Pikachu')

# Process an entire generation
processor.process_generation(1)  # Gen 1

# Process all generations
processor.process_all_generations()
```

### Direct Image Processing

```python
from PIL import Image
from src.data.sprite_processor import SpriteProcessor

# Create processor
processor = SpriteProcessor()

# Load an image
image = Image.open('path/to/sprite.png')

# Process sprite into thumbnail and detail versions
thumb, detail = processor.process_sprite(image)

# Save processed images
thumb.save('thumbnail.png')
detail.save('detail.png')
```

## Output Structure

Processed sprites are stored in the following directory structure:

```
assets/sprites/
├── thumb/              # Thumbnail sprites (32x32)
│   ├── 001.png        # Bulbasaur
│   ├── 002.png        # Ivysaur
│   └── ...
└── detail/             # Detail sprites (96x96)
    ├── 001.png        # Bulbasaur
    ├── 002.png        # Ivysaur
    └── ...
```

File names follow the format `{pokemon_id:03d}.png`, where the Pokémon ID is zero-padded to 3 digits.

## Performance Considerations

### API Rate Limiting

The processor includes rate limiting to avoid overwhelming PokéAPI:
- Default delay: 0.1 seconds between requests
- Configurable via `--delay` parameter
- Processing all Gen 1-3 (386 Pokémon) takes approximately 10-15 minutes

### Caching

The processor checks if sprites already exist before processing:
- Skips re-processing if both thumbnail and detail versions exist
- Allows resuming interrupted processing sessions
- Reduces unnecessary API calls

### Internet Requirements

- Initial processing requires internet connection to fetch sprites from PokéAPI
- Once processed, sprites are stored locally and don't require internet
- Consider pre-processing sprites before deploying to Raspberry Pi

## Technical Details

### Quantization Algorithm

The pipeline uses Pillow's built-in quantization with a custom palette:

1. **Color Mapping**: Each pixel is mapped to the nearest color in the GBC palette using Euclidean distance in RGB space
2. **Dithering**: Floyd-Steinberg dithering is applied to distribute quantization errors across neighboring pixels
3. **Alpha Preservation**: Transparency is preserved through the process by handling the alpha channel separately

### Image Quality

The GBC palette and dithering provide several benefits:
- **Retro Aesthetic**: Authentic Gameboy Color look and feel
- **Reduced File Size**: Limited palette means smaller PNG files
- **Better Display**: Optimized for small LCD screens with limited color depth
- **Consistent Style**: Uniform appearance across all sprites

## Troubleshooting

### Common Issues

**Problem**: "Error fetching sprite URL"
- **Cause**: Network connectivity issues or PokéAPI rate limiting
- **Solution**: Check internet connection, increase `--delay` parameter

**Problem**: "Failed to download sprite"
- **Cause**: Invalid sprite URL or network timeout
- **Solution**: Retry processing, check if the Pokémon ID is valid

**Problem**: Sprites look pixelated or blocky
- **Cause**: This is expected! The GBC palette and dithering create a retro look
- **Solution**: This is intentional. To disable dithering, modify `use_dithering=False` in the code

**Problem**: Processing is too slow
- **Cause**: Conservative rate limiting to respect PokéAPI
- **Solution**: Decrease `--delay` parameter (minimum 0.05 seconds recommended)

### Validation

To verify processed sprites:

```bash
# Check if sprites exist
ls -l assets/sprites/thumb/ | wc -l
ls -l assets/sprites/detail/ | wc -l

# View a specific sprite
# (On systems with image viewers)
xdg-open assets/sprites/detail/025.png  # Pikachu
```

## Integration with ShokeDex

The processed sprites integrate with ShokeDex:

1. **Database**: Sprite paths can be stored in the database alongside Pokémon data
2. **UI Rendering**: Load sprites using Pillow or pygame for display
3. **Caching**: Pre-load frequently accessed sprites into memory

Example integration:

```python
from PIL import Image
import pygame

# Load sprite with Pillow
sprite = Image.open('assets/sprites/detail/025.png')

# Convert to pygame surface for rendering
mode = sprite.mode
size = sprite.size
data = sprite.tobytes()
py_image = pygame.image.fromstring(data, size, mode)
```

## Future Enhancements

Potential improvements to the sprite pipeline:

1. **Custom Palettes**: Support for different color schemes (original GB green, custom themes)
2. **Batch Optimization**: Parallel processing for faster generation
3. **Format Options**: Support for other formats (BMP, GIF for animation)
4. **Sprite Variants**: Shiny forms, gender differences, regional variants
5. **Animation Support**: Animated sprites for detail view
6. **Compression**: Further optimize file sizes for storage

## Credits

- Sprite data sourced from [PokéAPI](https://pokeapi.co/)
- Gameboy Color palette inspired by authentic GBC hardware capabilities
- Processing powered by [Pillow](https://python-pillow.org/)

## License

This tool is part of ShokeDex and follows the same MIT License with IP disclaimer. Pokémon sprites are property of Nintendo, Creatures Inc., and GAME FREAK Inc.
