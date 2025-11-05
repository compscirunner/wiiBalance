#!/usr/bin/env python3
"""
Wii Balance Board Connection Module

This module provides functionality to connect to and read data from a Wii Balance Board
via Bluetooth. It handles device discovery, connection, calibration, and sensor data reading.
"""

import time
import struct
import sys

try:
    import bluetooth
    BLUETOOTH_AVAILABLE = True
except ImportError:
    BLUETOOTH_AVAILABLE = False
    print("Warning: PyBluez not installed. Install with: pip install pybluez")


class WiiBalanceBoard:
    """
    A class to interface with the Wii Balance Board via Bluetooth.
    
    The Wii Balance Board has 4 weight sensors (top-right, top-left, bottom-right, bottom-left)
    and communicates via Bluetooth using the standard Wii Remote protocol.
    """
    
    # Wii Balance Board constants
    DEVICE_NAME = "Nintendo RVL-WBC-01"
    
    # Button codes
    BUTTON_POWER = 0x08
    
    # Calibration data
    CALIBRATION_REQUEST = b'\xa1\x17\x04\xa4\x00\x24\x00\x18'
    
    def __init__(self):
        """Initialize the Wii Balance Board connection handler."""
        self.control_socket = None
        self.interrupt_socket = None
        self.connected = False
        self.calibration = {
            'top_right': {'zero': 0, 'weight_17kg': 0, 'weight_34kg': 0},
            'top_left': {'zero': 0, 'weight_17kg': 0, 'weight_34kg': 0},
            'bottom_right': {'zero': 0, 'weight_17kg': 0, 'weight_34kg': 0},
            'bottom_left': {'zero': 0, 'weight_17kg': 0, 'weight_34kg': 0}
        }
        self.address = None
        
    def discover(self, timeout=10):
        """
        Discover nearby Wii Balance Board devices.
        
        Args:
            timeout: Maximum time to search for devices (seconds)
            
        Returns:
            str: Bluetooth address of the first discovered Balance Board, or None
        """
        if not BLUETOOTH_AVAILABLE:
            print("Error: Bluetooth library not available")
            return None
            
        print(f"Searching for Wii Balance Board (timeout: {timeout}s)...")
        print("Please press the red sync button on the Wii Balance Board now.")
        
        try:
            nearby_devices = bluetooth.discover_devices(
                duration=timeout,
                lookup_names=True,
                flush_cache=True
            )
            
            for addr, name in nearby_devices:
                print(f"Found device: {name} ({addr})")
                if name == self.DEVICE_NAME:
                    print(f"Found Wii Balance Board at {addr}")
                    self.address = addr
                    return addr
                    
            print("No Wii Balance Board found.")
            return None
            
        except Exception as e:
            print(f"Error during discovery: {e}")
            return None
    
    def connect(self, address=None):
        """
        Connect to a Wii Balance Board.
        
        Args:
            address: Bluetooth address of the board. If None, will attempt discovery.
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        if not BLUETOOTH_AVAILABLE:
            print("Error: Bluetooth library not available")
            return False
            
        if address is None:
            address = self.discover()
            if address is None:
                return False
        
        self.address = address
        
        try:
            print(f"Connecting to Wii Balance Board at {address}...")
            
            # Connect to control channel (port 17)
            self.control_socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
            self.control_socket.connect((address, 17))
            
            # Connect to interrupt channel (port 19)
            self.interrupt_socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
            self.interrupt_socket.connect((address, 19))
            
            print("Successfully connected!")
            self.connected = True
            
            # Request status report
            self._send_command(b'\x52\x15\x00')
            time.sleep(0.1)
            
            # Enable reporting
            self._send_command(b'\x52\x12\x00\x34')
            time.sleep(0.1)
            
            return True
            
        except Exception as e:
            print(f"Connection failed: {e}")
            self.disconnect()
            return False
    
    def disconnect(self):
        """Disconnect from the Wii Balance Board."""
        if self.control_socket:
            try:
                self.control_socket.close()
            except (OSError, bluetooth.btcommon.BluetoothError):
                pass
            self.control_socket = None
            
        if self.interrupt_socket:
            try:
                self.interrupt_socket.close()
            except (OSError, bluetooth.btcommon.BluetoothError):
                pass
            self.interrupt_socket = None
            
        self.connected = False
        print("Disconnected from Wii Balance Board")
    
    def _send_command(self, data):
        """
        Send a command to the Wii Balance Board.
        
        Args:
            data: Bytes to send
        """
        if self.control_socket:
            try:
                self.control_socket.send(data)
            except Exception as e:
                print(f"Error sending command: {e}")
    
    def read_sensor_data(self, timeout=1.0):
        """
        Read raw sensor data from the Wii Balance Board.
        
        Args:
            timeout: Maximum time to wait for data (seconds)
            
        Returns:
            dict: Dictionary with sensor values for each corner, or None on error
        """
        if not self.connected or not self.interrupt_socket:
            print("Error: Not connected to Wii Balance Board")
            return None
        
        try:
            self.interrupt_socket.settimeout(timeout)
            data = self.interrupt_socket.recv(25)
            
            if len(data) < 25:
                return None
            
            # Parse sensor data (bytes 4-11 contain the 4 sensor values)
            # Each sensor value is 2 bytes (big endian)
            if data[1] == 0x34:  # Data report type
                top_right = struct.unpack('>H', data[4:6])[0]
                bottom_right = struct.unpack('>H', data[6:8])[0]
                top_left = struct.unpack('>H', data[8:10])[0]
                bottom_left = struct.unpack('>H', data[10:12])[0]
                
                return {
                    'top_right': top_right,
                    'top_left': top_left,
                    'bottom_right': bottom_right,
                    'bottom_left': bottom_left,
                    'total': top_right + top_left + bottom_right + bottom_left
                }
            
            return None
            
        except bluetooth.btcommon.BluetoothError as e:
            if 'timed out' not in str(e):
                print(f"Bluetooth error reading data: {e}")
            return None
        except Exception as e:
            print(f"Error reading sensor data: {e}")
            return None
    
    def get_weight(self, samples=5):
        """
        Get calibrated weight readings from all sensors.
        
        Args:
            samples: Number of samples to average
            
        Returns:
            dict: Weight in kg for each sensor and total weight, or None on error
        """
        readings = []
        
        for _ in range(samples):
            data = self.read_sensor_data()
            if data:
                readings.append(data)
            time.sleep(0.01)
        
        if not readings:
            return None
        
        # Average the readings
        avg = {
            'top_right': sum(r['top_right'] for r in readings) / len(readings),
            'top_left': sum(r['top_left'] for r in readings) / len(readings),
            'bottom_right': sum(r['bottom_right'] for r in readings) / len(readings),
            'bottom_left': sum(r['bottom_left'] for r in readings) / len(readings)
        }
        
        # Simple linear conversion (raw values to kg)
        # These are approximations and may need calibration for accuracy
        # Typical range is 0-2048 for each sensor
        scale_factor = 34.0 / 2048.0  # Assuming max ~34kg per sensor
        
        result = {
            'top_right': avg['top_right'] * scale_factor,
            'top_left': avg['top_left'] * scale_factor,
            'bottom_right': avg['bottom_right'] * scale_factor,
            'bottom_left': avg['bottom_left'] * scale_factor
        }
        result['total'] = sum(result.values())
        
        return result
    
    def get_center_of_gravity(self):
        """
        Calculate the center of gravity based on sensor readings.
        
        Returns:
            tuple: (x, y) coordinates where (0, 0) is center, or None on error
                   x: -1 (left) to 1 (right)
                   y: -1 (front) to 1 (back)
        """
        weight = self.get_weight()
        if not weight or weight['total'] < 5:  # Minimum 5kg threshold
            return None
        
        # Calculate center of gravity
        # Assuming board dimensions and sensor positions
        left = weight['top_left'] + weight['bottom_left']
        right = weight['top_right'] + weight['bottom_right']
        front = weight['top_left'] + weight['top_right']
        back = weight['bottom_left'] + weight['bottom_right']
        
        x = (right - left) / weight['total']
        y = (back - front) / weight['total']
        
        return (x, y)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


def main():
    """Example usage of the WiiBalanceBoard class."""
    print("Wii Balance Board Connection Example")
    print("=" * 50)
    
    if not BLUETOOTH_AVAILABLE:
        print("\nError: PyBluez library is required.")
        print("Install it with: pip install pybluez")
        print("\nOn Linux, you may also need:")
        print("  sudo apt-get install bluetooth libbluetooth-dev")
        return 1
    
    board = WiiBalanceBoard()
    
    try:
        # Discover and connect
        if not board.connect():
            print("Failed to connect to Wii Balance Board")
            return 1
        
        print("\nReading sensor data... (Press Ctrl+C to stop)")
        print("-" * 50)
        
        # Read data continuously
        while True:
            weight = board.get_weight()
            
            if weight:
                print(f"\rTotal: {weight['total']:6.2f}kg | "
                      f"TL: {weight['top_left']:5.2f}kg | "
                      f"TR: {weight['top_right']:5.2f}kg | "
                      f"BL: {weight['bottom_left']:5.2f}kg | "
                      f"BR: {weight['bottom_right']:5.2f}kg", end='', flush=True)
                
                cog = board.get_center_of_gravity()
                if cog:
                    x, y = cog
                    # Optional: print center of gravity
                    # print(f" | CoG: ({x:+.2f}, {y:+.2f})")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\nStopping...")
    except Exception as e:
        print(f"\nError: {e}")
        return 1
    finally:
        board.disconnect()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
