"""
Audio Manager for ShokeDex - Handles Pokémon cries and sound effects

Manages:
- Pokémon cry playback
- Volume control
- Lazy loading of audio files
- pygame.mixer configuration

Audio files expected at: assets/audio/cries/{pokemon_id:03d}.ogg
"""

import pygame
from pathlib import Path
from typing import Optional, Dict


class AudioManager:
    """
    Manages audio playback for ShokeDex.
    
    Features:
    - Lazy-load audio files (load on demand, not all at once)
    - Cache recently used cries in memory
    - Volume control
    - Clean error handling for missing files
    """
    
    # Audio file configuration
    DEFAULT_CRIES_DIR = "assets/audio/cries"
    AUDIO_FORMAT = "ogg"  # OGG Vorbis (compressed, good for Pi)
    MAX_CACHE_SIZE = 20  # Keep last 20 cries in memory
    
    def __init__(
        self, 
        cries_dir: Optional[str] = None,
        volume: float = 0.7,
        enabled: bool = True
    ):
        """
        Initialize AudioManager.
        
        Args:
            cries_dir: Directory containing cry audio files
            volume: Initial volume (0.0 to 1.0)
            enabled: Whether audio is enabled
        """
        self.cries_dir = Path(cries_dir or self.DEFAULT_CRIES_DIR)
        self.volume = max(0.0, min(1.0, volume))  # Clamp to valid range
        self.enabled = enabled
        
        # Audio cache (pokemon_id -> pygame.mixer.Sound)
        self.cache: Dict[int, pygame.mixer.Sound] = {}
        self.cache_order: list = []  # Track access order for LRU eviction
        
        # Initialize pygame mixer if enabled
        self.initialized = False
        if self.enabled:
            self._init_mixer()
    
    def _init_mixer(self):
        """Initialize pygame mixer for audio playback."""
        try:
            # Check if mixer is already initialized
            if pygame.mixer.get_init() is None:
                # Initialize with Pi-friendly settings
                # 22050 Hz, 16-bit, stereo, 512 buffer
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            
            self.initialized = True
            print("Audio system initialized")
            
        except pygame.error as e:
            print(f"Warning: Could not initialize audio system: {e}")
            print("Audio will be disabled")
            self.enabled = False
            self.initialized = False
    
    def _get_cry_path(self, pokemon_id: int) -> Path:
        """
        Get file path for Pokémon cry.
        
        Args:
            pokemon_id: Pokémon national dex number
            
        Returns:
            Path to audio file
        """
        filename = f"{pokemon_id:03d}.{self.AUDIO_FORMAT}"
        return self.cries_dir / filename
    
    def _load_cry(self, pokemon_id: int) -> Optional[pygame.mixer.Sound]:
        """
        Load Pokémon cry from file.
        
        Args:
            pokemon_id: Pokémon national dex number
            
        Returns:
            pygame.mixer.Sound object or None if file not found
        """
        # Check if already in cache
        if pokemon_id in self.cache:
            # Update access order
            self.cache_order.remove(pokemon_id)
            self.cache_order.append(pokemon_id)
            return self.cache[pokemon_id]
        
        # Load from file
        cry_path = self._get_cry_path(pokemon_id)
        
        if not cry_path.exists():
            print(f"Warning: Cry audio not found for Pokémon #{pokemon_id} at {cry_path}")
            return None
        
        try:
            sound = pygame.mixer.Sound(str(cry_path))
            sound.set_volume(self.volume)
            
            # Add to cache
            self.cache[pokemon_id] = sound
            self.cache_order.append(pokemon_id)
            
            # Evict oldest if cache too large
            if len(self.cache) > self.MAX_CACHE_SIZE:
                oldest = self.cache_order.pop(0)
                del self.cache[oldest]
            
            return sound
            
        except pygame.error as e:
            print(f"Error loading cry for Pokémon #{pokemon_id}: {e}")
            return None
    
    def play_cry(self, pokemon_id: int) -> bool:
        """
        Play Pokémon cry.
        
        Args:
            pokemon_id: Pokémon national dex number
            
        Returns:
            True if played successfully, False otherwise
        """
        if not self.enabled or not self.initialized:
            return False
        
        # Load cry (from cache or file)
        sound = self._load_cry(pokemon_id)
        
        if sound is None:
            return False
        
        try:
            # Stop any currently playing sound
            pygame.mixer.stop()
            
            # Play the cry
            sound.play()
            return True
            
        except pygame.error as e:
            print(f"Error playing cry for Pokémon #{pokemon_id}: {e}")
            return False
    
    def stop(self):
        """Stop all audio playback."""
        if self.initialized:
            pygame.mixer.stop()
    
    def set_volume(self, volume: float):
        """
        Set audio volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
        
        # Update volume for all cached sounds
        for sound in self.cache.values():
            sound.set_volume(self.volume)
    
    def get_volume(self) -> float:
        """Get current volume level."""
        return self.volume
    
    def enable(self):
        """Enable audio."""
        if not self.initialized:
            self._init_mixer()
        self.enabled = True
    
    def disable(self):
        """Disable audio."""
        self.stop()
        self.enabled = False
    
    def is_enabled(self) -> bool:
        """Check if audio is enabled."""
        return self.enabled and self.initialized
    
    def is_playing(self) -> bool:
        """Check if any audio is currently playing."""
        if not self.initialized:
            return False
        return pygame.mixer.get_busy()
    
    def preload_cries(self, pokemon_ids: list[int]):
        """
        Preload multiple Pokémon cries into cache.
        
        Useful for preloading evolution chains or favorites.
        
        Args:
            pokemon_ids: List of Pokémon IDs to preload
        """
        if not self.enabled or not self.initialized:
            return
        
        for pokemon_id in pokemon_ids:
            self._load_cry(pokemon_id)
    
    def clear_cache(self):
        """Clear the audio cache to free memory."""
        self.cache.clear()
        self.cache_order.clear()
    
    def get_cache_info(self) -> Dict[str, any]:
        """
        Get information about the audio cache.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            'cached_cries': len(self.cache),
            'max_cache_size': self.MAX_CACHE_SIZE,
            'cache_ids': self.cache_order.copy()
        }
    
    def check_cry_exists(self, pokemon_id: int) -> bool:
        """
        Check if cry audio file exists for a Pokémon.
        
        Args:
            pokemon_id: Pokémon national dex number
            
        Returns:
            True if file exists, False otherwise
        """
        return self._get_cry_path(pokemon_id).exists()
    
    def get_missing_cries(self, max_id: int = 386) -> list[int]:
        """
        Get list of Pokémon IDs with missing cry files.
        
        Args:
            max_id: Maximum Pokémon ID to check (default 386 for Gen 1-3)
            
        Returns:
            List of Pokémon IDs without cry files
        """
        missing = []
        for pokemon_id in range(1, max_id + 1):
            if not self.check_cry_exists(pokemon_id):
                missing.append(pokemon_id)
        return missing
    
    def cleanup(self):
        """Clean up resources (call on app shutdown)."""
        self.stop()
        self.clear_cache()
        if self.initialized:
            pygame.mixer.quit()
            self.initialized = False
