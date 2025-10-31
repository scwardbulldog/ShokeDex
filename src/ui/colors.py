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
