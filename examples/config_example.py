"""
Example Configuration for ShokeDex

This file demonstrates how to create performance profiles for different
Raspberry Pi models and use cases. Copy this to src/config.py and customize.
"""

# Display Configuration
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320
FPS = 30

# Database Configuration
DATABASE_PATH = "data/pokedex.db"

# Performance Profiles
PERFORMANCE_PROFILES = {
    'pi3': {
        'name': 'Raspberry Pi 3B+',
        'fps': 30,
        'sprite_cache_size': 50,
        'resolution': (480, 320),
        'debounce_time': 0.1,
        'enable_vsync': True,
        'db_cache_size': 32000,  # 32MB
    },
    'pi4': {
        'name': 'Raspberry Pi 4',
        'fps': 60,
        'sprite_cache_size': 100,
        'resolution': (800, 480),
        'debounce_time': 0.05,
        'enable_vsync': True,
        'db_cache_size': 64000,  # 64MB
    },
    'performance': {
        'name': 'Maximum Performance (Lower Quality)',
        'fps': 30,
        'sprite_cache_size': 25,
        'resolution': (320, 240),
        'debounce_time': 0.15,
        'enable_vsync': False,
        'db_cache_size': 16000,  # 16MB
    },
    'quality': {
        'name': 'Maximum Quality (Slower)',
        'fps': 60,
        'sprite_cache_size': 150,
        'resolution': (800, 480),
        'debounce_time': 0.05,
        'enable_vsync': True,
        'db_cache_size': 128000,  # 128MB
    },
}

# Default profile to use
DEFAULT_PROFILE = 'pi3'

# GPIO Pin Configuration (BCM numbering)
GPIO_PIN_MAP = {
    'up': 17,
    'down': 27,
    'left': 22,
    'right': 23,
    'select': 24,
    'back': 25,
    'start': 16,
}

# Input Configuration
INPUT_MODE = 'keyboard'  # 'keyboard' or 'gpio'
ENABLE_GPIO_PULLUP = True  # Use software pull-up resistors

# Performance Monitoring
ENABLE_PERFORMANCE_MONITORING = False  # Enable for development/debugging
PERFORMANCE_OVERLAY = False  # Show FPS/CPU overlay on screen
PERFORMANCE_LOG_INTERVAL = 30  # Log performance stats every N seconds

# Sprite Configuration
SPRITE_THUMB_SIZE = (32, 32)
SPRITE_DETAIL_SIZE = (96, 96)
SPRITE_CACHE_ENABLED = True

# Database Optimization
DB_PRAGMAS = {
    'journal_mode': 'WAL',  # Write-Ahead Logging for better concurrency
    'synchronous': 'NORMAL',  # Balance between safety and speed
    'temp_store': 'MEMORY',  # Use RAM for temporary tables
    'mmap_size': 30000000000,  # 30GB memory-mapped I/O
    'page_size': 4096,  # Standard page size
}

# UI Configuration
UI_FONT_SIZE = 14
UI_GRID_COLS = 4
UI_GRID_ROWS = 3
UI_ANIMATION_SPEED = 0.2  # Seconds for transitions

# Development Settings
DEBUG_MODE = False
VERBOSE_LOGGING = False


def detect_pi_model():
    """
    Detect Raspberry Pi model and return appropriate profile.
    
    Returns:
        str: Profile name ('pi3', 'pi4', or DEFAULT_PROFILE if detection fails)
    """
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read()
            if 'Pi 4' in model or 'Pi 400' in model:
                return 'pi4'
            elif 'Pi 3' in model:
                return 'pi3'
    except FileNotFoundError:
        # Not running on Raspberry Pi
        pass
    except Exception as e:
        print(f"Warning: Could not detect Pi model: {e}")
    
    return DEFAULT_PROFILE


