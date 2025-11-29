"""
Data loader for ShokeDex
Fetches Pokémon data from PokéAPI and loads it into the database
"""

import re
import requests
import time
from typing import Dict, Any, List, Optional
from .database import Database


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


class PokemonDataLoader:
    """Loads Pokémon data from PokéAPI"""
    
    BASE_URL = "https://pokeapi.co/api/v2"
    
    def __init__(self, db: Database, rate_limit_delay: float = 0.1):
        """
        Initialize data loader
        
        Args:
            db: Database instance
            rate_limit_delay: Delay between API requests in seconds
        """
        self.db = db
        self.rate_limit_delay = rate_limit_delay
        
    def fetch_json(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch JSON data from URL with rate limiting
        
        Args:
            url: URL to fetch
            
        Returns:
            JSON data as dictionary or None if request fails
        """
        try:
            time.sleep(self.rate_limit_delay)
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
            
    def get_generation_for_pokemon(self, pokemon_id: int) -> int:
        """
        Determine generation based on Pokémon ID
        
        Args:
            pokemon_id: Pokémon ID
            
        Returns:
            Generation number (1-3 for Gen 1-3)
        """
        if 1 <= pokemon_id <= 151:
            return 1
        elif 152 <= pokemon_id <= 251:
            return 2
        elif 252 <= pokemon_id <= 386:
            return 3
        else:
            return 4  # Default for anything beyond Gen 3
            
    def load_types(self):
        """Load all Pokémon types"""
        print("Loading types...")
        types_url = f"{self.BASE_URL}/type"
        types_data = self.fetch_json(types_url)
        
        if not types_data:
            print("Failed to fetch types")
            return
            
        for type_entry in types_data.get('results', []):
            type_detail = self.fetch_json(type_entry['url'])
            if type_detail:
                type_id = type_detail['id']
                type_name = type_detail['name']
                
                # Only include valid Gen 1-3 types (17 types)
                # Excludes: unknown, shadow, fairy (Gen 6), stellar (Gen 9)
                if type_name not in VALID_GEN3_TYPES:
                    continue
                    
                self.db.execute("""
                    INSERT OR IGNORE INTO types (id, name)
                    VALUES (?, ?)
                """, (type_id, type_name))
                
        self.db.commit()
        print("Types loaded successfully")
        
    def load_stats(self):
        """Load stat definitions"""
        print("Loading stats...")
        stats = [
            (1, 'hp'),
            (2, 'attack'),
            (3, 'defense'),
            (4, 'special-attack'),
            (5, 'special-defense'),
            (6, 'speed')
        ]
        
        self.db.executemany("""
            INSERT OR IGNORE INTO stats (id, name)
            VALUES (?, ?)
        """, stats)
        
        self.db.commit()
        print("Stats loaded successfully")
        
    def load_pokemon(self, start_id: int = 1, end_id: int = 386):
        """
        Load Pokémon data for a range of IDs
        
        Args:
            start_id: Starting Pokémon ID (default: 1)
            end_id: Ending Pokémon ID (default: 386 for Gen 1-3)
        """
        print(f"Loading Pokémon {start_id} to {end_id}...")
        
        for pokemon_id in range(start_id, end_id + 1):
            print(f"Loading Pokémon #{pokemon_id}...", end=' ')
            
            pokemon_url = f"{self.BASE_URL}/pokemon/{pokemon_id}"
            pokemon_data = self.fetch_json(pokemon_url)
            
            if not pokemon_data:
                print(f"Failed")
                continue
                
            # Get species data for additional info
            species_data = None
            if 'species' in pokemon_data and pokemon_data['species']:
                species_data = self.fetch_json(pokemon_data['species']['url'])
                
            # Insert Pokémon
            generation = self.get_generation_for_pokemon(pokemon_id)
            species_id = species_data['id'] if species_data else pokemon_id
            
            # Get era-appropriate Pokédex description
            description = None
            if species_data:
                description = self._get_era_flavor_text(species_data, generation)
            
            self.db.execute("""
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
                type_id = self._get_type_id(type_entry['type']['name'])
                if type_id:
                    self.db.execute("""
                        INSERT OR REPLACE INTO pokemon_types (pokemon_id, type_id, slot)
                        VALUES (?, ?, ?)
                    """, (pokemon_id, type_id, type_entry['slot']))
                    
            # Insert stats
            for stat_entry in pokemon_data.get('stats', []):
                stat_id = self._get_stat_id(stat_entry['stat']['name'])
                if stat_id:
                    self.db.execute("""
                        INSERT OR REPLACE INTO pokemon_stats (pokemon_id, stat_id, base_stat, effort)
                        VALUES (?, ?, ?, ?)
                    """, (
                        pokemon_id,
                        stat_id,
                        stat_entry['base_stat'],
                        stat_entry['effort']
                    ))
                    
            # Insert abilities
            for ability_entry in pokemon_data.get('abilities', []):
                ability_name = ability_entry['ability']['name']
                is_hidden = ability_entry.get('is_hidden', False)
                slot = ability_entry['slot']
                
                # Get or create ability
                ability_data = self.fetch_json(ability_entry['ability']['url'])
                if ability_data:
                    ability_id = ability_data['id']
                    
                    self.db.execute("""
                        INSERT OR IGNORE INTO abilities (id, name)
                        VALUES (?, ?)
                    """, (ability_id, ability_name))
                    
                    self.db.execute("""
                        INSERT OR REPLACE INTO pokemon_abilities 
                        (pokemon_id, ability_id, is_hidden, slot)
                        VALUES (?, ?, ?, ?)
                    """, (pokemon_id, ability_id, is_hidden, slot))
                    
            self.db.commit()
            print(f"Done ({pokemon_data['name']})")
            
        print(f"Pokémon {start_id}-{end_id} loaded successfully")
        
    def load_evolutions(self, start_id: int = 1, end_id: int = 386):
        """
        Load evolution chains for Pokémon range
        
        Args:
            start_id: Starting Pokémon ID
            end_id: Ending Pokémon ID
        """
        print(f"Loading evolutions for Pokémon {start_id} to {end_id}...")
        
        processed_chains = set()
        
        for pokemon_id in range(start_id, end_id + 1):
            print(f"Checking evolutions for #{pokemon_id}...", end=' ')
            
            # Get species data
            species_url = f"{self.BASE_URL}/pokemon-species/{pokemon_id}"
            species_data = self.fetch_json(species_url)
            
            if not species_data or not species_data.get('evolution_chain'):
                print("No evolution data")
                continue
                
            chain_url = species_data['evolution_chain']['url']
            chain_id = int(chain_url.rstrip('/').split('/')[-1])
            
            # Skip if we've already processed this chain
            if chain_id in processed_chains:
                print("Already processed")
                continue
                
            chain_data = self.fetch_json(chain_url)
            if not chain_data:
                print("Failed to fetch chain")
                continue
                
            # Insert evolution chain
            self.db.execute("""
                INSERT OR IGNORE INTO evolution_chains (id)
                VALUES (?)
            """, (chain_id,))
            
            # Process evolution chain recursively
            self._process_evolution_chain(chain_id, chain_data['chain'], None)
            
            processed_chains.add(chain_id)
            self.db.commit()
            print("Done")
            
        print("Evolutions loaded successfully")
        
    def _process_evolution_chain(self, chain_id: int, chain_link: Dict, from_pokemon_id: Optional[int]):
        """
        Recursively process evolution chain
        
        Args:
            chain_id: Evolution chain ID
            chain_link: Chain link data from API
            from_pokemon_id: ID of the Pokémon this evolves from (None for base)
        """
        # Get current Pokémon ID from species URL
        species_url = chain_link['species']['url']
        to_pokemon_id = int(species_url.rstrip('/').split('/')[-1])
        
        # Only process Gen 1-3 Pokémon
        if to_pokemon_id > 386:
            return
            
        # If there's a previous Pokémon, create evolution entry
        if from_pokemon_id is not None:
            for evolution_detail in chain_link.get('evolution_details', []):
                trigger = evolution_detail.get('trigger', {}).get('name')
                min_level = evolution_detail.get('min_level')
                item = evolution_detail.get('item', {}).get('name') if evolution_detail.get('item') else None
                min_happiness = evolution_detail.get('min_happiness')
                time_of_day = evolution_detail.get('time_of_day') or None
                
                self.db.execute("""
                    INSERT OR IGNORE INTO evolutions 
                    (evolution_chain_id, from_pokemon_id, to_pokemon_id, min_level, 
                     trigger, item, min_happiness, time_of_day)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    chain_id,
                    from_pokemon_id,
                    to_pokemon_id,
                    min_level,
                    trigger,
                    item,
                    min_happiness,
                    time_of_day
                ))
                
        # Process next evolutions
        for evolves_to in chain_link.get('evolves_to', []):
            self._process_evolution_chain(chain_id, evolves_to, to_pokemon_id)
            
    def _get_type_id(self, type_name: str) -> Optional[int]:
        """Get type ID by name"""
        cursor = self.db.execute("SELECT id FROM types WHERE name = ?", (type_name,))
        row = cursor.fetchone()
        return row[0] if row else None
        
    def _get_stat_id(self, stat_name: str) -> Optional[int]:
        """Get stat ID by name"""
        cursor = self.db.execute("SELECT id FROM stats WHERE name = ?", (stat_name,))
        row = cursor.fetchone()
        return row[0] if row else None
    
    def _clean_flavor_text(self, text: str) -> str:
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
    
    def _get_era_flavor_text(self, species_data: Dict, generation: int) -> Optional[str]:
        """Extract era-appropriate English flavor text for a Pokémon.
        
        Prefers games from the Pokémon's original generation.
        
        Args:
            species_data: Species data from PokéAPI
            generation: The Pokémon's generation (1, 2, or 3)
            
        Returns:
            Cleaned flavor text string, or None if not found
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
                    return self._clean_flavor_text(entry['flavor_text'])
        
        # Fallback: use any English entry (prefer earlier ones)
        return self._clean_flavor_text(english_entries[0]['flavor_text'])
        
    def load_all_gen1_to_3(self):
        """Load all data for Gen 1-3 (Pokémon #1-386)"""
        print("Starting full Gen 1-3 data load...")
        print("=" * 60)
        
        self.load_types()
        self.load_stats()
        self.load_pokemon(1, 386)
        self.load_evolutions(1, 386)
        
        print("=" * 60)
        print("Gen 1-3 data load complete!")
