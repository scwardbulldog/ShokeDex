# Data Loading Guide

This guide explains how to load Pokémon data into the ShokeDex database.

## Prerequisites

- Database initialized: `python src/data/manage_db.py init`
- Internet connection (for loading from PokéAPI)
- Python 3.11+ with required dependencies

## Loading Data from PokéAPI

### Load All Gen 1-3 Data

To load all Pokémon from Generations 1-3 (Pokémon #1-386):

```bash
python src/data/manage_db.py seed --gen 1-3
```

**Note:** This process can take 10-20 minutes due to API rate limiting to respect PokéAPI's usage policies.

### Load Individual Generations

Load only specific generations:

```bash
# Generation 1 only (Bulbasaur to Mew)
python src/data/manage_db.py seed --gen 1

# Generation 2 only (Chikorita to Celebi)
python src/data/manage_db.py seed --gen 2

# Generation 3 only (Treecko to Deoxys)
python src/data/manage_db.py seed --gen 3
```

### Adjust API Rate Limiting

If you experience API rate limit errors, increase the delay between requests:

```bash
# Use 0.5 second delay between requests (slower but safer)
python src/data/manage_db.py seed --gen 1-3 --delay 0.5
```

## Programmatic Data Loading

You can also load data programmatically in your own scripts:

```python
from src.data.database import Database
from src.data.loader import PokemonDataLoader

# Initialize database
with Database() as db:
    db.create_schema()
    
    # Create loader
    loader = PokemonDataLoader(db, rate_limit_delay=0.1)
    
    # Load all Gen 1-3 data
    loader.load_all_gen1_to_3()
    
    # Or load specific ranges
    # loader.load_types()
    # loader.load_stats()
    # loader.load_pokemon(1, 151)  # Gen 1
    # loader.load_evolutions(1, 151)
```

## Loading from Local JSON/CSV Files

For environments without internet access or to speed up development, you can export data from PokéAPI once and load it locally.

### Export Data (with Internet)

```python
from src.data.database import Database
from src.data.loader import PokemonDataLoader
import json

# Export to JSON
with Database() as db:
    pokemon_list = []
    for i in range(1, 387):
        pokemon = db.get_pokemon_by_id(i)
        if pokemon:
            stats = db.get_pokemon_stats(i)
            evolutions = db.get_evolutions(i)
            pokemon['stats'] = stats
            pokemon['evolutions'] = evolutions
            pokemon_list.append(pokemon)
    
    with open('data/pokemon_gen1-3.json', 'w') as f:
        json.dump(pokemon_list, f, indent=2)
```

### Import from JSON

```python
import json
from src.data.database import Database

with open('data/pokemon_gen1-3.json', 'r') as f:
    pokemon_list = json.load(f)

with Database() as db:
    db.create_schema()
    # Insert data from JSON
    for pokemon in pokemon_list:
        # Insert pokemon, stats, evolutions...
        pass
```

## Verifying Loaded Data

After loading data, verify it was successful:

```bash
# Show statistics
python src/data/manage_db.py stats

# Query specific Pokémon
python src/data/manage_db.py query --id 25
python src/data/manage_db.py query --name pikachu
```

Expected output after loading Gen 1-3:
- Gen 1: 151 Pokémon
- Gen 2: 100 Pokémon
- Gen 3: 135 Pokémon
- Total: 386 Pokémon

## Updating Data

To update existing data:

1. The loader uses `INSERT OR REPLACE` so re-running it will update existing records
2. No need to clear the database first
3. To start fresh, delete the database file and re-initialize:

```bash
rm data/pokedex.db
python src/data/manage_db.py init
python src/data/manage_db.py seed --gen 1-3
```

## Troubleshooting

### API Connection Issues

**Error:** `Failed to resolve 'pokeapi.co'`

**Solution:** Check your internet connection. If behind a proxy, configure your environment:

```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
```

### Rate Limiting

**Error:** HTTP 429 (Too Many Requests)

**Solution:** Increase the delay between requests:

```bash
python src/data/manage_db.py seed --gen 1-3 --delay 0.5
```

### Database Locked

**Error:** `database is locked`

**Solution:** 
- Close any other programs accessing the database
- Ensure only one seeding process runs at a time
- If on Raspberry Pi, check if disk I/O is slow

### Incomplete Data

**Issue:** Some Pokémon are missing

**Solution:**
- Check the console output for specific failures
- Re-run the seed command (it will skip existing records and fill in gaps)
- Verify internet connectivity throughout the process

## Performance Notes

- Loading all 386 Pokémon takes approximately 10-20 minutes
- Each Pokémon requires 3-5 API calls:
  - Pokemon data
  - Species data
  - Ability data
  - Type data (cached after first load)
  - Evolution chain data
- Rate limiting is intentional to be respectful to PokéAPI

## Data Updates and Maintenance

### Adding New Generations

To add support for newer generations in the future:

1. Update the `get_generation_for_pokemon()` method in `loader.py`
2. Call `load_pokemon()` with the new range
3. Update documentation

Example for Gen 4:
```python
loader.load_pokemon(387, 493)  # Gen 4
loader.load_evolutions(387, 493)
```

### Refreshing Existing Data

PokéAPI data can change (corrections, new forms, etc.). To refresh:

```bash
# Re-seed will update existing records
python src/data/manage_db.py seed --gen 1-3
```

## Alternative Data Sources

If PokéAPI is unavailable, alternative sources include:

1. **Local PokéAPI Mirror**: Clone and run PokéAPI locally
2. **CSV Files**: Use exported CSV files from community sources
3. **Manual Entry**: For development, create minimal test data

## Next Steps

After loading data:
1. Verify data with `stats` and `query` commands
2. Start building the UI components
3. Test database queries in your application
4. Consider adding sprites and images to `assets/sprites/`
