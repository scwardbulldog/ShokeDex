# ShokeDex Data Module

This module handles all database operations and data loading for ShokeDex.

## Components

### `database.py`

Core database module that provides:
- SQLite database connection management
- Schema creation and management
- Query methods for Pokémon, types, stats, and evolutions
- Context manager support for safe connection handling

**Key Classes:**
- `Database`: Main database interface

**Usage:**
```python
from src.data.database import Database

with Database() as db:
    pokemon = db.get_pokemon_by_id(25)
    print(f"{pokemon['name']}: {pokemon['types']}")
```

### `loader.py`

Data loader that fetches Pokémon data from PokéAPI and populates the database.

**Key Classes:**
- `PokemonDataLoader`: Fetches and loads data from PokéAPI

**Features:**
- Rate limiting to respect API usage policies
- Automatic generation detection
- Comprehensive data loading (types, stats, evolutions, abilities)

**Usage:**
```python
from src.data.database import Database
from src.data.loader import PokemonDataLoader

with Database() as db:
    db.create_schema()
    loader = PokemonDataLoader(db)
    loader.load_all_gen1_to_3()
```

### `migrations.py`

Database migration management system for schema versioning.

**Key Classes:**
- `Migration`: Represents a single migration
- `MigrationManager`: Manages and applies migrations

**Features:**
- Version tracking
- Upgrade and downgrade support
- Migration history

**Usage:**
```python
from src.data.database import Database
from src.data.migrations import MigrationManager, Migration

with Database() as db:
    manager = MigrationManager(db)
    manager.apply_all_pending()
```

### `manage_db.py`

Command-line interface for database management.

**Commands:**
- `init`: Initialize database schema
- `seed`: Load Pokémon data from PokéAPI
- `stats`: Show database statistics
- `query`: Query Pokémon information
- `migrate`: Run pending migrations

**Usage:**
```bash
# Initialize database
python src/data/manage_db.py init

# Seed with Gen 1-3 data
python src/data/manage_db.py seed --gen 1-3

# Query a Pokémon
python src/data/manage_db.py query --id 25

# Show statistics
python src/data/manage_db.py stats
```

## Database Schema

The database includes the following tables:

### Core Tables
- **pokemon**: Basic Pokémon information
- **types**: Type definitions (Fire, Water, etc.)
- **stats**: Stat definitions (HP, Attack, etc.)

### Relationship Tables
- **pokemon_types**: Links Pokémon to their types
- **pokemon_stats**: Stores base stat values for each Pokémon
- **pokemon_abilities**: Links Pokémon to their abilities

### Evolution Tables
- **evolution_chains**: Evolution chain identifiers
- **evolutions**: Evolution relationships and requirements

### Support Tables
- **abilities**: Ability definitions
- **moves**: Move definitions (structure for future use)
- **pokemon_moves**: Links Pokémon to their moves (structure for future use)
- **schema_version**: Tracks database schema version

For detailed schema documentation, see [docs/database_schema.md](../../docs/database_schema.md).

## Data Coverage

Currently supports Generations 1-3:
- **Gen 1**: Pokémon #1-151 (Bulbasaur to Mew)
- **Gen 2**: Pokémon #152-251 (Chikorita to Celebi)  
- **Gen 3**: Pokémon #252-386 (Treecko to Deoxys)

## Development

### Adding New Features

1. **New Queries**: Add methods to the `Database` class
2. **New Data Sources**: Extend `PokemonDataLoader` or create new loaders
3. **Schema Changes**: Create migrations in `migrations.py`

### Testing

Run tests with:
```bash
python -m unittest tests.test_database -v
```

### Future Enhancements

Planned features:
- Move data population
- Sprite/image management
- Type effectiveness data
- Form and variant support
- Additional generations

## Performance Considerations

- Uses indexes on commonly queried columns
- Connection pooling recommended for high-frequency access
- Rate limiting on API requests to respect PokéAPI terms
- Batch inserts for efficient data loading

## Dependencies

- **sqlite3**: Python standard library
- **requests**: HTTP client for API calls
- **pathlib**: Path handling (standard library)
- **typing**: Type hints (standard library)

## License

Part of the ShokeDex project - see main LICENSE file.

## Contributing

When modifying the data module:
1. Maintain backward compatibility with existing database files
2. Create migrations for schema changes
3. Update tests for new functionality
4. Document changes in this README and schema documentation
5. Follow PEP 8 style guidelines
