"""
Demo script for sprite processing pipeline
Shows how to use the SpriteProcessor class
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.sprite_processor import SpriteProcessor
from PIL import Image, ImageDraw


def create_demo_sprite():
    """Create a simple demo sprite for testing"""
    # Create a 200x200 image with transparency
    img = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a colorful Pokémon-like sprite
    # Body (yellow circle)
    draw.ellipse([50, 60, 150, 160], fill=(255, 220, 0, 255))
    
    # Ears (triangles - simplified as circles)
    draw.ellipse([40, 30, 70, 70], fill=(255, 220, 0, 255))
    draw.ellipse([130, 30, 160, 70], fill=(255, 220, 0, 255))
    draw.ellipse([45, 35, 65, 55], fill=(0, 0, 0, 255))
    draw.ellipse([135, 35, 155, 55], fill=(0, 0, 0, 255))
    
    # Eyes
    draw.ellipse([70, 80, 90, 100], fill=(0, 0, 0, 255))
    draw.ellipse([110, 80, 130, 100], fill=(0, 0, 0, 255))
    
    # Red cheeks
    draw.ellipse([50, 95, 70, 115], fill=(255, 50, 50, 255))
    draw.ellipse([130, 95, 150, 115], fill=(255, 50, 50, 255))
    
    # Mouth
    draw.arc([80, 105, 120, 125], 0, 180, fill=(0, 0, 0, 255), width=2)
    
    # Tail (lightning bolt shape - simplified)
    draw.polygon([(155, 100), (165, 90), (160, 110), (170, 100), (160, 130), (165, 110)],
                 fill=(255, 220, 0, 255))
    
    return img


def demo_basic_processing():
    """Demonstrate basic sprite processing"""
    print("=" * 60)
    print("Demo: Basic Sprite Processing")
    print("=" * 60)
    
    # Create processor
    processor = SpriteProcessor(output_dir='assets/sprites')
    
    # Create a demo sprite
    print("\n1. Creating demo sprite...")
    demo_sprite = create_demo_sprite()
    print("   ✓ Demo sprite created (200x200 RGBA)")
    
    # Process sprite
    print("\n2. Processing sprite...")
    thumb, detail = processor.process_sprite(demo_sprite)
    print(f"   ✓ Thumbnail generated: {thumb.size} {thumb.mode}")
    print(f"   ✓ Detail generated: {detail.size} {detail.mode}")
    
    # Save results
    print("\n3. Saving processed sprites...")
    demo_dir = Path('examples/demo_output')
    demo_dir.mkdir(exist_ok=True)
    
    thumb.save(demo_dir / 'demo_thumb.png')
    detail.save(demo_dir / 'demo_detail.png')
    demo_sprite.save(demo_dir / 'demo_original.png')
    
    print(f"   ✓ Saved to {demo_dir}/")
    print("     - demo_original.png (original)")
    print("     - demo_detail.png (96x96 GBC palette)")
    print("     - demo_thumb.png (32x32 GBC palette)")
    

def demo_palette_colors():
    """Demonstrate Gameboy Color palette"""
    from src.data.sprite_processor import GAMEBOY_COLOR_PALETTE
    
    print("\n" + "=" * 60)
    print("Demo: Gameboy Color Palette")
    print("=" * 60)
    
    print(f"\nTotal colors in palette: {len(GAMEBOY_COLOR_PALETTE)}")
    print("\nFirst 10 colors (RGB):")
    for i, color in enumerate(GAMEBOY_COLOR_PALETTE[:10], 1):
        print(f"  {i:2d}. RGB{color}")
    
    # Create a palette swatch image
    print("\n4. Creating palette swatch image...")
    swatch_width = 20
    swatch_height = 20
    cols = 8
    rows = (len(GAMEBOY_COLOR_PALETTE) + cols - 1) // cols
    
    palette_img = Image.new('RGB', (cols * swatch_width, rows * swatch_height), (255, 255, 255))
    draw = ImageDraw.Draw(palette_img)
    
    for i, color in enumerate(GAMEBOY_COLOR_PALETTE):
        x = (i % cols) * swatch_width
        y = (i // cols) * swatch_height
        draw.rectangle([x, y, x + swatch_width, y + swatch_height], fill=color)
    
    demo_dir = Path('examples/demo_output')
    demo_dir.mkdir(exist_ok=True)
    palette_img.save(demo_dir / 'gbc_palette.png')
    print(f"   ✓ Palette swatch saved to {demo_dir}/gbc_palette.png")


def demo_quantization_comparison():
    """Demonstrate the difference between original and quantized images"""
    print("\n" + "=" * 60)
    print("Demo: Quantization with and without Dithering")
    print("=" * 60)
    
    processor = SpriteProcessor()
    demo_sprite = create_demo_sprite()
    
    # Resize to detail size
    detail_sized = processor.resize_sprite(demo_sprite, (96, 96))
    detail_rgb = detail_sized.convert('RGB')
    
    print("\n5. Comparing quantization methods...")
    
    # Without dithering
    quantized_no_dither = processor.quantize_to_gbc_palette(detail_rgb, use_dithering=False)
    
    # With dithering
    quantized_with_dither = processor.quantize_to_gbc_palette(detail_rgb, use_dithering=True)
    
    # Save comparisons
    demo_dir = Path('examples/demo_output')
    demo_dir.mkdir(exist_ok=True)
    
    detail_rgb.save(demo_dir / 'comparison_original.png')
    quantized_no_dither.save(demo_dir / 'comparison_no_dither.png')
    quantized_with_dither.save(demo_dir / 'comparison_with_dither.png')
    
    print(f"   ✓ Saved comparison images to {demo_dir}/")
    print("     - comparison_original.png (full color)")
    print("     - comparison_no_dither.png (GBC palette, no dithering)")
    print("     - comparison_with_dither.png (GBC palette, with dithering)")


def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("ShokeDex Sprite Processing Pipeline Demo")
    print("=" * 60)
    
    try:
        demo_basic_processing()
        demo_palette_colors()
        demo_quantization_comparison()
        
        print("\n" + "=" * 60)
        print("Demo Complete!")
        print("=" * 60)
        print("\nCheck the 'examples/demo_output/' directory to see the results.")
        print("\nTo process real Pokémon sprites from PokéAPI:")
        print("  python src/data/sprite_processor.py --pokemon 25")
        print("  python src/data/sprite_processor.py --gen 1")
        print("  python src/data/sprite_processor.py --all")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
