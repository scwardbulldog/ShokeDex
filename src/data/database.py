"""
Database module for ShokeDex
Manages SQLite database schema and operations for Pokémon data
"""

import sqlite3
import os
from typing import Optional, List, Dict, Any
from pathlib import Path


class Database:
    """Manages SQLite database connections and operations"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file. If None, uses default location.
        """
        if db_path is None:
            # Default to data directory in project root
            project_root = Path(__file__).parent.parent.parent
            data_dir = project_root / "data"
            data_dir.mkdir(exist_ok=True)
            db_path = str(data_dir / "pokedex.db")
        
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        
    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        
    def create_schema(self):
        """Create database schema for Pokémon data"""
        if not self.conn:
            raise RuntimeError("Database not connected")
            
        cursor = self.conn.cursor()
        
        # Create types table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS types (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create pokemon table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pokemon (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                species_id INTEGER NOT NULL,
                height INTEGER NOT NULL,
                weight INTEGER NOT NULL,
                base_experience INTEGER,
                generation INTEGER NOT NULL,
                is_default BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create pokemon_types junction table (many-to-many)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pokemon_types (
                pokemon_id INTEGER NOT NULL,
                type_id INTEGER NOT NULL,
                slot INTEGER NOT NULL,
                PRIMARY KEY (pokemon_id, type_id),
                FOREIGN KEY (pokemon_id) REFERENCES pokemon(id) ON DELETE CASCADE,
                FOREIGN KEY (type_id) REFERENCES types(id) ON DELETE CASCADE
            )
        """)
        
        # Create stats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create pokemon_stats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pokemon_stats (
                pokemon_id INTEGER NOT NULL,
                stat_id INTEGER NOT NULL,
                base_stat INTEGER NOT NULL,
                effort INTEGER DEFAULT 0,
                PRIMARY KEY (pokemon_id, stat_id),
                FOREIGN KEY (pokemon_id) REFERENCES pokemon(id) ON DELETE CASCADE,
                FOREIGN KEY (stat_id) REFERENCES stats(id) ON DELETE CASCADE
            )
        """)
        
        # Create evolution_chains table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evolution_chains (
                id INTEGER PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create evolutions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evolutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evolution_chain_id INTEGER NOT NULL,
                from_pokemon_id INTEGER,
                to_pokemon_id INTEGER NOT NULL,
                min_level INTEGER,
                trigger TEXT,
                item TEXT,
                min_happiness INTEGER,
                time_of_day TEXT,
                min_beauty INTEGER,
                min_affection INTEGER,
                relative_physical_stats INTEGER,
                party_species_id INTEGER,
                party_type_id INTEGER,
                trade_species_id INTEGER,
                needs_overworld_rain BOOLEAN DEFAULT 0,
                turn_upside_down BOOLEAN DEFAULT 0,
                FOREIGN KEY (evolution_chain_id) REFERENCES evolution_chains(id) ON DELETE CASCADE,
                FOREIGN KEY (from_pokemon_id) REFERENCES pokemon(id) ON DELETE SET NULL,
                FOREIGN KEY (to_pokemon_id) REFERENCES pokemon(id) ON DELETE CASCADE,
                UNIQUE(evolution_chain_id, from_pokemon_id, to_pokemon_id)
            )
        """)
        
        # Create abilities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS abilities (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                is_hidden BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create pokemon_abilities junction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pokemon_abilities (
                pokemon_id INTEGER NOT NULL,
                ability_id INTEGER NOT NULL,
                is_hidden BOOLEAN DEFAULT 0,
                slot INTEGER NOT NULL,
                PRIMARY KEY (pokemon_id, ability_id),
                FOREIGN KEY (pokemon_id) REFERENCES pokemon(id) ON DELETE CASCADE,
                FOREIGN KEY (ability_id) REFERENCES abilities(id) ON DELETE CASCADE
            )
        """)
        
        # Create moves table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS moves (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                type_id INTEGER,
                power INTEGER,
                pp INTEGER,
                accuracy INTEGER,
                priority INTEGER DEFAULT 0,
                damage_class TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (type_id) REFERENCES types(id) ON DELETE SET NULL
            )
        """)
        
        # Create pokemon_moves junction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pokemon_moves (
                pokemon_id INTEGER NOT NULL,
                move_id INTEGER NOT NULL,
                level_learned_at INTEGER DEFAULT 0,
                move_learn_method TEXT NOT NULL,
                PRIMARY KEY (pokemon_id, move_id, move_learn_method),
                FOREIGN KEY (pokemon_id) REFERENCES pokemon(id) ON DELETE CASCADE,
                FOREIGN KEY (move_id) REFERENCES moves(id) ON DELETE CASCADE
            )
        """)
        
        # Create schema_version table for migrations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            )
        """)
        
        # Insert initial schema version
        cursor.execute("""
            INSERT OR IGNORE INTO schema_version (version, description)
            VALUES (1, 'Initial schema with pokemon, types, stats, evolutions, abilities, and moves')
        """)
        
        # Create indexes for better query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pokemon_name ON pokemon(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pokemon_generation ON pokemon(generation)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pokemon_types_pokemon ON pokemon_types(pokemon_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pokemon_types_type ON pokemon_types(type_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pokemon_stats_pokemon ON pokemon_stats(pokemon_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_evolutions_chain ON evolutions(evolution_chain_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_evolutions_from ON evolutions(from_pokemon_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_evolutions_to ON evolutions(to_pokemon_id)")
        
        self.conn.commit()
        
    def get_schema_version(self) -> int:
        """Get current schema version"""
        if not self.conn:
            raise RuntimeError("Database not connected")
            
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT MAX(version) FROM schema_version")
            result = cursor.fetchone()
            return result[0] if result[0] is not None else 0
        except sqlite3.OperationalError:
            return 0
            
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query"""
        if not self.conn:
            raise RuntimeError("Database not connected")
        return self.conn.cursor().execute(query, params)
        
    def executemany(self, query: str, params_list: List[tuple]):
        """Execute a query with multiple parameter sets"""
        if not self.conn:
            raise RuntimeError("Database not connected")
        self.conn.cursor().executemany(query, params_list)
        
    def commit(self):
        """Commit current transaction"""
        if not self.conn:
            raise RuntimeError("Database not connected")
        self.conn.commit()
        
    def get_pokemon_by_id(self, pokemon_id: int) -> Optional[Dict[str, Any]]:
        """Get Pokémon by ID with all related data"""
        cursor = self.execute("""
            SELECT p.*, GROUP_CONCAT(DISTINCT t.name) as types
            FROM pokemon p
            LEFT JOIN pokemon_types pt ON p.id = pt.pokemon_id
            LEFT JOIN types t ON pt.type_id = t.id
            WHERE p.id = ?
            GROUP BY p.id
        """, (pokemon_id,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
        
    def get_pokemon_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get Pokémon by name"""
        cursor = self.execute("""
            SELECT p.*, GROUP_CONCAT(DISTINCT t.name) as types
            FROM pokemon p
            LEFT JOIN pokemon_types pt ON p.id = pt.pokemon_id
            LEFT JOIN types t ON pt.type_id = t.id
            WHERE LOWER(p.name) = LOWER(?)
            GROUP BY p.id
        """, (name,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
        
    def get_pokemon_stats(self, pokemon_id: int) -> List[Dict[str, Any]]:
        """Get stats for a Pokémon"""
        cursor = self.execute("""
            SELECT s.name, ps.base_stat, ps.effort
            FROM pokemon_stats ps
            JOIN stats s ON ps.stat_id = s.id
            WHERE ps.pokemon_id = ?
            ORDER BY s.id
        """, (pokemon_id,))
        
        return [dict(row) for row in cursor.fetchall()]
        
    def get_pokemon_by_generation(self, generation: int) -> List[Dict[str, Any]]:
        """
        Get all Pokémon from a specific generation using ID ranges.
        
        Args:
            generation: Generation number (1, 2, or 3)
                       1 = Kanto (#1-151)
                       2 = Johto (#152-251)
                       3 = Hoenn (#252-386)
        
        Returns:
            List of dicts with Pokemon data including types
        
        Raises:
            ValueError: If generation not in range 1-3
        """
        # Generation ranges per architecture decision ADR-005
        GENERATION_RANGES = {
            1: (1, 151),    # Kanto: Bulbasaur to Mew
            2: (152, 251),  # Johto: Chikorita to Celebi
            3: (252, 386)   # Hoenn: Treecko to Deoxys
        }
        
        # Validate generation parameter
        if generation not in GENERATION_RANGES:
            raise ValueError(f"Invalid generation: {generation}. Must be 1, 2, or 3.")
        
        start_id, end_id = GENERATION_RANGES[generation]
        
        # Use parameterized BETWEEN query for security and performance
        cursor = self.execute("""
            SELECT p.*, GROUP_CONCAT(DISTINCT t.name) as types
            FROM pokemon p
            LEFT JOIN pokemon_types pt ON p.id = pt.pokemon_id
            LEFT JOIN types t ON pt.type_id = t.id
            WHERE p.id BETWEEN ? AND ?
            GROUP BY p.id
            ORDER BY p.id
        """, (start_id, end_id))
        
        return [dict(row) for row in cursor.fetchall()]
        
    def get_evolutions(self, pokemon_id: int) -> List[Dict[str, Any]]:
        """Get evolution chain for a Pokémon"""
        cursor = self.execute("""
            SELECT e.*, p1.name as from_name, p2.name as to_name
            FROM evolutions e
            LEFT JOIN pokemon p1 ON e.from_pokemon_id = p1.id
            JOIN pokemon p2 ON e.to_pokemon_id = p2.id
            WHERE e.from_pokemon_id = ? OR e.to_pokemon_id = ?
            ORDER BY e.min_level
        """, (pokemon_id, pokemon_id))
        
        return [dict(row) for row in cursor.fetchall()]
