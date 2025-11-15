"""
Tests for AudioManager

Tests audio initialization, cry playback, caching, and volume control.
Note: These tests mock pygame.mixer since audio hardware may not be available.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import os

from src.audio_manager import AudioManager


class TestAudioManager(unittest.TestCase):
    """Test cases for AudioManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory for cry files
        self.temp_dir = tempfile.mkdtemp()
        self.cries_dir = Path(self.temp_dir) / "cries"
        self.cries_dir.mkdir()
        
        # Create some dummy cry files
        for pokemon_id in [1, 2, 3, 25, 150]:
            cry_file = self.cries_dir / f"{pokemon_id:03d}.ogg"
            cry_file.touch()  # Create empty file
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Remove temp directory and files
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('pygame.mixer')
    def test_initialization(self, mock_mixer):
        """Test AudioManager initialization"""
        mock_mixer.get_init.return_value = None
        
        audio_manager = AudioManager(cries_dir=str(self.cries_dir))
        
        self.assertTrue(audio_manager.enabled)
        self.assertEqual(audio_manager.volume, 0.7)
        mock_mixer.init.assert_called_once()
    
    @patch('pygame.mixer')
    def test_disabled_audio(self, mock_mixer):
        """Test AudioManager with audio disabled"""
        audio_manager = AudioManager(
            cries_dir=str(self.cries_dir),
            enabled=False
        )
        
        self.assertFalse(audio_manager.enabled)
        mock_mixer.init.assert_not_called()
    
    @patch('pygame.mixer')
    def test_volume_control(self, mock_mixer):
        """Test volume setting and clamping"""
        mock_mixer.get_init.return_value = None
        audio_manager = AudioManager(cries_dir=str(self.cries_dir))
        
        # Set volume
        audio_manager.set_volume(0.5)
        self.assertEqual(audio_manager.get_volume(), 0.5)
        
        # Test clamping above 1.0
        audio_manager.set_volume(1.5)
        self.assertEqual(audio_manager.get_volume(), 1.0)
        
        # Test clamping below 0.0
        audio_manager.set_volume(-0.5)
        self.assertEqual(audio_manager.get_volume(), 0.0)
    
    def test_cry_path_generation(self):
        """Test cry file path generation"""
        audio_manager = AudioManager(
            cries_dir=str(self.cries_dir),
            enabled=False
        )
        
        # Test path formatting
        path = audio_manager._get_cry_path(1)
        self.assertEqual(path.name, "001.ogg")
        
        path = audio_manager._get_cry_path(25)
        self.assertEqual(path.name, "025.ogg")
        
        path = audio_manager._get_cry_path(386)
        self.assertEqual(path.name, "386.ogg")
    
    def test_check_cry_exists(self):
        """Test checking for cry file existence"""
        audio_manager = AudioManager(
            cries_dir=str(self.cries_dir),
            enabled=False
        )
        
        # Files we created
        self.assertTrue(audio_manager.check_cry_exists(1))
        self.assertTrue(audio_manager.check_cry_exists(25))
        self.assertTrue(audio_manager.check_cry_exists(150))
        
        # Files we didn't create
        self.assertFalse(audio_manager.check_cry_exists(4))
        self.assertFalse(audio_manager.check_cry_exists(100))
    
    def test_get_missing_cries(self):
        """Test getting list of missing cry files"""
        audio_manager = AudioManager(
            cries_dir=str(self.cries_dir),
            enabled=False
        )
        
        # Check first 10
        missing = audio_manager.get_missing_cries(max_id=10)
        
        # We created 1, 2, 3 - so 4-10 should be missing
        self.assertIn(4, missing)
        self.assertIn(5, missing)
        self.assertIn(10, missing)
        
        # Files we created should not be missing
        self.assertNotIn(1, missing)
        self.assertNotIn(2, missing)
        self.assertNotIn(3, missing)
    
    @patch('pygame.mixer')
    def test_cache_management(self, mock_mixer):
        """Test audio cache behavior"""
        mock_mixer.get_init.return_value = (22050, -16, 2, 512)
        mock_mixer.Sound = Mock(return_value=Mock())
        
        audio_manager = AudioManager(
            cries_dir=str(self.cries_dir),
            volume=0.5
        )
        audio_manager.MAX_CACHE_SIZE = 3  # Small cache for testing
        
        # Load some cries
        audio_manager._load_cry(1)
        audio_manager._load_cry(2)
        audio_manager._load_cry(3)
        
        # Cache should have 3 items
        cache_info = audio_manager.get_cache_info()
        self.assertEqual(cache_info['cached_cries'], 3)
        
        # Load another - should evict oldest (1)
        audio_manager._load_cry(25)
        cache_info = audio_manager.get_cache_info()
        self.assertEqual(cache_info['cached_cries'], 3)
        self.assertNotIn(1, audio_manager.cache)
        self.assertIn(25, audio_manager.cache)
    
    @patch('pygame.mixer')
    def test_cache_lru_behavior(self, mock_mixer):
        """Test LRU cache behavior (accessing moves to front)"""
        mock_mixer.get_init.return_value = (22050, -16, 2, 512)
        mock_mixer.Sound = Mock(return_value=Mock())
        
        audio_manager = AudioManager(
            cries_dir=str(self.cries_dir),
            volume=0.5
        )
        audio_manager.MAX_CACHE_SIZE = 3
        
        # Load 3 cries
        audio_manager._load_cry(1)
        audio_manager._load_cry(2)
        audio_manager._load_cry(3)
        
        # Access cry 1 again (moves it to front of LRU)
        audio_manager._load_cry(1)
        
        # Load new cry - should evict 2 (not 1)
        audio_manager._load_cry(25)
        
        self.assertIn(1, audio_manager.cache)  # Recently accessed
        self.assertNotIn(2, audio_manager.cache)  # Evicted
        self.assertIn(3, audio_manager.cache)
        self.assertIn(25, audio_manager.cache)
    
    @patch('pygame.mixer')
    def test_clear_cache(self, mock_mixer):
        """Test cache clearing"""
        mock_mixer.get_init.return_value = (22050, -16, 2, 512)
        mock_mixer.Sound = Mock(return_value=Mock())
        
        audio_manager = AudioManager(cries_dir=str(self.cries_dir))
        
        # Load some cries
        audio_manager._load_cry(1)
        audio_manager._load_cry(2)
        
        # Clear cache
        audio_manager.clear_cache()
        
        # Cache should be empty
        cache_info = audio_manager.get_cache_info()
        self.assertEqual(cache_info['cached_cries'], 0)
    
    @patch('pygame.mixer')
    def test_play_cry(self, mock_mixer):
        """Test playing Pokémon cry"""
        mock_mixer.get_init.return_value = (22050, -16, 2, 512)
        mock_sound = Mock()
        mock_mixer.Sound = Mock(return_value=mock_sound)
        
        audio_manager = AudioManager(cries_dir=str(self.cries_dir))
        
        # Play existing cry
        result = audio_manager.play_cry(25)
        
        self.assertTrue(result)
        mock_mixer.stop.assert_called_once()  # Stop previous sound
        mock_sound.play.assert_called_once()  # Play new sound
    
    @patch('pygame.mixer')
    def test_play_missing_cry(self, mock_mixer):
        """Test playing cry for file that doesn't exist"""
        mock_mixer.get_init.return_value = (22050, -16, 2, 512)
        
        audio_manager = AudioManager(cries_dir=str(self.cries_dir))
        
        # Try to play non-existent cry
        result = audio_manager.play_cry(999)
        
        self.assertFalse(result)
    
    @patch('pygame.mixer')
    def test_preload_cries(self, mock_mixer):
        """Test preloading multiple cries"""
        mock_mixer.get_init.return_value = (22050, -16, 2, 512)
        mock_mixer.Sound = Mock(return_value=Mock())
        
        audio_manager = AudioManager(cries_dir=str(self.cries_dir))
        
        # Preload multiple cries
        audio_manager.preload_cries([1, 2, 3, 25])
        
        # Check cache
        self.assertIn(1, audio_manager.cache)
        self.assertIn(2, audio_manager.cache)
        self.assertIn(3, audio_manager.cache)
        self.assertIn(25, audio_manager.cache)
    
    @patch('pygame.mixer')
    def test_enable_disable(self, mock_mixer):
        """Test enabling and disabling audio"""
        mock_mixer.get_init.return_value = None
        
        audio_manager = AudioManager(
            cries_dir=str(self.cries_dir),
            enabled=False
        )
        
        self.assertFalse(audio_manager.is_enabled())
        
        # Enable
        audio_manager.enable()
        self.assertTrue(audio_manager.is_enabled())
        
        # Disable
        audio_manager.disable()
        self.assertFalse(audio_manager.enabled)
    
    @patch('pygame.mixer')
    def test_cleanup(self, mock_mixer):
        """Test cleanup on shutdown"""
        mock_mixer.get_init.return_value = (22050, -16, 2, 512)
        mock_mixer.Sound = Mock(return_value=Mock())
        
        audio_manager = AudioManager(cries_dir=str(self.cries_dir))
        audio_manager._load_cry(1)
        
        # Cleanup
        audio_manager.cleanup()
        
        # Should stop playback, clear cache, and quit mixer
        mock_mixer.stop.assert_called()
        self.assertEqual(len(audio_manager.cache), 0)
        mock_mixer.quit.assert_called_once()
        self.assertFalse(audio_manager.initialized)


if __name__ == '__main__':
    unittest.main()
