# wiiBalance

A Python library for connecting to and reading data from the Nintendo Wii Balance Board via Bluetooth.

## Features

- 🔌 Easy Bluetooth connection to Wii Balance Board
- ⚖️ Real-time weight sensor data reading from all 4 sensors
- 📊 Automatic weight calculation and averaging
- 🎯 Center of gravity calculation
- 🔄 Context manager support for automatic connection handling
- 📝 Comprehensive examples and documentation

## Requirements

- Python 3.6 or higher
- Bluetooth adapter (built-in or USB)
- Linux, macOS, or Windows with Bluetooth support

### System Dependencies

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get update
sudo apt-get install bluetooth libbluetooth-dev python3-dev
```

**macOS:**
Bluetooth support is built-in. You may need to install Xcode Command Line Tools:
```bash
xcode-select --install
```

**Windows:**
Windows Bluetooth support requires additional setup. PyBluez may have limited functionality on Windows.

## Installation

1. Clone this repository:
```bash
git clone https://github.com/compscirunner/wiiBalance.git
cd wiiBalance
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

Or install directly:
```bash
pip install pybluez
```

## Quick Start

### Basic Usage

```python
from wii_balance_board import WiiBalanceBoard

# Create a board instance
board = WiiBalanceBoard()

# Connect to the board (will auto-discover)
if board.connect():
    # Read weight data
    weight = board.get_weight()
    print(f"Total weight: {weight['total']:.2f} kg")
    
    # Disconnect when done
    board.disconnect()
```

### Using Context Manager

```python
from wii_balance_board import WiiBalanceBoard

with WiiBalanceBoard() as board:
    if board.connect():
        weight = board.get_weight()
        print(f"Weight: {weight['total']:.2f} kg")
```

### Running the Example Script

The main module can be run directly for a quick demo:

```bash
python wii_balance_board.py
```

Or run the comprehensive examples:

```bash
python example_usage.py
```

This will show an interactive menu with various usage examples.

## How to Connect

1. Put the Wii Balance Board into discovery mode:
   - Remove the battery cover on the bottom
   - Press the small red SYNC button inside the battery compartment
   - The blue LED on the front will start blinking

2. Run your Python script within 20 seconds:
   ```bash
   python wii_balance_board.py
   ```

3. The script will automatically discover and connect to the board

## API Reference

### WiiBalanceBoard Class

#### Methods

- **`discover(timeout=10)`** - Search for nearby Wii Balance Boards
  - Returns: Bluetooth address or None

- **`connect(address=None)`** - Connect to a Wii Balance Board
  - Parameters: `address` - Optional Bluetooth address (will auto-discover if None)
  - Returns: True if successful, False otherwise

- **`disconnect()`** - Disconnect from the board

- **`read_sensor_data(timeout=1.0)`** - Read raw sensor values
  - Returns: Dict with raw values for each sensor

- **`get_weight(samples=5)`** - Get calibrated weight readings
  - Parameters: `samples` - Number of samples to average
  - Returns: Dict with weight in kg for each sensor and total

- **`get_center_of_gravity()`** - Calculate center of gravity
  - Returns: Tuple (x, y) where values range from -1 to 1

### Example Return Values

**`get_weight()` returns:**
```python
{
    'top_left': 15.3,      # kg
    'top_right': 16.1,     # kg
    'bottom_left': 14.8,   # kg
    'bottom_right': 15.9,  # kg
    'total': 62.1          # kg
}
```

**`get_center_of_gravity()` returns:**
```python
(0.05, -0.12)  # (x, y) coordinates
# x: -1 (left) to 1 (right)
# y: -1 (front) to 1 (back)
```

## Troubleshooting

### Connection Issues

**Board not found during discovery:**
- Make sure the board is in pairing mode (blue LED blinking)
- Try pressing the SYNC button again
- Move closer to the Bluetooth adapter
- Make sure no other device is connected to the board

**Permission denied errors (Linux):**
```bash
sudo usermod -a -G bluetooth $USER
# Log out and log back in for changes to take effect
```

Or run with sudo (not recommended for production):
```bash
sudo python wii_balance_board.py
```

**PyBluez installation fails:**

On Linux, install system dependencies first:
```bash
sudo apt-get install bluetooth libbluetooth-dev python3-dev
pip install pybluez
```

### Reading Issues

**Getting None or zero values:**
- Make sure you're standing on the board or applying weight
- Check that the board has batteries and is powered on
- Try reconnecting to the board

## Use Cases

- Fitness and weight tracking applications
- Balance training and rehabilitation
- Gaming and interactive installations
- Research and data collection
- Posture analysis

## Technical Details

The Wii Balance Board is essentially a Bluetooth HID device that:
- Has 4 strain gauge sensors (one in each corner)
- Communicates using the Wii Remote protocol
- Uses Bluetooth L2CAP on ports 17 (control) and 19 (interrupt)
- Provides 16-bit values for each sensor
- Can measure up to approximately 150 kg (330 lbs) total

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Nintendo for creating the Wii Balance Board
- The PyBluez community for Bluetooth support in Python
- Various open-source Wii Balance Board projects that helped understand the protocol

## Related Projects

- [xwiimote](https://github.com/dvdhrm/xwiimote) - Linux kernel driver for Wii devices
- [wiiboard-simple](https://github.com/InitialForce/WiiBoard_Simple) - Another Python implementation
- [node-wiibalanceboard](https://github.com/lubbert/node-wiibalanceboard) - Node.js implementation