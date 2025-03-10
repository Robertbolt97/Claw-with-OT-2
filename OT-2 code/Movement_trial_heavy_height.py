# run this before "stty -F /dev/ttyUSB0 speed 115200" to set usb port speed correctly
# Also this if not working ""stty -F /dev/ttyUSB0 -ixon -ixoff" Disables the XON/XOFF software flow control for transmitting dat and disables the XON/XOFF software flow control for receiving data.
#temperature effects the motor controls, maybe a way to look into this with thermcouple
#lsof /dev/ttyUSB0 to find the sessison and then screen -X -S 2202 quit to kill the specfic screen 


from opentrons import protocol_api
from opentrons.types import Point  # Import Point for position offset
import subprocess  # Import subprocess to run the Python scripts
import time

metadata = {
    "apiLevel": "2.15",  # move_to requires API level 2.15
    "protocolName": "Movement Trial Heavy Height",
    "description": """Move pipette to sequential deck positions while moving labware accordingly""",
    "author": "Robert Bolt"
}


def run(protocol: protocol_api.ProtocolContext):
    
    # Load pipette and labware in position 1
    pipette = protocol.load_instrument("p300_multi_gen2", "right")
    plate = protocol.load_labware("corning_96_wellplate_360ul_flat", "1")
    
    pipette.default_speed = 100

    # Move pipette and labware sequentially through positions 2 to 10
    for i in range(2, 10):
        # Define position offset relative to well A6
        position = plate["A6"].top().move(Point(x=20.5, y=86, z=174.0)) # x = left(negative)/right(positive), y, backwards/forwards

        # Move pipette to the adjusted position
        pipette.move_to(position)
        
        protocol.delay(seconds=1)
        
        # Run the first Python script (Claw_grab.py)
        subprocess.run(["python3", "/var/lib/jupyter/notebooks/Claw/Claw_grab_heavy_height.py"]) #this works
        
        protocol.delay(seconds=1)

        # Move the plate to the next deck position
        protocol.move_labware(labware=plate, new_location=str(i))
        
        protocol.delay(seconds=1)
        
        position = plate["A6"].top().move(Point(x=20.5, y=86, z=174.0))
        
        pipette.move_to(position)
        
        protocol.delay(seconds=1)
        
        # Run the second Python script (Claw_release.py) after pipette movement
        subprocess.run(["python3", "/var/lib/jupyter/notebooks/Claw/Claw_release.py"])  # Runs this code before it moves 
        
        protocol.delay(seconds=1)

        

