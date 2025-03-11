The following calibration is required for the claw to function correctly and consistently:

  1) Coordinate determination

  Any labware to fit the deck space has the maximum didmension os 127.76 mm long, 85.57 mm wide. Thus the middle of the labware is 63.88 mm x 42.79 mm, therefore the vertical axis in which the middle of the claw is situated needs to be situated over this point
     X = 20.5, This compensates for the P300 8-channel's placement in the right pipette slot, ensuring the claw is centered over the labware.
     Y = 86.0, This accounts for the pipette mount's extension, effectively preventing collisions between the labware and the pipettes during retrieval.
     Z = 174.0,  This is set to this vertical axis of the pipette to keep it out of the way

     The resulting retrieval position is defined by the following command:
     
       position = plate["A6"].top().move(Point(x=20.5, y=86.0, z=174.0))


  2) The Claw calibration

     ![Pulse width measurements](Pi zero wh code/Images/PWM.JPG)
