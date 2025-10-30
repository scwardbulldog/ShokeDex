"""
Sprite processor for ShokeDex
Converts Pokémon sprites to Gameboy Color palette with dithering
Generates thumbnail (32x32) and detail (96x96) versions
"""

import os
import requests
import time
from pathlib import Path
from typing import Tuple, Optional, List
from PIL import Image, ImageDraw


# Gameboy Color palette - 56 colors (4 palettes of 4 colors each, plus additional colors)
# Based on the actual GBC color capabilities
GAMEBOY_COLOR_PALETTE = [
    # Palette 0 - Grayscale
    (255, 255, 255),  # White
    (192, 192, 192),  # Light gray
    (96, 96, 96),     # Dark gray
    (0, 0, 0),        # Black
    
    # Palette 1 - Reds/Pinks
    (255, 0, 0),      # Red
    (255, 128, 128),  # Light red
    (128, 0, 0),      # Dark red
    (255, 192, 203),  # Pink
    
    # Palette 2 - Blues
    (0, 0, 255),      # Blue
    (128, 128, 255),  # Light blue
    (0, 0, 128),      # Dark blue
    (0, 255, 255),    # Cyan
    
    # Palette 3 - Greens
    (0, 255, 0),      # Green
    (128, 255, 128),  # Light green
    (0, 128, 0),      # Dark green
    (0, 128, 64),     # Teal
    
    # Palette 4 - Yellows/Oranges
    (255, 255, 0),    # Yellow
    (255, 192, 0),    # Gold
    (255, 128, 0),    # Orange
    (128, 64, 0),     # Brown
    
    # Palette 5 - Purples
    (128, 0, 128),    # Purple
    (255, 0, 255),    # Magenta
    (192, 128, 255),  # Light purple
    (64, 0, 64),      # Dark purple
    
    # Additional common colors for variety
    (255, 255, 128),  # Light yellow
    (128, 255, 255),  # Light cyan
    (255, 128, 255),  # Light magenta
    (64, 64, 64),     # Very dark gray
    (224, 224, 224),  # Very light gray
    (192, 0, 0),      # Medium red
    (0, 192, 0),      # Medium green
    (0, 0, 192),      # Medium blue
    (192, 192, 0),    # Olive
    (0, 192, 192),    # Medium cyan
    (192, 0, 192),    # Medium magenta
    (128, 128, 0),    # Dark yellow
    (0, 128, 128),    # Dark cyan
    (128, 0, 255),    # Blue-violet
    (255, 128, 64),   # Light orange
    (64, 128, 64),    # Forest green
    (160, 82, 45),    # Sienna
    (210, 180, 140),  # Tan
    (139, 69, 19),    # Saddle brown
    (255, 215, 0),    # Gold (alt)
    (184, 134, 11),   # Dark goldenrod
    (218, 165, 32),   # Goldenrod
    (240, 230, 140),  # Khaki
    (189, 183, 107),  # Dark khaki
    (154, 205, 50),   # Yellow green
    (107, 142, 35),   # Olive drab
    (85, 107, 47),    # Dark olive green
    (173, 216, 230),  # Light blue
    (135, 206, 235),  # Sky blue
    (70, 130, 180),   # Steel blue
    (25, 25, 112),    # Midnight blue
    (112, 128, 144),  # Slate gray
]


