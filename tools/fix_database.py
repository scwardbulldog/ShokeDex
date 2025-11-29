#!/usr/bin/env python3
"""
Database fix script for ShokeDex
Fixes:
1. Load era-appropriate Pokédex descriptions for all Pokémon
2. Load missing Pokémon (#299 Nincada)
3. Remove invalid types (Fairy, Stellar) not in Gen 1-3

Usage:
    python -m src.data.fix_database [--dry-run]
"""

import argparse
import requests
import time
import re
import sys
from pathlib import Path
from typing import Optional, Dict, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.database import Database


# PokéAPI base URL
BASE_URL = "https://pokeapi.co/api/v2"

# Rate limit delay between API calls (seconds)
RATE_LIMIT_DELAY = 0.1

# Valid types for Gen 1-3 (17 types - excludes Fairy from Gen 6 and Stellar from Gen 9)
VALID_GEN3_TYPES = {
    'normal', 'fire', 'water', 'electric', 'grass', 'ice',
    'fighting', 'poison', 'ground', 'flying', 'psychic',
    'bug', 'rock', 'ghost', 'dragon', 'dark', 'steel'
}

# Preferred game versions for flavor text by generation
# Listed in preference order - first available will be used
PREFERRED_VERSIONS = {
    1: ['red', 'blue', 'yellow', 'firered', 'leafgreen'],  # Gen 1: Kanto
    2: ['gold', 'silver', 'crystal', 'heartgold', 'soulsilver'],  # Gen 2: Johto  
    3: ['ruby', 'sapphire', 'emerald', 'omega-ruby', 'alpha-sapphire'],  # Gen 3: Hoenn
}

# Generation ranges
GENERATION_RANGES = {
    1: (1, 151),    # Kanto
    2: (152, 251),  # Johto
    3: (252, 386),  # Hoenn
}


def get_generation(pokemon_id: int) -> int:
    """Get generation number for a Pokémon ID."""
    if 1 <= pokemon_id <= 151:
        return 1
    elif 152 <= pokemon_id <= 251:
        return 2
    elif 252 <= pokemon_id <= 386:
        return 3
    return 0


def fetch_json(url: str) -> Optional[Dict]:
    """Fetch JSON from URL with rate limiting."""
    try:
        time.sleep(RATE_LIMIT_DELAY)
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching {url}: {e}")
        return None


def clean_flavor_text(text: str) -> str:
    """Clean up flavor text from PokéAPI.
    
    Removes form feed characters, normalizes newlines, and cleans whitespace.
    """
    # Replace form feed and other control characters with space
    text = re.sub(r'[\f\x0c]', ' ', text)
    # Replace newlines with space
    text = re.sub(r'\n', ' ', text)
    # Normalize multiple spaces to single space
    text = re.sub(r'\s+', ' ', text)
    # Strip leading/trailing whitespace
    return text.strip()


def get_era_flavor_text(species_data: dict, generation: int) -> Optional[str]:
    """Extract era-appropriate English flavor text for a Pokémon.
    
    Prefers games from the Pokémon's original generation.
    """
    flavor_entries = species_data.get('flavor_text_entries', [])
    
    # Filter to English entries only
    english_entries = [
        entry for entry in flavor_entries 
        if entry.get('language', {}).get('name') == 'en'
    ]
    
    if not english_entries:
        return None
    
    # Get preferred versions for this generation
    preferred = PREFERRED_VERSIONS.get(generation, [])
    
    # Try preferred versions in order
    for version_name in preferred:
        for entry in english_entries:
            if entry.get('version', {}).get('name') == version_name:
                return clean_flavor_text(entry['flavor_text'])
    
    # Fallback: use any English entry (prefer earlier ones)
    return clean_flavor_text(english_entries[0]['flavor_text'])


