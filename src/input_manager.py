"""
Input Manager for ShokeDex - Handles GPIO buttons, keyboard, and events

Supports both development (keyboard) and hardware (GPIO) input modes.
"""

import pygame
import time
from enum import Enum
from typing import Optional, Dict, Callable, List
import sys


class InputAction(Enum):
    """Available input actions"""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    SELECT = "select"
    BACK = "back"
    START = "start"
    NONE = "none"


class InputMode(Enum):
    """Input mode - keyboard or GPIO"""
    KEYBOARD = "keyboard"
    GPIO = "gpio"


class InputManager:
    """
    Manages input from keyboard (dev) and GPIO buttons (hardware).
    
    Provides a unified interface for handling user input regardless of the source.
    """
    
    # Default keyboard mappings
    DEFAULT_KEYBOARD_MAP = {
        pygame.K_UP: InputAction.UP,
        pygame.K_w: InputAction.UP,
        pygame.K_DOWN: InputAction.DOWN,
        pygame.K_s: InputAction.DOWN,
        pygame.K_LEFT: InputAction.LEFT,
        pygame.K_a: InputAction.LEFT,
        pygame.K_RIGHT: InputAction.RIGHT,
        pygame.K_d: InputAction.RIGHT,
        pygame.K_RETURN: InputAction.SELECT,
        pygame.K_SPACE: InputAction.SELECT,
        pygame.K_ESCAPE: InputAction.BACK,
        pygame.K_BACKSPACE: InputAction.BACK,
        pygame.K_TAB: InputAction.START,
    }
    
    # Default GPIO pin mappings (BCM numbering)
    DEFAULT_GPIO_MAP = {
        17: InputAction.UP,
        27: InputAction.DOWN,
        22: InputAction.LEFT,
        23: InputAction.RIGHT,
        24: InputAction.SELECT,
        25: InputAction.BACK,
        16: InputAction.START,
    }
    
    def __init__(
        self,
        mode: InputMode = InputMode.KEYBOARD,
        keyboard_map: Optional[Dict[int, InputAction]] = None,
        gpio_map: Optional[Dict[int, InputAction]] = None,
    ):
        """
        Initialize InputManager.
        
        Args:
            mode: Input mode (KEYBOARD or GPIO)
            keyboard_map: Custom keyboard mapping (uses default if None)
            gpio_map: Custom GPIO pin mapping (uses default if None)
        """
        self.mode = mode
        self.keyboard_map = keyboard_map or self.DEFAULT_KEYBOARD_MAP
        self.gpio_map = gpio_map or self.DEFAULT_GPIO_MAP
        
        # Track last press time for each key to implement debounce
        # This prevents OS key repeat but allows rapid tapping
        self.last_press_time: Dict[int, float] = {}
        self.debounce_time = 0.05  # 50ms debounce window - prevents OS repeats, allows fast tapping
        
        # Event handlers
        self.handlers: Dict[InputAction, List[Callable]] = {
            action: [] for action in InputAction
        }
        
        # GPIO setup (only if in GPIO mode)
        self.gpio_buttons = {}
        if self.mode == InputMode.GPIO:
            self._setup_gpio()
    
    def _setup_gpio(self):
        """Set up GPIO buttons if available."""
        try:
            from gpiozero import Button
            
            for pin, action in self.gpio_map.items():
                # Create button with pull-up resistor (button connects to ground)
                button = Button(pin, pull_up=True, bounce_time=0.1)
                self.gpio_buttons[action] = button
                
                # Set up button press handler
                button.when_pressed = lambda a=action: self._handle_gpio_press(a)
                
        except ImportError:
            print("Warning: gpiozero not available. GPIO input disabled.")
            print("Install with: pip install gpiozero")
            # Fall back to keyboard mode
            self.mode = InputMode.KEYBOARD
        except Exception as e:
            print(f"Warning: Failed to initialize GPIO: {e}")
            print("Falling back to keyboard mode.")
            self.mode = InputMode.KEYBOARD
    
    def _handle_gpio_press(self, action: InputAction):
        """Handle GPIO button press."""
        self._trigger_handlers(action)
    
    def register_handler(self, action: InputAction, handler: Callable):
        """
        Register a handler function for an input action.
        
        Args:
            action: The input action to handle
            handler: Function to call when action occurs (no arguments)
        """
        if action not in self.handlers:
            self.handlers[action] = []
        self.handlers[action].append(handler)
    
    def unregister_handler(self, action: InputAction, handler: Callable):
        """
        Unregister a handler function.
        
        Args:
            action: The input action
            handler: Function to remove
        """
        if action in self.handlers and handler in self.handlers[action]:
            self.handlers[action].remove(handler)
    
    def _trigger_handlers(self, action: InputAction):
        """Trigger all handlers for an action."""
        if action in self.handlers:
            for handler in self.handlers[action]:
                handler()
    
    def process_event(self, event: pygame.event.Event) -> InputAction:
        """
        Process a pygame event and return the corresponding input action.
        
        Uses time-based debouncing to prevent OS key repeats while allowing rapid tapping.
        
        Args:
            event: Pygame event to process
            
        Returns:
            InputAction corresponding to the event, or NONE if not mapped
        """
        if self.mode == InputMode.KEYBOARD:
            if event.type == pygame.KEYDOWN:
                current_time = time.time()
                
                # Check if this key was pressed recently (debounce)
                if event.key in self.last_press_time:
                    time_since_last_press = current_time - self.last_press_time[event.key]
                    if time_since_last_press < self.debounce_time:
                        # Too soon - this is likely an OS repeat event
                        return InputAction.NONE
                
                # Record this press time
                self.last_press_time[event.key] = current_time
                
                action = self.keyboard_map.get(event.key, InputAction.NONE)
                if action != InputAction.NONE:
                    self._trigger_handlers(action)
                return action
            elif event.type == pygame.KEYUP:
                # Clear the press time when key is released
                if event.key in self.last_press_time:
                    del self.last_press_time[event.key]
        
        return InputAction.NONE
    
    def get_action_from_keyup(self, event: pygame.event.Event) -> InputAction:
        """
        Get the input action for a KEYUP event.
        
        Args:
            event: Pygame KEYUP event
            
        Returns:
            InputAction corresponding to the released key
        """
        if event.type == pygame.KEYUP:
            return self.keyboard_map.get(event.key, InputAction.NONE)
        return InputAction.NONE
    
    def get_action(self, event: pygame.event.Event) -> InputAction:
        """
        Get the input action for an event without triggering handlers.
        
        Args:
            event: Pygame event to check
            
        Returns:
            InputAction corresponding to the event
        """
        if self.mode == InputMode.KEYBOARD and event.type == pygame.KEYDOWN:
            return self.keyboard_map.get(event.key, InputAction.NONE)
        return InputAction.NONE
    
    def is_pressed(self, action: InputAction) -> bool:
        """
        Check if an action's button is currently pressed (for GPIO mode).
        
        Args:
            action: The input action to check
            
        Returns:
            True if button is pressed, False otherwise
        """
        if self.mode == InputMode.GPIO and action in self.gpio_buttons:
            return self.gpio_buttons[action].is_pressed
        return False
    
    def cleanup(self):
        """Clean up resources (close GPIO if needed)."""
        if self.mode == InputMode.GPIO:
            for button in self.gpio_buttons.values():
                button.close()
            self.gpio_buttons.clear()
    
    def get_mode_name(self) -> str:
        """Get human-readable name of current input mode."""
        return self.mode.value
    
    def switch_mode(self, new_mode: InputMode):
        """
        Switch between keyboard and GPIO modes.
        
        Args:
            new_mode: New input mode to use
        """
        if new_mode == self.mode:
            return
        
        # Clean up old mode
        self.cleanup()
        
        # Set new mode
        self.mode = new_mode
        
        # Set up new mode
        if self.mode == InputMode.GPIO:
            self._setup_gpio()
