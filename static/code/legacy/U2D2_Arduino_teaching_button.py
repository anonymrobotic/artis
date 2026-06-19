import os
import sys
import time
import serial  # For communication with Arduino
from dynamixel_sdk import *  # Uses Dynamixel SDK

# Control table addresses for MX series
ADDR_TORQUE_ENABLE = 24
ADDR_GOAL_POSITION = 30
ADDR_PRESENT_POSITION = 36
ADDR_MOVING_SPEED = 32
ADDR_TORQUE_LIMIT = 34

# Data byte length
LEN_GOAL_POSITION = 2
LEN_PRESENT_POSITION = 2
LEN_MOVING_SPEED = 2
LEN_TORQUE_LIMIT = 2

# Protocol version for MX series
PROTOCOL_VERSION = 1.0

# Default setting
BAUDRATE = 57600
DEVICENAME = '/dev/ttyUSB0'  # Adjust according to your system (e.g., COM3 for Windows)
ARDUINO_PORT = '/dev/ttyACM0'  # Port for Arduino communication
ARDUINO_BAUDRATE = 9600

DXL_IDs = [2, 3, 4, 5, 6, 7, 8]  # List of Dynamixel IDs
TORQUE_ENABLE = 1  # Enable torque
TORQUE_DISABLE = 0  # Disable torque
MAX_TORQUE = 1023  # Maximum torque limit

# Establish communication with Arduino
try:
    arduino = serial.Serial(ARDUINO_PORT, ARDUINO_BAUDRATE, timeout=1)
    time.sleep(2)  # Allow time for Arduino to initialize
    print("Connected to Arduino on", ARDUINO_PORT)
except Exception as e:
    print("Failed to connect to Arduino:", e)
    arduino = None

# Initialize PortHandler instance
portHandler = PortHandler(DEVICENAME)

# Initialize PacketHandler instance
packetHandler = PacketHandler(PROTOCOL_VERSION)

# Open port
if not portHandler.openPort():
    print("Failed to open the port")
    sys.exit()
print("Succeeded to open the port")

# Set port baudrate
if not portHandler.setBaudRate(BAUDRATE):
    print("Failed to set the baudrate")
    sys.exit()
print("Succeeded to set the baudrate")

# Enable torque for all servos
for dxl_id in DXL_IDs:
    packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
    print(f"Dynamixel {dxl_id} has been successfully connected")

# Function to move motors to a given predefined position and speed
def move_motors(positions_speeds):
    for dxl_id, (position, speed) in positions_speeds.items():
        packetHandler.write2ByteTxRx(portHandler, dxl_id, ADDR_MOVING_SPEED, speed)
        packetHandler.write2ByteTxRx(portHandler, dxl_id, ADDR_GOAL_POSITION, position)
        print(f"Dynamixel {dxl_id} moved to {position} at speed {speed}")

# Function to read the position of a motor
def read_motor_position(dxl_id):
    position, _, _ = packetHandler.read2ByteTxRx(portHandler, dxl_id, ADDR_PRESENT_POSITION)
    return position

# Function to control relay via Arduino
def control_relay(state):
    if arduino:
        arduino.write(state.encode())
        print(f"Relay {'ON' if state == '1' else 'OFF'} sent to Arduino")
    else:
        print("Arduino connection not established.")

print("Press keys for predefined actions. Press 't' for the new sequence, 'y' to disable torque, 'u' to move all motors and turn off relay.")

while True:
    key = input("Enter command: ").strip().lower()
    
    if key == 't':
        # Step 1: Read and store positions of motors 2, 4, 6, 8
        saved_positions = {motor_id: read_motor_position(motor_id) for motor_id in [2, 4, 6, 8]}
        print("Saved positions:", saved_positions)

        # Step 2: Turn on relay
        control_relay('1')
        
        # Step 3: Fix motors 2, 4, 6, 8
        for motor_id, position in saved_positions.items():
            packetHandler.write2ByteTxRx(portHandler, motor_id, ADDR_GOAL_POSITION, position)
            print(f"Motor {motor_id} fixed at position {position}")
        
        # Step 4: Move motors 3, 5, 7 to position 1000 with speed 50
        for motor_id in [3, 5, 7]:
            packetHandler.write2ByteTxRx(portHandler, motor_id, ADDR_MOVING_SPEED, 50)
            packetHandler.write2ByteTxRx(portHandler, motor_id, ADDR_GOAL_POSITION, 1000)
            print(f"Motor {motor_id} moving to position 1000 at speed 50")
    
    elif key == 'y':
        # Disable torque for all motors and turn off relay
        for dxl_id in DXL_IDs:
            packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
            print(f"Torque disabled for Dynamixel {dxl_id}")
        control_relay('0')
        print("Torque disabled for manual adjustment.")
    
    elif key == 'u':
        move_motors({2: (2052, 80), 3: (1330, 85), 4: (2052, 80), 5: (1330, 87), 6: (2052, 80), 7: (1330, 90), 8: (1712, 80)})
        control_relay('0')
        print("All motors moved to specified positions and relay turned off.")
    
    elif key == 'e':
        print("Exiting program...")
        control_relay('0')
        break

# Disable torque after motion
for dxl_id in DXL_IDs:
    packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
    print(f"Torque disabled for Dynamixel {dxl_id}")

# Close port
portHandler.closePort()
if arduino:
    arduino.close()
