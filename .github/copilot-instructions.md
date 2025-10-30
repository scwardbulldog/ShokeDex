# GitHub Copilot Instructions for ShokeDex

## Project Overview

ShokeDex is a handheld Pokédex device built on Raspberry Pi that displays Pokémon information with an LCD display and interactive GPIO controls. This is a Python-based hardware project targeting Raspberry Pi 3B+ or newer with Raspberry Pi OS (Bookworm).

**Key Characteristics:**
- Educational fan project inspired by Pokémon franchise (not commercially affiliated)
- Designed for resource-constrained Raspberry Pi hardware
- Physical device with LCD display and button controls via GPIO
- Local-first architecture with offline capability
- Supports Pokémon Generations 1-3 (National Pokédex #1-386)

## Tech Stack

### Core Technologies
- **Python 3.11+** - Primary language (3.12 supported)
- **pygame 2.5.0+** - Graphics rendering and display management
- **Pillow 10.0.0+** - Image processing and sprite manipulation
- **SQLite3** - Local database (Python standard library)
- **requests 2.31.0+** - HTTP client for PokéAPI integration
- **gpiozero 2.0.0+** - GPIO interface for physical buttons

### Target Platform
- Raspberry Pi OS (Bookworm - Debian 12 based)
- Kernel 6.1+
- Headless or desktop operation
- Small LCD displays (3.5"-7") with resolutions like 480x320 or 800x480

## Architecture & Design Patterns

### Database Layer (`src/data/`)
- **Database class**: Context manager pattern for SQLite connections
- **PokemonDataLoader**: Fetches data from PokéAPI with rate limiting
- **MigrationManager**: Schema versioning system
- All queries use **parameterized statements** to prevent SQL injection
- Comprehensive relational schema with 12 tables covering:
  - Core Pokémon data (pokemon table)
  - Types (18 Pokémon types)
  - Stats (HP, Attack, Defense, Sp.Atk, Sp.Def, Speed)
  - Evolution chains with requirements
  - Abilities
  - Moves (structure for future use)

### Project Structure
```
src/
├── data/           # Database operations (IMPLEMENTED)
├── ui/             # User interface modules (COMING SOON)
├── hardware/       # GPIO controls (COMING SOON)
├── config.py       # Configuration (COMING SOON)
└── main.py         # Entry point (COMING SOON)
```

## Coding Standards

### Python Style
- Follow **PEP 8** guidelines strictly
- Use type hints where beneficial for clarity
- Write descriptive docstrings for all public functions/classes
- Keep functions focused and single-purpose
- Use meaningful variable names (e.g., `pokemon_id`, not `pid`)

### Database Operations
- **Always use parameterized queries**: `cursor.execute("SELECT * FROM pokemon WHERE id = ?", (pokemon_id,))`
- Never use string formatting for SQL queries
- Use context managers (`with Database() as db:`) for connections
- Handle exceptions gracefully with appropriate error messages
- Close cursors after use

### Error Handling
- Catch specific exceptions rather than bare `except:`
- Provide informative error messages for users
- Log errors appropriately (consider Raspberry Pi log accessibility)
- Gracefully handle missing hardware (GPIO) when developing on non-Pi systems

### Performance Considerations
- Optimize for Raspberry Pi's limited resources
- Use indexes on frequently queried columns (name, generation, types)
- Batch database operations when possible
- Be mindful of memory usage with image/sprite loading
- Cache frequently accessed data appropriately

## Domain Knowledge

### Pokémon Data
- **National Pokédex numbers**: #001-151 (Gen 1), #152-251 (Gen 2), #252-386 (Gen 3)
- **Types for Gen 1-3**: 
  - Gen 1 (15 types): Normal, Fire, Water, Electric, Grass, Ice, Fighting, Poison, Ground, Flying, Psychic, Bug, Rock, Ghost, Dragon
  - Gen 2+ adds: Dark, Steel (17 types total)
  - Note: Fairy type was introduced in Gen 6, not applicable to this project
- **6 Base Stats**: HP, Attack, Defense, Special Attack, Special Defense, Speed
- Pokémon can have 1-2 types (dual-typing)
- Evolution chains can be complex (branching, items, happiness, trades, etc.)

### Data Source
- Primary source: **PokéAPI** (https://pokeapi.co/)
- Rate limiting: Default 0.5s delay between requests
- No authentication required
- Comprehensive and well-structured data
- Use `PokemonDataLoader` class for all API interactions

## Hardware Integration Patterns

### GPIO Button Handling (Future Implementation)
- Use `gpiozero` library for button controls
- Implement pull-down resistors (10kΩ) for each button
- Debounce buttons to prevent false triggers
- Common button layout: D-pad (4 buttons) + A/B/Select/Start (4 buttons)
- Handle graceful degradation when GPIO unavailable (development mode)

### Display Considerations
- Target small LCD screens (480x320 to 800x480)
- Design UI for readability at small sizes
- Use pygame for rendering
- Consider touch and non-touch display variants
- Optimize sprite sizes for performance and display resolution

## Testing Requirements

### Test Framework
- Use Python's `unittest` module (existing tests in `tests/`)
- Run tests with: `python -m unittest discover tests -v`
- Maintain test coverage for all database operations
- Test edge cases (missing data, API failures, invalid inputs)

### Test Patterns
- Use temporary databases for testing (`:memory:` or temp files)
- Clean up resources in `tearDown()` methods
- Mock external API calls when testing loader functionality
- Test context manager behavior explicitly

## Common Operations

### Database Management CLI
The `src/data/manage_db.py` script provides:
- `init` - Initialize database schema
- `seed --gen 1-3` - Load Pokémon data from PokéAPI
- `stats` - Show database statistics  
- `query --id 25` or `--name pikachu` - Query Pokémon data
- `migrate` - Run schema migrations

### Querying Pokémon Data
```python
from src.data.database import Database

with Database() as db:
    # Get Pokémon by ID
    pokemon = db.get_pokemon_by_id(25)  # Pikachu
    
    # Get Pokémon by name
    pokemon = db.get_pokemon_by_name("pikachu")
    
    # Get base stats
    stats = db.get_pokemon_stats(25)
    
    # Get types
    types = db.get_pokemon_types(25)
    
    # Get evolution chain
    evolutions = db.get_evolution_chain(25)
```

## Security Guidelines

- **Never commit secrets** (API keys, credentials, personal data)
- **Use parameterized queries** exclusively for SQL
- **Validate user inputs** before processing
- **Handle file paths safely** to prevent directory traversal
- **Sanitize data from external APIs** before database insertion
- Run CodeQL security scans on code changes

## File Organization

### Assets Directory
- `assets/sprites/` - Pokémon sprite images
- `assets/icons/` - UI icons and graphics
- `assets/fonts/` - Custom fonts for display

### Data Directory
- `data/pokedex.db` - SQLite database (created on init, not version controlled)

### Documentation
- Keep docs up-to-date with code changes
- Use Markdown for all documentation
- Include code examples in docs
- Document breaking changes clearly

## Future Development Areas

### Upcoming Modules
1. **UI System** (`src/ui/`):
   - pygame-based interface
   - Screen management and navigation
   - Sprite rendering
   - Menu systems optimized for small displays

2. **Hardware Controls** (`src/hardware/`):
   - GPIO button interface
   - Input event handling
   - Button mapping configuration
   - Debouncing logic

3. **Configuration** (`src/config.py`):
   - Display settings (resolution, framerate)
   - GPIO pin mappings
   - Database paths
   - API rate limiting
   - Theme/appearance settings

4. **Main Application** (`src/main.py`):
   - Application lifecycle management
   - State management
   - Screen routing

### Planned Enhancements
- Move data population (structure exists but not yet implemented)
- Sprite/image management and caching
- Type effectiveness calculations
- Pokémon forms and variants (Alolan forms, Mega evolutions, etc.)
- Additional generations (Gen 4+)
- Export/import for offline data sharing
- Full-text search capabilities
- Sound effects and music (if supported by hardware)

## Development Workflow

1. **Setup**: Create virtual environment, install dependencies from `requirements.txt`
2. **Initialize DB**: Run `python src/data/manage_db.py init`
3. **Load Data**: Run `python src/data/manage_db.py seed --gen 1-3` (requires internet)
4. **Development**: Make changes, write tests
5. **Testing**: Run `python -m unittest discover tests -v`
6. **Documentation**: Update relevant docs
7. **Commit**: Use clear, descriptive commit messages

## Common Patterns to Suggest

### Adding New Database Queries
1. Add method to `Database` class in `src/data/database.py`
2. Use parameterized queries
3. Add corresponding test in `tests/test_database.py`
4. Document in relevant docs

### Working with PokéAPI
1. Use `PokemonDataLoader` class
2. Respect rate limiting (default 0.5s between requests)
3. Handle API errors gracefully
4. Transform API response to match database schema

### Creating New UI Screens (Future)
1. Extend base screen class
2. Implement render() and handle_input() methods
3. Follow pygame event loop pattern
4. Keep display updates efficient for Raspberry Pi

## Avoid Common Pitfalls

- ❌ Don't use string formatting for SQL queries
- ❌ Don't assume GPIO hardware is always available
- ❌ Don't load large images without scaling for target display
- ❌ Don't make unbounded API requests without rate limiting
- ❌ Don't ignore exception handling in hardware operations
- ❌ Don't commit database files or virtual environments to git
- ❌ Don't use Windows-specific paths (use `os.path` or `pathlib`)

## Helpful Reminders

- This is a **hardware project** - code must run on resource-constrained Raspberry Pi
- **Offline-first design** - core functionality should work without internet
- **Physical buttons** - UI must be navigable without mouse/keyboard
- **Small displays** - optimize for readability at 480x320 or similar resolutions
- **Fan project** - respect Pokémon IP, maintain educational focus
- **Python 3.11+** - use modern Python features where appropriate
- **SQLite** - single-file database for easy backup and portability
