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
    "protocolName": "Thunderbolt",
    "description": """Prepare plates with dye and then move them into position""",
    "author": "Robert Bolt"
}


def run(protocol: protocol_api.ProtocolContext):
    
    # Load pipette and labware in position 1
    left_pipette = protocol.load_instrument("p300_single_gen2", "left")
    right_pipette = protocol.load_instrument("p300_multi_gen2", "right")
    
    dye = protocol.load_labware("agilent_1_reservoir_290ml",10)
    three_hundred_tips = protocol.load_labware("opentrons_96_tiprack_300ul",11)
    plate_1 = protocol.load_labware("corning_96_wellplate_360ul_flat", "8") #Ends in deck position 2
    plate_2 = protocol.load_labware("corning_96_wellplate_360ul_flat", "1") #Ends in deck position 5
    plate_3 = protocol.load_labware("corning_96_wellplate_360ul_flat", "6") #Ends in deck position 8

    dye_volume = 200

    # Wells in plates
    plate_wells = {
    plate_1: ["E1","F1","C2","D2","E2","B3","C3","D3","A4","B4","C4","A5","B5","A6"],
    plate_2: ["C4","E4","F4","G4","H4","A5","B5","C5","D5","E5","F5","G5","H5","A6", "B6","C6","D6","E6","F6","G6","H6","A7","B7","C7","D7","E7","F7","G7","A8","C8","D8","E8","F8","C9","D9","E9","C10","D10"],
    plate_3: ["H3","G4","H4","F5","G5","H5","E6","F6","G6","H6","E7","F7","G7","H7","E8","F8","G8","H8","E9","F9","G9","H9","E10","F10","G10","H10","E11","F11","G11","E12","F12"]
}

    def transfer_liquid():
        left_pipette.pick_up_tip(three_hundred_tips['A1'])
        
        for plate, wells in plate_wells.items():
            for well in wells:
                left_pipette.aspirate(dye_volume, dye['A1'])
                left_pipette.air_gap(10)
                left_pipette.dispense(dye_volume+10, plate[well].top(z=-1.5))
                left_pipette.blow_out(plate[well].top(z=-1.5))
                left_pipette.touch_tip(plate[well], radius=0.2, v_offset=-1.5)

        left_pipette.drop_tip()

    def move_plate(plate, new_position):
    
        right_pipette.default_speed = 50
       
        position = plate["A6"].top().move(Point(x=20.5, y=86, z=174.0))

        right_pipette.move_to(position)
       
        protocol.delay(seconds=1)

        subprocess.run(["python3", "/var/lib/jupyter/notebooks/Claw/Claw_grab_heavy.py"])

        protocol.delay(seconds=1)

        protocol.move_labware(labware=plate, new_location=new_position)

        protocol.delay(seconds=1)

        position = plate["A6"].top().move(Point(x=20.5, y=86, z=174.0))

        right_pipette.move_to(position)
                       
        protocol.delay(seconds=1)

        subprocess.run(["python3", "/var/lib/jupyter/notebooks/Claw/Claw_release_heavy.py"])

        protocol.delay(seconds=10)


    # Execute transfers and moves
    transfer_liquid()
    move_plate(plate_1, 2)
    move_plate(plate_2, 5)
    move_plate(plate_3, 8)

    # Flash OT-2 lights to indicate completion
    for _ in range(3):
        protocol.set_rail_lights(True)
        protocol.delay(seconds=1)
        protocol.set_rail_lights(False)
        protocol.delay(seconds=1)

    protocol.set_rail_lights(True)
   