def get_active_profile():
    """
    Get the active performance profile.
    
    Returns:
        dict: Profile configuration dictionary
    """
    profile_name = detect_pi_model()
    return PERFORMANCE_PROFILES[profile_name]


def apply_profile(profile_name):
    """
    Apply a specific performance profile to global configuration.
    
    Args:
        profile_name (str): Name of profile to apply
    """
    if profile_name not in PERFORMANCE_PROFILES:
        print(f"Warning: Profile '{profile_name}' not found, using default")
        profile_name = DEFAULT_PROFILE
    
    profile = PERFORMANCE_PROFILES[profile_name]
    
    # Apply profile settings to globals
    global FPS, DISPLAY_WIDTH, DISPLAY_HEIGHT
    FPS = profile['fps']
    DISPLAY_WIDTH, DISPLAY_HEIGHT = profile['resolution']
    
    print(f"Applied profile: {profile['name']}")
    print(f"  Resolution: {DISPLAY_WIDTH}x{DISPLAY_HEIGHT}")
    print(f"  Target FPS: {FPS}")


def get_config():
    """
    Get complete configuration dictionary.
    
    Returns:
        dict: All configuration settings
    """
    profile = get_active_profile()
    
    return {
        'display': {
            'width': DISPLAY_WIDTH,
            'height': DISPLAY_HEIGHT,
            'fps': FPS,
            'vsync': profile.get('enable_vsync', True),
        },
        'input': {
            'mode': INPUT_MODE,
            'gpio_pins': GPIO_PIN_MAP,
            'debounce_time': profile.get('debounce_time', 0.1),
            'pullup': ENABLE_GPIO_PULLUP,
        },
        'performance': {
            'sprite_cache_size': profile.get('sprite_cache_size', 50),
            'db_cache_size': profile.get('db_cache_size', 32000),
            'monitoring_enabled': ENABLE_PERFORMANCE_MONITORING,
            'overlay_enabled': PERFORMANCE_OVERLAY,
        },
        'database': {
            'path': DATABASE_PATH,
            'pragmas': DB_PRAGMAS,
        },
        'ui': {
            'font_size': UI_FONT_SIZE,
            'grid_cols': UI_GRID_COLS,
            'grid_rows': UI_GRID_ROWS,
            'animation_speed': UI_ANIMATION_SPEED,
        },
        'sprites': {
            'thumb_size': SPRITE_THUMB_SIZE,
            'detail_size': SPRITE_DETAIL_SIZE,
            'cache_enabled': SPRITE_CACHE_ENABLED,
        },
        'debug': {
            'mode': DEBUG_MODE,
            'verbose': VERBOSE_LOGGING,
        },
    }


# Example usage in main application:
"""
from src.config import get_config, apply_profile

# Auto-detect and apply profile
apply_profile(detect_pi_model())

# Or manually select profile
# apply_profile('pi4')

# Get full configuration
config = get_config()

# Use in application
screen = pygame.display.set_mode((config['display']['width'], config['display']['height']))
clock = pygame.time.Clock()

# Main loop
while running:
    clock.tick(config['display']['fps'])
    # ...
"""


if __name__ == '__main__':
    # Demo: Show detected profile and configuration
    print("ShokeDex Configuration Example")
    print("=" * 60)
    print()
    
    detected = detect_pi_model()
    print(f"Detected profile: {detected}")
    print()
    
    profile = get_active_profile()
    print(f"Profile: {profile['name']}")
    print(f"  Resolution: {profile['resolution']}")
    print(f"  Target FPS: {profile['fps']}")
    print(f"  Sprite Cache: {profile['sprite_cache_size']} sprites")
    print(f"  Debounce Time: {profile['debounce_time']}s")
    print()
    
    print("Available profiles:")
    for name, prof in PERFORMANCE_PROFILES.items():
        print(f"  - {name}: {prof['name']}")
    print()
    
    print("Full configuration:")
    import json
    config = get_config()
    print(json.dumps(config, indent=2))
