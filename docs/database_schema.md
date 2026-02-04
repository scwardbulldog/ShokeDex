# ShokeDex Database Schema

This document describes the SQLite database schema used by ShokeDex to store Pokémon data for Generations 1-3.

## Overview

The database is designed to store comprehensive Pokémon data including:
- Basic Pokémon information (name, height, weight, etc.)
- Types and type relationships
- Base stats
- Evolution chains and requirements
- Abilities
- Moves (structure provided for future use)

## Database Location

By default, the database is stored at: `data/pokedex.db`

## Schema Version

The database includes a versioning system to track schema changes over time.

Current version: **1**

## Tables

### `pokemon`

Stores basic Pokémon information.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER (PK) | Pokémon ID (National Pokédex number) |
| name | TEXT | Pokémon name (lowercase) |
| species_id | INTEGER | Species ID from PokéAPI |
| height | INTEGER | Height in decimeters |
| weight | INTEGER | Weight in hectograms |
| base_experience | INTEGER | Base experience yield |
| generation | INTEGER | Generation number (1-3) |
| is_default | BOOLEAN | Whether this is the default form |
| description | TEXT | Pokémon description/flavor text |
| created_at | TIMESTAMP | Record creation timestamp |
| updated_at | TIMESTAMP | Record update timestamp |

**Indexes:**
- `idx_pokemon_name` on `name`
- `idx_pokemon_generation` on `generation`

### `types`

Stores Pokémon type definitions.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER (PK) | Type ID |
| name | TEXT (UNIQUE) | Type name (e.g., 'fire', 'water') |
| created_at | TIMESTAMP | Record creation timestamp |

### `pokemon_types`

Junction table linking Pokémon to their types (many-to-many).

| Column | Type | Description |
|--------|------|-------------|
| pokemon_id | INTEGER (PK, FK) | Reference to pokemon.id |
| type_id | INTEGER (PK, FK) | Reference to types.id |
| slot | INTEGER | Type slot (1 or 2) |

**Indexes:**
- `idx_pokemon_types_pokemon` on `pokemon_id`
- `idx_pokemon_types_type` on `type_id`

### `stats`

Stores stat definitions.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER (PK) | Stat ID |
| name | TEXT (UNIQUE) | Stat name (e.g., 'hp', 'attack') |
| created_at | TIMESTAMP | Record creation timestamp |

**Stats included:**
1. HP
2. Attack
3. Defense
4. Special Attack
5. Special Defense
6. Speed

### `pokemon_stats`

Stores base stat values for each Pokémon.

| Column | Type | Description |
|--------|------|-------------|
| pokemon_id | INTEGER (PK, FK) | Reference to pokemon.id |
| stat_id | INTEGER (PK, FK) | Reference to stats.id |
| base_stat | INTEGER | Base stat value |
| effort | INTEGER | Effort value (EVs) |

**Indexes:**
- `idx_pokemon_stats_pokemon` on `pokemon_id`

### `evolution_chains`

Stores evolution chain identifiers.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER (PK) | Evolution chain ID |
| created_at | TIMESTAMP | Record creation timestamp |

### `evolutions`

Stores evolution relationships and requirements.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER (PK, AUTO) | Evolution record ID |
| evolution_chain_id | INTEGER (FK) | Reference to evolution_chains.id |
| from_pokemon_id | INTEGER (FK) | Source Pokémon ID (NULL for base) |
| to_pokemon_id | INTEGER (FK) | Target Pokémon ID |
| min_level | INTEGER | Minimum level required |
| trigger | TEXT | Evolution trigger (e.g., 'level-up', 'trade') |
| item | TEXT | Required item name |
| min_happiness | INTEGER | Minimum happiness required |
| time_of_day | TEXT | Required time of day |
| min_beauty | INTEGER | Minimum beauty stat |
| min_affection | INTEGER | Minimum affection |
| relative_physical_stats | INTEGER | Attack vs Defense comparison |
| party_species_id | INTEGER | Required party Pokémon species |
| party_type_id | INTEGER | Required party type |
| trade_species_id | INTEGER | Required trade partner species |
| needs_overworld_rain | BOOLEAN | Requires rain in overworld |
| turn_upside_down | BOOLEAN | Requires device upside down |

**Indexes:**
- `idx_evolutions_chain` on `evolution_chain_id`
- `idx_evolutions_from` on `from_pokemon_id`
- `idx_evolutions_to` on `to_pokemon_id`

### `abilities`

Stores ability definitions.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER (PK) | Ability ID |
| name | TEXT (UNIQUE) | Ability name |
| is_hidden | BOOLEAN | Whether this is a hidden ability |
| created_at | TIMESTAMP | Record creation timestamp |

### `pokemon_abilities`

Junction table linking Pokémon to their abilities.

