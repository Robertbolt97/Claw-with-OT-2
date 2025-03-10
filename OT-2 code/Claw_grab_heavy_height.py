import pyvisa
import time

metadata = {
    "apiLevel": "2.11",
    "protocolName": "Run Script via UART",
    "description": "Sends multiple commands to execute Python scripts on Raspberry Pi via UART",
    "author": "Robert Bolt"
}

rm = pyvisa.ResourceManager()
# serial_port = 'ASRL13::INSTR'  # Simulation
serial_port = 'ASRL/dev/ttyUSB0::INSTR'  # Linux/macOS

try:
    instrument = rm.open_resource(serial_port)
    instrument.timeout = 2000
    instrument.baud_rate = 115200

    commands = [
        "python3 /home/pi/open_full.py\n",
        "python3 /home/pi/down.py\n",
        "python3 /home/pi/up_small.py\n", 
        "nohup python3 /home/pi/close_small_hold.py &\n",  # Run in background
    ]

    # Run the first few commands
    for command in commands:
        instrument.write(command)
        time.sleep(1)  # Adjust timing if needed
        try:
            response = instrument.read()
            print(f"Response from Pi: {response}")
        except pyvisa.errors.VisaIOError:
            print(f"No response received for command: {command.strip()}")

    # Add a small delay to give the background process time to start
    time.sleep(2.5)  # Adjust sleep time if needed

    # Now run the final command (after background task has had time to start)
    instrument.write("nohup python3 /home/pi/up_2.py &\n")
    time.sleep(2.5)  # Adjust timing if needed
    try:
        response = instrument.read()
        print(f"Response from Pi: {response}")
    except pyvisa.errors.VisaIOError:
        print(f"No response received for command: up.py")

except pyvisa.errors.VisaIOError as e:
    print(f"Error communicating with the instrument: {e}")
    
# Two issues:
# 1) Gripper jumps open after its gone up
