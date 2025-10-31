"""
Tests for input manager module
"""

import unittest
import pygame
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.input_manager import InputManager, InputAction, InputMode


class TestInputManager(unittest.TestCase):
    """Test InputManager class"""
    
    @classmethod
    def setUpClass(cls):
        """Initialize pygame once for all tests"""
        pygame.init()
    
    @classmethod
    def tearDownClass(cls):
        """Quit pygame after all tests"""
        pygame.quit()
    
    def setUp(self):
        """Create InputManager for testing"""
        self.input_manager = InputManager(mode=InputMode.KEYBOARD)
    
    def tearDown(self):
        """Clean up InputManager"""
        self.input_manager.cleanup()
    
    def test_initialization(self):
        """Test InputManager initializes correctly"""
        self.assertEqual(self.input_manager.mode, InputMode.KEYBOARD)
        self.assertIsNotNone(self.input_manager.keyboard_map)
        self.assertIsNotNone(self.input_manager.handlers)
    
    def test_keyboard_mapping(self):
        """Test keyboard key mappings"""
        # Test arrow keys
        self.assertEqual(
            self.input_manager.keyboard_map[pygame.K_UP],
            InputAction.UP
        )
        self.assertEqual(
            self.input_manager.keyboard_map[pygame.K_DOWN],
            InputAction.DOWN
        )
        self.assertEqual(
            self.input_manager.keyboard_map[pygame.K_LEFT],
            InputAction.LEFT
        )
        self.assertEqual(
            self.input_manager.keyboard_map[pygame.K_RIGHT],
            InputAction.RIGHT
        )
        
        # Test WASD keys
        self.assertEqual(
            self.input_manager.keyboard_map[pygame.K_w],
            InputAction.UP
        )
        self.assertEqual(
            self.input_manager.keyboard_map[pygame.K_s],
            InputAction.DOWN
        )
        
        # Test action keys
        self.assertEqual(
            self.input_manager.keyboard_map[pygame.K_RETURN],
            InputAction.SELECT
        )
        self.assertEqual(
            self.input_manager.keyboard_map[pygame.K_ESCAPE],
            InputAction.BACK
        )
    
    def test_custom_keyboard_mapping(self):
        """Test custom keyboard mapping"""
        custom_map = {
            pygame.K_z: InputAction.SELECT,
            pygame.K_x: InputAction.BACK,
        }
        manager = InputManager(mode=InputMode.KEYBOARD, keyboard_map=custom_map)
        
        self.assertEqual(manager.keyboard_map[pygame.K_z], InputAction.SELECT)
        self.assertEqual(manager.keyboard_map[pygame.K_x], InputAction.BACK)
        
        manager.cleanup()
    
    def test_get_action(self):
        """Test getting action from event"""
        # Create a key down event for UP
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
        action = self.input_manager.get_action(event)
        
        self.assertEqual(action, InputAction.UP)
    
    def test_get_action_unmapped_key(self):
        """Test getting action for unmapped key"""
        # Create event for unmapped key
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F1)
        action = self.input_manager.get_action(event)
        
        self.assertEqual(action, InputAction.NONE)
    
    def test_get_action_non_keydown_event(self):
        """Test getting action from non-keydown event"""
        # Create a key up event
        event = pygame.event.Event(pygame.KEYUP, key=pygame.K_UP)
        action = self.input_manager.get_action(event)
        
        self.assertEqual(action, InputAction.NONE)
    
    def test_register_handler(self):
        """Test registering event handlers"""
        call_count = {'value': 0}
        
        def handler():
            call_count['value'] += 1
        
        self.input_manager.register_handler(InputAction.SELECT, handler)
        
        # Trigger the action
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        self.input_manager.process_event(event)
        
        self.assertEqual(call_count['value'], 1)
    
    def test_multiple_handlers(self):
        """Test multiple handlers for same action"""
        call_count = {'handler1': 0, 'handler2': 0}
        
        def handler1():
            call_count['handler1'] += 1
        
        def handler2():
            call_count['handler2'] += 1
        
        self.input_manager.register_handler(InputAction.SELECT, handler1)
        self.input_manager.register_handler(InputAction.SELECT, handler2)
        
        # Trigger the action
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        self.input_manager.process_event(event)
        
        self.assertEqual(call_count['handler1'], 1)
        self.assertEqual(call_count['handler2'], 1)
    
    def test_unregister_handler(self):
        """Test unregistering event handlers"""
        call_count = {'value': 0}
        
        def handler():
            call_count['value'] += 1
        
        self.input_manager.register_handler(InputAction.SELECT, handler)
        self.input_manager.unregister_handler(InputAction.SELECT, handler)
        
        # Trigger the action
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        self.input_manager.process_event(event)
        
        # Handler should not have been called
        self.assertEqual(call_count['value'], 0)
    
    def test_get_mode_name(self):
        """Test getting mode name"""
        self.assertEqual(
            self.input_manager.get_mode_name(),
            InputMode.KEYBOARD.value
        )
    
    def test_process_event_returns_action(self):
        """Test that process_event returns the action"""
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT)
        action = self.input_manager.process_event(event)
        
        self.assertEqual(action, InputAction.LEFT)


class TestInputAction(unittest.TestCase):
    """Test InputAction enum"""
    
    def test_all_actions_exist(self):
        """Test that all expected actions exist"""
        expected_actions = [
            'UP', 'DOWN', 'LEFT', 'RIGHT',
            'SELECT', 'BACK', 'START', 'NONE'
        ]
        
        for action_name in expected_actions:
            self.assertTrue(hasattr(InputAction, action_name))
    
    def test_action_values(self):
        """Test action enum values"""
        self.assertEqual(InputAction.UP.value, "up")
        self.assertEqual(InputAction.DOWN.value, "down")
        self.assertEqual(InputAction.SELECT.value, "select")


if __name__ == '__main__':
    unittest.main()