def fix_descriptions(db: Database, dry_run: bool = False) -> Tuple[int, int]:
    """Load era-appropriate Pokédex descriptions for all Pokémon.
    
    Returns:
        Tuple of (updated_count, failed_count)
    """
    print("\n" + "=" * 60)
    print("FIXING POKÉDEX DESCRIPTIONS")
    print("=" * 60)
    
    updated = 0
    failed = 0
    
    for pokemon_id in range(1, 387):
        # Check if Pokémon exists in database
        cursor = db.execute("SELECT id, name, description FROM pokemon WHERE id = ?", (pokemon_id,))
        row = cursor.fetchone()
        
        if not row:
            print(f"  #{pokemon_id}: Not in database, skipping")
            continue
            
        pokemon_name = row[1]
        current_desc = row[2]
        generation = get_generation(pokemon_id)
        
        # Skip if already has a description (unless it's very short/placeholder)
        if current_desc and len(current_desc) > 20:
            print(f"  #{pokemon_id} {pokemon_name}: Already has description, skipping")
            continue
        
        print(f"  #{pokemon_id} {pokemon_name} (Gen {generation})...", end=' ', flush=True)
        
        # Fetch species data from PokéAPI
        species_url = f"{BASE_URL}/pokemon-species/{pokemon_id}"
        species_data = fetch_json(species_url)
        
        if not species_data:
            print("FAILED (API error)")
            failed += 1
            continue
        
        # Get era-appropriate flavor text
        flavor_text = get_era_flavor_text(species_data, generation)
        
        if not flavor_text:
            print("FAILED (no English text)")
            failed += 1
            continue
        
        if dry_run:
            print(f"WOULD UPDATE: {flavor_text[:50]}...")
        else:
            db.execute(
                "UPDATE pokemon SET description = ? WHERE id = ?",
                (flavor_text, pokemon_id)
            )
            db.commit()
            print(f"OK ({len(flavor_text)} chars)")
        
        updated += 1
    
    print(f"\nDescriptions: {updated} updated, {failed} failed")
    return updated, failed


