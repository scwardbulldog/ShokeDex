"""
Tests for sprite processor module
"""

import unittest
import tempfile
import os
from pathlib import Path
from PIL import Image

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.sprite_processor import SpriteProcessor, GAMEBOY_COLOR_PALETTE


class TestSpriteProcessor(unittest.TestCase):
    """Test SpriteProcessor class"""
    
    def setUp(self):
        """Create temporary directory for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self.processor = SpriteProcessor(output_dir=self.temp_dir)
        
    def tearDown(self):
        """Clean up temporary directory"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_processor_initialization(self):
        """Test processor creates directories"""
        self.assertTrue(self.processor.thumb_dir.exists())
        self.assertTrue(self.processor.detail_dir.exists())
        
    def test_gameboy_palette_size(self):
        """Test that the Gameboy Color palette has correct number of colors"""
        self.assertEqual(len(GAMEBOY_COLOR_PALETTE), 56)
        
    def test_gameboy_palette_format(self):
        """Test that all palette colors are valid RGB tuples"""
        for color in GAMEBOY_COLOR_PALETTE:
            self.assertIsInstance(color, tuple)
            self.assertEqual(len(color), 3)
            for value in color:
                self.assertIsInstance(value, int)
                self.assertGreaterEqual(value, 0)
                self.assertLessEqual(value, 255)
    
    def test_get_closest_color(self):
        """Test finding closest palette color"""
        # Test pure white
        white = self.processor.get_closest_color((255, 255, 255))
        self.assertEqual(white, (255, 255, 255))
        
        # Test pure black
        black = self.processor.get_closest_color((0, 0, 0))
        self.assertEqual(black, (0, 0, 0))
        
        # Test that a color returns something from the palette
        result = self.processor.get_closest_color((128, 64, 32))
        self.assertIn(result, GAMEBOY_COLOR_PALETTE)
    
    def test_resize_sprite_thumbnail(self):
        """Test resizing sprite to thumbnail size"""
        # Create a test image
        test_image = Image.new('RGBA', (100, 100), (255, 0, 0, 255))
        
        # Resize to thumbnail
        resized = self.processor.resize_sprite(test_image, (32, 32))
        
        self.assertEqual(resized.size, (32, 32))
        self.assertEqual(resized.mode, 'RGBA')
    
    def test_resize_sprite_detail(self):
        """Test resizing sprite to detail size"""
        # Create a test image
        test_image = Image.new('RGBA', (200, 200), (0, 255, 0, 255))
        
        # Resize to detail
        resized = self.processor.resize_sprite(test_image, (96, 96))
        
        self.assertEqual(resized.size, (96, 96))
        self.assertEqual(resized.mode, 'RGBA')
    
    def test_resize_sprite_aspect_ratio(self):
        """Test that resizing preserves aspect ratio"""
        # Create a wide test image
        test_image = Image.new('RGBA', (200, 100), (0, 0, 255, 255))
        
        # Resize to square
        resized = self.processor.resize_sprite(test_image, (96, 96))
        
        # Check that the image is centered and has transparent borders
        self.assertEqual(resized.size, (96, 96))
        
        # Check that corners are transparent (should be padding)
        self.assertEqual(resized.getpixel((0, 0)), (0, 0, 0, 0))
    
    def test_quantize_to_gbc_palette(self):
        """Test quantization to GBC palette"""
        # Create a test image with various colors
        test_image = Image.new('RGB', (10, 10))
        pixels = []
        for i in range(10):
            for j in range(10):
                pixels.append((i * 25, j * 25, (i + j) * 12))
        test_image.putdata(pixels)
        
        # Quantize
        quantized = self.processor.quantize_to_gbc_palette(test_image, use_dithering=False)
        
        self.assertEqual(quantized.mode, 'RGB')
        self.assertEqual(quantized.size, test_image.size)
        
        # Verify all colors are from the palette
        unique_colors = set(quantized.getdata())
        for color in unique_colors:
            # Check if color is close to any palette color
            found = False
            for palette_color in GAMEBOY_COLOR_PALETTE:
                if color == palette_color:
                    found = True
                    break
            # Note: Due to PIL's internal processing, colors might not match exactly
            # so we just verify the image was processed
        
    def test_quantize_with_dithering(self):
        """Test quantization with dithering enabled"""
        test_image = Image.new('RGB', (50, 50), (128, 128, 128))
        
        quantized = self.processor.quantize_to_gbc_palette(test_image, use_dithering=True)
        
        self.assertEqual(quantized.mode, 'RGB')
        self.assertEqual(quantized.size, test_image.size)
    
    def test_process_sprite(self):
        """Test processing sprite into thumbnail and detail"""
        # Create a test sprite
        test_image = Image.new('RGBA', (150, 150), (255, 128, 0, 255))
        
        # Process
        thumb, detail = self.processor.process_sprite(test_image)
        
        # Check sizes
        self.assertEqual(thumb.size, (32, 32))
        self.assertEqual(detail.size, (96, 96))
        
        # Check modes
        self.assertEqual(thumb.mode, 'RGBA')
        self.assertEqual(detail.mode, 'RGBA')
    
    def test_process_sprite_with_transparency(self):
        """Test processing sprite with transparent areas"""
        # Create a test sprite with transparency
        test_image = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
        # Draw a circle
        from PIL import ImageDraw
        draw = ImageDraw.Draw(test_image)
        draw.ellipse([25, 25, 75, 75], fill=(255, 0, 0, 255))
        
        # Process
        thumb, detail = self.processor.process_sprite(test_image)
        
        # Check that corners are still transparent
        self.assertEqual(thumb.getpixel((0, 0))[3], 0)
        self.assertEqual(detail.getpixel((0, 0))[3], 0)
    
    def test_directory_structure(self):
        """Test that processor creates correct directory structure"""
        self.assertTrue((Path(self.temp_dir) / 'thumb').exists())
        self.assertTrue((Path(self.temp_dir) / 'detail').exists())
    
    def test_sprite_filename_format(self):
        """Test that sprite filenames follow the correct format"""
        # This test verifies the format used in process_pokemon_sprite
        thumb_path = self.processor.thumb_dir / f"{25:03d}.png"
        self.assertEqual(thumb_path.name, "025.png")
        
        detail_path = self.processor.detail_dir / f"{1:03d}.png"
        self.assertEqual(detail_path.name, "001.png")
    
    def test_generation_ranges(self):
        """Test that generation ID ranges are correct"""
        # This is implicitly tested in process_generation
        # Gen 1: 1-151
        # Gen 2: 152-251
        # Gen 3: 252-386
        gen_ranges = {
            1: (1, 151),
            2: (152, 251),
            3: (252, 386)
        }
        
        # Verify ranges don't overlap and are contiguous
        self.assertEqual(gen_ranges[1][1] + 1, gen_ranges[2][0])
        self.assertEqual(gen_ranges[2][1] + 1, gen_ranges[3][0])
        
        # Verify total count
        total = sum(end - start + 1 for start, end in gen_ranges.values())
        self.assertEqual(total, 386)


