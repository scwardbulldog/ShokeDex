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
    
    # Blues
    DARK_BLUE = (33, 78, 120)
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
    
    # Type colors (for Pokemon types)
    TYPE_COLORS = {
        'normal': GRAY,
        'fire': RED,
        'water': BLUE,
        'electric': YELLOW,
        'grass': GREEN,
        'ice': LIGHT_BLUE,
        'fighting': DARK_RED,
        'poison': (160, 64, 160),
        'ground': (226, 191, 101),
        'flying': (169, 143, 243),
        'psychic': (249, 85, 135),
        'bug': (166, 185, 26),
        'rock': (182, 161, 54),
        'ghost': (115, 87, 151),
        'dragon': (111, 53, 252),
        'dark': (112, 87, 70),
        'steel': (183, 183, 206),
        'fairy': (214, 133, 173),
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
