import pyvisa
import time

metadata = {
    "apiLevel": "2.11",
    "protocolName": "Run Script via UART",
    "description": "Sends multiple commands to execute Python scripts on Raspberry Pi via UART",
    "author": "Robert Bolt"
}

rm = pyvisa.ResourceManager()
#serial_port = 'ASRL13::INSTR'  # Simulation
serial_port = 'ASRL/dev/ttyUSB0::INSTR' # Linux/macOS

try:
    instrument = rm.open_resource(serial_port)
    instrument.timeout = 2000
    instrument.baud_rate = 115200

    commands = [
        "python3 /home/pi/open_full.py\n",
        "python3 /home/pi/down.py\n",
        "python3 /home/pi/close_small.py\n",
        "python3 /home/pi/up.py\n",
    ]

    for command in commands:
        instrument.write(command)
        time.sleep(1)  # Adjust timing if needed
        try:
            response = instrument.read()
            print(f"Response from Pi: {response}")
        except pyvisa.errors.VisaIOError:
            print(f"No response received for command: {command.strip()}")

except pyvisa.errors.VisaIOError as e:
    print(f"Error communicating with the instrument: {e}")
