#!/usr/bin/env python3
"""
Example Usage of Wii Balance Board Connection

This script demonstrates various ways to use the WiiBalanceBoard class,
including basic connection, weight reading, and center of gravity tracking.
"""

import time
import sys
from wii_balance_board import WiiBalanceBoard


def example_basic_connection():
    """Example 1: Basic connection and single reading."""
    print("Example 1: Basic Connection")
    print("-" * 50)
    
    board = WiiBalanceBoard()
    
    # Connect to the board
    if board.connect():
        # Read sensor data once
        data = board.read_sensor_data()
        if data:
            print(f"Raw sensor values: {data}")
        
        # Get calibrated weight
        weight = board.get_weight()
        if weight:
            print(f"Total weight: {weight['total']:.2f} kg")
        
        board.disconnect()
    else:
        print("Failed to connect")


def example_continuous_reading():
    """Example 2: Continuous reading for 10 seconds."""
    print("\nExample 2: Continuous Reading (10 seconds)")
    print("-" * 50)
    
    board = WiiBalanceBoard()
    
    if not board.connect():
        print("Failed to connect")
        return
    
    try:
        start_time = time.time()
        while time.time() - start_time < 10:
            weight = board.get_weight()
            if weight:
                print(f"Weight: {weight['total']:6.2f} kg", end='\r', flush=True)
            time.sleep(0.1)
        print()  # New line after continuous reading
    finally:
        board.disconnect()


def example_center_of_gravity():
    """Example 3: Track center of gravity."""
    print("\nExample 3: Center of Gravity Tracking")
    print("-" * 50)
    print("Stand on the board and shift your weight...")
    
    board = WiiBalanceBoard()
    
    if not board.connect():
        print("Failed to connect")
        return
    
    try:
        for i in range(50):  # Read 50 samples
            weight = board.get_weight()
            cog = board.get_center_of_gravity()
            
            if weight and cog:
                x, y = cog
                print(f"Weight: {weight['total']:6.2f} kg | "
                      f"CoG: X={x:+.2f}, Y={y:+.2f}", end='\r', flush=True)
            
            time.sleep(0.1)
        print()  # New line
    finally:
        board.disconnect()


def example_context_manager():
    """Example 4: Using context manager."""
    print("\nExample 4: Using Context Manager")
    print("-" * 50)
    
    # The 'with' statement automatically handles connection and disconnection
    with WiiBalanceBoard() as board:
        if board.connect():
            for i in range(10):
                weight = board.get_weight()
                if weight:
                    print(f"Reading {i+1}: {weight['total']:.2f} kg")
                time.sleep(0.5)
        else:
            print("Failed to connect")


def example_specific_address():
    """Example 5: Connect to specific address."""
    print("\nExample 5: Connect to Specific Address")
    print("-" * 50)
    
    # You can provide a known Bluetooth address to skip discovery
    # Replace with your board's actual address
    address = "00:00:00:00:00:00"  # Example address
    
    print(f"Attempting to connect to {address}...")
    print("(This will likely fail with the example address)")
    
    board = WiiBalanceBoard()
    if board.connect(address):
        weight = board.get_weight()
        if weight:
            print(f"Weight: {weight['total']:.2f} kg")
        board.disconnect()
    else:
        print("Connection failed - use a valid address")


def interactive_menu():
    """Interactive menu to choose examples."""
    while True:
        print("\n" + "=" * 50)
        print("Wii Balance Board - Example Menu")
        print("=" * 50)
        print("1. Basic Connection")
        print("2. Continuous Reading (10 seconds)")
        print("3. Center of Gravity Tracking")
        print("4. Context Manager Example")
        print("5. Connect to Specific Address")
        print("0. Exit")
        print("-" * 50)
        
        try:
            choice = input("Select an example (0-5): ").strip()
            
            if choice == '0':
                print("Goodbye!")
                break
            elif choice == '1':
                example_basic_connection()
            elif choice == '2':
                example_continuous_reading()
            elif choice == '3':
                example_center_of_gravity()
            elif choice == '4':
                example_context_manager()
            elif choice == '5':
                example_specific_address()
            else:
                print("Invalid choice. Please select 0-5.")
                
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Run specific example from command line
        example = sys.argv[1]
        
        examples = {
            '1': example_basic_connection,
            '2': example_continuous_reading,
            '3': example_center_of_gravity,
            '4': example_context_manager,
            '5': example_specific_address
        }
        
        if example in examples:
            examples[example]()
        else:
            print(f"Unknown example: {example}")
            print("Usage: python example_usage.py [1-5]")
            return 1
    else:
        # Run interactive menu
        interactive_menu()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
