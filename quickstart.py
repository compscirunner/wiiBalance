#!/usr/bin/env python3
"""
Quick Start Example for Wii Balance Board

This is the simplest possible example to get started.
Just run this script and step on the board!
"""

from wii_balance_board import WiiBalanceBoard
import time

print("=" * 60)
print("Wii Balance Board - Quick Start")
print("=" * 60)
print()
print("Instructions:")
print("1. Press the red SYNC button inside the battery compartment")
print("2. Wait for the script to connect (blue LED will blink)")
print("3. Step on the board to see your weight!")
print()
print("-" * 60)

# Create and connect to the board
board = WiiBalanceBoard()

if board.connect():
    print()
    print("Connected! Step on the board...")
    print("-" * 60)
    
    try:
        # Read weight for 30 seconds
        for i in range(300):
            weight = board.get_weight()
            
            if weight and weight['total'] > 5:  # Only show if weight detected
                print(f"\rYour weight: {weight['total']:6.2f} kg ({weight['total']*2.205:6.2f} lbs)", 
                      end='', flush=True)
            else:
                print(f"\rWaiting for weight... {30 - i//10}s ", end='', flush=True)
            
            time.sleep(0.1)
        
        print("\n\nSession ended.")
        
    except KeyboardInterrupt:
        print("\n\nStopped by user.")
    
    finally:
        board.disconnect()
        
else:
    print()
    print("Failed to connect. Please check:")
    print("- Board is in pairing mode (red SYNC button pressed)")
    print("- Board has batteries installed")
    print("- Bluetooth is enabled on your computer")
    print("- You have necessary permissions (try with sudo on Linux)")
