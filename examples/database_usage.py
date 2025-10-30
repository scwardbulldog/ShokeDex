#!/usr/bin/env python3
"""
Example: Using the ShokeDex database module

This script demonstrates how to use the database module to query Pokémon data.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.database import Database


def example_query_pokemon():
    """Example: Query a Pokémon by ID or name"""
    print("=" * 60)
    print("Example 1: Query Pokémon")
    print("=" * 60)
    
    with Database() as db:
        # Query by ID
        pokemon = db.get_pokemon_by_id(25)
        if pokemon:
            print(f"\nPokémon #{pokemon['id']}: {pokemon['name'].title()}")
            print(f"  Types: {pokemon['types']}")
            print(f"  Height: {pokemon['height']} dm")
            print(f"  Weight: {pokemon['weight']} hg")
            print(f"  Generation: {pokemon['generation']}")
        else:
            print("\nPokémon #25 not found. Have you seeded the database?")
            print("Run: python src/data/manage_db.py seed --gen 1")


def example_query_stats():
    """Example: Query Pokémon stats"""
    print("\n" + "=" * 60)
    print("Example 2: Query Pokémon Stats")
    print("=" * 60)
    
    with Database() as db:
        stats = db.get_pokemon_stats(25)
        if stats:
            print("\nPikachu's Base Stats:")
            for stat in stats:
                print(f"  {stat['name'].replace('-', ' ').title()}: {stat['base_stat']}")
        else:
            print("\nNo stats found. Database may not be seeded.")


def example_query_by_generation():
    """Example: Query Pokémon by generation"""
    print("\n" + "=" * 60)
    print("Example 3: Query by Generation")
    print("=" * 60)
    
    with Database() as db:
        gen1_pokemon = db.get_pokemon_by_generation(1)
        print(f"\nFound {len(gen1_pokemon)} Generation 1 Pokémon")
        
        if gen1_pokemon:
            print("\nFirst 10 Gen 1 Pokémon:")
            for pokemon in gen1_pokemon[:10]:
                print(f"  #{pokemon['id']}: {pokemon['name'].title()}")


def example_query_evolutions():
    """Example: Query evolution chain"""
    print("\n" + "=" * 60)
    print("Example 4: Query Evolution Chain")
    print("=" * 60)
    
    with Database() as db:
        # Get Pikachu
        pokemon = db.get_pokemon_by_name('pikachu')
        if pokemon:
            print(f"\nEvolution chain for {pokemon['name'].title()}:")
            evolutions = db.get_evolutions(pokemon['id'])
            
            if evolutions:
                for evo in evolutions:
                    from_name = evo['from_name'].title() if evo['from_name'] else "Base"
                    to_name = evo['to_name'].title()
                    
                    print(f"  {from_name} → {to_name}", end='')
                    
                    details = []
                    if evo['min_level']:
                        details.append(f"Level {evo['min_level']}")
                    if evo['item']:
                        details.append(f"Item: {evo['item']}")
                    if evo['trigger']:
                        details.append(f"Trigger: {evo['trigger']}")
                    
                    if details:
                        print(f" ({', '.join(details)})")
                    else:
                        print()
            else:
                print("  No evolution data found")
        else:
            print("\nPokémon not found. Database may not be seeded.")


def example_custom_query():
    """Example: Custom SQL query"""
    print("\n" + "=" * 60)
    print("Example 5: Custom Query")
    print("=" * 60)
    
    with Database() as db:
        # Find all Electric-type Pokémon
        cursor = db.execute("""
            SELECT DISTINCT p.id, p.name
            FROM pokemon p
            JOIN pokemon_types pt ON p.id = pt.pokemon_id
            JOIN types t ON pt.type_id = t.id
            WHERE t.name = 'electric'
            ORDER BY p.id
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        if results:
            print("\nFirst 10 Electric-type Pokémon:")
            for row in results:
                print(f"  #{row[0]}: {row[1].title()}")
        else:
            print("\nNo Electric-type Pokémon found. Database may not be seeded.")


def example_database_stats():
    """Example: Get database statistics"""
    print("\n" + "=" * 60)
    print("Example 6: Database Statistics")
    print("=" * 60)
    
    with Database() as db:
        # Count total Pokémon
        cursor = db.execute("SELECT COUNT(*) FROM pokemon")
        total_pokemon = cursor.fetchone()[0]
        
        print(f"\nTotal Pokémon in database: {total_pokemon}")
        
        if total_pokemon > 0:
            # Count by generation
            print("\nPokémon by Generation:")
            for gen in range(1, 4):
                cursor = db.execute(
                    "SELECT COUNT(*) FROM pokemon WHERE generation = ?",
                    (gen,)
                )
                count = cursor.fetchone()[0]
                print(f"  Generation {gen}: {count}")
            
            # Count types
            cursor = db.execute("SELECT COUNT(*) FROM types")
            type_count = cursor.fetchone()[0]
            print(f"\nTotal types: {type_count}")
            
            # Count abilities
            cursor = db.execute("SELECT COUNT(*) FROM abilities")
            ability_count = cursor.fetchone()[0]
            print(f"Total abilities: {ability_count}")
        else:
            print("\nDatabase is empty. Run: python src/data/manage_db.py seed --gen 1-3")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("ShokeDex Database Usage Examples")
    print("=" * 60)
    
    # Check if database exists
    db = Database()
    import os
    if not os.path.exists(db.db_path):
        print("\n⚠ Database not found!")
        print("\nPlease initialize and seed the database first:")
        print("  1. python src/data/manage_db.py init")
        print("  2. python src/data/manage_db.py seed --gen 1-3")
        return
    
    try:
        example_database_stats()
        example_query_pokemon()
        example_query_stats()
        example_query_by_generation()
        example_query_evolutions()
        example_custom_query()
        
        print("\n" + "=" * 60)
        print("Examples completed!")
        print("=" * 60)
        print("\nFor more information, see:")
        print("  - docs/database_schema.md")
        print("  - docs/data_loading_guide.md")
        print("  - src/data/README.md")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure the database is initialized and seeded:")
        print("  python src/data/manage_db.py init")
        print("  python src/data/manage_db.py seed --gen 1-3")


if __name__ == '__main__':
    main()
