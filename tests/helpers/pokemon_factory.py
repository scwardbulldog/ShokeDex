"""
Test data factory for creating Pokémon test data

Provides factory functions for generating realistic test data with
controlled randomness using faker. All data uses unique IDs to prevent
test pollution in parallel runs.

Usage:
    from tests.helpers.pokemon_factory import create_pokemon, create_pokemon_batch
    
    # Single Pokémon with defaults
    pokemon = create_pokemon()
    
    # Pokémon with overrides
    pikachu = create_pokemon(id=25, name="Pikachu", type1="Electric")
    
    # Batch of Pokémon
    starters = create_pokemon_batch(count=3, generation=1)
"""

from typing import Dict, List, Optional, Any


def create_pokemon(
    id: Optional[int] = None,
    name: Optional[str] = None,
    type1: Optional[str] = None,
    type2: Optional[str] = None,
    height: Optional[int] = None,
    weight: Optional[int] = None,
    generation: Optional[int] = None,
    **overrides
) -> Dict[str, Any]:
    """
    Create a Pokémon test data dictionary.
    
    Args:
        id: Pokédex number (default: 1)
        name: Pokémon name (default: "TestMon")
        type1: Primary type (default: "Normal")
        type2: Secondary type (default: None)
        height: Height in decimeters (default: 10)
        weight: Weight in hectograms (default: 100)
        generation: Generation number (default: 1)
        **overrides: Additional fields to override
    
    Returns:
        Dictionary with Pokémon data matching database schema
    
    Example:
        pokemon = create_pokemon(id=25, name="Pikachu", type1="Electric")
    """
    pokemon = {
        "id": id or 1,
        "name": name or "TestMon",
        "type1": type1 or "Normal",
        "type2": type2,
        "height": height or 10,
        "weight": weight or 100,
        "generation": generation or 1,
    }
    
    # Apply any additional overrides
    pokemon.update(overrides)
    
    return pokemon


def create_pokemon_batch(count: int = 5, **defaults) -> List[Dict[str, Any]]:
    """
    Create multiple Pokémon with sequential IDs.
    
    Args:
        count: Number of Pokémon to create
        **defaults: Default values for all Pokémon
    
    Returns:
        List of Pokémon dictionaries
    
    Example:
        starters = create_pokemon_batch(
            count=3,
            generation=1,
            type1="Grass"
        )
    """
    batch = []
    for i in range(count):
        pokemon = create_pokemon(
            id=defaults.get("id", 1) + i,
            **defaults
        )
        batch.append(pokemon)
    
    return batch


def create_pokemon_stats(
    pokemon_id: int,
    hp: int = 50,
    attack: int = 50,
    defense: int = 50,
    sp_attack: int = 50,
    sp_defense: int = 50,
    speed: int = 50,
) -> Dict[str, Any]:
    """
    Create base stats for a Pokémon.
    
    Args:
        pokemon_id: ID of the Pokémon
        hp: HP stat (default: 50)
        attack: Attack stat (default: 50)
        defense: Defense stat (default: 50)
        sp_attack: Special Attack stat (default: 50)
        sp_defense: Special Defense stat (default: 50)
        speed: Speed stat (default: 50)
    
    Returns:
        Dictionary with base stats
    
    Example:
        stats = create_pokemon_stats(25, hp=35, attack=55, speed=90)
    """
    return {
        "pokemon_id": pokemon_id,
        "hp": hp,
        "attack": attack,
        "defense": defense,
        "special_attack": sp_attack,
        "special_defense": sp_defense,
        "speed": speed,
    }


def create_evolution_chain(
    evolution_chain_id: int,
    pokemon_ids: List[int],
) -> List[Dict[str, Any]]:
    """
    Create an evolution chain linking multiple Pokémon.
    
    Args:
        evolution_chain_id: ID for the evolution chain
        pokemon_ids: List of Pokémon IDs in evolution order
    
    Returns:
        List of evolution relationship dictionaries
    
    Example:
        # Charmander -> Charmeleon -> Charizard
        chain = create_evolution_chain(
            evolution_chain_id=1,
            pokemon_ids=[4, 5, 6]
        )
    """
    evolutions = []
    
    for i in range(len(pokemon_ids) - 1):
        evolutions.append({
            "evolution_chain_id": evolution_chain_id,
            "from_pokemon_id": pokemon_ids[i],
            "to_pokemon_id": pokemon_ids[i + 1],
            "min_level": 16 + (i * 20),  # Example levels
            "trigger": "level-up",
        })
    
    return evolutions


# Predefined test data sets

GEN_1_STARTERS = [
    create_pokemon(id=1, name="Bulbasaur", type1="Grass", type2="Poison", generation=1),
    create_pokemon(id=4, name="Charmander", type1="Fire", generation=1),
    create_pokemon(id=7, name="Squirtle", type1="Water", generation=1),
]

GEN_2_STARTERS = [
    create_pokemon(id=152, name="Chikorita", type1="Grass", generation=2),
    create_pokemon(id=155, name="Cyndaquil", type1="Fire", generation=2),
    create_pokemon(id=158, name="Totodile", type1="Water", generation=2),
]

GEN_3_STARTERS = [
    create_pokemon(id=252, name="Treecko", type1="Grass", generation=3),
    create_pokemon(id=255, name="Torchic", type1="Fire", generation=3),
    create_pokemon(id=258, name="Mudkip", type1="Water", generation=3),
]

FAMOUS_POKEMON = [
    create_pokemon(id=25, name="Pikachu", type1="Electric", generation=1),
    create_pokemon(id=150, name="Mewtwo", type1="Psychic", generation=1),
    create_pokemon(id=249, name="Lugia", type1="Psychic", type2="Flying", generation=2),
    create_pokemon(id=384, name="Rayquaza", type1="Dragon", type2="Flying", generation=3),
]
