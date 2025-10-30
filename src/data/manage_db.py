#!/usr/bin/env python3
"""
Database management CLI for ShokeDex
Provides commands to initialize, seed, and manage the database
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.database import Database
from src.data.loader import PokemonDataLoader
from src.data.migrations import MigrationManager


def init_database(args):
    """Initialize database schema"""
    print("Initializing database...")
    
    with Database(args.db_path) as db:
        db.create_schema()
        version = db.get_schema_version()
        print(f"Database initialized successfully (schema version: {version})")


def seed_database(args):
    """Seed database with Pokémon data"""
    print("Seeding database...")
    
    with Database(args.db_path) as db:
        loader = PokemonDataLoader(db, rate_limit_delay=args.delay)
        
        if args.gen == 'all' or args.gen == '1-3':
            loader.load_all_gen1_to_3()
        elif args.gen == '1':
            loader.load_types()
            loader.load_stats()
            loader.load_pokemon(1, 151)
            loader.load_evolutions(1, 151)
        elif args.gen == '2':
            loader.load_types()
            loader.load_stats()
            loader.load_pokemon(152, 251)
            loader.load_evolutions(152, 251)
        elif args.gen == '3':
            loader.load_types()
            loader.load_stats()
            loader.load_pokemon(252, 386)
            loader.load_evolutions(252, 386)
        else:
            print(f"Unknown generation: {args.gen}")
            return
            
    print("Database seeded successfully")


def show_stats(args):
    """Show database statistics"""
    with Database(args.db_path) as db:
        version = db.get_schema_version()
        print(f"Schema version: {version}")
        print()
        
        # Count Pokémon by generation
        print("Pokémon count by generation:")
        for gen in range(1, 4):
            cursor = db.execute("SELECT COUNT(*) FROM pokemon WHERE generation = ?", (gen,))
            count = cursor.fetchone()[0]
            print(f"  Gen {gen}: {count}")
            
        # Total counts
        tables = ['pokemon', 'types', 'stats', 'abilities', 'evolution_chains', 'evolutions']
        print("\nTotal counts:")
        for table in tables:
            cursor = db.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count}")


def query_pokemon(args):
    """Query Pokémon information"""
    with Database(args.db_path) as db:
        if args.id:
            pokemon = db.get_pokemon_by_id(args.id)
        elif args.name:
            pokemon = db.get_pokemon_by_name(args.name)
        else:
            print("Please specify --id or --name")
            return
            
        if not pokemon:
            print("Pokémon not found")
            return
            
        print(f"\nPokémon #{pokemon['id']}: {pokemon['name'].title()}")
        print(f"  Generation: {pokemon['generation']}")
        print(f"  Height: {pokemon['height']} dm")
        print(f"  Weight: {pokemon['weight']} hg")
        print(f"  Base Experience: {pokemon['base_experience']}")
        print(f"  Types: {pokemon['types']}")
        
        # Get stats
        stats = db.get_pokemon_stats(pokemon['id'])
        if stats:
            print("\n  Base Stats:")
            for stat in stats:
                print(f"    {stat['name']}: {stat['base_stat']}")
                
        # Get evolutions
        evolutions = db.get_evolutions(pokemon['id'])
        if evolutions:
            print("\n  Evolutions:")
            for evo in evolutions:
                if evo['from_name']:
                    print(f"    {evo['from_name'].title()} → {evo['to_name'].title()}", end='')
                else:
                    print(f"    Base → {evo['to_name'].title()}", end='')
                    
                if evo['min_level']:
                    print(f" (Level {evo['min_level']})", end='')
                if evo['item']:
                    print(f" (Item: {evo['item']})", end='')
                print()


def migrate_database(args):
    """Run database migrations"""
    with Database(args.db_path) as db:
        manager = MigrationManager(db)
        # Register migrations here if needed
        manager.apply_all_pending()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Database management tool for ShokeDex',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize database
  python manage_db.py init
  
  # Seed with all Gen 1-3 data
  python manage_db.py seed --gen 1-3
  
  # Seed only Gen 1
  python manage_db.py seed --gen 1
  
  # Show database statistics
  python manage_db.py stats
  
  # Query a Pokémon
  python manage_db.py query --id 25
  python manage_db.py query --name pikachu
        """
    )
    
    parser.add_argument(
        '--db-path',
        help='Path to database file (default: data/pokedex.db)',
        default=None
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize database schema')
    
    # Seed command
    seed_parser = subparsers.add_parser('seed', help='Seed database with Pokémon data')
    seed_parser.add_argument(
        '--gen',
        choices=['1', '2', '3', '1-3', 'all'],
        default='1-3',
        help='Generation(s) to load (default: 1-3)'
    )
    seed_parser.add_argument(
        '--delay',
        type=float,
        default=0.1,
        help='Delay between API requests in seconds (default: 0.1)'
    )
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show database statistics')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query Pokémon information')
    query_group = query_parser.add_mutually_exclusive_group(required=True)
    query_group.add_argument('--id', type=int, help='Pokémon ID')
    query_group.add_argument('--name', help='Pokémon name')
    
    # Migrate command
    migrate_parser = subparsers.add_parser('migrate', help='Run database migrations')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    # Execute command
    commands = {
        'init': init_database,
        'seed': seed_database,
        'stats': show_stats,
        'query': query_pokemon,
        'migrate': migrate_database
    }
    
    try:
        commands[args.command](args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
