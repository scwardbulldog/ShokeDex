#!/usr/bin/env python3
"""
Visual test: Stats tab type badge and height/weight spacing
Demonstrates the fix for overlapping type badges and physical measurements
"""

import pygame
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.database import Database
from src.ui.detail_screen import DetailScreen
from src.state_manager import StateManager

def main():
    pygame.init()
    screen = pygame.display.set_mode((480, 320))
    pygame.display.set_caption("Stats Tab - Type Badge Spacing Test")
    
    db_path = Path(__file__).parent.parent / "data" / "pokedex.db"
    
    with Database(str(db_path)) as database:
        class MockManager:
            def __init__(self):
                self.database = database
                self.state_manager = StateManager()
                self.sprite_loader = None
            def pop(self):
                pygame.quit()
                sys.exit(0)
        
        mgr = MockManager()
        
        # Test with multiple Pokemon to verify spacing
        test_pokemon = [
            (25, "Pikachu - Single type"),
            (1, "Bulbasaur - Dual type"),
            (6, "Charizard - Dual type"),
        ]
        
        current_index = 0
        detail = DetailScreen(mgr, test_pokemon[current_index][0])
        detail.on_enter()
        detail.current_tab = detail.current_tab.__class__.STATS
        
        print("\n" + "="*60)
        print("STATS TAB SPACING TEST")
        print("="*60)
        print("\nFixed: Type badges overlapping height/weight measurements")
        print("\nChanges:")
        print("  1. Badge height: 32px → 28px (saves 4px vertical)")
        print("  2. Margin below badges: 12px → 20/24px (better separation)")
        print("  3. Fixed calculation bug (wrong desc_panel_top reference)")
        print("\nControls:")
        print("  SPACE - Next test Pokemon")
        print("  ESC   - Quit")
        print("\nTest Pokemon:")
        for i, (pid, desc) in enumerate(test_pokemon):
            marker = " <--" if i == current_index else ""
            print(f"  {i+1}. {desc} (#{pid:03d}){marker}")
        print("\n" + "="*60 + "\n")
        
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        current_index = (current_index + 1) % len(test_pokemon)
                        pokemon_id, desc = test_pokemon[current_index]
                        detail = DetailScreen(mgr, pokemon_id)
                        detail.on_enter()
                        detail.current_tab = detail.current_tab.__class__.STATS
                        print(f"\nSwitched to: {desc}")
                        print(f"  Badges bottom: y={detail._badges_bottom_y}")
                        print(f"  Space available: {285 - detail._badges_bottom_y}px")
            
            detail.render(screen)
            
            # Draw visual guide lines
            font = pygame.font.Font(None, 12)
            
            # Badge bottom line
            pygame.draw.line(screen, (255, 0, 0), 
                           (0, detail._badges_bottom_y), 
                           (screen.get_width(), detail._badges_bottom_y), 1)
            label = font.render(f"Badges bottom: y={detail._badges_bottom_y}", True, (255, 0, 0))
            screen.blit(label, (2, detail._badges_bottom_y + 2))
            
            # Tab indicator line
            tab_y = 285
            pygame.draw.line(screen, (0, 255, 0), 
                           (0, tab_y), 
                           (screen.get_width(), tab_y), 1)
            label2 = font.render(f"Tab indicator: y={tab_y}", True, (0, 255, 0))
            screen.blit(label2, (2, tab_y - 12))
            
            # Available space label
            space = tab_y - detail._badges_bottom_y
            label3 = font.render(f"Available: {space}px", True, (255, 255, 0))
            screen.blit(label3, (2, (detail._badges_bottom_y + tab_y) // 2))
            
            pygame.display.flip()
            clock.tick(60)
        
        detail.on_exit()
        pygame.quit()

if __name__ == "__main__":
    main()