| Column | Type | Description |
|--------|------|-------------|
| pokemon_id | INTEGER (PK, FK) | Reference to pokemon.id |
| ability_id | INTEGER (PK, FK) | Reference to abilities.id |
| is_hidden | BOOLEAN | Whether this is a hidden ability slot |
| slot | INTEGER | Ability slot number |

### `moves`

Stores move definitions (structure for future use).

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER (PK) | Move ID |
| name | TEXT (UNIQUE) | Move name |
| type_id | INTEGER (FK) | Reference to types.id |
| power | INTEGER | Base power |
| pp | INTEGER | Power points |
| accuracy | INTEGER | Accuracy percentage |
| priority | INTEGER | Priority modifier |
| damage_class | TEXT | Physical, Special, or Status |
| created_at | TIMESTAMP | Record creation timestamp |

### `pokemon_moves`

Junction table linking Pokémon to their moves (structure for future use).

| Column | Type | Description |
|--------|------|-------------|
| pokemon_id | INTEGER (PK, FK) | Reference to pokemon.id |
| move_id | INTEGER (PK, FK) | Reference to moves.id |
| level_learned_at | INTEGER | Level when move is learned (0 for other methods) |
| move_learn_method | TEXT (PK) | How the move is learned (e.g., 'level-up', 'tm') |

### `schema_version`

Tracks database schema versions for migration management.

| Column | Type | Description |
|--------|------|-------------|
| version | INTEGER (PK) | Schema version number |
| applied_at | TIMESTAMP | When the version was applied |
| description | TEXT | Description of the version |

## Relationships

```
pokemon
├── pokemon_types → types
├── pokemon_stats → stats
├── pokemon_abilities → abilities
├── pokemon_moves → moves
└── evolutions (as from_pokemon_id or to_pokemon_id)
    └── evolution_chains

types ← pokemon_types ← pokemon
stats ← pokemon_stats ← pokemon
abilities ← pokemon_abilities ← pokemon
moves
├── pokemon_moves → pokemon
└── types (for move type)
```

## Data Source

Data is loaded from [PokéAPI](https://pokeapi.co/) using the included data loader.

## Generations Coverage

- **Generation 1**: Pokémon #1-151 (Bulbasaur to Mew)
- **Generation 2**: Pokémon #152-251 (Chikorita to Celebi)
- **Generation 3**: Pokémon #252-386 (Treecko to Deoxys)

## Usage Examples

### Initialize Database

```bash
python src/data/manage_db.py init
```

### Seed Database with Gen 1-3 Data

```bash
python src/data/manage_db.py seed --gen 1-3
```

This will fetch data from PokéAPI and populate the database. Note: This process can take 10-20 minutes due to API rate limiting.

### Query a Pokémon

```bash
# By ID
python src/data/manage_db.py query --id 25

# By name
python src/data/manage_db.py query --name pikachu
```

### Check Database Statistics

```bash
python src/data/manage_db.py stats
```

### Programmatic Access

```python
from src.data.database import Database

# Connect to database
with Database() as db:
    # Get Pokémon by ID
    pokemon = db.get_pokemon_by_id(25)
    print(f"{pokemon['name']}: {pokemon['types']}")
    
    # Get stats
    stats = db.get_pokemon_stats(25)
    for stat in stats:
        print(f"{stat['name']}: {stat['base_stat']}")
    
    # Get evolutions
    evolutions = db.get_evolutions(25)
    for evo in evolutions:
        print(f"{evo['from_name']} → {evo['to_name']}")
```

## Migrations

The database includes a migration system for future schema updates. To apply pending migrations:

```bash
python src/data/manage_db.py migrate
```

### Creating New Migrations

Add new migrations in `src/data/migrations.py`:

```python
def migration_v2_upgrade(db: Database):
    """Add new feature"""
    cursor = db.conn.cursor()
    cursor.execute("""
        ALTER TABLE pokemon ADD COLUMN new_field TEXT
    """)

migration_v2 = Migration(
    version=2,
    description="Add new_field to pokemon table",
    upgrade=migration_v2_upgrade,
    downgrade=migration_v2_downgrade
)

# Register in MigrationManager
manager.register_migration(migration_v2)
```

## Performance Considerations

- All foreign key relationships use indexes for efficient queries
- Primary keys are indexed by default
- Common query patterns (name lookup, generation filtering) have dedicated indexes
- Use connection pooling for high-frequency access patterns

## Backup and Maintenance

Since the database is a single SQLite file, backing up is simple:

```bash
# Backup
cp data/pokedex.db data/pokedex.db.backup

# Restore
cp data/pokedex.db.backup data/pokedex.db
```

For production use, consider:
- Regular automated backups
- Write-ahead logging (WAL) mode for concurrent access
- VACUUM command for database optimization

## Future Enhancements

Potential schema additions for future versions:
- Move data population (currently structure only)
- Pokémon sprites/image paths
- Type effectiveness chart
- Move effectiveness and battle mechanics
- Pokémon forms and variants
- Additional generations (4+)