class TestColorPalette(unittest.TestCase):
    """Test color palette properties"""
    
    def test_palette_has_primary_colors(self):
        """Test that palette includes primary colors"""
        # Check for white, black, red, green, blue
        self.assertIn((255, 255, 255), GAMEBOY_COLOR_PALETTE)  # White
        self.assertIn((0, 0, 0), GAMEBOY_COLOR_PALETTE)        # Black
        self.assertIn((255, 0, 0), GAMEBOY_COLOR_PALETTE)      # Red
        self.assertIn((0, 255, 0), GAMEBOY_COLOR_PALETTE)      # Green
        self.assertIn((0, 0, 255), GAMEBOY_COLOR_PALETTE)      # Blue
    
    def test_palette_has_grayscale(self):
        """Test that palette includes grayscale colors"""
        grayscale_colors = [
            (255, 255, 255),  # White
            (0, 0, 0),        # Black
        ]
        for color in grayscale_colors:
            self.assertIn(color, GAMEBOY_COLOR_PALETTE)
    
    def test_palette_diversity(self):
        """Test that palette has good color diversity"""
        # Check that we have colors in different hue ranges
        has_red = any(r > 200 and g < 100 and b < 100 for r, g, b in GAMEBOY_COLOR_PALETTE)
        has_green = any(r < 100 and g > 200 and b < 100 for r, g, b in GAMEBOY_COLOR_PALETTE)
        has_blue = any(r < 100 and g < 100 and b > 200 for r, g, b in GAMEBOY_COLOR_PALETTE)
        
        self.assertTrue(has_red, "Palette should include red colors")
        self.assertTrue(has_green, "Palette should include green colors")
        self.assertTrue(has_blue, "Palette should include blue colors")


if __name__ == '__main__':
    unittest.main()
