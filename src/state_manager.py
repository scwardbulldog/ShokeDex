"""
State Manager for ShokeDex - Handles application state persistence

Manages:
- Last viewed Pokémon (for startup restoration)
- Favorites/recently viewed
- User preferences
- Session state

Uses simple JSON file for storage.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any


class StateManager:
    """
    Manages persistent application state across sessions.
    
    State is stored in a simple JSON file, making it easy to:
    - Backup/restore user data
    - Inspect/debug state manually
    - Transfer between devices
    """
    
    # Default state file location
    DEFAULT_STATE_FILE = "data/shokedex_state.json"
    
    # Current state version (for future migration support)
    STATE_VERSION = "1.0.0"
    
    def __init__(self, state_file: Optional[str] = None):
        """
        Initialize StateManager.
        
        Args:
            state_file: Path to state file (uses default if None)
        """
        self.state_file = Path(state_file or self.DEFAULT_STATE_FILE)
        self.state: Dict[str, Any] = self._load_state()
    
    def _get_default_state(self) -> Dict[str, Any]:
        """Get default state structure."""
        return {
            "version": self.STATE_VERSION,
            "last_viewed": {
                "pokemon_id": 1,  # Start with Bulbasaur
                "generation": 1,  # Kanto
            },
            "favorites": [],
            "recent": [],  # Last 10 viewed Pokémon
            "preferences": {
                "input_mode": "keyboard",
                "volume": 0.7,
            },
            "stats": {
                "total_views": 0,
                "unique_viewed": 0,
                "sessions": 0,
            }
        }
    
    def _load_state(self) -> Dict[str, Any]:
        """
        Load state from JSON file.
        
        Returns:
            State dictionary (default if file doesn't exist)
        """
        if not self.state_file.exists():
            return self._get_default_state()
        
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
                
            # Validate version (simple check for now)
            if state.get('version') != self.STATE_VERSION:
                print(f"Warning: State version mismatch. Expected {self.STATE_VERSION}, got {state.get('version')}")
                # Could trigger migration here in the future
            
            # Validate and clamp values (Story 1.5: AC #6)
            needs_correction = False
            
            # Validate last_viewed section
            if 'last_viewed' in state:
                # Clamp pokemon_id to valid range (1-386)
                if 'pokemon_id' in state['last_viewed']:
                    original_id = state['last_viewed']['pokemon_id']
                    state['last_viewed']['pokemon_id'] = max(1, min(386, original_id))
                    if state['last_viewed']['pokemon_id'] != original_id:
                        print(f"Warning: pokemon_id {original_id} out of range, clamped to {state['last_viewed']['pokemon_id']}")
                        needs_correction = True
                
                # Clamp generation to valid range (1-3)
                if 'generation' in state['last_viewed']:
                    original_gen = state['last_viewed']['generation']
                    state['last_viewed']['generation'] = max(1, min(3, original_gen))
                    if state['last_viewed']['generation'] != original_gen:
                        print(f"Warning: generation {original_gen} out of range, clamped to {state['last_viewed']['generation']}")
                        needs_correction = True
            
            # Validate preferences section
            if 'preferences' in state:
                # Clamp volume to valid range (0.0-1.0)
                if 'volume' in state['preferences']:
                    original_volume = state['preferences']['volume']
                    state['preferences']['volume'] = max(0.0, min(1.0, float(original_volume)))
                    if abs(state['preferences']['volume'] - original_volume) > 0.001:
                        print(f"Warning: volume {original_volume} out of range, clamped to {state['preferences']['volume']}")
                        needs_correction = True
                
                # Validate input_mode
                if 'input_mode' in state['preferences']:
                    if state['preferences']['input_mode'] not in ('keyboard', 'gpio'):
                        print(f"Warning: invalid input_mode '{state['preferences']['input_mode']}', defaulting to 'keyboard'")
                        state['preferences']['input_mode'] = 'keyboard'
                        needs_correction = True
            
            # If we corrected values, save the corrected state back to file
            if needs_correction:
                try:
                    with open(self.state_file, 'w', encoding='utf-8') as f:
                        json.dump(state, f, indent=2, ensure_ascii=False)
                    print("Corrected state file saved")
                except IOError:
                    pass  # Don't fail on save error during load
            
            return state
            
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: State file corrupted, resetting to defaults - {e}")
            # Overwrite corrupt file with defaults
            default_state = self._get_default_state()
            try:
                self.state_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.state_file, 'w', encoding='utf-8') as f:
                    json.dump(default_state, f, indent=2, ensure_ascii=False)
            except IOError:
                pass  # Don't fail if we can't write defaults
            return default_state
    
    def save_state(self) -> bool:
        """
        Save current state to JSON file using atomic write pattern.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Atomic write pattern: write to temp file then rename (Story 1.5: AC #7)
            temp_file = Path(str(self.state_file) + '.tmp')
            
            # Write to temporary file
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
            
            # Atomic rename (POSIX systems guarantee atomicity)
            temp_file.replace(self.state_file)
            
            return True
            
        except IOError as e:
            print(f"Error saving state file: {e}")
            return False
    
    # Last Viewed Methods
    
    def get_last_viewed_id(self) -> int:
        """Get last viewed Pokémon ID."""
        return self.state['last_viewed']['pokemon_id']
    
    def get_last_viewed_generation(self) -> int:
        """Get last viewed generation (1, 2, or 3)."""
        return self.state['last_viewed']['generation']
    
    def set_last_viewed(self, pokemon_id: int, generation: Optional[int] = None):
        """
        Set last viewed Pokémon.
        
        Args:
            pokemon_id: Pokémon national dex number
            generation: Generation (auto-detected if None)
        """
        # Auto-detect generation if not provided
        if generation is None:
            if 1 <= pokemon_id <= 151:
                generation = 1
            elif 152 <= pokemon_id <= 251:
                generation = 2
            elif 252 <= pokemon_id <= 386:
                generation = 3
            else:
                generation = 1  # Default fallback
        
        self.state['last_viewed']['pokemon_id'] = pokemon_id
        self.state['last_viewed']['generation'] = generation
        
        # Update recents
        self._add_to_recent(pokemon_id)
        
        # Update stats
        self.state['stats']['total_views'] += 1
    
    # Favorites Methods
    
    def get_favorites(self) -> List[int]:
        """Get list of favorite Pokémon IDs."""
        return self.state['favorites'].copy()
    
    def is_favorite(self, pokemon_id: int) -> bool:
        """Check if Pokémon is in favorites."""
        return pokemon_id in self.state['favorites']
    
    def add_favorite(self, pokemon_id: int):
        """Add Pokémon to favorites."""
        if pokemon_id not in self.state['favorites']:
            self.state['favorites'].append(pokemon_id)
    
    def remove_favorite(self, pokemon_id: int):
        """Remove Pokémon from favorites."""
        if pokemon_id in self.state['favorites']:
            self.state['favorites'].remove(pokemon_id)
    
    def toggle_favorite(self, pokemon_id: int) -> bool:
        """
        Toggle favorite status.
        
        Returns:
            True if now favorited, False if unfavorited
        """
        if self.is_favorite(pokemon_id):
            self.remove_favorite(pokemon_id)
            return False
        else:
            self.add_favorite(pokemon_id)
            return True
    
    # Recent Methods
    
    def get_recent(self) -> List[int]:
        """Get list of recently viewed Pokémon IDs (newest first)."""
        return self.state['recent'].copy()
    
    def _add_to_recent(self, pokemon_id: int):
        """
        Add Pokémon to recent list (internal).
        
        Maintains max 10 recent items, newest first.
        """
        recent = self.state['recent']
        
        # Remove if already present
        if pokemon_id in recent:
            recent.remove(pokemon_id)
        
        # Add to front
        recent.insert(0, pokemon_id)
        
        # Keep only last 10
        self.state['recent'] = recent[:10]
    
    # Preferences Methods
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a preference value."""
        return self.state['preferences'].get(key, default)
    
    def set_preference(self, key: str, value: Any):
        """Set a preference value."""
        self.state['preferences'][key] = value
    
    def get_volume(self) -> float:
        """Get audio volume (0.0 to 1.0)."""
        return self.get_preference('volume', 0.7)
    
    def set_volume(self, volume: float):
        """Set audio volume (0.0 to 1.0)."""
        volume = max(0.0, min(1.0, volume))  # Clamp to valid range
        self.set_preference('volume', volume)
    
    def get_input_mode(self) -> str:
        """Get input mode ('keyboard' or 'gpio')."""
        return self.get_preference('input_mode', 'keyboard')
    
    def set_input_mode(self, mode: str):
        """Set input mode."""
        if mode in ('keyboard', 'gpio'):
            self.set_preference('input_mode', mode)
    
    # Stats Methods
    
    def get_stats(self) -> Dict[str, int]:
        """Get usage statistics."""
        return self.state['stats'].copy()
    
    def increment_session(self):
        """Increment session counter (call on app startup)."""
        self.state['stats']['sessions'] += 1
    
    def update_unique_viewed(self, count: int):
        """Update count of unique Pokémon viewed."""
        self.state['stats']['unique_viewed'] = count
    
    # Utility Methods
    
    def reset_state(self):
        """Reset to default state (clears all user data)."""
        self.state = self._get_default_state()
    
    def export_state(self) -> str:
        """Export state as JSON string."""
        return json.dumps(self.state, indent=2)
    
    def import_state(self, json_str: str) -> bool:
        """
        Import state from JSON string.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            state = json.loads(json_str)
            # Basic validation
            if 'version' in state and 'last_viewed' in state:
                self.state = state
                return True
            else:
                print("Invalid state format")
                return False
        except json.JSONDecodeError as e:
            print(f"Error parsing state JSON: {e}")
            return False