class SpriteProcessor:
    """Processes Pokémon sprites with Gameboy Color palette"""
    
    BASE_URL = "https://pokeapi.co/api/v2"
    
    def __init__(self, output_dir: str = "assets/sprites", rate_limit_delay: float = 0.1):
        """
        Initialize sprite processor
        
        Args:
            output_dir: Base directory for sprite output
            rate_limit_delay: Delay between API requests in seconds
        """
        self.output_dir = Path(output_dir)
        self.thumb_dir = self.output_dir / "thumb"
        self.detail_dir = self.output_dir / "detail"
        self.rate_limit_delay = rate_limit_delay
        
        # Create directories if they don't exist
        self.thumb_dir.mkdir(parents=True, exist_ok=True)
        self.detail_dir.mkdir(parents=True, exist_ok=True)
        
    def get_closest_color(self, rgb: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """
        Find the closest color in the Gameboy Color palette
        
        Args:
            rgb: RGB color tuple
            
        Returns:
            Closest color from the palette
        """
        min_distance = float('inf')
        closest_color = GAMEBOY_COLOR_PALETTE[0]
        
        for palette_color in GAMEBOY_COLOR_PALETTE:
            # Calculate Euclidean distance in RGB space
            distance = sum((a - b) ** 2 for a, b in zip(rgb, palette_color))
            if distance < min_distance:
                min_distance = distance
                closest_color = palette_color
                
        return closest_color
    
    def quantize_to_gbc_palette(self, image: Image.Image, use_dithering: bool = True) -> Image.Image:
        """
        Quantize image to Gameboy Color palette
        
        Args:
            image: Input PIL Image
            use_dithering: Whether to apply Floyd-Steinberg dithering
            
        Returns:
            Quantized image
        """
        # Convert to RGB if not already
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Create a palette image
        palette_image = Image.new('P', (1, 1))
        palette_data = []
        for color in GAMEBOY_COLOR_PALETTE:
            palette_data.extend(color)
        # Pad palette to 256 colors
        while len(palette_data) < 768:
            palette_data.append(0)
        palette_image.putpalette(palette_data)
        
        # Quantize using PIL's built-in method with or without dithering
        if use_dithering:
            quantized = image.quantize(palette=palette_image, dither=Image.Dither.FLOYDSTEINBERG)
        else:
            quantized = image.quantize(palette=palette_image, dither=Image.Dither.NONE)
        
        # Convert back to RGB
        return quantized.convert('RGB')
    
    def resize_sprite(self, image: Image.Image, size: Tuple[int, int]) -> Image.Image:
        """
        Resize sprite with proper aspect ratio handling
        
        Args:
            image: Input PIL Image
            size: Target size (width, height)
            
        Returns:
            Resized image with transparency preserved
        """
        # Create a new image with transparency
        result = Image.new('RGBA', size, (0, 0, 0, 0))
        
        # Calculate scaling to fit within target size while maintaining aspect ratio
        img_ratio = image.width / image.height
        target_ratio = size[0] / size[1]
        
        if img_ratio > target_ratio:
            # Image is wider, scale by width
            new_width = size[0]
            new_height = int(size[0] / img_ratio)
        else:
            # Image is taller, scale by height
            new_height = size[1]
            new_width = int(size[1] * img_ratio)
        
        # Resize the image
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Center the image
        x_offset = (size[0] - new_width) // 2
        y_offset = (size[1] - new_height) // 2
        
        result.paste(resized, (x_offset, y_offset), resized if 'A' in resized.mode else None)
        
        return result
    
    def process_sprite(self, image: Image.Image, thumb_size: Tuple[int, int] = (32, 32),
                      detail_size: Tuple[int, int] = (96, 96)) -> Tuple[Image.Image, Image.Image]:
        """
        Process a sprite into thumbnail and detail versions
        
        Args:
            image: Input PIL Image
            thumb_size: Thumbnail size
            detail_size: Detail size
            
        Returns:
            Tuple of (thumbnail, detail) images
        """
        # Ensure image has alpha channel
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Resize to detail size first
        detail = self.resize_sprite(image, detail_size)
        
        # Apply GBC palette to detail (on RGB data, preserving alpha)
        detail_rgb = detail.convert('RGB')
        detail_quantized = self.quantize_to_gbc_palette(detail_rgb, use_dithering=True)
        
        # Restore alpha channel
        detail_final = Image.new('RGBA', detail.size)
        detail_final.paste(detail_quantized, (0, 0))
        # Apply original alpha mask
        detail_final.putalpha(detail.getchannel('A'))
        
        # Create thumbnail from detail
        thumb = self.resize_sprite(detail_final, thumb_size)
        
        return thumb, detail_final
    
    def fetch_sprite_url(self, pokemon_id: int) -> Optional[str]:
        """
        Fetch sprite URL for a Pokémon from PokéAPI
        
        Args:
            pokemon_id: Pokémon ID
            
        Returns:
            Sprite URL or None if not found
        """
        try:
            time.sleep(self.rate_limit_delay)
            response = requests.get(f"{self.BASE_URL}/pokemon/{pokemon_id}", timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Try to get the official artwork first, fallback to default front sprite
            sprite_url = (data.get('sprites', {}).get('other', {})
                         .get('official-artwork', {}).get('front_default'))
            
            if not sprite_url:
                sprite_url = data.get('sprites', {}).get('front_default')
            
            return sprite_url
        except requests.exceptions.RequestException as e:
            print(f"Error fetching sprite URL for Pokémon {pokemon_id}: {e}")
            return None
    
    def download_sprite(self, url: str) -> Optional[Image.Image]:
        """
        Download sprite from URL
        
        Args:
            url: Image URL
            
        Returns:
            PIL Image or None if download fails
        """
        try:
            time.sleep(self.rate_limit_delay)
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            from io import BytesIO
            return Image.open(BytesIO(response.content))
        except Exception as e:
            print(f"Error downloading sprite from {url}: {e}")
            return None
    
    def process_pokemon_sprite(self, pokemon_id: int, pokemon_name: str = None) -> bool:
        """
        Process a single Pokémon sprite
        
        Args:
            pokemon_id: Pokémon ID
            pokemon_name: Optional Pokémon name for logging
            
        Returns:
            True if successful, False otherwise
        """
        # Check if sprites already exist
        thumb_path = self.thumb_dir / f"{pokemon_id:03d}.png"
        detail_path = self.detail_dir / f"{pokemon_id:03d}.png"
        
        if thumb_path.exists() and detail_path.exists():
            print(f"Sprites for #{pokemon_id:03d} {pokemon_name or ''} already exist, skipping")
            return True
        
        print(f"Processing Pokémon #{pokemon_id:03d} {pokemon_name or ''}...")
        
        # Fetch sprite URL
        sprite_url = self.fetch_sprite_url(pokemon_id)
        if not sprite_url:
            print(f"  Failed to fetch sprite URL")
            return False
        
        # Download sprite
        sprite = self.download_sprite(sprite_url)
        if not sprite:
            print(f"  Failed to download sprite")
            return False
        
        # Process sprite
        try:
            thumb, detail = self.process_sprite(sprite)
            
            # Save sprites
            thumb.save(thumb_path, 'PNG')
            detail.save(detail_path, 'PNG')
            
            print(f"  Successfully processed and saved sprites")
            return True
        except Exception as e:
            print(f"  Error processing sprite: {e}")
            return False
    
    def process_generation(self, generation: int) -> int:
        """
        Process all Pokémon sprites for a generation
        
        Args:
            generation: Generation number (1, 2, or 3)
            
        Returns:
            Number of sprites successfully processed
        """
        # Define ID ranges for each generation
        gen_ranges = {
            1: (1, 151),
            2: (152, 251),
            3: (252, 386)
        }
        
        if generation not in gen_ranges:
            print(f"Invalid generation: {generation}. Must be 1, 2, or 3.")
            return 0
        
        start_id, end_id = gen_ranges[generation]
        print(f"\nProcessing Generation {generation} (Pokémon #{start_id}-#{end_id})...")
        print("=" * 60)
        
        success_count = 0
        for pokemon_id in range(start_id, end_id + 1):
            if self.process_pokemon_sprite(pokemon_id):
                success_count += 1
        
        print(f"\nGeneration {generation} complete: {success_count}/{end_id - start_id + 1} sprites processed")
        return success_count
    
    def process_all_generations(self) -> int:
        """
        Process all Pokémon sprites for generations 1-3
        
        Returns:
            Total number of sprites successfully processed
        """
        total_success = 0
        for gen in [1, 2, 3]:
            total_success += self.process_generation(gen)
        
        print(f"\n{'=' * 60}")
        print(f"All generations complete: {total_success} total sprites processed")
        return total_success


def main():
    """Main entry point for sprite processing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process Pokémon sprites with Gameboy Color palette')
    parser.add_argument('--gen', type=int, choices=[1, 2, 3], 
                       help='Process specific generation (1, 2, or 3)')
    parser.add_argument('--all', action='store_true',
                       help='Process all generations (1-3)')
    parser.add_argument('--pokemon', type=int,
                       help='Process specific Pokémon by ID')
    parser.add_argument('--output', type=str, default='assets/sprites',
                       help='Output directory for sprites (default: assets/sprites)')
    parser.add_argument('--delay', type=float, default=0.1,
                       help='Delay between API requests in seconds (default: 0.1)')
    
    args = parser.parse_args()
    
    # Create processor
    processor = SpriteProcessor(output_dir=args.output, rate_limit_delay=args.delay)
    
    # Process based on arguments
    if args.pokemon:
        processor.process_pokemon_sprite(args.pokemon)
    elif args.gen:
        processor.process_generation(args.gen)
    elif args.all:
        processor.process_all_generations()
    else:
        print("Please specify --gen, --all, or --pokemon")
        parser.print_help()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
