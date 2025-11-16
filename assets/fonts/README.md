# ShokeDex Custom Fonts

This directory contains custom fonts for the ShokeDex UI, matching the UX Design Specification's holographic aesthetic.

## Fonts Included

### Orbitron Bold (`Orbitron-Bold.ttf`)
- **Source:** Google Fonts (Open Font License)
- **Usage:** Generation names, Pokémon names, headers
- **Style:** Futuristic geometric sans-serif
- **Size:** 285KB
- **License:** SIL Open Font License 1.1

### Share Tech Mono Regular (`ShareTechMono-Regular.ttf`)
- **Source:** Google Fonts (Open Font License)
- **Usage:** Position counters, Pokédex numbers, technical data
- **Style:** Technical monospace
- **Size:** 42KB
- **License:** SIL Open Font License 1.1

## Font Usage in Code

```python
# Load fonts with fallback
try:
    badge_name_font = pygame.font.Font("assets/fonts/Orbitron-Bold.ttf", 24)
except:
    badge_name_font = pygame.font.Font(None, 24)  # System fallback

try:
    counter_font = pygame.font.Font("assets/fonts/ShareTechMono-Regular.ttf", 18)
except:
    counter_font = pygame.font.Font(None, 18)  # System fallback
```

## License Information

Both fonts are licensed under the SIL Open Font License 1.1, which allows:
- ✅ Free use in both personal and commercial projects
- ✅ Bundling with software
- ✅ Modification and redistribution

Full license texts available at:
- https://fonts.google.com/specimen/Orbitron/license
- https://fonts.google.com/specimen/Share+Tech+Mono/license

## Download Sources

These fonts were downloaded from the official Google Fonts GitHub repository:
- Orbitron: https://github.com/google/fonts/tree/main/ofl/orbitron
- Share Tech Mono: https://github.com/google/fonts/tree/main/ofl/sharetechmono
