"""
Color scheme for ShokeDex - Retro Gameboy-inspired palette
"""

# Gameboy Color inspired palette
class Colors:
    """Retro color palette for the UI"""
    
    # Primary colors - from the Gameboy Color palette
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    
    # Grayscale
    DARK_GRAY = (56, 56, 56)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (192, 192, 192)
    
    # Greens (classic Gameboy)
    DARK_GREEN = (15, 56, 15)
    GREEN = (48, 98, 48)
    LIGHT_GREEN = (139, 172, 15)
    PALE_GREEN = (155, 188, 15)
    
    # Blues (Gameboy palette)
    GAMEBOY_DARK_BLUE = (33, 78, 120)  # Original Gameboy-style blue
    BLUE = (68, 137, 192)
    LIGHT_BLUE = (153, 219, 255)
    
    # Reds
    DARK_RED = (120, 33, 33)
    RED = (192, 68, 68)
    LIGHT_RED = (255, 153, 153)
    
    # Yellows
    DARK_YELLOW = (184, 184, 56)
    YELLOW = (248, 216, 120)
    LIGHT_YELLOW = (255, 247, 168)
    
    # UI specific colors
    BACKGROUND = DARK_GREEN
    FOREGROUND = PALE_GREEN
    TEXT_PRIMARY = WHITE
    TEXT_SECONDARY = LIGHT_GRAY
    TEXT_DARK = DARK_GRAY
    
    # UI elements
    SELECTION_BG = LIGHT_GREEN
    SELECTION_TEXT = BLACK
    BORDER = GREEN
    HIGHLIGHT = LIGHT_BLUE
    ERROR = RED
    SUCCESS = LIGHT_GREEN
    
    # Holographic Blue System (Anime Pokédex aesthetic)
    DEEP_SPACE_BLACK = (10, 14, 26)      # #0a0e1a - Background
    DARK_BLUE = (26, 47, 74)              # #1a2f4a - Panels
    ELECTRIC_BLUE = (0, 212, 255)         # #00d4ff - Primary UI, borders
    BRIGHT_CYAN = (77, 247, 255)          # #4df7ff - Highlights, glow
    ICE_BLUE = (168, 230, 255)            # #a8e6ff - Secondary text
    HOLOGRAM_WHITE = (232, 244, 248)      # #e8f4f8 - Primary text
    
    # Stat bar colors (Story 3.2 - color-coded by value ranges)
    STAT_COLORS = {
        'low': (113, 128, 150),          # 0-50: Gray #718096
        'medium': (0, 212, 255),         # 51-100: Electric blue #00d4ff
        'high': (77, 247, 255),          # 101-150: Bright cyan #4df7ff
        'exceptional': (255, 107, 53)    # 151+: Plasma orange #ff6b35
    }


# Type colors for Pokemon type badges (Story 3.3)
# Based on UX Design Specification - Holographic Palette (Gen 1-3 types only)
# Source: docs/ux-design-specification.md#Type-Colors
TYPE_COLORS = {
    'normal': (184, 184, 208),      # #b8b8d0 - Cooler futuristic gray
    'fire': (255, 107, 53),         # #ff6b35 - Plasma orange
    'water': (77, 159, 255),        # #4d9fff - Electric blue
    'electric': (255, 210, 63),     # #ffd23f - Neon yellow
    'grass': (107, 255, 107),       # #6bff6b - Bright holographic green
    'ice': (168, 230, 255),         # #a8e6ff - Ice blue
    'fighting': (255, 71, 87),      # #ff4757 - Energetic red
    'poison': (178, 77, 255),       # #b24dff - Neon purple
    'ground': (212, 165, 116),      # #d4a574 - Sandy hologram
    'flying': (141, 159, 255),      # #8d9fff - Sky hologram
    'psychic': (255, 107, 189),     # #ff6bbd - Bright psychic pink
    'bug': (184, 216, 72),          # #b8d848 - Bioluminescent green
    'rock': (196, 176, 122),        # #c4b07a - Stone with glow
    'ghost': (157, 124, 206),       # #9d7cce - Spectral purple
    'dragon': (141, 77, 255),       # #8d4dff - Majestic purple-blue
    'dark': (139, 115, 85),         # #8b7355 - Shadowed brown
    'steel': (203, 213, 224)        # #cbd5e0 - Metallic shimmer
}


def get_stat_color(value: int) -> tuple:
    """
    Map stat value to RGB color based on ranges.
    
    Args:
        value: Base stat value (0-255)
        
    Returns:
        RGB color tuple for the stat bar
        
    Color mapping (Story 3.2 AC #3):
        0-50: Gray (low stats)
        51-100: Electric blue (medium stats)
        101-150: Bright cyan (high stats)
        151+: Plasma orange (exceptional stats)
    """
    if value <= 50:
        return Colors.STAT_COLORS['low']
    elif value <= 100:
        return Colors.STAT_COLORS['medium']
    elif value <= 150:
        return Colors.STAT_COLORS['high']
    else:
        return Colors.STAT_COLORS['exceptional']
