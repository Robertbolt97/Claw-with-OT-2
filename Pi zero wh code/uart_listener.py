import serial
import subprocess

# Set up serial communication
ser = serial.Serial('/dev/serial0', 115200, timeout=1)

while True:
    command = ser.readline().decode().strip()
    if command:
        print(f"Executing: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        ser.write(result.stdout.encode() + result.stderr.encode())
