#!/usr/bin/env python3
"""
Unit tests for Wii Balance Board module.

Note: These tests validate the class structure and logic but do not require
actual hardware. Hardware integration testing requires a physical Wii Balance Board.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys

# Mock bluetooth module if not available
sys.modules['bluetooth'] = MagicMock()
sys.modules['bluetooth.btcommon'] = MagicMock()

from wii_balance_board import WiiBalanceBoard


class TestWiiBalanceBoardStructure(unittest.TestCase):
    """Test the structure and initialization of WiiBalanceBoard class."""
    
    def test_class_initialization(self):
        """Test that the class initializes with correct default values."""
        board = WiiBalanceBoard()
        
        self.assertIsNone(board.control_socket)
        self.assertIsNone(board.interrupt_socket)
        self.assertFalse(board.connected)
        self.assertIsNone(board.address)
        self.assertIsInstance(board.calibration, dict)
        
    def test_calibration_structure(self):
        """Test that calibration data structure is correctly initialized."""
        board = WiiBalanceBoard()
        
        # Check that all sensors have calibration data
        required_sensors = ['top_right', 'top_left', 'bottom_right', 'bottom_left']
        for sensor in required_sensors:
            self.assertIn(sensor, board.calibration)
            self.assertIn('zero', board.calibration[sensor])
            self.assertIn('weight_17kg', board.calibration[sensor])
            self.assertIn('weight_34kg', board.calibration[sensor])
    
    def test_device_name_constant(self):
        """Test that device name constant is set."""
        self.assertEqual(WiiBalanceBoard.DEVICE_NAME, "Nintendo RVL-WBC-01")
    
    def test_context_manager_support(self):
        """Test that the class supports context manager protocol."""
        board = WiiBalanceBoard()
        
        # Should have __enter__ and __exit__ methods
        self.assertTrue(hasattr(board, '__enter__'))
        self.assertTrue(hasattr(board, '__exit__'))
        self.assertTrue(callable(board.__enter__))
        self.assertTrue(callable(board.__exit__))


class TestWiiBalanceBoardMethods(unittest.TestCase):
    """Test the methods of WiiBalanceBoard class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.board = WiiBalanceBoard()
    
    def test_disconnect_safe_when_not_connected(self):
        """Test that disconnect can be called safely when not connected."""
        # Should not raise any exception
        self.board.disconnect()
        self.assertFalse(self.board.connected)
    
    def test_read_sensor_data_when_not_connected(self):
        """Test reading sensor data when not connected returns None."""
        result = self.board.read_sensor_data()
        self.assertIsNone(result)
    
    def test_get_weight_when_not_connected(self):
        """Test getting weight when not connected returns None."""
        result = self.board.get_weight()
        self.assertIsNone(result)
    
    def test_get_center_of_gravity_with_no_weight(self):
        """Test center of gravity returns None with insufficient weight."""
        # Mock get_weight to return very low weight
        with patch.object(self.board, 'get_weight') as mock_weight:
            mock_weight.return_value = {
                'top_right': 1.0,
                'top_left': 1.0,
                'bottom_right': 1.0,
                'bottom_left': 1.0,
                'total': 4.0  # Below 5kg threshold
            }
            result = self.board.get_center_of_gravity()
            self.assertIsNone(result)
    
    def test_get_center_of_gravity_calculation(self):
        """Test center of gravity calculation logic."""
        with patch.object(self.board, 'get_weight') as mock_weight:
            # Simulate balanced weight
            mock_weight.return_value = {
                'top_right': 25.0,
                'top_left': 25.0,
                'bottom_right': 25.0,
                'bottom_left': 25.0,
                'total': 100.0
            }
            result = self.board.get_center_of_gravity()
            
            self.assertIsNotNone(result)
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 2)
            
            x, y = result
            # With balanced weight, center should be near (0, 0)
            self.assertAlmostEqual(x, 0.0, places=5)
            self.assertAlmostEqual(y, 0.0, places=5)
    
    def test_get_center_of_gravity_right_shift(self):
        """Test center of gravity calculation with weight shifted right."""
        with patch.object(self.board, 'get_weight') as mock_weight:
            # Simulate weight shifted to the right
            mock_weight.return_value = {
                'top_right': 40.0,
                'top_left': 10.0,
                'bottom_right': 40.0,
                'bottom_left': 10.0,
                'total': 100.0
            }
            result = self.board.get_center_of_gravity()
            
            self.assertIsNotNone(result)
            x, y = result
            # X should be positive (right)
            self.assertGreater(x, 0)
            # Y should be near 0 (balanced front-back)
            self.assertAlmostEqual(y, 0.0, places=5)
    
    def test_context_manager_disconnect_on_exit(self):
        """Test that context manager properly disconnects on exit."""
        with patch.object(WiiBalanceBoard, 'disconnect') as mock_disconnect:
            with WiiBalanceBoard() as board:
                pass
            # disconnect should have been called
            mock_disconnect.assert_called_once()


class TestWiiBalanceBoardDataProcessing(unittest.TestCase):
    """Test data processing and calculations."""
    
    def test_weight_calculation_scale_factor(self):
        """Test that weight calculation uses reasonable scale factor."""
        board = WiiBalanceBoard()
        
        # Mock read_sensor_data to return known values
        with patch.object(board, 'read_sensor_data') as mock_read:
            mock_read.return_value = {
                'top_right': 2048,
                'top_left': 2048,
                'bottom_right': 2048,
                'bottom_left': 2048,
                'total': 8192
            }
            
            result = board.get_weight(samples=1)
            
            self.assertIsNotNone(result)
            self.assertIn('total', result)
            # With max values (2048 per sensor), total should be around 136kg (4 * 34kg)
            self.assertGreater(result['total'], 100)
            self.assertLess(result['total'], 150)
    
    def test_weight_averaging(self):
        """Test that weight readings are properly averaged."""
        board = WiiBalanceBoard()
        
        # Mock read_sensor_data to return varying values
        values = [
            {'top_right': 100, 'top_left': 100, 'bottom_right': 100, 'bottom_left': 100},
            {'top_right': 200, 'top_left': 200, 'bottom_right': 200, 'bottom_left': 200},
        ]
        
        with patch.object(board, 'read_sensor_data') as mock_read:
            mock_read.side_effect = values
            
            result = board.get_weight(samples=2)
            
            self.assertIsNotNone(result)
            # Each sensor should average to 150 (100+200)/2
            # With scale factor 34/2048, this is approximately 2.5kg per sensor
            expected_per_sensor = 150 * (34.0 / 2048.0)
            self.assertAlmostEqual(result['top_right'], expected_per_sensor, places=1)


class TestWiiBalanceBoardConstants(unittest.TestCase):
    """Test that important constants are defined."""
    
    def test_device_name(self):
        """Test device name constant."""
        self.assertEqual(WiiBalanceBoard.DEVICE_NAME, "Nintendo RVL-WBC-01")
    
    def test_button_power_constant(self):
        """Test button constant."""
        self.assertEqual(WiiBalanceBoard.BUTTON_POWER, 0x08)


def run_tests():
    """Run all tests and return results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestWiiBalanceBoardStructure))
    suite.addTests(loader.loadTestsFromTestCase(TestWiiBalanceBoardMethods))
    suite.addTests(loader.loadTestsFromTestCase(TestWiiBalanceBoardDataProcessing))
    suite.addTests(loader.loadTestsFromTestCase(TestWiiBalanceBoardConstants))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
