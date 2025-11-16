"""
Visual demonstration of the GenerationBadge component.

Run this to see the badge in action with different generations and Pokemon IDs.
"""

import pygame
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ui.home_screen import GenerationBadge, GENERATION_NAMES
from src.ui.colors import Colors


def main():
    """Run the badge demonstration."""
    pygame.init()
    
    # Create display
    screen = pygame.display.set_mode((480, 320))
    pygame.display.set_caption("GenerationBadge Demo")
    
    # Initialize fonts
    name_font = pygame.font.Font(None, 24)
    counter_font = pygame.font.Font(None, 18)
    title_font = pygame.font.Font(None, 32)
    
    # Create badges for each generation
    badges = {
        1: GenerationBadge(generation=1, pokemon_id=25),
        2: GenerationBadge(generation=2, pokemon_id=152),
        3: GenerationBadge(generation=3, pokemon_id=252)
    }
    
    # Set fonts for all badges
    for badge in badges.values():
        badge.name_font = name_font
        badge.counter_font = counter_font
    
    # Demo state
    current_gen = 1
    pokemon_id = 1
    clock = pygame.time.Clock()
    running = True
    
    print("Badge Demo Controls:")
    print("  L/R or A/D: Switch generation")
    print("  UP/DOWN or W/S: Change Pokemon ID")
    print("  ESC: Exit")
    print()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    # Previous generation
                    current_gen = current_gen - 1 if current_gen > 1 else 3
                    pokemon_id = [1, 152, 252][current_gen - 1]
                    print(f"Switched to {GENERATION_NAMES[current_gen]} (Generation {current_gen})")
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    # Next generation
                    current_gen = current_gen + 1 if current_gen < 3 else 1
                    pokemon_id = [1, 152, 252][current_gen - 1]
                    print(f"Switched to {GENERATION_NAMES[current_gen]} (Generation {current_gen})")
                elif event.key in (pygame.K_UP, pygame.K_w):
                    # Next Pokemon
                    pokemon_id = min(pokemon_id + 1, 386)
                    print(f"Pokemon ID: {pokemon_id}")
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    # Previous Pokemon
                    pokemon_id = max(pokemon_id - 1, 1)
                    print(f"Pokemon ID: {pokemon_id}")
        
        # Clear screen
        screen.fill(Colors.BACKGROUND)
        
        # Draw title
        title = title_font.render("GenerationBadge Demo", True, Colors.TEXT_PRIMARY)
        title_rect = title.get_rect(center=(240, 30))
        screen.blit(title, title_rect)
        
        # Update current badge
        badges[current_gen].update(pokemon_id)
        
        # Draw current badge (centered)
        badges[current_gen].render(screen, x=130, y=80)
        
        # Draw all three badges below (for comparison)
        y_pos = 160
        for gen in [1, 2, 3]:
            # Draw label
            label_text = name_font.render(
                f"Generation {gen} ({GENERATION_NAMES[gen]}):",
                True,
                Colors.TEXT_SECONDARY
            )
            screen.blit(label_text, (10, y_pos))
            
            # Draw badge
            badges[gen].render(screen, x=250, y=y_pos - 5)
            
            y_pos += 50
        
        # Draw instructions
        instructions = [
            "Controls:",
            "L/R or A/D: Switch generation",
            "UP/DOWN or W/S: Change Pokemon ID"
        ]
        
        instr_font = pygame.font.Font(None, 14)
        y = 10
        for line in instructions:
            text = instr_font.render(line, True, Colors.TEXT_SECONDARY)
            screen.blit(text, (10, y))
            y += 15
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()
    print("\nDemo ended.")


if __name__ == "__main__":
    main()
