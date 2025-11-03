"""
Settings Screen for ShokeDex - Application settings
"""

import pygame
from typing import Optional, List, Dict
from .screen import Screen
from .colors import Colors
from ..input_manager import InputAction, InputMode


class SettingsScreen(Screen):
    """
    Settings screen for configuring application options.
    
    Currently includes network sync toggle and input mode selection.
    """
    
    def __init__(self, screen_manager, input_manager=None, sync_manager=None):
        """
        Initialize SettingsScreen.
        
        Args:
            screen_manager: ScreenManager instance
            input_manager: InputManager instance (optional)
            sync_manager: SyncManager instance (optional)
        """
        super().__init__(screen_manager)
        self.input_manager = input_manager
        self.sync_manager = sync_manager
        
        # Settings
        self.settings = {
            'network_sync': False,
            'input_mode': 'keyboard',
            'volume': 50,
        }
        
        # Menu state
        self.menu_items: List[Dict] = [
            {
                'label': 'Network Sync',
                'type': 'toggle',
                'key': 'network_sync',
                'description': 'Sync data with server'
            },
            {
                'label': 'Input Mode',
                'type': 'choice',
                'key': 'input_mode',
                'choices': ['keyboard', 'gpio'],
                'description': 'Input device to use'
            },
            {
                'label': 'Volume',
                'type': 'slider',
                'key': 'volume',
                'min': 0,
                'max': 100,
                'step': 10,
                'description': 'Audio volume level'
            },
            {
                'label': 'Back',
                'type': 'action',
                'action': 'back',
                'description': 'Return to previous screen'
            },
        ]
        
        self.selected_index = 0
        
        # Fonts
        self.title_font: Optional[pygame.font.Font] = None
        self.text_font: Optional[pygame.font.Font] = None
        self.small_font: Optional[pygame.font.Font] = None
    
    def on_enter(self):
        """Called when screen becomes active."""
        super().on_enter()
        
        # Initialize fonts
        self.title_font = pygame.font.Font(None, 32)
        self.text_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 16)
        
        # Load current input mode if available
        if self.input_manager:
            self.settings['input_mode'] = self.input_manager.get_mode_name()
        
        # Load sync state if available
        if self.sync_manager:
            sync_info = self.sync_manager.get_sync_info()
            self.settings['network_sync'] = sync_info['enabled']
    
    def handle_input(self, action: InputAction):
        """Handle input actions."""
        if action == InputAction.UP:
            self.selected_index = max(0, self.selected_index - 1)
        elif action == InputAction.DOWN:
            self.selected_index = min(
                len(self.menu_items) - 1,
                self.selected_index + 1
            )
        elif action == InputAction.SELECT:
            self._activate_item()
        elif action == InputAction.LEFT:
            self._adjust_item(-1)
        elif action == InputAction.RIGHT:
            self._adjust_item(1)
        elif action == InputAction.BACK:
            self.screen_manager.pop()
    
    def _activate_item(self):
        """Activate the selected menu item."""
        item = self.menu_items[self.selected_index]
        
        if item['type'] == 'toggle':
            # Toggle the setting
            key = item['key']
            self.settings[key] = not self.settings[key]
            self._apply_setting(key)
        elif item['type'] == 'action':
            if item['action'] == 'back':
                self.screen_manager.pop()
    
    def _adjust_item(self, delta: int):
        """Adjust the value of the selected item."""
        item = self.menu_items[self.selected_index]
        
        if item['type'] == 'choice':
            key = item['key']
            choices = item['choices']
            current_idx = choices.index(self.settings[key])
            new_idx = (current_idx + delta) % len(choices)
            self.settings[key] = choices[new_idx]
            self._apply_setting(key)
        elif item['type'] == 'slider':
            key = item['key']
            step = item['step']
            min_val = item['min']
            max_val = item['max']
            new_val = self.settings[key] + (delta * step)
            self.settings[key] = max(min_val, min(max_val, new_val))
            self._apply_setting(key)
    
    def _apply_setting(self, key: str):
        """Apply a setting change."""
        if key == 'input_mode' and self.input_manager:
            # Switch input mode
            mode_name = self.settings['input_mode']
            try:
                if mode_name == 'keyboard':
                    self.input_manager.switch_mode(InputMode.KEYBOARD)
                elif mode_name == 'gpio':
                    self.input_manager.switch_mode(InputMode.GPIO)
                    # Check if GPIO initialization succeeded
                    if self.input_manager.mode == InputMode.KEYBOARD:
                        # GPIO failed, revert setting
                        self.settings['input_mode'] = 'keyboard'
                        print("Warning: GPIO initialization failed, using keyboard")
            except Exception as e:
                print(f"Error switching input mode: {e}")
                self.settings['input_mode'] = 'keyboard'
                self.input_manager.mode = InputMode.KEYBOARD
        elif key == 'network_sync':
            # Handle network sync toggle
            if self.sync_manager:
                self.sync_manager.enable_sync(self.settings['network_sync'])
                if self.settings['network_sync'] and self.sync_manager.is_online():
                    # Start sync if online
                    self.sync_manager.start_sync()
            else:
                print(f"Network sync {'enabled' if self.settings['network_sync'] else 'disabled'} (stub)")
        elif key == 'volume':
            # Stub for volume control
            print(f"Volume set to {self.settings['volume']}%")
    
    def update(self, delta_time: float):
        """Update screen state."""
        pass
    
    def render(self, surface: pygame.Surface):
        """Render the screen."""
        # Clear background
        surface.fill(Colors.BACKGROUND)
        
        # Draw title
        title_text = self.title_font.render("Settings", True, Colors.TEXT_PRIMARY)
        title_rect = title_text.get_rect(center=(240, 20))
        surface.blit(title_text, title_rect)
        
        # Draw menu items
        y = 60
        for i, item in enumerate(self.menu_items):
            is_selected = (i == self.selected_index)
            self._render_menu_item(surface, item, y, is_selected)
            y += 50
        
        # Draw description for selected item
        if 0 <= self.selected_index < len(self.menu_items):
            desc = self.menu_items[self.selected_index].get('description', '')
            desc_text = self.small_font.render(desc, True, Colors.TEXT_SECONDARY)
            desc_rect = desc_text.get_rect(center=(240, 290))
            surface.blit(desc_text, desc_rect)
        
        # Draw help text
        help_text = self.small_font.render(
            "←/→: Adjust | SELECT: Toggle | BACK: Return",
            True,
            Colors.TEXT_SECONDARY
        )
        help_rect = help_text.get_rect(right=470, bottom=315)
        surface.blit(help_text, help_rect)
    
    def _render_menu_item(
        self,
        surface: pygame.Surface,
        item: Dict,
        y: int,
        is_selected: bool
    ):
        """Render a single menu item."""
        # Draw selection highlight
        if is_selected:
            rect = pygame.Rect(20, y - 5, 440, 40)
            pygame.draw.rect(surface, Colors.SELECTION_BG, rect)
            pygame.draw.rect(surface, Colors.BORDER, rect, 2)
        
        text_color = Colors.SELECTION_TEXT if is_selected else Colors.TEXT_PRIMARY
        
        # Draw label
        label_text = self.text_font.render(item['label'], True, text_color)
        surface.blit(label_text, (30, y))
        
        # Draw value based on type
        if item['type'] == 'toggle':
            key = item['key']
            value = "ON" if self.settings[key] else "OFF"
            value_color = Colors.SUCCESS if self.settings[key] else Colors.ERROR
            if is_selected:
                value_color = text_color
            
            value_text = self.text_font.render(value, True, value_color)
            value_rect = value_text.get_rect(right=450, centery=y + 10)
            surface.blit(value_text, value_rect)
        elif item['type'] == 'choice':
            key = item['key']
            value = self.settings[key].upper()
            
            value_text = self.text_font.render(value, True, text_color)
            value_rect = value_text.get_rect(right=450, centery=y + 10)
            surface.blit(value_text, value_rect)
        elif item['type'] == 'slider':
            key = item['key']
            value = self.settings[key]
            
            # Draw slider
            slider_x = 300
            slider_width = 140
            slider_rect = pygame.Rect(slider_x, y + 5, slider_width, 10)
            pygame.draw.rect(surface, Colors.GRAY, slider_rect)
            
            # Draw filled portion
            fill_width = int(slider_width * value / item['max'])
            fill_rect = pygame.Rect(slider_x, y + 5, fill_width, 10)
            pygame.draw.rect(surface, Colors.LIGHT_GREEN, fill_rect)
            pygame.draw.rect(surface, Colors.BORDER, slider_rect, 1)
            
            # Draw value text
            value_text = self.small_font.render(str(value), True, text_color)
            surface.blit(value_text, (slider_x + slider_width + 10, y + 2))
        elif item['type'] == 'action':
            # Draw arrow for action items
            if is_selected:
                arrow_text = self.text_font.render("→", True, text_color)
                arrow_rect = arrow_text.get_rect(right=450, centery=y + 10)
                surface.blit(arrow_text, arrow_rect)
