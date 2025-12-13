"""
Layout Measurement Demo for Story 5.7 Task 5

Measures vertical space usage for each tab on DetailScreen
to verify all tabs fit within 320px viewport constraint.

Target: Info tab ~290px, Stats tab ~280px, Evolution tab ~270px
"""

import pygame
import sys
from src.ui.detail_screen import DetailScreen
from src.ui.screen_manager import ScreenManager
from src.data.database import Database
from src.state_manager import StateManager
from src.input_manager import InputManager, InputMode


def measure_tab_layout(screen_size=(480, 320)):
    """Measure vertical usage for each DetailScreen tab."""
    
    pygame.init()
    surface = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Tab Layout Measurement")
    
    # Create managers
    with Database() as db:
        state_manager = StateManager()
        input_manager = InputManager(mode=InputMode.KEYBOARD)
        
        # Create screen manager and attach managers
        screen_manager = ScreenManager(surface)
        screen_manager.database = db
        screen_manager.state_manager = state_manager
        screen_manager.input_manager = input_manager
        
        # Test with Pikachu (#25) - has evolution chain
        detail_screen = DetailScreen(screen_manager, pokemon_id=25)
        detail_screen.on_enter()
        
        # Create measurement surface with grid
        measure_surface = pygame.Surface(screen_size)
        
        tabs = ["INFO", "STATS", "EVOLUTION"]
        results = {}
        
        for tab_name in tabs:
            # Switch to tab
            from src.ui.detail_screen import DetailTab
            if tab_name == "INFO":
                detail_screen.current_tab = DetailTab.INFO
            elif tab_name == "STATS":
                detail_screen.current_tab = DetailTab.STATS
            else:
                detail_screen.current_tab = DetailTab.EVOLUTION
            
            # Clear surface
            measure_surface.fill((10, 14, 26))  # Deep space black
            
            # Render tab
            detail_screen.render(measure_surface)
            
            # Analyze vertical usage by scanning pixels
            # Look for non-background pixels to determine content bounds
            background_color = (10, 14, 26)
            
            min_y = screen_size[1]
            max_y = 0
            
            for y in range(screen_size[1]):
                row_has_content = False
                for x in range(screen_size[0]):
                    pixel = measure_surface.get_at((x, y))[:3]  # RGB only
                    if pixel != background_color:
                        row_has_content = True
                        break
                
                if row_has_content:
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)
            
            vertical_usage = max_y - min_y + 1 if max_y >= min_y else 0
            
            results[tab_name] = {
                'min_y': min_y,
                'max_y': max_y,
                'vertical_px': vertical_usage,
                'screen_height': screen_size[1],
                'fits_viewport': vertical_usage <= screen_size[1]
            }
            
            # Visual feedback
            print(f"\n{tab_name} Tab Layout:")
            print(f"  Content starts at y={min_y}px")
            print(f"  Content ends at y={max_y}px")
            print(f"  Total vertical usage: {vertical_usage}px")
            print(f"  Screen height: {screen_size[1]}px")
            print(f"  Fits viewport: {'✓ YES' if vertical_usage <= screen_size[1] else '✗ NO (OVERFLOW)'}")
            print(f"  Remaining space: {screen_size[1] - vertical_usage}px")
            
            # Check against targets
            targets = {'INFO': 290, 'STATS': 280, 'EVOLUTION': 270}
            target = targets.get(tab_name, 300)
            
            if vertical_usage <= target:
                print(f"  Target {target}px: ✓ PASS (under target)")
            elif vertical_usage <= screen_size[1]:
                print(f"  Target {target}px: ⚠ OVER TARGET but fits viewport")
            else:
                print(f"  Target {target}px: ✗ FAIL (exceeds viewport)")
        
        # Summary
        print("\n" + "="*50)
        print("SUMMARY")
        print("="*50)
        
        all_fit = all(r['fits_viewport'] for r in results.values())
        
        if all_fit:
            print("✓ ALL TABS FIT WITHIN 320px VIEWPORT")
            print(f"\nVertical usage: Info={results['INFO']['vertical_px']}px, "
                  f"Stats={results['STATS']['vertical_px']}px, "
                  f"Evolution={results['EVOLUTION']['vertical_px']}px")
        else:
            print("✗ SOME TABS OVERFLOW VIEWPORT - LAYOUT ADJUSTMENT NEEDED")
            for tab, data in results.items():
                if not data['fits_viewport']:
                    overflow = data['vertical_px'] - data['screen_height']
                    print(f"  {tab}: Overflows by {overflow}px")
        
        detail_screen.on_exit()
    
    pygame.quit()
    return results


if __name__ == "__main__":
    print("DetailScreen Tab Layout Measurement")
    print("Story 5.7 Task 5: Verify all tabs fit within 320px viewport\n")
    
    # Test on 480x320 (small display target)
    print("Testing on 480x320 display (primary target)...")
    results_480 = measure_tab_layout((480, 320))
    
    # Test on 800x480 for comparison
    print("\n" + "="*50)
    print("Testing on 800x480 display (secondary target)...")
    results_800 = measure_tab_layout((800, 480))
    
    sys.exit(0)
