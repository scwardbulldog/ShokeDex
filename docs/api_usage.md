# API Usage Guide

## PokéAPI Integration

ShokeDex will use the [PokéAPI](https://pokeapi.co/) to fetch Pokémon data.

## Coming Soon

Detailed API integration documentation will be added as the project develops.

## Endpoints

- Pokémon details: `https://pokeapi.co/api/v2/pokemon/{id}`
- Pokémon species: `https://pokeapi.co/api/v2/pokemon-species/{id}`
- Sprites and images
- Evolution chains
- Types and abilities

## Rate Limiting

PokéAPI is free and does not require authentication, but please be respectful:
- Cache data locally when possible
- Implement reasonable request delays
- Use the SQLite database to store frequently accessed data
