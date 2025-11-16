"""
Generate generation badge icons for ShokeDex.

Creates simple geometric badge icons with holographic blue aesthetic:
- Kanto: Circle (Poké Ball inspired)
- Johto: Star (GS Ball inspired) 
- Hoenn: Triangle (Master Ball inspired)
"""

from PIL import Image, ImageDraw
import os


def create_kanto_badge(size=40):
    """Create Kanto badge - circular Poké Ball inspired design."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Electric blue colors
    blue = (0, 212, 255, 255)  # #00d4ff
    bright_cyan = (77, 247, 255, 255)  # #4df7ff
    
    # Outer circle
    draw.ellipse([2, 2, size-2, size-2], outline=blue, width=3)
    
    # Center horizontal line (Poké Ball split)
    draw.line([5, size//2, size-5, size//2], fill=bright_cyan, width=2)
    
    # Center circle
    center = size // 2
    radius = size // 6
    draw.ellipse([center-radius, center-radius, center+radius, center+radius], 
                 fill=bright_cyan, outline=blue, width=2)
    
    return img


def create_johto_badge(size=40):
    """Create Johto badge - star/diamond GS Ball inspired design."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Electric blue colors
    blue = (0, 212, 255, 255)
    bright_cyan = (77, 247, 255, 255)
    
    # Diamond/star shape (4-pointed)
    center = size // 2
    points = [
        (center, 4),           # Top
        (size-4, center),      # Right
        (center, size-4),      # Bottom
        (4, center)            # Left
    ]
    
    # Outer diamond
    draw.polygon(points, outline=blue, width=3)
    
    # Inner star lines
    draw.line([center, 8, center, size-8], fill=bright_cyan, width=2)
    draw.line([8, center, size-8, center], fill=bright_cyan, width=2)
    
    # Center glow
    draw.ellipse([center-4, center-4, center+4, center+4], fill=bright_cyan)
    
    return img


def create_hoenn_badge(size=40):
    """Create Hoenn badge - triangular Master Ball inspired design."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Electric blue colors
    blue = (0, 212, 255, 255)
    bright_cyan = (77, 247, 255, 255)
    
    # Equilateral triangle pointing up
    center_x = size // 2
    points = [
        (center_x, 4),              # Top
        (size-4, size-6),           # Bottom right
        (4, size-6)                 # Bottom left
    ]
    
    # Outer triangle
    draw.polygon(points, outline=blue, width=3)
    
    # Inner lines from each vertex to opposite side midpoint
    # Creates triangular Master Ball pattern
    mid_bottom = (center_x, size-6)
    mid_right = ((size-4 + 4)//2, (size-6 + size-6)//2)
    
    draw.line([center_x, 4, center_x, size-10], fill=bright_cyan, width=2)
    
    # Center circle
    center_y = size // 2 + 2
    draw.ellipse([center_x-5, center_y-5, center_x+5, center_y+5], 
                 fill=bright_cyan, outline=blue, width=2)
    
    return img


def main():
    """Generate all three badge icons."""
    output_dir = "assets/icons"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Create badges
    badges = {
        'badge_kanto.png': create_kanto_badge(),
        'badge_johto.png': create_johto_badge(),
        'badge_hoenn.png': create_hoenn_badge()
    }
    
    # Save badges
    for filename, img in badges.items():
        filepath = os.path.join(output_dir, filename)
        img.save(filepath)
        print(f"✓ Created {filepath}")
    
    print(f"\nGenerated {len(badges)} badge icons in {output_dir}/")


if __name__ == "__main__":
    main()