def fix_missing_pokemon(db: Database, dry_run: bool = False) -> bool:
    """Load missing Pokémon #299 (Nincada).
    
    Returns:
        True if successful, False otherwise
    """
    print("\n" + "=" * 60)
    print("FIXING MISSING POKÉMON")
    print("=" * 60)
    
    # Check which Pokémon are missing
    cursor = db.execute("SELECT id FROM pokemon WHERE id BETWEEN 1 AND 386")
    existing_ids = {row[0] for row in cursor.fetchall()}
    missing_ids = set(range(1, 387)) - existing_ids
    
    if not missing_ids:
        print("  All 386 Pokémon present!")
        return True
    
    print(f"  Missing Pokémon IDs: {sorted(missing_ids)}")
    
    for pokemon_id in sorted(missing_ids):
        print(f"  Loading #{pokemon_id}...", end=' ', flush=True)
        
        # Fetch Pokémon data
        pokemon_url = f"{BASE_URL}/pokemon/{pokemon_id}"
        pokemon_data = fetch_json(pokemon_url)
        
        if not pokemon_data:
            print("FAILED (API error)")
            return False
        
        # Fetch species data for description
        species_url = f"{BASE_URL}/pokemon-species/{pokemon_id}"
        species_data = fetch_json(species_url)
        
        generation = get_generation(pokemon_id)
        species_id = species_data['id'] if species_data else pokemon_id
        
        # Get description
        description = None
        if species_data:
            description = get_era_flavor_text(species_data, generation)
        
        if dry_run:
            print(f"WOULD INSERT: {pokemon_data['name']}")
            continue
        
        # Insert Pokémon
        db.execute("""
            INSERT OR REPLACE INTO pokemon 
            (id, name, species_id, height, weight, base_experience, generation, is_default, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pokemon_data['id'],
            pokemon_data['name'],
            species_id,
            pokemon_data['height'],
            pokemon_data['weight'],
            pokemon_data.get('base_experience'),
            generation,
            pokemon_data.get('is_default', True),
            description
        ))
        
        # Insert types
        for type_entry in pokemon_data.get('types', []):
            type_name = type_entry['type']['name']
            if type_name not in VALID_GEN3_TYPES:
                continue
            cursor = db.execute("SELECT id FROM types WHERE name = ?", (type_name,))
            type_row = cursor.fetchone()
            if type_row:
                db.execute("""
                    INSERT OR REPLACE INTO pokemon_types (pokemon_id, type_id, slot)
                    VALUES (?, ?, ?)
                """, (pokemon_id, type_row[0], type_entry['slot']))
        
        # Insert stats
        for stat_entry in pokemon_data.get('stats', []):
            stat_name = stat_entry['stat']['name']
            cursor = db.execute("SELECT id FROM stats WHERE name = ?", (stat_name,))
            stat_row = cursor.fetchone()
            if stat_row:
                db.execute("""
                    INSERT OR REPLACE INTO pokemon_stats (pokemon_id, stat_id, base_stat, effort)
                    VALUES (?, ?, ?, ?)
                """, (pokemon_id, stat_row[0], stat_entry['base_stat'], stat_entry['effort']))
        
        # Insert abilities
        for ability_entry in pokemon_data.get('abilities', []):
            ability_url = ability_entry['ability']['url']
            ability_data = fetch_json(ability_url)
            if ability_data:
                ability_id = ability_data['id']
                ability_name = ability_entry['ability']['name']
                is_hidden = ability_entry.get('is_hidden', False)
                slot = ability_entry['slot']
                
                db.execute("""
                    INSERT OR IGNORE INTO abilities (id, name)
                    VALUES (?, ?)
                """, (ability_id, ability_name))
                
                db.execute("""
                    INSERT OR REPLACE INTO pokemon_abilities (pokemon_id, ability_id, is_hidden, slot)
                    VALUES (?, ?, ?, ?)
                """, (pokemon_id, ability_id, is_hidden, slot))
        
        db.commit()
        print(f"OK ({pokemon_data['name']})")
    
    return True


def fix_invalid_types(db: Database, dry_run: bool = False) -> int:
    """Remove invalid types (Fairy, Stellar) that don't belong in Gen 1-3.
    
    Returns:
        Number of types removed
    """
    print("\n" + "=" * 60)
    print("FIXING INVALID TYPES")
    print("=" * 60)
    
    # Find invalid types
    cursor = db.execute("SELECT id, name FROM types")
    all_types = cursor.fetchall()
    
    invalid_types = [(tid, name) for tid, name in all_types if name not in VALID_GEN3_TYPES]
    
    if not invalid_types:
        print("  No invalid types found!")
        return 0
    
    print(f"  Found invalid types: {[name for _, name in invalid_types]}")
    
    removed = 0
    for type_id, type_name in invalid_types:
        print(f"  Removing '{type_name}' (id={type_id})...", end=' ', flush=True)
        
        if dry_run:
            print("WOULD REMOVE")
        else:
            # First remove any pokemon_types references (shouldn't be any for Fairy/Stellar in Gen 1-3)
            db.execute("DELETE FROM pokemon_types WHERE type_id = ?", (type_id,))
            # Then remove the type itself
            db.execute("DELETE FROM types WHERE id = ?", (type_id,))
            db.commit()
            print("OK")
        
        removed += 1
    
    print(f"\nTypes removed: {removed}")
    return removed


def main():
    parser = argparse.ArgumentParser(
        description='Fix ShokeDex database: descriptions, missing Pokémon, invalid types'
    )
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Show what would be done without making changes'
    )
    args = parser.parse_args()
    
    if args.dry_run:
        print("=" * 60)
        print("DRY RUN MODE - No changes will be made")
        print("=" * 60)
    
    print("\nShokeDex Database Fix Script")
    print("=" * 60)
    
    with Database() as db:
        # Check current state
        cursor = db.execute("SELECT COUNT(*) FROM pokemon")
        pokemon_count = cursor.fetchone()[0]
        
        cursor = db.execute("SELECT COUNT(*) FROM pokemon WHERE description IS NOT NULL AND description != ''")
        desc_count = cursor.fetchone()[0]
        
        cursor = db.execute("SELECT COUNT(*) FROM types")
        type_count = cursor.fetchone()[0]
        
        print(f"Current state:")
        print(f"  - Pokémon: {pokemon_count}/386")
        print(f"  - With descriptions: {desc_count}/{pokemon_count}")
        print(f"  - Types: {type_count} (should be 17)")
        
        # Run fixes
        fix_missing_pokemon(db, args.dry_run)
        fix_descriptions(db, args.dry_run)
        fix_invalid_types(db, args.dry_run)
        
        # Show final state
        if not args.dry_run:
            print("\n" + "=" * 60)
            print("FINAL STATE")
            print("=" * 60)
            
            cursor = db.execute("SELECT COUNT(*) FROM pokemon")
            pokemon_count = cursor.fetchone()[0]
            
            cursor = db.execute("SELECT COUNT(*) FROM pokemon WHERE description IS NOT NULL AND description != ''")
            desc_count = cursor.fetchone()[0]
            
            cursor = db.execute("SELECT COUNT(*) FROM types")
            type_count = cursor.fetchone()[0]
            
            print(f"  - Pokémon: {pokemon_count}/386")
            print(f"  - With descriptions: {desc_count}/{pokemon_count}")
            print(f"  - Types: {type_count}")
        
        print("\n✅ Database fix complete!")


if __name__ == '__main__':
    main()
